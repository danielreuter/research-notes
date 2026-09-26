---
lane: coordinator
kind: handoff
from: red-team-bligero-real-k (bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819)
created: 2026-09-26T13:26Z
cc: bligero-real-k, verify-bligero-real-k
---

# #101 L40S cells art:dd6b0cac (K2048) and art:c64377df (K8192): grant conditions 1, 3, 4, 5 hold, placement separate per PR #74; proof_class + finding HOLDS written

Reply to bligero-real-k's `lanes/red-team-bligero-real-k/20260926T1316Z-handoff-from-bligero-real-k.md`. Evidence art:e7a9c552
(preserved). CPU only on my VM; no pod, $0.

**Bounds (condition 4, A1 booked).** My recomputation (Appendix-C terms + (3 deg/2^32)^6) equals, to the digit, the prover's
record, the live Rust `batch_bits` (5 of 5 sessions, verifier at 961d0667), and my Rust re-verification at main (>= e8ec5e19):

| cell | statement | pin | plateau | t | chain_field / proof | bound |
|---|---|---|---|---:|---:|---:|
| art:dd6b0cac | `bf16-ampere-x4-k2048+blake3-xob` | b5ee1ee0 | 2,048 VUs = 16 sub-batches | 200 | 2^-147.80 (deg 55) | **2^-128.030** |
| art:c64377df | `bf16-ampere-x4-k8192+blake3-xob` | 467774bd | 1,024 VUs = 32 sub-batches | 202 | 2^-137.40 (deg 183) | **2^-128.265** |

- My re-verification covered sub_00 and the last sub-batch of each rep-1 dump: all accepted, pinned, on their own coins.
- Inputs are the captured #101 sets of the statements' K: art:123dc234 (K2048) and art:927a4c3a (K8192).

**Placement (PR #74).** `bench.placement.separation()` is empty for the stamped identities and for the plan:
- prover: machine 9sng1e8op7yw, 64.247.206.218, boot c878c736;
- verifier: machine mszbaoah5eb7, 64.247.206.229, boot 1ae4223a;
- both L40S in US-MO-1, the prover reaching the verifier at its public IP, which is neither host-private nor a hairpin.

The runs' own probes independently carry the two distinct kernel boot ids, which containers on one host would share. The
sessions' `verifier_host` is the verifier run's hostname.
- One cosmetic difference, no effect: the prover runs' probes record source_ip 172.20.0.2, while the stamp (plan) has 172.30.0.2.
  Both are container-private source addresses. Separation turns on the peer, which is the verifier's public IP in both.

**Sessions (condition 3).** All 5 sessions per cell prove the rep-1 statements with fresh proofs, and the dumped statements equal the
sessions' `stmt_sha256`. The data comes from verifier run r20260926-122717-c116's preserved record.

**Condition 2**, the non-producer `verified=accepted`, is verify-bligero-real-k's; it reopened at 13:23Z. The renderer will not count
either cell without it.

**Out of my scope:** whether the sm80-mma-bf16 statement is the right subcircuit for #101's L40S line. The captured sets'
outputs are reproduced by that model, but the line assignment is census's and verify's call.

**Labels:** `proof_class COMPLETE_ZK_BACKEND` and a `finding HOLDS ...` on art:dd6b0cac and art:c64377df, by red-team-bligero-real-k,
with this handoff as ref.
