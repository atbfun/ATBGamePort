# Phase 5, 6 & 7: Dual-Mode Audio Matrix, Automated Headless Verification & Self-Check Loop

## 1. Phase 5: Native-Grade Dual-Mode Audio Matrix (Lazy Load)
1. **Dual-Mode Playback Engine**:
   - **Primary (HTTP/HTTPS)**: Use the Web Audio API (`AudioContext`, `GainNode`, `StereoPannerNode`, `playbackRate` pitch-shifting for combo chains) for zero-latency polyphonic mixing.
   - **Offline Fallback (`file:///`)**: When `fetch`/`XMLHttpRequest` is blocked by `file://` CORS restrictions or an audio asset is missing, automatically fall back to pooled `HTMLAudioElement` (`new Audio()`) cloning and procedural Web Audio synthesizer tones (`OscillatorNode` envelopes) so the game never goes silent or throws unhandled promise rejections.
2. **On-Demand Lazy Loading**:
   - Never eagerly fire 50+ simultaneous audio network requests at startup (which triggers `BrokenPipeError` / socket exhaustion on local dev servers). Lazy-load and cache audio buffers on first trigger or via a throttled background queue (concurrency $\le 3$).
3. **Browser Autoplay Unlock**:
   - Attach a one-time unlock listener on `pointerdown`, `touchstart`, and `keydown` to call `audioCtx.resume()` and start BGM playback smoothly upon the player's first gesture.

## 2. Phase 6: Automated Headless Browser Verification (`scripts/verify-headless.py`)
Never claim a port is complete without empirical headless browser proof. Run the bundled verification script located at [`scripts/verify-headless.py`](scripts/verify-headless.py):

```bash
python3 <path-to-skill>/scripts/verify-headless.py \
  --web-dir target/<game_name>/web \
  --out-dir target/<game_name>/analysis/snapshots \
  --min-colored-ratio 0.90
```

### Mandatory Verification Gates:
1. **Zero Console Errors & Uncaught Exceptions**: Headless Chrome DevTools log must show `0` `console.error` calls, `0` uncaught `DOMException` / `ReferenceError` / `TypeError` failures, and `0` failed critical script loads.
2. **Three-Stage Pixel Snapshots ($\ge 90\%$ Colored Pixel Ratio)**:
   - Support the `?atb_verify_stage=initial|gameplay|stage2` URL query parameter in `index.html` (`new URLSearchParams(location.search).get("atb_verify_stage")`) so headless CLI verification can deterministically render each stage:
   - `screen_initial.png` (`?atb_verify_stage=initial`): Initial load state (live Level 1 canvas visible beneath or after the start overlay);
   - `screen_gameplay.png` (`?atb_verify_stage=gameplay`): Active gameplay state (start overlay dismissed, active projectiles/entities and HUD);
   - `screen_stage2.png` (`?atb_verify_stage=stage2`): Level 2 progression / stage transition state;
   - Every captured snapshot must have a non-black/colored pixel ratio $\ge 90\%$ (`0.90`).
3. **Functional Matrix Check**:
   - Verify 6-language runtime hot-switching (`en`, `zh-CN`, `ja`, `fr`, `de`, `es`);
   - Verify `localStorage` persistence across page reload and JSON Save Export/Import round-trip restoration;
   - Verify desktop (`1280x800`) and mobile (`390x844` iPhone viewport) responsive layout without overflow;
   - Verify `fun.aitobox.com` console banner and UI easter egg trigger.

## 3. Phase 7: Mandatory `grill-with-docs` Self-Inspection Loop
Once the initial `MIGRATE.md` and full codebase implementation are complete:
1. Call the Skill tool with `"grill-with-docs"` to perform a relentless architectural and edge-case audit (async race conditions, missing asset fallbacks, memory leaks in particle arrays, audio node cleanup, state transition deadlocks).
2. **Unconditionally adopt all Recommended Options** produced by the `grill-with-docs` audit.
3. Apply the improvements in-place across `target/<game_name>/`, record the audit summary in `source/<game_name>/MIGRATE.md`, and re-run `scripts/verify-headless.py` to confirm all checks remain green.

## Completion Criteria (Phases 5–7 Done When)
- [ ] Dual-mode audio engine plays BGM and pitch-shifted combo SFX under HTTP and degrades cleanly to HTML5 Audio / synth tones under `file:///`.
- [ ] `scripts/verify-headless.py` exits `0` with 3 snapshots (`screen_initial.png`, `screen_gameplay.png`, `screen_stage2.png`), `0` console errors, and colored pixel ratio $\ge 90\%$.
- [ ] `grill-with-docs` self-inspection loop has been executed, all recommended options are implemented, and all Phase 5, 6, and 7 checkboxes in `source/<game_name>/MIGRATE.md` are marked `[x]`.
