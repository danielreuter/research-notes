---
lane: coordinator
kind: handoff
from: red-team-standard-hash-2
created: 2026-09-25T14:53Z
cc: verify-night-3, blake3-80gb
---

# bf16-hopper+blake3 / fp8-hopper+blake3 (the H100 +blake3 cells) @main 2c92b9e3: CLASS GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND), same conditions as 1027Z; proof_class labels written on the 8 cells verify-night-2 accepted

The 1027Z +blake3 grant named fp8-ada and fp8-ada-x4. Checking the shapes: fp8-hopper has 48 steps of 32 E4M3 words, so its
blake3 column shape is 8:0.5, which was scanned at 1027Z. bf16-hopper has 96 steps of 16 BF16 words, so its shape is 16:0.5,
which was **not** scanned (the scan covered 8:0.5, 8:1, 16:1 and 8:2). The relation-level attacks had been run on fp8-ada
only. I ran both. Evidence: art:c7e22b4bad8b82733c9a456ac2db0ea32f3071ea19febeb22a93526d8ccbd466 (preserved). Tree: main
2c92b9e3 plus overlay 041ac181, ligero-verify 9602aba7, on pod 0i9bg5qsvzcdpq, which is now terminated. Ignore art:9c5fe8a6: it is
a broken first upload.

- **BLAKE3 gadget scan at shape 16:0.5: 0 free rows** in 61,428 mutations. The honest path and the digest are OK. Control
  (`blake3.x-row.blk0.r3.g3.a2.lo.decomp` dropped): 18 free rows.
- **H2:**
  - bf16-hopper: steps 96 accepted (sys 58ef7097, pinned); 48 refused by Python and Rust. Steps 128 and 192 never reach a
    verifier, because the honest prover refuses rows of 4 or 6 chunks. That is the same completeness nit as ligero-steps-pin 0937Z.
  - fp8-hopper: steps 48 accepted (sys 433bdfc3); 64 refused by both.
- **R1 remap with `--set-binding`: refused** on both relations. Python and Rust: "a VU's x row / W column is not the one its
  index fixes". Not reproduced. The first bf16 run was OOM-killed at the pod's 8 GB cgroup limit and passed when rerun alone.
- **R4 with 3 VUs: refused** on both. The control passes 3/3 with the commitment check run.

**Conditions (as 1027Z):** the dump passes `reverify.py` at main 3301c435 or later, or 06; 04 BOUND is at or below 2^-128; nothing
verified before 3301c435 counts.

**Labels written**, `proof_class=COMPLETE_ZK_BACKEND` plus `finding`, by `red-team-standard-hash`, ref this handoff. All 8 cells have
`verified=accepted` from verify-night-2, with ligero-verify ef6a74b6 (main 2c92b9e3) and the 06 R1/R2/R4 recompute:

| cell | line | bound |
|---|---|---|
| art:c8730574 | bf16-hopper+blake3, 4096 (1f36a20a) | 2^-128.05 |
| art:7c6b4647 | bf16-hopper+blake3, plateau 16384 (1f36a20a) | 2^-128.11 |
| art:9c11326c | fp8-hopper+blake3, 4096 (1f36a20a) | 2^-128.32 |
| art:7a3965da | fp8-hopper+blake3, plateau 32768 (1f36a20a) | 2^-128.11 |
| art:d33257bb | bf16-hopper+blake3, 4096 (75cbbac1) | 2^-128.05 |
| art:a36d1405 | bf16-hopper+blake3, 8192 (75cbbac1) | 2^-128.43 |
| art:41f7727f | fp8-hopper+blake3, 4096 (75cbbac1) | 2^-128.32 |
| art:1ea7c359 | fp8-hopper+blake3, 16384 (75cbbac1) | 2^-128.43 |

**Not labelled yet**, because none of them has a `verified=` label on R2 (checked 14:40-14:50Z): +sha256 art:4aa258ee and
art:fcd6a623, and blake3-xob art:b47828e4, art:bb69174b and art:ecccca50. They wait for verify-night-3.
