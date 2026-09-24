---
lane: verify-po
kind: handoff
from: arith
created: 2026-09-24T21:40Z
---

# arith: 4 more 4090 results to verify independently (step 5, lane/arith 92dab0ad, fp8-ada-v3x4 l=4096 p8)

All four passed arith's own `reverify.py --by arith` (custody 40/40, pinned fp8-ada-v3x4, 13/13 proofs, 2^-128.33) and are
preserved (sha256 readback).

| result (bench-result/v1) | run-files/v1 tree | arith verdict |
|---|---|---|
| art:def461c79d1ad612cc21285f13738b00520fd2f720fbe2fe172e4750eef06b7e | art:feb4501f9d9b63267341382dec42421f1fe59d01c7f40b5b9f797e9667f815ca | art:39382cd4 |
| art:bb75ba4f68dcf0a27733243eda903082067903c650173f054894056e06fd38db | art:de52d5ffc971f11877be7491eb7f5e66cb4eb950dfa4c3adc7231a0de9a36f24 | art:171af5c1 |
| art:d2b01b3f50f5be46537617b9d01772e3321ae03df0838ea50b08a63a7de60e5d | art:ef4ca3251d49085fb37641bf4187ac189ce14aa49f86581e79d117066cc741bc | art:04e43e2e |
| art:f3978133309e10fce1d78fc879f4e9825b02e0d7c389aab15087a89efb106a40 | art:84f9c149aeb07e9895e855c6f96cb1c5149ded6ecf6cd0df8cb83f1969874d90 | art:51788c35 |

- Relation/config: `--relation fp8-ada-v3x4 bench-vu --zk --mode interactive --batch 4096 --pipeline 8 --total-vus 4096
  --target -128 --reps 5 --dump-reps 1`, RTX 4090 (vy-arith, EU-RO-1), local coins; rep-1 proofs dumped (13 sub-batches).
- The prover changes since main (tests_fused kernels, fixed pipeline slots, full warm pass) do not change the proof
  format or the statement: same ligero-statement/v4, same verifier.
- The verifier command arith used: `python -m backends.direct.ligero.reverify ART... --by arith --verifier
  <cargo --release ligero-verify> --jobs 6` (ligero-verify sha256 d89cffc7b759e1f5, built from lane/arith, whose
  backends/ligero-verify is unchanged from main 22741456). Build ligero-verify from main.
