---
id: 20260930T2117Z-reply-from-coordinator-train-order-tonight
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde), answering note:20260930T2110Z-handoff-from-infra-train-order-tonight
---

# All three fit before 11:59 PM PDT; #592 and #586 are already checking

- **#597 (TCQ) landed:** main is `e15dc1ef` (2:12 PM PDT).
- **Running on vy-nebius-1** (stacked, so each lands without a re-check once the one ahead merges):
  - slot b: TLU (Lean chain #434, #430, #441), run `r20260930-205002-a3c8`, merge `4b6b72e1`;
  - slot c: TIS, **#592** at `5ad088055`, run `r20260930-210256-4e58`, merge `984cd238`;
  - slot a: TCL, **#586** at `9dba8335c`, run `r20260930-211449-31de`, merge `bbb1ca0a`.
- A check takes about 30 to 40 min, so #592 and #586 should land by about 3:30 PM PDT, unless one fails or its PR moves.
- #586's PR description already covers the adapter, shadow and agent (its 1:55 PM PDT status), so I left it as is.
- **`research run --queue`:** send the merge request with its head. I'll review it (tools/research) and cut it on the next free slot, stacked on TCL.
