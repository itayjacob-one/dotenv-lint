"""Command-line interface for dotenv-lint."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .checks import Finding, build_summary, run_checks
from .parser import ParsedEnvFile, parse_env_file


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envfile-lint",
        description="Lint one or more .env files.",
    )
    p.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        default=[".env"],
        help="Path(s) to .env file(s) to lint (default: .env)",
    )
    p.add_argument(
        "--example",
        "-e",
        metavar="PATH",
        default=None,
        help="Path to a .env.example file for drift checking",
    )
    return p


def lint_files(
    paths: List[str],
    example_path: Optional[str] = None,
    out=None,
) -> int:
    """
    Lint *paths*, optionally against *example_path*.
    Writes output to *out* (default: sys.stdout).
    Returns the exit code (0 or 1).
    """
    if out is None:
        out = sys.stdout

    example_parsed: Optional[ParsedEnvFile] = None
    if example_path is not None:
        try:
            example_parsed = parse_env_file(example_path)
        except OSError as exc:
            print(f"envfile-lint: error: cannot open example file: {exc}", file=sys.stderr)
            return 2

    all_findings: List[Finding] = []

    for path in paths:
        try:
            parsed = parse_env_file(path)
        except OSError as exc:
            print(f"envfile-lint: error: cannot open file: {exc}", file=sys.stderr)
            return 2
        findings = run_checks(parsed, example=example_parsed)
        all_findings.extend(findings)

    for finding in all_findings:
        print(str(finding), file=out)

    print(build_summary(all_findings), file=out)

    has_errors = any(f.level == "error" for f in all_findings)
    return 1 if has_errors else 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    exit_code = lint_files(
        paths=args.files,
        example_path=args.example,
    )
    sys.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    main()
