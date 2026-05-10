import asyncio
import logging
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="UTC")

JOB_DEFINITIONS = {
    "news": {
        "name": "AI News",
        "description": "Fetches AI news from RSS feeds, Google News, Reddit, and The Guardian API",
        "default_cron": "0 */6 * * *",
        "sources": [
            {"name": "MIT Technology Review", "type": "RSS"},
            {"name": "The Verge - AI", "type": "RSS"},
            {"name": "VentureBeat AI", "type": "RSS"},
            {"name": "AI News", "type": "RSS"},
            {"name": "Towards Data Science", "type": "RSS"},
            {"name": "Wired - AI", "type": "RSS"},
            {"name": "TechCrunch - AI", "type": "RSS"},
            {"name": "ZDNet - AI", "type": "RSS"},
            {"name": "The Register - AI", "type": "RSS"},
            {"name": "Ars Technica", "type": "RSS"},
            {"name": "Analytics Vidhya", "type": "RSS"},
            {"name": "KDnuggets", "type": "RSS"},
            {"name": "Machine Learning Mastery", "type": "RSS"},
            {"name": "Import AI (Jack Clark)", "type": "RSS"},
            {"name": "The Gradient", "type": "RSS"},
            {"name": "Synced Review", "type": "RSS"},
            {"name": "Unite.AI", "type": "RSS"},
            {"name": "Marktechpost", "type": "RSS"},
            {"name": "The Batch (DeepLearning.AI)", "type": "RSS"},
            {"name": "Hugging Face Blog", "type": "RSS"},
            {"name": "Google News: artificial intelligence", "type": "Google News"},
            {"name": "Google News: large language model", "type": "Google News"},
            {"name": "Google News: AI agents", "type": "Google News"},
            {"name": "Google News: generative AI", "type": "Google News"},
            {"name": "Google News: machine learning research", "type": "Google News"},
            {"name": "Google News: OpenAI GPT", "type": "Google News"},
            {"name": "Google News: Claude Anthropic", "type": "Google News"},
            {"name": "Google News: AI regulation policy", "type": "Google News"},
            {"name": "Google News: AI safety alignment", "type": "Google News"},
            {"name": "Google News: deep learning neural network", "type": "Google News"},
            {"name": "Google News: AI startup funding", "type": "Google News"},
            {"name": "Google News: robotics automation AI", "type": "Google News"},
            {"name": "Google News: NLP", "type": "Google News"},
            {"name": "Google News: computer vision AI", "type": "Google News"},
            {"name": "Google News: AI healthcare", "type": "Google News"},
            {"name": "Google News: AI chip semiconductor", "type": "Google News"},
            {"name": "Google News: multimodal AI model", "type": "Google News"},
            {"name": "Google News: reinforcement learning", "type": "Google News"},
            {"name": "Google News: open source AI model", "type": "Google News"},
            {"name": "Google News: AI ethics bias", "type": "Google News"},
            {"name": "Reddit r/MachineLearning", "type": "Reddit RSS"},
            {"name": "Reddit r/artificial", "type": "Reddit RSS"},
            {"name": "Reddit r/AINews", "type": "Reddit RSS"},
            {"name": "Reddit r/LocalLLaMA", "type": "Reddit RSS"},
            {"name": "Reddit r/ChatGPT", "type": "Reddit RSS"},
            {"name": "Reddit r/singularity", "type": "Reddit RSS"},
            {"name": "Reddit r/deeplearning", "type": "Reddit RSS"},
            {"name": "The Guardian API (5 queries)", "type": "API", "note": "Requires GUARDIAN_API_KEY"},
        ],
    },
    "github": {
        "name": "GitHub Repos",
        "description": "Fetches trending AI repositories from GitHub search and topic pages",
        "default_cron": "0 */12 * * *",
        "sources": [
            {"name": "GitHub search: artificial intelligence", "type": "GitHub API"},
            {"name": "GitHub search: machine learning", "type": "GitHub API"},
            {"name": "GitHub search: deep learning", "type": "GitHub API"},
            {"name": "GitHub search: large language model", "type": "GitHub API"},
            {"name": "GitHub search: AI agent", "type": "GitHub API"},
            {"name": "GitHub search: neural network", "type": "GitHub API"},
            {"name": "GitHub search: transformer model", "type": "GitHub API"},
            {"name": "GitHub topic: llm", "type": "GitHub API"},
            {"name": "GitHub topic: ai-agent", "type": "GitHub API"},
            {"name": "GitHub topic: langchain", "type": "GitHub API"},
            {"name": "GitHub topic: stable-diffusion", "type": "GitHub API"},
        ],
    },
    "research": {
        "name": "Research Papers",
        "description": "Fetches latest AI research papers from arXiv across 6 categories",
        "default_cron": "0 */8 * * *",
        "sources": [
            {"name": "arXiv cs.AI (Artificial Intelligence)", "type": "arXiv API"},
            {"name": "arXiv cs.LG (Machine Learning)", "type": "arXiv API"},
            {"name": "arXiv cs.CL (Computation & Language)", "type": "arXiv API"},
            {"name": "arXiv cs.CV (Computer Vision)", "type": "arXiv API"},
            {"name": "arXiv cs.RO (Robotics)", "type": "arXiv API"},
            {"name": "arXiv stat.ML (Statistics & ML)", "type": "arXiv API"},
            {"name": "arXiv search: AI agent", "type": "arXiv API"},
            {"name": "arXiv search: large language model", "type": "arXiv API"},
            {"name": "arXiv search: multimodal AI", "type": "arXiv API"},
        ],
    },
    "courses": {
        "name": "Courses",
        "description": "Seeds curated AI course list and fetches educational YouTube videos",
        "default_cron": "0 0 * * 0",
        "sources": [
            {"name": "Curated course list (12 courses)", "type": "Curated"},
            {"name": "YouTube: machine learning tutorial 2025", "type": "YouTube API", "note": "Requires YOUTUBE_API_KEY"},
            {"name": "YouTube: AI agent course", "type": "YouTube API"},
            {"name": "YouTube: LLM fine-tuning tutorial", "type": "YouTube API"},
        ],
    },
    "agents": {
        "name": "AI Tools & Agents",
        "description": "Seeds curated AI tools and fetches trending HuggingFace models and spaces",
        "default_cron": "0 0 * * 0",
        "sources": [
            {"name": "Curated tools list (12 tools)", "type": "Curated"},
            {"name": "HuggingFace trending text-generation models", "type": "HuggingFace API"},
            {"name": "HuggingFace trending spaces", "type": "HuggingFace API"},
        ],
    },
    "videos": {
        "name": "Videos",
        "description": "Fetches AI-related YouTube videos across 5 search queries",
        "default_cron": "0 0 * * *",
        "sources": [
            {"name": "YouTube: artificial intelligence 2025", "type": "YouTube API", "note": "Requires YOUTUBE_API_KEY"},
            {"name": "YouTube: large language models tutorial", "type": "YouTube API"},
            {"name": "YouTube: AI agents explained", "type": "YouTube API"},
            {"name": "YouTube: machine learning course", "type": "YouTube API"},
            {"name": "YouTube: ChatGPT Claude Gemini comparison", "type": "YouTube API"},
        ],
    },
    "trends": {
        "name": "Trend Topics",
        "description": "Refreshes AI trending topic mention counts from curated seed data",
        "default_cron": "0 0 * * *",
        "sources": [
            {"name": "Curated AI trend topics (15 topics)", "type": "Curated"},
        ],
    },
}


