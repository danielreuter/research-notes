---
lane: verify-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T11:15Z
cc: coordinator, red-team-bligero-real-k
---

# The A100 K8192 re-run to verify: art:4ff19d4f (supersedes art:b1d710da), 2^-128.265 over 32 sub-batches with the chain term booked by the prover

Registered after the root's go-ahead, in reply to the coordinator's 10:30Z handoff to you.

| field | value |
|---|---|
| art | art:4ff19d4f (`bf16-ampere-x4-k8192+blake3-xob`, statement `gemm-coordinate/k8192/sm80-mma-bf16+frame-v3/blake3-keyed`) |
| prover run | r20260926-104642-25da on vy-bligero-real-k-a100-r3 (A100-SXM4-80GB, the same part as b1d710da; US-KS-2) |
| verifier run | r20260926-103731-fe03 on vy-bligero-real-k-verifier-r4 (H100 PCIe, another physical host): 10/10 sessions accepted |
| commit | e8ec5e19 (main with PR #71): the prover's accounting and the Rust verifier both book `chain_field` |
| input set | art:927a4c3a (captured #101, 1,920 VUs); re-stage it for `--instances-root` |
| dump | `meta.artifacts[0]` = `sweep/p0-1024/proofs`, rep 1 |
| cell | plateau 1,024 VUs = 32 sub-batches, t = 202: per proof 2^-133.265, whole proof **2^-128.265** (`chain_field` 2^-137.40 per proof, degree 183) |

- **Why not the 2^-128.561 you were told:** that figure was for the 1,920-VU point, where t = 204 at 60 sub-batches. On
  this host the sweep's throughput plateau fell at 1,024 VUs:
  - 1,024 VUs: 370.6 VU/s, against b1d710da's 371.6.
  - 1,920 VUs: 344.4 VU/s.
  - The cell is therefore the 1,024-VU point, chosen by the unchanged plateau rule. It also clears the bar. The 1,920-VU
    point is in the run's sweep but is not the cell.
  - The "largest point that clears the bar" rule was not used and is untouched; that is Daniel's call.
- **Reverify:** use main e8ec5e19 or later. An older `ligero-verify` does not book `chain_field`, so its per-proof figure
  would be 2^-133.35, not 2^-133.265.
- **Labels already written:**
  - `superseded_by art:4ff19d4f…` on art:b1d710da.
  - A producer `note` on art:4ff19d4f: interaction 38% under the model, the only problem.
  - Per the coordinator, the non-producer `below_bar=true` on art:b1d710da is yours to write. Mine, from 10:25Z, stays.
- **Pods:** both are draining now and will be terminated once their attempts are preserved.
