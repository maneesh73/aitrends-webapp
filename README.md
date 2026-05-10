# AI Pulse — AI News, Research & Trends Hub

A full-stack web app aggregating AI news, research papers, GitHub repos, courses, agents/tools, trends, and videos.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI + SQLAlchemy + SQLite |
| Frontend | React + Vite + Tailwind CSS |
| Scheduler | APScheduler (background cron jobs, persisted in DB) |
| External APIs | GitHub API, arXiv, HuggingFace, YouTube, Google News RSS, The Guardian API, Reddit RSS |

## Quick Start

### 1. Set up environment variables

```bash
cd backend
cp .env.example .env
# Edit .env and fill in your keys
```

| Variable | Where to get it | Required? |
|----------|----------------|-----------|
| `SYNC_SECRET_KEY` | Set any strong secret string | **Yes** — gates all sync and admin operations |
| `GUARDIAN_API_KEY` | https://open-platform.theguardian.com (free) | Optional — adds Guardian news articles |
| `GITHUB_TOKEN` | GitHub → Settings → Developer settings | Optional (higher rate limits) |
| `HUGGINGFACE_API_KEY` | https://huggingface.co/settings/tokens | Optional |
| `YOUTUBE_API_KEY` | Google Cloud Console → YouTube Data API v3 | Optional |

### 2. Install & run backend

```bash
cd backend
~/.local/bin/uv venv .venv          # or: python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at http://localhost:8000 — API docs at http://localhost:8000/docs

> **Note:** This project uses [uv](https://github.com/astral-sh/uv) as the Python package manager.
> Install it with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 3. Install & run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

### 4. Load initial data

Visit http://localhost:5173, click the **🔒 lock icon** in the top bar, enter your `SYNC_SECRET_KEY`, then click **"Initialize & Load All Data"** on the home page.

This seeds:
- 12 curated AI courses (Coursera, fast.ai, Harvard, HuggingFace, etc.)
- 12 AI agents & frameworks (LangChain, AutoGPT, CrewAI, etc.)
- 15 trending AI topics
- News from 20 RSS feeds + 20 Google News queries + 7 Reddit subreddits (no API key needed)
- arXiv papers from cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML
- GitHub trending AI repos

---

## Admin Sync Scheduler

The app includes an admin panel at `/admin` for configuring automated cron schedules for each data source. **This page and its API are only accessible from localhost** — blocked at the nginx level for all remote connections.

### Accessing the admin panel

**On the server directly:**
```
http://localhost/ai/admin
```

**Via SSH tunnel from your local machine:**
```bash
ssh -L 8080:127.0.0.1:80 vps3ct@netizen9.com
# Then open: http://localhost:8080/ai/admin
```

Enter your `SYNC_SECRET_KEY` in the login screen (stored in localStorage for the session).

### What the admin panel shows

Each of the 7 data jobs has its own card displaying:

- **Enable/disable toggle** — whether the cron job is active
- **Schedule selector** — presets (every 1h / 3h / 6h / 12h / 24h / weekly) or a custom cron expression
- **Last run** — timestamp, status (✓ ok / ✗ error), and result message
- **Next run** — when the job is next scheduled to fire
- **Sources list** — expandable list of every feed, API, or dataset the job pulls from, with colour-coded type badges (RSS, Google News, Reddit RSS, API, GitHub API, arXiv API, YouTube API, HuggingFace API, Curated)
- **Run now** — triggers the job immediately in a background thread without affecting the schedule

### Scheduled jobs and their defaults

| Job | Default schedule | Sources |
|-----|-----------------|---------|
| AI News | Every 6 hours | 20 RSS feeds + 20 Google News queries + 7 Reddit subreddits + Guardian API |
| GitHub Repos | Every 12 hours | 7 GitHub search queries + 4 topic searches |
| Research Papers | Every 8 hours | 6 arXiv categories + 3 keyword searches |
| Videos | Every 24 hours | 5 YouTube search queries |
| Trend Topics | Every 24 hours | 15 curated seed topics |
| Courses | Weekly | 12 curated courses + 3 YouTube queries |
| AI Tools & Agents | Weekly | 12 curated tools + HuggingFace trending models + spaces |

All jobs start **disabled** by default. Enable them individually in the admin panel.

### Admin API endpoints (localhost only)

All require `x-sync-key` header matching `SYNC_SECRET_KEY`.

```bash
# List all jobs with status and sources
curl http://localhost:8000/api/admin/jobs -H "x-sync-key: your-key"

