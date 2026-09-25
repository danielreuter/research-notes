---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T05:12Z
---

# Integration a2edab4d: good evidence, but I merge it only on top of main's circuit pins (#13): send "integration ready v2"

a2edab4d merges textually clean onto main c1891d48, but main now pins A-GKR circuits (#13) and a2edab4d adds no fp8-ada / fp8-hopper /
fp4-nvf4 pin lines, so main would refuse every FP8/NVFP4 A-GKR verify after the merge. Please (before continuing step 2 past the
public-input version, see 0507Z):
1. merge origin/main (>= c1891d48) into lane/agkr-bound (merge, not rebase);
2. add the pin lines for the statements the verified cells use (docs/agkr-circuit-pin.md in the Project store has the exact
   non-merged lines; add the merged-LK ones for art:45c5be4a / art:ad76c106 / art:f277786d's statements as that doc describes);
3. on your pod: `cargo test --release` of backends/gkr/verifier (Rust >= 1.89), and one bench_result cell per family with
   `--relation` showing `circuit_pinned: true` and the same proof sha256 as in your 0500Z table;
4. handoff "agkr integration ready v2: <sha>". I merge that into main at once.
