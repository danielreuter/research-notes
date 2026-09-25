---
lane: verify-night-3
kind: report
created: 2026-09-25T14:31Z
status: open
---

CHECKPOINT 977ad27b (14:59Z) [open] accepted: xob b47828e4 (vd cc5f72de), bb69174b (99a5a9fd), ecccca50 (47cf9051); sha256 fcd6a623 (192c1ed9, via reverify fix 977ad27b). Handoff red-team-standard-hash-2 1502Z. Running 4aa258ee r20260925-145803-dd7d
CHECKPOINT 977ad27b (14:51Z) [open] xob b47828e4 + bb69174b PASS (labels pending push); ecccca50 running. sha256 fcd6a623 ERROR (tree has proofs at root, no proofs/): reverify patched 977ad27b to read root layout, rerunning; 4aa258ee fetching
CHECKPOINT a5d9b632 (14:45Z) [open] equiv art:d9b3724d (x4 8192) -> verdict art:73aa7efe, art:b6f2e1df (x4 32768) -> art:7b44bcad: both --check reproduce, equal=True, candidate == result instances; verified=accepted, preserved. Renderer _equiv_content @2c92b9e3 still wants frozen==[0,4096] (coord told). Running: reverify sha256 fcd6a623/4aa258ee, xob b47828e4/bb69174b/ecccca50
CHECKPOINT a5d9b632 (14:38Z) [open] H100 +blake3 table rows (c8730574 7c6b4647 9c11326c 7a3965da) already verified=accepted by verify-night-2 -> item 3 done. Pod bootstrapping (frozen set + cargo). Queue: equiv d9b3724d/b6f2e1df, sha256 4aa258ee/fcd6a623, xob b47828e4/bb69174b/ecccca50
CHECKPOINT a5d9b632 (14:35Z) [open] pod vy-verify-night-3 k2ww8qvkhxlvab (cpu3c 16vCPU, 150GB, guard 30) bootstrapping r20260925-143459-f66c; verifier tree lane/verify-night-3 a5d9b632 = main 2c92b9e3 + 5b28557b (xob pins); next: equiv d9b3724d/b6f2e1df, sha256 x4
CHECKPOINT 2c92b9e3 (14:31Z) [open] started 14:33Z (relaunch of verify-night-2); branch lane/verify-night-3 @2c92b9e3; reading inbox; queue: x4 equiv d9b3724d/b6f2e1df, +sha256 x4, H100 +blake3, xob
