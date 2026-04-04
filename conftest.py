"""Pytest configuration for hermes-loop-plugin.

Bootstraps the hermes_loop_plugin package in sys.modules so that relative
imports inside __init__.py work correctly without installing the package.
Also prevents pytest from collecting __init__.py as a test module.
"""

import importlib.util
import sys
from pathlib import Path

# Tell pytest not to collect the package __init__.py
collect_ignore = ["__init__.py"]

_REPO = Path(__file__).parent
_PKG = "hermes_loop_plugin"


def _bootstrap_package() -> None:
    """Register hermes_loop_plugin (and its submodules) into sys.modules."""
    if _PKG in sys.modules:
        return

    # 1. Create the package shell FIRST so relative imports in submodules resolve.
    import types
    pkg_shell = types.ModuleType(_PKG)
    pkg_shell.__package__ = _PKG
    pkg_shell.__path__ = [str(_REPO)]
    pkg_shell.__file__ = str(_REPO / "__init__.py")
    sys.modules[_PKG] = pkg_shell

    # 2. Load submodules in dependency order (display has no relative imports;
    #    tools imports display; commands/schemas are standalone).
    load_order = ("display", "schemas", "commands", "tools")
    for name in load_order:
        full_name = f"{_PKG}.{name}"
        spec = importlib.util.spec_from_file_location(
            full_name, _REPO / f"{name}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = _PKG
        sys.modules[full_name] = mod
        spec.loader.exec_module(mod)
        setattr(pkg_shell, name, mod)

    # 3. Now exec __init__.py into the package shell.
    pkg_spec = importlib.util.spec_from_file_location(
        _PKG,
        _REPO / "__init__.py",
        submodule_search_locations=[str(_REPO)],
    )
    # Re-use the shell (already in sys.modules) so relative imports bind to it.
    pkg_shell.__spec__ = pkg_spec
    pkg_spec.loader.exec_module(pkg_shell)


_bootstrap_package()
