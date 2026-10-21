# ADR 0001: Explicit Prerequisites for Reverse Engineering (`reverse-engineer-anything`) and Self-Inspection (`grill-with-docs`)

## Context

`atb-game-porting` orchestrates end-to-end game reverse engineering and HTML5 Canvas reconstruction. Two steps in the workflow rely on specialized companion skills and native binary analysis toolchains:
1. **Phase 1 (Binary Reverse Engineering)**: Dissects PE/Mach-O executables, `.rdata` vtables/RTTI symbols, and proprietary data formats using `reverse-engineer-anything` (REA) alongside `/Applications/Hopper Disassembler.app` and CLI tools (`objdump`, `otool`, `strings`, `hexdump`).
2. **Phase 7 (Self-Inspection Loop)**: Audits the generated `MIGRATE.md` specification and HTML5 codebase for edge-case bugs and race conditions using `grill-with-docs` (from [`mattpocock/skills`](https://github.com/mattpocock/skills)).

## Decision

We adopt an **Explicit Prerequisites** policy (modeled after `mattpocock/skills` ADR 0001):

- **Hard Skill Dependencies (`reverse-engineer-anything` and `grill-with-docs`)**:
  - Declared prominently in Step 1 of the installation guide in `README.md` / `README.zh-CN.md`, in `docs/atb-game-porting.md`, and in the `## Explicit Prerequisites` section of `skills/atb-game-porting/SKILL.md`.
  - If an agent runs `atb-game-porting` without these companion skills installed, `SKILL.md` instructs the agent to stop and give the user the exact installation command rather than silently skipping binary analysis or self-auditing.
- **Native Toolchain Dependencies**:
  - Documented explicitly: Python 3 + Google Chrome/Chromium (for `scripts/verify-headless.py`), `ffmpeg` + `libopenmpt` (for audio transcoding), and `Hopper Disassembler` + standard CLI binary utilities (`objdump`, `otool`, `strings`, `hexdump`).

## Consequences

- Zero silent quality degradation: agents never hallucinate binary formats or skip the final self-inspection loop.
- Users get a clear, copy-pasteable 30-second setup path in `README.md` and `README.zh-CN.md`.
