"""Shared pytest fixtures."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def tmp_env(tmp_path):
    """Return a factory that writes a .env file inside tmp_path."""
    def factory(filename: str, content: str) -> Path:
        p = tmp_path / filename
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p
    return factory
