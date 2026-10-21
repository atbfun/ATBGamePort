# ATB Game to GitHub Pages

一键将各类 HTML5、Canvas、WebGL、Phaser、Pixi、Unity WebGL 等网页游戏项目自动部署到 GitHub Pages 的自动化技能。

## 特色能力

- 🚀 **一键自动化**：自动检测游戏入口 `index.html`、资产结构与软链接，生成 GitHub Actions 工作流。
- 🔗 **跨目录软链接穿透**：解决网页前端在子目录、素材存放在同级或上级目录并在 Pages 静态托管中失效的问题。
- 🌐 **路径诊断与子路径兼容**：自动检查根绝对路径（如 `/assets/...`），保障在 `https://<owner>.github.io/<repo>/` 二级路径下正常运行。
- 🛡️ **防 Jekyll 过滤**：自动注入 `.nojekyll`，防止游戏引擎的特殊文件或下划线前缀文件被过滤。
- 🧪 **本地离线暂存验证**：在生成 CI 配置前先行模拟打包与结构完整性校验。

## 快速使用

```bash
# 演练检查（不写入文件）
python3 scripts/deploy.py --target /path/to/game --dry-run

# 一键生成部署流水线并更新 README
python3 scripts/deploy.py --target /path/to/game

# 一键生成、提交并推送到 GitHub
python3 scripts/deploy.py --target /path/to/game --commit --push
```

## 目录结构

```text
atb-game-to-githubpage/
├── SKILL.md                          # 技能规范与 Agent 交互操作指南
├── README.md                         # 技能介绍与使用说明
├── scripts/
│   └── deploy.py                     # 一键扫描、打包测试与生成部署脚本的 CLI
├── templates/
│   └── deploy-pages.yml.template     # GitHub Actions 工作流模板
└── tests/
    └── test_deploy.py                # 单元测试套件
```
