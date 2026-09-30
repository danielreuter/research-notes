---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-attention · kind: decision · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T03:59Z · re: PR #477

# FA2's partial -inf guard: yes, model it

- **Why:** Daniel's rule is that the IR matches the hardware bit for bit, on every bit pattern. FA2 applies `Check_inf` only in its masking steps, as FA3 did.
- **How:** reuse the FA3 construction, `Attention_v4{…, MASKED_FROM}` (#105), with FA2's masking-step boundary, rather than inventing a new form. It binds `blackwell_consumer`'s FA2, `Attention_v2{DOT=Hopper, INV=Fa2InvSum}` plus the guard placement.
- **Acceptance:**
  - every head bit-exact, including non-finite rows: a constructed all-±inf and NaN score set, as #105 used;
  - no existing record's digest moves (sm_89 FA2 records keep their Definition unless the same guard placement holds there too; if it does, **report it and don't change it**, since that would move records);
  - the circuit-check passes.
- **Where:** fold it into #477 if it's small, else a PR stacked on it. It should land before the sweep night; finite rows are already exact, so it doesn't block the lane's other work.
- **Good result:** `Attention_v2{DOT=Hopper,INV=Fa2InvSum}` exact on every finite head of 122,228, with the MUFU tables and tiles matched. That's the FA2 correspondence milestone.
