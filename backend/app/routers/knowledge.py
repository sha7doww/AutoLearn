"""
Knowledge tracking and recommendation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.knowledge import (
    KnowledgeStateRequest,
    KnowledgeStateResponse,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem
)
from app.services.knowledge_tracking import get_knowledge_tracker, IRTKnowledgeTracker
from app.services.course_service import CourseService
from app.database.neo4j_driver import get_neo4j_driver, Neo4jDriver
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


def get_course_service(db: Neo4jDriver = Depends(get_neo4j_driver)) -> CourseService:
    """Dependency to get course service"""
    return CourseService(db)


@router.post("/state", response_model=KnowledgeStateResponse)
async def calculate_knowledge_state(
    request: KnowledgeStateRequest,
    tracker: IRTKnowledgeTracker = Depends(get_knowledge_tracker)
):
    """
    Calculate student's knowledge state from course scores

    Uses IRT (Item Response Theory) model to estimate mastery levels
    for different knowledge domains based on course performance.

    Args:
        request: Student ID and course scores

    Returns:
        Knowledge state with domain-wise mastery levels
    """
    try:
        # Estimate knowledge state using IRT
        knowledge_vector = tracker.estimate_knowledge_state(request.course_scores)

        # Analyze strengths and weaknesses
        overall_level, strengths, weaknesses = tracker.analyze_knowledge_state(
            knowledge_vector
        )

        return KnowledgeStateResponse(
            student_id=request.student_id,
            knowledge_vector=knowledge_vector,
            overall_level=overall_level,
            strengths=strengths,
            weaknesses=weaknesses,
            calculated_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error calculating knowledge state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_courses(
    request: RecommendationRequest,
    tracker: IRTKnowledgeTracker = Depends(get_knowledge_tracker),
    course_service: CourseService = Depends(get_course_service)
):
    """
    Recommend courses based on student's knowledge state

    Considers:
    - Student's current knowledge level
    - Prerequisite requirements
    - Personalized difficulty assessment
    - Completed courses

    Args:
        request: Student ID, knowledge state, completed courses

    Returns:
        List of recommended courses with reasons
    """
    try:
        # If knowledge state not provided, return error
        if not request.knowledge_state:
            raise HTTPException(
                status_code=400,
                detail="Knowledge state required for recommendations"
            )

        # Get all available courses
        all_courses = course_service.get_all_courses()

        recommendations = []

        for course in all_courses:
            # Skip completed courses
            if course.id in request.completed_courses:
                continue

            # Get detailed course info
            course_detail = course_service.get_course_by_id(course.id)
            if not course_detail:
                continue

            # Check prerequisites
            missing_prerequisites = []
            prerequisites_met = True

            for prereq_id in course_detail.prerequisites:
                if prereq_id not in request.completed_courses:
                    prerequisites_met = False
                    missing_prerequisites.append(prereq_id)

            # Calculate personalized difficulty
            difficulty_score, difficulty_label = tracker.calculate_course_difficulty_for_student(
                course.label,
                request.knowledge_state
            )

            # Calculate match score based on:
            # 1. Prerequisites satisfaction
            # 2. Knowledge readiness
            # 3. Difficulty match (prefer slightly challenging courses)
            match_score = 0.0

            if prerequisites_met:
                match_score += 0.4  # 40% for meeting prerequisites

            # Knowledge readiness (30%)
            knowledge_readiness = 1.0 - difficulty_score  # Lower difficulty = higher readiness
            match_score += 0.3 * knowledge_readiness

            # Optimal challenge (30%) - prefer courses with difficulty 0.4-0.7
            if 0.4 <= difficulty_score <= 0.7:
                match_score += 0.3
            else:
                match_score += 0.3 * (1 - abs(difficulty_score - 0.55) / 0.55)

            # Generate recommendation reason
            reason_parts = []

            if prerequisites_met:
                reason_parts.append("满足先修要求")
            else:
                reason_parts.append(f"需要完成{len(missing_prerequisites)}门先修课程")

            if knowledge_readiness > 0.7:
                reason_parts.append("知识储备充分")
            elif knowledge_readiness > 0.4:
                reason_parts.append("知识储备基本满足")
            else:
                reason_parts.append("建议先加强基础")

            if 0.4 <= difficulty_score <= 0.7:
                reason_parts.append("难度适中")
            elif difficulty_score < 0.4:
                reason_parts.append("较为简单")
            else:
                reason_parts.append("具有挑战性")

            reason = "，".join(reason_parts)

            recommendations.append(RecommendationItem(
                course_id=course.id,
                course_name=course.label,
                reason=reason,
                match_score=match_score,
                difficulty_match=difficulty_label,
                prerequisites_met=prerequisites_met,
                missing_prerequisites=missing_prerequisites
            ))

        # Sort by match score and take top N
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        top_recommendations = recommendations[:request.max_recommendations]

        return RecommendationResponse(
            student_id=request.student_id,
            recommendations=top_recommendations,
            generated_at=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def get_knowledge_domains(
    tracker: IRTKnowledgeTracker = Depends(get_knowledge_tracker)
):
    """
    Get all available knowledge domains

    Returns:
        List of knowledge domains tracked by the system
    """
    try:
        # Extract unique domains from course mapping
        domains = set()
        for course_domains in tracker.course_knowledge_mapping.values():
            domains.update(course_domains)

        return {
            "domains": sorted(list(domains)),
            "total": len(domains)
        }

    except Exception as e:
        logger.error(f"Error getting knowledge domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))
