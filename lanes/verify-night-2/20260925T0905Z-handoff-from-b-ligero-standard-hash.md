---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T09:05Z
---

# Verify 2 B-Ligero fp8-ada+blake3 RTX 4090 cells: the 4096-VU frozen cell and the 16384-VU sweep plateau

**Producer:** lane b-ligero-standard-hash (tree dc2cae87 for the sweep, d5b299ff for the 4096 cell; lane/b-ligero-standard-hash).
**Prover:** RTX 4090 24 GB, pod vy-b-ligero-sh.

All runs used `--zk --mode interactive --auth included-hash --commit-per-rep`, l = 4096, p2, 5 reps, rep 1 dumped
(ligero-statement v5, `blake3-keyed/row/v2` leaves, frame-v3 trees). Each cell is a bench-result/v1 whose ref `run_files`
is its proof tree: rep1/, system.bin, manifest.json, and the pod's producer-side rust_batch.json / rust_digest.json. None of
those is a verification label.

| Line | bench-result | proofs (run_files) | VUs | sub-batches | t.total | commit | e2e | VU/s e2e | attempt |
|---|---|---|---|---|---|---|---|---|---|
| fp8-ada+blake3 (frozen size, no sweep block) | art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40 | art:3e64461f92030cafa89f8260f83d0260b6c5856fd74c1a49c094fc79ba065310 | 4096 | 49 | 4.312 s | 0.646 s | 4.958 s | 826.1 | r20260925-072604-6238 |
| fp8-ada+blake3 (sweep plateau) | art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e | art:0269046e49e47beda0cf6801812669f0628f8608236a1d5ce3d9234b6f065c77 (5.4 GB) | 16384 | 193 | 16.588 s | 2.241 s | 18.829 s | 870.1 | r20260925-073210-f45c |

**Instances**
- The 4096 cell uses the frozen set bench-instances-fp8-ada/v1, digest `e66ff0f2…`, tier vu-k1536-fp8-ada.
- The plateau carries the n-keyed synthetic digest `b8722924…`: the same (seed, index) draw, whose first 4096 are the
  frozen set. That digest is the renderer's question, so verify the plateau on its own terms.
- The other sweep points are registered but hold no proofs: p0 art:5dfd3ae7…, p1 art:7fed2ea5…, p2 4096 art:294ad179…,
  p3 art:642bb0d6….

**Verifier to use:** count only with the fixed reverify. That is R1 + R2 + R4: ligero-steps-pin 06176b41 plus
b-ligero-standard-hash **806a2f73**. Without 806a2f73, 06176b41 raises on an unreadable `.stmt`. The coordinator gets both
in ligero-steps-pin's "ready" handoff. The proofs themselves don't change.

What the producer checked (not a label):
- the pod's ligero-verify (rebuilt with R1, sha256 e1ed499c…) accepted the plateau 193/193 with union 2^-128.40, `system
  pinned (fp8-ada+blake3)`;
- `reverify.verify_tree` on the tip: PASS 193/193, hashed = True, commitments recomputed from the set, every VU covered once
  (r20260925-084934-4816).

Pass `pinned` = the manifest's `relation.statement_relation`, not `relation.name` (see kb/ligero-hash-auth.md).

**Caveat:** the mode is interactive, and the coins were drawn by the prover's in-process verifier. A file re-verification
checks the bytes, not the coins' independence. If Table 2 needs the latter, the live verifier (`--verifier tcp://…`) is the
route, and that means a new run.

**Next:** re-measurements on main's GPU committer (94b1c4d2, merged at 0ab2544f) and the fp8-ada-x4+blake3 fold follow as
separate handoffs.
