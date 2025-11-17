<template>
  <div class="background">
    <NavBar />
    <div class="controls">
      <input type="text" id="searchBar" placeholder="搜索节点..." v-model="searchQuery"/>
      <button @click="highlightNodes">确定</button>
      <button @click="goToDagre">跳转到知识图谱</button>
    </div>
    <div id="mynetwork"></div>
  </div>
</template>

<script>
import { DataSet, Network } from 'vis-network/standalone';
import { throttle } from 'lodash'; // 引入 lodash 的 throttle 函数
import { useRouter } from 'vue-router';
import NavBar from "@/components/NavBar.vue"; // 导入 useRouter

export default {
  name: 'GraphVisualization',
  components: {NavBar},
  setup() {
    const router = useRouter(); // 获取 router 实例
    return { router, searchQuery: '' }; // 添加 searchQuery
  },

  mounted() {
    this.createNetwork();
  },
  methods: {
    createNetwork() {
      const nodes = new DataSet([
       { id: 1, label: '数学分析', url: 'https://example.com/page1' },
        { id: 2, label: '并行计算', url: 'https://example.com/page2' },
        { id: 3, label: '数值计算及其计算机实现', url: 'https://example.com/page3' },
        { id: 4, label: '自然语言处理导论', url: 'https://example.com/page4' },
        { id: 5, label: '操作系统实践(进阶)', url: 'https://example.com/page5' },
        { id: 6, label: '现代CAD技术(A)', url: 'https://example.com/page6' },
        { id: 7, label: '计算机视觉', url: 'https://example.com/page7' },
        { id: 8, label: '游戏项目实践', url: 'https://example.com/page8' },
        { id: 9, label: '数据挖掘', url: 'https://example.com/page9' },
        { id: 10, label: '多智能体系统与实践', url: 'https://example.com/page10' },
        { id: 11, label: '计算机网络工程', url: 'https://example.com/page11' },
        { id: 12, label: '网络安全基础', url: 'https://example.com/page12' },
        { id: 13, label: '存储技术基础', url: 'https://example.com/page13' },
        { id: 14, label: '模式识别与机器学习', url: 'https://example.com/page14' },
        { id: 15, label: '服务器维护及网站建设', url: 'https://example.com/page15' },
        { id: 16, label: '问题求解与程序设计', url: 'https://example.com/page16' },
        { id: 17, label: '计算机图形学', url: 'https://example.com/page17' },
        { id: 18, label: '云计算实践', url: 'https://example.com/page18' },
        { id: 19, label: '创新创业基础与实践', url: 'https://example.com/page19' },
        { id: 20, label: '多媒体技术', url: 'https://example.com/page20' },
        { id: 21, label: '算法分析与设计', url: 'https://example.com/page21' },
        { id: 22, label: '数字图像处理', url: 'https://example.com/page22' },
        { id: 23, label: '人机交互技术', url: 'https://example.com/page23' },
        { id: 24, label: '数学建模', url: 'https://example.com/page24' },
        { id: 25, label: '数据可视化', url: 'https://example.com/page25' },
        { id: 26, label: '最优化方法', url: 'https://example.com/page26' },
        { id: 27, label: '计算机新技术前沿', url: 'https://example.com/page27' },
        { id: 28, label: '信息系统安全概论', url: 'https://example.com/page28' },
        { id: 29, label: '编程思维与实践', url: 'https://example.com/page29' },
        { id: 30, label: '程序设计原理与C语言', url: 'https://example.com/page30' },
        { id: 31, label: '大学物理B(一)：力学，热学', url: 'https://example.com/page31' },
        { id: 32, label: '大学物理B（二）：电磁学、波动与光学部分', url: 'https://example.com/page32' },
        { id: 33, label: '概率论与数理统计', url: 'https://example.com/page33' },
        { id: 34, label: '计算机导论', url: 'https://example.com/page34' },
        { id: 35, label: '离散数学', url: 'https://example.com/page35' },
        { id: 36, label: '人工智能', url: 'https://example.com/page36' },
        { id: 37, label: '数据结构', url: 'https://example.com/page37' },
        { id: 38, label: '数字逻辑电路', url: 'https://example.com/page38' },
        { id: 39, label: '线性代数', url: 'https://example.com/page39' },
        { id: 40, label: '操作系统', url: 'https://example.com/page40' },
        { id: 41, label: '计算机网络', url: 'https://example.com/page41' },
        { id: 42, label: '嵌入式系统原理与实践', url: 'https://example.com/page42' },
        { id: 43, label: '计算机系统结构', url: 'https://example.com/page43' },
        { id: 44, label: '数据库系统原理与实践', url: 'https://example.com/page44' },
        { id: 45, label: '编译原理与实践', url: 'https://example.com/page45' },
        { id: 46, label: '信息工程伦理', url: 'https://example.com/page46' },
        { id: 47, label: '线性代数进阶', url: 'https://example.com/page47' },
        { id: 48, label: '计算机基础实践', url: 'https://example.com/page48' },
        { id: 49, label: '面向对象程序设计（基于Java）', url: 'https://example.com/page49' },
        { id: 50, label: '面向对象程序设计（基于C++）', url: 'https://example.com/page50' },
        { id: 51, label: '专业英语', url: 'https://example.com/page51' },
        { id: 52, label: '信号与系统', url: 'https://example.com/page52' },
        { id: 53, label: '计算机组成与实践', url: 'https://example.com/page53' },
        { id: 54, label: '生物信息学', url: 'https://example.com/page54' },
        { id: 55, label: '大数据系统', url: 'https://example.com/page55' },
        { id: 56, label: '智能推荐系统', url: 'https://example.com/page56' },
        { id: 57, label: '视觉感知与前沿技术', url: 'https://example.com/page57' },
        { id: 58, label: '统计学习算法导论', url: 'https://example.com/page58' },
        { id: 59, label: '现代CAD技术（B）', url: 'https://example.com/page59' },
        { id: 60, label: '可信机器学习', url: 'https://example.com/page60' },
        { id: 61, label: '计算机动画', url: 'https://example.com/page61' },
        { id: 62, label: '深度学习基础与导论', url: 'https://example.com/page62' },
        { id: 63, label: '强化学习基础', url: 'https://example.com/page63' },
        { id: 64, label: 'AIoT系统设计与实践', url: 'https://example.com/page64' },
        { id: 65, label: '写作与表达', url: 'https://example.com/page65' },
        { id: 66, label: 'python程序设计', url: 'https://example.com/page66' },
        { id: 99, label: '学科基础课', url: 'https://example.com/page99' },
        { id: 100, label: '专业必修课', url: 'https://example.com/page100' },
        { id: 101, label: '专业任意选修课', url: 'https://example.com/page101' }
      ]);

      const edges = new DataSet([

        { from:99, to:1, arrows: 'to' },
        { from:99, to:30, arrows: 'to' },
        { from:99, to:34, arrows: 'to' },
        { from:99, to:31, arrows: 'to' },
        { from:99, to:32, arrows: 'to' },
        { from:99, to:37, arrows: 'to' },
        { from:99, to:38, arrows: 'to' },
        { from:99, to:39, arrows: 'to' },
        { from:99, to:35, arrows: 'to' },
        // { from:22, to:64, arrows: 'to' },
        // { from:22, to:64, arrows: 'to' },
        // { from:22, to:64, arrows: 'to' },
        // { from:22, to:64, arrows: 'to' },
        { from:100, to:29, arrows: 'to' },
        { from:100, to:33, arrows: 'to' },
        { from:100, to:36, arrows: 'to' },
        { from:100, to:53, arrows: 'to' },
        { from:100, to:40, arrows: 'to' },
        { from:100, to:41, arrows: 'to' },
        { from:100, to:42, arrows: 'to' },
        { from:100, to:43, arrows: 'to' },
        { from:100, to:44, arrows: 'to' },
        { from:100, to:45, arrows: 'to' },
        { from:100, to:46, arrows: 'to' },
        { from:101, to:47, arrows: 'to' },
        { from:101, to:48, arrows: 'to' },
        { from:101, to:49, arrows: 'to' },
        { from:101, to:50, arrows: 'to' },
        { from:101, to:51, arrows: 'to' },
        { from:101, to:52, arrows: 'to' },
        { from:101, to:16, arrows: 'to' },
        { from:101, to:17, arrows: 'to' },
        { from:101, to:18, arrows: 'to' },
        { from:101, to:19, arrows: 'to' },
        { from:101, to:20, arrows: 'to' },
        { from:101, to:21, arrows: 'to' },
        { from:101, to:22, arrows: 'to' },
        { from:101, to:23, arrows: 'to' },
        { from:101, to:24, arrows: 'to' },
        { from:101, to:25, arrows: 'to' },
        { from:101, to:26, arrows: 'to' },
        { from:101, to:27, arrows: 'to' },
        { from:101, to:28, arrows: 'to' },
        { from:101, to:54, arrows: 'to' },
        { from:101, to:2, arrows: 'to' },
        { from:101, to:3, arrows: 'to' },
        { from:101, to:4, arrows: 'to' },
        { from:101, to:5, arrows: 'to' },
        { from:101, to:6, arrows: 'to' },
        { from:101, to:7, arrows: 'to' },
        { from:101, to:8, arrows: 'to' },
        { from:101, to:9, arrows: 'to' },
        { from:101, to:10, arrows: 'to' },
        { from:101, to:11, arrows: 'to' },
        { from:101, to:12, arrows: 'to' },
        { from:101, to:13, arrows: 'to' },
        { from:101, to:14, arrows: 'to' },
        { from:101, to:15, arrows: 'to' },
        { from:101, to:55, arrows: 'to' },
        { from:101, to:56, arrows: 'to' },
        { from:101, to:57, arrows: 'to' },
        { from:101, to:58, arrows: 'to' },
        { from:101, to:59, arrows: 'to' },
        { from:101, to:60, arrows: 'to' },
        { from:101, to:61, arrows: 'to' },
        { from:101, to:62, arrows: 'to' },
        { from:101, to:63, arrows: 'to' },
        { from:101, to:64, arrows: 'to' },

        { from:101, to:65, arrows: 'to' },
        { from:101, to:66, arrows: 'to' }
        // { from:101, to:35, arrows: 'to' },


      ]);

      this.networkContainer = document.getElementById('mynetwork');
      const data = { nodes, edges };
      const options = {
         physics: {
          enabled: true,
          solver: 'barnesHut',
          forceAtlas2Based: {
            gravitationalConstant: -10000,
            centralGravity: 0.1,
            springLength: 250,
            springConstant: 0.05,
            avoidOverlap: 2, // 节点间距调整，增大此值可减少节点之间的重叠
          },
          barnesHut: {
            gravitationalConstant: -10000,
            springLength: 250,
            springConstant: 0.005,
          },
          repulsion: {
            centralGravity: 0.1,
            springLength: 250,
            springConstant: 0.02,
            nodeDistance: 1000,
          },
        },
        nodes: {
          shape: 'ellipse',
          size: 200,
          font: {
            size: 14,
            color: '#000',
            face: 'Arial',
            strokeWidth: 2,
            strokeColor: '#fff',
          },
          color: {
            background: '#97C2FC',
            border: '#2B7CE9',
          },
        },
        edges: {
          color: {
            color: '#848484',
            highlight: '#848484',
            hover: '#848484',
          },
          smooth: {
            type: 'continuous',
            roundness: 0.2,
          },
          arrows: {
            to: { enabled: true, scaleFactor: 1 },
          },
        },
        layout: {
          hierarchical: {
            enabled: false,
          },
        },
      };

      this.network = new Network(this.networkContainer, data, options);

      this.network.on('click', (params) => {
        if (params.nodes.length > 0) {
          const selectedNodeId = params.nodes[0];
          const selectedNode = nodes.get(selectedNodeId);
          // 如果选中的节点有url字段，可以直接跳转
          if (selectedNode.url) {
            this.$router.push({ name: 'course' }); // 假设你的 route 名称是 'courseoutline'
          }
        }
      });


      this.nodes = nodes; // 保存 nodes 以便后续访问
      // 网络节点和边的定义省略...
    },
    highlightNodes: throttle(function() { // 使用节流函数
      const query = this.searchQuery.toLowerCase(); // 使用绑定的 searchQuery
      if (!query) return; // 如果输入框为空，直接返回

      this.network.body.data.nodes.update(this.nodes.map((node) => {
        return { id: node.id, color: { background: '#97C2FC' } };
      }));

      this.nodes.forEach((node) => {
        if (node.label.toLowerCase().includes(query)) {
          this.network.body.data.nodes.update({ id: node.id, color: { background: 'orange' } });
          this.network.focus(node.id, {
            scale: 1.5,
            animation: {
              duration: 500,
              easingFunction: 'easeInOutQuad',
            },
          });
        }
      });
    }),
    goToDagre() {
      this.router.push({ name: 'mydagre' }); // 确保你的路由配置中有 myDagre
    },
  },
};
</script>

<style scoped>
.background {
  background-image: url('@/assets/pics/xingxi.png'); /* 替换为你的星空图片路径 */
  background-size: cover;
  background-repeat: no-repeat;
  width: 1680px;
  height: 100%;
}

.controls {
  margin-top: 95px; /* 向下移动输入框和按钮，防止被 NavBar 遮挡 */
  padding-left: 20px; /* 添加一些左右间距 */
}

#mynetwork {
  width: 1500px;
  height: 1000px;
  border: 1px solid lightgray;
}

button {
  margin-left: 10px;
}
</style>
