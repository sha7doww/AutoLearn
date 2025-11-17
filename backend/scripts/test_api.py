"""
API测试脚本
用于验证SmartPath后端API功能
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

# ANSI颜色代码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")


def print_section(title):
    print(f"\n{YELLOW}{'=' * 60}{RESET}")
    print(f"{YELLOW}{title}{RESET}")
    print(f"{YELLOW}{'=' * 60}{RESET}\n")


def test_health_check():
    """测试健康检查端点"""
    print_section("测试 1: 健康检查")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API运行正常")
            print_info(f"状态: {data.get('status')}")
            print_info(f"数据库: {data.get('database')}")
            return True
        else:
            print_error(f"健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"连接失败: {e}")
        print_info("请确保后端服务已启动在 http://localhost:8000")
        return False


def test_get_all_courses():
    """测试获取所有课程"""
    print_section("测试 2: 获取所有课程")
    try:
        response = requests.get(f"{API_BASE_URL}/api/courses/")
        if response.status_code == 200:
            courses = response.json()
            print_success(f"成功获取 {len(courses)} 门课程")
            # 显示前5门课程
            print_info("前5门课程:")
            for course in courses[:5]:
                print(f"  - {course['id']}: {course['label']} ({course.get('difficulty', 'N/A')})")
            return True
        else:
            print_error(f"获取课程失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def test_get_course_detail():
    """测试获取课程详情"""
    print_section("测试 3: 获取课程详情")
    course_id = 36  # 人工智能
    try:
        response = requests.get(f"{API_BASE_URL}/api/courses/{course_id}")
        if response.status_code == 200:
            course = response.json()
            print_success(f"成功获取课程详情")
            print_info(f"课程: {course['label']}")
            print_info(f"难度: {course.get('difficulty', 'N/A')}")
            print_info(f"学分: {course.get('credits', 'N/A')}")
            print_info(f"先修课程: {course.get('prerequisites', [])}")
            return True
        else:
            print_error(f"获取课程详情失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def test_search_courses():
    """测试课程搜索"""
    print_section("测试 4: 搜索课程")
    keyword = "算法"
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/courses/search",
            json={"keyword": keyword, "search_type": "fuzzy"}
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"搜索成功，找到 {data['total']} 门相关课程")
            for course in data['courses']:
                print(f"  - {course['label']}")
            return True
        else:
            print_error(f"搜索失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def test_knowledge_state():
    """测试知识状态计算"""
    print_section("测试 5: 知识状态计算")
    sample_scores = {
        "高等数学": 85,
        "线性代数": 78,
        "概率论与数理统计": 82,
        "程序设计原理与C语言": 90,
        "数据结构": 88
    }
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/knowledge/state",
            json={
                "student_id": "test_student",
                "course_scores": sample_scores
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success("知识状态计算成功")
            print_info(f"综合水平: {data['overall_level']:.2f}")
            print_info(f"优势领域: {', '.join(data['strengths'])}")
            print_info(f"薄弱环节: {', '.join(data['weaknesses'])}")
            print_info("知识向量:")
            for domain, value in data['knowledge_vector'].items():
                print(f"  - {domain}: {value:.2f}")
            return True
        else:
            print_error(f"知识状态计算失败: {response.status_code}")
            print_info(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def test_recommendations():
    """测试课程推荐"""
    print_section("测试 6: 课程推荐")
    sample_knowledge_state = {
        "数学基础": 0.75,
        "编程基础": 0.85,
        "算法基础": 0.78
    }
    completed_courses = [1, 30, 37, 39]  # 已完成的课程ID

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/knowledge/recommend",
            json={
                "student_id": "test_student",
                "knowledge_state": sample_knowledge_state,
                "completed_courses": completed_courses,
                "max_recommendations": 5
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"推荐成功，获得 {len(data['recommendations'])} 个推荐")
            for i, rec in enumerate(data['recommendations'][:5], 1):
                print(f"\n  推荐 {i}: {rec['course_name']}")
                print(f"    匹配度: {rec['match_score']:.2f}")
                print(f"    难度: {rec['difficulty_match']}")
                print(f"    理由: {rec['reason']}")
            return True
        else:
            print_error(f"推荐失败: {response.status_code}")
            print_info(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def test_learning_path():
    """测试学习路径生成"""
    print_section("测试 7: 学习路径生成")
    target_course_id = 36  # 人工智能
    completed_courses = [1, 30, 37, 39, 33, 34, 35]

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/courses/learning-path",
            json={
                "target_course_id": target_course_id,
                "completed_courses": completed_courses
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"学习路径生成成功")
            print_info(f"目标课程: {data['target_course_name']}")
            print_info(f"需要学习 {len(data['recommended_sequence'])} 门课程")
            print_info(f"总学分: {data['total_credits']}")
            print_info(f"预计学期: {data['estimated_semesters']}")
            print_info("\n学习序列:")
            for i, course in enumerate(data['course_details'], 1):
                print(f"  {i}. {course['label']} ({course.get('credits', 3)}学分)")
            return True
        else:
            print_error(f"路径生成失败: {response.status_code}")
            print_info(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False


def main():
    """运行所有测试"""
    print(f"\n{BLUE}{'*' * 60}{RESET}")
    print(f"{BLUE}SmartPath API 测试套件{RESET}")
    print(f"{BLUE}{'*' * 60}{RESET}")

    tests = [
        ("健康检查", test_health_check),
        ("获取所有课程", test_get_all_courses),
        ("获取课程详情", test_get_course_detail),
        ("搜索课程", test_search_courses),
        ("知识状态计算", test_knowledge_state),
        ("课程推荐", test_recommendations),
        ("学习路径生成", test_learning_path)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print_info("\n测试被中断")
            sys.exit(0)
        except Exception as e:
            print_error(f"测试异常: {e}")
            results.append((name, False))

    # 显示总结
    print_section("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print(f"\n{GREEN}{'=' * 60}{RESET}")
        print(f"{GREEN}所有测试通过！系统运行正常。{RESET}")
        print(f"{GREEN}{'=' * 60}{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{'=' * 60}{RESET}")
        print(f"{RED}部分测试失败，请检查日志。{RESET}")
        print(f"{RED}{'=' * 60}{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
