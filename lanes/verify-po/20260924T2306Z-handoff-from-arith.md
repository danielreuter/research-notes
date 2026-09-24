---
lane: verify-po
kind: handoff
from: arith
created: 2026-09-24T23:06Z
---

# arith: 4 A100 results to verify independently (lane/arith 92dab0ad; bf16-ampere-v3 l=16384 p8, local coins)

All passed arith's own `reverify.py --by arith` (custody 76/76, pinned bf16-ampere-v3, 25/25 proofs, 2^-128.05; ligero-verify
built from lane/arith = main 22741456's sources, sha256 f7e9bf575d522cee on that pod) and are preserved. Pod vy-arith-a100b
(A100-SXM4-80GB, US-KS-2). Command: `--relation bf16-ampere-v3 bench-vu --zk --mode interactive --batch 16384 --pipeline 8
--total-vus 4096 --target -128 --reps 5 --dump-reps 1`, BENCH_INSTANCES=1 bootstrap, LIGERO_REFERENCE_HINTS=0.

| tag | result (bench-result/v1) | run-files/v1 tree |
|---|---|---|
| a16-tip-r1 | art:5bcbf3fb67cbd1b49df2120b87e62b7643c44a39f780537cda3df682a9b7db52 | art:61bc49022826473e959de5e09516e34e251a1c0cbd4ae2dc30b8ca12c6aa9ad6 |
| a16-tip-r2 | art:b83f1ff0815bb6a767c01c1ee1b1220ac1a8ddad5cf4f4a0633d430be03e96a7 | art:bf3e9ac8a46503fa5d7f8e8f4ce9e5941588d613172354b81f31ca9d1b71c6fb |
| a16-tip-r3 | art:4e87bc8acbfff9630e3030e2cd176db6de17f9a1144b1f769bcd50152562443e | art:4d0b8cde7f2070b4dd2a89fde80ba3ccbf98cb00c438160210c7b3e057e07c51 |
| a16-tip-r4 | art:228f07b15a1298e4b231bd06a9aa19e64e709ecbaa1cae89baa49909b37850ab | art:bfec2c1292f3eeefb08d70a1252786927ed18de07f5dd6feaf347ab9f6a730e9 |
