# ATBGamePort Glossary

Ubiquitous domain language shared by human engineers, coding agents, and the `atb-game-porting` skill suite, powered by [fun.aitobox.com](https://fun.aitobox.com).

## Language

**Source Bundle (`source/<game>/`)**:
The read-only input directory holding the original desktop game's artifacts: native executables (`.exe`, `.dll`, PE/Mach-O images), packed archives, legacy separated RGB + Alpha textures, tracker music (`MO3`, `IT`, `XM`, `MOD`, `MIDI`), and configuration files.
_Avoid_: raw folder, old game dir, input dump

**Target Port (`target/<game>/`)**:
The structured output directory produced by the porting workflow, containing `analysis/` (reverse engineering reports and snapshots), `assets/` (reconstructed 32-bit RGBA PNGs, transcoded MP3/OGG audio, and JSON configs), `src/` (C++ simulation code), and `web/` (zero-dependency HTML5 Canvas entrypoint).
_Avoid_: output folder, build dir, dist

**Migration State Machine (`MIGRATE.md`)**:
The canonical single source of truth located at `source/<game>/MIGRATE.md` that tracks the 7-phase porting checklist from binary dissection through `grill-me` self-inspection.
_Avoid_: todo list, porting notes, progress doc

**Zero-Black-Screen Guard**:
The five non-negotiable rendering invariants enforced in Phase 4: (1) `isImgValid(img)` checks with geometric vector fallbacks on every `ctx.drawImage` call, (2) `web/assets -> ../assets` symlink with bidirectional loader fallback, (3) `document.readyState` mount guard, (4) live Level 1 rendering on frame 1 beneath the start overlay, and (5) automated headless browser verification proving $\ge 90\%$ colored pixel ratio and `0` console errors.
_Avoid_: canvas error handling, fallback rendering

**Dual-Mode Audio Matrix**:
The Phase 5 sound architecture that uses the Web Audio API (`AudioContext`) for low-latency polyphonic mixing and pitch-shifted combo chains under HTTP/HTTPS, and automatically falls back to pooled `HTMLAudioElement` cloning plus procedural Web Audio synthesizer tones when opened offline via `file:///`.
_Avoid_: audio player, sound manager

**Cross-Device Save Envelope**:
The standardized JSON export/import payload (`atb_<game>_save_<YYYYMMDD_HHMMSS>.json`) managed by the namespace-isolated `StorageManager` (`atb_<game>_*` keys in `localStorage` with `try...catch` and in-memory fallback), containing `game_id`, `version`, `timestamp`, and `data`.
_Avoid_: save file, localstorage dump

## Relationships

- A **Source Bundle** owns one **Migration State Machine (`MIGRATE.md`)** and produces one **Target Port**.
- Every **Target Port** enforces the **Zero-Black-Screen Guard**, the **Dual-Mode Audio Matrix**, and the **Cross-Device Save Envelope**.
