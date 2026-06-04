"""Tests for surface-pattern -> CODEOWNERS-pattern translation."""

import pytest

from se_codeowners.errors import SurfacesError
from se_codeowners.translate import translate_pattern


@pytest.mark.parametrize(
    ("surface_pattern", "expected"),
    [
        ("README.md", "/README.md"),
        ("LICENSE", "/LICENSE"),
        ("CITATION.cff", "/CITATION.cff"),
        ("pyproject.toml", "/pyproject.toml"),
        ("docs/**", "/docs/**"),
        ("sql/duckdb/**", "/sql/duckdb/**"),
        ("data/raw/**", "/data/raw/**"),
        ("artifacts/**", "/artifacts/**"),
        (".github/**", "/.github/**"),
        (
            "src/datafun/app_retail_duckdb_case.py",
            "/src/datafun/app_retail_duckdb_case.py",
        ),
        ("docs/*", "/docs/*"),
        ("/already/anchored.py", "/already/anchored.py"),
    ],
)
def test_translate_known_patterns(surface_pattern: str, expected: str) -> None:
    assert translate_pattern(surface_pattern) == expected


@pytest.mark.parametrize(
    "bad", ["!docs/**", "src/**/x.py", "data/file?.csv", "logs/[0-9].log"]
)
def test_translate_rejects_unsupported(bad: str) -> None:
    with pytest.raises(SurfacesError):
        translate_pattern(bad)


def test_translate_rejects_empty() -> None:
    with pytest.raises(SurfacesError):
        translate_pattern("")
