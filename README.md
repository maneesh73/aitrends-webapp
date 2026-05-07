# AI Pulse — AI News, Research & Trends Hub

A full-stack web app aggregating AI news, research papers, GitHub repos, courses, agents/tools, trends, and videos.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI + SQLAlchemy + SQLite |
| Frontend | React + Vite + Tailwind CSS |
| External APIs | NewsAPI, GitHub API, arXiv, HuggingFace, YouTube, Google News RSS |

## Quick Start

### 1. Set up environment variables

```bash
cd backend
cp .env.example .env
# Edit .env and fill in your keys
```

| Variable | Where to get it | Required? |
|----------|----------------|-----------|
| `SYNC_SECRET_KEY` | Set any strong secret string | **Yes** — gates all sync operations |
| `NEWS_API_KEY` | https://newsapi.org | Optional (20 RSS feeds + Google News work without it) |
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
- News from 20 RSS feeds + 8 Google News queries (no API key needed)
- arXiv papers from cs.AI, cs.LG, cs.CL, cs.CV
- GitHub trending AI repos

---

## Admin Sync Access

All content sync endpoints are protected. Only an admin with the correct key can trigger a sync.

### How it works

1. The `SYNC_SECRET_KEY` value is set in `backend/.env` — never exposed in frontend code
2. In the UI, a **🔒 lock icon** sits in the top-right of every page
3. Clicking it opens a modal to enter the key
4. If correct, the key is saved to `localStorage` and the **Sync button appears**
5. Clicking **🔓** (or clearing `localStorage`) hides the Sync button again
6. If the key is ever revoked or changed on the server, the next Sync returns 403 and the UI auto-locks

**Regular visitors never see the Sync button.**

### API-level enforcement

Every write endpoint requires an `x-sync-key` header matching `SYNC_SECRET_KEY`:

```bash
# Correct key → 200 OK
curl -X POST http://localhost:8000/api/news/fetch \
     -H "x-sync-key: your-secret-key"

# Missing or wrong key → 403 Forbidden
curl -X POST http://localhost:8000/api/news/fetch
```

Protected endpoints:
- `POST /api/news/fetch`
- `POST /api/research/fetch`
- `POST /api/github/fetch`
- `POST /api/agents/fetch`
- `POST /api/courses/fetch`
- `POST /api/trends/fetch`
- `POST /api/seed-all`

---

## News Sources

The news section pulls from **28 sources** on every sync:

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

### Google News RSS (8 queries — free, no API key)
`artificial intelligence` · `large language model` · `AI agents 2025` · `generative AI` · `machine learning research` · `OpenAI GPT` · `Claude Anthropic` · `AI regulation policy`

### NewsAPI (5 parallel queries — requires `NEWS_API_KEY`)
`artificial intelligence` · `large language model` · `AI agent autonomous` · `generative AI startup` · `machine learning research`

---

## Sections

| Section | Source | Sync endpoint |
|---------|--------|---------------|
| AI News | 20 RSS feeds + Google News + NewsAPI | `POST /api/news/fetch` |
| Research | arXiv API (cs.AI, cs.LG, cs.CL, cs.CV, stat.ML) | `POST /api/research/fetch` |
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
│   ├── main.py             # FastAPI app, CORS, router registration, /api/seed-all
│   ├── auth.py             # require_sync_auth dependency (x-sync-key header check)
│   ├── config.py           # Settings loaded from .env (incl. SYNC_SECRET_KEY)
│   ├── database.py         # SQLAlchemy SQLite setup
│   ├── models.py           # DB models: Article, Repository, Paper, Course, AITool, Video, TrendTopic
│   ├── schemas.py          # Pydantic response schemas
│   ├── requirements.txt
│   ├── .env.example        # Template — copy to .env and fill in values
│   ├── services/           # External API integrations
│   │   ├── news_service.py         (20 RSS feeds + Google News RSS + NewsAPI multi-query)
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
│       └── trends.py       (GET paginated + POST /fetch — auth protected)
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Topbar.jsx      # Lock/unlock modal + Sync button (admin only)
    │   │   ├── Sidebar.jsx
    │   │   ├── SearchBar.jsx
    │   │   ├── Pagination.jsx
    │   │   ├── LoadingSpinner.jsx
    │   │   └── EmptyState.jsx
    │   ├── pages/              # One page per section
    │   │   ├── Home.jsx
    │   │   ├── News.jsx
    │   │   ├── Research.jsx
    │   │   ├── Courses.jsx
    │   │   ├── GitHub.jsx
    │   │   ├── Agents.jsx
    │   │   ├── Trends.jsx
    │   │   └── Videos.jsx
    │   └── hooks/
    │       └── useFetch.js     # usePaginatedFetch hook
    ├── tailwind.config.js      # Custom dark theme tokens
    └── vite.config.js          # Proxies /api → localhost:8000
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

The database acts as a local cache — content is fetched from external APIs and stored so the UI stays fast regardless of external API availability. Duplicate URLs/IDs are skipped on every sync.
