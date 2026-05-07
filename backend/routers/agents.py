from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import AITool
from schemas import AIToolOut, PaginatedResponse, FetchStatus
from services import huggingface_service
from auth import require_sync_auth

router = APIRouter(prefix="/api/agents", tags=["agents"])

CURATED_TOOLS = [
    {"name": "LangChain", "description": "Framework for building LLM-powered apps with chains, agents, and memory.", "url": "https://langchain.com", "github_url": "https://github.com/langchain-ai/langchain", "category": "Framework", "tags": ["llm", "agents", "python"], "stars": 90000, "is_agent": False},
    {"name": "AutoGPT", "description": "Autonomous AI agent that chains GPT-4 thoughts to accomplish goals.", "url": "https://agpt.co", "github_url": "https://github.com/Significant-Gravitas/AutoGPT", "category": "Agent", "tags": ["autonomous", "gpt-4", "agent"], "stars": 165000, "is_agent": True},
    {"name": "CrewAI", "description": "Multi-agent framework for orchestrating role-playing AI agents.", "url": "https://crewai.com", "github_url": "https://github.com/joaomdmoura/crewAI", "category": "Multi-Agent", "tags": ["multi-agent", "llm", "python"], "stars": 18000, "is_agent": True},
    {"name": "LlamaIndex", "description": "Data framework for LLM-based applications; RAG and indexing.", "url": "https://llamaindex.ai", "github_url": "https://github.com/run-llama/llama_index", "category": "Framework", "tags": ["rag", "llm", "indexing"], "stars": 35000, "is_agent": False},
    {"name": "Ollama", "description": "Run large language models locally with simple API.", "url": "https://ollama.ai", "github_url": "https://github.com/ollama/ollama", "category": "Runtime", "tags": ["local", "llm", "inference"], "stars": 80000, "is_agent": False},
    {"name": "MetaGPT", "description": "Multi-agent meta programming framework that assigns roles to GPT models.", "url": "https://deepwisdom.ai", "github_url": "https://github.com/geekan/MetaGPT", "category": "Multi-Agent", "tags": ["multi-agent", "gpt", "coding"], "stars": 43000, "is_agent": True},
    {"name": "OpenDevin", "description": "Open-source AI software developer agent (SWE-Agent).", "url": "https://opendevin.github.io", "github_url": "https://github.com/OpenDevin/OpenDevin", "category": "Agent", "tags": ["coding", "agent", "swe"], "stars": 32000, "is_agent": True},
    {"name": "Dify", "description": "LLMOps platform for building AI workflows and agents visually.", "url": "https://dify.ai", "github_url": "https://github.com/langgenius/dify", "category": "Platform", "tags": ["llmops", "workflow", "no-code"], "stars": 42000, "is_agent": False},
    {"name": "AnythingLLM", "description": "All-in-one AI app for chat with documents, agents, and integrations.", "url": "https://useanything.com", "github_url": "https://github.com/Mintplex-Labs/anything-llm", "category": "App", "tags": ["rag", "documents", "local"], "stars": 22000, "is_agent": False},
    {"name": "AutoGen", "description": "Microsoft's multi-agent conversational framework for LLM apps.", "url": "https://microsoft.github.io/autogen", "github_url": "https://github.com/microsoft/autogen", "category": "Multi-Agent", "tags": ["microsoft", "multi-agent", "python"], "stars": 31000, "is_agent": True},
    {"name": "Flowise", "description": "Drag-and-drop UI for building LLM flows with LangChain.", "url": "https://flowiseai.com", "github_url": "https://github.com/FlowiseAI/Flowise", "category": "Platform", "tags": ["no-code", "langchain", "workflow"], "stars": 30000, "is_agent": False},
    {"name": "Semantic Kernel", "description": "Microsoft SDK for integrating AI into apps with plugins.", "url": "https://learn.microsoft.com/semantic-kernel", "github_url": "https://github.com/microsoft/semantic-kernel", "category": "SDK", "tags": ["microsoft", "plugins", "dotnet"], "stars": 22000, "is_agent": False},
]


@router.get("", response_model=PaginatedResponse)
def get_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: str = Query(""),
    is_agent: bool = Query(None),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(AITool)
    if category:
        query = query.filter(AITool.category.ilike(f"%{category}%"))
    if is_agent is not None:
        query = query.filter(AITool.is_agent == is_agent)
    if search:
        query = query.filter(AITool.name.ilike(f"%{search}%") | AITool.description.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(desc(AITool.stars))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[AIToolOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def fetch_tools(db: Session = Depends(get_db)):
    saved = 0
    for tool in CURATED_TOOLS:
        existing = db.query(AITool).filter(AITool.name == tool["name"]).first()
        if not existing:
            db.add(AITool(**tool))
            saved += 1
    db.commit()
    hf_models = await huggingface_service.fetch_trending_models(limit=15)
    saved += huggingface_service.save_hf_tools(db, hf_models)
    hf_spaces = await huggingface_service.fetch_trending_spaces(limit=10)
    saved += huggingface_service.save_hf_tools(db, hf_spaces, is_agent=True)
    return FetchStatus(status="ok", fetched=saved, message=f"Saved {saved} new tools")
