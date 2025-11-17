<template>
  <div class="graph-container">
    <div ref="container"></div>
    <div class="overlay">
      <h1>课程关系图 Course Relationship Graph</h1>
      <p>拖动旋转，滚轮缩放，右键平移 | Drag to rotate, scroll to zoom, right-click to pan</p>
      <div class="search-box">
        <input v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜索课程..." />
        <button @click="searchNode">搜索</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer'
import { useRouter } from 'vue-router'


export default {
  setup() {
    const router = useRouter()
    const container = ref(null)
    const loading = ref(true)
    const searchQuery = ref('')
    let scene, camera, renderer, labelRenderer, controls;
    let nodes = [];
    let edges = []; // 显式声明
    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()
    

    const courseData = {
      nodes: [
        { id: 1, label: '数学分析' },
        { id: 2, label: '并行计算' },
        { id: 3, label: '数值计算及其计算机实现' },
        { id: 4, label: '自然语言处理导论' },
        { id: 5, label: '操作系统实践(进阶)' },
        { id: 6, label: '现代CAD技术(A)' },
        { id: 7, label: '计算机视觉' },
        { id: 8, label: '游戏项目实践' },
        { id: 9, label: '数据挖掘' },
        { id: 10, label: '多智能体系统与实践' },
        { id: 11, label: '计算机网络工程' },
        { id: 12, label: '网络安全基础' },
        { id: 13, label: '存储技术基础' },
        { id: 14, label: '模式识别与机器学习' },
        { id: 15, label: '服务器维护及网站建设' },
        { id: 16, label: '问题求解与程序设计' },
        { id: 17, label: '计算机图形学' },
        { id: 18, label: '云计算实践' },
        { id: 19, label: '创新创业基础与实践' },
        { id: 20, label: '多媒体技术' },
        { id: 21, label: '算法分析与设计' },
        { id: 22, label: '数字图像处理' },
        { id: 23, label: '人机交互技术' },
        { id: 24, label: '数学建模' },
        { id: 25, label: '数据可视化' },
        { id: 26, label: '最优化方法' },
        { id: 27, label: '计算机新技术前沿' },
        { id: 28, label: '信息系统安全概论' },
        { id: 29, label: '编程思维与实践' },
        { id: 30, label: '程序设计原理与C语言' },
        { id: 31, label: '大学物理B(一)：力学，热学' },
        { id: 32, label: '大学物理B（二）：电磁学、波动与光学部分' },
        { id: 33, label: '概率论与数理统计' },
        { id: 34, label: '计算机导论' },
        { id: 35, label: '离散数学' },
        { id: 36, label: '人工智能' },
        { id: 37, label: '数据结构' },
        { id: 38, label: '数字逻辑电路' },
        { id: 39, label: '线性代数' },
        { id: 40, label: '操作系统' },
        { id: 41, label: '计算机网络' },
        { id: 42, label: '嵌入式系统原理与实践' },
        { id: 43, label: '计算机系统结构' },
        { id: 44, label: '数据库系统原理与实践' },
        { id: 45, label: '编译原理与实践' },
        { id: 46, label: '信息工程伦理' },
        { id: 47, label: '线性代数进阶' },
        { id: 48, label: '计算机基础实践' },
        { id: 49, label: '面向对象程序设计（基于Java）' },
        { id: 50, label: '面向对象程序设计（基于C++）' },
        { id: 51, label: '专业英语' },
        { id: 52, label: '信号与系统' },
        { id: 53, label: '计算机组成与实践' },
        { id: 54, label: '生物信息学' },
        { id: 55, label: '大数据系统' },
        { id: 56, label: '智能推荐系统' },
        { id: 57, label: '视觉感知与前沿技术' },
        { id: 58, label: '统计学习算法导论' },
        { id: 59, label: '现代CAD技术（B）' },
        { id: 60, label: '可信机器学习' },
        { id: 61, label: '计算机动画' },
        { id: 62, label: '深度学习基础与导论' },
        { id: 63, label: '强化学习基础' },
        { id: 64, label: 'AIoT系统设计与实践' },
        { id: 65, label: '写作与表达' },
        { id: 66, label: 'python程序设计' },
        { id: 67, label: '大学英语' }
      ],
      edges: [
        { from: 34, to: 16 }, { from: 30, to: 16 }, { from: 1, to: 16 },
        { from: 1, to: 31 }, { from: 1, to: 32 }, { from: 1, to: 17 },
        { from: 39, to: 17 }, { from: 50, to: 17 }, { from: 37, to: 17 },
        { from: 11, to: 18 }, { from: 30, to: 21 }, { from: 37, to: 21 },
        { from: 66, to: 22 }, { from: 30, to: 23 }, { from: 1, to: 24 },
        { from: 39, to: 24 }, { from: 33, to: 24 }, { from: 29, to: 24 },
        { from: 37, to: 25 }, { from: 30, to: 25 }, { from: 39, to: 26 },
        { from: 34, to: 28 }, { from: 11, to: 28 }, { from: 44, to: 28 },
        { from: 40, to: 28 }, { from: 29, to: 36 }, { from: 30, to: 37 },
        { from: 33, to: 36 }, { from: 34, to: 36 }, { from: 35, to: 36 },
        { from: 37, to: 36 }, { from: 1, to: 36 }, { from: 39, to: 35 },
        { from: 39, to: 36 }, { from: 40, to: 2 }, { from: 53, to: 2 },
        { from: 1, to: 3 }, { from: 35, to: 3 }, { from: 30, to: 3 },
        { from: 33, to: 4 }, { from: 36, to: 4 }, { from: 40, to: 5 },
        { from: 50, to: 6 }, { from: 66, to: 6 }, { from: 22, to: 7 },
        { from: 37, to: 8 }, { from: 49, to: 8 }, { from: 50, to: 8 },
        { from: 49, to: 9 }, { from: 50, to: 9 }, { from: 1, to: 9 },
        { from: 39, to: 9 }, { from: 33, to: 9 }, { from: 30, to: 9 },
        { from: 1, to: 10 }, { from: 33, to: 10 }, { from: 39, to: 10 },
        { from: 36, to: 10 }, { from: 41, to: 11 }, { from: 40, to: 11 },
        { from: 40, to: 12 }, { from: 41, to: 12 }, { from: 41, to: 13 },
        { from: 1, to: 14 }, { from: 33, to: 14 }, { from: 36, to: 14 },
        { from: 39, to: 14 }, { from: 30, to: 40 }, { from: 37, to: 40 },
        { from: 53, to: 40 }, { from: 40, to: 41 }, { from: 43, to: 41 },
        { from: 30, to: 42 }, { from: 53, to: 42 }, { from: 38, to: 42 },
        { from: 37, to: 42 }, { from: 40, to: 43 }, { from: 53, to: 43 },
        { from: 30, to: 43 }, { from: 37, to: 44 }, { from: 40, to: 44 },
        { from: 30, to: 45 }, { from: 35, to: 45 }, { from: 37, to: 45 },
        { from: 40, to: 45 }, { from: 41, to: 46 }, { from: 34, to: 46 },
        { from: 36, to: 46 }, { from: 39, to: 47 }, { from: 30, to: 49 },
        { from: 30, to: 50 }, { from: 34, to: 51 }, { from: 67, to: 51 },
        { from: 1, to: 52 }, { from: 36, to: 54 }, { from: 40, to: 55 },
        { from: 39, to: 55 }, { from: 35, to: 55 }, { from: 37, to: 55 },
        { from: 44, to: 55 }, { from: 29, to: 55 }, { from: 36, to: 56 },
        { from: 37, to: 56 }, { from: 36, to: 57 }, { from: 37, to: 57 },
        { from: 39, to: 57 }, { from: 7, to: 57 }, { from: 1, to: 58 },
        { from: 33, to: 58 }, { from: 1, to: 59 }, { from: 36, to: 60 },
        { from: 49, to: 61 }, { from: 22, to: 62 }, { from: 14, to: 62 },
        { from: 36, to: 63 }, { from: 42, to: 64 }, { from: 4, to: 64 },
        { from: 14, to: 64 }, { from: 22, to: 64 }
      ]
    }

    function animate() {
      requestAnimationFrame(animate)

      nodes.forEach(node => {
        node.rotation.x += 0.005
        node.rotation.y += 0.005
      })

      edges.forEach(edge => {
        edge.material.opacity = (Math.sin(Date.now() * 0.001) + 1) * 0.3 + 0.3
      })

      controls.update()
      renderer.render(scene, camera)
      labelRenderer.render(scene, camera)
    }
    
    function searchNode() {
      const query = searchQuery.value.trim()
      if (!query) return

      nodes.forEach(node => {
        node.scale.set(1, 1, 1) // 重置所有节点大小
      })

      const targetIndex = courseData.nodes.findIndex(node => node.label.includes(query))
      if (targetIndex !== -1) {
        const targetSphere = nodes[targetIndex]
        if (targetSphere) {
          const targetPosition = targetSphere.position.clone()
          const targetCameraPosition = targetPosition.clone().multiplyScalar(2) // 想要去的新相机位置

          let progress = 0 // 进度
          const duration = 30 // 控制 lerp 的次数，越大越慢越平滑

          // 记录初始位置
          const startCameraPosition = camera.position.clone()
          const startTarget = controls.target.clone()
          const startScale = targetSphere.scale.clone()

          const animate = () => {
            if (progress < 1) {
              progress += 1 / duration

              // lerp 相机位置
              camera.position.lerpVectors(startCameraPosition, targetCameraPosition, progress)

              // lerp controls.target
              controls.target.lerpVectors(startTarget, targetPosition, progress)

              // lerp 放大节点
              targetSphere.scale.lerpVectors(startScale, new THREE.Vector3(2, 2, 2), progress)

              controls.update() // 刷新 controls（非常重要！）

              requestAnimationFrame(animate)
            } else {
              // 动画完成后，确保位置最终精确到位
              camera.position.copy(targetCameraPosition)
              controls.target.copy(targetPosition)
              targetSphere.scale.set(2, 2, 2)
              controls.update()
            }
          }

          animate()
        }
      }
    }

    function onMouseClick(event) {
      // 计算正确鼠标坐标
      const rect = renderer.domElement.getBoundingClientRect()
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(nodes)

      if (intersects.length > 0) {
        router.push({ name: 'course' }) // 移除参数传递
      }
    }

    // 初始化Three.js场景
    function init() {
      scene = new THREE.Scene()
      camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000)
      camera.position.z = 250

      // 初始化WebGL渲染器
      renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true,
        canvas: container.value.querySelector('canvas') || undefined
      })
      renderer.setSize(window.innerWidth, window.innerHeight)
      renderer.domElement.style.position = 'absolute'
      container.value.appendChild(renderer.domElement)

      // 初始化CSS2D标签渲染器
      labelRenderer = new CSS2DRenderer()
      labelRenderer.setSize(window.innerWidth, window.innerHeight)
      labelRenderer.domElement.style.position = 'absolute'
      labelRenderer.domElement.style.top = '0'
      labelRenderer.domElement.style.pointerEvents = 'none' // 关键设置
      labelRenderer.domElement.classList.add('label-renderer') // 添加CSS类
      container.value.appendChild(labelRenderer.domElement)

      // 初始化控制器（关键修改部分）
      controls = new OrbitControls(camera, renderer.domElement) // 使用WebGL渲染器作为事件源
      controls.enableDamping = true
      controls.dampingFactor = 0.05
      controls.screenSpacePanning = true // 启用屏幕空间平移
      controls.minDistance = 50
      controls.maxDistance = 500

      // 配置鼠标按键（关键）
      controls.mouseButtons = {
        LEFT: THREE.MOUSE.ROTATE,    // 左键旋转
        MIDDLE: THREE.MOUSE.DOLLY,   // 中键缩放
        RIGHT: THREE.MOUSE.PAN       // 右键平移
      }

      // 配置滚轮缩放
      controls.enableZoom = true
      controls.zoomSpeed = 1.0

      // 灯光设置
      scene.add(new THREE.AmbientLight(0xffffff, 0.5))
      const pointLight = new THREE.PointLight(0xffffff, 1)
      pointLight.position.set(10, 10, 10)
      scene.add(pointLight)

      createGraph();
      createStarfield(); // 添加星空背景

      // 事件监听
      window.addEventListener('resize', onWindowResize)
      renderer.domElement.addEventListener('click', onMouseClick) // 只保留这一个点击监听

      // 调试输出控制器状态
      console.log('Controls initialized:', {
        rotate: controls.enableRotate,
        zoom: controls.enableZoom,
        pan: controls.enablePan,
        damping: controls.enableDamping
      })
    }
    // 标签创建辅助函数
    const createLabelElement = (text) => {
      const labelDiv = document.createElement('div')
      labelDiv.className = 'node-label'
      labelDiv.textContent = text
      return labelDiv
    }

    // 创建图形元素
    const createGraph = () => {
      // 清除旧节点和边
      nodes.forEach(node => scene.remove(node))
      edges.forEach(edge => scene.remove(edge))
      nodes = []
      edges = []

      // 创建节点
      const sphereGeometry = new THREE.SphereGeometry(2, 32, 32)
      const sphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x00aaff,
        emissive: 0x0044aa,
        specular: 0xffffff,
        shininess: 100
      })

      const radius = 120
      const phi = Math.PI * (3 - Math.sqrt(5)) // 黄金角度

      courseData.nodes.forEach((node, index) => {
        // 节点位置计算
        const t = index / courseData.nodes.length
        const inclination = Math.acos(1 - 2 * t)
        const azimuth = phi * index

        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial)
        sphere.position.set(
          radius * Math.sin(inclination) * Math.cos(azimuth),
          radius * Math.sin(inclination) * Math.sin(azimuth),
          radius * Math.cos(inclination)
        )
        sphere.userData = { id: node.id } // 存储课程ID

        // 添加节点到场景
        scene.add(sphere)
        nodes.push(sphere)

        // 创建CSS2D标签（实际使用CSS2DObject）
        // eslint-disable-next-line no-unused-vars
        const label = new CSS2DObject(createLabelElement(node.label))
        label.position.copy(sphere.position)
        scene.add(label)
      })

      // 创建边
      const edgeMaterial = new THREE.LineBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.6
      })

      courseData.edges.forEach(edge => {
        const startNode = nodes.find(n => n.userData.id === edge.from)
        const endNode = nodes.find(n => n.userData.id === edge.to)

        if (startNode && endNode) {
          // 创建贝塞尔曲线
          const start = startNode.position
          const end = endNode.position
          const mid = new THREE.Vector3()
            .addVectors(start, end)
            .multiplyScalar(0.5)
            .add(new THREE.Vector3(
              (Math.random() - 0.5) * 20,
              (Math.random() - 0.5) * 20,
              (Math.random() - 0.5) * 20
            ))

          // 创建线对象
          const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
          const points = curve.getPoints(50)
          const geometry = new THREE.BufferGeometry().setFromPoints(points)
          const line = new THREE.Line(geometry, edgeMaterial)
          
          scene.add(line)
          edges.push(line) // 必须添加到edges数组
        }
      })
    }

    const createStarfield = () =>{
      const starGeometry = new THREE.BufferGeometry()
      const starMaterial = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.1,
        transparent: true,
        opacity: 0.8
      })

      const starVertices = []
      for (let i = 0; i < 10000; i++) {
        const x = (Math.random() - 0.5) * 3000
        const y = (Math.random() - 0.5) * 3000
        const z = (Math.random() - 0.5) * 3000
        starVertices.push(x, y, z)
      }

      starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3))
      const stars = new THREE.Points(starGeometry, starMaterial)
      scene.add(stars)
    }

    function onWindowResize() {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
      labelRenderer.setSize(window.innerWidth, window.innerHeight)
    }


    onMounted(() => {
      if (!container.value.querySelector('canvas')) {
        init()
        animate()
      }
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', onWindowResize)
      container.value.removeEventListener('click', onMouseClick)
      controls.dispose()
    })

    return { container, loading, searchQuery, searchNode }
  }
}
</script>

<style scoped>
.graph-container {
  width: 100vw;
  height: 100vh;
  background: #000000;
}

.overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  color: white;
  z-index: 10;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.overlay h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.overlay p {
  font-size: 0.875rem;
  opacity: 0.7;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 1.25rem;
  text-align: center;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

:global(.node-label) {
  color: white;
  background-color: rgba(0, 0, 0, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  pointer-events: none;
  white-space: nowrap;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 确保层级关系 */
.graph-container canvas {
  position: relative;
  z-index: 1;
}

.label-renderer {
  z-index: 2;
  pointer-events: none !important;
}
</style>