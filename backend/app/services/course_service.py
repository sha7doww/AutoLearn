"""
Course service - handles course-related business logic
"""
from typing import List, Dict, Any, Optional
from app.database.neo4j_driver import Neo4jDriver
from app.schemas.course import CourseBase, CourseDetail
import logging

logger = logging.getLogger(__name__)


class CourseService:
    """Service for course operations"""

    def __init__(self, db: Neo4jDriver):
        self.db = db

    def get_all_courses(self) -> List[CourseBase]:
        """Get all courses from the knowledge graph"""
        if self.db._driver is None:
            # Demo mode - use mock data
            from app.database.mock_data import get_mock_courses
            return [CourseBase(**course) for course in get_mock_courses()]

        query = """
        MATCH (c:Course)
        RETURN c.id as id, c.label as label,
               c.difficulty as difficulty, c.credits as credits,
               c.course_type as course_type
        ORDER BY c.id
        """
        results = self.db.execute_query(query)
        return [CourseBase(**record) for record in results]

    def get_course_by_id(self, course_id: int) -> Optional[CourseDetail]:
        """Get detailed course information by ID"""
        if self.db._driver is None:
            # Demo mode - use mock data
            from app.database.mock_data import get_mock_course_by_id
            course_data = get_mock_course_by_id(course_id)
            if course_data:
                return CourseDetail(**course_data)
            return None

        query = """
        MATCH (c:Course {id: $course_id})
        OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE]->(c)
        RETURN c.id as id, c.label as label,
               c.difficulty as difficulty, c.credits as credits,
               c.course_type as course_type,
               c.description as description,
               c.knowledge_points as knowledge_points,
               collect(DISTINCT prereq.id) as prerequisites
        """
        results = self.db.execute_query(query, {"course_id": course_id})

        if not results:
            return None

        record = results[0]
        # Filter out None values from prerequisites
        record['prerequisites'] = [pid for pid in record.get('prerequisites', []) if pid is not None]
        # Ensure knowledge_points is a list
        if not record.get('knowledge_points'):
            record['knowledge_points'] = []

        return CourseDetail(**record)

    def search_courses(self, keyword: str, search_type: str = "fuzzy") -> List[CourseBase]:
        """Search courses by keyword"""
        if self.db._driver is None:
            # Demo mode - use mock data
            from app.database.mock_data import search_mock_courses
            return [CourseBase(**course) for course in search_mock_courses(keyword)]

        if search_type == "exact":
            query = """
            MATCH (c:Course)
            WHERE c.label = $keyword
            RETURN c.id as id, c.label as label,
                   c.difficulty as difficulty, c.credits as credits,
                   c.course_type as course_type
            """
        else:  # fuzzy search
            query = """
            MATCH (c:Course)
            WHERE c.label CONTAINS $keyword
            RETURN c.id as id, c.label as label,
                   c.difficulty as difficulty, c.credits as credits,
                   c.course_type as course_type
            ORDER BY c.id
            """

        results = self.db.execute_query(query, {"keyword": keyword})
        return [CourseBase(**record) for record in results]

    def get_prerequisites(self, course_id: int, max_depth: int = 5) -> List[List[int]]:
        """Get all prerequisite paths for a course"""
        if self.db._driver is None:
            # Demo mode - use mock data
            from app.database.mock_data import get_mock_prerequisites
            return get_mock_prerequisites(course_id, max_depth)

        query = """
        MATCH path = (prereq:Course)-[:PREREQUISITE*1..$max_depth]->(c:Course {id: $course_id})
        RETURN [node in nodes(path) | node.id] as path_nodes
        ORDER BY length(path)
        """

        results = self.db.execute_query(query, {
            "course_id": course_id,
            "max_depth": max_depth
        })

        return [record['path_nodes'] for record in results]

    def get_direct_prerequisites(self, course_id: int) -> List[int]:
        """Get direct prerequisites for a course"""
        query = """
        MATCH (prereq:Course)-[:PREREQUISITE]->(c:Course {id: $course_id})
        RETURN prereq.id as prereq_id
        ORDER BY prereq.id
        """

        results = self.db.execute_query(query, {"course_id": course_id})
        return [record['prereq_id'] for record in results]

    def get_learning_path(self,
                         target_course_id: int,
                         completed_courses: List[int]) -> List[int]:
        """
        Generate a learning path to a target course
        considering already completed courses
        """
        # Get all prerequisites
        all_paths = self.get_prerequisites(target_course_id)

        if not all_paths:
            return [target_course_id]

        # Find the shortest path that includes uncompleted courses
        incomplete_courses = set()
        for path in all_paths:
            for course_id in path:
                if course_id not in completed_courses and course_id != target_course_id:
                    incomplete_courses.add(course_id)

        # Simple topological sort for incomplete courses
        # This is a simplified version - could be enhanced with proper graph algorithms
        ordered_path = sorted(list(incomplete_courses))
        ordered_path.append(target_course_id)

        return ordered_path

    def get_course_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        if self.db._driver is None:
            # Demo mode - use mock data
            from app.database.mock_data import get_mock_courses, get_mock_relationships
            courses = get_mock_courses()
            relationships = get_mock_relationships()
            return {
                "total_courses": len(courses),
                "total_relationships": len(relationships)
            }

        query = """
        MATCH (c:Course)
        WITH count(c) as total_courses
        MATCH ()-[r:PREREQUISITE]->()
        RETURN total_courses, count(r) as total_relationships
        """

        result = self.db.execute_query(query)
        return result[0] if result else {"total_courses": 0, "total_relationships": 0}
