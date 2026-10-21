# ADR 0002: Flat `skills/<skill-name>/` Layout and Native Multi-Agent Plugin Manifests

## Context

Agent skills can be consumed via two primary distribution routes:
1. **Managed Plugins** (`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`), which auto-update in Claude Code, Codex, GitHub Copilot CLI, and VS Code whenever `plugin.json`'s `version` field increments.
2. **File Copy / CLI Installers** (`npx skills@latest add atbfun/ATBGamePort` and `gemini skills install --path skills`), which copy skill directories into the user's workspace.

In multi-bucket repositories (`skills/<bucket>/<skill-name>/`), single-path installers like Gemini CLI and Codex recursive discovery require per-bucket flags or risk pulling in non-promoted draft buckets.

## Decision

1. **Flat Promoted Layout (`skills/<skill-name>/`)**:
   - Place promoted skills directly under `skills/<skill-name>/` (starting with `skills/atb-game-porting/`).
   - Co-locate all progressive disclosure reference files (`MIGRATE-TEMPLATE.md`, `REVERSE-ENGINEERING.md`, `ASSETS-AND-I18N.md`, `GAMEPLAY-AND-STORAGE.md`, `CANVAS-AND-UI.md`, `AUDIO-AND-VERIFICATION.md`), `agents/openai.yaml`, and `scripts/verify-headless.py` inside `skills/atb-game-porting/`.
2. **Self-Hosted Plugin Marketplace (`.claude-plugin/`)**:
   - Ship `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` at the repository root.
   - Automate version synchronization from `package.json` to `.claude-plugin/plugin.json` via `scripts/sync-plugin-version.mjs` and `.github/workflows/release.yml`.

## Consequences

- Every major coding agent harness (Claude Code, Codex, Copilot CLI, VS Code, Gemini CLI, Cursor, Windsurf, OpenCode, Antigravity) can install `atb-game-porting` cleanly from a single canonical path.
- Merging a Changeset release PR automatically triggers plugin updates for subscribed users.
