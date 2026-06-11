"""Auto-detection rules for gitctx — match repos to profiles by remote URL or path."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

import tomli_w

from .profiles import CONFIG_DIR, load_profiles

RULES_FILE = CONFIG_DIR / "rules.toml"


@dataclass
class Rule:
    """A single auto-detection rule.

    Matches a repo to a profile based on remote URL pattern or directory path glob.
    """

    profile: str
    remote_pattern: str = ""
    path_glob: str = ""
    priority: int = 0  # higher = checked first; default 0

    def to_dict(self) -> Dict[str, Union[str, int]]:
        d: Dict[str, Union[str, int]] = {"profile": self.profile}
        if self.remote_pattern:
            d["remote_pattern"] = self.remote_pattern
        if self.path_glob:
            d["path_glob"] = self.path_glob
        if self.priority != 0:
            d["priority"] = self.priority
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, int]]) -> Rule:
        return cls(
            profile=str(data["profile"]),
            remote_pattern=str(data.get("remote_pattern", "")),
            path_glob=str(data.get("path_glob", "")),
            priority=int(data.get("priority", 0)),
        )


def _ensure_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_rules() -> List[Rule]:
    """Load all rules from the TOML config file, sorted by priority descending."""
    if not RULES_FILE.exists():
        return []
    with open(RULES_FILE, "rb") as f:
        raw = tomllib.load(f)
    rules = [Rule.from_dict(data) for data in raw.get("rules", [])]
    rules.sort(key=lambda r: r.priority, reverse=True)
    return rules


def save_rules(rules: List[Rule]) -> None:
    """Persist all rules to the TOML config file."""
    _ensure_config_dir()
    raw = {"rules": [r.to_dict() for r in rules]}
    with open(RULES_FILE, "wb") as f:
        tomli_w.dump(raw, f)


def add_rule(
    profile: str,
    remote_pattern: str = "",
    path_glob: str = "",
    priority: int = 0,
) -> Rule:
    """Add a new rule and save. Returns the created Rule."""
    if not remote_pattern and not path_glob:
        raise ValueError("At least one of remote_pattern or path_glob is required")
    rule = Rule(
        profile=profile,
        remote_pattern=remote_pattern,
        path_glob=path_glob,
        priority=priority,
    )
    rules = load_rules()
    rules.append(rule)
    save_rules(rules)
    return rule


def remove_rule(index: int) -> bool:
    """Remove a rule by its 1-based index. Returns True if it existed."""
    rules = load_rules()
    if index < 1 or index > len(rules):
        return False
    del rules[index - 1]
    save_rules(rules)
    return True


def _get_remote_urls(cwd: str = ".") -> List[str]:
    """Get all remote URLs for the current repo."""
    import subprocess

    result = subprocess.run(
        ["git", "remote", "-v"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    urls = []
    for line in result.stdout.strip().splitlines():
        # Format: "origin  https://github.com/user/repo.git (fetch)"
        parts = line.split()
        if len(parts) >= 2:
            urls.append(parts[1])
    return list(set(urls))  # deduplicate


def _match_remote(pattern: str, urls: List[str]) -> bool:
    """Check if any remote URL matches the pattern (substring or regex)."""
    for url in urls:
        # Try as a simple substring match first
        if pattern in url:
            return True
        # Try as a regex
        try:
            if re.search(pattern, url):
                return True
        except re.error:
            pass
    return False


def _match_path(glob_pattern: str, cwd: str = ".") -> bool:
    """Check if the current directory matches the path glob pattern."""
    try:
        repo_path = Path(cwd).resolve()
        return repo_path in Path(".").resolve().glob(glob_pattern) or bool(
            Path(cwd).resolve().glob(glob_pattern)
        )
    except (OSError, ValueError):
        return False


def auto_detect(cwd: str = ".") -> Optional[str]:
    """Auto-detect which profile to use based on rules.

    Checks rules in priority order. Returns the profile alias
    if a rule matches, or None if no rules match.
    """
    rules = load_rules()
    if not rules:
        return None

    urls = _get_remote_urls(cwd)
    resolved_cwd = str(Path(cwd).resolve())

    for rule in rules:
        matched = False
        if rule.remote_pattern and _match_remote(rule.remote_pattern, urls):
            matched = True
        if rule.path_glob and _match_path(rule.path_glob, resolved_cwd):
            matched = True

        # If both patterns are specified, both must match (AND logic)
        if rule.remote_pattern and rule.path_glob:
            matched = _match_remote(rule.remote_pattern, urls) and _match_path(
                rule.path_glob, resolved_cwd
            )

        if matched:
            # Verify the profile actually exists
            profiles = load_profiles()
            if rule.profile in profiles:
                return rule.profile
    return None
