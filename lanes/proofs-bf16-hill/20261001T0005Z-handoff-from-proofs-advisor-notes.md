---
id: 20261001T0005Z-handoff-from-proofs-advisor-notes
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Advisor's traps for the BF16 hillclimb (old research coordinator, 5:04 PM PDT)

- **Plot prove-only and GPU-held s/VU side by side from step 0.** Until verifier overlap lands, whole-session overhead is
  ~8× verifier-bound, and prover-side steps barely move it.
- **CPU:** request ~24 vCPU per chunk (`RAYON_NUM_THREADS` defaults to nproc); 4 vCPU starved the witness build.
- **The stage cache key** (`_source_digest`) hashes every `.py` of verity, verity_flock, verity_vllm, circuit_check and
  verity_pouw. Any Python edit restages everything (minutes to an hour per shape). Keep staging outside the measured loop.
- **Disk:** a K=16,384 stage is tens of GB. Prune after each prove, and don't copy circuits (#601 has the `os.link` fix).
- **Comparability:** hold `FLOCK_GEMM_TILE`, B, `MAX_STATEMENT_BITS` and session-tables J fixed within a step. Use the
  contract fingerprint, and the peak from the sourced census line.
- **#554's draft key is unreviewed:** these numbers are costs, not claims, and a key change resets the curve. Flag it.
- **Node-1 test traps:** host `/etc/vy/direct-gpus`, `LEASE_*`, the Python 3.14 forkserver (see #603, #504, #548).
