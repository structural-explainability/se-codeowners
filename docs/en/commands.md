# Commands

| Command    | Durable responsibility                                             |
| ---------- | ------------------------------------------------------------------ |
| `generate` | Project the ownership declared in `surfaces.toml` into CODEOWNERS. |
| `check`    | Verify the committed CODEOWNERS still matches `surfaces.toml`.     |

Both commands read `.accountability/surfaces.toml` by default
and require `[codeowners].informs = true`;
without that opt-in they refuse (see DECISIONS.md).

## Command: generate

Render a CODEOWNERS file from the accountability surfaces.
Writes to stdout unless `--output` is given.

Usage

```shell
se-codeowners generate
se-codeowners generate --output .github/CODEOWNERS
se-codeowners generate --strict --output .github/CODEOWNERS
```

Options

| Option            | Default                         | Effect                                         |
| ----------------- | ------------------------------- | ---------------------------------------------- |
| `--surfaces PATH` | `.accountability/surfaces.toml` | Surfaces file to read.                         |
| `--output PATH`   | stdout                          | Write CODEOWNERS here instead of printing.     |
| `--strict`        | off                             | Fail if any role maps to a placeholder handle. |

Exit codes

- `0` CODEOWNERS rendered, and written if `--output` was given.
- `2` the surfaces file is missing, invalid, not opted in, has an unmapped
  role, uses a path pattern CODEOWNERS cannot express, or (under `--strict`)
  retains a placeholder handle.

## Command: check

Compare a committed CODEOWNERS against a fresh render and report drift. Intended
for pre-commit and CI.

Usage

```shell
se-codeowners check
se-codeowners check --strict
```

Options

| Option              | Default                         | Effect                                         |
| ------------------- | ------------------------------- | ---------------------------------------------- |
| `--surfaces PATH`   | `.accountability/surfaces.toml` | Surfaces file to read.                         |
| `--codeowners PATH` | `.github/CODEOWNERS`            | Committed CODEOWNERS to verify.                |
| `--strict`          | off                             | Fail if any role maps to a placeholder handle. |

Exit codes

- `0` the committed CODEOWNERS matches `surfaces.toml`.
- `1` the CODEOWNERS is missing or out of date; regenerate it.
- `2` the surfaces file could not be loaded or rendered (same conditions as
  `generate`).
