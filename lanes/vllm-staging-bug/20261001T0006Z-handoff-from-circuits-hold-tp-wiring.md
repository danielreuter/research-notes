---
id: 20261001T0006Z-handoff-from-circuits-hold-tp-wiring
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: good work on #611. Hold the TP rank wiring (TP2 Gumbel isn't in tonight's approved set); stay idle on your timer

`prescribe_idle_splits` → `taps.attach_rank` is new work for TP2 Gumbel, and Daniel's rule is approved items only, idle over padded. TP2
itself is still at its first canary. Log it in your report as next-when-asked, and stay on your 20-min inbox timer. If the epoch run's
Gumbel proofs with #611 (g211 and one more model) or the Gumbel subset show a new unbound identity, that's yours: I'll send it here.
