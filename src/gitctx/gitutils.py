"""Git config operations — read and write local user settings."""

import subprocess

from .profiles import Profile


def _git(*args: str, cwd: str | None = None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_config_set(key: str, value: str, cwd: str) -> None:
    """Set a local git config value."""
    subprocess.run(
        ["git", "config", "--local", key, value],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def _git_config_unset(key: str, cwd: str) -> None:
    """Unset a local git config value (ignores failure if not set)."""
    subprocess.run(
        ["git", "config", "--local", "--unset", key],
        cwd=cwd,
        capture_output=True,
    )


def _git_config_get(key: str, cwd: str) -> str | None:
    """Get a local git config value, or None if unset."""
    result = subprocess.run(
        ["git", "config", "--local", "--get", key],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_git_repo(path: str = ".") -> bool:
    """Check if the given path is inside a Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=path,
        capture_output=True,
    )
    return result.returncode == 0


def apply_profile(profile: Profile, cwd: str = ".") -> None:
    """Write a profile's settings to the local Git config."""
    _git_config_set("user.name", profile.name, cwd)
    _git_config_set("user.email", profile.email, cwd)
    if profile.signingkey:
        _git_config_set("user.signingkey", profile.signingkey, cwd)
    else:
        _git_config_unset("user.signingkey", cwd)


def detect_profile(cwd: str = ".") -> str | None:
    """Detect which profile is active in the current repo by matching config values.

    Returns the profile alias if a match is found, else None.
    """
    from .profiles import load_profiles

    name = _git_config_get("user.name", cwd)
    email = _git_config_get("user.email", cwd)
    signingkey = _git_config_get("user.signingkey", cwd) or ""

    if name is None and email is None:
        return None

    profiles = load_profiles()
    for alias, p in profiles.items():
        if p.name == name and p.email == email and p.signingkey == signingkey:
            return alias
    return None


def get_current_config(cwd: str = ".") -> dict[str, str | None]:
    """Return the current local git user config."""
    return {
        "name": _git_config_get("user.name", cwd),
        "email": _git_config_get("user.email", cwd),
        "signingkey": _git_config_get("user.signingkey", cwd),
    }
