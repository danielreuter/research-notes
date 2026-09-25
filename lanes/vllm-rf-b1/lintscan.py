"""Laptop-side AST lint scan (stdlib only, never imports verity_vllm): runs every zero-argument test function of
integrations/vllm/tests/lint/test_p*.py and prints the assertion text of the failing ones."""
import importlib
import inspect
import sys
import traceback
from pathlib import Path

root = Path(sys.argv[1]).resolve()          # the worktree's integrations/vllm
only = set(sys.argv[2:])
sys.path.insert(0, str(root))
bad = 0
for p in sorted((root / "tests" / "lint").glob("test_p*.py")):
    if only and p.stem not in only:
        continue
    mod = importlib.import_module(f"tests.lint.{p.stem}")
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if not name.startswith("test_") or fn.__module__ != mod.__name__ or inspect.signature(fn).parameters:
            continue
        try:
            fn()
        except AssertionError as e:
            bad += 1
            print(f"FAIL {p.stem}::{name}\n{str(e)[:6000]}\n")
        except Exception:
            bad += 1
            print(f"ERROR {p.stem}::{name}\n{traceback.format_exc()[-3000:]}\n")
print(f"{bad} failing")
