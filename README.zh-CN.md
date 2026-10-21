# ATBGamePort — 工业级小游戏逆向与 HTML5 移植技能库

[![skills.sh](https://img.shields.io/badge/skills.sh-VoswC8My6zgey2MK-0ea5e9)](https://www.skills.sh/p/VoswC8My6zgey2MK)
[![Powered by fun.aitobox.com](https://img.shields.io/badge/Powered_by-fun.aitobox.com-0ea5e9)](https://fun.aitobox.com)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./LICENSE)

[English](./README.md) | **简体中文**

面向真实工程的 AI 游戏逆向与 HTML5 移植技能库，由 [fun.aitobox.com](https://fun.aitobox.com) 驱动。专为将经典桌面小游戏（PopCap SexyAppFramework、Windows PE C++ 可执行程序、Flash 游戏及经典独立小游戏）端到端静态逆向、资产重构并移植为**零外部框架依赖、60 FPS 即点即玩的现代 HTML5 Canvas / Web Audio 游戏**而设计。

直接让 AI “仿照某某游戏写一个网页版”通常只能得到物理手感失真、贴图黑边、频繁黑屏报错的玩具代码。`ATBGamePort` 将数十年游戏逆向与前端工程经验浓缩为 **7 阶段渐进式披露（Progressive Disclosure）流水线**：二进制权威逆向 $\rightarrow$ 32位透明贴图合成与追踪音乐转码 $\rightarrow$ 6国语言 i18n $\rightarrow$ 跨设备 JSON 存档同步 $\rightarrow$ 桌面/移动端双端自适应 $\rightarrow$ Headless Chrome 像素级实证验收。

---

## 快速安装（30 秒上手）

通过插件（Plugin）安装可享受版本发布后的自动更新；通过 [skills.sh](https://www.skills.sh/p/VoswC8My6zgey2MK) 安装则会将可编辑的技能文件复制到你的项目中。每个 Agent 请二选一，避免重复加载。

### 1. 安装前置依赖（Prerequisites）

`atb-game-porting` 依赖 **Python 3**（用于私有二进制格式解析、RGB+Alpha 贴图合成及运行 `verify-headless.py` 自动化像素验收），并在 Phase 1（二进制逆向）与 Phase 7（架构自检）中协同调用两个配套技能：

```bash
# 1. 确保已安装 Python 3（推荐 Python 3.10+）
python3 --version

# 2. 安装 grill-with-docs（来自 mattpocock/skills），用于 Phase 7 自动化深度自检
npx skills@latest add mattpocock/skills --skill=grill-with-docs

# 3. 确保你的 Agent 环境已启用 reverse-engineer-anything (REA) 技能与 MCP 服务
```

### 2. 安装 `atb-game-porting`

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add atbfun/ATBGamePort
claude plugin install atb-game-porting@atbfun
```

默认开启自动更新。

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add atbfun/ATBGamePort
codex plugin add atb-game-porting@atbfun
```

每次启动时自动检查并更新。

</details>

<details>
<summary><strong>GitHub Copilot</strong> (CLI 与 VS Code)</summary>

```bash
copilot plugin marketplace add atbfun/ATBGamePort
copilot plugin install atb-game-porting@atbfun
```

随后在 `~/.copilot/settings.json` 中添加一次配置以开启自动更新：

```json
{
  "extraKnownMarketplaces": {
    "atbfun": { "source": { "source": "github", "repo": "atbfun/ATBGamePort" }, "autoUpdate": true }
  }
}
```

在 VS Code 中，也可直接运行 **Chat: Install Plugin From Source** 并输入 `https://github.com/atbfun/ATBGamePort`（每日自动更新）。

</details>

<details>
<summary><strong>Gemini CLI</strong>（手动更新）</summary>

```bash
gemini skills install https://github.com/atbfun/ATBGamePort.git --path skills
```

重新运行上述命令即可更新。

</details>

<details>
<summary><strong>其他 Agent 或可编辑文件安装</strong>（Cursor / Windsurf / OpenCode / Antigravity 等）</summary>

```bash
npx skills@latest add https://skills.sh/p/VoswC8My6zgey2MK -a <agent>  # cursor, windsurf, opencode, devin, amp, pi；省略 -a 可交互选择
```

更新时运行 `npx skills@latest update`。

</details>

<details>
<summary><strong>本地维护者软链安装</strong>（`git pull` 即时生效）</summary>

```bash
git clone https://github.com/atbfun/ATBGamePort.git
cd ATBGamePort
./scripts/link-skills.sh
```

自动将 `skills/atb-game-porting` 软链至 `~/.claude/skills` 与 `~/.agents/skills`。

</details>

---

## 端到端实战指引：从原始游戏到在线发布游玩（Example Walkthrough）

以经典小游戏 `gameA` 为例，完整的工作流只需以下几步：

### 1. 存放原始游戏到 `source/gameA`
将原始经典桌面游戏程序（`.exe`、`.dll`）、素材（图片、音效）及关卡配置放入：
```text
source/gameA/
├── game.exe
├── images/
├── sounds/
└── levels/
```

### 2. 使用 `atb-game-porting` 生成移植版本
对你的 AI 助手说：
> 使用 `atb-game-porting` 将 `source/gameA` 移植为 HTML5 游戏。

该技能（[`atb-game-porting`](./skills/atb-game-porting/SKILL.md)）将全自动执行二进制逆向分析、RGB+Alpha 透明素材合成、6 国语言国际化、跨端存档与零黑屏防御 Canvas 渲染，最终在 `target/gameA/` 生成完整且经过自动化无头像素验证的网页游戏：
```text
target/gameA/
├── analysis/reverse_engineering_report.md
├── assets/
├── src/
├── web/
│   ├── index.html
│   └── assets -> ../assets (软链接)
└── README.md
```

### 3. 新建 GitHub 仓库 `gameA` 并放入根目录
在 GitHub 上新建仓库（例如 `https://github.com/<your-username>/gameA`），并将 `target/gameA/` 中的移植内容放置于该仓库根目录并提交：
```bash
cd target/gameA
git init
git remote add origin https://github.com/<your-username>/gameA.git
git add .
git commit -m "feat: initial game port"
git push -u origin main
```

### 4. 开启 GitHub 仓库的 Pages 功能
打开 GitHub 仓库页面：
- 进入 **Settings** -> **Pages**
- 在 **Build and deployment** -> **Source** 下拉框中，选择 **GitHub Actions**（而非从分支部署）

### 5. 使用 `atb-game-to-githubpage` 一键部署
对 AI 助手说：
> 使用 `atb-game-to-githubpage` 把当前游戏部署到 GitHub Pages。

或在游戏仓库根目录下直接运行部署脚本（[`atb-game-to-githubpage`](./skills/atb-game-to-githubpage/SKILL.md)）：
```bash
python3 /path/to/ATBGamePort/skills/atb-game-to-githubpage/scripts/deploy.py --target . --commit --push
```
该技能会自动穿透并实体化跨目录素材软链接、检查二级子路径（`/gameA/`）相对引用、注入 `.nojekyll` 并推送 `.github/workflows/deploy-pages.yml` 工作流。

### 6. 访问 GitHub Pages URL 在线游玩
等待 GitHub Actions 流水线执行完毕（约 30 秒）后，即可在浏览器直接游玩：
```text
https://<your-username>.github.io/gameA/
```
享受零延迟 Web Audio 音效、自适应触控/鼠标交互及跨设备存档持久化！

### 7. 可选：使用 `atb-game-package` 生成离线单文件/便携包
如果你希望把游戏分发给没有服务器环境的玩家双击即玩，可以直接打包（[`atb-game-package`](./skills/atb-game-package/SKILL.md)）：
> 使用 `atb-game-package` 打包 `target/gameA`。

```bash
python3 /path/to/ATBGamePort/skills/atb-game-package/scripts/package-game.py --input-dir target/gameA --out-dir target/gameA/dist
```
生成内嵌 VFS 消除所有 CORS/Canvas 污染的 `gameA-standalone.html`（双击即可在任何浏览器游玩），以及带有原生双击启动器（macOS `.command`、Windows `.bat`）的 `gameA-portable/` 便携分发包。

---

## 为什么需要这个技能？（Why This Skill Exists）

我们构建 `atb-game-porting` 是为了彻底根治 AI 移植小游戏时最常见的 **4 大工程翻车模式**。

### #1：盲猜游戏逻辑，而不是逆向原始二进制

**痛点**：面对一个传统桌面游戏目录，普通 Agent 往往无视 `.exe` 可执行文件和私有格式数据，凭空捏造轨道曲线、碰撞半径与关卡节奏，做出来的网页版手感与原版天差地别。

**解法**：[`Phase 1: 二进制逆向规范`](./skills/atb-game-porting/REVERSE-ENGINEERING.md) 强制要求优先调用 `reverse-engineer-anything` (REA) 并结合 `/Applications/Hopper Disassembler.app` 与系统级命令（`objdump`、`otool`、`strings`、`hexdump`）。Agent 必须先脱壳（如 UPX）、扫描 `.rdata` 虚表与 MSVC RTTI 符号恢复类继承树、反编译私有曲线/关卡格式解析器，并输出 `target/<game>/analysis/reverse_engineering_report.md`，用二进制实证指导后续开发。

### #2：令人抓狂的 HTML5 Canvas 黑屏死锁

**痛点**：Web 移植版首次打开经常黑屏：404 或未解码完成的图片（`img.complete === true` 但 `naturalWidth === 0`）直接传入 `ctx.drawImage` 会抛出未捕获的 `DOMException` 瞬间杀死 `requestAnimationFrame` 主循环；或者因大体积关卡脚本导致 `DOMContentLoaded` 漏触发。

**解法**：[`Phase 4: 零黑屏 5 大防御铁律`](./skills/atb-game-porting/CANVAS-AND-UI.md) 强制封装 `isImgValid(img)` 并为所有图层提供纯 Canvas 几何矢量兜底绘制；建立 `web/assets -> ../assets` 双向路径回退软链；采用 `document.readyState` 双重挂载守卫；要求首帧即在半透明开始蒙层下渲染鲜活的 Level 1 实景画面；并在交付前通过 [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py) 强制验证彩色像素占比 $\ge 90\%$。

### #3：只有单语言、无存档、手机端无法操作的“半成品”

**痛点**：许多移植产物只有硬编码英文、刷新网页即丢失进度、在手机竖屏或刘海屏上严重裁切变形，且在本地双击 `file:///` 打开时因 CORS 报错彻底静音。

**解法**：
- **[`Phase 2: 资产重构与 6 国语言 i18n`](./skills/atb-game-porting/ASSETS-AND-I18N.md)**：批量将分离的 RGB 与 Alpha 遮罩合成为 32 位透明 PNG，将 `MO3`/`MOD`/`MIDI` 追踪音乐转码为 `MP3`/`OGG`，并 1:1 同步原版多语言或自动构建 **6 国标准语言字典（`en`、`zh-CN`、`ja`、`fr`、`de`、`es`）**，支持设置面板实时热切换。
- **[`Phase 3: StorageManager 与跨端存档/触控归一化`](./skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md)**：采用带 `atb_<game>_*` 命名空间隔离与 `try...catch` 内存兜底的 `StorageManager`，支持一键 **JSON 存档导出与导入（Cross-Device Save Sync）**；统一归一化 Pointer/Touch 坐标，提供 $\ge 44 \times 44\text{px}$ 虚拟按键与 `100dvh` 安全区适配。
- **[`Phase 5: 双模音频矩阵`](./skills/atb-game-porting/AUDIO-AND-VERIFICATION.md)**：HTTP 下采用 Web Audio API 零延迟混音与连击变调，离线 `file:///` 下自动降级为 HTML5 Audio 克隆与 Web Audio 合成器音效。

### #4：看到长文档就敷衍跳步（Premature Completion）

**痛点**：当把几百行指令塞进单个 `SKILL.md` 时，Agent 看到后面还有好几个阶段就会草率略过当前阶段，甚至不打开浏览器验证就宣称“移植完成”。

**解法**：遵循 `writing-for-agents` 的**渐进式披露（Progressive Disclosure）**原则，将 [`SKILL.md`](./skills/atb-game-porting/SKILL.md) 精简为 ~100 行的阶段路由主干，按阶段动态加载专项规范文件；以 [`source/<game>/MIGRATE.md`](./skills/atb-game-porting/MIGRATE-TEMPLATE.md) 作为唯一状态机；强制执行 [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py)（0 Console 报错 + 3 张实机截图彩色像素率 $\ge 90\%$）以及 Phase 7 的 `grill-with-docs` 自动化自检迭代循环。

---

## 技能索引（Reference）

### Model-invoked（模型按需调用 / 用户显式调用）

- **[atb-game-porting](./skills/atb-game-porting/SKILL.md)**（[详细说明文档](./docs/atb-game-porting.md)）：经典桌面小游戏端到端静态逆向、资产与 6 国语言 i18n 重构、跨端存档持久化、桌面/移动双端自适应与零黑屏 HTML5 Canvas 移植核心技能。
  - [`MIGRATE-TEMPLATE.md`](./skills/atb-game-porting/MIGRATE-TEMPLATE.md)：标准 7 阶段 `source/<game>/MIGRATE.md` 状态机模板。
  - [`REVERSE-ENGINEERING.md`](./skills/atb-game-porting/REVERSE-ENGINEERING.md)：Phase 1 REA、Hopper Disassembler 与原生命令行协同二进制逆向规范。
  - [`ASSETS-AND-I18N.md`](./skills/atb-game-porting/ASSETS-AND-I18N.md)：Phase 2 32 位透明 PNG 合成、追踪音乐转码与 6 国语言 i18n 规范。
  - [`GAMEPLAY-AND-STORAGE.md`](./skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md)：Phase 3 核心物理状态机、`StorageManager`、跨端 JSON 存档导入导出与触控归一化规范。
  - [`CANVAS-AND-UI.md`](./skills/atb-game-porting/CANVAS-AND-UI.md)：Phase 4 零黑屏 5 大防御铁律、`100dvh` 响应式安全区适配与 `fun.aitobox.com` 互动彩蛋规范。
  - [`AUDIO-AND-VERIFICATION.md`](./skills/atb-game-porting/AUDIO-AND-VERIFICATION.md)：Phase 5 双模音频矩阵、Phase 6 Headless Chrome 像素级验收与 Phase 7 `grill-with-docs` 自检循环。
  - [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py)：自动化 Headless 浏览器零报错与 $\ge 90\%$ 彩色像素占比校验脚本。

- **[atb-game-package](./skills/atb-game-package/SKILL.md)**（[详细说明文档](./docs/atb-game-package.md)）：零依赖 HTML5 游戏离线打包技能，生成内嵌 VFS 与运行时拦截层的单文件 `.html` 即点即玩包、带 macOS/Windows 原生双击启动器的便携目录及发行 `.zip`。
  - [`SINGLE-FILE-VFS.md`](./skills/atb-game-package/SINGLE-FILE-VFS.md)：浏览器内存 VFS 拦截层、动态资源内联与 CORS/Canvas 污染消除规范。
  - [`PORTABLE-LAUNCHER-AND-VERIFY.md`](./skills/atb-game-package/PORTABLE-LAUNCHER-AND-VERIFY.md)：macOS `.command` 与 Windows 原生 PowerShell `.bat` 双击启动器、Zip `0755` 权限及纯 `file:///` 无头验证规范。
  - [`scripts/package-game.py`](./skills/atb-game-package/scripts/package-game.py)：纯 Python 3 标准库双模打包与启动器生成引擎。
  - [`scripts/verify-package.py`](./skills/atb-game-package/scripts/verify-package.py)：基于纯 `file:///` 协议的无头 Chrome 自动化零报错与 $\ge 90\%$ 着色率验证脚本。

- **[atb-game-to-githubpage](./skills/atb-game-to-githubpage/SKILL.md)**（[详细说明文档](./docs/atb-game-to-githubpage.md)）：零污染 GitHub Pages 一键自动化部署技能，自动穿透资产跨目录软链接、诊断仓库二级子路径、注入 `.nojekyll` 并生成官方 GitHub Actions 工作流。
  - [`SYMLINKS-AND-SUBPATHS.md`](./skills/atb-game-to-githubpage/SYMLINKS-AND-SUBPATHS.md)：跨目录资产软链接穿透实体化、二级子路径相对路由与 `.nojekyll` Jekyll 过滤消除规范。
  - [`WORKFLOW-AND-PAGES.md`](./skills/atb-game-to-githubpage/WORKFLOW-AND-PAGES.md)：官方 GitHub Pages 工作流架构、OIDC 权限配置、自定义域名 CNAME 支持与仓库 Settings 开启指引。
  - [`scripts/deploy.py`](./skills/atb-game-to-githubpage/scripts/deploy.py)：纯 Python 3 标准库一键部署扫描、本地暂存沙盒验证与工作流生成引擎。

---

## 仓库治理规范

- [`GLOSSARY.md`](./GLOSSARY.md)：统一领域词汇表（Ubiquitous Language）。
- [`CLAUDE.md`](./CLAUDE.md)：维护者工程规范与渐进式披露约束。
- [`SCOPE.md`](./SCOPE.md)：Issue 与 PR 准入标准（要求提供真实移植会话证据）。
- [`CHANGELOG.md`](./CHANGELOG.md)：基于 Changesets 自动维护的版本发布历史。
