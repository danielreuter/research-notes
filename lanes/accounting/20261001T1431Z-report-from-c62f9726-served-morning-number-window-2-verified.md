---
id: 20261001T1431Z-report-from-c62f9726-served-morning-number-window-2-verified
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **The morning number: window 2 (bdedc145, r20261001-130909-dcae) is timed and verified. Decode is 2.973× and prefill 1.630× over graphed stock FP8.**
- **Verdicts** (verifier bdedc145, done 7:27 AM PDT): prefill ACCEPT 13 tiles, decode ACCEPT 94 over 8,320 matmuls, control REJECT 128, control-leaves REJECT 5.
- **Evidence:** art:4b0b5aed3d86ef0856d9b246e6ab6f81783bcc00941ef9370f1697a60376c0d5 holds the verdicts, manifests and e2e.json, sha-checked against node 2, and the run is too: both PRESERVED. The arm gate, validation and both commitment checks (as timed, and eager) passed; no JIT.
- **It replaces window 1** (b737755b: 3.097× and 1.630×, art:4cbf8588…). bdedc145's `check` r20261001-110405-347d passed (branch `cursor/served-whole-step-graph-e38e`), so it can open as the PR.
- **Pass deleted** (73 GB); disk 47%.
- **Targets:** decode is still 0.07× above 2.9×, and prefill 0.13× above 1.5×. The decode lever is my 14:24Z ask, and its `check` r20261001-142453-d85e is running on node 1. I have no prefill lever without a new ship.
