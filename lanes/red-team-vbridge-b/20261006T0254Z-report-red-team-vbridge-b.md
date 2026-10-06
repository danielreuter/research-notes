---
lane: red-team-vbridge-b
kind: report
created: 2026-10-06T02:54Z
status: final
---

CHECKPOINT 7c5cb816e (05:20Z) [final] evidence art:0e7f1aedabb8a9ab58e91b577ae7e3e1e84589ab0a9aaed644ab9aac46fef0ae (Lean #eval vs Python rows/outputs/values); audit run record art:fb6ffbf0ae7015ae1cb5054a50642baffffd8df28d29d9050672d19452b515b6; friction note:red-team-vbridge-b/20261006T0405Z-friction-cwd-clone-pythonpath
CHECKPOINT 7c5cb816e (05:20Z) [final] GRANT #1271@9a87c37ac and #1272@7c5cb816e; audit r20261006-040139-db49 PASS (replay on, 1750 records match, 3 axioms); labels on remote; note:red-team-vbridge-b/20261006T0400Z-finding-vbridge-b
CHECKPOINT 7c5cb816e (04:01Z) [open] audit r20261006-025421-cbce: verity/Security PASS (1750 guarantees, 3 axioms, replay ok); Proofs FAIL only on runs (warden generate: --cwd clone imports verity from src/<sha>); clean rerun r20261006-040139-db49 with a clone shim
CHECKPOINT 7c5cb816e (03:07Z) [open] B1 diff vs #1090 blob 440b0318: imports/namespace/doc only; Lean #eval of PR defs == Python rows+outputs on SMALL/cons8/edge/mul128, values == gf2k on real part; audit r20261006-025421-cbce running
CHECKPOINT 7c5cb816e (02:54Z) [open] reviewing #1271/#1272 (VBridge B1/B2) at 7c5cb816e; replay audit r20261006-025421-cbce on vy-nebius-1 running
