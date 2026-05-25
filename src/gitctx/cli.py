"""Command-line interface for gitctx."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.table import Table

from . import __version__
from .gitutils import apply_profile, detect_profile, get_current_config, is_git_repo
from .profiles import Profile, add_profile, get_profile, list_profiles, remove_profile

console = Console()
err_console = Console(stderr=True)


def _cmd_add(args: argparse.Namespace) -> int:
    """Add a new profile."""
    profile = add_profile(
        alias=args.alias,
        name=args.name,
        email=args.email,
        signingkey=args.signingkey or "",
    )
    console.print(f"[green]✔ Added profile[/] [bold]{args.alias}[/]")
    console.print(f"  name:       {profile.name}")
    console.print(f"  email:      {profile.email}")
    if profile.signingkey:
        console.print(f"  signingkey: {profile.signingkey}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    """Remove a profile."""
    if remove_profile(args.alias):
        console.print(f"[green]✔ Removed profile[/] [bold]{args.alias}[/]")
        return 0
    err_console.print(f"[red]✘ Profile '{args.alias}' not found[/]")
    return 1


def _cmd_list(args: argparse.Namespace) -> int:
    """List all profiles."""
    profiles = list_profiles()
    if not profiles:
        console.print("[dim]No profiles configured. Use 'gitctx add' to create one.[/]")
        return 0

    table = Table(title="Git Context Profiles", show_header=True)
    table.add_column("Alias", style="bold cyan")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Signing Key")

    for alias, p in sorted(profiles.items()):
        table.add_row(alias, p.name, p.email, p.signingkey or "—")

    console.print(table)
    return 0


def _cmd_use(args: argparse.Namespace) -> int:
    """Apply a profile to the current directory."""
    profile = get_profile(args.alias)
    if profile is None:
        err_console.print(f"[red]✘ Profile '{args.alias}' not found[/]")
        return 1

    cwd = args.directory or "."
    if not is_git_repo(cwd):
        err_console.print("[red]✘ Not inside a Git repository[/]")
        return 1

    apply_profile(profile, cwd)
    console.print(f"[green]✔ Using profile[/] [bold]{args.alias}[/] in {cwd}")
    console.print(f"  name:  {profile.name}")
    console.print(f"  email: {profile.email}")
    if profile.signingkey:
        console.print(f"  key:   {profile.signingkey}")
    return 0


def _cmd_current(args: argparse.Namespace) -> int:
    """Show the active profile for the current directory."""
    cwd = args.directory or "."
    alias = detect_profile(cwd)

    if args.quiet:
        if alias:
            print(alias)
        return 0 if alias else 1

    if alias:
        console.print(f"[bold green]{alias}[/]")
    else:
        # Show raw config even if no profile matches
        cfg = get_current_config(cwd)
        if cfg["name"] or cfg["email"]:
            console.print("[dim]No matching profile. Current local config:[/]")
            if cfg["name"]:
                console.print(f"  user.name:       {cfg['name']}")
            if cfg["email"]:
                console.print(f"  user.email:      {cfg['email']}")
            if cfg["signingkey"]:
                console.print(f"  user.signingkey: {cfg['signingkey']}")
        else:
            console.print("[dim]No local user config set in this repo.[/]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="gitctx",
        description="Switch Git user configs per directory.",
    )
    parser.add_argument("--version", action="version", version=f"gitctx {__version__}")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # add
    p_add = sub.add_parser("add", help="Add a new profile")
    p_add.add_argument("alias", help="Profile name (e.g. work, personal)")
    p_add.add_argument("--name", "-n", required=True, help="user.name value")
    p_add.add_argument("--email", "-e", required=True, help="user.email value")
    p_add.add_argument("--signingkey", "-s", default="", help="user.signingKey value")
    p_add.set_defaults(func=_cmd_add)

    # remove
    p_rm = sub.add_parser("remove", help="Remove a profile", aliases=["rm"])
    p_rm.add_argument("alias", help="Profile name to remove")
    p_rm.set_defaults(func=_cmd_remove)

    # list
    p_ls = sub.add_parser("list", help="List all profiles", aliases=["ls"])
    p_ls.set_defaults(func=_cmd_list)

    # use
    p_use = sub.add_parser("use", help="Apply a profile to the current directory")
    p_use.add_argument("alias", help="Profile name to activate")
    p_use.add_argument("--directory", "-C", default=".", help="Target directory (default: .)")
    p_use.set_defaults(func=_cmd_use)

    # current
    p_cur = sub.add_parser("current", help="Show the active profile")
    p_cur.add_argument("--directory", "-C", default=".", help="Target directory (default: .)")
    p_cur.add_argument("--quiet", "-q", action="store_true", help="Only print the alias name")
    p_cur.set_defaults(func=_cmd_current)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


def cli_entry() -> None:
    """Console script entry point."""
    raise SystemExit(main())


# Make `gitctx.cli:main` work as entry point
main.__module__ = "gitctx.cli"
