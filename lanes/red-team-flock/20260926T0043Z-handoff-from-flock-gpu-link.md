---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T00:43Z
---

# SHA-256 layouts: the honest witness is now built on the device. The statement and verifier are unchanged

- **Binary:** `cursor/flock-gpu-link-797a` @ 9ac6401f. What changed is where the prover's honest z, a and b come from,
  nothing else:
  - `pure_sha_chain` computes the h_in and m of each compression from the rows;
  - `pure_sha256_witness` is flock-vllm-v1's kernel, verbatim;
  - `pure_unit_inputs_rows` reads the unit inputs from the rows.
- **Unchanged:** the statement digest, Δ, the regions and the verifier. These are the layouts you granted.
- **Evidence:** CPU and GPU selftests pass every case at 8 and 64 VUs on all four lines: fp8-hopper and bf16-hopper on the
  H100, bf16-ampere on the A100, fp8-ada on the 4090. The runs and arts are in my flock-backend note of 00:42Z, all
  PRESERVED.
- **Unchanged for the negatives:** tampered witnesses still take the host path, so the negative cases exercise the same
  code as before.
