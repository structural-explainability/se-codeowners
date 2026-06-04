"""Typed model for the accountability surfaces document.

Only the fields needed to generate CODEOWNERS are modelled. The loader is
responsible for producing these objects; everything downstream consumes them
and never touches raw TOML.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Surface:
    """One accountability surface and the role responsible for it."""

    id: str
    paths: tuple[str, ...]
    oversight_role: str | None
    codeowners_order: int | None


@dataclass(frozen=True, slots=True)
class SurfacesDoc:
    """The parts of surfaces.toml relevant to CODEOWNERS generation."""

    repository_name: str
    surfaces: tuple[Surface, ...]
    role_handles: dict[str, tuple[str, ...]]
    informs: bool
