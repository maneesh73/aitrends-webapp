from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ArticleOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    image_url: Optional[str]
    source: Optional[str]
    author: Optional[str]
    published_at: Optional[datetime]
    category: str
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class RepositoryOut(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str]
    url: str
    stars: int
    forks: int
    language: Optional[str]
    topics: List[str] = []
    owner_avatar: Optional[str]
    is_trending: bool
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaperOut(BaseModel):
    id: int
    arxiv_id: str
    title: str
    abstract: Optional[str]
    authors: List[str] = []
    categories: List[str] = []
    url: str
    pdf_url: Optional[str]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class CourseOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    provider: Optional[str]
    instructor: Optional[str]
    thumbnail: Optional[str]
    level: Optional[str]
    duration: Optional[str]
    topics: List[str] = []
    is_free: bool

    class Config:
        from_attributes = True


class AIToolOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    url: Optional[str]
    github_url: Optional[str]
    category: Optional[str]
    tags: List[str] = []
    stars: int
    is_agent: bool
    logo_url: Optional[str]

    class Config:
        from_attributes = True


class VideoOut(BaseModel):
    id: int
    video_id: str
    title: str
    description: Optional[str]
    channel: Optional[str]
    thumbnail: Optional[str]
    url: str
    view_count: int
    like_count: int
    published_at: Optional[datetime]
    tags: List[str] = []
    summary: Optional[str]

    class Config:
        from_attributes = True


class TrendTopicOut(BaseModel):
    id: int
    topic: str
    description: Optional[str]
    mentions: int
    source: Optional[str]
    category: Optional[str]
    url: Optional[str]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool


class FetchStatus(BaseModel):
    status: str
    fetched: int
    message: str
