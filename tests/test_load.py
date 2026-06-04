"""Tests for loading and validating surfaces.toml."""

from pathlib import Path

import pytest

from se_codeowners import SurfacesError, load_surfaces

FIXTURE = Path(__file__).parent / "data" / "surfaces.toml"


def test_loads_fixture() -> None:
    doc = load_surfaces(FIXTURE)
    assert doc.repository_name == "datafun-05-sql"
    assert doc.informs is True
    assert len(doc.surfaces) == 4
    assert {s.oversight_role for s in doc.surfaces} == {
        "instructor",
        "maintainer",
        "data-steward",
        "owner",
    }


def test_handles_normalize_to_tuples() -> None:
    doc = load_surfaces(FIXTURE)
    assert doc.role_handles["owner"] == ("@denisecase",)
    assert doc.role_handles["maintainer"] == (
        "@denisecase",
        "@nwmissouri/datafun-maintainers",
    )


def test_missing_repository_name_is_clear(tmp_path: Path) -> None:
    bad = tmp_path / "surfaces.toml"
    bad.write_text("[repository]\nprofile = 'x'\n", encoding="utf-8")
    with pytest.raises(SurfacesError, match=r"repository.*name"):
        load_surfaces(bad)


def test_missing_file_is_clear(tmp_path: Path) -> None:
    with pytest.raises(SurfacesError, match="cannot read"):
        load_surfaces(tmp_path / "nope.toml")


def test_invalid_toml_is_clear(tmp_path: Path) -> None:
    bad = tmp_path / "surfaces.toml"
    bad.write_text("this = = broken", encoding="utf-8")
    with pytest.raises(SurfacesError, match="invalid TOML"):
        load_surfaces(bad)
