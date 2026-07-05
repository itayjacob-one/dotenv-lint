"""Tests for the parser module."""
from __future__ import annotations

from dotenv_lint.parser import parse_env_file, ParsedEnvFile, EnvLine


def test_parse_blank_and_comment(tmp_env):
    p = tmp_env(".env", """\
        # This is a comment

        VALID_KEY=value
    """)
    result = parse_env_file(str(p))
    assert isinstance(result, ParsedEnvFile)
    lines = result.lines
    assert lines[0].is_comment
    assert lines[1].is_blank
    assert lines[2].key == "VALID_KEY"
    assert lines[2].value == "value"


def test_parse_key_value(tmp_env):
    p = tmp_env(".env", "MY_KEY=hello world\n")
    result = parse_env_file(str(p))
    assert result.lines[0].key == "MY_KEY"
    assert result.lines[0].value == "hello world"


def test_parse_malformed_no_equals(tmp_env):
    p = tmp_env(".env", "NODEQUALS\n")
    result = parse_env_file(str(p))
    assert result.lines[0].is_malformed


def test_parse_spaced_equals(tmp_env):
    p = tmp_env(".env", "KEY = value\n")
    result = parse_env_file(str(p))
    assert result.lines[0].has_spaced_equals


def test_parse_empty_value(tmp_env):
    p = tmp_env(".env", "EMPTY=\n")
    result = parse_env_file(str(p))
    assert result.lines[0].key == "EMPTY"
    assert result.lines[0].value == ""


def test_parse_value_with_equals(tmp_env):
    """Values that themselves contain '=' must be kept intact."""
    p = tmp_env(".env", "URL=http://x.com?a=1&b=2\n")
    result = parse_env_file(str(p))
    assert result.lines[0].key == "URL"
    assert result.lines[0].value == "http://x.com?a=1&b=2"
