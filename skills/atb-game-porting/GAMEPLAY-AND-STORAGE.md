# Phase 3: Core Physics, Gameplay Mechanics, LocalStorage Persistence & Touch Input

## 1. High-Fidelity Core Physics & Gameplay State Machines
Reconstruct the original game's mechanics using the exact formulas, speeds, and thresholds recovered in Phase 1:
- **Input & Aiming**: Smooth turret/character rotation, ammo queue preview, and right-click/Space/touch ammo swapping.
- **Collision & Insertion Physics**: High-precision projectile-to-entity collision detection, smooth tangent insertion into moving chains/grids, and forward extrusion interpolation.
- **Elimination, Rollback & Combos**: Color-match elimination (e.g., >= 3 matching segments), gap creation, magnetic attraction rollback when gap ends match colors, and progressive chain/combo score multipliers.
- **Power-Ups & Stage Resolution**: Exact activation timers, blast radii, slow/reverse effects, accuracy beams, coin spawns, progress gauge completion, danger zone warnings, life deduction, and stage transition sequences.

## 2. User Settings & Local Storage Persistence (`StorageManager`)
Deliver a native-grade persistence experience backed by browser `localStorage`:
1. **Persisted Data Scope**:
   - **Personalized Settings**: Master volume, BGM volume, SFX volume, mute state, language preference (`en`/`zh-CN`/`ja`/`fr`/`de`/`es`), fullscreen/aspect-ratio preference, and custom keybindings.
   - **Progress & Profiles**: Player profile names, multi-profile switching, unlocked stages/levels, and highest cleared tiers/modes.
   - **Leaderboards & Statistics**: Historical high scores (player name, score, stage, date) and cumulative statistics (clears, max combos, coins collected, playtime).
2. **Engineering Robustness & Defenses**:
   - **Namespace Isolation**: Prefix all keys with `atb_<game_name>_` (e.g., `atb_<game_name>_settings`, `atb_<game_name>_profiles`, `atb_<game_name>_highscores`) to prevent cross-game collisions on shared domains.
   - **Strict `try...catch` Protection**: Wrap every `localStorage.getItem`, `setItem`, and `removeItem` call in `try...catch` to guard against private/incognito browsing restrictions, `SecurityError`, and `QuotaExceededError`.
   - **In-Memory Fallback**: Seamlessly fall back to an in-memory store when `localStorage` is unavailable so gameplay never crashes.
   - **Auto-Save & Reset**: Auto-save immediately upon setting changes, stage clears, and high-score updates; provide a confirmed "Reset Save Data" action in settings.

## 3. Cross-Device Save Export & Import Specification
Every ported game must provide standardized **Save Export/Import** in `StorageManager`:
- **Export Save (`exportSave()`)**:
  - Serialize all `atb_<game_name>_*` records into a JSON envelope:
    ```json
    {
      "game_id": "atb_<game_name>",
      "version": "1.0.0",
      "timestamp": "2026-10-21T00:00:00.000Z",
      "data": { ... }
    }
    ```
  - Trigger a browser file download named `atb_<game_name>_save_<YYYYMMDD_HHMMSS>.json` (and optionally support clipboard copy).
- **Import Save (`importSave(jsonOrFile)`)**:
  - Accept a `.json` file upload (`<input type="file" accept=".json">`) or pasted JSON string.
  - Validate schema integrity and verify `game_id === "atb_<game_name>"` before mutating state.
  - **Atomic Application & Live Refresh**: Back up current state, write validated keys to `localStorage`, refresh in-memory state and UI immediately without requiring a full page reload, and display a localized success/error toast. Malformed files must leave existing saves untouched.

## 4. Mobile Touch & Cross-Device Input Normalization
1. **Normalized Coordinate Mapping**:
   - Map all Pointer, Touch, and Mouse coordinates into the fixed internal game resolution (`internalWidth` x `internalHeight`) using:
     ```js
     const rect = canvas.getBoundingClientRect();
     const gameX = (clientX - rect.left) * (internalWidth / rect.width);
     const gameY = (clientY - rect.top) * (internalHeight / rect.height);
     ```
2. **Gesture Suppression & Touch Ergonomics**:
   - Apply `touch-action: none; user-select: none; -webkit-user-select: none;` to the canvas container and prevent default browser scrolling/zooming on `touchstart`/`touchmove`.
   - Provide explicit on-screen virtual controls for desktop-only inputs (such as right-click ammo swap or pause/skill hotkeys) with touch hit targets $\ge 44 \times 44\text{px}$.

## Completion Criteria (Phase 3 Done When)
- [ ] All core physics, collision, combo, power-up, and win/loss state machines match the original binary's rules.
- [ ] `StorageManager` persists settings, profiles, unlocked stages, and high scores under `atb_<game_name>_*` with `try...catch` and in-memory fallback.
- [ ] Cross-device JSON Save Export and Import validate `game_id` and hot-refresh game state without page reload.
- [ ] Pointer/Touch coordinates and $\ge 44 \times 44\text{px}$ virtual buttons work accurately across desktop and mobile viewports.
- [ ] Phase 3 items are checked off in `source/<game_name>/MIGRATE.md`.
