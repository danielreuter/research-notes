---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: **GO (#101 fourth try, early start on train V)** · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T17:52Z

# GO: #101 on train V `fe7931d5`

**The GO commit:** `fe7931d5996e66424c531a15e91afce2563a812a`, with tree `d4c65ae7530e14b7b465915be920edfaf15b2db2`.
- This is main `ac412eb8` plus #309, the registry catalogue that fixes #101's third failure. I approved it at 2026-09-28T17:52Z.
- Its gate check `r20260928-173120-9e29` should pass about 18:28Z, and the research coordinator merges it keeping this tree.

**The bundle:** `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/artifacts/epoch-101-train-v-fe7931d5.bundle`.
- sha256 `c6f3184f4f6b19163ba3befeb6e540a09f576c6d67e1e274f37731741f936003`, ref `refs/tmp/trainv`.
- It needs `be354ab0` and `269829d8`. Verify the commit and tree before starting.

**The row:** #101 at 1 pair (its record), cap $5, on 1× L40S, L40 or RTX 6000 Ada (142 SMs) with at least 94 GB. Set these in the row's environment:
- `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=110000000`, which the row's `manifest build` and `program-graph --word` read;
- `--word-max-gates GumbelTopPTokenSelect_v2=110000000` wherever a CLI takes it.

Its latest start is about 21:50Z, and the balance test applies (about $21 of headroom at 17:36Z).

**Record and STOP rules**, the same as for #73's early start:
- Carry the commit `fe7931d5` and the tree `d4c65ae7`, and hold the `expected/` write.
- If V's gate check fails on vLLM or core code, I write STOP; then terminate and discard.
- The record is written only after I confirm that the landed main's tree is `d4c65ae7`, or that the difference provably doesn't touch #101's Build.
