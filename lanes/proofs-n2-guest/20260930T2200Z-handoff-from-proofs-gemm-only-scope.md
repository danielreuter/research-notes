---
id: 20260930T2200Z-handoff-from-proofs-gemm-only-scope
campaign: verity
lane: proofs-n2-guest
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Scope, 3:00 PM PDT: GEMM coordinates only, which on node 2 means #1936 (K=8192), 3 chunks; the non-GEMM rows stay held

At 2:58 PM PDT infra held 12 of your `pn2g-*` jobs in `/workspace/pouw/fill/held-proofs-pn2g/`. Nothing was deleted.
- **Approved:** "next coordinates" meant **GEMM coordinates** (`GemmCoordinate_v2`). On node 2 that's only **#1936,
  K=8192**, a new K class: its stage job plus **3 chunks** after its gate. node2-ops is restoring `pn2g-1936-stage.sh`.
- **Held, pending the research owner's yes:** the non-GEMM rows: #2 SiluMul; #21, #6 and #20 RMSNorm; #3 and #4 RoPE; #12,
  #15, #1546, #9 and #5 AttentionHead. Don't requeue them or restore anything from `held-proofs-pn2g/` yourself. I'll tell
  you if the owner says yes.
- Keep your refill loop stopped (a STOP file is set) except for #1936. Never more than 3 chunks of #1936.
- K=8192 may not fit the current circuit: M0 notes that K=8192 needs a circuit change. If #1936's stage or gate fails for
  that reason, stop, report it, and queue nothing else.
