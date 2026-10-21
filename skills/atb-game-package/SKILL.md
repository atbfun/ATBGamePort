---
name: atb-game-package
description: Use when packaging HTML5 Canvas games into zero-dependency standalone offline bundles (<game>-standalone.html) with embedded VFS and runtime interceptor shim, or portable directories with OS-native zero-dependency launchers (Play-macOS.command, Play-Windows.bat) and distribution zip archives.
---

# ATB Game Package

Zero-dependency packaging toolchain and discipline for converting Web/HTML5 Canvas games into self-contained offline standalone files and portable distribution bundles, powered by [fun.aitobox.com](https://fun.aitobox.com).

Read [`GLOSSARY.md`](../../GLOSSARY.md) if present in the repository for ubiquitous domain terminology.

## Explicit Prerequisites

Before packaging an HTML5 game port, verify that the required local tools are available:

1. **Environment & Toolchains**:
   - Activate the project Conda environment if present: `conda activate ATBPort`.
   - Python 3 standard library (no third-party pip dependencies required).
   - Google Chrome, Chromium, Microsoft Edge, or Brave Browser installed for headless verification.
2. **Input Compatibility**:
   - Accepts standard `ATBGamePort` target directories (`target/<game>/` containing `web/index.html` and `assets/`).
   - Also accepts custom web game directories containing an `index.html` entrypoint.

## Non-Negotiable Red Lines

1. **Zero External Runtime Dependencies**:
   The packaged game artifacts must run out-of-the-box on end-user machines without requiring players to install Python, Node.js, Web servers, or browser plugins.
2. **Zero CORS & Tainted Canvas Violations on `file:///`**:
   The standalone bundle (`<game>-standalone.html`) must execute offline via direct browser double-clicking without throwing `Cross-Origin Request Blocked`, `SecurityError`, or canvas tainting exceptions.
3. **Preserved Executable Permissions in Archives**:
   Distribution zip archives must preserve Unix `0755` executable permissions on macOS `.command` launcher scripts so users can launch immediately upon extraction.

## Core Execution Workflow

Execute the packaging pipeline in strict phase order:

```
[1. Resolve Game Layout & Assets]
         │
         ▼
[2. Build Standalone HTML & VFS Shim]  ──> Read SINGLE-FILE-VFS.md
         │
         ▼
[3. Build Portable Directory & Launchers] ──> Read PORTABLE-LAUNCHER-AND-VERIFY.md
         │
         ▼
[4. Headless file:/// & Archive Verify] ──> Run scripts/verify-package.py
```

### Step 1: Input Resolution & Target Scaffolding
1. Inspect the input game path to identify `index.html` and associated asset directories (`assets/`, `images/`, `sounds/`, `music/`, `data/`).
2. Dereference all symbolic links (such as `web/assets -> ../assets`) into physical target paths.

### Step 2: Single-File VFS Bundling
Read [`SINGLE-FILE-VFS.md`](SINGLE-FILE-VFS.md).
1. Inline local CSS files and rewrite CSS `url(...)` declarations to Base64 Data URIs.
2. Inline local JavaScript files, safely escaping `</script>` sequences.
3. Inject the `__ATB_VFS__` runtime shim at the top of `<head>` to intercept `fetch`, `XMLHttpRequest`, `Image.src`, and `Audio.src`.
4. Output `<game>-standalone.html` into `dist/`.

### Step 3: Portable Directory & Native OS Launchers
Read [`PORTABLE-LAUNCHER-AND-VERIFY.md`](PORTABLE-LAUNCHER-AND-VERIFY.md).
1. Materialize all assets into `dist/<game>-portable/` without dangling symlinks.
2. Generate `Play-macOS.command` (macOS double-click launcher) and set `0755` permissions.
3. Generate `Play-Windows.bat` (Windows launcher powered by built-in PowerShell `HttpListener`).
4. Generate `README-PLAY.txt` with bilingual quick-start instructions.
5. Create `dist/<game>-release.zip` embedding Unix `0755` zip header permissions.

### Step 4: Automated Verification
Run [`scripts/verify-package.py`](scripts/verify-package.py) to prove zero console errors and $\ge 90\%$ colored pixel ratio across snapshots under pure `file:///` execution, and verify archive permissions.

```bash
python3 skills/atb-game-package/scripts/verify-package.py \
  --html-file target/<game>/dist/<game>-standalone.html \
  --portable-dir target/<game>/dist/<game>-portable \
  --zip-file target/<game>/dist/<game>-release.zip \
  --min-colored-ratio 0.90
```
