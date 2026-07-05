"""Integration tests for the CLI."""
from __future__ import annotations

from io import StringIO

import pytest

from dotenv_lint.cli import lint_files, main


def test_clean_file_exits_0(tmp_env):
    p = tmp_env(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    out = StringIO()
    code = lint_files([str(p)], out=out)
    assert code == 0


def test_error_file_exits_1(tmp_env):
    p = tmp_env(".env", "DB_HOST=\n")  # blank value -> error
    out = StringIO()
    code = lint_files([str(p)], out=out)
    assert code == 1


def test_missing_file_exits_2(tmp_path):
    out = StringIO()
    code = lint_files([str(tmp_path / "nonexistent.env")], out=out)
    assert code == 2


def test_output_format(tmp_env):
    p = tmp_env(".env", "KEY=\n")
    out = StringIO()
    lint_files([str(p)], out=out)
    output = out.getvalue()
    # Should contain file:line: level check-name message
    assert ":1:" in output
    assert "error" in output
    assert "blank-value" in output


def test_summary_always_printed(tmp_env):
    p = tmp_env(".env", "GOOD=value\n")
    out = StringIO()
    lint_files([str(p)], out=out)
    assert "Summary:" in out.getvalue()


def test_multiple_files(tmp_env):
    p1 = tmp_env("a.env", "KEY=value\n")
    p2 = tmp_env("b.env", "KEY=\n")  # error
    out = StringIO()
    code = lint_files([str(p1), str(p2)], out=out)
    assert code == 1


def test_drift_via_lint_files(tmp_env):
    env = tmp_env(".env", "A=1\nEXTRA=secret\n")
    example = tmp_env(".env.example", "A=example\n")
    out = StringIO()
    code = lint_files([str(env)], example_path=str(example), out=out)
    assert code == 1
    assert "drift" in out.getvalue()


def test_main_exits(tmp_env, monkeypatch):
    p = tmp_env(".env", "GOOD=value\n")
    monkeypatch.setattr("sys.argv", ["dotenv-lint", str(p)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_exits_1_on_error(tmp_env, monkeypatch):
    p = tmp_env(".env", "BAD=\n")
    monkeypatch.setattr("sys.argv", ["dotenv-lint", str(p)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_finding_str_format():
    from dotenv_lint.checks import Finding
    f = Finding(path=".env", lineno=5, level="error", check_name="duplicate", message="oops")
    assert str(f) == ".env:5: error duplicate oops"
