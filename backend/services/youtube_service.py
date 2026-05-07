import httpx
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models import Video
from config import settings

YOUTUBE_SEARCH_API = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API = "https://www.googleapis.com/youtube/v3/videos"

AI_YOUTUBE_QUERIES = [
    "artificial intelligence 2025",
    "large language models tutorial",
    "AI agents explained",
    "machine learning course",
    "ChatGPT Claude Gemini comparison",
]


async def search_videos(query: str = "AI tutorial 2025", max_results: int = 10) -> List[Dict]:
    if not settings.youtube_api_key:
        return []
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(YOUTUBE_SEARCH_API, params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_results,
                "key": settings.youtube_api_key,
                "relevanceLanguage": "en",
                "order": "relevance",
            })
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                video_ids = [i["id"]["videoId"] for i in items if "videoId" in i.get("id", {})]
                stats = await _get_video_stats(video_ids, client)
                return _merge_video_data(items, stats)
        except Exception:
            pass
    return []


async def _get_video_stats(video_ids: List[str], client: httpx.AsyncClient) -> Dict:
    if not video_ids or not settings.youtube_api_key:
        return {}
    try:
        resp = await client.get(YOUTUBE_VIDEOS_API, params={
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": settings.youtube_api_key,
        })
        if resp.status_code == 200:
            return {
                item["id"]: item.get("statistics", {})
                for item in resp.json().get("items", [])
            }
    except Exception:
        pass
    return {}


def _merge_video_data(items: List[Dict], stats: Dict) -> List[Dict]:
    results = []
    for item in items:
        vid_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {})
        stat = stats.get(vid_id, {})
        published = None
        pub_str = snippet.get("publishedAt", "")
        if pub_str:
            try:
                published = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            except Exception:
                pass
        results.append({
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:500],
            "channel": snippet.get("channelTitle", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "view_count": int(stat.get("viewCount", 0)),
            "like_count": int(stat.get("likeCount", 0)),
            "published_at": published,
            "tags": [],
            "summary": snippet.get("description", "")[:300],
        })
    return results


def save_videos(db: Session, videos: List[Dict]) -> int:
    saved = 0
    for item in videos:
        if not item.get("video_id"):
            continue
        existing = db.query(Video).filter(Video.video_id == item["video_id"]).first()
        if existing:
            continue
        video = Video(**{k: v for k, v in item.items() if k in Video.__table__.columns.keys()})
        db.add(video)
        saved += 1
    db.commit()
    return saved
