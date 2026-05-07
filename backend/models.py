from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from database import Base


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000), unique=True, index=True)
    image_url = Column(String(1000))
    source = Column(String(200))
    author = Column(String(200))
    published_at = Column(DateTime)
    category = Column(String(100), default="news")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())


class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    full_name = Column(String(500), unique=True, index=True)
    description = Column(Text)
    url = Column(String(1000))
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    language = Column(String(100))
    topics = Column(JSON, default=list)
    owner_avatar = Column(String(1000))
    is_trending = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime)


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String(50), unique=True, index=True)
    title = Column(String(1000), nullable=False)
    abstract = Column(Text)
    authors = Column(JSON, default=list)
    categories = Column(JSON, default=list)
    url = Column(String(1000))
    pdf_url = Column(String(1000))
    published_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000), unique=True)
    provider = Column(String(200))
    instructor = Column(String(200))
    thumbnail = Column(String(1000))
    level = Column(String(50))
    duration = Column(String(100))
    topics = Column(JSON, default=list)
    is_free = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class AITool(Base):
    __tablename__ = "ai_tools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    url = Column(String(1000))
    github_url = Column(String(1000))
    category = Column(String(100))
    tags = Column(JSON, default=list)
    stars = Column(Integer, default=0)
    is_agent = Column(Boolean, default=False)
    logo_url = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(100), unique=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    channel = Column(String(200))
    thumbnail = Column(String(1000))
    url = Column(String(1000))
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    published_at = Column(DateTime)
    tags = Column(JSON, default=list)
    summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class TrendTopic(Base):
    __tablename__ = "trend_topics"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(300), nullable=False)
    description = Column(Text)
    mentions = Column(Integer, default=0)
    source = Column(String(100))
    category = Column(String(100))
    url = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())
