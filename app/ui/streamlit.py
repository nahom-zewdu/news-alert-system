# app/ui/streamlit.py
"""
Streamlit demo UI for News Alert System
Clean, simple, and beautiful dashboard.
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

# Sidebar
st.sidebar.header("Settings")
refresh_interval = st.sidebar.slider("Auto-refresh (seconds)", 10, 120, 30)
st.sidebar.caption(f"API: {API_BASE}")

search_query = st.sidebar.text_input("Search in title or summary")

# Auto-refresh
st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Session state for new item highlighting
if "last_seen_ids" not in st.session_state:
    st.session_state.last_seen_ids = set()
if "highlight_until" not in st.session_state:
    st.session_state.highlight_until = {}

now = datetime.now(timezone.utc)

# Columns
col_main, col_side = st.columns([3, 1])

# Main panel
with col_main:
    st.subheader("News Feed")

    # Manual fetch
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
                st.error(f"Error: {e}")

    # Load news
    try:
        resp = requests.get(f"{API_BASE}/news/?limit=200")
        resp.raise_for_status()
        news = resp.json()
    except Exception as e:
        st.error(f"Failed to load news: {e}")
        news = []

    if not news:
        st.info("No articles available yet. Click 'Fetch Latest News' to start.")
        st.stop()

    df = pd.DataFrame(news)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)

    # Sidebar filters: Source & Category
    sources = sorted(df["source"].dropna().unique())
    categories = sorted(df["category"].dropna().unique())

    selected_sources = st.sidebar.multiselect("Source", options=sources)
    selected_categories = st.sidebar.multiselect("Category", options=categories)

    # Simple time period filter
    st.sidebar.subheader("Time Period")
    period_options = {
        "Today": (now.date(), now.date()),
        "Last 7 days": (now.date() - timedelta(days=6), now.date()),
        "Last 30 days": (now.date() - timedelta(days=29), now.date()),
        "This year": (datetime(now.year, 1, 1).date(), now.date()),
        "All time": (df["published_at"].dt.date.min(), df["published_at"].dt.date.max()),
    }

    selected_period = st.sidebar.radio("Show articles from", options=list(period_options.keys()), index=2)

    start_date, end_date = period_options[selected_period]

    # Apply all filters
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

    # Detect new items
    current_ids = set(filtered["id"])
    new_ids = current_ids - st.session_state.last_seen_ids
    for nid in new_ids:
        st.session_state.highlight_until[nid] = now.timestamp() + 10  # 10 seconds highlight
    st.session_state.last_seen_ids = current_ids

    # Display articles
    for _, row in filtered.sort_values("published_at", ascending=False).iterrows():
        item = row.to_dict()
        is_new = now.timestamp() < st.session_state.highlight_until.get(item["id"], 0)

        # Card style
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
            with st.spinner("Sending..."):
                try:
                    r = requests.post(f"{API_BASE}/alerts/{item['id']}")
                    r.raise_for_status()
                    st.success("Alert sent")
                except Exception as e:
                    st.error("Failed to send alert")

        st.markdown("</div>", unsafe_allow_html=True)

# Side panel: Alert History
with col_side:
    st.subheader("Alert History")

    try:
        r = requests.get(f"{API_BASE}/alerts/")
        r.raise_for_status()
        alerts = r.json().get("alerts", [])
    except Exception:
        st.error("Failed to load alerts")
        alerts = []

    if alerts:
        for alert in reversed(alerts):
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
