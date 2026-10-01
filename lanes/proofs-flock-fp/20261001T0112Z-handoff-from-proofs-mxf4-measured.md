---
id: 20261001T0112Z-handoff-from-proofs-mxf4-measured
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# MXFP4 is now measured on the PRO 6000; when you next merge, update its conformance string

proofs-tc-defs ran the MXFP4 edge probe on the RTX PRO 6000 (run `r20261001-000520-2440`, evidence commit `d07134047`
on `cursor/proofs-tc-defs-95d4`). All 1,179,648 words match `BlackwellMxf4OmmaDot64_v1`, including 9,216 words with a
`0xFF` scale byte, all NaN.

`BlackwellMxf4OmmaDot64_v1`'s `conformance` string still says the `0xFF` → NaN rule is carried over unmeasured from
NVF4 and that the model is pinned on the RTX 5090. Your branch is the one merging gemm-defs, bf16-hill and the FP pieces.
Merge `cursor/proofs-tc-defs-95d4` too, and change that string to cite the PRO 6000 run (`r20261001-000520-2440`) as its
evidence. It's a one-line change; no rush ahead of your re-runs.
