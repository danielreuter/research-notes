---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T07:32Z
---

# Merge request: PR #388, the `EPOCH_NOW` clock seam (`test_epoch_row` reads no clock), before the follow-up's first launch

- **The PR:** [#388](https://github.com/danielreuter/verity/pull/388), branch `cursor/epoch-now-seam-2622`, head `2b82ddf6`, one commit on main `610ee10f` (T6, carrying
  #352). It isn't a GO prerequisite; the vLLM coordinator (07:01Z) wants it before the first launch, so that a flaky `check` can't block that train.
- **The change:**
  - `epoch_row.sh` measures its deadlines from `now()`, which is `EPOCH_NOW` when set, else `date +%s`.
  - `verity-vllm epoch job` reads no clock.
  - `test_epoch_row.py` fixes the job's start with `EPOCH_NOW` set to it. `tests/test_no_wall_clock.py` drops its two `ALLOWED` entries for
    that file, as bc-01468472 described.
- **Tests:** `test_no_wall_clock.py` (4), `test_epoch_row.py`, `test_epoch.py` and `tests/lint` pass. Three runs passed under a load average above 4.
- **No digest moves.** It needs a recorded `check` of `2b82ddf6`.
