"""
Neo4j database driver and connection management
"""
from neo4j import GraphDatabase
from typing import Optional, List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class Neo4jDriver:
    """Neo4j database driver wrapper"""

    def __init__(self, uri: str, user: str, password: str):
        self._driver = None
        self._uri = uri
        self._user = user
        self._password = password

    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._user, self._password)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self._uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            logger.warning("Will use demo mode with mock data")
            self._driver = None  # Use demo mode

    def close(self):
        """Close database connection"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")

        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a write query (CREATE, UPDATE, DELETE)

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Summary of the operation
        """
        if not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")

        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set
            }


# Global driver instance
neo4j_driver = Neo4jDriver(
    uri=settings.neo4j_uri,
    user=settings.neo4j_user,
    password=settings.neo4j_password
)


def get_neo4j_driver() -> Neo4jDriver:
    """Get the global Neo4j driver instance"""
    return neo4j_driver
