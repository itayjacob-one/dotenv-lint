"""Tests for the summary helper."""
from __future__ import annotations

from dotenv_lint.checks import Finding, build_summary


def test_summary_no_findings():
    result = build_summary([])
    assert "0 finding" in result
    assert "0 error" in result
    assert "0 warning" in result


def test_summary_mixed():
    findings = [
        Finding(path=".env", lineno=1, level="error", check_name="duplicate", message="x"),
        Finding(path=".env", lineno=2, level="error", check_name="drift", message="y"),
        Finding(path=".env", lineno=3, level="warning", check_name="key-naming", message="z"),
    ]
    result = build_summary(findings)
    assert "3 finding" in result
    assert "2 error" in result
    assert "1 warning" in result
