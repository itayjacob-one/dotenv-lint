"""Tests for the drift check."""
from __future__ import annotations

from dotenv_lint.checks import check_drift
from dotenv_lint.parser import parse_env_file


def test_no_drift(tmp_env):
    env = tmp_env(".env", "A=1\nB=2\n")
    example = tmp_env(".env.example", "A=example\nB=example\n")
    parsed = parse_env_file(str(env))
    ex_parsed = parse_env_file(str(example))
    assert check_drift(parsed, ex_parsed) == []


def test_key_in_env_missing_from_example(tmp_env):
    env = tmp_env(".env", "A=1\nEXTRA=secret\n")
    example = tmp_env(".env.example", "A=example\n")
    parsed = parse_env_file(str(env))
    ex_parsed = parse_env_file(str(example))
    findings = check_drift(parsed, ex_parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "drift"
    assert findings[0].level == "error"
    assert "EXTRA" in findings[0].message
    assert findings[0].path == str(env)


def test_key_in_example_missing_from_env(tmp_env):
    env = tmp_env(".env", "A=1\n")
    example = tmp_env(".env.example", "A=example\nMISSING=\n")
    parsed = parse_env_file(str(env))
    ex_parsed = parse_env_file(str(example))
    findings = check_drift(parsed, ex_parsed)
    assert len(findings) == 1
    assert findings[0].check_name == "drift"
    assert findings[0].level == "error"
    assert "MISSING" in findings[0].message
    assert findings[0].path == str(example)


def test_bidirectional_drift(tmp_env):
    env = tmp_env(".env", "A=1\nB_ENV_ONLY=secret\n")
    example = tmp_env(".env.example", "A=example\nC_EXAMPLE_ONLY=\n")
    parsed = parse_env_file(str(env))
    ex_parsed = parse_env_file(str(example))
    findings = check_drift(parsed, ex_parsed)
    assert len(findings) == 2
    names = {f.message for f in findings}
    # one finding mentions B_ENV_ONLY, the other C_EXAMPLE_ONLY
    assert any("B_ENV_ONLY" in m for m in names)
    assert any("C_EXAMPLE_ONLY" in m for m in names)
