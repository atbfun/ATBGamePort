---
name: atb-game-to-githubpage
description: Use when deploying an HTML5, WebGL, Canvas, Phaser, Pixi, or static interactive web game to GitHub Pages, configuring automated GitHub Actions workflows, resolving asset symlinks and subpaths, and generating .nojekyll. Part of the ATB series.
---

# ATB Game to GitHub Pages

Automated toolchain and deployment discipline for publishing Web/HTML5 Canvas games to GitHub Pages with zero-pollution GitHub Actions workflows, powered by [fun.aitobox.com](https://fun.aitobox.com).

Read [`GLOSSARY.md`](../../GLOSSARY.md) if present in the repository for ubiquitous domain terminology.

## Explicit Prerequisites

Before deploying a game to GitHub Pages, verify that the required local tools are available:

1. **Environment & Toolchains**:
   - Activate the project Conda environment if present: `conda activate ATBPort`.
   - Python 3 standard library (no third-party pip dependencies required).
   - Git CLI configured with access to the target remote repository.
2. **Input Compatibility**:
   - Web game directory containing an `index.html` entrypoint (root, `web/`, `dist/`, or `target/<game>/web/`).
   - Sibling or internal asset folders (`assets/`, `images/`, `sounds/`, `data/`).

## Non-Negotiable Red Lines

1. **Zero-Pollution GitHub Actions Deployment**:
   Never create or maintain orphan `gh-pages` git branches. Always publish through GitHub Actions using official Pages actions (`upload-pages-artifact@v3` and `deploy-pages@v4`).
2. **Dereferenced Asset Symlinks**:
   Never leave raw symbolic links pointing outside the publishing bundle. All external symlinks must be dereferenced and replaced with concrete directory trees in the build step.
3. **Subpath-Safe Relative Routing**:
   Never allow root-absolute paths (`/assets/...`, `/style.css`) in static web games. All assets must load relative to the repository subpath (`https://<owner>.github.io/<repo>/`).
4. **Mandatory Jekyll Bypass**:
   Every deployed artifact must include `.nojekyll` in its root to prevent Jekyll from dropping underscore-prefixed game engine bundles.

## Core Execution Workflow

Execute the deployment pipeline in strict phase order:

```
[1. Discover Web Entry & Symlinked Assets]
                  │
                  ▼
[2. Audit Subpath Routing & .nojekyll]       ──> Read SYMLINKS-AND-SUBPATHS.md
                  │
                  ▼
[3. Generate GitHub Actions Workflow]        ──> Read WORKFLOW-AND-PAGES.md
                  │
                  ▼
[4. Staging Verification & Hand-off]         ──> Run scripts/deploy.py
```

### Step 1: Layout & Asset Linkage Discovery
1. Identify the game entrypoint: search for `index.html` at repository root or subfolders (`web/`, `dist/`, `target/<game>/web/`).
2. Inspect asset links: identify any symlinks (e.g., `web/assets -> ../assets`) pointing outside the web root.

### Step 2: Subpath Audit & Dereferencing Rules
Read [`SYMLINKS-AND-SUBPATHS.md`](SYMLINKS-AND-SUBPATHS.md).
1. Audit HTML, CSS, and JS files for root-absolute paths (`/assets/...`). Ensure relative paths (`assets/...` or `./assets/...`) are used.
2. Formulate asset dereferencing commands replacing symlinks with physical directories in `_site`.
3. Ensure `.nojekyll` is generated in `_site`.

### Step 3: Workflow Generation & Configuration
Read [`WORKFLOW-AND-PAGES.md`](WORKFLOW-AND-PAGES.md).
1. Generate `.github/workflows/deploy-pages.yml` with concurrency and required permissions (`pages: write`, `id-token: write`).
2. If a custom domain is specified, generate the root `CNAME` file.
3. Update `README.md` with the live demo link (`https://<owner>.github.io/<repo>/`).

### Step 4: Automated Verification & Execution
Run [`scripts/deploy.py`](scripts/deploy.py) to simulate local staging, verify bundle contents, and apply changes:

```bash
# 1. Dry-run staging verification
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target . --dry-run

# 2. Generate workflow, test staging, and update README
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target .

# 3. Optional: One-click commit and push
python3 skills/atb-game-to-githubpage/scripts/deploy.py --target . --commit --push
```

Verify tests by running [`tests/test_deploy.py`](tests/test_deploy.py). Advise human partner to confirm repository **Settings -> Pages** is set to **GitHub Actions**.
