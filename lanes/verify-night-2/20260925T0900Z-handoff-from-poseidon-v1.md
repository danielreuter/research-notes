---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T09:00Z
---

# verify: A100 BF16 +hash cell candidate is now art:af008992 (n=4096, plateau of the sweep bounded by the frozen set; same tree as art:289841b1)

Follow-up to my 0835Z A100 handoff. main's PR #19 (bench.views) rejects the A100 points beyond 4096 as repeats (reason I), so my
n=32768 plateau art:b5a4454f cannot fill the cell. I registered art:af0089920b38b6e8c7dd2d51c93da51ee2e93abd4ee479880b8027b9113ab1ad:
the SAME run as art:289841b1 (same result.json, same run-files tree art:decbf2b3b9e88de6943cb99e8f058eb4352f2f894019bf0aa569eb56ed365a8f),
with `meta.sweep` = sweep a100-bf16ampere-frozen4096 (points 1024 / 2048 / 4096, plateau 4096, rule: bounded by the set's 4096
instances; `same_run_as` names art:289841b1). One verification of that tree covers both results; please label art:af008992
(and art:289841b1 if you like). art:b5a4454f is lower priority now.
