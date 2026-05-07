import httpx
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models import Repository
from config import settings

GITHUB_API = "https://api.github.com"
AI_SEARCH_QUERIES = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "large language model",
    "AI agent",
    "neural network",
    "transformer model",
]


async def fetch_trending_repos(language: str = "", since: str = "weekly") -> List[Dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    results = []
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        for query in AI_SEARCH_QUERIES[:3]:
            try:
                resp = await client.get(f"{GITHUB_API}/search/repositories", params={
                    "q": f"{query} stars:>100",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10,
                })
                if resp.status_code == 200:
                    data = resp.json()
                    results.extend(data.get("items", []))
            except Exception:
                continue
    return results


async def fetch_repos_by_topic(topic: str = "llm", per_page: int = 20) -> List[Dict]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"token {settings.github_token}"

    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            resp = await client.get(f"{GITHUB_API}/search/repositories", params={
                "q": f"topic:{topic} stars:>500",
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
            })
            if resp.status_code == 200:
                return resp.json().get("items", [])
        except Exception:
            pass
    return []


def save_repos(db: Session, repos: List[Dict]) -> int:
    saved = 0
    seen = set()
    for item in repos:
        full_name = item.get("full_name", "")
        if not full_name or full_name in seen:
            continue
        seen.add(full_name)
        existing = db.query(Repository).filter(Repository.full_name == full_name).first()
        updated_at = None
        if item.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            except Exception:
                pass
        if existing:
            existing.stars = item.get("stargazers_count", existing.stars)
            existing.forks = item.get("forks_count", existing.forks)
            existing.updated_at = updated_at
            db.commit()
            continue
        repo = Repository(
            name=item.get("name", ""),
            full_name=full_name,
            description=item.get("description", ""),
            url=item.get("html_url", ""),
            stars=item.get("stargazers_count", 0),
            forks=item.get("forks_count", 0),
            language=item.get("language", ""),
            topics=item.get("topics", []),
            owner_avatar=item.get("owner", {}).get("avatar_url", ""),
            is_trending=True,
            updated_at=updated_at,
        )
        db.add(repo)
        saved += 1
    db.commit()
    return saved
