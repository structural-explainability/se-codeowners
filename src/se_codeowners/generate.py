"""Render a CODEOWNERS file from a :class:`SurfacesDoc`."""

from .errors import SurfacesError
from .model import Surface, SurfacesDoc
from .translate import translate_pattern

_PLACEHOLDER_TOKENS = ("@OWNER", "OWNER_HANDLE")


def generate_codeowners_lines(
    doc: SurfacesDoc,
    grouped: list[tuple[Surface, list[tuple[str, str]]]],
    width: int,
) -> str:
    """Generate the lines of the CODEOWNERS file.

    Args:
        doc (SurfacesDoc): The surfaces document being rendered.
        grouped (list[tuple[Surface, list[tuple[str, str]]]]): Grouped surfaces and their patterns.
        width (int): The width to pad the patterns to.

    Returns:
        str: The generated CODEOWNERS file content.
    """
    lines: list[str] = []
    lines.extend(_header(doc).splitlines())
    for surface, rows in grouped:
        lines.append("")
        lines.append(f"# Surface: {surface.id} (role: {surface.oversight_role})")
        lines.extend(f"{pattern.ljust(width)}  {owners}" for pattern, owners in rows)
    return "\n".join(lines) + "\n"


def render_codeowners(doc: SurfacesDoc, *, strict: bool = False) -> str:
    """Return CODEOWNERS file content for ``doc``.

    Surfaces without an ``oversight_role`` are skipped. If ``strict`` is set,
    a handle still containing a placeholder token is treated as an error.

    Args:
        doc (SurfacesDoc): The surfaces document to render.
        * means that the following parameters must be passed as keyword arguments.
        strict (bool, optional): Whether to treat placeholder handles as errors. Defaults to False.
    """
    if not doc.informs:
        raise SurfacesError(
            "surfaces.toml does not opt into CODEOWNERS generation "
            "([codeowners].informs is not true)"
        )

    grouped: list[tuple[Surface, list[tuple[str, str]]]] = []
    all_patterns: list[str] = []

    for surface in _projected_surfaces(doc):
        owners_text = " ".join(_resolve_owners(surface, doc, strict=strict))
        rows = [(translate_pattern(pattern), owners_text) for pattern in surface.paths]
        if rows:
            grouped.append((surface, rows))
            all_patterns.extend(pattern for pattern, _ in rows)

    if not all_patterns:
        raise SurfacesError("no surfaces with an oversight_role were found")
    width = max(len(pattern) for pattern in all_patterns)
    return generate_codeowners_lines(doc, grouped, width)


def _header(doc: SurfacesDoc) -> str:
    return f"""\
# ============================================================
# .github/CODEOWNERS
# ============================================================
# GENERATED FILE -- do not edit by hand.
#
# Source:     .accountability/surfaces.toml
# Generator:  se-codeowners
# Repository: {doc.repository_name}
# Regenerate: se-codeowners generate --output .github/CODEOWNERS
#
# [codeowners].informs = true means this surfaces manifest intentionally
# informs the generated GitHub CODEOWNERS projection.
#
# [codeowners].requires_code_owner_review = {str(doc.requires_code_owner_review).lower()}
# records whether repository governance expects GitHub branch protection or
# rulesets to require CODEOWNER review before protected changes merge.
# Actual enforcement is configured in GitHub, not in this generated file.
#
# Each entry reflects the oversight_role assigned to an accountability
# surface, resolved to a handle via [codeowners.role_handles]. GitHub
# applies the LAST matching pattern for a given path, so order matters.
# Surfaces are emitted by codeowners_order, then surface id."""


def _projected_surfaces(doc: SurfacesDoc) -> list[Surface]:
    projected = [
        surface for surface in doc.surfaces if surface.oversight_role is not None
    ]

    missing_order = [
        surface.id for surface in projected if surface.codeowners_order is None
    ]
    if missing_order:
        joined = ", ".join(sorted(missing_order))
        raise SurfacesError(
            f"projected surfaces must declare codeowners_order; missing for: {joined}"
        )

    return sorted(
        projected,
        key=lambda surface: (_require_codeowners_order(surface), surface.id),
    )


def _require_codeowners_order(surface: Surface) -> int:
    if surface.codeowners_order is None:
        raise SurfacesError(
            f"surface {surface.id!r}: projected surface is missing codeowners_order"
        )
    return surface.codeowners_order


def _resolve_owners(
    surface: Surface, doc: SurfacesDoc, *, strict: bool
) -> tuple[str, ...]:
    role = surface.oversight_role
    if role is None:  # pragma: no cover - callers filter None first
        raise SurfacesError(f"surface '{surface.id}' has no oversight_role")

    handles = doc.role_handles.get(role)
    if not handles:
        raise SurfacesError(
            f"surface '{surface.id}' has oversight_role '{role}', but "
            "[codeowners.role_handles] has no handle for it"
        )

    if strict:
        for handle in handles:
            if any(token in handle for token in _PLACEHOLDER_TOKENS):
                raise SurfacesError(
                    f"role '{role}' is mapped to placeholder handle '{handle}'; "
                    "replace it with a real GitHub handle or team"
                )
    return handles
