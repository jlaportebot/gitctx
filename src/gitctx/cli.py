"""Command-line interface for gitctx."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.table import Table

from . import __version__
from .gitutils import apply_profile, detect_profile, get_current_config, is_git_repo
from .profiles import add_profile, get_profile, list_profiles, remove_profile
from .rules import add_rule, auto_detect, load_rules, remove_rule as remove_rule_func

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
    console.print(f"  name: {profile.name}")
    console.print(f"  email: {profile.email}")
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
    console.print(f"  name: {profile.name}")
    console.print(f"  email: {profile.email}")
    if profile.signingkey:
        console.print(f"  key: {profile.signingkey}")
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
                console.print(f"  user.name: {cfg['name']}")
            if cfg["email"]:
                console.print(f"  user.email: {cfg['email']}")
            if cfg["signingkey"]:
                console.print(f"  user.signingkey: {cfg['signingkey']}")
        else:
            console.print("[dim]No local user config set in this repo.[/]")
    return 0


def _cmd_auto(args: argparse.Namespace) -> int:
    """Auto-detect and apply the right profile for the current directory."""
    cwd = args.directory or "."
    if not is_git_repo(cwd):
        err_console.print("[red]✘ Not inside a Git repository[/]")
        return 1

    alias = auto_detect(cwd)
    if alias is None:
        err_console.print("[yellow]⚠ No auto-detection rule matches this repo.[/]")
        err_console.print(
            "[dim]Add rules with: gitctx rule add --profile <name> --remote <pattern>[/]"
        )
        return 1

    profile = get_profile(alias)
    if profile is None:
        err_console.print(
            f"[red]✘ Rule matched profile '{alias}' but that profile doesn't exist.[/]"
        )
        return 1

    if not args.dry_run:
        apply_profile(profile, cwd)

    if args.dry_run:
        console.print(f"[cyan] Would apply profile[/] [bold]{alias}[/] (dry run)")
    else:
        console.print(f"[green]✔ Auto-applied profile[/] [bold]{alias}[/]")
    console.print(f"  name: {profile.name}")
    console.print(f"  email: {profile.email}")
    if profile.signingkey:
        console.print(f"  key: {profile.signingkey}")
    return 0


def _cmd_rule_add(args: argparse.Namespace) -> int:
    """Add an auto-detection rule."""
    if not args.remote and not args.path:
        err_console.print("[red]✘ At least one of --remote or --path is required[/]")
        return 1

    try:
        rule = add_rule(
            profile=args.profile,
            remote_pattern=args.remote or "",
            path_glob=args.path or "",
            priority=args.priority,
        )
    except ValueError as e:
        err_console.print(f"[red]✘ {e}[/]")
        return 1

    console.print(f"[green]✔ Added rule for profile[/] [bold]{args.profile}[/]")
    if rule.remote_pattern:
        console.print(f"  remote: {rule.remote_pattern}")
    if rule.path_glob:
        console.print(f"  path: {rule.path_glob}")
    if rule.priority:
        console.print(f"  priority: {rule.priority}")
    return 0


def _cmd_rule_list(args: argparse.Namespace) -> int:
    """List all auto-detection rules."""
    rules = load_rules()
    if not rules:
        console.print(
            "[dim]No auto-detection rules. Use 'gitctx rule add' to create one.[/]"
        )
        return 0

    table = Table(title="Auto-Detection Rules", show_header=True)
    table.add_column("#", style="dim")
    table.add_column("Profile", style="bold cyan")
    table.add_column("Remote Pattern")
    table.add_column("Path Glob")
    table.add_column("Priority")

    for i, r in enumerate(rules, 1):
        table.add_row(
            str(i),
            r.profile,
            r.remote_pattern or "—",
            r.path_glob or "—",
            str(r.priority),
        )

    console.print(table)
    return 0


def _cmd_rule_remove(args: argparse.Namespace) -> int:
    """Remove an auto-detection rule by index."""
    if remove_rule_func(args.index):
        console.print(f"[green]✔ Removed rule #{args.index}[/]")
        return 0
    err_console.print(f"[red]✘ Rule #{args.index} not found[/]")
    return 1


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
    p_use.add_argument(
        "--directory", "-C", default=".", help="Target directory (default: .)"
    )
    p_use.set_defaults(func=_cmd_use)

    # current
    p_cur = sub.add_parser("current", help="Show the active profile")
    p_cur.add_argument(
        "--directory", "-C", default=".", help="Target directory (default: .)"
    )
    p_cur.add_argument(
        "--quiet", "-q", action="store_true", help="Only print the alias name"
    )
    p_cur.set_defaults(func=_cmd_current)

    # auto
    p_auto = sub.add_parser("auto", help="Auto-detect and apply the right profile")
    p_auto.add_argument(
        "--directory", "-C", default=".", help="Target directory (default: .)"
    )
    p_auto.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be applied without changing config",
    )
    p_auto.set_defaults(func=_cmd_auto)

    # rule (subcommand group)
    p_rule = sub.add_parser("rule", help="Manage auto-detection rules")
    rule_sub = p_rule.add_subparsers(dest="rule_command", help="Rule commands")

    # rule add
    p_rule_add = rule_sub.add_parser("add", help="Add an auto-detection rule")
    p_rule_add.add_argument(
        "--profile", "-p", required=True, help="Profile to apply when rule matches"
    )
    p_rule_add.add_argument(
        "--remote", "-r", default="", help="Remote URL pattern (substring or regex)"
    )
    p_rule_add.add_argument(
        "--path", "-P", default="", help="Directory path glob pattern"
    )
    p_rule_add.add_argument(
        "--priority", default=0, type=int, help="Rule priority (higher = checked first)"
    )
    p_rule_add.set_defaults(func=_cmd_rule_add)

    # rule list
    p_rule_ls = rule_sub.add_parser(
        "list", help="List all auto-detection rules", aliases=["ls"]
    )
    p_rule_ls.set_defaults(func=_cmd_rule_list)

    # rule remove
    p_rule_rm = rule_sub.add_parser(
        "remove", help="Remove a rule by index", aliases=["rm"]
    )
    p_rule_rm.add_argument(
        "index", type=int, help="Rule number to remove (from 'rule list')"
    )
    p_rule_rm.set_defaults(func=_cmd_rule_remove)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # Handle the 'rule' subcommand group
    if args.command == "rule":
        if not args.rule_command:
            parser.parse_args(["rule", "--help"])
            return 0
        return args.func(args)

    return args.func(args)


def cli_entry() -> None:
    """Console script entry point."""
    raise SystemExit(main())


# Make `gitctx.cli:main` work as entry point
main.__module__ = "gitctx.cli"
