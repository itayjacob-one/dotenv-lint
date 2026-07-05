"""Tests for the key-naming check."""
from __future__ import annotations

import pytest

from dotenv_lint.checks import check_key_naming
from dotenv_lint.parser import parse_env_file


@pytest.mark.parametrize("key", ["MY_KEY", "KEY", "A", "KEY123", "MY_KEY_123"])
def test_valid_keys(tmp_env, key):
    p = tmp_env(".env", f"{key}=value\n")
    parsed = parse_env_file(str(p))
    assert check_key_naming(parsed) == []


@pytest.mark.parametrize("key", ["my_key", "myKey", "My_Key", "key-name", "key.name", "1KEY"])
def test_invalid_keys(tmp_env, key):
    p = tmp_env(".env", f"{key}=value\n")
    parsed = parse_env_file(str(p))
    findings = check_key_naming(parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "key-naming"
    assert findings[0].level == "warning"


def test_warning_does_not_affect_exit_code(tmp_env):
    """A file with only naming warnings should produce exit 0."""
    from io import StringIO
    from dotenv_lint.cli import lint_files

    p = tmp_env(".env", "lowercase=value\n")
    out = StringIO()
    code = lint_files([str(p)], out=out)
    assert code == 0
