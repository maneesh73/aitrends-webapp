from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models import TrendTopic, Article, Paper, Repository
from auth import require_sync_auth
from schemas import TrendTopicOut, PaginatedResponse, FetchStatus

router = APIRouter(prefix="/api/trends", tags=["trends"])

SEED_TRENDS = [
    {"topic": "Large Language Models (LLMs)", "description": "Massive neural language models like GPT-4, Claude, Gemini driving AI capabilities.", "mentions": 9800, "source": "multiple", "category": "Models", "url": ""},
    {"topic": "AI Agents & Autonomy", "description": "Autonomous AI systems that plan and execute multi-step tasks using tools.", "mentions": 7600, "source": "multiple", "category": "Agents", "url": ""},
    {"topic": "Retrieval-Augmented Generation (RAG)", "description": "Grounding LLM responses with external knowledge retrieval.", "mentions": 6400, "source": "arxiv", "category": "Technique", "url": ""},
    {"topic": "Multimodal AI", "description": "Models that handle text, images, audio, and video together (GPT-4V, Gemini).", "mentions": 5900, "source": "multiple", "category": "Models", "url": ""},
    {"topic": "Open-Source LLMs", "description": "Llama 3, Mistral, Falcon — powerful open models challenging closed ones.", "mentions": 5200, "source": "github", "category": "Models", "url": ""},
    {"topic": "AI Coding Assistants", "description": "GitHub Copilot, Cursor, Devin — AI transforming software development.", "mentions": 4800, "source": "multiple", "category": "Tools", "url": ""},
    {"topic": "Fine-tuning & RLHF", "description": "Customizing pre-trained models with domain data and human feedback.", "mentions": 4100, "source": "arxiv", "category": "Technique", "url": ""},
    {"topic": "Vector Databases", "description": "Pinecone, Weaviate, Qdrant — specialized DBs for LLM memory and retrieval.", "mentions": 3700, "source": "github", "category": "Infrastructure", "url": ""},
    {"topic": "On-Device AI / Edge Inference", "description": "Running AI models locally on phones, laptops, and edge hardware.", "mentions": 3500, "source": "multiple", "category": "Infrastructure", "url": ""},
    {"topic": "AI Safety & Alignment", "description": "Research on making AI systems safe, aligned with human values.", "mentions": 3200, "source": "arxiv", "category": "Research", "url": ""},
    {"topic": "Diffusion Models", "description": "Image/video generation models like DALL-E 3, Stable Diffusion, Sora.", "mentions": 3000, "source": "multiple", "category": "Models", "url": ""},
    {"topic": "AI in Healthcare", "description": "Medical imaging, drug discovery, clinical AI applications.", "mentions": 2800, "source": "arxiv", "category": "Application", "url": ""},
    {"topic": "Graph Neural Networks", "description": "GNNs applied to molecule design, knowledge graphs, and social networks.", "mentions": 2400, "source": "arxiv", "category": "Research", "url": ""},
    {"topic": "Federated Learning", "description": "Training ML models across distributed devices without centralizing data.", "mentions": 2100, "source": "arxiv", "category": "Technique", "url": ""},
    {"topic": "Prompt Engineering", "description": "Systematic techniques for crafting effective LLM prompts.", "mentions": 1900, "source": "multiple", "category": "Technique", "url": ""},
]


@router.get("", response_model=PaginatedResponse)
def get_trends(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
    category: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(TrendTopic)
    if category:
        query = query.filter(TrendTopic.category == category)
    total = query.count()
    items = (
        query.order_by(desc(TrendTopic.mentions))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[TrendTopicOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "articles": db.query(Article).count(),
        "repositories": db.query(Repository).count(),
        "papers": db.query(Paper).count(),
        "trends": db.query(TrendTopic).count(),
    }


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def seed_trends(db: Session = Depends(get_db)):
    saved = 0
    for trend in SEED_TRENDS:
        existing = db.query(TrendTopic).filter(TrendTopic.topic == trend["topic"]).first()
        if not existing:
            db.add(TrendTopic(**trend))
            saved += 1
        else:
            existing.mentions = trend["mentions"]
    db.commit()
    return FetchStatus(status="ok", fetched=saved, message=f"Seeded {saved} trends")


@router.get("/videos", response_model=PaginatedResponse)
def get_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    from models import Video
    from schemas import VideoOut
    query = db.query(Video)
    if search:
        query = query.filter(Video.title.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(desc(Video.published_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[VideoOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )
