# gitctx

[![PyPI version](https://img.shields.io/pypi/v/gitctx.svg)](https://pypi.org/project/gitctx/)
[![Python versions](https://img.shields.io/pypi/pyversions/gitctx.svg)](https://pypi.org/project/gitctx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

> **Switch Git user configs per directory — with auto-detection** — work email here, personal email there, OSS identity there.

Ever commit with your work email to a personal repo? Or forget to set your signing key for an open-source project? **gitctx** lets you define named profiles, apply them to any directory, and **auto-detect the right profile** based on the repo's remote URL or path.

## Features

- 🎯 **Profile-based** — define named configs (work, personal, oss) once, apply anywhere
- 📁 **Directory-scoped** — each project gets the right identity automatically
- 🔮 **Auto-detect** — rules match profiles by remote URL pattern or directory path
- 🔄 **Instant switching** — one command to change, no manual `git config` edits
- 🔍 **Current status** — see which profile is active at a glance
- ✏️ **Manage profiles** — add, edit, remove profiles with simple commands
- 🪝 **Shell hook** — optional prompt integration to show active profile
- 💾 **Tiny & fast** — pure Python, no external dependencies beyond `rich`

## Install

```bash
pip install gitctx
```

## Quick Start

```bash
# Create profiles
gitctx add work --name "Jane Doe" --email "jane@company.com" --signingkey ABC123
gitctx add personal --name "Jane Doe" --email "jane@gmail.com"
gitctx add oss --name "JaneDoe" --email "jane@users.noreply.github.com"

# Apply manually
gitctx use work

# Check what's active
gitctx current
```

## Auto-Detection (the killer feature)

Define rules so gitctx **automatically** picks the right profile when you enter a repo:

```bash
# Match any repo whose remote URL contains "github.com/mycompany"
gitctx rule add --profile work --remote "github.com/mycompany"

# Match repos under a specific directory
gitctx rule add --profile work --path "/home/jane/work/*"

# Use regex for more complex matching
gitctx rule add --profile oss --remote "github\\.com/janedoe/"

# Higher priority rules win
gitctx rule add --profile client-a --remote "github.com/client-a" --priority 10
gitctx rule add --profile work --remote "github.com" --priority 1

# Auto-apply the matching profile to the current repo
gitctx auto

# Dry run to see what would be applied
gitctx auto --dry-run

# List rules
gitctx rule list

# Remove a rule
gitctx rule remove 1
```

### How auto-detection works

1. Rules are checked in **priority order** (highest first)
2. If a rule's `--remote` pattern matches any of the repo's remote URLs (as substring or regex), it's a match
3. If a rule's `--path` glob matches the repo's directory, it's a match
4. If **both** `--remote` and `--path` are specified, **both** must match (AND logic)
5. The first matching rule wins

### Shell hook for automatic switching

Add to your `.bashrc` / `.zshrc` to auto-switch profiles when you `cd` into a repo:

```bash
# Auto-apply gitctx profile on directory change
gitctx_auto_cd() {
    builtin cd "$@" || return
    if git rev-parse --git-dir > /dev/null 2>&1; then
        gitctx auto 2>/dev/null
    fi
}
alias cd='gitctx_auto_cd'
```

Or just show the active profile in your prompt:

```bash
__gitctx_ps1() {
    local profile
    profile=$(gitctx current --quiet 2>/dev/null)
    if [ -n "$profile" ]; then
        echo " [$profile]"
    fi
}
PS1='$(__gitctx_ps1)'$PS1
```

## How It Works

`gitctx` stores profiles in `~/.gitctx/profiles.toml` and rules in `~/.gitctx/rules.toml`. When you run `gitctx use <name>` or `gitctx auto`, it writes the matching `user.name`, `user.email`, and `user.signingKey` to the **local** Git config of the current directory (`.git/config`).

This means:
- ✅ No global config changes — each repo stays independent
- ✅ Works with any Git workflow
- ✅ Survives across clones — just run `gitctx auto` once per clone

## Configuration Files

**Profiles** (`~/.gitctx/profiles.toml`):

```toml
[work]
name = "Jane Doe"
email = "jane@company.com"
signingkey = "ABC123DEF456"

[personal]
name = "Jane Doe"
email = "jane@gmail.com"
```

**Rules** (`~/.gitctx/rules.toml`):

```toml
[[rules]]
profile = "work"
remote_pattern = "github.com/mycompany"
priority = 5

[[rules]]
profile = "personal"
path_glob = "/home/jane/personal/*"

[[rules]]
profile = "oss"
remote_pattern = "github\\.com/janedoe/"
priority = 10
```

## Command Reference

| Command | Description |
|---------|-------------|
| `gitctx add <alias> -n <name> -e <email> [-s <key>]` | Add a profile |
| `gitctx remove <alias>` | Remove a profile |
| `gitctx list` | List all profiles |
| `gitctx use <alias> [-C <dir>]` | Apply a profile to a directory |
| `gitctx current [-C <dir>] [-q]` | Show active profile |
| `gitctx auto [-C <dir>] [-n]` | Auto-detect and apply the right profile |
| `gitctx rule add -p <profile> [-r <remote>] [-P <path>] [--priority N]` | Add an auto-detection rule |
| `gitctx rule list` | List all rules |
| `gitctx rule remove <index>` | Remove a rule |

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick start for contributors:**

```bash
git clone https://github.com/jlaportebot/gitctx.git
cd gitctx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint & format (once configured)
ruff check .
ruff format --check .
```

**Good first issues:** Look for the [`good first issue` label](https://github.com/jlaportebot/gitctx/issues?q=label%3A%22good+first+issue%22) — we'll mentor you through it.

**Questions?** Open a [Discussion](https://github.com/jlaportebot/gitctx/discussions) or [issue](https://github.com/jlaportebot/gitctx/issues/new/choose).

## License

MIT © Jonathan La Porte — see [LICENSE](LICENSE) for details.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). We follow the Contributor Covenant.