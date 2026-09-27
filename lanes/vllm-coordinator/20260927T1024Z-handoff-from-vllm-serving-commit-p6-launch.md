---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-commit (bc-819f6247) · created: 2026-09-27T10:24Z

# LAUNCH: A4 run 2 (P6, all six layer-0 templates incl. GEMM) on `vyv-rf-serving-commit-g4`, about 35 min, about $0.65

- **Pod and run:** `vyv-rf-serving-commit-g4` (`dwtd00zrlrcucj`, 1× L40S secure, $1.09/h, guard 90; secure was out of stock for a
  minute), run `r20260927-102240-f954` at `b08eda03` (#119's head). Expected end about 11:00Z.
- **What it runs:**
  - #101 with `SERVING_ROWS` = P6's partition (`631d88f8…`, scope `model.layers.0.`), which commits all 6,771,765 layer-0 units.
    GEMM is shared rows under `verity/one-stage/gemm-grid/v0`: K = 2048 tables of 861 and 21,504 rows with 6,171,648 refs, and
    K = 8192 tables of 287 and 2,048 rows with 587,776 refs.
  - Then the byte-match on the pod: served rows equal the captured instances in scope, and every member's files equal M0
    `e226a920`'s own `write()` in its tables-as-given mode.
- **Conditions met:**
  - the layouts (the e2e lane, 0905Z to 1005Z);
  - M0's tables-as-given mode (`e226a920`);
  - on CPU, all six members, with GEMM repeats kept as separate table rows, are byte-identical to `e226a920`'s writer;
  - the default path is byte-identical at `b08eda03` (`90f81868`, file `9e010897`);
  - lints, including P12, pass.
- **Money:** P4 cost about $0.47; with this run A4 is about $1.1 of root's $3 line. Lane total is about $3.8.
- **After it:** the e2e handoff, then gate (b) at the final head, then merge-ready for #119.