def _update_job_status(job_id: str, status: str, message: str):
    from database import SessionLocal
    from models import SyncJobConfig
    db = SessionLocal()
    try:
        cfg = db.query(SyncJobConfig).filter(SyncJobConfig.id == job_id).first()
        if cfg:
            cfg.last_run_at = datetime.utcnow()
            cfg.last_run_status = status
            cfg.last_run_message = message[:500]
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update job status for {job_id}: {e}")
    finally:
        db.close()


def _run_news():
    from database import SessionLocal
    from services import news_service
    db = SessionLocal()
    try:
        articles = (
            news_service.fetch_rss_articles()
            + news_service.fetch_google_news_rss()
            + news_service.fetch_reddit_rss()
            + news_service.fetch_guardian_articles()
        )
        saved = news_service.save_articles(db, articles)
        _update_job_status("news", "ok", f"Saved {saved} new articles from {len(articles)} fetched")
    except Exception as e:
        _update_job_status("news", "error", str(e)[:500])
        logger.error(f"News job failed: {e}")
    finally:
        db.close()


def _run_github():
    async def _fetch():
        from services import github_service
        repos = await github_service.fetch_trending_repos()
        for topic in ["llm", "ai-agent", "langchain", "stable-diffusion"]:
            repos += await github_service.fetch_repos_by_topic(topic)
        return repos

    from database import SessionLocal
    from services import github_service
    db = SessionLocal()
    try:
        repos = asyncio.run(_fetch())
        saved = github_service.save_repos(db, repos)
        _update_job_status("github", "ok", f"Saved {saved} new repos from {len(repos)} fetched")
    except Exception as e:
        _update_job_status("github", "error", str(e)[:500])
        logger.error(f"GitHub job failed: {e}")
    finally:
        db.close()


