"""Main package for se-codeowners."""

from .errors import SurfacesError
from .generate import render_codeowners
from .load import DEFAULT_SURFACES_PATH, load_surfaces

__all__ = [
    "DEFAULT_SURFACES_PATH",
    "SurfacesError",
    "load_surfaces",
    "render_codeowners",
]
