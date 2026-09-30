---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 20260930T0557Z · re: GO 0522Z

Re-granted: #470 @ c7db5d88 and #439 @ c65fa2fc (both clean on main eeaa6847; labels pushed 05:53Z). #467 @ 7b8eb2e1 stands.

TP is a coverage axis, but `row.py` refuses `--config-run 1` for tensor-parallel rows ("covers single-GPU rows for now"). Until that changes, TP2/TP4 cells are `ov.gate unsupported:config-run-tp`, recorded without pods. Extending the config run to TP2 (per-rank Build + build-global merge, one instrumented Commit, replay on both ranks) is the next config-run PR after the first TP1 breadth pass. Size it and tell me if it is more than a small change. Also: sm_120 full rows (with Match) fold sm_120 linears as Unsupported; config runs skip Match, so this does not touch the sweep. Assumption monikers for `finding:<cause>` labels are in docs/semantic-assumptions.md.
