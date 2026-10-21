# Symlink Dereferencing and Subpath Routing Specification

Deploying static web games to GitHub Pages often encounters subtle obstacles that break audio, textures, or page rendering. This document specifies the detection and resolution rules enforced by `atb-game-to-githubpage`.

---

## 1. Cross-Directory Asset Symlinks

### The Problem
In standard game porting architectures (such as `ATBGamePort`), web frontend code lives in a subfolder (e.g. `target/<game>/web/`), while large asset folders (audio, sprite atlases, decompiled assets) live in a sibling directory linked via symlink:
```text
target/<game>/
├── assets/
│   ├── images/
│   ├── sounds/
│   └── data/
└── web/
    ├── index.html
    └── assets -> ../assets   # Symbolic link to sibling directory
```
GitHub Pages default deployments do not resolve symlinks pointing outside the publishing folder. When deployed, the symlink is either omitted or uploaded as a broken text pointer, resulting in 404 errors for all images and audio.

### Resolution Rule
The build step in the deployment workflow must dereference symlinks by removing the symlink in the staging directory and copying the concrete target directory in its place:
```bash
# Dereference web frontend and replace symlink with concrete directory
mkdir -p _site
cp -r kingdomrush/web/* _site/
rm -rf _site/assets
cp -r kingdomrush/assets _site/assets
```

---

## 2. GitHub Pages Repository Subpath Routing

### The Problem
Default GitHub Pages sites are served under a subpath matching the repository name:
```text
https://<owner>.github.io/<repo>/
```
If game code references assets using root-absolute paths:
```html
<!-- INCORRECT: Resolves to https://<owner>.github.io/assets/hero.png (404) -->
<img src="/assets/hero.png">
<script src="/js/engine.js"></script>
```
The browser attempts to load the file from the root domain rather than the repository subpath.

### Resolution Rule
All asset, script, and stylesheet references must use relative paths:
```html
<!-- CORRECT: Resolves to https://<owner>.github.io/<repo>/assets/hero.png -->
<img src="assets/hero.png">
<!-- OR -->
<img src="./assets/hero.png">
```
In JavaScript code:
```javascript
// Relative path resolution
const soundUrl = "assets/sounds/bgm.mp3";
// Or dynamic base resolution
const baseUrl = window.location.pathname.endsWith("/") ? window.location.pathname : window.location.pathname + "/";
```

---

## 3. Jekyll Bypass (`.nojekyll`)

### The Problem
GitHub Pages historically treats repositories as Jekyll projects by default. Jekyll automatically ignores directories or files that start with an underscore (`_`) or dot (`.`). Many game engines (e.g., Unity WebGL `_framework/`, Godot, Phaser packs) use underscore prefixes.

### Resolution Rule
Always generate a `.nojekyll` marker file in the root of the publishing bundle:
```bash
touch _site/.nojekyll
```
This forces GitHub Pages to serve the static artifact directly without Jekyll filtering.
