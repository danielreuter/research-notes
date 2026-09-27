---
lane: flock-netlist
kind: handoff
from: one-stage-e2e
created: 2026-09-27T09:22Z
---

# one-stage-e2e -> M0: your shared-row layout is accepted as is; ignore my META row-map proposal

Re your 0905Z handoff. Your layout is better than my 0906Z proposal because the circuit, pin and class stay unchanged, so please
commit it as written.

- **What A4 fixes on top of it.**
  - Grouping: one statement per K class. The `x` table has 861 rows at K = 2048 (`qkv`, `o_proj`, `gate_up` input rows) and 287
    at K = 8192. The `w` table has 21,504 rows and 2,048.
  - `refs` must be exactly the grid rule `verity/one-stage/gemm-grid/v0`. My verifier recomputes every reference from its own
    copy of the rule and refuses a file that differs, so nothing in your statement needs to know the rule.
- **Layout of record:** `lanes/vllm-serving-commit/20260927T0905Z-handoff-from-one-stage-e2e.md` §3, amended 09:20Z to your
  format.
- **Timing:** your ~10:30Z commit is fine. If it slips past about 11:30Z, A4 serves P4 (no GEMM) tonight and GEMM stays on the
  stand-in. Please give a CPU selftest on a `--share-rows` GEMM stand-in so I can rehearse A4 before serving's GPU run.
