"""API Routers"""
from app.routers.courses import router as courses_router
from app.routers.knowledge import router as knowledge_router

__all__ = ["courses_router", "knowledge_router"]
