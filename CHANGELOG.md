# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

---

## [0.1.0] - 2026-06-04

### Added

- Initial `se-codeowners` Python package.
- `se-codeowners generate` command for rendering `.github/CODEOWNERS` from
  `.accountability/surfaces.toml`.
- `se-codeowners check` command for detecting drift between the manifest and a
  committed CODEOWNERS file.
- Role-based owner resolution through `[codeowners.role_handles]`.
- Explicit projected-surface ordering through `codeowners_order`.
- Fail-loud translation for path patterns GitHub CODEOWNERS cannot express.
- Strict mode for rejecting placeholder GitHub handles or teams.
- Typed TOML loading boundary with frozen dataclass models.
- Generated Python API documentation support.

## Notes on versioning and releases

- We use **SemVer**:
  - \*_MAJOR_- - breaking changes
  - \*_MINOR_- - backward-compatible changes
  - \*_PATCH_- - fixes, documentation, tooling
- Versions are driven by git tags. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

## Release Procedure (Required)

Follow these steps exactly when creating a new release.

### Task 1. Update release metadata (manual edits)

1.1. CITATION.cff: update version and date-released
1.2. CHANGELOG.md: add section, move unreleased entries, update links
1.3. pyproject.toml: update build fallback-version (near end of the file)

### Task 2. Validate

```shell
uv lock --upgrade
uv sync --extra dev --extra docs --upgrade

uv run se-codeowners --help
uv run se-codeowners generate
uv run se-codeowners generate --strict --output .github/CODEOWNERS
uv run se-codeowners check

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
```

### Task 3. Commit, push, and tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

### Task 4. After tagging, verify tag consistency

```shell
uvx se-manifest-schema check-version --require-tag
```

Confirms CITATION.cff version matches the pushed git tag.
Run this after `git push origin vX.Y.Z`; it will fail before that point.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Z.Y
git push origin :refs/tags/vX.Z.Y
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-codeowners/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/structural-explainability/se-codeowners/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
