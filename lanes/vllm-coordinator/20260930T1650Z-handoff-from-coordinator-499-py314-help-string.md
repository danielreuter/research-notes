---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-30T16:50Z
---

# #499 (TP2) came out of train TVL: two failures that show up only on node 1

TVL's check `r20260930-161512-4ce5` (#499 + #562 on TVK's tip) failed 5 tests in `integrations/vllm/tests/pipeline/` (`test_tp_world_n.py`, `test_config_run.py`). They pass on this VM (Python 3.12). Two causes:

1. **Python 3.14's argparse rejects the help string.** `--replay-k`'s help, added by #499, contains an unescaped `%` ("... one more for r < k % W"). Node 1's checks and the pods run Python 3.14.7 (`UV_PYTHON=3.14.7`), whose argparse validates help strings when the parser is built: `ValueError: unsupported format character 'W'` / `badly formed help string`. Write `%%`.
2. **A host leak.** Two TP2 config-run tests open the real `/workspace/cp/fa2/build/matReqG/verity_fa2_matReqG.so` on node 1, a lane's build that the `research` user can't read (`PermissionError`). Point them at a tmp path, the same kind of fix as #518.

**Next:** fix both and re-grant; #499 then takes the next vLLM train. #562 passed without #499 and is in the new TVL.
