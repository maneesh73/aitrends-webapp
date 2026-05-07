from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Course
from schemas import CourseOut, PaginatedResponse, FetchStatus
from services import youtube_service
from auth import require_sync_auth

router = APIRouter(prefix="/api/courses", tags=["courses"])

CURATED_COURSES = [
    {"title": "Deep Learning Specialization", "description": "Master deep learning fundamentals with Andrew Ng. Covers neural networks, CNNs, RNNs, and more.", "url": "https://www.coursera.org/specializations/deep-learning", "provider": "Coursera / DeepLearning.AI", "instructor": "Andrew Ng", "thumbnail": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://d15cw65ipctsrr.cloudfront.net/56/a7620049d511e8a7a6f5d72d544eb1/DeepLearningAI_blue.png", "level": "Intermediate", "duration": "3 months", "topics": ["deep learning", "neural networks", "CNN", "RNN"], "is_free": False},
    {"title": "Machine Learning Specialization", "description": "Newly updated course by Andrew Ng covering supervised, unsupervised, and reinforcement learning.", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "provider": "Coursera / DeepLearning.AI", "instructor": "Andrew Ng", "thumbnail": "", "level": "Beginner", "duration": "3 months", "topics": ["machine learning", "regression", "classification"], "is_free": False},
    {"title": "Practical Deep Learning for Coders", "description": "Fast.ai's top-down approach to deep learning with PyTorch. Free and hands-on.", "url": "https://course.fast.ai", "provider": "fast.ai", "instructor": "Jeremy Howard", "thumbnail": "", "level": "Intermediate", "duration": "Self-paced", "topics": ["deep learning", "pytorch", "computer vision", "nlp"], "is_free": True},
    {"title": "CS50's Introduction to AI with Python", "description": "Harvard's AI course covering search, optimization, ML, neural networks, and language.", "url": "https://cs50.harvard.edu/ai/", "provider": "Harvard / edX", "instructor": "Brian Yu", "thumbnail": "", "level": "Beginner", "duration": "7 weeks", "topics": ["AI", "python", "search", "machine learning"], "is_free": True},
    {"title": "LLM Bootcamp", "description": "Full stack deep learning's intensive course on building LLM-powered apps.", "url": "https://fullstackdeeplearning.com/llm-bootcamp/", "provider": "Full Stack Deep Learning", "instructor": "Various", "thumbnail": "", "level": "Advanced", "duration": "Self-paced", "topics": ["llm", "langchain", "deployment", "prompting"], "is_free": True},
    {"title": "Hugging Face NLP Course", "description": "Official HuggingFace course on transformers, fine-tuning, and building NLP apps.", "url": "https://huggingface.co/learn/nlp-course", "provider": "HuggingFace", "instructor": "HuggingFace Team", "thumbnail": "", "level": "Intermediate", "duration": "Self-paced", "topics": ["nlp", "transformers", "fine-tuning", "bert"], "is_free": True},
    {"title": "Stanford CS224N: NLP with Deep Learning", "description": "Stanford's flagship NLP course covering transformers, BERT, GPT and state-of-the-art models.", "url": "https://web.stanford.edu/class/cs224n/", "provider": "Stanford University", "instructor": "Chris Manning", "thumbnail": "", "level": "Advanced", "duration": "Quarter", "topics": ["nlp", "transformers", "deep learning"], "is_free": True},
    {"title": "Google Machine Learning Crash Course", "description": "Fast-paced introduction to ML fundamentals using TensorFlow APIs.", "url": "https://developers.google.com/machine-learning/crash-course", "provider": "Google", "instructor": "Google Engineers", "thumbnail": "", "level": "Beginner", "duration": "15 hours", "topics": ["machine learning", "tensorflow", "google"], "is_free": True},
    {"title": "Applied AI with DeepLearning", "description": "IBM's course on applied AI, covering Watson, AutoML, and deployment.", "url": "https://www.coursera.org/learn/ai", "provider": "IBM / Coursera", "instructor": "Romeo Kienzler", "thumbnail": "", "level": "Intermediate", "duration": "4 weeks", "topics": ["applied ai", "ibm", "automl", "deployment"], "is_free": False},
    {"title": "Generative AI with LLMs", "description": "DeepLearning.AI course on generative AI, covering fine-tuning and RLHF.", "url": "https://www.coursera.org/learn/generative-ai-with-llms", "provider": "Coursera / DeepLearning.AI", "instructor": "Various", "thumbnail": "", "level": "Intermediate", "duration": "3 weeks", "topics": ["generative ai", "llm", "fine-tuning", "rlhf"], "is_free": False},
    {"title": "LangChain for LLM App Development", "description": "Short course on building LLM applications with LangChain from DeepLearning.AI.", "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/", "provider": "DeepLearning.AI", "instructor": "Harrison Chase", "thumbnail": "", "level": "Beginner", "duration": "1-2 hours", "topics": ["langchain", "llm", "python", "agents"], "is_free": True},
    {"title": "Building AI Agents from Scratch", "description": "Hands-on course building autonomous AI agents using Python and LLMs.", "url": "https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/", "provider": "DeepLearning.AI", "instructor": "Various", "thumbnail": "", "level": "Intermediate", "duration": "2 hours", "topics": ["agents", "langgraph", "autonomy"], "is_free": True},
]


@router.get("", response_model=PaginatedResponse)
def get_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    level: str = Query(""),
    is_free: bool = Query(None),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(Course)
    if level:
        query = query.filter(Course.level.ilike(f"%{level}%"))
    if is_free is not None:
        query = query.filter(Course.is_free == is_free)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%") | Course.description.ilike(f"%{search}%"))
    total = query.count()
    items = (
        query.order_by(desc(Course.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[CourseOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.post("/fetch", response_model=FetchStatus, dependencies=[Depends(require_sync_auth)])
async def seed_courses(db: Session = Depends(get_db)):
    saved = 0
    for course in CURATED_COURSES:
        existing = db.query(Course).filter(Course.url == course["url"]).first()
        if not existing:
            db.add(Course(**course))
            saved += 1
    db.commit()
    for query in ["machine learning tutorial 2025", "AI agent course", "LLM fine-tuning tutorial"]:
        videos = await youtube_service.search_videos(query=query, max_results=5)
        for v in videos:
            course_url = v["url"]
            existing = db.query(Course).filter(Course.url == course_url).first()
            if not existing:
                db.add(Course(
                    title=v["title"],
                    description=v["description"],
                    url=course_url,
                    provider="YouTube",
                    instructor=v["channel"],
                    thumbnail=v["thumbnail"],
                    level="Various",
                    duration="Video",
                    topics=["AI", "machine learning"],
                    is_free=True,
                ))
                saved += 1
    db.commit()
    return FetchStatus(status="ok", fetched=saved, message=f"Seeded {saved} courses")
