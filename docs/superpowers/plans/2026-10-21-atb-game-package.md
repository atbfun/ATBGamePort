# `atb-game-package` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `atb-game-package` skill and zero-dependency packaging toolchain that bundles any HTML5 game into a self-contained offline `<game>-standalone.html` (with embedded VFS interceptor) and a `<game>-portable/` directory with native macOS/Windows double-click launchers and a release zip.

**Architecture:** Pure Python 3 standard library bundler (`scripts/package-game.py`) scans game directories, resolves and dereferences symlinked assets, encodes binaries to Base64, and injects a lightweight VFS runtime shim into `<head>` intercepting `fetch`, `XHR`, `Image.src`, and `Audio.src` for 100% CORS-free offline play under `file:///`. Generates native Windows (`.bat` via PowerShell `HttpListener`) and macOS (`.command`) launchers and validates offline execution with Headless Chrome via `scripts/verify-package.py`.

**Tech Stack:** Python 3 (standard library: `base64`, `mimetypes`, `zipfile`, `html.parser`, `shutil`, `urllib`), JavaScript (ES6 In-Browser VFS Shim), Windows PowerShell (`System.Net.HttpListener`), POSIX Bash, Node.js validation harness (`scripts/validate-skills.mjs`).

**Spec:** [`docs/superpowers/specs/2026-10-21-atb-game-package-design.md`](docs/superpowers/specs/2026-10-21-atb-game-package-design.md)

## Global Constraints

- Zero external pip or npm dependencies for packaging and verification scripts (`package-game.py` and `verify-package.py` must use pure Python 3 stdlib).
- Code generation safety: never generate or edit more than 1,000 lines in a single file tool call.
- Follow ATBGamePort Progressive Disclosure: `skills/atb-game-package/SKILL.md` must stay around 100–120 lines; detailed phase specs belong in sibling files (`SINGLE-FILE-VFS.md`, `PORTABLE-LAUNCHER-AND-VERIFY.md`).
- Every skill must carry `agents/openai.yaml` with `display_name` and `short_description`.
- All repository validations in `npm run check` must pass with zero errors.

## Review Focus

1. Asset URL with query strings or hashes (e.g. `assets/sprites.png?v=1.2#crop`) does not break VFS matching.
2. Canvas drawing of inlined images via `ctx.drawImage()` does not taint canvas on `file:///` and `getImageData` succeeds without `SecurityError`.
3. Relative asset path lookups with leading `./` or `../` (e.g. `../assets/sounds/click.mp3`) cleanly resolve to canonical `assets/sounds/click.mp3`.
4. macOS `.command` file in `<game>-release.zip` preserves Unix `0755` executable permissions across unzipping.
5. `verify-package.py` runs headless Chrome on `file:///` without an active HTTP server and verifies colored pixel ratio $\ge 90\%$ and 0 console errors.

---

### Task 1: Core Packaging Engine & In-Memory VFS Interceptor (`scripts/package-game.py`)

**Files:**
- Create: `skills/atb-game-package/scripts/package-game.py`
- Create: `tests/test_package_game.py`

**Interfaces:**
- Produces: CLI script `skills/atb-game-package/scripts/package-game.py` accepting `--input-dir`, `--out-dir`, `--game-name`, `--mode (all|single|portable)`
- Produces: Functions `resolve_game_layout(input_dir: Path) -> GameLayout`, `build_standalone_html(...) -> Path`, `build_portable_bundle(...) -> Path`, `build_release_zip(...) -> Path`

- [ ] **Step 1: Write the unit test for packaging engine**
Create `tests/test_package_game.py` creating a temporary mock game directory with:
- `index.html` referencing `<link rel="stylesheet" href="style.css">`, `<script src="game.js"></script>`, `<img src="assets/images/logo.png">`, `fetch("assets/data/level.json")`, `new Audio("assets/sounds/ping.mp3")`
- `style.css` referencing `url('assets/images/bg.png')`
- `assets/` directory with test PNG, MP3, and JSON files, plus a `web/assets -> ../assets` symlink structure.
Test asserts:
- `resolve_game_layout()` identifies entrypoint and assets directory.
- `package-game.py --mode all` produces `<game>-standalone.html`, `<game>-portable/`, and `<game>-release.zip`.
- Standalone HTML contains `__ATB_VFS__` with all assets, VFS interceptor shim, and inlined CSS/JS.
- Zip file contains `Play-macOS.command` with Unix executable permission (`0o100755`).

