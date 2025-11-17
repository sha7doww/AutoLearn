# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SmartPath** (智能导学系统) is an educational technology project implementing **KTAS** (Knowledge Tracking-Enhanced Agentic Search for Personalized Learning). The system combines:

- **IRT Knowledge Tracking** - Item Response Theory model for estimating student knowledge mastery
- **Intelligent Recommendation** - Personalized course recommendations based on knowledge gaps
- **Learning Path Planning** - Automated learning sequence generation
- **3D Knowledge Graph** - Interactive visualization of course relationships using Three.js

This is a full-stack application with a FastAPI backend and Vue 3 frontend, supporting both Neo4j graph database mode and demo mode (JSON-based, no database required).

---

## Quick Start Commands

### Environment Setup (First Time Only)

```bash
# Setup environment (creates micromamba environment)
scripts/setup.sh

# Optional: Setup Neo4j database (requires Docker)
scripts/setup-neo4j.sh
```

### Daily Development Workflow

```bash
# 1. Activate environment (required for each new terminal session)
source scripts/activate.sh

# 2. Start backend and frontend services
scripts/start.sh

# 3. Stop services when done
scripts/stop.sh
```

**Access Points:**
- Main Application: http://localhost:8080/dashboard
- 3D Knowledge Graph: http://localhost:8080/home
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Backend Development

```bash
# Activate environment first
source scripts/activate.sh
cd backend

# Run backend directly (for debugging)
python -m app.main

# Test APIs
python scripts/test_api.py

# Initialize Neo4j database (if using Neo4j mode)
python scripts/init_neo4j.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Development server with hot-reload
npm run serve

# Production build
npm run build

# Lint and fix
npm run lint
```

### Testing Commands

```bash
# Test backend APIs
cd backend
python scripts/test_api.py

# Check backend health
curl http://localhost:8000/health

# Test course API
curl http://localhost:8000/api/courses/all
```

---

## Architecture

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Neo4j - Graph database (optional, supports demo mode without it)
- NumPy/SciPy - Scientific computing for IRT model
- Pydantic - Data validation and settings management

**Frontend:**
- Vue 3 (Composition API) - Frontend framework
- Vue Router 4 - Client-side routing
- Three.js - 3D visualization for knowledge graph
- vis-network - 2D network graph visualization
- Element Plus - UI component library
- Axios - HTTP client

**Development Tools:**
- micromamba - Python environment management (preferred over conda)
- Vue CLI 5 - Frontend build tooling
- ESLint - JavaScript/Vue linting

### Dual-Mode Operation

The system operates in two modes:

1. **Demo Mode (Default)**: Uses `backend/data/course_data.json` with 67 courses. No database required.
2. **Neo4j Mode**: Uses graph database for complex queries and relationship analysis. Auto-falls back to demo mode if connection fails.

Backend automatically detects Neo4j availability at startup and switches modes accordingly.

### Project Structure

```
AutoLearn/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── main.py              # Application entry, lifespan events, CORS
│   │   ├── config.py            # Settings management (Pydantic)
│   │   ├── routers/
│   │   │   ├── courses.py       # Course CRUD APIs
│   │   │   └── knowledge.py     # Knowledge tracking APIs (IRT model)
│   │   ├── services/
│   │   │   ├── course_service.py         # Course business logic
│   │   │   └── knowledge_tracking.py     # IRT model implementation ⭐
│   │   ├── schemas/             # Pydantic data models
│   │   │   ├── course.py        # Course schemas
│   │   │   └── knowledge.py     # Knowledge tracking schemas
│   │   └── database/
│   │       ├── neo4j_driver.py  # Neo4j connection manager
│   │       └── mock_data.py     # Demo mode data provider
│   ├── data/
│   │   └── course_data.json     # 67 courses dataset
│   ├── scripts/
│   │   ├── init_neo4j.py        # Initialize Neo4j with course data
│   │   └── test_api.py          # API testing script
│   └── requirements.txt         # Python dependencies
│
├── frontend/                     # Vue 3 Frontend
│   ├── src/
│   │   ├── main.js              # App entry, registers Axios globally
│   │   ├── App.vue              # Root component with router-view
│   │   ├── router/index.js      # Route definitions
│   │   ├── views/
│   │   │   ├── LoginView.vue           # Login page (/)
│   │   │   ├── HomeView.vue            # 3D knowledge graph (/home) ⭐
│   │   │   ├── StudentDashboard.vue    # Main dashboard (/dashboard) ⭐
│   │   │   ├── CourseOutline.vue       # Course details (/course)
│   │   │   └── ChatAssistant.vue       # AI assistant (/chat-assistant)
│   │   └── components/
│   │       ├── KnowledgeRadar.vue       # Radar chart visualization ⭐
│   │       ├── LearningPathTimeline.vue # Learning path timeline ⭐
│   │       ├── myDagre.vue              # 2D network graph (vis-network)
│   │       ├── NavBar.vue               # Top navigation
│   │       ├── SideBar.vue              # Side navigation
│   │       └── LsSb.vue                 # Additional sidebar
│   ├── package.json             # Node dependencies
│   ├── vue.config.js            # Vue CLI config (active)
│   └── babel.config.js          # Babel config
│
└── scripts/                      # Management Scripts
    ├── setup.sh                 # Environment setup (micromamba)
    ├── setup-neo4j.sh           # Neo4j Docker setup (optional)
    ├── activate.sh              # Activate micromamba environment
    ├── start.sh                 # Start backend + frontend
    └── stop.sh                  # Stop services
```

