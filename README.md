# gitctx

> **Switch Git user configs per directory** — work email here, personal email there.

Ever commit with your work email to a personal repo? Or forget to set your signing key for an open-source project? **gitctx** lets you define named profiles and apply them to any directory — instantly and reliably.

## Features

- 🎯 **Profile-based** — define named configs (work, personal, oss) once, apply anywhere
- 📁 **Directory-scoped** — each project gets the right identity automatically
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
# Create your first profile
gitctx add work --name "Jane Doe" --email "jane@company.com" --signingkey ABC123

# Create another
gitctx add personal --name "Jane Doe" --email "jane@gmail.com"

# Apply to the current directory
gitctx use work

# Check what's active
gitctx current

# List all profiles
gitctx list

# Remove a profile
gitctx remove personal
```

## How It Works

`gitctx` stores profiles in `~/.gitctx/profiles.toml`. When you run `gitctx use <name>`, it writes the matching `user.name`, `user.email`, and `user.signingKey` to the **local** Git config of the current directory (`.git/config`).

This means:
- ✅ No global config changes — each repo stays independent
- ✅ Works with any Git workflow
- ✅ Survives across clones — just run `gitctx use` once per clone

## Shell Integration (optional)

Add to your `.bashrc` / `.zshrc` to show the active profile in your prompt:

```bash
# Show gitctx profile in prompt
__gitctx_ps1() {
    local profile
    profile=$(gitctx current --quiet 2>/dev/null)
    if [ -n "$profile" ]; then
        echo " [$profile]"
    fi
}
PS1='$(__gitctx_ps1)'$PS1
```

## Configuration File

Profiles are stored in `~/.gitctx/profiles.toml`:

```toml
[work]
name = "Jane Doe"
email = "jane@company.com"
signingkey = "ABC123DEF456"

[personal]
name = "Jane Doe"
email = "jane@gmail.com"
```

## License

MIT © Jonathan La Porte