def _run_research():
    async def _fetch():
        from services import arxiv_service
        papers = []
        for cat in arxiv_service.AI_CATEGORIES:
            papers += await arxiv_service.fetch_papers(cat, max_results=15)
        for query in ["AI agent", "large language model", "multimodal AI"]:
            papers += await arxiv_service.search_papers(query, max_results=10)
        return papers

    from database import SessionLocal
    from services import arxiv_service
    db = SessionLocal()
    try:
        papers = asyncio.run(_fetch())
        saved = arxiv_service.save_papers(db, papers)
        _update_job_status("research", "ok", f"Saved {saved} new papers from {len(papers)} fetched")
    except Exception as e:
        _update_job_status("research", "error", str(e)[:500])
        logger.error(f"Research job failed: {e}")
    finally:
        db.close()


def _run_courses():
    async def _fetch_videos():
        from services import youtube_service
        videos = []
        for query in ["machine learning tutorial 2025", "AI agent course", "LLM fine-tuning tutorial"]:
            videos += await youtube_service.search_videos(query=query, max_results=5)
        return videos

    from database import SessionLocal
    from models import Course
    from routers.courses import CURATED_COURSES
    db = SessionLocal()
    try:
        saved = 0
        for course in CURATED_COURSES:
            if not db.query(Course).filter(Course.url == course["url"]).first():
                db.add(Course(**course))
                saved += 1
        db.commit()
        videos = asyncio.run(_fetch_videos())
        for v in videos:
            if not db.query(Course).filter(Course.url == v["url"]).first():
                db.add(Course(
                    title=v["title"],
                    description=v.get("description", ""),
                    url=v["url"],
                    provider="YouTube",
                    instructor=v.get("channel", ""),
                    thumbnail=v.get("thumbnail", ""),
                    level="Various",
                    duration="Video",
                    topics=["AI", "machine learning"],
                    is_free=True,
                ))
                saved += 1
        db.commit()
        _update_job_status("courses", "ok", f"Saved {saved} new courses")
    except Exception as e:
        _update_job_status("courses", "error", str(e)[:500])
        logger.error(f"Courses job failed: {e}")
    finally:
        db.close()


