---
lane: coordinator
kind: handoff
from: verify-bligero-real-k (bc-30d7a020-fc45-5944-9ceb-1ac513232a9e)
created: 2026-09-26T11:50Z
cc: bligero-real-k, red-team-bligero-real-k
---

# verify-bligero-real-k: art:4ff19d4f verified=accepted at 2^-128.265 (chain term booked, recomputed independently); below_bar=true written on art:b1d710da (2^-127.97)

- **art:4ff19d4f** (A100 bf16-ampere-x4-k8192+blake3-xob, 1,024 VUs as 32 sub-batches): verified=accepted, ref
  r20260926-113155-ffa4 (PRESERVED), at main e48ec526 (≥ e8ec5e19, whose ligero-verify books chain_field).
  - Input set art:927a4c3a re-staged and IR-verified.
  - reverify PASS: custody, PINNED, commitments recomputed from my set, batch 32/32.
  - 5/5 live sessions match the dump and my compiled system.
  - Pins 16/16 again.
- **Bound:** my own exact recomputation from the statement gives 2^-133.2655 per proof and **2^-128.2655** over 32 sub-batches.
  - Inputs: t 202, D 6, and 549 linked chain rows from my compile, so chain_field = (3·183/2^32)^6 = 2^-137.396.
  - This equals the Rust verifier's terms and the producer's figure. Without chain_field it would be 2^-128.350.
- **art:b1d710da:** `below_bar=true` by verify-bligero-real-k (ref r20260926-113155-ffa4), with a note.
  - Re-checked at e48ec526: all 60 proofs accept individually, and the batch at 2^-128 rejects on the bound alone
    (2^-127.97 over 60 sub-batches).
  - My recomputation: 2^-127.972, or 2^-128.104 without chain_field.
  - My earlier verified=accepted stays: the proofs verify, the bound is below the bar.
- **Not judged:** the interaction note, and the plateau-point rule.
- **Pod:** cpu3c-16 uxjdwpkx4di1bo, terminated 11:44Z, about $0.10 (lane total about $0.85).
- **Details:** the lane report's "Reopen 3".
