# DECISIONS

<!-- markdownlint-disable MD024 -->

Architectural decisions for `se-codeowners`.

This document records current load-bearing decisions, rationale, and consequences.

---

## SECO-D-0001: The kit owns the engine, not the ownership contract

### Date recorded

2026-06-04

### Decision

`se-codeowners` owns reusable Python machinery for loading, validating,
translating, and rendering CODEOWNERS output from accountability-surface
metadata. The accountability contract itself covering which surfaces exist,
which paths they cover, which role owns each, and which handle fills each role,
remains repo-specific material in the owning repository's
`.accountability/surfaces.toml`.

### Rationale

Many repositories share the need to turn role-based oversight metadata into a
CODEOWNERS file, but their surfaces, roles, and ownership are repo-specific
contract material.

Moving those declarations into the kit would make a generic engine own
repository-specific governance content and would create cross-repository churn
whenever a surface or role changes.

### Consequences

- The kit provides generic models, a loader, a path translator, a renderer,
  and command plumbing.
- Repositories provide a declarative `.accountability/surfaces.toml` and own
  their surfaces, roles, and handles.
- The kit loads repo-provided declarations but must not hard-code surface ids,
  paths, role names, or handles.

---

## SECO-D-0002: surfaces.toml is the source of truth; CODEOWNERS is generated

### Date recorded

2026-06-04

### Decision

`.accountability/surfaces.toml` is the single source of truth for ownership.
`.github/CODEOWNERS` is a generated artifact, regenerated from the surfaces
file and never edited by hand.

### Rationale

Two hand-maintained expressions of the same ownership intent drift apart.
Designating the surfaces file as the rationale and CODEOWNERS as its mechanical
projection keeps a single edit point and makes the relationship auditable.

### Consequences

- The generated CODEOWNERS carries a "do not edit by hand" header naming its
  source and its regeneration command.
- `se-codeowners check` compares a committed CODEOWNERS against a fresh render
  and exits non-zero on drift, for use in pre-commit and CI.
- Ownership changes are made in `surfaces.toml`, after which CODEOWNERS is
  regenerated.

---

## SECO-D-0003: Generation is opt-in per repository

### Date recorded

2026-06-04

### Decision

The kit generates CODEOWNERS only when the surfaces file sets
`[codeowners].informs = true`. Without that opt-in, generation refuses.

### Rationale

Not every repository that carries accountability surfaces wants those surfaces
to drive CODEOWNERS, and CODEOWNERS under branch protection becomes an
enforcing gate. The opt-in keeps the surfaces file advisory by default and
makes the decision to project it into an enforcing artifact explicit.

### Consequences

- A repository without `informs = true` receives a clear refusal rather than an
  empty or partial file.
- The choice to enforce ownership is recorded in the surfaces file, not implied
  by the presence of the tool.

---

## SECO-D-0004: No untyped value escapes the load boundary

### Date recorded

2026-06-04

### Decision

Every value parsed from TOML is narrowed to a concrete type at the load
boundary through explicit helpers. The rest of the package consumes a
frozen-dataclass model and never touches raw parsed data.

### Rationale

`tomllib` returns `dict[str, Any]`. Allowing `Any` to flow into translation and
rendering would move type failures far from their cause and defeat strict type
checking. Narrowing at the boundary turns malformed input into a clear error
that names the offending key.

### Consequences

- `_narrow.py` converts parsed values to typed values or raises `SurfacesError`
  with the document path to the bad key.
- `model.py` exposes frozen dataclasses (`Surface`, `SurfacesDoc`); downstream
  code is fully typed.
- The package type-checks under pyright strict with no `Any` leakage.

---

## SECO-D-0005: Module dependencies form a one-way layering

### Date recorded

2026-06-04

### Decision

Internal modules depend in one direction only: `_narrow` and `model` depend on
nothing else in the package; `load` depends on both; `translate` is standalone;
`generate` depends on `model` and `translate`; `cli` depends on `load` and
`generate`.

### Rationale

