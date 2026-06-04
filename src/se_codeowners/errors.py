"""Error types for se-codeowners."""

__all__ = ["SurfacesError"]


class SurfacesError(ValueError):
    """Raised when surfaces.toml does not match the expected structure."""
