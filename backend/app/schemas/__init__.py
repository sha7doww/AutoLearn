"""API Schemas"""
from app.schemas.course import (
    CourseBase,
    CourseDetail,
    CourseSearchRequest,
    CourseSearchResponse,
    PrerequisitePathRequest,
    PrerequisitePathResponse,
    LearningPathRequest,
    LearningPathResponse
)
from app.schemas.knowledge import (
    KnowledgeStateRequest,
    KnowledgeStateResponse,
    RecommendationRequest,
    RecommendationItem,
    RecommendationResponse
)

__all__ = [
    "CourseBase",
    "CourseDetail",
    "CourseSearchRequest",
    "CourseSearchResponse",
    "PrerequisitePathRequest",
    "PrerequisitePathResponse",
    "LearningPathRequest",
    "LearningPathResponse",
    "KnowledgeStateRequest",
    "KnowledgeStateResponse",
    "RecommendationRequest",
    "RecommendationItem",
    "RecommendationResponse"
]
