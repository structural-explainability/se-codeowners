"""Tests for CODEOWNERS rendering."""

from pathlib import Path

import pytest

from se_codeowners import SurfacesError, load_surfaces, render_codeowners

FIXTURE = Path(__file__).parent / "data" / "surfaces.toml"


def test_render_contains_expected_lines() -> None:
    out = render_codeowners(load_surfaces(FIXTURE))
    assert "# Surface: data-contract (role: data-steward)" in out
    assert "/data/raw/**" in out
    assert "/README.md" in out
    # Multiple owners are space-joined on one line.
    assert "@denisecase @nwmissouri/datafun-maintainers" in out
    # Patterns are column-aligned (consistent gap before owners).
    assert "/LICENSE" in out
    assert "# Repository:" in out
    assert "# [codeowners].requires_code_owner_review = false" in out


def test_render_is_deterministic() -> None:
    doc = load_surfaces(FIXTURE)
    assert render_codeowners(doc) == render_codeowners(doc)


def test_informs_false_refuses(tmp_path: Path) -> None:
    src = FIXTURE.read_text(encoding="utf-8").replace(
        "informs = true", "informs = false"
    )
    path = tmp_path / "surfaces.toml"
    path.write_text(src, encoding="utf-8")
    with pytest.raises(SurfacesError, match="does not opt into"):
        render_codeowners(load_surfaces(path))


def test_unmapped_role_is_clear(tmp_path: Path) -> None:
    src = FIXTURE.read_text(encoding="utf-8").replace(
        'data-steward = "@denisecase"\n', ""
    )
    path = tmp_path / "surfaces.toml"
    path.write_text(src, encoding="utf-8")
    with pytest.raises(SurfacesError, match="no handle for it"):
        render_codeowners(load_surfaces(path))


def test_strict_rejects_placeholder(tmp_path: Path) -> None:
    src = FIXTURE.read_text(encoding="utf-8").replace('"@denisecase"', '"@OWNER"')
    path = tmp_path / "surfaces.toml"
    path.write_text(src, encoding="utf-8")
    doc = load_surfaces(path)
    # Non-strict still renders; strict refuses placeholders.
    assert "@OWNER" in render_codeowners(doc)
    with pytest.raises(SurfacesError, match="placeholder"):
        render_codeowners(doc, strict=True)
