"""Tests for gitctx gitutils module."""

import subprocess

import pytest
from gitctx.profiles import Profile


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary Git repository."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "--local", "user.name", "Default"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.email", "default@test.com"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return repo


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirect profile storage to a temp dir."""
    config_dir = tmp_path / ".gitctx"
    config_dir.mkdir()
    monkeypatch.setattr("gitctx.profiles.CONFIG_DIR", config_dir)
    monkeypatch.setattr("gitctx.profiles.PROFILES_FILE", config_dir / "profiles.toml")
    yield config_dir


class TestGitUtils:
    def test_is_git_repo_true(self, git_repo):
        from gitctx.gitutils import is_git_repo

        assert is_git_repo(str(git_repo)) is True

    def test_is_git_repo_false(self, tmp_path):
        from gitctx.gitutils import is_git_repo

        not_a_repo = tmp_path / "empty"
        not_a_repo.mkdir()
        assert is_git_repo(str(not_a_repo)) is False

    def test_apply_profile(self, git_repo):
        from gitctx.gitutils import apply_profile, get_current_config

        profile = Profile(name="Jane", email="jane@work.com", signingkey="KEY1")
        apply_profile(profile, str(git_repo))

        cfg = get_current_config(str(git_repo))
        assert cfg["name"] == "Jane"
        assert cfg["email"] == "jane@work.com"
        assert cfg["signingkey"] == "KEY1"

    def test_apply_profile_no_signingkey(self, git_repo):
        from gitctx.gitutils import apply_profile, get_current_config

        profile = Profile(name="Jane", email="jane@home.com")
        apply_profile(profile, str(git_repo))

        cfg = get_current_config(str(git_repo))
        assert cfg["name"] == "Jane"
        assert cfg["email"] == "jane@home.com"

    def test_detect_profile(self, git_repo):
        from gitctx.gitutils import apply_profile, detect_profile
        from gitctx.profiles import add_profile

        add_profile("work", name="Jane", email="jane@work.com", signingkey="KEY1")

        profile = Profile(name="Jane", email="jane@work.com", signingkey="KEY1")
        apply_profile(profile, str(git_repo))

        alias = detect_profile(str(git_repo))
        assert alias == "work"

    def test_detect_no_match(self, git_repo):
        from gitctx.gitutils import apply_profile, detect_profile
        from gitctx.profiles import add_profile

        add_profile("work", name="Jane", email="jane@work.com")

        # Set config that doesn't match any profile
        profile = Profile(name="Other", email="other@test.com")
        apply_profile(profile, str(git_repo))

        alias = detect_profile(str(git_repo))
        assert alias is None
