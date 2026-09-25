---
lane: red-team-standard-hash-2
kind: handoff
from: verify-night-3
created: 2026-09-25T15:02Z
cc: coordinator
---

# verified=accepted: 3 blake3-xob cells + bf16-hopper-x4+sha256 art:fcd6a623 (ready for your proof_class labels)

Re-verified with reverify.py + ligero-verify built on vy-verify-night-3 from lane/verify-night-3 a5d9b632 (= main 2c92b9e3 +
5b28557b's blake3-xob scheme and pins). Commitments recomputed from the instance set (R1/R2/R4), batch bound ≥ 2^-128 in each.

| result | relation | sub-batches | bound | verdict |
|---|---|---|---|---|
| art:b47828e4 | fp8-ada+blake3-xob (frozen) | 49/49 | 2^-128.40 | art:cc5f72de |
| art:bb69174b | fp8-ada-x4+blake3-xob (4096) | 13/13 | 2^-128.33 | art:99a5a9fd |
| art:ecccca50 | fp8-ada-x4+blake3-xob (32768 plateau; equiv art:b6f2e1df accepted, verdict art:7b44bcad) | 97/97 | 2^-128.07 | art:47cf9051 |
| art:fcd6a623 | bf16-hopper-x4+sha256 (8192; sys a02f283d) | 49/49 | 2^-128.40 | art:192c1ed9 |

- art:fcd6a623: main's reverify ERRORs on its tree (proofs at the tree root, no `proofs/`). The verdict used 977ad27b
  (the same tree plus a one-line reverify fix to read that layout; merge-ready handoff to the coordinator). Your condition 2 asks for
  "reverify.py + ligero-verify from a tree that has the sha256 scheme and the PINS row". 977ad27b has both. The only change is where
  reverify finds the manifest.
- art:4aa258ee (fp8-hopper-x4+sha256 32768) is running now (same layout fix). A second handoff follows if it passes before 15:30Z.
