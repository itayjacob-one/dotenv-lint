"""Tests for the duplicate-keys check."""
from __future__ import annotations

from dotenv_lint.checks import check_duplicates
from dotenv_lint.parser import parse_env_file


def test_no_duplicates(tmp_env):
    p = tmp_env(".env", "A=1\nB=2\nC=3\n")
    parsed = parse_env_file(str(p))
    assert check_duplicates(parsed) == []


def test_single_duplicate(tmp_env):
    p = tmp_env(".env", "A=1\nB=2\nA=3\n")
    parsed = parse_env_file(str(p))
    findings = check_duplicates(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "duplicate"
    assert findings[0].level == "error"
    assert findings[0].lineno == 3
    assert "'A'" in findings[0].message


def test_multiple_duplicates(tmp_env):
    p = tmp_env(".env", "A=1\nA=2\nA=3\n")
    parsed = parse_env_file(str(p))
    findings = check_duplicates(parsed)
    # lines 2 and 3 are duplicates of line 1
    assert len(findings) == 2


def test_duplicate_across_comments(tmp_env):
    p = tmp_env(".env", "A=1\n# comment\nA=2\n")
    parsed = parse_env_file(str(p))
    findings = check_duplicates(parsed)
    assert len(findings) == 1
