# Canonical Install Blocks (`install-block.md`)

Single source of truth for installation commands across `README.md` and `README.zh-CN.md`.
A plugin updates itself when `.claude-plugin/plugin.json` `version` increments; `skills.sh` and `gemini skills install` copy editable files into your workspace. Pick one route per agent so skills are not installed twice.

## 1. Prerequisites

<canonical-block name="prerequisites">

```bash
# 1. Ensure Python 3 (3.10+ recommended) is installed
python3 --version

# 2. Install grill-with-docs (from mattpocock/skills) for Phase 7 self-inspection
npx skills@latest add mattpocock/skills --skill=grill-with-docs

# 3. Ensure reverse-engineer-anything (REA) skill & MCP server are enabled in your agent
```

</canonical-block>

## 2. Install `atb-game-porting`

### Claude Code

<canonical-block name="claude-code">

```bash
claude plugin marketplace add atbfun/ATBGamePort
claude plugin install atb-game-porting@atbfun
```

Updates itself automatically when a new version is released.

</canonical-block>

### Codex

<canonical-block name="codex">

```bash
codex plugin marketplace add atbfun/ATBGamePort
codex plugin add atb-game-porting@atbfun
```

Updates itself at startup.

</canonical-block>

### GitHub Copilot (CLI and VS Code)

<canonical-block name="copilot">

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

</canonical-block>

### Gemini CLI

<canonical-block name="gemini">

```bash
gemini skills install https://github.com/atbfun/ATBGamePort.git --path skills
```

Re-run the command to update.

</canonical-block>

### Any other agent, or editable files (`skills.sh`)

<canonical-block name="other-agents">

```bash
npx skills@latest add https://skills.sh/p/VoswC8My6zgey2MK -a <agent>  # cursor, windsurf, opencode, devin, amp, pi; omit -a to choose
```

To update, run `npx skills@latest update`.

</canonical-block>
