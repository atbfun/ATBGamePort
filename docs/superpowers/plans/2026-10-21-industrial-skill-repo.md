# ATBGamePort Industrial-Grade Skill Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure `ATBGamePort` into an industrial-grade, multi-agent installable, continuously versioned Skill & Plugin repository modeled after `mattpocock/skills`.

**Architecture:** Place the core skill under `skills/atb-game-porting/` using Progressive Disclosure (`SKILL.md` as a ~100-line execution spine pointing to 6 phase-specific sibling reference files and `scripts/verify-headless.py`). Ship multi-agent plugin manifests (`.claude-plugin/plugin.json` and `marketplace.json` + `agents/openai.yaml`), a Changesets release pipeline (`package.json`, `scripts/sync-plugin-version.mjs`, `.github/workflows/release.yml`), and a zero-dependency static contract validator (`scripts/validate-skills.mjs` + `.github/workflows/validate.yml`) alongside bilingual showcase docs (`README.md`, `README.zh-CN.md`) and domain governance (`GLOSSARY.md`, `CLAUDE.md`, `SCOPE.md`, `.agents/adr/`).

**Tech Stack:** Markdown (Agent Skills specification), Node.js (ESM validation & version sync scripts, `@changesets/cli`), Python 3 (`verify-headless.py`), Bash (`link-skills.sh`, `list-skills.sh`), GitHub Actions.

**Spec:** [`docs/superpowers/specs/2026-10-21-industrial-skill-repo-design.md`](../specs/2026-10-21-industrial-skill-repo-design.md)

## Global Constraints

- Repository URL: `https://github.com/atbfun/ATBGamePort`, Brand URL: `https://fun.aitobox.com`, Marketplace name: `atbfun`, Plugin/Skill name: `atb-game-porting`.
- Code generation safety guardrail: Never exceed 1,000 lines in a single file write or edit call.
- Language rule: All agent-consumed files (`SKILL.md`, disclosed references, `GLOSSARY.md`, `CLAUDE.md`, ADRs, `docs/atb-game-porting.md`) in concise English; top-level showcase READMEs in both English (`README.md`) and Simplified Chinese (`README.zh-CN.md`).
- Preserve 100% of original `atb-game-porting/SKILL.md` domain requirements across `skills/atb-game-porting/SKILL.md` and its 6 disclosed reference files, then remove the root `atb-game-porting/` directory.
- Track `.agents/adr/`, `.agents/install-block.md`, and `.agents/rules/env-activate.md` in Git (update `.gitignore` so `.agents` is not blanket-ignored).

## Review Focus

- Broken relative links or missing disclosed reference files inside `skills/atb-game-porting/SKILL.md` must fail `node scripts/validate-skills.mjs` with exit code `1`.
- Version drift between `package.json` and `.claude-plugin/plugin.json` must fail `node scripts/sync-plugin-version.mjs --check` with exit code `1`.
- Self-referential symlinks on `~/.claude/skills` or `~/.agents/skills` pointing into the repo must be detected and rejected by `scripts/link-skills.sh` before creating circular links.
- Missing `agents/openai.yaml` or mismatched frontmatter `name` vs. directory name must fail `node scripts/validate-skills.mjs`.
- `skills/atb-game-porting/scripts/verify-headless.py` must gracefully handle missing Chrome binary or non-existent target directory with a clear error message and non-zero exit code, while supporting `--help` cleanly.

---

### Task 1: Plugin Manifests, Release Scripts, and Repository Contract Validator

**Files:**
- Modify: `.gitignore`
- Create: `package.json`
- Create: `.changeset/config.json`
- Create: `.changeset/README.md`
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `scripts/sync-plugin-version.mjs`
- Create: `scripts/validate-skills.mjs`
- Create: `scripts/list-skills.sh`
- Create: `scripts/link-skills.sh`

**Interfaces:**
- Consumes: Node.js `node:fs`, `node:path`, `node:url`.
- Produces:
  - `node scripts/sync-plugin-version.mjs [--check]` (syncs `package.json` `version` -> `.claude-plugin/plugin.json` `version`)
  - `node scripts/validate-skills.mjs` (validates plugin manifests, skill frontmatter, `agents/openai.yaml`, relative file links inside `skills/**/*.md`, and skill mentions in `README.md`, `README.zh-CN.md`, `skills/README.md`)
  - `scripts/list-skills.sh` & `scripts/link-skills.sh`

- [ ] **Step 1: Create `package.json`, `.changeset/`, `.claude-plugin/`, and `scripts/`**

