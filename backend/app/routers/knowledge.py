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
import random

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


def get_course_service(db: Neo4jDriver = Depends(get_neo4j_driver)) -> CourseService:
    """Dependency to get course service"""
    return CourseService(db)


def generate_personalized_reason(
    course_name: str,
    prerequisites_met: bool,
    knowledge_readiness: float,
    difficulty_score: float,
    missing_prerequisites: list
) -> str:
    """
    Generate personalized course recommendation reasons based on course characteristics

    TODO: Replace with LLM-generated personalized recommendations in the future
    """
    # Course category detection
    ai_keywords = ['人工智能', '机器学习', '深度学习', '神经网络', '计算机视觉', '自然语言', '模式识别', '智能', '数据挖掘']
    system_keywords = ['操作系统', '计算机系统', '编译', '体系结构', '嵌入式', '组成']
    network_keywords = ['网络', '分布式', '云计算', '并行计算']
    math_keywords = ['数学', '概率', '统计', '线性代数', '离散', '微积分', '数值', '最优化']
    programming_keywords = ['程序设计', 'Java', 'C++', 'Python', '编程', '算法', '数据结构']
    practical_keywords = ['实践', '项目', '工程', 'CAD', '多媒体', '游戏']

    is_ai = any(keyword in course_name for keyword in ai_keywords)
    is_system = any(keyword in course_name for keyword in system_keywords)
    is_network = any(keyword in course_name for keyword in network_keywords)
    is_math = any(keyword in course_name for keyword in math_keywords)
    is_programming = any(keyword in course_name for keyword in programming_keywords)
    is_practical = any(keyword in course_name for keyword in practical_keywords)

    reason_templates = []

    # Prerequisites assessment
    if not prerequisites_met:
        prereq_reasons = [
            f"建议先完成{len(missing_prerequisites)}门基础课程，打好理论基础",
            f"当前还需完成{len(missing_prerequisites)}门前置课程，建议循序渐进学习",
            f"为更好掌握本课程，建议优先完成{len(missing_prerequisites)}门先修课"
        ]
        reason_templates.append(random.choice(prereq_reasons))
    else:
        prereq_reasons = [
            "已具备必要的知识基础",
            "先修课程已完成，可以开始学习",
            "前置知识储备充足",
            "基础课程已掌握"
        ]
        reason_templates.append(random.choice(prereq_reasons))

    # Knowledge readiness with course-specific advice
    if knowledge_readiness > 0.7:
        if is_ai:
            readiness_reasons = [
                "您的数学和算法基础扎实，适合深入学习AI技术",
                "知识储备充分，建议尝试前沿的AI算法与应用",
                "理论基础优秀，可以开始探索深度学习等高级主题"
            ]
        elif is_system:
            readiness_reasons = [
                "系统基础扎实，可以深入理解底层原理",
                "知识储备充分，适合学习系统级编程",
                "理论基础优秀，建议学习操作系统内核机制"
            ]
        elif is_math:
            readiness_reasons = [
                "数学功底扎实，建议学习更高级的数学课程",
                "理论基础优秀，可以挑战抽象数学思维",
                "知识储备充分，适合深入数学证明与推导"
            ]
        elif is_practical:
            readiness_reasons = [
                "理论基础扎实，正是实践动手的好时机",
                "知识储备充分，建议通过项目巩固理论知识",
                "适合通过实践项目提升工程能力"
            ]
        else:
            readiness_reasons = [
                "知识储备充分，可以轻松掌握",
                "理论基础扎实，学习起来会比较顺利",
                "已具备良好的知识基础"
            ]
        reason_templates.append(random.choice(readiness_reasons))

    elif knowledge_readiness > 0.4:
        if is_ai:
            readiness_reasons = [
                "建议同步复习线性代数和概率论，助力AI算法理解",
                "数学基础基本具备，学习时注意加强矩阵运算和优化理论",
                "适合入门AI领域，建议多实践经典算法"
            ]
        elif is_system:
            readiness_reasons = [
                "系统基础基本具备，学习时建议多动手实验",
                "适合系统编程入门，注意理解底层原理",
                "建议边学边实践，加深对系统机制的理解"
            ]
        elif is_programming:
            readiness_reasons = [
                "编程基础基本具备，建议通过大量练习提升",
                "适合巩固编程能力，注意培养良好的代码习惯",
                "知识储备基本满足，多写代码是提升关键"
            ]
        elif is_network:
            readiness_reasons = [
                "网络基础基本具备，建议学习时搭建实验环境",
                "适合学习网络协议，注意理论与实践结合",
                "知识储备基本满足，建议通过抓包分析加深理解"
            ]
        else:
            readiness_reasons = [
                "知识储备基本满足，学习时注意查缺补漏",
                "基础知识已具备，建议稳扎稳打学习",
                "适合当前水平，边学边巩固基础"
            ]
        reason_templates.append(random.choice(readiness_reasons))

    else:
        if is_ai or is_math:
            readiness_reasons = [
                "建议先加强数学基础（微积分、线性代数、概率论）",
                "数学基础需要强化，建议先学习相关数学课程",
                "为更好理解课程内容，建议优先巩固数学知识"
            ]
        elif is_system or is_programming:
            readiness_reasons = [
                "建议先完成编程基础课程，提升代码能力",
                "编程基础需要加强，建议多练习算法和数据结构",
                "为顺利学习本课程，建议先巩固编程基本功"
            ]
        else:
            readiness_reasons = [
                "建议先加强基础知识，循序渐进学习",
                "基础知识需要巩固，建议先学习前置课程",
                "为更好掌握内容，建议优先完成基础课程"
            ]
        reason_templates.append(random.choice(readiness_reasons))

    # Difficulty assessment with specific advice
    if 0.4 <= difficulty_score <= 0.7:
        if is_ai:
            difficulty_reasons = [
                "课程难度适中，是进入AI领域的理想选择",
                "难度设置合理，适合系统学习机器学习理论",
                "挑战度适中，建议结合Kaggle竞赛实践"
            ]
        elif is_practical:
            difficulty_reasons = [
                "项目难度适中，适合提升工程实践能力",
                "实践项目设置合理，能有效巩固理论知识",
                "工程难度适宜，建议组队完成项目"
            ]
        elif is_math:
            difficulty_reasons = [
                "理论难度适中，适合深入数学思维训练",
                "数学深度合理，建议多做习题巩固",
                "难度设置适宜，能有效提升数学素养"
            ]
        else:
            difficulty_reasons = [
                "难度适中，适合当前阶段学习",
                "课程难度设置合理，学习体验良好",
                "挑战度适宜，能有效提升专业能力"
            ]
        reason_templates.append(random.choice(difficulty_reasons))

    elif difficulty_score < 0.4:
        if is_practical:
            difficulty_reasons = [
                "入门级实践项目，适合培养动手能力",
                "项目难度较低，适合快速上手实践",
                "实践难度友好，建议独立完成积累经验"
            ]
        elif is_programming:
            difficulty_reasons = [
                "编程难度适中，适合打好编程基础",
                "代码量适中，适合培养编程习惯",
                "难度友好，建议多写代码提升熟练度"
            ]
        else:
            difficulty_reasons = [
                "课程难度较低，可以快速掌握",
                "入门难度友好，学习压力较小",
                "内容相对简单，适合轻松学习"
            ]
        reason_templates.append(random.choice(difficulty_reasons))

    else:  # High difficulty
        if is_ai:
            difficulty_reasons = [
                "AI前沿课程，具有较高挑战性，建议充分预习",
                "深度学习理论较难，建议多参考论文和开源项目",
                "算法理论深入，需要投入较多时间钻研"
            ]
        elif is_system:
            difficulty_reasons = [
                "系统底层原理复杂，建议多动手实验验证",
                "涉及较多底层细节，需要耐心调试和分析",
                "系统级编程难度高，建议分模块逐步攻克"
            ]
        elif is_math:
            difficulty_reasons = [
                "数学理论深入，建议多推导证明加深理解",
                "理论抽象度高，需要投入较多时间思考",
                "数学难度较大，建议组建学习小组互助"
            ]
        else:
            difficulty_reasons = [
                "课程具有一定挑战性，建议做好时间规划",
                "内容较为深入，需要持续投入学习",
                "难度较高，建议充分利用课程资源"
            ]
        reason_templates.append(random.choice(difficulty_reasons))

    return "，".join(reason_templates)


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
            # 1. Prerequisites satisfaction (35%)
            # 2. Knowledge readiness (40%)
            # 3. Optimal challenge curve (25%)
            match_score = 0.0

            # 1. Prerequisites (35%)
            if prerequisites_met:
                match_score += 0.35
            else:
                # Strong penalty for missing prerequisites
                penalty = min(0.35, len(missing_prerequisites) * 0.12)
                match_score += max(0, 0.35 - penalty)

            # 2. Knowledge readiness (40%) - Most important factor
            # Use a bell curve that peaks at moderate readiness
            knowledge_readiness = 1.0 - difficulty_score
            if knowledge_readiness > 0.85:
                # Too easy - discourage
                readiness_score = 0.40 * (0.5 + 0.5 * (1 - knowledge_readiness) / 0.15)
            elif knowledge_readiness >= 0.6:
                # Sweet spot - high readiness
                readiness_score = 0.40
            elif knowledge_readiness >= 0.4:
                # Moderate - acceptable
                readiness_score = 0.40 * (0.6 + 0.4 * (knowledge_readiness - 0.4) / 0.2)
            elif knowledge_readiness >= 0.25:
                # Below threshold - penalize
                readiness_score = 0.40 * (0.3 + 0.3 * (knowledge_readiness - 0.25) / 0.15)
            else:
                # Too difficult - strong penalty
                readiness_score = 0.40 * (0.3 * knowledge_readiness / 0.25)
            match_score += readiness_score

            # 3. Optimal challenge curve (25%)
            # Prefer moderate challenge - not too easy, not too hard
            if 0.3 <= difficulty_score <= 0.5:
                # Optimal zone
                challenge_score = 0.25
            elif 0.2 <= difficulty_score < 0.3 or 0.5 < difficulty_score <= 0.6:
                # Good zone
                challenge_score = 0.20
            elif 0.1 <= difficulty_score < 0.2 or 0.6 < difficulty_score <= 0.7:
                # Acceptable zone
                challenge_score = 0.15
            elif difficulty_score < 0.1:
                # Too easy - penalize
                challenge_score = 0.08
            elif difficulty_score <= 0.8:
                # Getting hard
                challenge_score = 0.10
            else:
                # Too hard - strong penalty
                challenge_score = 0.05
            match_score += challenge_score

            # Add random variation to ensure diversity (±3%)
            match_score += random.uniform(-0.03, 0.03)

            # Clamp to [0, 1] and scale to 60-95% range for display
            match_score = max(0.0, min(1.0, match_score))
            # Scale: map [0.5, 1.0] -> [0.6, 0.95], map [0, 0.5) -> [0.3, 0.6)
            if match_score >= 0.5:
                match_score = 0.6 + (match_score - 0.5) * 0.7  # 0.5->0.6, 1.0->0.95
            else:
                match_score = 0.3 + match_score * 0.6  # 0->0.3, 0.5->0.6

            # Generate personalized recommendation reason
            reason = generate_personalized_reason(
                course_name=course.label,
                prerequisites_met=prerequisites_met,
                knowledge_readiness=knowledge_readiness,
                difficulty_score=difficulty_score,
                missing_prerequisites=missing_prerequisites
            )

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
