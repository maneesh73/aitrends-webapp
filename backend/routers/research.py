from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Paper
from schemas import PaperOut, PaginatedResponse, FetchStatus
from services import arxiv_service
from auth import require_sync_auth

router = APIRouter(prefix="/api/research", tags=["research"])


@router.get("/papers", response_model=PaginatedResponse)
def get_papers(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: str = Query(""),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(Paper)
    if category:
        query = query.filter(Paper.categories.contains(category))
    if search:
        query = query.filter(
            Paper.title.ilike(f"%{search}%") | Paper.abstract.ilike(f"%{search}%")
        )
    total = query.count()
    items = (
        query.order_by(desc(Paper.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[PaperOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def fetch_papers(db: Session = Depends(get_db)):
    total_saved = 0
    for cat in arxiv_service.AI_CATEGORIES:
        papers = await arxiv_service.fetch_papers(category=cat, max_results=15)
        total_saved += arxiv_service.save_papers(db, papers)
    for query in ["AI agent", "large language model", "multimodal AI"]:
        papers = await arxiv_service.search_papers(query=query, max_results=10)
        total_saved += arxiv_service.save_papers(db, papers)
    return FetchStatus(status="ok", fetched=total_saved, message=f"Saved {total_saved} new papers")
