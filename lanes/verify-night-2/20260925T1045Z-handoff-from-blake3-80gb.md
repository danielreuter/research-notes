---
lane: verify-night-2
kind: handoff
from: blake3-80gb
---

# Verify 4 B-Ligero +blake3 H100 re-measurements on 75cbbac1 (main 3301c435 + GPU committer, glibc malloc tunables set)

Producer: lane blake3-80gb, tree **75cbbac1** (main 3301c435 = steps pin + R1/R2/R4 reverify; b-ligero-standard-hash 0ab2544f; my
sweep_vu `--keep`). Prover H100 80GB HBM3 (pod vy-blake3-80gb = 0std0gx3ah22o1), attempt **r20260925-095924-a6ec**, env
MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 (coordinator 1003Z; not yet in this tree's fingerprint).
`--zk --mode interactive --auth included-hash --commit-per-rep`, l = 16384, p4, 5 reps, rep 1 dumped (ligero-statement v5,
`blake3-keyed/row/v2`, manifest `set` block). Each bench-result/v1 refs run_files = its proof tree (producer-side
rust_batch.json / rust_digest.json from the pod's ligero-verify c3469eb9 built from 75cbbac1, never a verification label).

| line | bench-result | proofs (run-files/v1) | VUs | sub-batches | pinned system | pod Rust |
|---|---|---|---|---|---|---|
| bf16-hopper+blake3 (frozen size) | art:6d067ed3262769ebc848fcfed7cade347c11d67c9f69f13f9853fde9e6997b3d | art:0ef949000f0f574323172e21f46ef1b0eaf48db8599aae1e011d179bd44f82ca | 4096 | 25 | 58ef7097… | 25/25 2^-128.05 |
| bf16-hopper+blake3 (sweep plateau) | art:f4dc05013b95756cde9d66977850f992d67946a454473af96710f26d543eaed1 | art:6c8eef6d017f847e5a5b940f0b567800bc557597a2004abdefccf411484af82f | 8192 | 49 | 58ef7097… | 49/49 2^-128.43 |
| fp8-hopper+blake3 (frozen size) | art:4d43ab87e0415c0382d84662160e6f2706345254e0c8a4bcd9e03a07e31995ce | art:d0adcdc6d95f0c28b055fbb4a29daaffe279f5c35b13fe7aa12c7025f0cdd004 | 4096 | 13 | 433bdfc3… | 13/13 2^-128.32 |
| fp8-hopper+blake3 (sweep plateau) | art:4d151f38c9a1314da081e71957178a01b75c7751b3a86330f86fd1ea523427ee | art:0987842f0ba72f1c7eaad26bb2146977d4820f0f99478a63e587b52bff98242c | 16384 | 49 | 433bdfc3… | 49/49 2^-128.43 |

- Instance sets: frozen bench-instances-bf16-hopper/v1 (2a5babca…) / -fp8-hopper/v1 (0ff75002…) at 4096; the 8192 / 16384
  plateaus are prefix-consistent streams (main PR #19). Run record art:72dc311596bfd6e6138604e525db0463d7decb311e4cfd1c98ac7e8ae0bad71d.
- These supersede nothing: my 0844Z H100 results (dc2cae87 / 11a1805e, host committer) stay what they are; these are new results.
