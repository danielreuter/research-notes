---
lane: coordinator
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T13:20Z
---

# Your 1124Z: the x4 8192 instance-equiv/v1 is art:d9b3724d, sent to verify-night-2. blake3-xob now has a conditional class grant (red-team 1226Z), and the x4 xob plateau is 5676 VU/s at 1.89e7×. Decision: merge 5b28557b's blake3-xob?

**1. Rule I for art:6b6d4484 / art:19be6afa.**
- **art:d9b3724db1d21db49cbd399642685f1a2b4aa8d21d4bab3b6c7623caaf0ca7f3**, PRESERVED, in the PR #21 shape.
  - `frozen` = the stream ref over [0, 8192] (manifest 35a95ed5…, seed 20260922).
  - `candidate` = range [0, 8192], manifest 5ca6851d…. equal = true, and `--check` reproduces it.
- It came from main 2c92b9e3's `bench/{instance_equiv,tables,views}.py` overlaid on my 5b28557b pod tree (no loader diff);
  the tool field says so.
- Sent to verify-night-2 at 1315Z. My 1142Z "the schema can't express 8192" is superseded, and I did not re-register 4096,
  per your 1125Z.

**2. blake3-xob class.** red-team-standard-hash 1226Z: CLASS GRANTED WITH CONDITIONS for fp8-ada(+x4)+blake3-xob at 5b28557b.
- Scan: 0 free rows in 47,764 and 95,384 mutations; the control finds 16.
- The twin relabel is refused both ways. H2, R1 and R4 pass.
- The conditions:
  - re-verify with `reverify.py` + `ligero-verify` from 5b28557b or later, or with 06;
  - 04 BOUND ≤ 2^-128;
  - the run is at 5b28557b or 672b23ae.
- verify-night-2 (1230Z) reviewed the verifier diff and will build a second verifier from main plus the 9-file diff.
- **Decision for you:** merging `lane/b-ligero-standard-hash` at 5b28557b would give main the scheme and pins, so every lane
  could use one verifier. Files:
  - ligero: witness(_device).py, the leaf files, registry, frame_gpu.py;
  - ligero-verify: leaf.rs;
  - tests.
  It does not change the +blake3 pin (71f39e44 is kept, and the refactor is verified).

**3. The x4 +blake3-xob sweep** (r20260925-121605-357f, PROVISIONAL, custody-r2, malloc env).
- 1024..32768 VUs: 4119 / 4737 / 5189 / 5506 / 5626 / 5676 VU/s. 65536 hit a CUDA OOM.
- Plateau 32768: e2e 5.773 s (t.total 5.723 + commit 0.050), **1.89e7×**, Rust ACCEPT 97/97 at 2^-128.07. That's
  art:ecccca50…, tree art:0785fd3d…, with proofs.
- It's not converged: +0.9% over 16384. The 24 GB of VRAM is the ceiling. Compare x4 +blake3 at 4096: 5.19e7×.
- Its instances are [0, 32768] of the same stream. Its instance-equiv/v1 is art:b6f2e1dfcc3473058aad66d1aa271b4828140f3e667ef646ee176ca81a26109a
  (candidate fd076a29…, equal, reproduces), sent to verify-night-2.

**4. Running:** the x1 +blake3-xob sweep, r20260925-130720-ab7a: 1867 / 1991 / 2026 VU/s at 1024 / 2048 / 4096 so far. FINAL
by 15:00Z.
