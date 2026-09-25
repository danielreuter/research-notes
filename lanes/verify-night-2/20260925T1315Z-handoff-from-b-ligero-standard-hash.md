---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T13:15Z
---

# Two items: the x4 8192 instance-equiv/v1 document is art:d9b3724d (PR #21 shape, coordinator 1124Z), and the x4+blake3-xob sweep plateau is art:ecccca50 (PROVISIONAL, class granted with conditions)

**1. instance-equiv/v1 for fp8-ada-x4 at 8192. art:d9b3724db1d21db49cbd399642685f1a2b4aa8d21d4bab3b6c7623caaf0ca7f3**, PRESERVED.
- It's for art:6b6d4484 / art:19be6afa (the x4 +blake3 8192 plateau). The meta is the tool's document plus `lane` and `provenance`.
- `frozen` is the synthetic stream ref over [0, 8192]: bench-instances-fp8-ada/v1, vu-k1536-fp8-ada, manifest 35a95ed5…, seed 20260922.
- `candidate` is range [0, 8192], manifest 5ca6851d…, the same seed and recipe. equal = true: x / W / y are 02f36a40… / 6930ef27… /
  ad569a39… on both sides. `--check` reproduces the document.
- Tool: main 2c92b9e3's `bench/{instance_equiv,tables,views}.py`, overlaid on my 5b28557b pod tree, because a sweep was running
  from that tree. `git diff 5b28557b 2c92b9e3` touches no relchain, relations or loader file. The tool field reads
  `@5b28557b+bench@2c92b9e3`. Script: `lanes/b-ligero-standard-hash/evidence/pod-scripts/43-equiv-8192.sh`; the document is
  copied to `evidence/equiv/instance-equiv-fp8-ada-x4-8192.json`.

**2. fp8-ada-x4+blake3-xob sweep plateau (PROVISIONAL; red-team-standard-hash 1226Z granted the class with conditions).**
- **art:ecccca50500cecececefcd7dfb4aa97572a1e334332f1c191744489fbeccf82a**, proofs included. Tree art:0785fd3dffe9bb80fcdc3cb3feae85bf32dd22c8b4b4fc06248d8f2e7e9bc5a6.
- Run r20260925-121605-357f at 5b28557b, custody-r2, malloc env, l = 4096 p2, sys f90e7b41 / table 6ecf18da.
- 32768 VUs: t.total 5.723 + commit 0.050 = e2e 5.773 s, 5676 VU/s, 1.89e7×. My Rust run: ACCEPT 97/97 at 2^-128.07,
  python 97/97.
- It's not converged: +0.9% over 16384. 65536 hit a CUDA OOM.
- Its instances run past the frozen 4096, over [0, 32768] of the same stream. Its instance-equiv/v1 (13:19Z, the same script
  with `VUS=32768`) is **art:b6f2e1dfcc3473058aad66d1aa271b4828140f3e667ef646ee176ca81a26109a**, PRESERVED.
  - `frozen` = the stream over [0, 32768], manifest a80b38f2….
  - `candidate` = manifest fd076a29…, which is this result's `workload_fingerprint.instances`.
  - equal = true, and `--check` reproduces it.
- The grant's conditions: re-verify from 5b28557b or later with `reverify.py` + `ligero-verify` (or 06 ROOTS-MATCH), and
  04 BOUND ≤ 2^-128.
- The sweep's SLIM points (1024..16384) are in my report; they're not for verification.

The x1+blake3-xob sweep (r20260925-130720-ab7a) is running. Its plateau follows by about 14:20Z.
