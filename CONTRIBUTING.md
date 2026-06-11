# Contributing to gitctx

Thanks for wanting to contribute! gitctx is a CLI tool for switching Git user configs per directory with auto-detection. All help is welcome — code, docs, tests, bug reports, feature ideas.

## Quick Start

```bash
# Clone and set up
git clone https://github.com/jlaportebot/gitctx.git
cd gitctx
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -v

# Run linting (if configured)
ruff check .
ruff format --check .

# Run the CLI
gitctx --help
```

## How to Contribute

### 1. Find Something to Work On

- Check [open issues](https://github.com/jlaportebot/gitctx/issues) — look for `good first issue`, `help wanted`, `docs`
- Have an idea? Open an issue first to discuss before building
- Found a bug? Report it with the bug template

### 2. Make Your Changes

```bash
# Create a branch
git checkout -b feature/your-thing
# or
git checkout -b fix/your-thing
# or
git checkout -b docs/your-thing

# Make changes, test locally
pytest -v
# ruff check .  # once configured
# ruff format --check .  # once configured
```

### 3. Submit a PR

- Push your branch and open a PR against `main`
- Fill out the PR template
- Link the issue: `Fixes #123` or `Closes #123`
- CI must pass (tests, lint, format)

## Code Standards

### Python Style

- **ruff** for linting + formatting (configured in pyproject.toml)
- **Python 3.9+** — use modern syntax
- Line length: 100 chars

### Architecture

```
src/gitctx/
├── cli.py          # Click CLI entry point (all commands)
├── config.py       # Profiles & rules TOML handling
├── git_utils.py    # Git config reading/writing
├── detector.py     # Auto-detection logic (rules matching)
└── shell.py        # Shell hook helpers
```

**Key principles:**
- Tiny & fast — minimal deps (`rich`, `tomli`, `tomli-w`)
- Single file per concern
- CLI is the main interface — library functions are internal
- Config stored in `~/.gitctx/` — profiles.toml + rules.toml

### Testing

- **Unit tests**: `tests/test_*.py` — test individual functions
- **Integration tests**: `tests/test_cli.py` — end-to-end CLI runs
- **Fixtures**: `tests/conftest.py` — temp dirs, git repos

```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=gitctx --cov-report=term-missing
```

## PR Requirements

- [ ] Tests pass (`pytest -v`)
- [ ] Lint clean (`ruff check .`) — once configured
- [ ] Format clean (`ruff format --check .`) — once configured
- [ ] No debug code left (`print()`, `breakpoint()`, commented-out code)
- [ ] Docstrings on public functions/classes
- [ ] New code has tests
- [ ] Updated docs if user-facing behavior changed

## Communication

- **Issues** — Bugs, features, questions
- **Discussions** — General chat, ideas, "how do I...?"
- **PRs** — Code review happens here

Response time: usually within a day or two.

## Recognition

All contributors get credited in releases. We value code, docs, tests, bug reports, and answering questions.

---

**Questions?** Open a [Discussion](https://github.com/jlaportebot/gitctx/discussions) or comment on an issue.