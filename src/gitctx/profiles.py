"""Profile management for gitctx — load, save, add, remove profiles."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

import tomli_w

CONFIG_DIR = Path.home() / ".gitctx"
PROFILES_FILE = CONFIG_DIR / "profiles.toml"

GIT_USER_KEYS = ("name", "email", "signingkey")


@dataclass
class Profile:
    """A named Git user configuration."""

    name: str
    email: str
    signingkey: str = ""

    def to_dict(self) -> dict[str, str]:
        d = {"name": self.name, "email": self.email}
        if self.signingkey:
            d["signingkey"] = self.signingkey
        return d

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Profile:
        return cls(
            name=data["name"],
            email=data["email"],
            signingkey=data.get("signingkey", ""),
        )


def _ensure_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_profiles() -> dict[str, Profile]:
    """Load all profiles from the TOML config file."""
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE, "rb") as f:
        raw = tomllib.load(f)
    return {name: Profile.from_dict(data) for name, data in raw.items()}


def save_profiles(profiles: dict[str, Profile]) -> None:
    """Persist all profiles to the TOML config file."""
    _ensure_config_dir()
    raw = {name: p.to_dict() for name, p in profiles.items()}
    with open(PROFILES_FILE, "wb") as f:
        tomli_w.dump(raw, f)


def add_profile(alias: str, name: str, email: str, signingkey: str = "") -> Profile:
    """Add or replace a profile and save."""
    profiles = load_profiles()
    profile = Profile(name=name, email=email, signingkey=signingkey)
    profiles[alias] = profile
    save_profiles(profiles)
    return profile


def remove_profile(alias: str) -> bool:
    """Remove a profile by alias. Returns True if it existed."""
    profiles = load_profiles()
    if alias not in profiles:
        return False
    del profiles[alias]
    save_profiles(profiles)
    return True


def get_profile(alias: str) -> Optional[Profile]:
    """Look up a single profile by alias."""
    return load_profiles().get(alias)


def list_profiles() -> dict[str, Profile]:
    """Return all profiles."""
    return load_profiles()
