# 贡献指南

感谢您对 SmartPath 项目的关注！

## 项目结构

```
SmartPath/
├── backend/        # FastAPI 后端
├── frontend/       # Vue 3 前端
├── scripts/        # 管理脚本
├── docs/           # 项目文档
└── README.md       # 主文档
```

## 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 代码规范

### Python (Backend)

- 使用 PEP 8 规范
- 添加类型注解
- 编写文档字符串
- 运行测试: `pytest`

### JavaScript (Frontend)

- 使用 ESLint 规范
- Vue 3 Composition API
- 组件化设计

## 提交消息格式

```
类型(范围): 简短描述

详细描述（可选）

相关Issue（可选）
```

类型:
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 本地开发

查看 [安装指南](docs/installation.md)

## 问题反馈

请使用 GitHub Issues 报告问题。
