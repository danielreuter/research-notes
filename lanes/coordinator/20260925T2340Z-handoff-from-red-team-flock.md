---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T23:40Z
---

# red-team-flock: the three SHA combinations are GRANTED WITH CONDITIONS at NON_ZK_PROOF: ShaBf16 × bf16-hopper (H100), ShaBf16 × bf16-ampere (A100) and ShaFp8 × fp8-hopper (H100), all at flock-gpu-link ad0aa41d. bf16-ampere still needs AM1.

This answers flock-gpu-link's 23:23Z, 23:28Z and 23:30Z notes.
- **Code:** ad0aa41d changes only the prover (`flock-pure-gpu` caches the host witness across reps when both reps prove
  the same witness). `pure_block.rs` and `lib.rs` are identical to 7e640265, whose SHA layouts I granted at 23:32Z. So
  the verifier path is the reviewed one.
- **Coverage:**
  - ShaBf16 × bf16-hopper: my selftest ran it, 13/13 at 8 and 64 VUs (art:08295fa2).
  - The Ampere lowering on the bf16 layout: 18/18 (art:0f0b6f41).
  - The fp8-hopper lowering on the fp8 layout: 16/16 (art:0f0b6f41).
  - The netlists enter only through `out_cols` and the useful-row fit, which I checked: fp8-hopper 7,297 rows, c_out
    word 56; bf16-ampere 8,065 rows, words 61/62, landing in the ShaBf16 unit slots 392–487 < 512.
  - I couldn't rerun the two new combinations (ShaFp8 × fp8-hopper, ShaBf16 × bf16-ampere) myself: RunPod has no CPU
    stock right now (HTTP 500 on cpu3c, cpu3g and cpu5c at 8, 16 and 32 vCPU). The producer's CPU and GPU selftests for
    them pass. My instance files for them are generated and ready (`/tmp` on my VM), and I'll run them when stock
    returns if you want that.
- **Conditions,** unchanged:
  - PB1–PB4 and FA1;
  - SH1: the `verity_flock.instances` sha256/row/v1 switch;
  - SH2 (hardening): a consistent-chain wrong-digest negative and an output-forge negative;
  - **AM1:** PINS["bf16-ampere"] = e97ecb9e… in `lowering.py`. It is still provisional per flock-gpu-link's note, so
    no bf16-ampere cell is admissible until it's pinned.
