# **News Alert System**

A modular **news aggregation, classification, and alerting** platform built with **FastAPI** (backend) and **Streamlit** (UI).
It fetches RSS articles, classifies them via LLMs (Groq/OpenAI API-compatible), stores them in MongoDB, and provides a simple UI to explore news and alert history.

Designed for **extensibility**, **clear modular boundaries**, and **easy deployment**.

---

## 🚀 Features

* **RSS Fetching**
  Periodically pulls articles from configurable RSS feeds.

* **LLM-Powered Classification**
  Uses Groq’s API to categorize articles (tech, politics, business, etc.).

* **MongoDB Persistence**
  Stores news items and alerts for search, filtering, and history.

* **Modular Architecture**
  Clean separation between:

  * `core` (scheduler + config)
  * `infrastructure` (RSS + HTTP + DB clients)
  * `services` (fetching, classification, alerting)
  * `api` (FastAPI routes)
  * `ui` (Streamlit dashboard)

* **Background Scheduler**
  Runs automated fetching + processing in intervals.

* **Streamlit UI**
  Visualize latest news, categories, and alert history.

---

## 🧱 Project Structure

```text
app/
├─ api/                 # FastAPI routers
├─ core/                # config, scheduler
├─ infrastructure/      # rss client, database adapters, http clients
├─ services/            # fetching, classification, alerting logic
├─ models/              # pydantic + mongoengine models
├─ ui/                  # Streamlit dashboard
└─ entrypoints.py       # CLI script entrypoints
```

Clear boundaries mean you can replace any subsystem (e.g., swap RSS, DB, LLM) without touching others.

---

## 📦 Installation

Clone the repo and install the project with its dependencies:

```bash
git clone https://github.com/yourname/news-alert-system
cd news-alert-system
uv sync
```

Create a `.env` file:

```env
MONGO_URI=mongodb://localhost:27017/news
GROQ_API_KEY=your_key
RSS_FEEDS=https://news.ycombinator.com/rss,https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
FETCH_INTERVAL=30
```

---

## ▶️ Running the System

This project ships with multiple entrypoints:

### **Start the API**

```bash
uv run start
```

Runs FastAPI with Uvicorn.

### **Run in dev mode**

```bash
uv run dev
```

Hot-reload for local development.

### **Launch the UI**

```bash
uv run ui
```

Starts the Streamlit dashboard.

### **Run the Scheduler Standalone**

```bash
uv run scheduler
```

Useful for containerization or distributed setups.

---

## 🧠 How It Works (Short Overview)

1. **Scheduler triggers** `fetch_and_process` every X seconds.
2. **RSS Client** fetches raw items.
3. **Classifier** calls Groq LLM and assigns a category.
4. **DB Layer** stores new items and ignores duplicates.
5. **API** exposes `/news/` and `/alerts/`.
6. **Streamlit UI** displays categorized news + alert history.

Everything is fully asynchronous where it matters (HTTP, classification).

---

## 🛠 Configuration

Almost everything is configurable via environment variables:

| Variable         | Description                   |
| ---------------- | ----------------------------- |
| `RSS_FEEDS`      | Comma-separated URLs          |
| `GROQ_API_KEY`   | API key for classification    |
| `MONGO_URI`      | MongoDB connection            |
| `FETCH_INTERVAL` | Scheduler interval in seconds |

---

## 🧪 Testing (Optional Section)

```bash
pytest -q
```

---

## 📐 Tech Stack

* **Backend:** FastAPI, Uvicorn
* **UI:** Streamlit
* **Data Layer:** MongoEngine (MongoDB)
* **Scheduling:** Python `schedule` + custom wrapper
* **LLM Classification:** Groq (OpenAI-compatible API)
* **HTTP Client:** httpx
* **RSS Parsing:** feedparser