- [ ] **Step 2: Run test to verify it fails**
Run: `python3 -m unittest tests/test_package_game.py`
Expected: FAIL (No module or file found).

- [ ] **Step 3: Implement `skills/atb-game-package/scripts/package-game.py`**
Implement the packaging engine in pure Python 3 standard library:
1. `resolve_game_layout(input_path: Path) -> GameLayout` (handles `target/<game>`, `target/<game>/web`, or custom directories).
2. `gather_vfs_assets(layout: GameLayout) -> Dict[str, dict]` (reads all assets, dereferences symlinks, converts to Base64, detects accurate MIME types).
3. `build_vfs_shim_js(vfs_data: dict) -> str` (compact JavaScript shim intercepting `fetch`, `XHR`, `Image.src`, `Audio.src`, `setAttribute`).
4. `build_standalone_html(layout: GameLayout, vfs: dict, out_file: Path) -> Path` (inlines CSS/JS/images, injects shim).
5. `build_portable_bundle(layout: GameLayout, out_dir: Path) -> Path` (copies materialized assets, writes `Play-macOS.command`, `Play-Windows.bat`, `README-PLAY.txt`).
6. `build_release_zip(standalone_html: Path, portable_dir: Path, out_zip: Path) -> Path` (archives bundle with `0755` permission bits on `.command`).
7. `main()` CLI entrypoint with argument parsing.

- [ ] **Step 4: Run test to verify it passes**
Run: `python3 -m unittest tests/test_package_game.py`
Expected: PASS (all tests pass).

- [ ] **Step 5: Commit**
```bash
git add skills/atb-game-package/scripts/package-game.py tests/test_package_game.py
git commit -m "feat(package): implement zero-dependency packaging engine and VFS runtime shim"
```

---

### Task 2: Automated Headless `file:///` Verification Script (`scripts/verify-package.py`)

**Files:**
- Create: `skills/atb-game-package/scripts/verify-package.py`
- Modify: `tests/test_package_game.py`

**Interfaces:**
- Consumes: `<game>-standalone.html` and `<game>-portable/` output from Task 1
- Produces: CLI script `skills/atb-game-package/scripts/verify-package.py` accepting `--html-file`, `--portable-dir`, `--zip-file`, `--min-colored-ratio`

- [ ] **Step 1: Write integration test for verification script**
Add test in `tests/test_package_game.py` testing `verify_portable_integrity()` and `verify_zip_permissions()` on the packaged fixture.

- [ ] **Step 2: Run test to verify it fails**
Run: `python3 -m unittest tests/test_package_game.py`
Expected: FAIL (verify_portable_integrity not defined).

- [ ] **Step 3: Implement `skills/atb-game-package/scripts/verify-package.py`**
Implement headless verification in pure Python 3:
1. `find_chrome_binary(explicit_path=None)` (discovers system Chrome / Chromium / Edge / Brave).
2. Pure Python PNG reader `compute_png_colored_ratio(png_path)` (copied/adapted from `skills/atb-game-porting/scripts/verify-headless.py`).
3. `verify_standalone_file_url(chrome_bin, html_file, out_dir, min_colored_ratio=0.90)`:
   - Opens `file:///<abs_path>?atb_verify_stage=initial|gameplay|stage2` in headless Chrome without starting any HTTP server.
   - Captures screenshots, verifies colored pixel ratio, and asserts 0 console errors/CORS failures.
4. `verify_portable_bundle(portable_dir)`:
   - Verifies no broken symlinks, checks that `Play-macOS.command` and `Play-Windows.bat` exist.
5. `verify_release_zip(zip_path)`:
   - Reads zip header and verifies `Play-macOS.command` has `0755` permissions.
6. CLI entrypoint supporting `--html-file`, `--portable-dir`, `--zip-file`, `--skip-browser`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python3 -m unittest tests/test_package_game.py`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add skills/atb-game-package/scripts/verify-package.py tests/test_package_game.py
git commit -m "feat(package): implement headless file protocol and bundle verification script"
```

