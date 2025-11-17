"""
Mock data for demo mode when Neo4j is not available
"""
import json
from pathlib import Path

# Load course data from JSON
data_file = Path(__file__).parent.parent.parent / "data" / "course_data.json"
with open(data_file, 'r', encoding='utf-8') as f:
    COURSE_DATA = json.load(f)


def get_mock_courses():
    """Get all courses from mock data"""
    return COURSE_DATA['courses']


def get_mock_course_by_id(course_id):
    """Get course by ID from mock data"""
    for course in COURSE_DATA['courses']:
        if course['id'] == course_id:
            # Add prerequisites
            prereqs = [
                rel['from'] for rel in COURSE_DATA['relationships']
                if rel['to'] == course_id
            ]
            course['prerequisites'] = prereqs
            course['knowledge_points'] = []
            course['description'] = course['label']
            return course
    return None


def get_mock_relationships():
    """Get all relationships from mock data"""
    return COURSE_DATA['relationships']


def search_mock_courses(keyword):
    """Search courses in mock data"""
    results = []
    for course in COURSE_DATA['courses']:
        if keyword in course['label']:
            results.append(course)
    return results


def get_mock_prerequisites(course_id, max_depth=5):
    """Get prerequisites from mock data using BFS"""
    relationships = COURSE_DATA['relationships']

    # Build adjacency list
    graph = {}
    for rel in relationships:
        if rel['to'] not in graph:
            graph[rel['to']] = []
        graph[rel['to']].append(rel['from'])

    # BFS to find all paths
    paths = []

    def dfs(current, path, depth):
        if depth > max_depth:
            return
        if current in graph:
            for prereq in graph[current]:
                new_path = [prereq] + path
                paths.append(new_path)
                dfs(prereq, new_path, depth + 1)

    dfs(course_id, [course_id], 0)
    return paths