Create `package.json` (`name: "atb-game-porting-skills"`, `version: "1.0.0"`, `private: true`, scripts: `changeset`, `version`, `check-plugin-version`, `validate`, `check`), `.changeset/config.json` (`repo: "atbfun/ATBGamePort"`, `access: "restricted"`, `baseBranch: "main"`), `.claude-plugin/plugin.json` (`name: "atb-game-porting"`, `version: "1.0.0"`, `skills: ["./skills/atb-game-porting"]`), `.claude-plugin/marketplace.json` (`name: "atbfun"`, plugin `atb-game-porting`), `scripts/sync-plugin-version.mjs`, `scripts/validate-skills.mjs`, `scripts/list-skills.sh`, and `scripts/link-skills.sh` (chmod `+x`). Update `.gitignore` to remove the blanket `.agents` ignore line so `.agents/` governance files are tracked.

- [ ] **Step 2: Run `sync-plugin-version.mjs --check` and `validate-skills.mjs` to verify expected initial behavior**

Run:
```bash
node scripts/sync-plugin-version.mjs --check
node scripts/validate-skills.mjs
```
Expected: `sync-plugin-version.mjs --check` outputs `plugin.json version is 1.0.0 (already in sync)` and exits `0`; `validate-skills.mjs` fails with exit code `1` reporting that `./skills/atb-game-porting/SKILL.md` does not exist yet.

- [ ] **Step 3: Commit Task 1**

```bash
git add .gitignore package.json .changeset .claude-plugin scripts
git commit -m "feat(infra): add plugin manifests, changesets config, and skill validator scripts"
```

---

### Task 2: Progressive Disclosure Skill Decomposition & Headless Verification Script

**Files:**
- Create: `skills/README.md`
- Create: `skills/atb-game-porting/SKILL.md`
- Create: `skills/atb-game-porting/MIGRATE-TEMPLATE.md`
- Create: `skills/atb-game-porting/REVERSE-ENGINEERING.md`
- Create: `skills/atb-game-porting/ASSETS-AND-I18N.md`
- Create: `skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md`
- Create: `skills/atb-game-porting/CANVAS-AND-UI.md`
- Create: `skills/atb-game-porting/AUDIO-AND-VERIFICATION.md`
- Create: `skills/atb-game-porting/agents/openai.yaml`
- Create: `skills/atb-game-porting/scripts/verify-headless.py`
- Delete: `atb-game-porting/SKILL.md`

**Interfaces:**
- Consumes: Legacy `atb-game-porting/SKILL.md` specification and `scripts/validate-skills.mjs` rules from Task 1.
- Produces:
  - `skills/atb-game-porting/SKILL.md` with context pointers to `MIGRATE-TEMPLATE.md`, `REVERSE-ENGINEERING.md`, `ASSETS-AND-I18N.md`, `GAMEPLAY-AND-STORAGE.md`, `CANVAS-AND-UI.md`, `AUDIO-AND-VERIFICATION.md`, and `scripts/verify-headless.py`.
  - `python3 skills/atb-game-porting/scripts/verify-headless.py --web-dir <dir> [--out-dir <dir>] [--min-colored-ratio 0.90]`

- [ ] **Step 1: Create `skills/atb-game-porting/` progressive disclosure files, `agents/openai.yaml`, `skills/README.md`, and `scripts/verify-headless.py`**

Decompose `atb-game-porting/SKILL.md` into `skills/atb-game-porting/SKILL.md` (~100 lines) and the 6 disclosed reference files preserving 100% of the technical rules:
1. `MIGRATE-TEMPLATE.md`: Full 7-phase `source/<game_name>/MIGRATE.md` checklist template and `target/<game_name>/` deliverable tree.
2. `REVERSE-ENGINEERING.md`: Phase 1 REA (`open_binary`, `binary_overview`, `inspect_pe_resources`), Hopper Disassembler (`/Applications/Hopper Disassembler.app` CLI & GUI), `objdump`/`otool`/`strings`/`hexdump`, `.rdata` vtable/RTTI recovery, and `target/<game_name>/analysis/reverse_engineering_report.md`.
3. `ASSETS-AND-I18N.md`: Phase 2 32-bit RGB+Alpha PNG composition, MO3/MOD/MIDI to MP3/OGG transcoding via `libopenmpt`/`ffmpeg`, Sound ID mapping table, and 1:1 original i18n sync or 6-language generation (`en`, `zh-CN`, `ja`, `fr`, `de`, `es`) with runtime hot-switching.
4. `GAMEPLAY-AND-STORAGE.md`: Phase 3 core physics & mechanics, `StorageManager` with `atb_<game_name>_*` namespace isolation and `try...catch` + in-memory fallback, cross-device JSON save export/import (`atb_<game_name>_save_<YYYYMMDD_HHMMSS>.json`), and mobile Pointer/Touch coordinate normalization (`getBoundingClientRect()`, `touch-action: none`, $\ge 44 \times 44\text{px}$ virtual controls).
5. `CANVAS-AND-UI.md`: Phase 4 Zero-Black-Screen 5 defensive rules (`isImgValid`, `web/assets -> ../assets` symlink + bidirectional fallback, `document.readyState` guard, instant frame-1 live render under start overlay, headless pixel check), `100dvh` + `aspect-ratio` + `env(safe-area-inset-*)` responsive layout, and `fun.aitobox.com` console banner + UI badge + interactive easter egg modal.
6. `AUDIO-AND-VERIFICATION.md`: Phase 5 Dual-Mode Web Audio API + HTML5 Audio/synthetic fallback, lazy loading, touch autoplay unlock, Phase 6 headless browser verification via `scripts/verify-headless.py`, and Phase 7 mandatory `grill-with-docs` self-inspection loop.

