from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Article
from schemas import ArticleOut, PaginatedResponse, FetchStatus
from services import news_service
from auth import require_sync_auth

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=PaginatedResponse)
def get_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: str = Query(""),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(Article)
    if category:
        query = query.filter(Article.category == category)
    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(desc(Article.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[ArticleOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def fetch_news(db: Session = Depends(get_db)):
    rss_articles = news_service.fetch_rss_articles()
    google_articles = news_service.fetch_google_news_rss()
    newsapi_articles = await news_service.fetch_from_newsapi_multi()
    all_articles = rss_articles + google_articles + newsapi_articles
    saved = news_service.save_articles(db, all_articles)
    sources = len(news_service.AI_RSS_FEEDS) + len(news_service.GOOGLE_NEWS_QUERIES)
    return FetchStatus(status="ok", fetched=saved, message=f"Fetched from {sources} sources, saved {saved} new articles")
