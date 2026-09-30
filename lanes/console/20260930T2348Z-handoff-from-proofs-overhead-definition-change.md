---
id: 20260930T2348Z-handoff-from-proofs-overhead-definition-change
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Hillclimb plots: overhead now includes the verifier interaction (Daniel, 4:47 PM PDT)

An update to `note:20260930T2259Z-handoff-from-proofs-hillclimb-plots-spec`: **overhead** = peak ÷ (2·K·VUs ÷ t_session).
t_session is the wall time of the whole interactive proof job (prover, live-coin round trips with the verifier, verdicts),
steady state, per VU. Throughput is VUs ÷ t_session. Points gain an optional `t_prove_only_s_per_vu` (prover buckets only);
show it in the tooltip. Nothing else in the record changes.
