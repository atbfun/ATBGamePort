## What it does

`atb-game-package` converts Web/HTML5 Canvas games into zero-dependency, self-contained offline standalone files and portable distribution bundles. When games are delivered to players, double-clicking `index.html` on the `file:///` protocol normally crashes due to browser CORS policies blocking `fetch()` and `XMLHttpRequest`, canvas tainting (`SecurityError`), and broken symlinks. `atb-game-package` packages the game into:
1. `<game>-standalone.html`: A single self-contained HTML file embedding a lightweight in-browser Virtual File System (`window.__ATB_VFS__`) and runtime interceptor shim. Double-clicking it in any modern browser on Windows, macOS, Linux, iOS, or Android immediately runs the game with zero dependencies and zero CORS errors.
2. `<game>-portable/`: A standalone directory with dereferenced assets and platform-native double-click launchers: `Play-macOS.command` (macOS) and `Play-Windows.bat` (Windows PowerShell `HttpListener`), requiring zero external installations.
3. `<game>-release.zip`: A distribution archive embedding Unix `0755` executable permissions for macOS launchers.

## When to reach for it

- **Invocation mode.** Type `/atb-game-package`, or invoke the skill after completing a game port with `atb-game-porting`.
- **Trigger boundary.** Reach for this when delivering, distributing, or archiving any HTML5 game created under `target/<game>/` (or custom web game directories) into click-to-play packages without requiring users to launch an HTTP server.

## Prerequisites

- **Environment**:
  - Python 3 standard library (no pip dependencies required).
  - Google Chrome, Chromium, Microsoft Edge, or Brave Browser for automated headless verification.
- **Input Directory**:
  - Standard `ATBGamePort` target directory (`target/<game>/` containing `web/index.html` and `assets/`), or any directory containing an `index.html` entrypoint.

## The 4-Phase Packaging Pipeline

| Phase | Disclosed Reference | Core Deliverable |
| :--- | :--- | :--- |
| **Phase 1: Layout & Asset Discovery** | [`SINGLE-FILE-VFS.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-package/SINGLE-FILE-VFS.md) | Resolves game entrypoint and dereferences all asset files |
| **Phase 2: Standalone HTML & VFS Shim** | [`SINGLE-FILE-VFS.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-package/SINGLE-FILE-VFS.md) | Inlines CSS/JS/images and injects `__ATB_VFS__` runtime interceptors for `fetch`, `XHR`, `Image.src`, and `Audio.src` |
| **Phase 3: Portable Launchers & Zip** | [`PORTABLE-LAUNCHER-AND-VERIFY.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-package/PORTABLE-LAUNCHER-AND-VERIFY.md) | Generates `Play-macOS.command`, `Play-Windows.bat`, and `<game>-release.zip` with preserved `0755` permissions |
| **Phase 4: Headless file:/// Verification** | [`PORTABLE-LAUNCHER-AND-VERIFY.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-package/PORTABLE-LAUNCHER-AND-VERIFY.md) | Runs `verify-package.py` via direct `file:///` protocol (0 CORS errors, colored pixel ratio $\ge 90\%$) |

## CLI Usage

### 1. Packaging a Game
```bash
python3 skills/atb-game-package/scripts/package-game.py \
  --input-dir target/<game> \
  --out-dir target/<game>/dist \
  --mode all
```

Options:
- `--mode all`: Generates standalone HTML, portable folder, and release zip (default).
- `--mode single`: Generates only the `<game>-standalone.html` file.
- `--mode portable`: Generates only the `<game>-portable/` directory.

### 2. Automated Headless file:/// Verification
```bash
python3 skills/atb-game-package/scripts/verify-package.py \
  --html-file target/<game>/dist/<game>-standalone.html \
  --portable-dir target/<game>/dist/<game>-portable \
  --zip-file target/<game>/dist/<game>-release.zip \
  --min-colored-ratio 0.90
```

## Common questions

**How does `<game>-standalone.html` bypass browser CORS restrictions on `file:///`?**  
The packager inlines all binary and text assets into Base64 entries inside a virtual filesystem (`window.__ATB_VFS__`). An in-browser shim intercepts `fetch()` and `XMLHttpRequest`, intercepting relative asset URLs and synthesizing responses directly from memory.

**Why doesn't drawing images onto `<canvas>` throw a Tainted Canvas `SecurityError`?**  
When images are loaded from external files under `file:///`, browsers treat them as cross-origin and taint the canvas context. The `__ATB_VFS__` shim rewrites image `src` assignments into Base64 Data URIs (`data:image/png;base64,...`). Under modern browser security rules, same-origin Data URIs do not taint the canvas, allowing `ctx.getImageData()` to run safely.

**How does `Play-Windows.bat` run without Python or Node.js installed?**  
It uses Windows PowerShell's built-in `.NET System.Net.HttpListener` class, which has been part of standard Windows since Windows 7. It creates a local HTTP server bound to loopback `127.0.0.1` and opens the default browser without any third-party dependencies.

**Why does `Play-macOS.command` need special handling in the release zip?**  
Standard zip tools often strip the Unix `0755` executable permission bit. When users extract the zip, double-clicking `.command` triggers an permission denied error. `package-game.py` explicitly embeds Unix `0755` permission attributes in the zip file header.

## It's working if

- Running `package-game.py` creates `dist/<game>-standalone.html`, `dist/<game>-portable/`, and `dist/<game>-release.zip`.
- Double-clicking `dist/<game>-standalone.html` opens the default browser and runs the game smoothly without console errors.
- Running `verify-package.py` exits `0` with 3 verification snapshots achieving $\ge 90\%$ colored pixel ratio and 0 console errors under direct `file:///` execution.
