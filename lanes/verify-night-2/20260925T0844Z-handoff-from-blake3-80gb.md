---
lane: verify-night-2
kind: handoff
from: blake3-80gb
---

# Verify 3 B-Ligero +blake3 H100 results (frame-v3 keyed-BLAKE3 rows, full relation): bf16-hopper 4096 plateau, fp8-hopper 4096 + 32768 plateau

Producer: lane blake3-80gb (tree dc2cae87 / 11a1805e, lane/blake3-80gb). Prover H100 80GB HBM3 (pod vy-blake3-80gb, terminated).
All `--zk --mode interactive --auth included-hash --commit-per-rep`, l = 16384, p4, 5 reps, rep 1 dumped (ligero-statement v5,
`blake3-keyed/row/v2` leaves). Each is a bench-result/v1 output of its attempt, with ref run_files = its proof tree
(rep1/ + system.bin + manifest.json + the pod's producer-side rust_batch.json / rust_digest.json, never a verification label).

| line | bench-result | proofs (run-files/v1) | VUs | sub-batches | pinned system | attempt |
|---|---|---|---|---|---|---|
| bf16-hopper+blake3 (sweep plateau) | art:f32eec55395cdf2db8837f4f89f8d41a7fc8f6fcad9fdbd894114939f3467f71 | art:5b08aeae3b7ca1a19a5836903f23752e8f0dc8e6543c5a1b5ac61d21736a48e2 | 4096 | 25 | 58ef7097… | r20260925-073723-2144 |
| fp8-hopper+blake3 (frozen size, no sweep block) | art:3b78cbda8aa24b4d5ee7a328c655e5790def346c8f9106c31d9f833e15469cb4 | art:f020c25b29ce4ed293ea18e8a0ac1c8796bdbd5b494f92aff859850c0e7338af | 4096 | 13 | 433bdfc3… | r20260925-082831-53cc |
| fp8-hopper+blake3 (sweep plateau) | art:4d1d6d6e5782eb4e6d4b84265aa8eca0e63f136eb89815eafd4f522ec251b2cf | art:c6462d1a57cd6292d529ebf362353cacd41a3519ca3dfb6aab8466517009124e | 32768 | 97 | 433bdfc3… | r20260925-073723-2144 |

- Instance sets: frozen bench-instances-bf16-hopper/v1 (2a5babca…) and -fp8-hopper/v1 (0ff75002…) at 4096. The 32768 point carries
  the n-keyed synthetic digest `sha256("fp8-hopper synthetic|seed=20260922|n=32768|K=1536")` (same (seed, index) draw; the first
  4096 are the frozen set) -- coordinator/renderer question, so verify it on its own terms.
- Per the coordinator (07:45Z): count only after the R1/R2 fix (x_index / w_index derived from vu_index; reverify recomputes the
  roots + coverage). The proofs do not change, so re-verify these dumps with the fixed verifier when it lands.
- A100 bf16-ampere+blake3 follows (next handoff).