# Update schedule for a job (cron expression + enabled flag)
curl -X PUT http://localhost:8000/api/admin/jobs/news \
     -H "x-sync-key: your-key" \
     -H "Content-Type: application/json" \
     -d '{"cron_expr": "0 */6 * * *", "enabled": true}'

# Trigger a job immediately
curl -X POST http://localhost:8000/api/admin/jobs/news/run \
     -H "x-sync-key: your-key"
```

### nginx access restriction

Two location blocks in `nginx.conf` enforce localhost-only access, placed before the general `/api/` and `/ai/` blocks:

```nginx
# Admin API — localhost only
location /api/admin/ {
    allow 127.0.0.1;
    deny all;
    proxy_pass http://127.0.0.1:8000;
    ...
}

# Admin UI — localhost only
location ~ ^/ai/admin {
    allow 127.0.0.1;
    deny all;
    ...
}
```

Remote clients receive **403 Forbidden** for both the page and all API calls. The `SYNC_SECRET_KEY` provides a second layer of auth for localhost clients.

---

## Content Sync (manual triggers)

All content sync endpoints are also protected by `x-sync-key`. These can be called from anywhere with the key (unlike admin endpoints which are localhost-only).

```bash
# Correct key → 200 OK
curl -X POST http://localhost:8000/api/news/fetch \
     -H "x-sync-key: your-secret-key"

