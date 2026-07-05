"""Parser for .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnvLine:
    """Represents a single parsed line from a .env file."""
    lineno: int
    raw: str
    is_blank: bool = False
    is_comment: bool = False
    key: Optional[str] = None
    value: Optional[str] = None
    # True when the line has content but could not be parsed as key=value
    is_malformed: bool = False
    # True when there are spaces around the '=' sign
    has_spaced_equals: bool = False


@dataclass
class ParsedEnvFile:
    """All lines from a parsed .env file."""
    path: str
    lines: List[EnvLine] = field(default_factory=list)


def parse_env_file(path: str) -> ParsedEnvFile:
    """Read *path* and return a ParsedEnvFile."""
    result = ParsedEnvFile(path=path)
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            result.lines.append(_parse_line(lineno, line))
    return result


def _parse_line(lineno: int, raw: str) -> EnvLine:
    stripped = raw.strip()

    if stripped == "":
        return EnvLine(lineno=lineno, raw=raw, is_blank=True)

    if stripped.startswith("#"):
        return EnvLine(lineno=lineno, raw=raw, is_comment=True)

    # Check for spaces around '=' (e.g. KEY = value or KEY =value or KEY= value)
    # We look for an '=' in the raw (stripped) content.
    if "=" not in stripped:
        return EnvLine(lineno=lineno, raw=raw, is_malformed=True)

    # Split on the FIRST '=' only.
    key_part, _, value_part = stripped.partition("=")

    # Detect stray spaces: key_part ends with space OR value_part starts with space
    # (but value_part starting with space is allowed by some parsers; we flag it as
    # the assignment spec says "stray spaces around '=' that break dotenv parsers").
    has_spaced_equals = key_part != key_part.rstrip() or value_part != value_part.lstrip()

    # Normalise for storage (we keep the raw for reporting)
    key = key_part.strip()
    value = value_part.strip()

    if not key:
        return EnvLine(lineno=lineno, raw=raw, is_malformed=True)

    return EnvLine(
        lineno=lineno,
        raw=raw,
        key=key,
        value=value,
        has_spaced_equals=has_spaced_equals,
    )
