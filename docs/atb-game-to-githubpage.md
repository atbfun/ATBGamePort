## What it does

`atb-game-to-githubpage` automates deploying HTML5, Canvas, WebGL, Phaser, Pixi, Godot, and Unity WebGL games to **GitHub Pages** using modern zero-pollution GitHub Actions workflows.

Deploying static web games to GitHub Pages commonly fails due to subtle traps:
1. **Asset Symlinks & Subproject Monorepos**: Game frontends often live in subfolders (e.g. `web/`, `dist/`, `target/<game>/web/`), while large asset folders live in sibling directories linked via symlinks (`web/assets -> ../assets`). GitHub Pages ignores external symlinks, breaking images and audio.
2. **Subpath Routing 404s**: Default GitHub Pages deployments run under `https://<owner>.github.io/<repo>/`. Absolute asset paths like `/assets/hero.png` or `/sound/bgm.mp3` fail with 404 errors.
3. **Jekyll Filtering**: Jekyll ignores directories and files prefixed with underscores (`_`) or dots, which silently breaks game engine bundles (such as Unity WebGL `_framework/`).
4. **Git Branch Pollution**: Legacy deployment tools create orphan `gh-pages` branches that bloat the repository history.

`atb-game-to-githubpage` scans the repository, dereferences external symlinks, audits relative asset paths, injects `.nojekyll`, tests staging locally, and outputs a zero-pollution GitHub Actions workflow (`.github/workflows/deploy-pages.yml`) utilizing official Pages deployment actions (`actions/upload-pages-artifact@v3` and `actions/deploy-pages@v4`).

## When to reach for it

- **Invocation mode.** Type `/atb-game-to-githubpage`, or invoke the skill after completing a game port with `atb-game-porting`.
- **Trigger boundary.** Reach for this when ready to publish, share, or showcase an HTML5 game on GitHub Pages without manual server setup.

## Prerequisites

- **Environment**:
  - Python 3 standard library (no pip dependencies required).
  - Git CLI configured for the repository.
- **Input Directory**:
  - Any web game repository or subfolder containing an `index.html` entrypoint and associated assets.

## The 4-Phase Deployment Pipeline

| Phase | Disclosed Reference | Core Deliverable |
| :--- | :--- | :--- |
| **Phase 1: Layout & Asset Discovery** | [`SYMLINKS-AND-SUBPATHS.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-to-githubpage/SYMLINKS-AND-SUBPATHS.md) | Discovers `index.html` and maps external asset symlinks |
| **Phase 2: Subpath Audit & .nojekyll** | [`SYMLINKS-AND-SUBPATHS.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-to-githubpage/SYMLINKS-AND-SUBPATHS.md) | Scans for root-absolute URLs and ensures Jekyll bypass |
| **Phase 3: Workflow Generation** | [`WORKFLOW-AND-PAGES.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-to-githubpage/WORKFLOW-AND-PAGES.md) | Generates `.github/workflows/deploy-pages.yml` with OIDC & Pages permissions |
| **Phase 4: Staging Verification & Push** | [`WORKFLOW-AND-PAGES.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-to-githubpage/WORKFLOW-AND-PAGES.md) | Validates staged `_site` bundle and updates `README.md` with live demo URL |

## CLI Usage

### 1. Dry-Run Staging Simulation
```bash
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target /path/to/game --dry-run
```

### 2. Generate Workflow and Test Staging
```bash
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target /path/to/game
```

### 3. One-Click Commit and Push
```bash
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target /path/to/game --commit --push
```

### 4. Deploy with Custom Domain
```bash
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target /path/to/game --domain "arcade.example.com"
```

## Common questions

**Why does GitHub Pages show 404 for assets when my local preview works fine?**  
GitHub Pages hosts sites under a subpath matching the repository name (`https://user.github.io/repo/`). If asset URLs start with a slash (`/assets/image.png`), the browser looks for `https://user.github.io/assets/image.png`. Using relative paths (`assets/image.png` or `./assets/image.png`) fixes the issue.

**Why does the deployed game fail to load images when symlinks are used?**  
Default GitHub Pages publishing ignores symbolic links that point outside the published folder. `atb-game-to-githubpage` detects symlinks and generates build steps in GitHub Actions that replace the symlink with the real target folder inside `_site`.

**How do I activate GitHub Pages once the workflow is pushed?**  
In your GitHub repository, go to **Settings** -> **Pages**. Under **Build and deployment** -> **Source**, select **GitHub Actions**. Your game will deploy automatically on push.
