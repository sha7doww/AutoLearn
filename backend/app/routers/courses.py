"""
Course management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
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
from app.services.course_service import CourseService
from app.database.neo4j_driver import get_neo4j_driver, Neo4jDriver
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/courses", tags=["courses"])


def get_course_service(db: Neo4jDriver = Depends(get_neo4j_driver)) -> CourseService:
    """Dependency to get course service"""
    return CourseService(db)


@router.get("/", response_model=List[CourseBase])
async def get_all_courses(service: CourseService = Depends(get_course_service)):
    """
    Get all courses in the knowledge graph

    Returns:
        List of all courses with basic information
    """
    try:
        courses = service.get_all_courses()
        return courses
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: int,
    service: CourseService = Depends(get_course_service)
):
    """
    Get detailed information about a specific course

    Args:
        course_id: Course ID

    Returns:
        Detailed course information including prerequisites
    """
    try:
        course = service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
        return course
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=CourseSearchResponse)
async def search_courses(
    request: CourseSearchRequest,
    service: CourseService = Depends(get_course_service)
):
    """
    Search courses by keyword

    Args:
        request: Search request with keyword and search type

    Returns:
        List of matching courses
    """
    try:
        courses = service.search_courses(request.keyword, request.search_type)
        return CourseSearchResponse(
            courses=courses,
            total=len(courses)
        )
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prerequisites", response_model=PrerequisitePathResponse)
async def get_prerequisites(
    request: PrerequisitePathRequest,
    service: CourseService = Depends(get_course_service)
):
    """
    Get prerequisite paths for a course

    Args:
        request: Request with course ID and max depth

    Returns:
        All prerequisite paths and detailed information
    """
    try:
        # Get course info
        course = service.get_course_by_id(request.course_id)
        if not course:
            raise HTTPException(
                status_code=404,
                detail=f"Course {request.course_id} not found"
            )

        # Get all prerequisite paths
        paths = service.get_prerequisites(request.course_id, request.max_depth)

        # Get detailed info for each course in paths
        all_course_ids = set()
        for path in paths:
            all_course_ids.update(path)

        path_details = []
        for path in paths:
            path_info = {
                "path": path,
                "length": len(path) - 1,  # -1 because target course is included
                "courses": []
            }

            for cid in path:
                c = service.get_course_by_id(cid)
                if c:
                    path_info["courses"].append({
                        "id": c.id,
                        "name": c.label
                    })

            path_details.append(path_info)

        return PrerequisitePathResponse(
            course_id=request.course_id,
            course_name=course.label,
            path=paths,
            path_details=path_details
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prerequisites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning-path", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    service: CourseService = Depends(get_course_service)
):
    """
    Generate a personalized learning path to target course

    Args:
        request: Request with target course and completed courses

    Returns:
        Recommended learning sequence
    """
    try:
        # Get target course
        target_course = service.get_course_by_id(request.target_course_id)
        if not target_course:
            raise HTTPException(
                status_code=404,
                detail=f"Course {request.target_course_id} not found"
            )

        # Generate learning path
        sequence = service.get_learning_path(
            request.target_course_id,
            request.completed_courses
        )

        # Get detailed information for each course in sequence
        course_details = []
        total_credits = 0.0

        for course_id in sequence:
            course = service.get_course_by_id(course_id)
            if course:
                course_details.append(course)
                if course.credits:
                    total_credits += course.credits

        # Estimate semesters (assuming ~20 credits per semester)
        estimated_semesters = max(1, int(total_credits / 20))

        return LearningPathResponse(
            target_course_id=request.target_course_id,
            target_course_name=target_course.label,
            recommended_sequence=sequence,
            course_details=course_details,
            total_credits=total_credits,
            estimated_semesters=estimated_semesters
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_statistics(service: CourseService = Depends(get_course_service)):
    """
    Get knowledge graph statistics

    Returns:
        Statistics about courses and relationships
    """
    try:
        stats = service.get_course_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
