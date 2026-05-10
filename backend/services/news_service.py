import feedparser
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import Article
from config import settings

AI_RSS_FEEDS = [
    # Tech & AI news outlets
    ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
    ("The Verge - AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("VentureBeat AI", "https://venturebeat.com/ai/feed/"),
    ("AI News", "https://www.artificialintelligence-news.com/feed/"),
    ("Towards Data Science", "https://towardsdatascience.com/feed"),
    ("Wired - AI", "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss"),
    ("TechCrunch - AI", "https://techcrunch.com/tag/artificial-intelligence/feed/"),
    ("ZDNet - AI", "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("The Register - AI", "https://www.theregister.com/tag/ai/rss"),
    ("Ars Technica - AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("Analytics Vidhya", "https://www.analyticsvidhya.com/feed/"),
    ("KDnuggets", "https://www.kdnuggets.com/feed"),
    ("Machine Learning Mastery", "https://machinelearningmastery.com/feed/"),
    ("Import AI (Jack Clark)", "https://jack-clark.net/feed/"),
    ("The Gradient", "https://thegradient.pub/rss/"),
    ("Synced Review", "https://syncedreview.com/feed/"),
    ("Unite.AI", "https://www.unite.ai/feed/"),
    ("Marktechpost", "https://www.marktechpost.com/feed/"),
    ("The Batch (DeepLearning.AI)", "https://www.deeplearning.ai/the-batch/rss/"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
]

# Google News RSS — free, no key needed
GOOGLE_NEWS_QUERIES = [
    "artificial intelligence",
    "large language model",
    "AI agents",
    "generative AI",
    "machine learning research",
    "OpenAI GPT",
    "Claude Anthropic",
    "AI regulation policy",
    "AI safety alignment",
    "deep learning neural network",
    "AI startup funding",
    "robotics automation AI",
    "natural language processing NLP",
    "computer vision AI",
    "AI healthcare medicine",
    "AI chip semiconductor",
    "multimodal AI model",
    "reinforcement learning",
    "open source AI model",
    "AI ethics bias",
]

REDDIT_RSS_FEEDS = [
    ("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
    ("Reddit r/artificial", "https://www.reddit.com/r/artificial/.rss"),
    ("Reddit r/AINews", "https://www.reddit.com/r/AINews/.rss"),
    ("Reddit r/LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/.rss"),
    ("Reddit r/ChatGPT", "https://www.reddit.com/r/ChatGPT/.rss"),
    ("Reddit r/singularity", "https://www.reddit.com/r/singularity/.rss"),
    ("Reddit r/deeplearning", "https://www.reddit.com/r/deeplearning/.rss"),
]

GUARDIAN_SECTIONS = [
    "technology",
    "science",
]

GUARDIAN_QUERIES = [
    "artificial intelligence",
    "machine learning",
    "large language model",
    "generative AI",
    "AI regulation",
]


def fetch_guardian_articles() -> List[Dict]:
    articles = []
    api_key = settings.guardian_api_key
    if not api_key:
        return []
    import httpx
    base_url = "https://content.guardianapis.com/search"
    with httpx.Client(timeout=15) as client:
        for query in GUARDIAN_QUERIES:
            try:
                resp = client.get(base_url, params={
                    "q": query,
                    "api-key": api_key,
                    "show-fields": "thumbnail,trailText,byline",
                    "order-by": "newest",
                    "page-size": 20,
                    "section": "technology|science",
                })
                if resp.status_code != 200:
                    continue
                results = resp.json().get("response", {}).get("results", [])
                for item in results:
                    fields = item.get("fields", {})
                    published = None
                    pub_str = item.get("webPublicationDate", "")
                    if pub_str:
                        try:
                            published = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                        except Exception:
                            pass
                    articles.append({
                        "title": item.get("webTitle", ""),
                        "description": fields.get("trailText", "")[:500],
                        "url": item.get("webUrl", ""),
                        "image_url": fields.get("thumbnail", ""),
                        "source": "The Guardian",
                        "author": fields.get("byline", ""),
                        "published_at": published,
                        "category": "news",
                        "tags": [query],
                    })
            except Exception:
                continue
    return articles


def fetch_reddit_rss() -> List[Dict]:
    articles = []
    for source_name, url in REDDIT_RSS_FEEDS:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "AITrends/1.0"})
            for entry in feed.entries[:20]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", "")[:500] if entry.get("summary") else "",
                    "url": entry.get("link", ""),
                    "image_url": "",
                    "source": source_name,
                    "author": entry.get("author", ""),
                    "published_at": published,
                    "category": "news",
                    "tags": [],
                })
        except Exception:
            continue
    return articles


def fetch_google_news_rss() -> List[Dict]:
    """Fetch from Google News RSS — completely free, no API key required."""
    articles = []
    for query in GOOGLE_NEWS_QUERIES:
        encoded = query.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", "")[:500] if entry.get("summary") else "",
                    "url": entry.get("link", ""),
                    "image_url": "",
                    "source": f"Google News — {query}",
                    "author": "",
                    "published_at": published,
                    "category": "news",
                    "tags": [query],
                })
        except Exception:
            continue
    return articles


def fetch_rss_articles() -> List[Dict]:
    articles = []
    for source_name, url in AI_RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:25]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", "")[:500] if entry.get("summary") else "",
                    "url": entry.get("link", ""),
                    "image_url": _extract_image(entry),
                    "source": source_name,
                    "author": entry.get("author", ""),
                    "published_at": published,
                    "category": "news",
                    "tags": [],
                })
        except Exception:
            continue
    return articles


def _extract_image(entry) -> str:
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url", "")
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if "image" in enc.get("type", ""):
                return enc.get("href", "")
    return ""


def save_articles(db: Session, articles: List[Dict]) -> int:
    saved = 0
    seen_urls: set = set()
    for item in articles:
        url = item.get("url", "")
        if not url or not item.get("title"):
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        existing = db.query(Article).filter(Article.url == url).first()
        if existing:
            continue
        article = Article(
            title=item["title"],
            description=item.get("description", ""),
            url=url,
            image_url=item.get("image_url") or item.get("urlToImage", ""),
            source=item.get("source", {}).get("name", "") if isinstance(item.get("source"), dict) else item.get("source", ""),
            author=item.get("author", ""),
            published_at=item.get("published_at") or item.get("publishedAt"),
            category=item.get("category", "news"),
            tags=item.get("tags", []),
        )
        db.add(article)
        saved += 1
    try:
        db.commit()
    except Exception:
        db.rollback()
        saved = _save_articles_one_by_one(db, articles)
    return saved


def _save_articles_one_by_one(db: Session, articles: List[Dict]) -> int:
    saved = 0
    seen_urls: set = set()
    for item in articles:
        url = item.get("url", "")
        if not url or not item.get("title") or url in seen_urls:
            continue
        seen_urls.add(url)
        try:
            existing = db.query(Article).filter(Article.url == url).first()
            if existing:
                continue
            db.add(Article(
                title=item["title"],
                description=item.get("description", ""),
                url=url,
                image_url=item.get("image_url") or item.get("urlToImage", ""),
                source=item.get("source", {}).get("name", "") if isinstance(item.get("source"), dict) else item.get("source", ""),
                author=item.get("author", ""),
                published_at=item.get("published_at") or item.get("publishedAt"),
                category=item.get("category", "news"),
                tags=item.get("tags", []),
            ))
            db.commit()
            saved += 1
        except Exception:
            db.rollback()
    return saved
