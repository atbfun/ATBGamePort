# `MIGRATE.md` Standard Document Generation Template

When creating `source/<game_name>/MIGRATE.md` for a new game, use the template below as the single source of truth and state machine. Customize class names, binary magic headers, sound enums, and mechanics to match the specific game under `source/<game_name>/`.

```markdown
# <Game Name> Porting Specification & Progress Checklist (MIGRATE.md)

- **Source Path**: `source/<game_name>/`
- **Target Path**: `target/<game_name>/`
- **Target Platform**: Modern Native HTML5 Canvas Instant-Play (60 FPS, Zero External Framework Dependencies)
- **Created Date**: YYYY-MM-DD

---

## Task Execution Checklist

### Phase 1: PE Dissection, Symbol Extraction & Proprietary Format RE (Prioritize REA & Maximize Hopper)
- [ ] **1.1 REA & Native Tool Collaborative Analysis & Unpacking**: Prioritize invoking REA (`reverse-engineer-anything`) alongside local tools (Hopper Disassembler and CLI toolchains) for `binary_overview` and `inspect_pe_resources`, identify packing (e.g., UPX), unpack, and analyze PE sections and import tables.
- [ ] **1.2 REA & Hopper RTTI Symbol & Class Graph Recovery**: Use REA and Hopper Disassembler to scan `.rdata` vtables and RTTI symbols, reconstructing the class hierarchy, main app, board, entities, and managers.
- [ ] **1.3 REA & Hopper Decompilation of Proprietary Level/Data Formats**: Decompile curve trajectories, spawning timelines, physics parameters, and config decoding functions (generating parser scripts/code).
- [ ] **1.4 Produce Reverse Engineering Report**: Record analysis findings in `target/<game_name>/analysis/reverse_engineering_report.md`.

### Phase 2: Full Asset Restructuring & Multi-Language i18n
- [ ] **2.1 Icon & Texture Extraction**: Extract PE embedded icons and basic textures.
- [ ] **2.2 Dual-Channel Alpha Automated Composition**: Batch-merge separated RGB textures and grayscale Alpha masks into 32-bit transparent PNGs.
- [ ] **2.3 SpriteSheet & Animation Frame Parsing**: Export motion sequences, particle explosions, and font glyph metadata.
- [ ] **2.4 Native BGM Tracker Transcoding**: Reverse proprietary music (MO3/MOD/MIDI) and transcode to modern stereo `MP3` and `OGG`.
- [ ] **2.5 Native Sound Library & Sound ID Mapping**: Extract all native sound effects, building a 1:1 mapping table matching native enums.
- [ ] **2.6 Multi-Language (i18n) Extraction & 6-Language Generation**: Extract original strings; if single-language, auto-generate complete dictionaries for English (`en`), Simplified Chinese (`zh-CN`), Japanese (`ja`), French (`fr`), German (`de`), and Spanish (`es`) with runtime hot-switching.

### Phase 3: Core Physics & Game Mechanics Implementation
- [ ] **3.1 Player Input & Interaction**: Implement mouse aiming, keyboard hotkeys, firing mechanics, and ammo swapping.
- [ ] **3.2 Collision Detection & Insertion Mechanics**: Implement high-precision ballistic collision detection with smooth insertion and extrusion physics.
- [ ] **3.3 Match-3 Rules & Elimination Algorithm**: Implement color matching, cascading chain reactions, and independent multi-segment entity displacement.
- [ ] **3.4 Magnetic Attraction & Combo Chains**: Implement magnetic rollback attraction between matching ends and progressive combo multipliers.
- [ ] **3.5 Power-Ups & Special Ability State Machines**: Implement activation conditions, radii, durations, and mutual exclusions for all classic power-ups.
- [ ] **3.6 Stage Objectives, Skull Danger & Win/Loss Resolution**: Implement gauge chantings, skull mouth death triggers, life deductions, and stage victory progression.
- [ ] **3.7 Local Storage Persistence & Save Architecture**: Implement `StorageManager` with namespace isolation and `try...catch` guards to persist user settings (volume/mute/language), unlocked stages, profiles, and high scores with in-memory fallbacks.
- [ ] **3.8 Cross-Device Save Export & Import**: Implement standard JSON save export downloads and upload import validation, enabling seamless cross-device synchronization.
- [ ] **3.9 Mobile Touch & Input Normalization**: Unify Pointer/Touch and Mouse/Keyboard events, provide on-screen virtual buttons (touch targets >= 44px), and suppress mobile gesture interference.

### Phase 4: Visual Rendering, Particle Systems & Occlusion Layers (Zero Black Screen)
- [ ] **4.1 Layered Canvas Rendering**: Formally partition background, shadows, moving entities, tunnel occlusion masks, particles, and HUD layers.
- [ ] **4.2 Tangent Angle Alignment**: Calculate rotational orientation `alpha = atan2(dy, dx)` based on waypoint vectors for realistic rolling visuals.
- [ ] **4.3 Particles & Dynamic Feedback**: Implement explosion shockwaves, sparks, floating bonus score text, and camera shake.
- [ ] **4.4 Rendering Robustness & Geometric Fallbacks**: Validate all image draws with `isImgValid`, provide Canvas vector fallbacks, and wrap frame loops in `try...catch` to prevent `DOMException` crashes.
- [ ] **4.5 Multi-Language UI & Settings Panel**: Implement 6-language hot-switching, volume sliders, and save reset options in the UI.
- [ ] **4.6 Save Management UI (Export/Import Buttons & Dialog)**: Provide clean save export download and file upload restoration controls with visual feedback.
- [ ] **4.7 Mobile & Desktop Responsive Layout**: Implement `100dvh` and `aspect-ratio` adaptive scaling, Safe Area notch insets, and mobile compact layouts with normalized coordinate mapping.
- [ ] **4.8 Platform Easter Egg (fun.aitobox.com) Implementation**: Output console banner on initialization, provide persistent `Powered by fun.aitobox.com` badge in settings/main menu, and interactive easter egg modal.

### Phase 5: Native-Grade Audio Matrix & Dual-Mode Sound Engine (Lazy Load)
- [ ] **5.1 Dual-Mode Audio Implementation**:
  - Web Audio API for zero-latency polyphonic mixing under HTTP hosting.
  - Automatic fallback to HTML5 Audio cloning and synthetic tone fallbacks under local `file://` offline execution.
