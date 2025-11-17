"""
Neo4j Database Initialization Script
Loads course data from JSON and creates knowledge graph
"""
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.neo4j_driver import Neo4jDriver
from app.config import settings


def load_course_data():
    """Load course data from JSON file"""
    data_file = Path(__file__).parent.parent / "data" / "course_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def clear_database(driver: Neo4jDriver):
    """Clear all existing data"""
    print("Clearing existing data...")
    query = "MATCH (n) DETACH DELETE n"
    driver.execute_write(query)
    print("✓ Database cleared")


def create_constraints(driver: Neo4jDriver):
    """Create database constraints"""
    print("Creating constraints...")

    # Create unique constraint on Course.id
    constraint_query = """
    CREATE CONSTRAINT course_id_unique IF NOT EXISTS
    FOR (c:Course) REQUIRE c.id IS UNIQUE
    """
    try:
        driver.execute_write(constraint_query)
        print("✓ Constraints created")
    except Exception as e:
        print(f"Note: Constraint creation skipped or already exists: {e}")


def import_courses(driver: Neo4jDriver, courses):
    """Import courses into Neo4j"""
    print(f"Importing {len(courses)} courses...")

    query = """
    UNWIND $courses AS course
    CREATE (c:Course {
        id: course.id,
        label: course.label,
        difficulty: course.difficulty,
        credits: course.credits,
        course_type: course.course_type,
        description: course.label,
        knowledge_points: []
    })
    """

    result = driver.execute_write(query, {"courses": courses})
    print(f"✓ Created {result['nodes_created']} course nodes")


def import_relationships(driver: Neo4jDriver, relationships):
    """Import prerequisite relationships"""
    print(f"Importing {len(relationships)} prerequisite relationships...")

    query = """
    UNWIND $relationships AS rel
    MATCH (from:Course {id: rel.from})
    MATCH (to:Course {id: rel.to})
    CREATE (from)-[:PREREQUISITE]->(to)
    """

    result = driver.execute_write(query, {"relationships": relationships})
    print(f"✓ Created {result['relationships_created']} prerequisite relationships")


def verify_import(driver: Neo4jDriver):
    """Verify the import was successful"""
    print("\nVerifying import...")

    # Count courses
    count_query = "MATCH (c:Course) RETURN count(c) as count"
    result = driver.execute_query(count_query)
    course_count = result[0]['count']
    print(f"✓ Total courses: {course_count}")

    # Count relationships
    rel_query = "MATCH ()-[r:PREREQUISITE]->() RETURN count(r) as count"
    result = driver.execute_query(rel_query)
    rel_count = result[0]['count']
    print(f"✓ Total prerequisites: {rel_count}")

    # Sample query - find courses with most prerequisites
    sample_query = """
    MATCH (c:Course)
    OPTIONAL MATCH (prereq:Course)-[:PREREQUISITE]->(c)
    WITH c, count(prereq) as prereq_count
    WHERE prereq_count > 0
    RETURN c.label as course, prereq_count
    ORDER BY prereq_count DESC
    LIMIT 5
    """
    results = driver.execute_query(sample_query)
    print("\nTop 5 courses by prerequisite count:")
    for record in results:
        print(f"  - {record['course']}: {record['prereq_count']} prerequisites")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Neo4j Knowledge Graph Initialization")
    print("=" * 60)
    print(f"\nConnecting to Neo4j at {settings.neo4j_uri}...")

    # Create driver and connect
    driver = Neo4jDriver(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )

    try:
        driver.connect()
        print("✓ Connected successfully\n")

        # Load data
        data = load_course_data()
        print(f"Loaded data: {len(data['courses'])} courses, {len(data['relationships'])} relationships\n")

        # Confirm before clearing
        response = input("This will clear existing data. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            return

        # Execute import steps
        clear_database(driver)
        create_constraints(driver)
        import_courses(driver, data['courses'])
        import_relationships(driver, data['relationships'])
        verify_import(driver)

        print("\n" + "=" * 60)
        print("Import completed successfully!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Access Neo4j Browser at http://localhost:7474")
        print("2. Start the FastAPI server: python -m app.main")
        print("3. View API docs at http://localhost:8000/docs")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
