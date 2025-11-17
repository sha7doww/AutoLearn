"""
Course-related schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CourseBase(BaseModel):
    """Base course information"""
    id: int
    label: str = Field(..., description="Course name")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    credits: Optional[float] = Field(None, description="Course credits")
    course_type: Optional[str] = Field(None, description="Course type (required/elective)")


class CourseDetail(CourseBase):
    """Detailed course information with prerequisites"""
    prerequisites: List[int] = Field(default_factory=list, description="List of prerequisite course IDs")
    knowledge_points: List[str] = Field(default_factory=list, description="Main knowledge points")
    description: Optional[str] = Field(None, description="Course description")


class CourseSearchRequest(BaseModel):
    """Course search request"""
    keyword: str = Field(..., description="Search keyword")
    search_type: str = Field("fuzzy", description="Search type: fuzzy or exact")


class CourseSearchResponse(BaseModel):
    """Course search response"""
    courses: List[CourseBase]
    total: int = Field(..., description="Total number of results")


class PrerequisitePathRequest(BaseModel):
    """Request for prerequisite path"""
    course_id: int = Field(..., description="Target course ID")
    max_depth: int = Field(5, description="Maximum depth of prerequisite chain")


class PrerequisitePathResponse(BaseModel):
    """Prerequisite path response"""
    course_id: int
    course_name: str
    path: List[List[int]] = Field(..., description="All possible prerequisite paths")
    path_details: List[Dict[str, Any]] = Field(..., description="Detailed path information")


class LearningPathRequest(BaseModel):
    """Request for generating learning path"""
    target_course_id: int
    completed_courses: List[int] = Field(default_factory=list)
    knowledge_state: Optional[Dict[str, float]] = Field(None, description="Student's knowledge state")


class LearningPathResponse(BaseModel):
    """Learning path response"""
    target_course_id: int
    target_course_name: str
    recommended_sequence: List[int] = Field(..., description="Recommended course sequence")
    course_details: List[CourseDetail]
    total_credits: float
    estimated_semesters: int