- [ ] **5.2 BGM Seamless Looping & Dynamic SFX**: Implement looping background music, pitch-shifting combo chains, and danger sirens.
- [ ] **5.3 Audio Lazy Loading & Autoplay Unlock**: Prevent connection pool exhaustion by lazy loading audio assets on demand and unlocking upon first user interaction.

### Phase 6: Engineering Delivery & Automated Verification
- [ ] **6.1 Project Code Archiving**: Organize `src/` (C++ simulation engine) and `web/` (instant-play HTML5 Canvas).
- [ ] **6.2 Cross-Protocol & Browser Compatibility**: Verify stability across HTTP hosting and direct offline `file://` double-clicking.
- [ ] **6.3 Performance & Hand-Feel Benchmarking**: Ensure locked 60 FPS, automatic multi-level progression, and gameplay physics fidelity matching the original.
- [ ] **6.4 Automated Headless Browser Snapshot & Pixel Ratio Verification**: Run `verify-headless.py` capturing initial, gameplay, and stage transition snapshots, confirming 0 console errors and canvas colored pixel ratio >= 90%.
- [ ] **6.5 i18n Switching & Local Storage Persistence Verification**: Verify clean typography across 6 languages without clipping, and complete restoration of settings and saves across reloads.
- [ ] **6.6 Cross-Device Save Export/Import Verification**: Verify JSON export, storage clearing, and 100% save restoration upon import across separate browser sessions.
- [ ] **6.7 Mobile & Multi-Resolution Responsive Verification**: Test across desktop (4K/1080p) and mobile (iPhone/iPad/Android) portrait and landscape modes, confirming zero distortion and pixel-accurate touch tracking.
- [ ] **6.8 Platform Easter Egg & Link Verification**: Verify console banner logging, interactive modal trigger on logo/badge clicks, and valid links to `fun.aitobox.com`.

### Phase 7: grill-with-docs Self-Inspection & Iteration Loop
- [ ] **7.1 Automated grill-with-docs In-Depth Audit**: Conduct self-examination across architecture, reverse engineering completeness, physical fidelity, and Web resilience.
- [ ] **7.2 Unconditional Adoption of Recommended Options**: Adopt all best-practice engineering options recommended by `grill-with-docs`.
- [ ] **7.3 In-Place Full Refinement & Hardening**: Execute second-round comprehensive code and documentation refinement, eliminating all blind spots and recording Review Findings.
```

---

## Standard Deliverables Directory Structure (`target/<game_name>/`)

Ported projects under `target/<game_name>/` must maintain the following layout:

```text
target/<game_name>/
├── CMakeLists.txt              # C++ simulation build configuration (optional but recommended)
├── README.md                   # Standalone technical guide and execution instructions
├── analysis/                   # Reverse engineering analysis reports
│   └── reverse_engineering_report.md
├── assets/                     # Reconstructed full asset library (32-bit PNGs, transcoded audio, configs)
├── src/                        # Reconstructed object-oriented C++ logic source code
└── web/                        # Instant-play HTML5 entrypoint
    ├── assets -> ../assets     # Symbolic link for HTTP & file:/// dual compatibility
    └── index.html              # Pure native Canvas single-entry or modular implementation
```