Create `skills/atb-game-porting/scripts/verify-headless.py` (executable Python 3 script supporting `--help`, `--web-dir`, `--out-dir`, `--min-colored-ratio`) and remove the legacy `atb-game-porting/` directory.

- [ ] **Step 2: Verify `verify-headless.py` and `list-skills.sh`**

Run:
```bash
python3 -m py_compile skills/atb-game-porting/scripts/verify-headless.py
python3 skills/atb-game-porting/scripts/verify-headless.py --help
./scripts/list-skills.sh
```
Expected: `py_compile` exits `0`, `--help` prints usage instructions, and `list-skills.sh` outputs `skills/atb-game-porting/SKILL.md`.

- [ ] **Step 3: Commit Task 2**

```bash
git add -A skills atb-game-porting
git commit -m "feat(skill): decompose atb-game-porting into progressive disclosure modules and headless verifier"
```

---

### Task 3: Governance, Glossary, ADRs, Bilingual Documentation & GitHub Workflows

**Files:**
- Create: `GLOSSARY.md`
- Create: `CLAUDE.md`
- Create: `AGENTS.md`
- Create: `SCOPE.md`
- Create: `CHANGELOG.md`
- Create: `.agents/install-block.md`
- Create: `.agents/adr/0001-explicit-prerequisites-for-re-and-grilling.md`
- Create: `.agents/adr/0002-flat-skills-layout-and-claude-plugin.md`
- Create: `docs/atb-game-porting.md`
- Create: `README.md`
- Create: `README.zh-CN.md`
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/idea.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`
- Create: `.github/workflows/release.yml`
- Create: `.github/workflows/validate.yml`

**Interfaces:**
- Consumes: Skill paths and validation contracts from Tasks 1 & 2.
- Produces: Complete repository documentation, governance files, and CI/CD workflows passing `npm run check`.

- [ ] **Step 1: Create `GLOSSARY.md`, `CLAUDE.md`, `AGENTS.md`, `SCOPE.md`, `CHANGELOG.md`, and `.agents/` files**

Write `GLOSSARY.md` defining the 6 core domain terms (`Source Bundle`, `Target Port`, `Migration State Machine`, `Zero-Black-Screen Guard`, `Dual-Mode Audio Matrix`, `Cross-Device Save Envelope`), `CLAUDE.md` (and `AGENTS.md` pointing to `CLAUDE.md`), `SCOPE.md`, `CHANGELOG.md` (`1.0.0`), `.agents/install-block.md`, and ADRs `0001` and `0002`.

- [ ] **Step 2: Create `docs/atb-game-porting.md`, `README.md`, `README.zh-CN.md`, and `.github/` templates & workflows**

Write `docs/atb-game-porting.md` (with sections `What it does`, `When to reach for it`, `Prerequisites`, `The 6-Phase Porting Pipeline`, `Common questions`, `It's working if`), `README.md` (English showcase with prerequisite setup, 30-second multi-agent install blocks, "Why This Skill Exists" 4-failure-mode narrative, and skill reference), `README.zh-CN.md` (Simplified Chinese counterpart), `.github/ISSUE_TEMPLATE/{bug.yml,idea.yml,config.yml}`, and `.github/workflows/{release.yml,validate.yml}`.

- [ ] **Step 3: Run full validation suite and local skill linking test**

Run:
```bash
npm run check
./scripts/list-skills.sh
./scripts/link-skills.sh
```
Expected: `npm run check` passes with 0 errors (`plugin.json version is 1.0.0 (already in sync)` and `All skill validations passed!`), `list-skills.sh` outputs `skills/atb-game-porting/SKILL.md`, and `link-skills.sh` links `atb-game-porting` into `~/.claude/skills` and `~/.agents/skills`.

- [ ] **Step 4: Commit Task 3**

```bash
git add GLOSSARY.md CLAUDE.md AGENTS.md SCOPE.md CHANGELOG.md .agents docs README.md README.zh-CN.md .github
git commit -m "docs: add bilingual READMEs, glossary, ADRs, human docs, and CI/release workflows"
```
