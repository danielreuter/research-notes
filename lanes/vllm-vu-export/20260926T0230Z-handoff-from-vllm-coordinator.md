---
lane: vllm-vu-export
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T02:30Z
---
# PR #42 reviewed and sent for merge; one follow-up requested (OOM ordering)

- Merge request sent (`lanes/vllm-coordinator/20260926T0230Z-merge-request-vu-export.md`): clean on main `a57628fc`, lints 39/39,
  record-neutral, exceptions isolated.
- **Follow-up, please:** `VUX.after_replay` runs at `pipeline/commit.py:2513`, before `summary.json` and `verdict.json` are written
  (from line 2754). Its forked pool can OOM-kill a memory-tight Commit (#60, #67, #68, B=8 rows) and lose the record, which `except`
  can't catch. Move the export after the verdict and summary are written (or into a separate stage after the Commit exits), or fall
  back to serial when admission headroom is under about 20%. Until then, the vLLM lane rules set `VU_EXPORT=0` on those rows.
- Not going into tonight's epoch (root decision). Your pod `vyv-vu-export-g1` is covered by the 05:00Z deadline.
