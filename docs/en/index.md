# se-codeowners

`se-codeowners` generates a GitHub CODEOWNERS file from the role-based oversight
metadata in a repository's `.accountability/surfaces.toml`.

It provides generic tooling to load, validate, translate, and render ownership
entries from accountability-surface declarations. The owning repository supplies
the surfaces, roles, and handles; the kit supplies the engine.

## Purpose

The package exists so repositories that already describe accountability surfaces
can project role-based oversight into an enforceable CODEOWNERS file from one
shared engine, instead of each maintaining its own script for the same
repository mechanics.

The kit serves repositories that maintain a `.accountability/surfaces.toml` with
a `[codeowners]` opt-in. It does not define ownership; it renders the ownership a
repository declares.

## Public command

The package exposes one console command with two subcommands:

```shell
se-codeowners generate   # render CODEOWNERS from surfaces.toml
se-codeowners check      # verify a committed CODEOWNERS is up to date
```

See [Commands](./commands.md) for subcommand responsibilities and options.

## API reference

The Python API reference is generated from source during documentation builds.

See [API Reference](./api/index.md) for generated package documentation.
