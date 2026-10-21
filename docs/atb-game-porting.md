## What it does

`atb-game-porting` drives the end-to-end static reverse engineering, asset reconstruction, and modern zero-dependency HTML5 Canvas / Web Audio porting of classic desktop games (such as PopCap SexyAppFramework executables, Windows PE C++ games, and Flash titles). Rather than letting the agent guess game mechanics from screenshots or filenames, it forces the agent to dissect the original binary first, maintain a persistent 7-phase state machine in `source/<game>/MIGRATE.md`, and verify the finished port in a headless browser before declaring completion.

## When to reach for it

- **Invocation mode.** Type `/atb-game-porting`, or let the agent reach for it automatically whenever you ask to reverse-engineer, port, or rebuild a game under `source/<game>/` into `target/<game>/`.
- **Trigger boundary.** Reach for this when porting a desktop or legacy mini-game to HTML5 Canvas, generating or updating `source/<game>/MIGRATE.md`, or auditing an existing Web port against the Zero-Black-Screen Guard, 6-language i18n, cross-device save sync, or responsive mobile/desktop adaptation requirements.

## Prerequisites

- **Companion skills**:
  - `reverse-engineer-anything` (REA) for Phase 1 PE/Mach-O binary dissection and RTTI extraction.
  - `grill-with-docs` (from [`mattpocock/skills`](https://github.com/mattpocock/skills)) for the Phase 7 self-inspection and architecture hardening loop.
- **Local toolchains**:
  - Python 3 and Google Chrome / Chromium for running `skills/atb-game-porting/scripts/verify-headless.py`.
  - `ffmpeg` and `libopenmpt` (`openmpt123`) when transcoding tracker modules (`MO3`, `IT`, `XM`, `MOD`, `MIDI`).
  - `/Applications/Hopper Disassembler.app` (on macOS) and standard CLI binary tools (`objdump`, `otool`, `strings`, `hexdump`) for deep control-flow and format decompilation.
- **Workspace layout**: Reads from a **Source Bundle** at `source/<game>/`, tracks state in `source/<game>/MIGRATE.md`, and writes the **Target Port** to `target/<game>/`.

## The 6-Phase Porting Pipeline + Self-Check Loop

The skill keeps its top-level `SKILL.md` compact and discloses phase-specific rules only when the agent enters that phase:

| Phase | Disclosed Reference | Core Deliverable |
| :--- | :--- | :--- |
| **Step 2: State Machine** | [`MIGRATE-TEMPLATE.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/MIGRATE-TEMPLATE.md) | Initializes or resumes `source/<game>/MIGRATE.md` |
| **Phase 1: Binary RE** | [`REVERSE-ENGINEERING.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/REVERSE-ENGINEERING.md) | Unpacks binaries, recovers RTTI classes & proprietary formats into `target/<game>/analysis/reverse_engineering_report.md` |
| **Phase 2: Assets & i18n** | [`ASSETS-AND-I18N.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/ASSETS-AND-I18N.md) | Composites 32-bit RGBA PNGs, transcodes tracker audio, and builds 1:1 original or 6-language (`en`/`zh-CN`/`ja`/`fr`/`de`/`es`) dictionaries |
| **Phase 3: Gameplay & Storage** | [`GAMEPLAY-AND-STORAGE.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md) | Rebuilds physics, `StorageManager` (`atb_<game>_*`), JSON Save Export/Import, and normalized touch input |
| **Phase 4: Canvas & UI** | [`CANVAS-AND-UI.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/CANVAS-AND-UI.md) | Enforces the **Zero-Black-Screen Guard**, `100dvh` safe-area responsive layout, and `fun.aitobox.com` easter eggs |
| **Phase 5 & 6: Audio & Verify** | [`AUDIO-AND-VERIFICATION.md`](https://github.com/atbfun/ATBGamePort/blob/main/skills/atb-game-porting/AUDIO-AND-VERIFICATION.md) | Implements the **Dual-Mode Audio Matrix** and runs `scripts/verify-headless.py` ($\ge 90\%$ colored pixels, `0` console errors) |
| **Phase 7: Self-Check Loop** | `grill-with-docs` | Audits edge cases, unconditionally adopts all recommended options, and re-verifies in-place |

## Common questions

**Why does the skill require `isImgValid(img)` and geometric vector fallbacks on every `ctx.drawImage` call?**
In browser Canvas engines, a missing or corrupted image file reports `img.complete === true` while `img.naturalWidth === 0`. Passing that element to `ctx.drawImage` throws an uncaught `DOMException` that immediately terminates the `requestAnimationFrame` loop and leaves the player staring at a black screen. Checking `img && img.complete && img.naturalWidth > 0` and falling back to Canvas vector shapes guarantees the game remains playable even if an asset fails to load.

**How does the ported game work both on an HTTP server and when double-clicked via `file:///`?**
Step 1 creates a `target/<game>/web/assets -> ../assets` symlink, and the asset/audio loaders implement bidirectional path fallback (`assets/` first, `../assets/` second). Simultaneously, the **Dual-Mode Audio Matrix** uses Web Audio API over HTTP and falls back to `HTMLAudioElement` cloning plus Web Audio synth tones when `file:///` blocks `fetch()` via CORS.

**Why is there a hard 1,000-line limit per file edit call?**
Generating multi-thousand-line HTML5 Canvas engines in a single tool call frequently triggers model output truncation or infinite retry loops. Writing the structural skeleton first and filling in modules incrementally keeps every tool call deterministic and reviewable.

## It's working if

- `source/<game>/MIGRATE.md` exists and its checkboxes progress phase by phase alongside `target/<game>/analysis/reverse_engineering_report.md`.
- Opening `target/<game>/web/index.html` renders a live Level 1 game board on frame 1 beneath the start overlay, logs the `fun.aitobox.com` console banner, and hot-switches across all 6 languages (`en`, `zh-CN`, `ja`, `fr`, `de`, `es`).
- Exporting a save downloads `atb_<game>_save_<timestamp>.json`, and importing it restores unlocked levels, settings, and high scores immediately without reloading the page.
- Running `python3 skills/atb-game-porting/scripts/verify-headless.py --web-dir target/<game>/web` exits `0` with `screen_initial.png`, `screen_gameplay.png`, and `screen_stage2.png` all exceeding a `90%` colored pixel ratio and `0` console errors.
