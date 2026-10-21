# ATBGamePort Industrial-Grade Skill Repository Design Spec

- **Date**: 2026-10-21
- **Repository**: `https://github.com/atbfun/ATBGamePort`
- **Brand / Platform**: `fun.aitobox.com`
- **Reference Architecture**: [`mattpocock/skills`](https://github.com/mattpocock/skills)

---

## 1. Shared Understanding & Goals

### 1.1 Purpose
Transform `ATBGamePort` from a single monolithic `atb-game-porting/SKILL.md` file into a reliable, continuously updatable, industrial-grade open-source Agent Skill & Plugin repository modeled after `mattpocock/skills`.

### 1.2 Confirmed Architectural Decisions
1. **Repository Positioning**: Pure Skill & Plugin distribution repository. It ships skills, progressive-disclosure reference specs, verification scripts, documentation, and plugin manifests—without bundling heavy game binary workspaces (`source/` or `target/`) in the repository.
2. **Skill Granularity**: Core single skill (`skills/atb-game-porting/`) backed by **Progressive Disclosure** sibling reference files (`MIGRATE-TEMPLATE.md`, `REVERSE-ENGINEERING.md`, `ASSETS-AND-I18N.md`, `GAMEPLAY-AND-STORAGE.md`, `CANVAS-AND-UI.md`, `AUDIO-AND-VERIFICATION.md`) and an executable headless browser verification script (`scripts/verify-headless.py`).
3. **Prerequisite Strategy**: Explicit Prerequisites (following `mattpocock/skills` ADR 0001). Companion skills (`reverse-engineer-anything` and `grill-with-docs` from `mattpocock/skills`) and native RE toolchains (`Hopper Disassembler`, `objdump`, `otool`, `strings`, `hexdump`, `ffmpeg`, `libopenmpt`, Python 3 + Chrome) are explicitly declared in `README.md`, `README.zh-CN.md`, and `SKILL.md`, with clear install instructions and hard precondition prompts if missing.
4. **Language Strategy**: All agent-consumed files (`SKILL.md`, disclosed references, `GLOSSARY.md`, `CLAUDE.md`, ADRs, `docs/`) are written in concise English for optimal cross-model token efficiency and trigger accuracy; top-level showcase documentation is provided in both English (`README.md`) and Simplified Chinese (`README.zh-CN.md`).

---

## 2. Target Repository Layout

```text
ATBGamePort/
├── .agents/
│   ├── adr/
│   │   ├── 0001-explicit-prerequisites-for-re-and-grilling.md
│   │   └── 0002-flat-skills-layout-and-claude-plugin.md
│   ├── install-block.md
│   └── rules/
│       └── env-activate.md
├── .changeset/
│   ├── README.md
│   └── config.json
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug.yml
│   │   ├── config.yml
│   │   └── idea.yml
│   └── workflows/
│       ├── release.yml
│       └── validate.yml
├── docs/
│   └── atb-game-porting.md
├── scripts/
│   ├── link-skills.sh
│   ├── list-skills.sh
│   ├── sync-plugin-version.mjs
│   └── validate-skills.mjs
├── skills/
│   ├── README.md
│   └── atb-game-porting/
│       ├── SKILL.md
│       ├── MIGRATE-TEMPLATE.md
│       ├── REVERSE-ENGINEERING.md
│       ├── ASSETS-AND-I18N.md
│       ├── GAMEPLAY-AND-STORAGE.md
│       ├── CANVAS-AND-UI.md
│       ├── AUDIO-AND-VERIFICATION.md
│       ├── agents/
│       │   └── openai.yaml
│       └── scripts/
│           └── verify-headless.py
├── AGENTS.md
├── CHANGELOG.md
├── CLAUDE.md
├── GLOSSARY.md
├── LICENSE
├── README.md
├── README.zh-CN.md
├── SCOPE.md
└── package.json
```

> **Cleanup Note**: Once `atb-game-porting/SKILL.md` is migrated and decomposed into `skills/atb-game-porting/`, the legacy root-level `atb-game-porting/` directory is removed so there is only a single source of truth. Also, `.gitignore` is updated so `.agents/adr/` and `.agents/install-block.md` are tracked in Git while `.agents/rules/` or local scratch files remain properly handled.

---

## 3. Component Design

### 3.1 Progressive Disclosure Skill (`skills/atb-game-porting/`)

Following the `writing-for-agents` information hierarchy:

1. **`SKILL.md` (Primary Spine, ~100 lines)**:
   - **Frontmatter**: `name: atb-game-porting` and a high-precision model-invoked `description` front-loading trigger branches (porting classic desktop/PE/Flash games to HTML5 Canvas, initializing or updating `source/<game>/MIGRATE.md`, auditing zero-black-screen/i18n/save/responsive compliance).
   - **Explicit Prerequisites Gate**: Instructs the agent to verify that `reverse-engineer-anything` (REA) and `grill-with-docs` are available (telling the user how to install them if absent), and activates the local environment (`conda activate ATBPort` when present).
   - **Code Generation Safety Guardrail**: Enforces the hard limit of $\le 1,000$ lines per file write/edit call (skeleton first, incremental population second).
   - **Phase-Gated Workflow & Context Pointers**: Lists the 6-phase porting state machine + Phase 7 `grill-with-docs` loop. Each phase step contains an explicit context pointer instructing the agent to read the corresponding sibling file before executing that phase:
     - Step 2 (`MIGRATE.md` initialization/sync) $\rightarrow$ Read [`MIGRATE-TEMPLATE.md`](MIGRATE-TEMPLATE.md)
     - Phase 1 (Binary RE & Format Dissection) $\rightarrow$ Read [`REVERSE-ENGINEERING.md`](REVERSE-ENGINEERING.md)
     - Phase 2 (Asset Restructuring & 6-Language i18n) $\rightarrow$ Read [`ASSETS-AND-I18N.md`](ASSETS-AND-I18N.md)
     - Phase 3 (Physics, `StorageManager`, Cross-Device Save & Touch Input) $\rightarrow$ Read [`GAMEPLAY-AND-STORAGE.md`](GAMEPLAY-AND-STORAGE.md)
     - Phase 4 (Layered Canvas, Zero-Black-Screen Guard, Responsive Layout & `fun.aitobox.com` Easter Egg) $\rightarrow$ Read [`CANVAS-AND-UI.md`](CANVAS-AND-UI.md)
     - Phase 5 & 6 (Dual-Mode Audio Matrix, Headless Browser Verification & `grill-with-docs` Self-Check Loop) $\rightarrow$ Read [`AUDIO-AND-VERIFICATION.md`](AUDIO-AND-VERIFICATION.md) and execute [`scripts/verify-headless.py`](scripts/verify-headless.py)

2. **Disclosed Reference Files**:
   - Preserve 100% of the domain rules, defensive patterns, and specifications from the original `atb-game-porting/SKILL.md`, organized into focused, co-located reference modules with explicit completion criteria at the end of each phase.

3. **Automated Headless Verification Script (`skills/atb-game-porting/scripts/verify-headless.py`)**:
   - A self-contained Python 3 CLI script that:
     1. Starts a local background `ThreadingHTTPServer` serving `target/<game>/web/` (or `target/<game>/` with `web/assets` symlink verification);
     2. Launches headless Chrome/Chromium (auto-detecting macOS/Linux/Windows binary paths or Playwright/CDP) with an isolated `--user-data-dir`;
     3. Captures `screen_initial.png`, `screen_gameplay.png`, and `screen_stage2.png` (or verifies rendered frames);
     4. Checks that console errors and uncaught page exceptions equal `0`, and verifies that the non-black/colored pixel ratio is $\ge 90\%$, exiting non-zero on failure.

4. **Codex / Agent UI Metadata (`skills/atb-game-porting/agents/openai.yaml`)**:
   ```yaml
   interface:
     display_name: "ATB Game Porting"
     short_description: "Reverse-engineer and port classic games to zero-dependency HTML5 Canvas"
   ```

---

### 3.2 Multi-Agent Plugin & Distribution System

1. **`.claude-plugin/plugin.json`**:
   - Name: `atb-game-porting`
   - Version: `1.0.0` (synced automatically from `package.json`)
   - Repository: `https://github.com/atbfun/ATBGamePort`
   - Homepage: `https://fun.aitobox.com`
   - Skills array: `["./skills/atb-game-porting"]`

2. **`.claude-plugin/marketplace.json`**:
   - Name: `atbfun`
   - Owner: `ATBPort (https://fun.aitobox.com)`
   - Exposes `atb-game-porting` at source `"./"` so Claude Code, Codex, GitHub Copilot CLI, and VS Code can subscribe to automatic updates.

3. **`.agents/install-block.md`**:
   - Canonical install snippets for Claude Code, Codex, GitHub Copilot, Gemini CLI (`--path skills`), and `npx skills@latest add atbfun/ATBGamePort`, plus the prerequisite installation commands for `reverse-engineer-anything` and `mattpocock/skills`.

4. **`scripts/link-skills.sh` & `scripts/list-skills.sh`**:
   - `link-skills.sh` symlinks every skill directory under `skills/` into `~/.claude/skills` and `~/.agents/skills`, protecting against self-referential symlink loops.
   - `list-skills.sh` outputs all `SKILL.md` paths in the repository in sorted order.

---

### 3.3 Continuous Release & Validation Pipeline

1. **`package.json` & `.changeset/`**:
   - Configures `@changesets/cli` and `@changesets/changelog-github` pointing to `atbfun/ATBGamePort`.
   - Scripts:
     - `"changeset": "changeset"`
     - `"version": "changeset version && node scripts/sync-plugin-version.mjs"`
     - `"check-plugin-version": "node scripts/sync-plugin-version.mjs --check"`
     - `"validate": "node scripts/validate-skills.mjs"`
     - `"check": "npm run check-plugin-version && npm run validate"`

2. **`scripts/sync-plugin-version.mjs`**:
   - Synchronizes `package.json` `version` to `.claude-plugin/plugin.json` during `npm run version` and verifies sync under `--check`.

3. **`scripts/validate-skills.mjs`**:
   - Zero-dependency Node.js validation script that fails with exit code `1` if:
     - `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` is invalid JSON or missing required fields;
     - Any skill listed in `plugin.json` is missing `SKILL.md` or `agents/openai.yaml`;
     - `SKILL.md` frontmatter is missing `name` or `description`, or `name` does not match the directory name;
     - Any relative markdown link or script reference inside `skills/atb-game-porting/*.md` points to a non-existent file;
     - Any skill is missing from `README.md`, `README.zh-CN.md`, or `skills/README.md`.

4. **GitHub Actions Workflows (`.github/workflows/`)**:
   - `release.yml`: Triggers on push to `main`, runs `changesets/action@v1` to open/update the `"chore: version skills"` PR and tag releases.
   - `validate.yml`: Triggers on `pull_request` and `push` to `main`, running `npm run check` and `python3 -m py_compile skills/atb-game-porting/scripts/verify-headless.py`.

---

### 3.4 Governance, Domain Glossary & Documentation

1. **`GLOSSARY.md`**:
   - Defines canonical domain terms: **Source Bundle**, **Target Port**, **Migration State Machine (`MIGRATE.md`)**, **Zero-Black-Screen Guard**, **Dual-Mode Audio Matrix**, **Cross-Device Save Envelope**, and **StorageManager**.
2. **`CLAUDE.md` & `AGENTS.md`**:
   - Documents repository invariants for coding agents maintaining `ATBGamePort` (progressive disclosure rules, doc sync rules, version sync rules, no-broken-links rule, and local `conda activate ATBPort` dev rule).
3. **`SCOPE.md` & `.github/ISSUE_TEMPLATE/`**:
   - Requires every bug or enhancement issue to include an **Observed Porting Failure** (game genre/engine, porting phase, expected vs. actual agent behavior).
4. **`.agents/adr/`**:
   - `0001-explicit-prerequisites-for-re-and-grilling.md`
   - `0002-flat-skills-layout-and-claude-plugin.md`
5. **`docs/atb-game-porting.md`**:
   - Human-facing guide structured into `## What it does`, `## When to reach for it`, `## Prerequisites`, `## The 6-Phase Porting Pipeline`, `## Common questions`, and `## It's working if`.
6. **`README.md` & `README.zh-CN.md`**:
   - Bilingual entrypoints with language switcher links, 30-second prerequisite + plugin setup instructions, "Why This Skill Exists" failure-mode breakdown, architecture overview, and skill reference table.

---

## 4. Verification & Acceptance Criteria

1. `npm run check` passes with 0 errors (version sync, frontmatter validity, `openai.yaml` presence, zero broken links across all skill files and READMEs).
2. `python3 skills/atb-game-porting/scripts/verify-headless.py --help` executes cleanly and validates CLI arguments.
3. `./scripts/list-skills.sh` and `./scripts/link-skills.sh` run cleanly without errors.
4. All 100% of technical requirements from the original `atb-game-porting/SKILL.md` (REA + Hopper RE, 32-bit alpha composition, MO3/MOD audio transcoding, 6-language i18n, `StorageManager` + JSON save export/import, 100dvh + safe-area + touch normalization, zero-black-screen 5 rules, `fun.aitobox.com` console & UI easter eggs, `grill-with-docs` self-check loop, $\le 1000$ lines edit guardrail) are preserved across `SKILL.md` and its disclosed reference files.
