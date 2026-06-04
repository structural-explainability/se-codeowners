"""Translate accountability-surface path patterns into CODEOWNERS patterns.

``surfaces.toml`` uses repository-root-relative glob patterns such as
``"docs/**"`` or ``"README.md"``.

GitHub CODEOWNERS uses gitignore-style patterns with a smaller feature set.

This module converts the former to the latter and rejects patterns
that CODEOWNERS cannot express.

CODEOWNERS conventions relied on here:

* A leading ``/`` anchors a pattern to the repository root.
* A trailing ``/`` matches a directory and everything beneath it (recursive).
* ``dir/*`` matches files directly in ``dir`` but not its subdirectories.

CODEOWNERS does NOT support
negation (``!``),
single-character (``?``),
character ranges (``[...]``), or a
``**`` segment anywhere except as a trailing ``/**`` directory marker.

Those are rejected with a clear error so that drift is caught
at generation time rather than producing a CODEOWNERS
file that silently matches nothing.
"""

from .errors import SurfacesError

_UNSUPPORTED_TOKENS = ("!", "?", "[", "]")
_RECURSIVE_DIR_SUFFIX = "/**"


def translate_pattern(pattern: str) -> str:
    """Convert a single surface path pattern to a CODEOWNERS pattern."""
    _require_non_empty_pattern(pattern)
    _reject_unsupported_tokens(pattern)
    _reject_unsupported_recursive_glob(pattern)

    return _anchor_to_repo_root(pattern)


def _anchor_to_repo_root(pattern: str) -> str:
    if pattern.startswith("/"):
        return pattern
    return f"/{pattern}"


def _is_trailing_recursive_dir_pattern(pattern: str) -> bool:
    return pattern.endswith(_RECURSIVE_DIR_SUFFIX)


def _reject_unsupported_tokens(pattern: str) -> None:
    for token in _UNSUPPORTED_TOKENS:
        if token in pattern:
            raise SurfacesError(
                f"pattern '{pattern}' uses '{token}', which CODEOWNERS does not support"
            )


def _reject_unsupported_recursive_glob(pattern: str) -> None:
    if "**" not in pattern:
        return

    if _is_trailing_recursive_dir_pattern(pattern):
        return

    raise SurfacesError(
        f"pattern '{pattern}' uses '**' in a position CODEOWNERS cannot express; "
        "rewrite it as a trailing 'dir/**' or as a concrete path"
    )


def _require_non_empty_pattern(pattern: str) -> None:
    if not pattern:
        raise SurfacesError("empty path pattern")