---

### Task 3: Skill Specifications & Progressive Disclosure Documentation

**Files:**
- Create: `skills/atb-game-package/SKILL.md`
- Create: `skills/atb-game-package/SINGLE-FILE-VFS.md`
- Create: `skills/atb-game-package/PORTABLE-LAUNCHER-AND-VERIFY.md`
- Create: `skills/atb-game-package/agents/openai.yaml`
- Create: `docs/atb-game-package.md`

**Interfaces:**
- Produces: Complete skill directory matching ATBGamePort skill specifications.
- Validates against: `scripts/validate-skills.mjs`.

- [ ] **Step 1: Write `agents/openai.yaml`**
Create `skills/atb-game-package/agents/openai.yaml` with:
```yaml
interface:
  display_name: "ATB Game Package"
  short_description: "Zero-dependency offline packager for HTML5 games with standalone HTML and native launchers"
```

- [ ] **Step 2: Write `SINGLE-FILE-VFS.md`**
Document Phase 1 & 2: asset discovery, symlink handling, VFS manifest generation, and in-browser VFS runtime shim interception specifications.

- [ ] **Step 3: Write `PORTABLE-LAUNCHER-AND-VERIFY.md`**
Document Phase 3 & 4: portable directory materialization, macOS `.command` & Windows `.bat` launchers, `zipfile` `0755` permissions, and `file:///` headless verification.

- [ ] **Step 4: Write `SKILL.md`**
Create `skills/atb-game-package/SKILL.md` (~100 lines) with valid frontmatter (`name: atb-game-package`, `description`), prerequisites, 4-phase execution workflow, and non-negotiable red lines.

- [ ] **Step 5: Write `docs/atb-game-package.md`**
Create human-facing documentation covering installation, CLI usage (`package-game.py` & `verify-package.py`), dual-mode package formats, and integration with `atb-game-porting`.

- [ ] **Step 6: Commit**
```bash
git add skills/atb-game-package/ docs/atb-game-package.md
git commit -m "docs(package): add atb-game-package skill specifications and guides"
```

---

### Task 4: Repository Manifest & Cross-Skill Integration

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `skills/README.md`
- Modify: `skills/atb-game-porting/SKILL.md`
- Modify: `docs/atb-game-porting.md`
- Modify: `scripts/link-skills.sh` (if needed)

**Interfaces:**
- Consumes: Skill `skills/atb-game-package`
- Produces: 100% clean validation in `npm run check`

- [ ] **Step 1: Update `.claude-plugin/plugin.json`**
Add `"./skills/atb-game-package"` to `skills` array.

- [ ] **Step 2: Update `skills/README.md`**
Add `atb-game-package` entry in the skill directory index.

- [ ] **Step 3: Update `README.md` and `README.zh-CN.md`**
Add `atb-game-package` to the skill showcase section, commands list, and workflow explanation in both languages.

- [ ] **Step 4: Update `skills/atb-game-porting/SKILL.md` and `docs/atb-game-porting.md`**
Add optional post-porting packaging pointer (Step 9 / Packaging section) pointing to `atb-game-package`.

- [ ] **Step 5: Run validation check**
Run: `npm run check` (or `node scripts/sync-plugin-version.mjs --check && node scripts/validate-skills.mjs`)
Expected: `All skill repository validations passed!`.

- [ ] **Step 6: Commit**
```bash
git add .claude-plugin/plugin.json README.md README.zh-CN.md skills/README.md skills/atb-game-porting/SKILL.md docs/atb-game-porting.md
git commit -m "chore(manifest): register atb-game-package skill across plugin and documentation"
```

---

## Plan Self-Review Checklist

- [x] Spec coverage: All 6 spec sections are implemented across Tasks 1–4.
- [x] Step scan: Every step is single-action, carries checkable verification commands, and avoids vague lines.
- [x] Type consistency: File names, script arguments (`--input-dir`, `--out-dir`, `--mode`), and VFS function names align across all tasks.
- [x] Review Focus: 5 failure modes mapped to test assertions in Task 1 and Task 2.
- [x] Proportion: Clear and concise plan document without transcript code dumps.
