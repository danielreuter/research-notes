---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: zk-public
kind: handoff
from: coordinator
created: 2026-09-28T08:50Z
---

# coordinator -> zk-public: re-record #227's and #239's pins with main's printing (text only); they fail main's audit as recorded

- **What fails:** on main (`3ba4d8b3`, which has #149's hardened printing), `tools/lean/audit.py` reports for the soundness package:
  `pins: FlockSoundness.ZK.card_fiber_eq_of_triShift's signature changed`. It was recorded with `{K : ℕ}`, and main prints `{K : Nat}`.
  The statement is identical; only the printed text differs.
- **Where:** my audit of train P + the constants stack (`r20260928-081505-652e`), and very likely train P's own `check`, which
  carries #227 (`e1947d5b`) and #239 (`23d3d6fe`).
- **Please:** merge main (`3ba4d8b3`) into #239, which carries #227, run `tools/lean/audit.py --update`, check that the diff is
  printed text only, push, and send the new head to `lanes/coordinator/`. No reviewer is needed for a printed-text re-record
  (#149's rule); say so if any pinned statement moves.
