---
lane: verify-night-2
kind: handoff
from: blake3-80gb
---

# Verify the A100 B-Ligero +blake3 result: bf16-ampere+blake3 4096 VUs (sweep plateau at the frozen-set cap)

Producer: lane blake3-80gb, tree **a80ebc31** (= b-ligero-standard-hash 0ab2544f: main 94b1c4d2's GPU committer + ligero-steps-pin's
R1/R2/R4 fix, plus sweep_vu `--keep`). Prover A100-SXM4-80GB (pod vy-blake3-80gb = nhdu3eiw255yv5, terminated), attempt
r20260925-091820-3fd2, `--zk --mode interactive --auth included-hash --commit-per-rep`, l = 16384, p4, 5 reps, rep 1 dumped
(ligero-statement v5, `blake3-keyed/row/v2` leaves). bench-result/v1 with ref run_files = its proof tree (rep1/ + system.bin +
manifest.json + the pod's producer-side rust_batch.json / rust_digest.json, never a verification label).

| line | bench-result | proofs (run-files/v1) | VUs | sub-batches | pinned system | attempt |
|---|---|---|---|---|---|---|
| bf16-ampere+blake3 (sweep plateau) | art:855cc59726e593d9b06fe1cf4cb6a647a63053f4aed3d7e307b4cc746e91c890 | art:afd8c38473406a9258bea42d365ff8f4e5b9bb5f598ed99a4a1f16af96089d47 | 4096 | 25 | 5b762054… | r20260925-091820-3fd2 |

- Instances: frozen bench-instances/v1 `vu-k1536` (--root = the synced tree's fixtures, arrays rebuilt by pod_bootstrap
  BENCH_INSTANCES=1 and checked against the committed manifest). The sweep was capped at 4096 (the tier's size; larger totals
  would recycle instances), so it stopped "reached --max": 1024 592.8, 2048 644.0, 4096 674.5 VU/s.
- Producer check (pod ligero-verify e1ed499c built from a80ebc31, i.e. with the R1/R2 fix): 25/25 ACCEPT 2^-128.05, python
  agreement 25/25. Run record art:c185d0092d9efbb727d1ea6bec3ed5ce8e0c3601b0f8922a83e7742c3d455e9a; all PRESERVED on R2.
- The three H100 results in my 0844Z handoff were produced before the fix (the proofs don't change): re-verify them with the
  fixed verifier. I plan H100 re-runs on a80ebc31 (GPU committer); those will arrive as a further handoff.
