---
id: proofs/20261005T0633Z-finding-rec-reprice
campaign: flock
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: bc-2a00fbff-762d-5c36-a641-1bbff50ddb4d (rec-reprice, for the proofs coordinator bc-8416bc72)
---

# Recursive witness ZK at m = 35: what the outer proof costs against today's `--zk` (K = 4096)

Branch `cursor/rec-reprice-95d4` (origin/main 43bef6294 + `cursor/rec-v0-95d4` cbad2989e). Work in progress; every number
below is marked measured or estimated as it lands.

## Baseline (given, from the dense rollup art:c343ae88d618f9b5ffc8699951fb2a7bf0e36f151a450a671305c88c7bee1996)

| K | mode | run | units | prove | session | verify | bytes/rep |
|---|---|---|---:|---:|---:|---:|---:|
| 4096 | `--zk` | r20261002-062836-96bb | 2,048 | 1.063 s | 3.05 s | 5.72 s | 1,179,202 |
| 4096 | M0 | r20261002-062731-0015 | 2,048 | 0.723 s | 0.876 s | 0.488 s | |
| 14336 | `--zk` | r20261002-122853-c740 | 512 | 1.071 s | 4.85 s | 11.75 s | |
| 14336 | M0 | r20261002-063820-d94b | 512 | 0.740 s | 1.111 s | 1.132 s | |

The baseline prover (cfbad08, branch cursor/vllm-overhead-dense-95d4 at 2b829a1) predates main's circuit format, so this
lane rebuilds main's GPU prover and reruns M0 and `--zk` on the same node for a like-for-like comparison.

## Runs

(recorded as they start)
