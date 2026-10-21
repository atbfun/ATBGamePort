---
name: atb-game-porting
description: Use when porting, reverse-engineering, or rebuilding classic desktop games into modern Web/HTML5 games. Prioritizes calling REA (reverse-engineer-anything) for binary analysis, enforces i18n multi-language synchronization or 6-language generation (en/zh-CN/ja/fr/de/es), implements localStorage-based settings and progress persistence with cross-device save export/import, ensures comprehensive mobile & desktop dual-screen responsive adaptation across resolutions, embeds fun.aitobox.com platform-driven easter eggs, initializes or updates `source/<game>/MIGRATE.md`, and drives the 6-phase migration workflow.
---

# ATB Game Porting

End-to-end discipline for static reverse engineering, automated asset restructuring, and modern zero-dependency HTML5 Canvas / Web Audio instant-play porting of classic native desktop games (PopCap games, Windows PE executables, MSVC C++ architectures, Flash engines).

Read [`GLOSSARY.md`](../../GLOSSARY.md) if present in the repository for ubiquitous domain terminology.

## Explicit Prerequisites

Before starting a port, verify that the required companion skills and local tools are available:

1. **Required Companion Skills**:
   - **`reverse-engineer-anything` (REA)**: Mandatory for Phase 1 binary dissection (`open_binary`, `binary_overview`, `inspect_pe_resources`).
   - **`grill-with-docs`** (from [`mattpocock/skills`](https://github.com/mattpocock/skills)): Mandatory for the Phase 7 self-inspection and architecture hardening loop.
   - If either companion skill is missing, stop and instruct the user to install them before proceeding.
2. **Environment & Native Toolchains**:
   - Activate the project Conda environment if present: `conda activate ATBPort`.
   - Utilize local reverse engineering tools (`/Applications/Hopper Disassembler.app` on macOS, `objdump`, `otool`, `strings`, `hexdump`), media transcoders (`ffmpeg`, `libopenmpt`), and Python 3 + Chrome/Chromium for headless pixel verification.

## Non-Negotiable Red Lines

1. **Code Generation Safety (<= 1,000 Lines per Call)**:
   Never generate or replace more than 1,000 lines of code in a single file write or edit tool call. For large HTML5 entrypoints or C++ simulation engines, write the structural skeleton, constants, and interface stubs first, then populate implementations incrementally across multiple tool calls.
2. **Evidence Over Guessing**:
   Never guess binary formats, trajectories, or physics constants. Extract authoritative evidence from PE sections, RTTI symbols, and decompiled pseudocode first.
3. **Zero-Black-Screen First Delivery**:
   Every port must pass all 5 Zero-Black-Screen defensive invariants and the automated headless browser check ($\ge 90\%$ colored pixel ratio, 0 console errors) before claiming completion.

## Core Execution Workflow

Execute every game port in strict phase order. Load each phase's disclosed reference file right before starting that phase so its rules and completion criteria stay fresh in context:

```
[1. Inspect Source Bundle & Scaffold Target Port]
        │
        ▼
[2. Initialize or Sync source/<game>/MIGRATE.md] ──> Read MIGRATE-TEMPLATE.md
        │
        ▼
[3. Phase 1: Binary RE & Format Dissection]       ──> Read REVERSE-ENGINEERING.md
        │
        ▼
[4. Phase 2: Asset Restructuring & 6-Lang i18n]   ──> Read ASSETS-AND-I18N.md
        │
        ▼
[5. Phase 3: Physics, StorageManager & Touch]     ──> Read GAMEPLAY-AND-STORAGE.md
        │
        ▼
[6. Phase 4: Zero-Black-Screen Canvas & UI]       ──> Read CANVAS-AND-UI.md
        │
        ▼
[7. Phase 5 & 6: Audio Matrix & Headless Verify]  ──> Read AUDIO-AND-VERIFICATION.md
        │                                             & run scripts/verify-headless.py
        ▼
[8. Phase 7: grill-with-docs Self-Check Loop]     ──> Call Skill tool with "grill-with-docs"
```

### Step 1: Inspection & Target Scaffolding
1. Inspect executables (`.exe`, `.dll`), artwork (`images/`), audio (`sounds/`, `music/`), and configs (`levels/`, `properties/`) in `source/<game_name>/`.
2. Scaffold `target/<game_name>/` with `analysis/`, `assets/`, `src/`, `web/`, and `README.md`.
3. Immediately create the bidirectional asset symlink:
   ```bash
   ln -sfn ../assets target/<game_name>/web/assets
   ```

### Step 2: Migration State Machine (`source/<game_name>/MIGRATE.md`)
Read [`MIGRATE-TEMPLATE.md`](MIGRATE-TEMPLATE.md). If `source/<game_name>/MIGRATE.md` does not exist, generate it from the template tailored to the game's binary formats, classes, and mechanics. If it already exists, resume from the first unchecked item. Update checkboxes in `MIGRATE.md` as each phase completes.

### Step 3: Phased Implementation (Phases 1–6)
Work through Phases 1 to 6 in order, reading the disclosed specification for each phase before writing code:

- **Phase 1 (Binary Dissection & Format Recovery)**: Read [`REVERSE-ENGINEERING.md`](REVERSE-ENGINEERING.md). Call the Skill tool with `"reverse-engineer-anything"` and combine with Hopper Disassembler and CLI tools to produce `target/<game_name>/analysis/reverse_engineering_report.md`.
- **Phase 2 (Asset Composition, Audio Transcoding & 6-Language i18n)**: Read [`ASSETS-AND-I18N.md`](ASSETS-AND-I18N.md). Rebuild 32-bit transparent PNGs, transcode tracker audio, and build 1:1 original or 6-language (`en`, `zh-CN`, `ja`, `fr`, `de`, `es`) dictionaries.
- **Phase 3 (Core Physics, `StorageManager`, Save Sync & Touch Input)**: Read [`GAMEPLAY-AND-STORAGE.md`](GAMEPLAY-AND-STORAGE.md). Implement gameplay mechanics, namespace-isolated `localStorage` persistence with JSON export/import, and normalized Pointer/Touch controls.
- **Phase 4 (Zero-Black-Screen Canvas, Responsive UI & Platform Easter Egg)**: Read [`CANVAS-AND-UI.md`](CANVAS-AND-UI.md). Implement layered Canvas rendering with `isImgValid` guards, `100dvh` + safe-area responsive layout, and the `fun.aitobox.com` console banner & interactive UI easter egg.
- **Phase 5 & 6 (Dual-Mode Audio Matrix & Automated Headless Verification)**: Read [`AUDIO-AND-VERIFICATION.md`](AUDIO-AND-VERIFICATION.md). Implement lazy-loaded Web Audio / HTML5 Audio playback and run [`scripts/verify-headless.py`](scripts/verify-headless.py) to prove 0 console errors and $\ge 90\%$ colored pixels across initial, gameplay, and stage-transition snapshots.

### Step 4: Mandatory `grill-with-docs` Self-Inspection Loop (Phase 7)
Upon completing the initial `MIGRATE.md` specification and initial full codebase implementation:
1. Call the Skill tool with `"grill-with-docs"` to audit architecture, async race conditions, missing asset fallbacks, audio pool exhaustion, and state machine edge cases.
2. Unconditionally adopt all **Recommended Options** surfaced during the audit.
3. Refactor the codebase and update `MIGRATE.md` in-place, then re-run [`scripts/verify-headless.py`](scripts/verify-headless.py) to confirm a clean green state before delivery.
