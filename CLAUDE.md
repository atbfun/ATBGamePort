# ATBGamePort Maintainer Guidelines (`CLAUDE.md`)

Skills live directly under `skills/<skill-name>/` (see [ADR 0002](./.agents/adr/0002-flat-skills-layout-and-claude-plugin.md)):

- `skills/atb-game-porting/`: The flagship end-to-end game reverse engineering and HTML5 Canvas porting workflow.

Every skill in `skills/` must be registered in:
1. `.claude-plugin/plugin.json` (`skills` array)
2. `README.md` (English showcase)
3. `README.zh-CN.md` (Simplified Chinese showcase)
4. `skills/README.md` (Skill index)
5. `docs/<skill-name>.md` (Human-facing documentation page)

## Progressive Disclosure & File Hygiene

- Keep each skill's `SKILL.md` concise (~100–120 lines) as the execution spine and phase router.
- Place phase-specific specifications, templates, and checklists into co-located sibling files inside `skills/<skill-name>/` (`MIGRATE-TEMPLATE.md`, `REVERSE-ENGINEERING.md`, `ASSETS-AND-I18N.md`, `GAMEPLAY-AND-STORAGE.md`, `CANVAS-AND-UI.md`, `AUDIO-AND-VERIFICATION.md`) reached via explicit context pointers.
- Every skill must carry `agents/openai.yaml` with `interface.display_name` and `interface.short_description`.
- Never generate or replace more than 1,000 lines in a single file write or edit tool call.

## Local Environment & Linking

- Before running shell commands in this workspace, activate the Conda environment when available: `conda activate ATBPort`.
- Run `./scripts/link-skills.sh` to symlink all skills under `skills/` into `~/.claude/skills` and `~/.agents/skills`. Re-run after adding or renaming any skill.

## Validation & Versioning

- Install commands in `README.md` and `README.zh-CN.md` are synchronized with [`.agents/install-block.md`](./.agents/install-block.md).
- Always run `npm run check` (`node scripts/sync-plugin-version.mjs --check && node scripts/validate-skills.mjs`) after modifying any skill, manifest, or documentation file.
- Version bumps are managed via `@changesets/cli` (`npx changeset` -> `npm run version`), which automatically syncs `package.json` and `.claude-plugin/plugin.json`.
