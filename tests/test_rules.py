"""Tests for gitctx rules module — auto-detection rules."""

import subprocess

import pytest

from gitctx.profiles import add_profile


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirect profile and rules storage to temp dirs."""
    config_dir = tmp_path / ".gitctx"
    config_dir.mkdir()
    monkeypatch.setattr("gitctx.profiles.CONFIG_DIR", config_dir)
    monkeypatch.setattr("gitctx.profiles.PROFILES_FILE", config_dir / "profiles.toml")
    monkeypatch.setattr("gitctx.rules.CONFIG_DIR", config_dir)
    monkeypatch.setattr("gitctx.rules.RULES_FILE", config_dir / "rules.toml")
    yield config_dir


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary Git repository with a remote."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/myorg/myrepo.git"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.name", "Test"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--local", "user.email", "test@test.com"],
        cwd=str(repo),
        check=True,
        capture_output=True,
    )
    return repo


class TestRule:
    def test_to_dict_minimal(self):
        from gitctx.rules import Rule

        r = Rule(profile="work", remote_pattern="github.com/myorg")
        d = r.to_dict()
        assert d["profile"] == "work"
        assert d["remote_pattern"] == "github.com/myorg"

    def test_to_dict_full(self):
        from gitctx.rules import Rule

        r = Rule(
            profile="work", remote_pattern="org", path_glob="/home/*/work", priority=5
        )
        d = r.to_dict()
        assert d["priority"] == 5
        assert d["path_glob"] == "/home/*/work"

    def test_from_dict(self):
        from gitctx.rules import Rule

        r = Rule.from_dict(
            {"profile": "oss", "remote_pattern": "github.com", "priority": 10}
        )
        assert r.profile == "oss"
        assert r.priority == 10

    def test_roundtrip(self):
        from gitctx.rules import Rule

        r = Rule(profile="p", remote_pattern="x", path_glob="y", priority=3)
        d = r.to_dict()
        r2 = Rule.from_dict(d)
        assert r2 == r


class TestRuleStorage:
    def test_load_empty(self, tmp_config):
        from gitctx.rules import load_rules

        assert load_rules() == []

    def test_add_and_load(self, tmp_config):
        from gitctx.rules import add_rule, load_rules

        add_rule("work", remote_pattern="github.com/myorg")
        rules = load_rules()
        assert len(rules) == 1
        assert rules[0].profile == "work"

    def test_add_multiple(self, tmp_config):
        from gitctx.rules import add_rule, load_rules

        add_rule("work", remote_pattern="github.com/company")
        add_rule("personal", remote_pattern="github.com/jlaporte")
        rules = load_rules()
        assert len(rules) == 2

    def test_priority_sorting(self, tmp_config):
        from gitctx.rules import add_rule, load_rules

        add_rule("low", remote_pattern="a", priority=1)
        add_rule("high", remote_pattern="b", priority=10)
        add_rule("mid", remote_pattern="c", priority=5)
        rules = load_rules()
        assert rules[0].profile == "high"
        assert rules[1].profile == "mid"
        assert rules[2].profile == "low"

    def test_remove_rule(self, tmp_config):
        from gitctx.rules import add_rule, remove_rule, load_rules

        add_rule("work", remote_pattern="x")
        add_rule("personal", remote_pattern="y")
        assert remove_rule(1) is True
        rules = load_rules()
        assert len(rules) == 1
        assert rules[0].profile == "personal"

    def test_remove_invalid_index(self, tmp_config):
        from gitctx.rules import remove_rule

        assert remove_rule(99) is False

    def test_add_requires_pattern(self, tmp_config):
        from gitctx.rules import add_rule

        with pytest.raises(ValueError):
            add_rule("work")


class TestAutoDetect:
    def test_detect_by_remote_url(self, git_repo, tmp_config):
        from gitctx.rules import add_rule, auto_detect

        add_profile("work", name="Jane", email="jane@work.com")
        add_rule("work", remote_pattern="github.com/myorg")
        result = auto_detect(str(git_repo))
        assert result == "work"

    def test_detect_no_match(self, git_repo, tmp_config):
        from gitctx.rules import add_rule, auto_detect

        add_profile("work", name="Jane", email="jane@work.com")
        add_rule("work", remote_pattern="gitlab.com")
        result = auto_detect(str(git_repo))
        assert result is None

    def test_detect_no_rules(self, git_repo, tmp_config):
        from gitctx.rules import auto_detect

        result = auto_detect(str(git_repo))
        assert result is None

    def test_detect_profile_missing(self, git_repo, tmp_config):
        from gitctx.rules import add_rule, auto_detect

        add_rule("nonexistent", remote_pattern="github.com/myorg")
        # Profile doesn't exist, so auto_detect should return None
        result = auto_detect(str(git_repo))
        assert result is None

    def test_detect_regex_pattern(self, git_repo, tmp_config):
        from gitctx.rules import add_rule, auto_detect

        add_profile("work", name="Jane", email="jane@work.com")
        add_rule("work", remote_pattern=r"github\.com/my\w+/")
        result = auto_detect(str(git_repo))
        assert result == "work"

    def test_priority_order(self, git_repo, tmp_config):
        from gitctx.rules import add_rule, auto_detect

        add_profile("low", name="Lo", email="lo@test.com")
        add_profile("high", name="Hi", email="hi@test.com")
        add_rule("low", remote_pattern="github.com", priority=1)
        add_rule("high", remote_pattern="github.com", priority=10)
        result = auto_detect(str(git_repo))
        assert result == "high"
