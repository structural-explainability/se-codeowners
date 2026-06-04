"""Command-line interface for se-codeowners.

Two subcommands:

* ``generate`` renders CODEOWNERS to stdout, or to ``--output``.
* ``check`` compares an existing CODEOWNERS against what would be generated
  and exits non-zero on drift, for use in pre-commit or CI.
"""

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, TextIO

from .errors import SurfacesError
from .generate import render_codeowners
from .load import DEFAULT_SURFACES_PATH, load_surfaces

DEFAULT_CODEOWNERS_PATH = Path(".github/CODEOWNERS")


@dataclass(frozen=True)
class AppContext:
    """Context for CLI command handlers."""

    stdout: TextIO
    stderr: TextIO
    load_surfaces: Callable[[Path], Any]
    render_codeowners: Callable[[Any, bool], str]


def default_context() -> AppContext:
    """Return the default application context, using real I/O and the real loader and renderer."""
    return AppContext(
        stdout=sys.stdout,
        stderr=sys.stderr,
        load_surfaces=load_surfaces,
        render_codeowners=lambda surfaces, strict: render_codeowners(
            surfaces,
            strict=strict,
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="se-codeowners",
        description="Generate a CODEOWNERS file from accountability surfaces.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    command_generate_configure(subparsers)
    command_check_configure(subparsers)

    return parser


def command_check_configure(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Configure the 'check' subcommand."""
    parser = subparsers.add_parser(
        "check",
        help="verify an existing CODEOWNERS is up to date",
    )
    parser.add_argument("--surfaces", type=Path, default=DEFAULT_SURFACES_PATH)
    parser.add_argument("--codeowners", type=Path, default=DEFAULT_CODEOWNERS_PATH)
    parser.add_argument("--strict", action="store_true")
    parser.set_defaults(handler=command_check_run)


def command_check_run(args: argparse.Namespace, ctx: AppContext) -> int:
    """Handle the 'check' subcommand."""
    expected = command_generate_run_helper(
        ctx,
        args.surfaces,
        strict=args.strict,
    )

    try:
        actual = args.codeowners.read_text(encoding="utf-8")
    except OSError:
        print(
            f"se-codeowners: {args.codeowners} is missing; "
            "run 'se-codeowners generate'",
            file=ctx.stderr,
        )
        return 1

    if actual != expected:
        print(
            f"se-codeowners: {args.codeowners} is out of date; "
            "regenerate with 'se-codeowners generate'",
            file=ctx.stderr,
        )
        return 1

    print(f"se-codeowners: {args.codeowners} is up to date", file=ctx.stderr)
    return 0


def command_generate_configure(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Configure the 'generate' subcommand."""
    parser = subparsers.add_parser(
        "generate",
        help="render CODEOWNERS from surfaces.toml",
    )
    parser.add_argument("--surfaces", type=Path, default=DEFAULT_SURFACES_PATH)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write here instead of stdout",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail on placeholder handles",
    )
    parser.set_defaults(handler=command_generate_run)


def command_generate_run(args: argparse.Namespace, ctx: AppContext) -> int:
    """Handle the 'generate' subcommand."""
    content = command_generate_run_helper(
        ctx,
        args.surfaces,
        strict=args.strict,
    )

    if args.output is None:
        ctx.stdout.write(content)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"se-codeowners: wrote {args.output}", file=ctx.stderr)
    return 0


def command_generate_run_helper(
    ctx: AppContext,
    surfaces_path: Path,
    *,
    strict: bool,
) -> str:
    """Render the expected CODEOWNERS content."""
    surfaces = ctx.load_surfaces(surfaces_path)
    return ctx.render_codeowners(surfaces, strict)


def main(
    argv: Sequence[str] | None = None,
    *,
    context: AppContext | None = None,
) -> int:
    """Entry point for the CLI."""
    ctx = context or default_context()
    args = build_parser().parse_args(argv)

    try:
        return args.handler(args, ctx)
    except SurfacesError as exc:
        print(f"se-codeowners: error: {exc}", file=ctx.stderr)
        return 2
