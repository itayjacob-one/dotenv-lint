"""Tests for the malformed-line check."""
from __future__ import annotations

from dotenv_lint.checks import check_malformed
from dotenv_lint.parser import parse_env_file


def test_no_malformed_lines(tmp_env):
    p = tmp_env(".env", "KEY=value\nOTHER=123\n")
    parsed = parse_env_file(str(p))
    assert check_malformed(parsed) == []


def test_malformed_no_equals(tmp_env):
    p = tmp_env(".env", "JUSTAWORD\n")
    parsed = parse_env_file(str(p))
    findings = check_malformed(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "malformed"
    assert findings[0].level == "error"
    assert findings[0].lineno == 1


def test_malformed_spaced_equals(tmp_env):
    p = tmp_env(".env", "KEY = value\n")
    parsed = parse_env_file(str(p))
    findings = check_malformed(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "malformed"
    assert findings[0].level == "error"


def test_malformed_spaced_equals_left_only(tmp_env):
    p = tmp_env(".env", "KEY =value\n")
    parsed = parse_env_file(str(p))
    findings = check_malformed(parsed)
    assert len(findings) == 1


def test_malformed_spaced_equals_right_only(tmp_env):
    p = tmp_env(".env", "KEY= value\n")
    parsed = parse_env_file(str(p))
    findings = check_malformed(parsed)
    assert len(findings) == 1


def test_comments_and_blanks_ignored(tmp_env):
    p = tmp_env(".env", "# comment\n\n")
    parsed = parse_env_file(str(p))
    assert check_malformed(parsed) == []
