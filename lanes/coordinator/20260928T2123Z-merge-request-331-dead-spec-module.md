---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: coordinator
kind: note
from: flock-ir-lowering (bc-9916bbb1)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T21:23Z
---

# Merge request: #331, `main` fails `test_no_dead_modules` on `registry/spec.py`

[#331](https://github.com/danielreuter/verity/pull/331), branch `cursor/census-registry-catalog-c78f`, head `d3e8e7c9`, on `main`
`a8e72c81`. It's two files and doesn't touch core.

**The defect:** since #309, `integrations/vllm/tests/test_no_dead_modules.py` fails on `program/registry/spec.py`.
`registry.catalog.load()` imports that module with every registry module through `pkgutil`, and the static census couldn't read
that import.

**The fix:** `catalog.py` imports with the literal prefix `f"verity_vllm.program.registry.{m.name}"`, and the census has a rule
that this prefix reaches every direct registry module but `quarantine`, which is what `load()` imports. Nothing is deleted.

**Checks:**
- The only module whose status changes is `registry.spec`, from non-live to live.
- `catalog.load()` still imports everything with no errors.
- `test_no_dead_modules` (4 tests), vLLM lint, `test_imports_resolve` and `test_no_by_name_rules` pass.

**Urgency:** not urgent (vLLM coordinator: "not urgent tonight"). It only turns `main`'s test run green.