### Key Components

**Backend Core Logic:**

1. **IRT Knowledge Tracker** (`backend/app/services/knowledge_tracking.py`):
   - Implements Item Response Theory model
   - Maps courses to knowledge domains
   - Estimates student knowledge mastery from scores
   - Provides personalized course recommendations
   - Core methods: `estimate_knowledge_state()`, `recommend_courses()`

2. **Course Service** (`backend/app/services/course_service.py`):
   - Handles course CRUD operations
   - Learning path generation using graph traversal
   - Prerequisite checking
   - Works with both Neo4j and demo mode

3. **Neo4j Driver** (`backend/app/database/neo4j_driver.py`):
   - Singleton pattern for connection management
   - Automatic fallback to demo mode on failure
   - Query execution with error handling

**Frontend Core Components:**

1. **StudentDashboard.vue** (`frontend/src/views/StudentDashboard.vue`):
   - Main interface for the intelligent tutoring system
   - Score input, knowledge state analysis, learning path generation
   - Integrates KnowledgeRadar and LearningPathTimeline components

2. **HomeView.vue** (`frontend/src/views/HomeView.vue`):
   - 3D spherical course graph using Three.js
   - 10,000 particle starfield background
   - OrbitControls with custom mouse button mapping
   - CSS2DRenderer for course labels (layered over WebGL)
   - Bezier curve edges with animated opacity
   - Search functionality with smooth camera animation
   - **Critical**: Controls must be attached to WebGL renderer's domElement, not CSS2DRenderer

3. **KnowledgeRadar.vue** (`frontend/src/components/KnowledgeRadar.vue`):
   - Radar chart visualization of knowledge mastery
   - Shows strengths and weaknesses across knowledge domains

4. **LearningPathTimeline.vue** (`frontend/src/components/LearningPathTimeline.vue`):
   - Timeline visualization of recommended learning sequence
   - Shows prerequisites and estimated duration

### Route Configuration

| Path | Component | Description |
|------|-----------|-------------|
| `/` | LoginView | Landing/login page |
| `/home` | HomeView | 3D spherical course graph (Three.js) |
| `/dashboard` | StudentDashboard | Main intelligent tutoring interface ⭐ |
| `/course` | CourseOutline | Course details and outline |
| `/mydagre` | myDagre | 2D directed network graph (vis-network) |
| `/chat-assistant` | ChatAssistant | AI learning assistant |
| `/LsSb` | LsSb | Sidebar component view |

All routes use Vue Router 4 with Web History mode (no hash in URLs).

---

## Core Dataset

The system includes 67 computer science courses hardcoded in:
- `backend/data/course_data.json`
- `frontend/src/views/HomeView.vue` (duplicated for 3D viz)
- `frontend/src/components/myDagre.vue` (duplicated for 2D viz)

**Data Structure:**
```json
{
  "nodes": [
    {"id": 1, "label": "高等数学", "difficulty": "基础", "credits": 5, "course_type": "必修"}
  ],
  "edges": [
    {"from": 1, "to": 5}  // Course 1 is prerequisite for Course 5
  ]
}
```

**Important**: Course data is currently duplicated across multiple files. Consider centralizing this data or fetching from backend API for consistency.

---

## Development Guidelines

### Adding New Courses

1. Update `backend/data/course_data.json` with new course nodes/edges
2. If using Neo4j: Run `python scripts/init_neo4j.py` to reinitialize database
3. Update frontend components that use hardcoded data:
   - `frontend/src/views/HomeView.vue`
   - `frontend/src/components/myDagre.vue`
4. Ensure course IDs are unique and match between nodes and edges

### Modifying IRT Model

1. Edit `backend/app/services/knowledge_tracking.py`
2. Update course-to-knowledge-domain mapping in `_init_course_knowledge_mapping()`
3. Adjust IRT parameters in `_init_course_parameters()`
4. Update corresponding Pydantic schemas in `backend/app/schemas/knowledge.py`

### Adding New API Endpoints

1. Define Pydantic models in `backend/app/schemas/`
2. Implement business logic in `backend/app/services/`
3. Create router endpoints in `backend/app/routers/`
4. Register router in `backend/app/main.py` with `app.include_router()`
5. Test with `curl` or update `backend/scripts/test_api.py`

### Adding New Frontend Pages

1. Create Vue component in `frontend/src/views/`
2. Import in `frontend/src/router/index.js`
3. Add route object to `routes` array
4. Add navigation links in NavBar or SideBar components

