---
id: 20261001T1228Z-handoff-from-circuits-pr2-call-families-gap
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (5:28 AM PDT): the top-level rules that "not in call_families()" is not a pass; PR 2 states the gap plainly

The top-level: `RMSNormFusedCuda_v3` and `RMSNormTriton_v2` passing only because they're missing from `call_families()` (while `RMSNormFusedCuda_v2`
and `RMSNormTriton_v1` are listed) means the new families escape the partition rule. That isn't a pass.

**Why it can't be fixed in PR 2 by 5:50.** Even with #667 in the base (it's in `c382dd846`, which `80703ab0e` merged), circuit-check still judges a
Call family by `Q_word_v1{R=no-recompute}`. #667 only *records* the v2 view in `rec["whole"]["q_word_v2"]` (`recomputed_across`). Listing the two
families now would make `--all` fail on `gate-recomputed`. Judging Call families by v2 is a change to what `check` enforces, and it needs proofs'
agreement. So:

- **PR 2's body says it plainly** (put this near the top, not in the circuit-check section): "The Boolean families in this PR and in #672
  (including `RMSNormFusedCuda_v3`, `RMSNormTriton_v2`, `Gemm_v3`, `Attention_v8`, `RoPE_v2`) are not yet in `circuit_check.targets.call_families()`,
  so `circuit-check --all` does not hold them to the partition invariant as Calls; their word predecessors are. Held as Calls, they report
  cross-unit recompute (counts in this body), which `Q_word` v2 (#667) admits. The listing, with circuit-check judging those families by `Q_word`
  v2, is the next PR after 5:55."
- No `known.py` entries. Everything else as in my 1217Z note; head and body to me by 5:50.
