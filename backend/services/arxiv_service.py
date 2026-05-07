import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models import Paper

ARXIV_API = "http://export.arxiv.org/api/query"
AI_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO", "stat.ML"]
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


async def fetch_papers(category: str = "cs.AI", max_results: int = 20) -> List[Dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(ARXIV_API, params={
                "search_query": f"cat:{category}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            })
            if resp.status_code == 200:
                return _parse_arxiv_response(resp.text)
        except Exception:
            pass
    return []


async def search_papers(query: str = "large language model", max_results: int = 20) -> List[Dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(ARXIV_API, params={
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
            })
            if resp.status_code == 200:
                return _parse_arxiv_response(resp.text)
        except Exception:
            pass
    return []


def _parse_arxiv_response(xml_text: str) -> List[Dict]:
    papers = []
    try:
        root = ET.fromstring(xml_text)
        for entry in root.findall("atom:entry", NS):
            arxiv_id_raw = entry.findtext("atom:id", "", NS)
            arxiv_id = arxiv_id_raw.split("/abs/")[-1] if "/abs/" in arxiv_id_raw else arxiv_id_raw

            published_str = entry.findtext("atom:published", "", NS)
            published = None
            if published_str:
                try:
                    published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except Exception:
                    pass

            authors = [
                a.findtext("atom:name", "", NS)
                for a in entry.findall("atom:author", NS)
            ]

            categories = [
                cat.get("term", "")
                for cat in entry.findall("atom:category", NS)
            ]

            pdf_url = ""
            for link in entry.findall("atom:link", NS):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")

            papers.append({
                "arxiv_id": arxiv_id,
                "title": (entry.findtext("atom:title", "", NS) or "").strip().replace("\n", " "),
                "abstract": (entry.findtext("atom:summary", "", NS) or "").strip()[:2000],
                "authors": authors[:5],
                "categories": categories,
                "url": arxiv_id_raw,
                "pdf_url": pdf_url,
                "published_at": published,
            })
    except Exception:
        pass
    return papers


def save_papers(db: Session, papers: List[Dict]) -> int:
    saved = 0
    for item in papers:
        if not item.get("arxiv_id"):
            continue
        existing = db.query(Paper).filter(Paper.arxiv_id == item["arxiv_id"]).first()
        if existing:
            continue
        paper = Paper(
            arxiv_id=item["arxiv_id"],
            title=item["title"],
            abstract=item.get("abstract", ""),
            authors=item.get("authors", []),
            categories=item.get("categories", []),
            url=item.get("url", ""),
            pdf_url=item.get("pdf_url", ""),
            published_at=item.get("published_at"),
        )
        db.add(paper)
        saved += 1
    db.commit()
    return saved
