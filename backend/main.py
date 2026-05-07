from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from config import settings
from routers import news, github, research, courses, agents, trends
from auth import require_sync_auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Trends API",
    description="Aggregated AI news, research, tools, courses and trends",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(github.router)
app.include_router(research.router)
app.include_router(courses.router)
app.include_router(agents.router)
app.include_router(trends.router)


@app.get("/")
def root():
    return {"message": "AI Trends API", "docs": "/docs"}


@app.post("/api/seed-all", dependencies=[Depends(require_sync_auth)])
async def seed_all():
    from database import SessionLocal
    from services import news_service, github_service, arxiv_service
    from routers.agents import CURATED_TOOLS
    from routers.courses import CURATED_COURSES
    from routers.trends import SEED_TRENDS
    from models import AITool, Course, TrendTopic

    db = SessionLocal()
    results = {}
    try:
        rss = news_service.fetch_rss_articles()
        results["news"] = news_service.save_articles(db, rss)

        repos = await github_service.fetch_trending_repos()
        results["repos"] = github_service.save_repos(db, repos)

        papers = await arxiv_service.fetch_papers("cs.AI", max_results=20)
        results["papers"] = arxiv_service.save_papers(db, papers)

        saved_tools = 0
        for tool in CURATED_TOOLS:
            if not db.query(AITool).filter(AITool.name == tool["name"]).first():
                db.add(AITool(**tool))
                saved_tools += 1
        db.commit()
        results["tools"] = saved_tools

        saved_courses = 0
        for course in CURATED_COURSES:
            if not db.query(Course).filter(Course.url == course["url"]).first():
                db.add(Course(**course))
                saved_courses += 1
        db.commit()
        results["courses"] = saved_courses

        saved_trends = 0
        for trend in SEED_TRENDS:
            if not db.query(TrendTopic).filter(TrendTopic.topic == trend["topic"]).first():
                db.add(TrendTopic(**trend))
                saved_trends += 1
        db.commit()
        results["trends"] = saved_trends

    finally:
        db.close()

    return {"status": "ok", "seeded": results}
