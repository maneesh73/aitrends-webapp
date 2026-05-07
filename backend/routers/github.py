from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Repository
from schemas import RepositoryOut, PaginatedResponse, FetchStatus
from services import github_service
from auth import require_sync_auth

router = APIRouter(prefix="/api/github", tags=["github"])


@router.get("/repos", response_model=PaginatedResponse)
def get_repos(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    language: str = Query(""),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(Repository)
    if language:
        query = query.filter(Repository.language.ilike(f"%{language}%"))
    if search:
        query = query.filter(
            Repository.name.ilike(f"%{search}%") | Repository.description.ilike(f"%{search}%")
        )
    total = query.count()
    items = (
        query.order_by(desc(Repository.stars))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[RepositoryOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def fetch_repos(db: Session = Depends(get_db)):
    repos = await github_service.fetch_trending_repos()
    for topic in ["llm", "ai-agent", "langchain", "stable-diffusion"]:
        repos += await github_service.fetch_repos_by_topic(topic)
    saved = github_service.save_repos(db, repos)
    return FetchStatus(status="ok", fetched=saved, message=f"Saved {saved} new repositories")
