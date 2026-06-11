"""Tests for gitctx CLI."""

import pytest

from gitctx.cli import main


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirect profile storage to a temp dir."""
    config_dir = tmp_path / ".gitctx"
    config_dir.mkdir()
    monkeypatch.setattr("gitctx.profiles.CONFIG_DIR", config_dir)
    monkeypatch.setattr("gitctx.profiles.PROFILES_FILE", config_dir / "profiles.toml")
    yield config_dir


class TestAddCommand:
    def test_add_profile(self, tmp_config, capsys):
        rc = main(["add", "work", "--name", "Jane", "--email", "jane@work.com"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "work" in out
        assert "jane@work.com" in out

    def test_add_with_signingkey(self, tmp_config, capsys):
        rc = main(
            [
                "add",
                "oss",
                "--name",
                "Jane",
                "--email",
                "jane@oss.com",
                "--signingkey",
                "ABC",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "ABC" in out

    def test_add_requires_name_and_email(self, tmp_config):
        with pytest.raises(SystemExit):
            main(["add", "test"])


class TestRemoveCommand:
    def test_remove_existing(self, tmp_config, capsys):
        main(["add", "work", "--name", "Jane", "--email", "jane@work.com"])
        rc = main(["remove", "work"])
        assert rc == 0

    def test_remove_nonexistent(self, tmp_config):
        rc = main(["remove", "ghost"])
        assert rc == 1


class TestListCommand:
    def test_list_empty(self, tmp_config, capsys):
        rc = main(["list"])
        assert rc == 0

    def test_list_with_profiles(self, tmp_config, capsys):
        main(["add", "work", "--name", "Jane", "--email", "jane@work.com"])
        main(["add", "home", "--name", "Jane", "--email", "jane@home.com"])
        rc = main(["list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "work" in out
        assert "home" in out


class TestCurrentCommand:
    def test_current_no_config(self, capsys):
        rc = main(["current"])
        # Not in a git repo or no config set
        assert rc in (0, 1)


class TestUseCommand:
    def test_use_missing_profile(self, tmp_config):
        rc = main(["use", "ghost"])
        assert rc == 1


class TestNoCommand:
    def test_no_args_shows_help(self, capsys):
        rc = main([])
        assert rc == 0
