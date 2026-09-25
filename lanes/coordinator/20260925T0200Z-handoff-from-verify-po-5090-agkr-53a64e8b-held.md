---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T02:00Z
---

# verified, label HELD: RTX 5090 NVFP4 A-GKR art:53a64e8b (same statement and proofs as dfbc86c4; verdict art:223c8efe, no label)

agkr-nvf4's 01:50Z record (00145f51, 0.1462 s) supersedes art:dfbc86c4 (0.1604 s) for the cell. The prover changes are
prover-only, so the statement (BOOL_QUADRATIC + PAIRED) and the proof bytes are unchanged, and your 0050Z hold applies. I
registered PASS verdict art:223c8efe and wrote **no label**, so the 5090 A-GKR cell stays art:49757870 (0.1905 s). When you
send "release", I will label from this verdict (`30-verdict-53a64e8b.sh HOLD=0 VID=art:223c8efe`). This result carries
the cell, but art:dfbc86c4 can be released too (verdict art:7d3aaf2e).
- The 3c769c6d verifier build (f271e422) on my pod accepts 5/5 (proof sha256 ebe7c545), taking 0.47-0.53 s each. The
  verifier sources at 00145f51 are identical to 3c769c6d's. The statement regenerated from 00145f51 on my pod is
  byte-identical, and public.bin has 0 rows mismatched against main's frozen NVFP4 set.
- Every proof and statement file is byte-identical to dfbc86c4's, and `27-nvf4-rewrite-check.py` passes again.
- Negatives, all rejected: mutate 148/148; my s flip, t+1, f+1, reordered public line and removed public line.
- Correction to my 0127Z handoff (dfbc86c4): those negatives were mine, not the producer's. agkr-nvf4 named no negatives
  tree, and its own negatives (python 115/115, Rust 56/56) were run with its binaries. The verdict does not change.
- Runs: verify r20260925-015434-8c48, verdict r20260925-015724-d06b.
- Four labels are now waiting for "release": art:45c5be4a (verdict art:df4d2c3c), art:3ae971dd (art:e96f50ac),
  art:dfbc86c4 (art:7d3aaf2e) and art:53a64e8b (art:223c8efe).
