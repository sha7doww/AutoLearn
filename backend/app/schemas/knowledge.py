"""
Knowledge tracking related schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class KnowledgeStateRequest(BaseModel):
    """Request for knowledge state calculation"""
    student_id: str
    course_scores: Dict[str, float] = Field(
        ...,
        description="Course ID to score mapping (0-100)"
    )


class KnowledgeStateResponse(BaseModel):
    """Knowledge state response"""
    student_id: str
    knowledge_vector: Dict[str, float] = Field(
        ...,
        description="Knowledge domain to mastery level mapping (0-1)"
    )
    overall_level: float = Field(..., description="Overall knowledge level")
    strengths: List[str] = Field(..., description="Strong knowledge areas")
    weaknesses: List[str] = Field(..., description="Weak knowledge areas")
    calculated_at: datetime = Field(default_factory=datetime.now)


class RecommendationRequest(BaseModel):
    """Request for course recommendation"""
    student_id: str
    knowledge_state: Optional[Dict[str, float]] = None
    completed_courses: List[int] = Field(default_factory=list)
    max_recommendations: int = Field(5, description="Maximum number of recommendations")


class RecommendationItem(BaseModel):
    """Single course recommendation"""
    course_id: int
    course_name: str
    reason: str = Field(..., description="Recommendation reason")
    match_score: float = Field(..., description="Match score (0-1)")
    difficulty_match: str = Field(..., description="Difficulty assessment for this student")
    prerequisites_met: bool
    missing_prerequisites: List[int] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Course recommendation response"""
    student_id: str
    recommendations: List[RecommendationItem]
    generated_at: datetime = Field(default_factory=datetime.now)
