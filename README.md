# ATBGamePort — Industrial-Grade Game Porting Skills

[![skills.sh](https://skills.sh/b/atbfun/ATBGamePort)](https://skills.sh/atbfun/ATBGamePort)
[![Powered by fun.aitobox.com](https://img.shields.io/badge/Powered_by-fun.aitobox.com-0ea5e9)](https://fun.aitobox.com)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](./LICENSE)

**English** | [简体中文](./README.zh-CN.md)

Industrial-grade agent skills for reverse-engineering and porting classic desktop games (PopCap SexyAppFramework executables, Windows PE C++ binaries, Flash engines, and retro mini-games) into modern, zero-dependency HTML5 Canvas & Web Audio instant-play games. Powered by [fun.aitobox.com](https://fun.aitobox.com).

Porting real games with AI is hard. Prompting an agent with *"build me a web clone of this game"* produces a shallow toy with guessed physics, broken assets, and black screens. `ATBGamePort` replaces guesswork with a disciplined 7-phase engineering pipeline: authoritative binary reverse engineering, automated RGB+Alpha asset composition, 6-language i18n, cross-device `localStorage` save sync, desktop & mobile dual adaptation, and headless browser pixel verification.

---

## Installation (30-second setup)

A plugin updates itself automatically when new versions release. [skills.sh](https://skills.sh/atbfun/ATBGamePort) copies editable files into your project. Pick one route per agent so you don't install every skill twice.

### 1. Install Prerequisites (Companion Skills)

`atb-game-porting` coordinates with two companion skills for binary dissection and architectural self-inspection:

```bash
# 1. Install grill-with-docs (from mattpocock/skills) for Phase 7 self-inspection
npx skills@latest add mattpocock/skills --skill=grill-with-docs

# 2. Ensure the reverse-engineer-anything (REA) skill & MCP server are enabled in your agent
```

### 2. Install `atb-game-porting`

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add atbfun/ATBGamePort
claude plugin install atb-game-porting@atbfun
```

Updates itself automatically when a new version is released.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add atbfun/ATBGamePort
codex plugin add atb-game-porting@atbfun
```

Updates itself at startup.

</details>

<details>
<summary><strong>GitHub Copilot</strong> (CLI and VS Code)</summary>

```bash
copilot plugin marketplace add atbfun/ATBGamePort
copilot plugin install atb-game-porting@atbfun
```

Then, once, add to `~/.copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "atbfun": { "source": { "source": "github", "repo": "atbfun/ATBGamePort" }, "autoUpdate": true }
  }
}
```

In VS Code, run **Chat: Install Plugin From Source** and enter `https://github.com/atbfun/ATBGamePort`. It updates daily.

</details>

<details>
<summary><strong>Gemini CLI</strong> (manual updates)</summary>

```bash
gemini skills install https://github.com/atbfun/ATBGamePort.git --path skills
```

Re-run the command to update.

</details>

<details>
<summary><strong>Any other agent, or editable files</strong> (manual updates)</summary>

```bash
npx skills@latest add atbfun/ATBGamePort -a <agent>  # cursor, windsurf, opencode, devin, amp, pi; omit -a to choose
```

To update, run `npx skills@latest update`.

</details>

<details>
<summary><strong>Local Maintainer Symlink</strong> (git pull updates)</summary>

```bash
git clone https://github.com/atbfun/ATBGamePort.git
cd ATBGamePort
./scripts/link-skills.sh
```

Links `skills/atb-game-porting` directly into `~/.claude/skills` and `~/.agents/skills`.

</details>

### 3. Drop a game into `source/<game_name>/` and start porting

Place your original game bundle under `source/<game_name>/` and tell your agent:

> Port `source/<game_name>` to HTML5 using `atb-game-porting`.

---

## Why This Skill Exists

We built `atb-game-porting` to eliminate the four recurring failure modes that plague AI-assisted game ports.

### #1: The Agent Guesses Game Mechanics Instead of Reading the Binary

**The Problem**: When handed a classic desktop game directory, agents typically ignore the `.exe` binary and proprietary data files, hallucinating level curves, collision radii, and spawn tables from scratch. The resulting port feels nothing like the original game.

**The Fix**: [`Phase 1: Binary Reverse Engineering`](./skills/atb-game-porting/REVERSE-ENGINEERING.md) mandates calling `reverse-engineer-anything` (REA) alongside `/Applications/Hopper Disassembler.app` and CLI toolchains (`objdump`, `otool`, `strings`, `hexdump`) first. The agent unpacks UPX binaries, recovers MSVC `.rdata` vtables and RTTI class hierarchies, decompiles proprietary curve/level parsers, and writes `target/<game>/analysis/reverse_engineering_report.md` before writing a single line of Web code.

### #2: The Dreaded HTML5 Canvas Black Screen

**The Problem**: Browser Canvas ports routinely fail on first launch due to four traps: passing a 404 image (`img.complete === true` but `naturalWidth === 0`) to `ctx.drawImage` (which throws an uncaught `DOMException` and kills the `requestAnimationFrame` loop), broken relative paths between HTTP and `file:///`, missed `DOMContentLoaded` events on large level bundles, or an empty black background behind the start screen.

**The Fix**: [`Phase 4: Zero-Black-Screen Guard`](./skills/atb-game-porting/CANVAS-AND-UI.md) enforces 5 defensive invariants—`isImgValid(img)` with pure Canvas geometric vector fallbacks on every layer, `web/assets -> ../assets` symlinks with bidirectional path probing, `document.readyState` bootstrap guards, live Level 1 rendering on frame 1 beneath the start overlay, and automated pixel verification via [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py).

### #3: Desktop-Only Toy Ports Without i18n, Saves, or Mobile Touch

**The Problem**: Most AI ports hardcode English strings, lose all progress on browser refresh, break on mobile viewports or iPhone notches, and go completely silent under offline `file:///` execution.

**The Fix**:
- **[`Phase 2: Assets & 6-Language i18n`](./skills/atb-game-porting/ASSETS-AND-I18N.md)**: Batch-composites separated RGB + Alpha masks into 32-bit PNGs, transcodes `MO3`/`MOD`/`MIDI` tracker modules to `MP3`/`OGG`, and synchronizes original multi-language strings or generates a complete 6-language dictionary (`en`, `zh-CN`, `ja`, `fr`, `de`, `es`) with runtime hot-switching.
- **[`Phase 3: StorageManager & Mobile Touch`](./skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md)**: Persists settings, profiles, unlocked stages, and high scores in namespace-isolated `localStorage` (`atb_<game>_*`) with Cross-Device JSON Save Export/Import, normalized Pointer/Touch coordinates, `100dvh` safe-area layout, and $\ge 44 \times 44\text{px}$ virtual touch controls.
- **[`Phase 5: Dual-Mode Audio Matrix`](./skills/atb-game-porting/AUDIO-AND-VERIFICATION.md)**: Uses Web Audio API over HTTP and automatically degrades to pooled `HTMLAudioElement` cloning plus procedural synth tones over `file:///`.

### #4: Premature Completion ("It Should Work!")

**The Problem**: Long multi-phase instructions cause agents to rush later phases or claim victory without ever opening a browser.

**The Fix**: `atb-game-porting` uses **Progressive Disclosure** (keeping [`SKILL.md`](./skills/atb-game-porting/SKILL.md) under 110 lines and loading phase specs on demand), tracks state in [`source/<game>/MIGRATE.md`](./skills/atb-game-porting/MIGRATE-TEMPLATE.md), requires running [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py) (proving `0` console errors and $\ge 90\%$ colored pixel ratio across 3 snapshots), and finishes with a mandatory `grill-with-docs` self-inspection loop.

---

## Reference

### Model-invoked

- **[atb-game-porting](./skills/atb-game-porting/SKILL.md)** ([docs](./docs/atb-game-porting.md)): End-to-end static reverse engineering, automated asset & 6-language i18n restructuring, `localStorage` cross-device save persistence, responsive mobile/desktop adaptation, and zero-black-screen HTML5 Canvas porting of classic desktop games.
  - [`MIGRATE-TEMPLATE.md`](./skills/atb-game-porting/MIGRATE-TEMPLATE.md): Standard 7-phase `source/<game>/MIGRATE.md` state machine checklist template.
  - [`REVERSE-ENGINEERING.md`](./skills/atb-game-porting/REVERSE-ENGINEERING.md): Phase 1 REA, Hopper Disassembler, and native CLI binary dissection specification.
  - [`ASSETS-AND-I18N.md`](./skills/atb-game-porting/ASSETS-AND-I18N.md): Phase 2 32-bit RGB+Alpha composition, tracker audio transcoding, and 6-language i18n specification.
  - [`GAMEPLAY-AND-STORAGE.md`](./skills/atb-game-porting/GAMEPLAY-AND-STORAGE.md): Phase 3 physics fidelity, `StorageManager`, cross-device JSON save sync, and mobile touch normalization.
  - [`CANVAS-AND-UI.md`](./skills/atb-game-porting/CANVAS-AND-UI.md): Phase 4 Zero-Black-Screen Guard, `100dvh` safe-area responsive layout, and `fun.aitobox.com` interactive easter egg specification.
  - [`AUDIO-AND-VERIFICATION.md`](./skills/atb-game-porting/AUDIO-AND-VERIFICATION.md): Phase 5 Dual-Mode Audio Matrix, Phase 6 headless Chrome pixel verification, and Phase 7 `grill-with-docs` self-check loop.
  - [`scripts/verify-headless.py`](./skills/atb-game-porting/scripts/verify-headless.py): Automated headless Chrome zero-error and $\ge 90\%$ colored pixel ratio verifier.

---

## Repository Governance

- [`GLOSSARY.md`](./GLOSSARY.md): Ubiquitous domain vocabulary across skills and ported games.
- [`CLAUDE.md`](./CLAUDE.md): Maintainer invariants and progressive disclosure rules.
- [`SCOPE.md`](./SCOPE.md): Contribution bar for issues and pull requests.
- [`CHANGELOG.md`](./CHANGELOG.md): Version release history managed via Changesets.