# Missing or wrong key → 403 Forbidden
curl -X POST http://localhost:8000/api/news/fetch
```

Protected sync endpoints:
- `POST /api/news/fetch`
- `POST /api/research/fetch`
- `POST /api/github/fetch`
- `POST /api/agents/fetch`
- `POST /api/courses/fetch`
- `POST /api/trends/fetch`
- `POST /api/seed-all`

---

## News Sources

The news section pulls from **48 sources** on every sync (no API key required except Guardian):

### RSS Feeds (20)
| Source | Feed |
|--------|------|
| MIT Technology Review | technologyreview.com/feed |
| The Verge — AI | theverge.com/rss/ai |
| VentureBeat AI | venturebeat.com/ai/feed |
| AI News | artificialintelligence-news.com/feed |
| Towards Data Science | towardsdatascience.com/feed |
| Wired — AI | wired.com/tag/artificial-intelligence |
| TechCrunch — AI | techcrunch.com/tag/artificial-intelligence |
| ZDNet — AI | zdnet.com/topic/artificial-intelligence |
| The Register | theregister.com/tag/ai |
| Ars Technica | arstechnica.com/technology-lab |
| Analytics Vidhya | analyticsvidhya.com/feed |
| KDnuggets | kdnuggets.com/feed |
| Machine Learning Mastery | machinelearningmastery.com/feed |
| Import AI (Jack Clark) | jack-clark.net/feed |
| The Gradient | thegradient.pub/rss |
| Synced Review | syncedreview.com/feed |
| Unite.AI | unite.ai/feed |
| Marktechpost | marktechpost.com/feed |
| The Batch (DeepLearning.AI) | deeplearning.ai/the-batch |
| Hugging Face Blog | huggingface.co/blog/feed.xml |

### Google News RSS (20 queries — free, no API key)
`artificial intelligence` · `large language model` · `AI agents` · `generative AI` · `machine learning research` · `OpenAI GPT` · `Claude Anthropic` · `AI regulation policy` · `AI safety alignment` · `deep learning neural network` · `AI startup funding` · `robotics automation AI` · `NLP` · `computer vision AI` · `AI healthcare` · `AI chip semiconductor` · `multimodal AI model` · `reinforcement learning` · `open source AI model` · `AI ethics bias`

### Reddit RSS (7 subreddits — free, no API key)
`r/MachineLearning` · `r/artificial` · `r/AINews` · `r/LocalLLaMA` · `r/ChatGPT` · `r/singularity` · `r/deeplearning`

### The Guardian API (5 queries — requires `GUARDIAN_API_KEY`)
`artificial intelligence` · `machine learning` · `large language model` · `generative AI` · `AI regulation`

---

## Sections

| Section | Source | Sync endpoint |
|---------|--------|---------------|
| AI News | 20 RSS feeds + 20 Google News + 7 Reddit + Guardian | `POST /api/news/fetch` |
| Research | arXiv API (cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML) | `POST /api/research/fetch` |
| Courses | Curated list + YouTube | `POST /api/courses/fetch` |
| GitHub | GitHub Search API | `POST /api/github/fetch` |
| Agents & Tools | Curated list + HuggingFace models/spaces | `POST /api/agents/fetch` |
| Trends | Curated seed data | `POST /api/trends/fetch` |
| Videos | YouTube Data API v3 | (requires `YOUTUBE_API_KEY`) |

---

## Project Structure

```
aitrends-webapp/
├── backend/
│   ├── main.py             # FastAPI app, CORS, router registration, lifespan (starts scheduler)
│   ├── scheduler.py        # APScheduler setup, job definitions, run functions for all 7 jobs
│   ├── auth.py             # require_sync_auth dependency (x-sync-key header check)
│   ├── config.py           # Settings loaded from .env
│   ├── database.py         # SQLAlchemy SQLite setup
│   ├── models.py           # DB models: Article, Repository, Paper, Course, AITool, Video,
│   │                       #            TrendTopic, SyncJobConfig
│   ├── schemas.py          # Pydantic response schemas
│   ├── requirements.txt
│   ├── .env.example        # Template — copy to .env and fill in values
│   ├── services/           # External API integrations
│   │   ├── news_service.py         (20 RSS feeds + Google News RSS + Reddit RSS + Guardian API)
│   │   ├── github_service.py       (GitHub Search API)
│   │   ├── arxiv_service.py        (arXiv API — no key needed)
│   │   ├── huggingface_service.py  (HuggingFace models + spaces)
│   │   └── youtube_service.py      (YouTube Data API v3)
│   └── routers/            # One FastAPI router per section
│       ├── news.py         (GET paginated + POST /fetch — auth protected)
│       ├── github.py       (GET paginated + POST /fetch — auth protected)
│       ├── research.py     (GET paginated + POST /fetch — auth protected)
│       ├── courses.py      (GET paginated + POST /fetch — auth protected)
│       ├── agents.py       (GET paginated + POST /fetch — auth protected)
│       ├── trends.py       (GET paginated + POST /fetch — auth protected)
│       └── admin.py        (GET/PUT /jobs, POST /jobs/{id}/run — localhost only)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Topbar.jsx      # Lock/unlock modal + Sync button (admin only)
│   │   │   ├── Sidebar.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   ├── Pagination.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   └── EmptyState.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── News.jsx
│   │   │   ├── Research.jsx
│   │   │   ├── Courses.jsx
│   │   │   ├── GitHub.jsx
│   │   │   ├── Agents.jsx
│   │   │   ├── Trends.jsx
│   │   │   ├── Videos.jsx
│   │   │   └── Admin.jsx       # Sync scheduler UI — localhost only, requires SYNC_SECRET_KEY
│   │   └── hooks/
│   │       └── useFetch.js     # usePaginatedFetch hook
│   ├── tailwind.config.js      # Custom dark theme tokens
│   └── vite.config.js          # Proxies /api → localhost:8000
└── nginx.conf                  # Nginx config with localhost-only blocks for /api/admin/ and /ai/admin
```

---

## Database

SQLite file at `backend/aitrends.db`. Tables:

| Table | Contents |
|-------|---------|
| `articles` | News articles (title, url, source, published_at, tags) |
| `repositories` | GitHub repos (name, stars, forks, language, topics) |
| `papers` | arXiv papers (arxiv_id, title, abstract, authors, categories) |
| `courses` | AI courses (title, provider, level, is_free, topics) |
| `ai_tools` | Agents & frameworks (name, category, is_agent, stars, tags) |
| `videos` | YouTube videos (video_id, title, channel, view_count, summary) |
| `trend_topics` | Trending topics (topic, mentions, category) |
| `sync_job_configs` | Cron job settings (id, cron_expr, enabled, last_run_at, last_run_status, last_run_message) |

The database acts as a local cache — content is fetched from external APIs and stored so the UI stays fast regardless of external API availability. Duplicate URLs/IDs are skipped on every sync.
