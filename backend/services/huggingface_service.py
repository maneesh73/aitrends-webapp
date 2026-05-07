import httpx
from typing import List, Dict
from sqlalchemy.orm import Session
from models import AITool
from config import settings

HF_API = "https://huggingface.co/api"
HF_MODELS_API = f"{HF_API}/models"
HF_SPACES_API = f"{HF_API}/spaces"
HF_DATASETS_API = f"{HF_API}/datasets"


async def fetch_trending_models(limit: int = 20) -> List[Dict]:
    headers = {}
    if settings.huggingface_api_key:
        headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            resp = await client.get(HF_MODELS_API, params={
                "sort": "downloads",
                "direction": -1,
                "limit": limit,
                "filter": "text-generation",
            })
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return []


async def fetch_trending_spaces(limit: int = 20) -> List[Dict]:
    headers = {}
    if settings.huggingface_api_key:
        headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            resp = await client.get(HF_SPACES_API, params={
                "sort": "likes",
                "direction": -1,
                "limit": limit,
            })
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return []


def save_hf_tools(db: Session, models: List[Dict], is_agent: bool = False) -> int:
    saved = 0
    for item in models:
        model_id = item.get("modelId") or item.get("id", "")
        if not model_id:
            continue
        url = f"https://huggingface.co/{model_id}"
        existing = db.query(AITool).filter(AITool.url == url).first()
        if existing:
            continue
        tags = item.get("tags", [])
        tool = AITool(
            name=model_id.split("/")[-1],
            description=item.get("description", f"HuggingFace model: {model_id}"),
            url=url,
            github_url="",
            category="HuggingFace Model",
            tags=tags[:10] if tags else [],
            stars=item.get("likes", 0),
            is_agent=is_agent,
            logo_url="https://huggingface.co/front/assets/huggingface_logo.svg",
        )
        db.add(tool)
        saved += 1
    db.commit()
    return saved
