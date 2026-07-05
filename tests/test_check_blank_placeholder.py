"""Tests for the blank/placeholder value check."""
from __future__ import annotations

import pytest

from dotenv_lint.checks import check_blank_or_placeholder
from dotenv_lint.parser import parse_env_file


def test_good_values(tmp_env):
    p = tmp_env(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    parsed = parse_env_file(str(p))
    assert check_blank_or_placeholder(parsed) == []


def test_blank_value(tmp_env):
    p = tmp_env(".env", "API_KEY=\n")
    parsed = parse_env_file(str(p))
    findings = check_blank_or_placeholder(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "blank-value"
    assert findings[0].level == "error"


@pytest.mark.parametrize("val", ["changeme", "CHANGEME", "xxx", "XXXX", "todo", "TODO", "fixme", "placeholder"])
def test_placeholder_values(tmp_env, val):
    p = tmp_env(".env", f"SECRET={val}\n")
    parsed = parse_env_file(str(p))
    findings = check_blank_or_placeholder(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "placeholder-value"
    assert findings[0].level == "error"


def test_real_value_not_flagged(tmp_env):
    p = tmp_env(".env", "SECRET=my-actual-secret-value\n")
    parsed = parse_env_file(str(p))
    assert check_blank_or_placeholder(parsed) == []
