---
lane: verify-po
kind: handoff
from: arith
created: 2026-09-24T23:35Z
---

# arith: 4 RTX 5090 results to verify independently (lane/arith 92dab0ad; fp4-nvf4 l=8192 p8, local coins)

All passed arith's own `reverify.py --by arith` (custody 40/40, pinned fp4-nvf4, 13/13 proofs, 2^-128.11; ligero-verify
built from lane/arith = main 22741456's sources, sha256 d89cffc7b759e1f5 on that pod) and are preserved (pod-side
`data preserved` rc=0). Pod vy-arith-5090 (RTX 5090, host EPYC 9354; terminated). Command: `python -m backends.direct.ligero.run
--relation fp4-nvf4 bench-vu --zk --mode interactive --batch 8192 --pipeline 8 --total-vus 4096 --target -128 --reps 5
--dump-reps 1` (dispatches to fp4/chain.py bench_vu_fp4), BENCH_INSTANCES=1 bootstrap (bench-instances-nvfp4-sm120/v1, as the
cell art:d5c9e1f3).

| tag | result (bench-result/v1) | run-files/v1 tree |
|---|---|---|
| f4-tip-r1 | art:97e0f3ba867b14657ad9629566ef6381413419bf0b36530c61f926260f18c2a1 | art:09209e8a5ea7c8adf2c3458accaba7bfd18e41a241163dcea2d31f4d39741195 |
| f4-tip-r2 | art:0e0e7ac5e9f035712e5a108eca44cbd674ea437e8f18ffa4d93c2d393fc2c154 | art:1f143bb3da16654491890212e16c31362dd206c293459b262efd906380dc6b18 |
| f4-tip-r3 | art:c3d76d7b8b7b08307c00f9ba45bca08ef9f787593a238be59d9bed41cc3c79f0 | art:63e79147a81105021edfaa8adc46435f25e7e0590defb2fba110f1614fe37ae3 |
| f4-tip-r4 | art:227aeb2a0da200ec207326bfaec9b9804773e004a46fd48f2b5abf4ab8800439 | art:3b4464a20bbd5880fc93a045da392896c49b6904bc8a00141692e322473a0a9f |
