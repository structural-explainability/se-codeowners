"""Boundary-narrowing helpers.

``tomllib`` returns ``dict[str, Any]``.

These helpers convert untyped parsed
values into concrete Python types at the parse boundary,
raising a clear :class:`SurfacesError` on any mismatch,
so no ``Any`` leaks past the `load` module into the rest of the package.

Every helper takes a ``ctx`` describing where in the document the value came
from (e.g. ``"surface[2].oversight_role"``)
so error messages point at the offending key
rather than failing somewhere downstream.
"""

from typing import cast

from .errors import SurfacesError


def as_bool(value: object, *, ctx: str) -> bool:
    if not isinstance(value, bool):
        raise SurfacesError(f"{ctx}: expected a boolean, got {type(value).__name__}")
    return value


def as_int(value: object, *, ctx: str) -> int:
    """Narrow a parsed TOML value to int, excluding bool."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise SurfacesError(f"{ctx}: expected integer")
    return value


def as_object_dict(value: object, *, ctx: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise SurfacesError(f"{ctx}: expected a table, got {type(value).__name__}")
    # TOML keys are always strings; widen the value type to ``object``.
    typed = cast("dict[object, object]", value)
    return {str(key): item for key, item in typed.items()}


def as_object_list(value: object, *, ctx: str) -> list[object]:
    if not isinstance(value, list):
        raise SurfacesError(f"{ctx}: expected an array, got {type(value).__name__}")
    return list(cast("list[object]", value))


def as_str(value: object, *, ctx: str) -> str:
    if not isinstance(value, str):
        raise SurfacesError(f"{ctx}: expected a string, got {type(value).__name__}")
    return value


def as_str_list(value: object, *, ctx: str) -> list[str]:
    items = as_object_list(value, ctx=ctx)
    return [as_str(item, ctx=f"{ctx}[{index}]") for index, item in enumerate(items)]


def optional(mapping: dict[str, object], key: str) -> object | None:
    return mapping.get(key)


def require(mapping: dict[str, object], key: str, *, ctx: str) -> object:
    if key not in mapping:
        raise SurfacesError(f"{ctx}: missing required key '{key}'")
    return mapping[key]
