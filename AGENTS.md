# AGENTS.md (se-codeowners)

## Contract Mode

Work in contract-first mode.

Do not recommend temporary fixes unless explicitly requested.
Do not introduce "for now" architecture.
Do not simplify in ways that create later reversal across repositories.
Build always with the end in mind.

Before recommending a change, identify:

1. the owner of the responsibility,
2. the public contract surface,
3. the dependency direction,
4. the release target,
5. whether the change scales across SE repositories,
6. whether the change creates future churn.

## Repository Purpose

`se-codeowners` is a standalone projection tool.

It loads accountable-surface metadata from `.accountability/surfaces.toml`,
resolves `oversight_role` values through `[codeowners.role_handles]`, translates
surface path patterns into GitHub CODEOWNERS patterns, renders
`.github/CODEOWNERS`, and checks committed output for drift.

The package owns the projection machinery. It does not own the accountable
surface vocabulary, the repository-specific surface contract, or legal /
organizational compliance claims.

## Release Target

This repository targets the current SE release train.

The canonical Python version is defined in `.python-version`.
Do not downgrade the Python target because current tooling lags.

If an API, command, dependency, or entry point fails, first determine the
intended durable surface. Then update the implementation to match that surface.

## Scope

Changes must preserve:

* determinism,
* cross-platform compatibility,
* typed load boundaries,
* explicit and inspectable structure,
* fail-loud behavior for unsupported CODEOWNERS patterns,
* drift-checkable generated artifacts.

Do not introduce hidden logic where declarative structure is possible.

## Projection Boundaries

`se-codeowners` may:

* parse `.accountability/surfaces.toml`,
* narrow TOML values into typed Python models,
* validate fields needed for CODEOWNERS projection,
* resolve `oversight_role` through `[codeowners.role_handles]`,
* translate supported path patterns into CODEOWNERS syntax,
* reject unsupported path patterns,
* render `.github/CODEOWNERS`,
* check generated output for drift.

`se-codeowners` must not:

* define the full accountable-surface vocabulary,
* infer owners from `surface.role.kind`,
* infer legal compliance,
* decide whether CODEOWNERS is branch-protection-gated,
* validate whether human review or evidence was substantively meaningful,
* silently approximate unsupported CODEOWNERS patterns.

## CODEOWNERS Ordering

CODEOWNERS applies the last matching pattern for a path.

Projected surfaces therefore use `codeowners_order` to make output order
explicit. Lower values emit earlier; later matching patterns take precedence.
Ties are emitted alphabetically by surface id.

Do not encode projection order into surface ids. Surface ids must remain
semantic and stable.

## Role Resolution

Owner resolution keys on role identity, not role kind.

Use:

```text
surface.oversight_role -> [codeowners.role_handles] -> GitHub handle/team
```

Do not derive CODEOWNERS owners from `surface.role.kind`.

`surface.role.kind` is a semantic classification axis for accountable-surface
reasoning, validation, and reporting. It is not an ownership identity.

## Module Boundaries

Maintain one-way internal layering:

* `_narrow.py` and `model.py` depend on nothing else in the package.
* `load.py` depends on `_narrow.py` and `model.py`.
* `translate.py` is standalone and handles only path-pattern translation.
* `generate.py` depends on `model.py` and `translate.py`.
* `cli.py` depends on `load.py` and `generate.py`.

No raw `Any` from `tomllib` may escape the load boundary.

## Python Tooling Constraints

Use `uv` for all Python environment and tooling commands.

Do not recommend or use `pip install ...` as the primary workflow.
Commands must work on Windows, macOS, and Linux.
Use Python-native or cross-platform tooling in scripts.
Avoid shell syntax that only works on one operating system.

## Quickstart

```shell
uv self update
uv python pin 3.15
uv sync --extra dev --extra docs --upgrade
```

## Lint and Format

```shell
uv run python -m ruff format .
uv run python -m ruff check . --fix
```

## CODEOWNERS Projection

```shell
uv run se-codeowners generate
uv run se-codeowners generate --strict --output .github/CODEOWNERS
uv run se-codeowners check --strict
```

## Build Documentation

```shell
uv run python -m zensical build
```

## pre-commit

pre-commit runs only on tracked or staged files.
Use `git add -A` before expecting hooks to run on newly created files.

```shell
uvx pre-commit run --all-files
```

## Release Validation

Use the repository release script when available.

For individual checks:

```shell
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade
uvx pre-commit run --all-files
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build
uvx --with-editable . --from import-linter lint-imports --config .github/.importlinter
uvx radon cc src/se_codeowners -s -a -n C
uv build
uvx twine check dist/*
```

## Non-goals

`se-codeowners` does not define:

* the accountable-surface specification,
* the complete accountable-service model,
* EU AI Act compliance,
* branch protection policy,
* human review quality,
* evidence truthfulness,
* incident response semantics,
* runtime AI governance behavior.

Those responsibilities belong to upstream specifications, repository policy,
platform configuration, or downstream accountable-service tooling.