A single dependency direction keeps each concern testable in isolation,
prevents import cycles, and keeps the cost of a change local. Translation can be
exercised without parsing; rendering without a CLI.

### Consequences

- `translate.py` has no knowledge of TOML, files, or the model and is tested
  directly on strings.
- Parsing, translation, and rendering are independently unit-tested.
- New behavior is added at the layer that owns it rather than threaded across
  modules.

---

## SECO-D-0006: Inexpressible path patterns fail at generation time

### Date recorded

2026-06-04

### Decision

The translator rejects any surface path pattern that CODEOWNERS cannot express
-- negation (`!`), single-character (`?`), character ranges (`[...]`), or a
`**` segment anywhere but a trailing `/**` -- and reports the offending
pattern. It does not emit a best-effort approximation.

### Rationale

CODEOWNERS uses gitignore-style patterns with a smaller feature set than the
globs a surfaces file may use. A pattern silently translated into something that
matches nothing produces a CODEOWNERS file that looks correct but assigns no
owner -- the most dangerous failure mode for an ownership file. Failing loudly
at generation time keeps the gap visible.

### Consequences

- Supported translations are explicit: `dir/**` to `/dir/` (recursive),
  `dir/*` to `/dir/*` (direct children only), and bare paths anchored with a
  leading `/`.
- An unsupported pattern stops generation with a message naming the pattern and
  suggesting a rewrite.
- The owning repository is required to express ownership in terms CODEOWNERS can
  honor.

---

## SECO-D-0007: Ownership is orthogonal to AI authority

### Date recorded

2026-06-04

### Decision

Every surface that declares an `oversight_role` produces CODEOWNERS entries,
regardless of its `ai_authority`. A surface whose authority is
`generate-with-verification` is still owned by its role.

### Rationale

`ai_authority` governs what an agent may do before a human reviews; ownership
governs who reviews a pull request that touches a path. These are separate axes.
A surface where an agent may self-verify edits still has a human accountable for
changes that reach a pull request.

### Consequences

- Generated outputs and other `generate-with-verification` surfaces appear in
  CODEOWNERS when they carry a role.
- A surface is excluded from CODEOWNERS by omitting its `oversight_role`, not by
  its authority level.
- Authority and ownership can be reasoned about and changed independently.

---

## SECO-D-0008: Owner resolution keys on role identity, not role kind

### Date recorded

2026-06-04

### Decision

CODEOWNERS owner resolution keys on a surface's projected ownership role: the
`oversight_role` string today, or an explicit ownership-role identity if the
role model later becomes structured. A role's `kind`, where present, is a
classification axis and must not be used to derive owners.

### Rationale

CODEOWNERS resolves a concrete reviewer per path, so resolution must occur at
the level where ownership decisions actually differ. That level is the specific
ownership role. `kind` is many-to-one over roles by design; deriving owners from
it would collapse roles that have distinct handles onto one owner and discard a
distinction the role layer exists to express.

Deriving owners from `kind` would also couple reviewer identity to the taxonomy:
reclassifying a role -- an analytic or vocabulary edit -- would silently change
who owns code. Ownership must change only when `[codeowners.role_handles]` or a
surface's projected ownership role is edited, never as a side effect of
re-categorizing.

`kind` exists to group roles for reasoning, validation, and reporting, not to
identify an owner. Using a classifier as an identity key is a category error.

### Consequences

- `[codeowners.role_handles]` is keyed at ownership-role granularity and is the
  single place that resolves who owns a surface.
- If the role model later carries a `kind`, the generator may validate against
  it, for example by requiring a human handle for human-steward kinds or a
  minimum reviewer count for certain kinds, but it must not derive owner
  identity from it.
- A role used by a surface but absent from `role_handles` remains a hard error;
  there is no fallback to a kind-level default.
- This is the sibling of SECO-D-0007: ownership derives from role identity,
  while `kind` and `ai_authority` are orthogonal axes that never resolve an
  owner.

<!-- markdownlint-enable MD024 -->
