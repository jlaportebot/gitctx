# Security Policy

## Reporting a Vulnerability

Found a security issue? **Don't open a public issue.**

Email **security@gitctx.dev** (or DM a maintainer on GitHub) with:
- What you found
- How to reproduce it
- Potential impact

We'll acknowledge within 48 hours and keep you updated.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | ✅ Yes |
| Older releases | ❌ No |

Security fixes go to `main` and get released ASAP.

## What We Consider Security Issues

- Arbitrary file write via config manipulation
- Command injection via profile/rule values
- Path traversal in config file handling
- Git config corruption leading to credential leakage

## What We Don't Consider Security Issues

- Bugs requiring local filesystem access you already have
- Config file permission issues (user controls `~/.gitctx/`)
- Shell hook bugs (user explicitly opts in)

## Disclosure Timeline

1. **Day 0**: Private report
2. **Day 1-2**: Triage + confirm
3. **Day 7-30**: Fix + test
4. **Day 30+**: Public disclosure, release, credit (unless you want anonymity)

## Security Practices

- Minimal dependencies — only `rich`, `tomli`, `tomli-w` (all well-maintained)
- No `eval()`, `exec()`, `subprocess.shell=True`
- TOML parsing uses `tomli` / `tomli-w` (safe)
- File operations use `pathlib` with validation
- Git config writes use `git config` CLI (not direct file manipulation)
- No network access ever

Run locally:
```bash
pip-audit
```