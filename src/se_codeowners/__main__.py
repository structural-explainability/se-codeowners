"""Entry point for ``python -m se_codeowners``.

WHY: The ``se-codeowners`` console script depends on its install directory
being on PATH, which is often not the case (notably the Scripts directory on
Windows) and is ambiguous when several environments are active. Running the
package as a module pins execution to the interpreter that invoked it --
e.g. ``uv run python -m se_codeowners`` or a CI step -- with no PATH lookup,
and gives the pre-commit hook a fallback entry. It imports ``cli.main``
directly rather than through the package facade so module execution does not
pull in the full public API.
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
