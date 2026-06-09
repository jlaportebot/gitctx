"""Tests for gitctx profiles module."""

import pytest

# We need to redirect the profiles module to use a temp dir
from gitctx.profiles import Profile


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirect profile storage to a temp directory for each test."""
    config_dir = tmp_path / ".gitctx"
    config_dir.mkdir()
    monkeypatch.setattr("gitctx.profiles.CONFIG_DIR", config_dir)
    monkeypatch.setattr("gitctx.profiles.PROFILES_FILE", config_dir / "profiles.toml")
    yield config_dir


class TestProfile:
    def test_to_dict_minimal(self):
        p = Profile(name="Ada", email="ada@example.com")
        d = p.to_dict()
        assert d == {"name": "Ada", "email": "ada@example.com"}

    def test_to_dict_with_signingkey(self):
        p = Profile(name="Ada", email="ada@example.com", signingkey="ABC")
        d = p.to_dict()
        assert d == {"name": "Ada", "email": "ada@example.com", "signingkey": "ABC"}

    def test_from_dict_minimal(self):
        p = Profile.from_dict({"name": "Bob", "email": "bob@x.com"})
        assert p.name == "Bob"
        assert p.email == "bob@x.com"
        assert p.signingkey == ""

    def test_from_dict_with_key(self):
        p = Profile.from_dict(
            {"name": "Bob", "email": "bob@x.com", "signingkey": "XYZ"}
        )
        assert p.signingkey == "XYZ"

    def test_roundtrip(self):
        p = Profile(name="Eve", email="eve@y.com", signingkey="K1")
        d = p.to_dict()
        p2 = Profile.from_dict(d)
        assert p2 == p


class TestProfileStorage:
    def test_load_empty(self, tmp_config):
        from gitctx.profiles import load_profiles

        profiles = load_profiles()
        assert profiles == {}

    def test_add_and_load(self, tmp_config):
        from gitctx.profiles import add_profile, load_profiles

        add_profile("work", name="Jane", email="jane@work.com", signingkey="KEY1")
        profiles = load_profiles()
        assert "work" in profiles
        assert profiles["work"].email == "jane@work.com"

    def test_add_multiple(self, tmp_config):
        from gitctx.profiles import add_profile, load_profiles

        add_profile("work", name="Jane", email="jane@work.com")
        add_profile("personal", name="Jane", email="jane@home.com")
        profiles = load_profiles()
        assert len(profiles) == 2
        assert profiles["personal"].email == "jane@home.com"

    def test_add_overwrites(self, tmp_config):
        from gitctx.profiles import add_profile, load_profiles

        add_profile("work", name="Old", email="old@work.com")
        add_profile("work", name="New", email="new@work.com")
        profiles = load_profiles()
        assert profiles["work"].name == "New"

    def test_remove_existing(self, tmp_config):
        from gitctx.profiles import add_profile, remove_profile, load_profiles

        add_profile("work", name="Jane", email="jane@work.com")
        assert remove_profile("work") is True
        assert load_profiles() == {}

    def test_remove_nonexistent(self, tmp_config):
        from gitctx.profiles import remove_profile

        assert remove_profile("ghost") is False

    def test_get_profile(self, tmp_config):
        from gitctx.profiles import add_profile, get_profile

        add_profile("oss", name="Jane", email="jane@oss.com", signingkey="S1")
        p = get_profile("oss")
        assert p is not None
        assert p.signingkey == "S1"

    def test_get_profile_missing(self, tmp_config):
        from gitctx.profiles import get_profile

        assert get_profile("missing") is None

    def test_persistence_across_loads(self, tmp_config):
        from gitctx.profiles import add_profile, load_profiles

        add_profile("work", name="Jane", email="jane@work.com")
        # Reload from disk
        profiles = load_profiles()
        assert "work" in profiles
