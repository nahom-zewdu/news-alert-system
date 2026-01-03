# app/ui/streamlit.py

"""
Streamlit UI for News Alert System
Professional dashboard with:
- News Feed
- Public subscription
- Admin subscriber management
"""
import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime, timedelta, timezone
from streamlit_autorefresh import st_autorefresh

# Use API_BASE from env if set, otherwise fallback
API_BASE = os.getenv("API_BASE", f"http://localhost:8000/api/v1")

st.set_page_config(page_title="News Alert Dashboard", layout="wide")
st.title("News Alert Dashboard")

# Auto-refresh only the feed tab
st_autorefresh(interval=30_000, key="feed_refresh")  # 30 seconds

# Fixed allowed topics
AVAILABLE_TOPICS = ["technology", "business", "science", "politics", "health"]

# Tabs
tab_feed, tab_subscribe, tab_manage = st.tabs(["News Feed", "Subscribe", "Manage Subscribers"])

# ==================== TAB 1: News Feed ====================
with tab_feed:
    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.subheader("Latest Articles")

        if st.button("Fetch Latest News"):
            with st.spinner("Fetching new articles..."):
                try:
                    r = requests.post(f"{API_BASE}/news/fetch/")
                    r.raise_for_status()
                    count = r.json().get("new_count", 0)
                    if count > 0:
                        st.success(f"Added {count} new articles")
                    else:
                        st.info("No new articles found")
                except Exception as e:
                    st.error("Fetch failed")

        # Load news
        try:
            resp = requests.get(f"{API_BASE}/news/?limit=200")
            resp.raise_for_status()
            news = resp.json()
        except Exception as e:
            st.error("Failed to load articles")
            news = []

        if not news:
            st.info("No articles yet. Click 'Fetch Latest News' to begin.")
            st.stop()

        df = pd.DataFrame(news)
        df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

        # Filters in sidebar
        with st.sidebar:
            st.header("Filters")
            search_query = st.text_input("Search title or summary")
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
            mask = (filtered["title"].str.lower().str.contains(q, na=False) |
                    filtered["summary"].str.lower().str.contains(q, na=False))
            filtered = filtered[mask]
        if selected_sources:
            filtered = filtered[filtered["source"].isin(selected_sources)]
        if selected_categories:
            filtered = filtered[filtered["category"].isin(selected_categories)]
        filtered = filtered[
            (filtered["published_at"].dt.date >= start_date) &
            (filtered["published_at"].dt.date <= end_date)
        ]

        # Highlight new items
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

            card_style = """
                <div style="
                    border-left: 4px solid #4CAF50;
                    background-color: #f8fff8;
                    padding: 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                ">
            """ if is_new else """
                <div style="
                    padding: 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    background-color: white;
                    border: 1px solid #eee;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                ">
            """
            st.markdown(card_style, unsafe_allow_html=True)

            st.markdown(f"**{item['title']}**")
            meta = f"**Source:** {item.get('source', 'Unknown')} | "
            meta += f"**Category:** {item.get('category', 'uncategorized')} | "
            meta += f"**Published:** {item['published_at'].strftime('%b %d, %Y at %H:%M UTC')}"
            st.caption(meta)

            if item.get("summary"):
                st.write(item["summary"])
            if item.get("link"):
                st.markdown(f"[Read full article]({item['link']})")

            if st.button("Send Alert", key=f"alert_{item['id']}"):
                with st.spinner("Sending..."):
                    try:
                        r = requests.post(f"{API_BASE}/alerts/{item['id']}")
                        r.raise_for_status()
                        data = r.json()
                        sent_count = data.get("sent_count", 0)
                        msg = data.get("message", "")
                        if sent_count > 0:
                            st.success(f"Alert sent to {sent_count} subscriber(s)")
                        else:
                            st.info(msg or "No subscribers for this category")
                    except Exception:
                        st.error("Failed to send alert")

            st.markdown("</div>", unsafe_allow_html=True)

    # Alert History
    with col_side:
        st.subheader("Recent Alerts")
        try:
            r = requests.get(f"{API_BASE}/alerts/?limit=10")
            r.raise_for_status()
            alerts = r.json().get("alerts", [])
        except Exception:
            st.error("Failed to load alerts")
            alerts = []

        if alerts:
            for alert in reversed(alerts):
                status = "Sent" if alert.get("sent") else "Failed"
                time = pd.to_datetime(alert.get("sent_at")).strftime("%b %d, %Y %H:%M") if alert.get("sent_at") else "N/A"
                st.markdown(f"**To:** {alert.get('to')}\n\n**Status:** {status} at {time}")
                st.markdown("---")
        else:
            st.info("No alerts sent yet.")

# ==================== TAB 2: Subscribe ====================
with tab_subscribe:
    st.header("Subscribe to News Alerts")
    st.write("Get the latest news delivered to your inbox based on your interests.")

    with st.form("subscription_form", clear_on_submit=True):
        email = st.text_input("Email address", placeholder="you@example.com")
        topics = st.multiselect(
            "Select topics of interest",
            options=AVAILABLE_TOPICS,
            help="You'll receive alerts only for selected topics"
        )
        submitted = st.form_submit_button("Subscribe")

        if submitted:
            if not email:
                st.error("Email is required")
            elif not topics:
                st.warning("Please select at least one topic")
            else:
                with st.spinner("Subscribing..."):
                    try:
                        r = requests.post(f"{API_BASE}/subscribers/", json={"email": email, "topics": topics})
                        if r.status_code == 201:
                            st.success("Thank you! You're now subscribed.")
                        elif r.status_code == 409:
                            st.info("This email is already subscribed.")
                        else:
                            r.raise_for_status()
                    except requests.HTTPError as e:
                        if e.response.status_code == 409:
                            st.info("Already subscribed")
                        else:
                            st.error("Subscription failed")
                    except Exception:
                        st.error("Connection error")

    st.info("To unsubscribe, use the 'Manage Subscribers' tab or contact the administrator.")

# ==================== TAB 3: Manage Subscribers (Admin) ====================
with tab_manage:
    st.header("Manage Subscribers")
    st.write("View and remove subscribers (admin only in production).")

    try:
        r = requests.get(f"{API_BASE}/subscribers/")
        r.raise_for_status()
        subscribers = r.json()
    except Exception as e:
        st.error("Failed to load subscribers")
        subscribers = []

    if not subscribers:
        st.info("No subscribers yet.")
    else:
        df_subs = pd.DataFrame(subscribers)
        df_subs["topics"] = df_subs["topics"].apply(lambda t: ", ".join(t) if t else "All topics")

        st.dataframe(
            df_subs[["email", "topics"]],
            use_container_width=True,
            hide_index=True
        )

        st.write("### Remove Subscriber")
        email_to_remove = st.text_input("Enter email to unsubscribe")
        if st.button("Remove Subscriber"):
            if not email_to_remove:
                st.error("Enter an email")
            else:
                with st.spinner("Removing..."):
                    try:
                        r = requests.delete(f"{API_BASE}/subscribers/{email_to_remove}")
                        r.raise_for_status()
                        st.success("Subscriber removed successfully")
                        st.rerun()  # Refresh the page
                    except requests.HTTPError as e:
                        if e.response.status_code == 404:
                            st.error("Subscriber not found")
                        else:
                            st.error("Removal failed")
                    except Exception:
                        st.error("Connection error")
