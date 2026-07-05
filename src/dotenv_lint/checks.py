"""All lint checks for dotenv-lint."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from .parser import ParsedEnvFile


# ---------------------------------------------------------------------------
# Finding data structure
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    path: str
    lineno: int  # 0 means "whole-file" finding
    level: str   # "error" | "warning" | "info"
    check_name: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.lineno}: {self.level} {self.check_name} {self.message}"


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

_PLACEHOLDER_VALUES = re.compile(
    r"^(changeme|xxx+|todo|fixme|placeholder|change_me|change-me)$",
    re.IGNORECASE,
)

_UPPER_SNAKE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def check_malformed(parsed: ParsedEnvFile) -> List[Finding]:
    """Check 3 – malformed lines (no '=', or spaces around '=')."""
    findings: List[Finding] = []
    for line in parsed.lines:
        if line.is_blank or line.is_comment:
            continue
        if line.is_malformed:
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="error",
                check_name="malformed",
                message=f"Line is not a valid key=value assignment: {line.raw!r}",
            ))
        elif line.has_spaced_equals:
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="error",
                check_name="malformed",
                message=(
                    f"Spaces around '=' may break dotenv parsers: {line.raw!r}"
                ),
            ))
    return findings


def check_duplicates(parsed: ParsedEnvFile) -> List[Finding]:
    """Check 2 – duplicate keys within the same file."""
    findings: List[Finding] = []
    seen: dict = {}
    for line in parsed.lines:
        if line.key is None:
            continue
        if line.key in seen:
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="error",
                check_name="duplicate",
                message=(
                    f"Key '{line.key}' already defined at line {seen[line.key]}"
                ),
            ))
        else:
            seen[line.key] = line.lineno
    return findings


def check_blank_or_placeholder(parsed: ParsedEnvFile) -> List[Finding]:
    """Check 4 – blank or placeholder values."""
    findings: List[Finding] = []
    for line in parsed.lines:
        if line.key is None:
            continue
        val = line.value or ""
        if val == "":
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="error",
                check_name="blank-value",
                message=f"Key '{line.key}' has an empty value",
            ))
        elif _PLACEHOLDER_VALUES.match(val):
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="error",
                check_name="placeholder-value",
                message=f"Key '{line.key}' has a placeholder value: {val!r}",
            ))
    return findings


def check_key_naming(parsed: ParsedEnvFile) -> List[Finding]:
    """Check 5 – keys must be UPPER_SNAKE_CASE (warning only)."""
    findings: List[Finding] = []
    for line in parsed.lines:
        if line.key is None:
            continue
        if not _UPPER_SNAKE.match(line.key):
            findings.append(Finding(
                path=parsed.path,
                lineno=line.lineno,
                level="warning",
                check_name="key-naming",
                message=(
                    f"Key '{line.key}' is not UPPER_SNAKE_CASE"
                ),
            ))
    return findings


def check_drift(
    parsed: ParsedEnvFile,
    example: ParsedEnvFile,
) -> List[Finding]:
    """Check 1 – drift between .env and .env.example."""
    findings: List[Finding] = []

    env_keys = {
        line.key: line.lineno
        for line in parsed.lines
        if line.key is not None
    }
    example_keys = {
        line.key: line.lineno
        for line in example.lines
        if line.key is not None
    }

    # Keys present in .env but missing from .env.example
    for key, lineno in env_keys.items():
        if key not in example_keys:
            findings.append(Finding(
                path=parsed.path,
                lineno=lineno,
                level="error",
                check_name="drift",
                message=(
                    f"Key '{key}' is in {parsed.path!r} "
                    f"but missing from example file {example.path!r}"
                ),
            ))

    # Keys present in .env.example but missing from .env
    for key, lineno in example_keys.items():
        if key not in env_keys:
            findings.append(Finding(
                path=example.path,
                lineno=lineno,
                level="error",
                check_name="drift",
                message=(
                    f"Key '{key}' is in example file {example.path!r} "
                    f"but missing from {parsed.path!r}"
                ),
            ))

    return findings


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def build_summary(findings: List[Finding]) -> str:
    """Check 6 – return a human-readable summary line."""
    errors = sum(1 for f in findings if f.level == "error")
    warnings = sum(1 for f in findings if f.level == "warning")
    total = errors + warnings
    return (
        f"Summary: {total} finding(s) — "
        f"{errors} error(s), {warnings} warning(s)"
    )


# ---------------------------------------------------------------------------
# Entry point: run all checks against one file
# ---------------------------------------------------------------------------

def run_checks(
    parsed: ParsedEnvFile,
    example: Optional[ParsedEnvFile] = None,
) -> List[Finding]:
    """Run all applicable checks and return findings in line order."""
    findings: List[Finding] = []
    findings.extend(check_malformed(parsed))
    findings.extend(check_duplicates(parsed))
    findings.extend(check_blank_or_placeholder(parsed))
    findings.extend(check_key_naming(parsed))
    if example is not None:
        findings.extend(check_drift(parsed, example))
    # Sort by (path, lineno) for deterministic output
    findings.sort(key=lambda f: (f.path, f.lineno))
    return findings
