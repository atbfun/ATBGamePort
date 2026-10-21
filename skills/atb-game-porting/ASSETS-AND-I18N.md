# Phase 2: Full Asset Restructuring & Multi-Language (i18n) Specification

## 1. Dual-Channel RGB + Alpha Automated Composition
Classic desktop engines (such as PopCap's SexyAppFramework) frequently store color channels (`<name>.jpg` or `<name>.bmp`) separately from grayscale opacity masks (`_<name>.gif`, `<name>_.png`, or palette colorkey masks).
1. Scan `source/<game_name>/images/` and packed archives to pair every RGB image with its corresponding Alpha mask or colorkey rule discovered in Phase 1.
2. Run a deterministic Python (Pillow/NumPy) batch pipeline to composite them into standard 32-bit RGBA transparent PNGs under `target/<game_name>/assets/images/`.
3. Verify that sprite sheet cell dimensions, frame counts, and tunnel occlusion cutouts have clean alpha edges with zero black/magenta halo artifacts.

## 2. Tracker Music & Native Sound Library Transcoding
1. **Tracker Modules (`MO3` / `IT` / `XM` / `MOD` / `S3M` / `MIDI`)**:
   - Inspect module sub-songs, pattern order tables, and loop points recovered in Phase 1.
   - Transcode into browser-native stereo `MP3` and `OGG` tracks via `libopenmpt` (`openmpt123`) and `ffmpeg`, preserving separate sub-songs (e.g., Menu theme, In-game loop, Danger loop, Victory fanfare, Game Over).
2. **Sound Effects & Global Sound ID Mapping**:
   - Convert all native SFX (`.wav`, `.ogg`, `.au`, or embedded resources) into normalized web-ready audio files under `target/<game_name>/assets/sounds/`.
   - Generate a 1:1 `SOUND_MAP` matching the original executable's sound enum identifiers (e.g., `SOUND_BALL_CLICK`, `SOUND_CHIME_1..5`, `SOUND_EXPLODE`, `SOUND_WARNING`).

## 3. Comprehensive Multi-Language & Internationalization (i18n) Specification
1. **Original Multi-Language Synchronization**:
   - If the original binary or asset bundle contains multi-language resources (`.properties`, `.xml`, string tables, PE `.rsrc` string sections), extract and synchronize them 1:1 into the Web i18n dictionary.
2. **Auto-Generate 6-Language System When Absent**:
   - If the original game only supported a single language (e.g., English only), build a complete, natural-sounding i18n dictionary supporting all **6 standard languages**:
     - **English (`en`)**
     - **Simplified Chinese (`zh-CN`)**
     - **Japanese (`ja`)**
     - **French (`fr`)**
     - **German (`de`)**
     - **Spanish (`es`)**
3. **Full UI Coverage & Runtime Hot-Switching**:
   - Translations must cover main menus, settings panels, tutorials/onboarding, stage names, scores & statistics, endgame screens, dialogs, save export/import prompts, and system toasts.
   - Auto-detect initial language via `navigator.language` (falling back to `en`), provide real-time hot-switching in the UI without requiring a page reload, and persist the user's choice in `StorageManager`.

## Completion Criteria (Phase 2 Done When)
- [ ] All RGB + Alpha image pairs and PE icons are composited into 32-bit RGBA PNGs in `target/<game_name>/assets/`.
- [ ] All BGM tracks and SFX are transcoded to Web-compatible formats and indexed in a 1:1 Sound ID mapping table.
- [ ] Complete i18n dictionary (original multi-language sync or full 6-language `en`/`zh-CN`/`ja`/`fr`/`de`/`es` set) is generated with zero missing keys across all UI surfaces.
- [ ] Phase 2 items are checked off in `source/<game_name>/MIGRATE.md`.
