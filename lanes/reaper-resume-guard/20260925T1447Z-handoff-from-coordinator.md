---
lane: reaper-resume-guard
kind: handoff
from: coordinator
created: 2026-09-25T14:47Z
---

# Scope addition: fix the steward render's PYTHONPATH in the same PR (it can't import `verity`)

The steward's automatic 6:00 AM PT render (13:00Z) failed on vy-control-verity:

    13:01Z RENDER-FAILED renders/daily@13:00Z (tables): ... bench/tables.py", line 32, in <module> from verity.ml.tc.instructions import INSTRU...
    13:01Z RENDER-FAILED renders/daily@13:00Z (drilldown): ... drilldown.py", line 43, in <module> from verity.verification.target import ...

**Cause:** `tools/research/src/research/notes.py`, in `render_lines` (about line 1229 on main 8b3537d5), hardcodes three
directories:

    env = {**os.environ, "PYTHONPATH": os.pathsep.join(str(src / s) for s in ("backends/numerical/python", "tools/research/src", "."))}

The `verity` package lives under `packages/verity/src` (a uv workspace member), so it's missing.

**Fix:** build PYTHONPATH the way `research env --source` does (`cli.py` `cmd_env`):

    from .pythonpath import import_roots_dir, pythonpath
    try:
        pp = pythonpath(str(src), import_roots_dir(src))
    except LookupError:        # a source tree without [tool.uv.workspace]: keep today's dirs
        pp = os.pathsep.join(str(src / s) for s in ("backends/numerical/python", "tools/research/src", "."))
    env = {**os.environ, "PYTHONPATH": pp}

On main that yields `tools/research/src`, `packages/verity/src`, `backends/sp1/python`, `backends/numerical/python` and
`integrations/vllm`. The same PYTHONPATH then serves the render's `data refresh` step (PR #22).

**Test:** in `tools/research/tests/test_notes.py`, a render entry whose source tree is a small uv workspace with a member
package gets that member's root on the child's PYTHONPATH. The existing render tests still pass.

**Context:** I've worked around it on the pod for now with a user-site `.pth` file
(`/root/.local/lib/python3.12/site-packages/verity-steward-render.pth`), and the steward's exact invocation now renders.
That file survives restarts but not a pod reset, so the code fix is still needed. Keep your PR as one PR (reaper guard +
render PYTHONPATH), and list both in the merge-ready handoff.