def _run_agents():
    async def _fetch_hf():
        from services import huggingface_service
        models = await huggingface_service.fetch_trending_models(limit=15)
        spaces = await huggingface_service.fetch_trending_spaces(limit=10)
        return models, spaces

    from database import SessionLocal
    from models import AITool
    from services import huggingface_service
    from routers.agents import CURATED_TOOLS
    db = SessionLocal()
    try:
        saved = 0
        for tool in CURATED_TOOLS:
            if not db.query(AITool).filter(AITool.name == tool["name"]).first():
                db.add(AITool(**tool))
                saved += 1
        db.commit()
        models, spaces = asyncio.run(_fetch_hf())
        saved += huggingface_service.save_hf_tools(db, models)
        saved += huggingface_service.save_hf_tools(db, spaces, is_agent=True)
        _update_job_status("agents", "ok", f"Saved {saved} new tools")
    except Exception as e:
        _update_job_status("agents", "error", str(e)[:500])
        logger.error(f"Agents job failed: {e}")
    finally:
        db.close()


def _run_videos():
    async def _fetch():
        from services import youtube_service
        videos = []
        for query in youtube_service.AI_YOUTUBE_QUERIES:
            videos += await youtube_service.search_videos(query=query, max_results=10)
        return videos

    from database import SessionLocal
    from services import youtube_service
    db = SessionLocal()
    try:
        videos = asyncio.run(_fetch())
        saved = youtube_service.save_videos(db, videos)
        _update_job_status("videos", "ok", f"Saved {saved} new videos from {len(videos)} fetched")
    except Exception as e:
        _update_job_status("videos", "error", str(e)[:500])
        logger.error(f"Videos job failed: {e}")
    finally:
        db.close()


def _run_trends():
    from database import SessionLocal
    from models import TrendTopic
    from routers.trends import SEED_TRENDS
    db = SessionLocal()
    try:
        saved = 0
        for trend in SEED_TRENDS:
            existing = db.query(TrendTopic).filter(TrendTopic.topic == trend["topic"]).first()
            if not existing:
                db.add(TrendTopic(**trend))
                saved += 1
            else:
                existing.mentions = trend["mentions"]
        db.commit()
        _update_job_status("trends", "ok", f"Refreshed {len(SEED_TRENDS)} trends, {saved} new")
    except Exception as e:
        _update_job_status("trends", "error", str(e)[:500])
        logger.error(f"Trends job failed: {e}")
    finally:
        db.close()


_JOB_FUNCS = {
    "news": _run_news,
    "github": _run_github,
    "research": _run_research,
    "courses": _run_courses,
    "agents": _run_agents,
    "videos": _run_videos,
    "trends": _run_trends,
}


def _schedule_apscheduler_job(job_id: str, cron_expr: str):
    func = _JOB_FUNCS.get(job_id)
    if not func:
        return
    try:
        trigger = CronTrigger.from_crontab(cron_expr, timezone="UTC")
        scheduler.add_job(func, trigger=trigger, id=job_id, replace_existing=True)
    except Exception as e:
        logger.error(f"Failed to schedule job {job_id}: {e}")


def reschedule_job(job_id: str, cron_expr: str, enabled: bool):
    if enabled:
        _schedule_apscheduler_job(job_id, cron_expr)
    else:
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass


def run_job_now(job_id: str) -> bool:
    func = _JOB_FUNCS.get(job_id)
    if not func:
        return False
    thread = threading.Thread(target=func, daemon=True, name=f"job-{job_id}-manual")
    thread.start()
    return True


def start_scheduler():
    from database import SessionLocal
    from models import SyncJobConfig

    db = SessionLocal()
    try:
        for job_id, defn in JOB_DEFINITIONS.items():
            cfg = db.query(SyncJobConfig).filter(SyncJobConfig.id == job_id).first()
            if not cfg:
                cfg = SyncJobConfig(id=job_id, cron_expr=defn["default_cron"], enabled=False)
                db.add(cfg)
        db.commit()

        for job_id in JOB_DEFINITIONS:
            cfg = db.query(SyncJobConfig).filter(SyncJobConfig.id == job_id).first()
            if cfg and cfg.enabled:
                _schedule_apscheduler_job(job_id, cfg.cron_expr)
    finally:
        db.close()

    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_next_run(job_id: str):
    job = scheduler.get_job(job_id)
    return job.next_run_time if job else None
