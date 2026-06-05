"""Load and validate ``.accountability/surfaces.toml`` into the typed model."""

from pathlib import Path
import tomllib

from ._narrow import (
    SurfacesError,
    as_bool,
    as_int,
    as_object_dict,
    as_object_list,
    as_str,
    as_str_list,
    optional,
    require,
)
from .model import Surface, SurfacesDoc

DEFAULT_SURFACES_PATH = Path(".accountability/surfaces.toml")


def load_surfaces(path: Path) -> SurfacesDoc:
    """Read ``path`` and return a validated :class:`SurfacesDoc`.

    Args:
        path (Path): The path to the surfaces.toml file.

    Returns:
        SurfacesDoc: The loaded and validated surfaces document.

    Raises:
        SurfacesError: If the file cannot be read, is not valid UTF-8, is not valid TOML, or does not conform to the expected structure.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SurfacesError(f"cannot read surfaces file '{path}': {exc}") from exc
    except UnicodeDecodeError as exc:
        raise SurfacesError(f"'{path}' is not valid UTF-8: {exc}") from exc

    try:
        parsed: dict[str, object] = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SurfacesError(f"invalid TOML in '{path}': {exc}") from exc

    return _build_doc(parsed)


def _build_codeowners(
    parsed: dict[str, object],
) -> tuple[dict[str, tuple[str, ...]], bool, bool]:
    raw = optional(parsed, "codeowners")
    if raw is None:
        return {}, False, False

    table = as_object_dict(raw, ctx="codeowners")

    informs = as_bool(
        require(table, "informs", ctx="codeowners"),
        ctx="codeowners.informs",
    )

    requires_code_owner_review = as_bool(
        require(table, "requires_code_owner_review", ctx="codeowners"),
        ctx="codeowners.requires_code_owner_review",
    )

    handles_value = optional(table, "role_handles")
    if handles_value is None:
        return {}, informs, requires_code_owner_review

    handles_table = as_object_dict(handles_value, ctx="codeowners.role_handles")
    role_handles = {
        role: _normalize_handles(value, ctx=f"codeowners.role_handles.{role}")
        for role, value in handles_table.items()
    }

    return role_handles, informs, requires_code_owner_review


def _build_doc(parsed: dict[str, object]) -> SurfacesDoc:
    repository = as_object_dict(
        require(parsed, "repository", ctx="root"), ctx="repository"
    )
    repo_name = as_str(
        require(repository, "name", ctx="repository"), ctx="repository.name"
    )
    role_handles, informs, requires_code_owner_review = _build_codeowners(parsed)
    return SurfacesDoc(
        repository_name=repo_name,
        surfaces=_build_surfaces(parsed),
        role_handles=role_handles,
        informs=informs,
        requires_code_owner_review=requires_code_owner_review,
    )


def _build_surfaces(parsed: dict[str, object]) -> tuple[Surface, ...]:
    raw = optional(parsed, "surface")
    if raw is None:
        return ()

    entries = as_object_list(raw, ctx="surface")
    surfaces: list[Surface] = []

    for index, entry in enumerate(entries):
        ctx = f"surface[{index}]"
        table = as_object_dict(entry, ctx=ctx)

        role_value = optional(table, "oversight_role")
        role = (
            as_str(role_value, ctx=f"{ctx}.oversight_role")
            if role_value is not None
            else None
        )
        order_value = optional(table, "codeowners_order")
        codeowners_order = (
            as_int(order_value, ctx=f"{ctx}.codeowners_order")
            if order_value is not None
            else None
        )
        surfaces.append(
            Surface(
                id=as_str(require(table, "id", ctx=ctx), ctx=f"{ctx}.id"),
                paths=tuple(
                    as_str_list(require(table, "paths", ctx=ctx), ctx=f"{ctx}.paths")
                ),
                oversight_role=role,
                codeowners_order=codeowners_order,
            )
        )

    return tuple(surfaces)


def _normalize_handles(value: object, *, ctx: str) -> tuple[str, ...]:
    """Accept either a single handle string or a list of handle strings."""
    if isinstance(value, str):
        return (value,)
    return tuple(as_str_list(value, ctx=ctx))
