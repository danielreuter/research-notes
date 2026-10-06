---
lane: pouw-e2e
kind: report
created: 2026-10-05T23:29Z
status: final
---

CHECKPOINT b87eeef64 (00:17Z) [final] bound to cursor/pouw-e2e-new-layout-e3fa (pushed, = b87eeef64, no commits: evidence only). PR doc internal/compute-accounting/pouw-e2e-pr.md in the project store
CHECKPOINT b87eeef64 (00:17Z) [final] PoUW e2e on b87eeef64 passes, no fix needed: served r20261005-232920-9a1c ACCEPT prefill+decode, REJECT both controls (art:2477c90f0e15d4210f6428ee2abb70ad1b2af69d90bb539b1eb9bbced4ad65ad); Lean r20261005-233222-098a; VM art:590afe2431e7404a7012457693712e2568384284bfb610553037861b153528c3. Open: pearl_c_u gate pin stale pre-move
CHECKPOINT b87eeef64 (23:59Z) [open] served r20261005-232920-9a1c: prefill ACCEPT (3 drawn, 10 excluded-row tiles of 2,752,512 over 128 matmuls); decode verify on 48 CPU workers, controls next. VM evidence art:590afe2431e7404a7012457693712e2568384284bfb610553037861b153528c3
CHECKPOINT b87eeef64 (23:39Z) [open] Lean r20261005-233222-098a (n1): RouteU built (1001 jobs), ncp_lean.json regen via Lean byte-identical. Served r20261005-232920-9a1c (n2): ship from b87eeef64, window 6.5 GPU-min exit 0, gates true, retained passes repeat commitments; CPU verify running
CHECKPOINT b87eeef64 (23:29Z) [open] b87eeef64 on VM: pouw suite 708 pass/2 skip, benchmarks/pouw 548/18 skip (fresh); 6/7 scheme vectors regen byte-identical, pearl_c_u differs only in its stale gate block (pre-move, 5f6a31c75); next: Lean ncp_lean r20261005-232900-e801 (n1), served r20261005-232920-9a1c (n2)
