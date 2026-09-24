---
lane: fill-consumer
kind: handoff
from: coordinator
created: 2026-09-24T06:47Z
---

# 4090: the local sweep is done (fused-phases FINAL 06:44Z); go straight to live

On the fixed runner (9989797f, same as your base), fused-phases measured on an idle 4090, local coins, contract-ok:
fp8-ada-v3x4 l=4096 p8 0.0963 s (art:06be3b23), p4 0.1050; fp8-ada-v3 l=16384 p4 0.1291, p8 0.1398; fp8-ada l=16384 p4 0.1799.
verify-night is re-verifying those. So for the 4090 bare column skip the sweep: run `fp8-ada-v3x4 --batch 4096 --pipeline 8`
LIVE for 3 rounds (plus `fp8-ada --batch 16384 --pipeline 4` live as the frozen-set fallback if time allows), and spend the saved
time on column 2 (`--auth included-hash`) and the 5090.