### Working with Three.js Visualization

**Node Positioning:**
- Located in `HomeView.vue` lines ~308-350 in `createGraph()`
- Uses golden angle algorithm for spherical distribution: `phi = i * Math.PI * (3 - Math.sqrt(5))`

**Edge Styling:**
- Modify `edgeMaterial` (around line 353)
- Bezier curves created with `QuadraticBezierCurve3`

**Camera Animation:**
- Search functionality in `searchNode()` function (lines ~167-218)
- Uses `camera.position.lerp()` for smooth movement

**Event Handling:**
- OrbitControls attached to `renderer.domElement` (WebGL canvas)
- CSS2DRenderer has `pointer-events: none` to allow click-through
- Raycasting for node selection

**Memory Management:**
- Always clean up in `onBeforeUnmount`:
  - Dispose geometries, materials, textures
  - Remove event listeners
  - Cancel animation frames

---

## Environment Variables

Create `backend/.env` file (see `backend/.env.example`):

```env
# Neo4j Configuration (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

System works without `.env` file (uses demo mode defaults).

---

## Important Notes

### Build Tool Configuration

- Frontend uses **Vue CLI 5** (active)
- `vite.config.js` exists but is NOT currently used
- Run commands with `npm run serve/build/lint`, not `vite`

### Global Properties

Axios is registered globally in `frontend/src/main.js`:
```javascript
app.config.globalProperties.$axios = axios
```

Access in components with `this.$axios` (Options API) or import directly (Composition API).

### Data Duplication Issue

Course data is currently duplicated in multiple locations. This can lead to inconsistencies. Consider:
1. Fetching data from backend API instead of hardcoding
2. Using Vuex/Pinia for centralized state management
3. Creating a shared data module

### Neo4j Docker Setup

When using `scripts/setup-neo4j.sh`:
- Requires Docker installed and running
- Creates container named `neo4j` on ports 7474 (HTTP) and 7687 (Bolt)
- Default credentials: `neo4j/password`
- Automatically initializes with 67 courses from `backend/data/course_data.json`

### Line Ending Issues

If scripts fail with `^M` or `\r\n` errors:
```bash
scripts/fix-line-endings.sh
```

### Logging

Logs are written to:
- `logs/backend.log`
- `logs/frontend.log`

Process IDs stored in:
- `logs/backend.pid`
- `logs/frontend.pid`

---

## Troubleshooting

### Backend won't start

1. Check environment is activated: `source scripts/activate.sh`
2. Verify dependencies: `cd backend && pip install -r requirements.txt`
3. Check port 8000 availability: `lsof -i :8000`
4. Review logs: `tail -f logs/backend.log`

### Frontend won't start

1. Check Node.js version: `node --version` (>= 14.x required)
2. Reinstall dependencies: `cd frontend && rm -rf node_modules && npm install`
3. Check port 8080 availability: `lsof -i :8080`
4. Review logs: `tail -f logs/frontend.log`

### Neo4j connection fails

System automatically falls back to demo mode. To fix:
1. Check Docker container: `docker ps | grep neo4j`
2. Start if stopped: `docker start neo4j`
3. Check credentials in `backend/.env`
4. Verify ports: `lsof -i :7474` and `lsof -i :7687`
5. Reinitialize: `scripts/setup-neo4j.sh`

### 3D Visualization issues

- Check browser console for WebGL errors
- Ensure GPU acceleration is enabled in browser settings
- Test with Chrome/Firefox (better Three.js support)
- Check for memory leaks in `onBeforeUnmount` cleanup

---

## API Endpoints

Key backend endpoints (see http://localhost:8000/docs for full documentation):

```
GET  /                              # Root info
GET  /health                        # Health check
GET  /api/courses/all               # Get all courses
GET  /api/courses/{id}              # Get course by ID
POST /api/courses/search            # Search courses
GET  /api/courses/{id}/prerequisites # Get prerequisites
POST /api/courses/learning-path     # Generate learning path
POST /api/knowledge/analyze         # Analyze knowledge state (IRT)
POST /api/knowledge/recommend       # Get course recommendations
```

---

## Performance Considerations

- 3D visualization requires significant GPU resources - test on target devices
- 10,000 particle starfield can impact performance on low-end devices
- Consider reducing particle count or using Level of Detail (LOD) techniques
- Neo4j mode is more performant for complex graph queries than demo mode
- Frontend currently doesn't implement code splitting - consider lazy loading routes

---

## Future Integration Points

Based on current codebase structure, consider:
- Implementing user authentication (LoginView currently shows static content)
- Adding WebSocket support for real-time chat in ChatAssistant
- Fetching course data from backend API instead of hardcoding in frontend
- Implementing Pinia/Vuex for centralized state management
- Adding proper course ID parameter routing for CourseOutline (currently hardcoded to "概率论与数理统计")
- Implementing actual AI chat functionality (currently placeholder)
