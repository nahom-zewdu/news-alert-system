"""
Streamlit demo UI for News Alert System
Clean, professional dashboard with separate tabs for feed and subscription.
"""
import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from streamlit_autorefresh import st_autorefresh

# Configuration
API_BASE = f"http://{os.getenv('APP_HOST', 'localhost')}:{os.getenv('APP_PORT', '8000')}/api/v1"

st.set_page_config(page_title="News Alert Dashboard", layout="wide")
st.title("News Alert Dashboard")

# Auto-refresh (only affects the News Feed tab)
st_autorefresh(interval=30_000, key="datarefresh")  # 30 seconds

# Available categories for subscription
AVAILABLE_TOPICS = ["technology", "business", "science", "politics", "health"]

# Tabs
tab_feed, tab_subscribe = st.tabs(["News Feed", "Newsletter Subscription"])

# ==================== TAB 1: News Feed ====================
with tab_feed:
    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.subheader("Latest Articles")

        # Manual fetch button
        if st.button("Fetch Latest News"):
            with st.spinner("Fetching and classifying new articles..."):
                try:
                    r = requests.post(f"{API_BASE}/news/fetch/")
                    r.raise_for_status()
                    count = r.json().get("new_count", 0)
                    if count > 0:
                        st.success(f"Added {count} new articles")
                    else:
                        st.info("No new articles at this time")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Load news
        try:
            resp = requests.get(f"{API_BASE}/news/?limit=200")
            resp.raise_for_status()
            news = resp.json()
        except Exception as e:
            st.error(f"Failed to load articles: {e}")
            news = []

        if not news:
            st.info("No articles yet. Click 'Fetch Latest News' to begin.")
            st.stop()

        df = pd.DataFrame(news)
        df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

        # Sidebar filters in feed tab
        with st.sidebar:
            st.header("Filters")

            search_query = st.text_input("Search in title or summary")

            sources = sorted(df["source"].dropna().unique())
            categories = sorted(df["category"].dropna().unique())

            selected_sources = st.multiselect("Source", options=sources)
            selected_categories = st.multiselect("Category", options=categories)

            st.subheader("Time Period")
            period_options = {
                "Today": (datetime.now(timezone.utc).date(), datetime.now(timezone.utc).date()),
                "Last 7 days": (datetime.now(timezone.utc).date() - timedelta(days=6), datetime.now(timezone.utc).date()),
                "Last 30 days": (datetime.now(timezone.utc).date() - timedelta(days=29), datetime.now(timezone.utc).date()),
                "This year": (datetime(datetime.now(timezone.utc).year, 1, 1).date(), datetime.now(timezone.utc).date()),
                "All time": (df["published_at"].dt.date.min(), df["published_at"].dt.date.max()),
            }
            selected_period = st.radio("Show articles from", options=list(period_options.keys()), index=2)

        start_date, end_date = period_options[selected_period]

        # Apply filters
        filtered = df.copy()

        if search_query:
            q = search_query.lower()
            mask = (
                filtered["title"].str.lower().str.contains(q, na=False) |
                filtered["summary"].str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]

        if selected_sources:
            filtered = filtered[filtered["source"].isin(selected_sources)]

        if selected_categories:
            filtered = filtered[filtered["category"].isin(selected_categories)]

        filtered = filtered[
            (filtered["published_at"].dt.date >= start_date) &
            (filtered["published_at"].dt.date <= end_date)
        ]

        # Session state for highlighting new items
        if "last_seen_ids" not in st.session_state:
            st.session_state.last_seen_ids = set()
        if "highlight_until" not in st.session_state:
            st.session_state.highlight_until = {}

        now = datetime.now(timezone.utc)
        current_ids = set(filtered["id"])
        new_ids = current_ids - st.session_state.last_seen_ids
        for nid in new_ids:
            st.session_state.highlight_until[nid] = now.timestamp() + 10
        st.session_state.last_seen_ids = current_ids

        # Display articles
        for _, row in filtered.sort_values("published_at", ascending=False).iterrows():
            item = row.to_dict()
            is_new = now.timestamp() < st.session_state.highlight_until.get(item["id"], 0)

            if is_new:
                st.markdown(
                    """
                    <div style="
                        border-left: 4px solid #4CAF50;
                        background-color: #f8fff8;
                        padding: 16px;
                        border-radius: 8px;
                        margin-bottom: 16px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    ">
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="
                        padding: 16px;
                        border-radius: 8px;
                        margin-bottom: 16px;
                        background-color: white;
                        border: 1px solid #eee;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                    ">
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(f"**{item['title']}**")

            meta = f"**Source:** {item.get('source', 'Unknown')} &nbsp; | &nbsp; "
            meta += f"**Category:** {item.get('category', 'uncategorized')} &nbsp; | &nbsp; "
            meta += f"**Published:** {item['published_at'].strftime('%b %d, %Y at %H:%M UTC')}"
            st.caption(meta)

            if item.get("summary"):
                st.write(item["summary"])

            if item.get("link"):
                st.markdown(f"[Read full article]({item['link']})")

            if st.button("Send Alert", key=f"alert_{item['id']}"):
                with st.spinner("Sending alert..."):
                    try:
                        r = requests.post(f"{API_BASE}/alerts/{item['id']}")
                        r.raise_for_status()
                        st.success("Alert sent to subscribers")
                    except Exception as e:
                        st.error("Failed to send alert")

            st.markdown("</div>", unsafe_allow_html=True)

    # Alert History in side column
    with col_side:
        st.subheader("Alert History")
        try:
            r = requests.get(f"{API_BASE}/alerts/")
            r.raise_for_status()
            alerts = r.json().get("alerts", [])
        except Exception:
            st.error("Failed to load history")
            alerts = []

        if alerts:
            for alert in reversed(alerts[:10]):  # Show latest 10
                status = "Sent" if alert.get("sent") else "Failed"
                time = alert.get("sent_at", "Unknown")
                if time != "Unknown":
                    time = pd.to_datetime(time).strftime("%b %d, %Y %H:%M")

                st.markdown(
                    f"""
                    **To:** {alert.get('to', 'N/A')}  
                    **Subject:** {alert.get('subject', 'N/A')}  
                    **Status:** {status}  
                    **Time:** {time}
                    """
                )
                st.markdown("---")
        else:
            st.info("No alerts sent yet.")

# ==================== TAB 2: Newsletter Subscription ====================
with tab_subscribe:
    st.header("Subscribe to News Alerts")
    st.write("Receive curated news alerts based on your preferred topics.")

    with st.form("subscription_form", clear_on_submit=True):
        email = st.text_input("Email address", placeholder="you@example.com")
        topics = st.multiselect(
            "Select topics you're interested in",
            options=AVAILABLE_TOPICS,
            help="You will receive alerts only for selected topics"
        )

        submitted = st.form_submit_button("Subscribe")
        if submitted:
            if not email:
                st.error("Please enter a valid email address.")
            elif not topics:
                st.warning("Please select at least one topic.")
            else:
                with st.spinner("Subscribing..."):
                    try:
                        payload = {"email": email, "topics": topics}
                        r = requests.post(f"{API_BASE}/subscribers/", json=payload)
                        if r.status_code == 201:
                            st.success("Thank you! You've been successfully subscribed.")
                        elif r.status_code == 409:
                            st.info("You're already subscribed.")
                        else:
                            r.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 409:
                            st.info("This email is already subscribed.")
                        else:
                            st.error("Subscription failed. Please try again later.")
                    except Exception:
                        st.error("An error occurred. Please check your connection.")

    st.info("To unsubscribe, contact the administrator or use the API endpoint directly.")