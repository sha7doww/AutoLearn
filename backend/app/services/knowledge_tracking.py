"""
Knowledge Tracking Service - IRT Model Implementation
Item Response Theory (IRT) based knowledge state estimation
"""
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit  # sigmoid function
import logging

logger = logging.getLogger(__name__)


class IRTKnowledgeTracker:
    """
    IRT-based knowledge tracking system

    Uses a simplified IRT model to estimate student knowledge state
    from course scores. Maps courses to knowledge domains and estimates
    mastery level for each domain.
    """

    def __init__(self):
        # Course to knowledge domain mapping
        # This mapping defines which knowledge domains each course covers
        self.course_knowledge_mapping = self._init_course_knowledge_mapping()

        # IRT parameters for courses (difficulty and discrimination)
        self.course_parameters = self._init_course_parameters()

    def _init_course_knowledge_mapping(self) -> Dict[str, List[str]]:
        """
        Initialize mapping from courses to knowledge domains

        Returns:
            Dictionary mapping course names to knowledge domains
        """
        # Simplified mapping - in production this should be loaded from database
        return {
            "数学分析": ["数学基础", "微积分"],
            "高等数学": ["数学基础", "微积分"],
            "线性代数": ["数学基础", "代数"],
            "概率论与数理统计": ["数学基础", "概率统计"],
            "离散数学": ["数学基础", "离散结构"],

            "程序设计基础": ["编程基础", "算法思维"],
            "C语言程序设计": ["编程基础", "系统编程"],
            "Python程序设计": ["编程基础", "脚本编程"],
            "Java程序设计": ["编程基础", "面向对象"],

            "数据结构": ["算法基础", "数据组织"],
            "算法设计与分析": ["算法基础", "算法设计"],

            "计算机组成原理": ["计算机系统", "硬件基础"],
            "操作系统": ["计算机系统", "系统软件"],
            "计算机网络": ["计算机系统", "网络通信"],

            "数据库系统": ["数据管理", "数据库技术"],
            "软件工程": ["软件开发", "工程方法"],

            "机器学习": ["人工智能", "数据分析"],
            "深度学习": ["人工智能", "神经网络"],
            "自然语言处理": ["人工智能", "语言处理"],
            "计算机视觉": ["人工智能", "图像处理"],
        }

    def _init_course_parameters(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize IRT parameters for courses

        Returns:
            Dictionary with course difficulty and discrimination parameters
        """
        # Simplified parameters - should be learned from actual student data
        # difficulty: course difficulty (-3 to 3, higher = harder)
        # discrimination: how well course score differentiates knowledge level
        return {
            "数学分析": {"difficulty": 1.5, "discrimination": 1.2},
            "高等数学": {"difficulty": 0.8, "discrimination": 1.0},
            "线性代数": {"difficulty": 0.5, "discrimination": 1.1},
            "概率论与数理统计": {"difficulty": 1.0, "discrimination": 1.0},
            "离散数学": {"difficulty": 1.2, "discrimination": 1.1},

            "程序设计基础": {"difficulty": 0.3, "discrimination": 0.9},
            "C语言程序设计": {"difficulty": 0.8, "discrimination": 1.0},
            "Python程序设计": {"difficulty": 0.5, "discrimination": 0.9},
            "Java程序设计": {"difficulty": 0.7, "discrimination": 1.0},

            "数据结构": {"difficulty": 1.3, "discrimination": 1.2},
            "算法设计与分析": {"difficulty": 1.8, "discrimination": 1.3},

            "机器学习": {"difficulty": 2.0, "discrimination": 1.2},
            "深度学习": {"difficulty": 2.2, "discrimination": 1.3},
        }

    def _score_to_ability(self, score: float) -> float:
        """
        Convert raw score (0-100) to IRT ability parameter

        Args:
            score: Raw score in range [0, 100]

        Returns:
            Ability estimate in range [-3, 3]
        """
        # Simple linear transformation with bounds
        # In production, use proper IRT estimation
        normalized = (score - 60) / 20  # Center at 60, scale by 20
        return np.clip(normalized, -3, 3)

    def estimate_knowledge_state(self,
                                 course_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Estimate student's knowledge state from course scores

        Args:
            course_scores: Dictionary mapping course names to scores (0-100)

        Returns:
            Dictionary mapping knowledge domains to mastery levels (0-1)
        """
        # Initialize knowledge domain abilities
        domain_abilities = {}
        domain_counts = {}

        # Aggregate scores by knowledge domain
        for course_name, score in course_scores.items():
            if course_name not in self.course_knowledge_mapping:
                logger.warning(f"Course {course_name} not in mapping, skipping")
                continue

            # Convert score to ability
            ability = self._score_to_ability(score)

            # Update all related knowledge domains
            for domain in self.course_knowledge_mapping[course_name]:
                if domain not in domain_abilities:
                    domain_abilities[domain] = 0.0
                    domain_counts[domain] = 0

                domain_abilities[domain] += ability
                domain_counts[domain] += 1

        # Average abilities for each domain and normalize to [0, 1]
        knowledge_state = {}
        for domain in domain_abilities:
            avg_ability = domain_abilities[domain] / domain_counts[domain]
            # Transform from [-3, 3] to [0, 1] using sigmoid
            knowledge_state[domain] = expit(avg_ability)

        return knowledge_state

    def analyze_knowledge_state(self,
                               knowledge_state: Dict[str, float]) -> Tuple[float, List[str], List[str]]:
        """
        Analyze knowledge state to identify strengths and weaknesses

        Args:
            knowledge_state: Dictionary mapping domains to mastery levels

        Returns:
            Tuple of (overall_level, strengths, weaknesses)
        """
        if not knowledge_state:
            return 0.0, [], []

        # Calculate overall level
        overall_level = np.mean(list(knowledge_state.values()))

        # Identify strengths (top 30%)
        sorted_domains = sorted(
            knowledge_state.items(),
            key=lambda x: x[1],
            reverse=True
        )

        threshold_strength = 0.7  # Domains above 0.7 are strengths
        threshold_weakness = 0.4  # Domains below 0.4 are weaknesses

        strengths = [
            domain for domain, level in sorted_domains
            if level >= threshold_strength
        ]

        weaknesses = [
            domain for domain, level in sorted_domains
            if level <= threshold_weakness
        ]

        return overall_level, strengths, weaknesses

    def calculate_course_difficulty_for_student(self,
                                                course_name: str,
                                                knowledge_state: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculate personalized difficulty of a course for a student

        Args:
            course_name: Name of the course
            knowledge_state: Student's current knowledge state

        Returns:
            Tuple of (difficulty_score, difficulty_label)
        """
        # Get course parameters
        if course_name not in self.course_parameters:
            return 0.5, "中等"  # Default medium difficulty

        course_params = self.course_parameters[course_name]
        base_difficulty = course_params["difficulty"]

        # Get required knowledge domains for this course
        if course_name not in self.course_knowledge_mapping:
            return 0.5, "中等"

        required_domains = self.course_knowledge_mapping[course_name]

        # Calculate student's readiness for this course
        readiness_scores = []
        for domain in required_domains:
            if domain in knowledge_state:
                readiness_scores.append(knowledge_state[domain])

        if not readiness_scores:
            avg_readiness = 0.5
        else:
            avg_readiness = np.mean(readiness_scores)

        # Personalized difficulty = base difficulty - student readiness
        # Higher readiness → lower perceived difficulty
        personalized_difficulty = base_difficulty - (avg_readiness - 0.5) * 2

        # Normalize to [0, 1]
        difficulty_score = expit(personalized_difficulty / 2)

        # Convert to label
        if difficulty_score < 0.3:
            difficulty_label = "简单"
        elif difficulty_score < 0.6:
            difficulty_label = "中等"
        elif difficulty_score < 0.8:
            difficulty_label = "较难"
        else:
            difficulty_label = "困难"

        return difficulty_score, difficulty_label


# Global instance
irt_tracker = IRTKnowledgeTracker()


def get_knowledge_tracker() -> IRTKnowledgeTracker:
    """Get the global knowledge tracker instance"""
    return irt_tracker
