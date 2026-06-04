# se-codeowners

[![PyPI](https://img.shields.io/pypi/v/se-codeowners?logo=pypi&label=pypi)](https://pypi.org/project/se-codeowners/)
[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-codeowners/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-codeowners)
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI-Lean](https://github.com/structural-explainability/se-codeowners/actions/workflows/ci-lean.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-codeowners/actions/workflows/ci-lean.yml)
[![CI](https://github.com/structural-explainability/se-codeowners/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-codeowners/actions/workflows/ci-python-zensical.yml)
[![Docs-Deploy](https://github.com/structural-explainability/se-codeowners/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-codeowners/actions/workflows/deploy-zensical.yml)
[![Pre-Release](https://github.com/structural-explainability/se-codeowners/actions/workflows/pre-release.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-codeowners/actions/workflows/pre-release.yml)
[![Release](https://github.com/structural-explainability/se-codeowners/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/structural-explainability/se-codeowners/actions/workflows/release-pypi.yml)
[![Links](https://github.com/structural-explainability/se-codeowners/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-codeowners/actions/workflows/links.yml)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-brightgreen.svg)](https://github.com/structural-explainability/se-codeowners/security)

> Standalone CLI utility that implements GitHub CODEOWNERS projection

## Overview

Generate a GitHub `CODEOWNERS` file from the role-based oversight metadata in
`.accountability/surfaces.toml`.

The surfaces file is the advisory rationale: it names each accountability
surface, the paths it covers, and the `oversight_role` responsible for it.
`se-codeowners` resolves each role to a GitHub handle or team via
`[codeowners.role_handles]` and emits the corresponding `CODEOWNERS` entries.

The generated `CODEOWNERS` file provides GitHub review routing.
It becomes a merge gate only when repository branch protection or
rulesets require code-owner review.

## Install

```shell
uv tool install se-codeowners
```

Uses the standard-library `tomllib`. No runtime dependencies.

## Run Without Installing

```shell
uvx se-codeowners --help
```

## Usage

```bash
# Render to stdout
uv run se-codeowners generate

# Write the file
uv run se-codeowners generate --output .github/CODEOWNERS

# Fail if any role still maps to a placeholder handle (e.g. `@OWNER`):
uv run se-codeowners generate --strict --output .github/CODEOWNERS

# Verify
uv run se-codeowners check
```

Both subcommands accept `--surfaces PATH`; `check` also accepts
`--codeowners PATH`. The defaults are `.accountability/surfaces.toml` and
`.github/CODEOWNERS`.

## What the surfaces file must contain

```toml
[codeowners]
informs = true                           # opt in; generation refuses without an entry
requires_code_owner_review = false       # opt in; generation refuses without an entry

[codeowners.role_handles]
owner = "@octocat"                       # a single handle
maintainer = ["@octocat", "@org/team"]   # or several owners
data-steward = "@octocat"

[[surface]]
id = "data-contract"
name = "Data contract"
paths = ["data/raw/**"]
oversight_role = "data-steward"          # must have an entry in role_handles
oversight_role = "data-steward"
codeowners_order = 100
```

Surfaces without an `oversight_role` are skipped.
A role used by a surface but missing from `role_handles` is a hard error.

Projected surfaces must declare `codeowners_order`.
Lower values emit earlier;
later matching CODEOWNERS patterns take precedence.

## Path translation

`surfaces.toml` uses repository-root-relative globs. `CODEOWNERS` uses
gitignore-style patterns with a smaller feature set, so patterns are converted:

| surfaces.toml     | CODEOWNERS         | meaning                         |
| ----------------- | ------------------ | ------------------------------- |
| `README.md`       | `/README.md`       | one file at the repo root       |
| `docs/**`         | `/docs/**`         | a directory, recursively        |
| `sql/duckdb/**`   | `/sql/duckdb/**`   | a nested directory, recursively |
| `docs/*`          | `/docs/*`          | direct children only            |
| `src/app/case.py` | `/src/app/case.py` | one nested file                 |

Patterns CODEOWNERS cannot express:

- negation (`!`),
- single-character (`?`),
- character ranges (`[...]`), or a
- `**` segment anywhere but a trailing `/**`

These are rejected at generation time with a message naming the offending pattern,
so the failure surfaces during generation.

GitHub applies the **last** matching pattern for a path.
Entries are emitted by `codeowners_order`, then surface id.

## Keeping it in sync (CI / pre-commit)

Add a hook to the consuming repository so a stale `CODEOWNERS` fails review:

```yaml
# .pre-commit-config.yaml in the repo that owns surfaces.toml
- repo: local
  hooks:
    - id: codeowners-up-to-date
      name: CODEOWNERS matches surfaces.toml
      entry: uv run se-codeowners check --strict
      language: system
      files: ^(\.accountability/surfaces\.toml|\.github/CODEOWNERS)$
      pass_filenames: false
```

## Layout

```text
se-codeowners/
├── src/se_codeowners/
│   ├── __init__.py        public API: load_surfaces, render_codeowners, ...
│   ├── __main__.py        module entry: python -m se_codeowners (PATH-independent)
│   ├── _narrow.py         boundary narrowing: tomllib Any -> typed values
│   ├── model.py           frozen dataclasses (Surface, SurfacesDoc)
│   ├── load.py            parse + validate surfaces.toml into the model
│   ├── translate.py       surface glob -> CODEOWNERS pattern
│   ├── generate.py        SurfacesDoc -> CODEOWNERS text
│   └── cli.py             generate / check subcommands
└── tests/
```

Dependency direction is one-way:

- `_narrow` and `model` depend on nothing in the package;
- `load` depends on both;
- `translate` is standalone;
- `generate` depends on `model` and `translate`;
- `cli` depends on `load` and `generate`.

No raw `Any` from `tomllib` escapes `_narrow`/`load`.

## Developer Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal

Open a machine terminal where you want the project:

```shell
git clone https://github.com/structural-explainability/se-codeowners

cd se-codeowners
code .
```

### In a VS Code terminal

Use VS Code Menu:
View / Command Palette / `Developer: Reload Window` to refresh.

```shell
uv self update
uv python pin 3.14
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade

uvx pre-commit install

uv run se-codeowners --help
uv run se-codeowners generate --help
uv run se-codeowners check --help

# validate manifest file
uvx se-manifest-schema validate-manifest --path SE_MANIFEST.toml --strict

git add -A
uvx pre-commit run --all-files
# repeat if changes were made
uvx pre-commit run --all-files

uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# check import layers
uvx --with-editable . --from import-linter lint-imports --config .github/.importlinter

# check complexity; no output is good (all A or B)
uvx radon cc src/se_codeowners -s -a -n C

uv build
uvx twine check dist/*

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

</details>

## Authority Manifest

[.accountability/surfaces.toml](./.accountability/surfaces.toml)

## Citation

[CITATION.cff](./CITATION.cff)

## License

[MIT](./LICENSE)

## Repository Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
