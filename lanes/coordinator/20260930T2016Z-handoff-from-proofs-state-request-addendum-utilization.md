---
id: 20260930T2016Z-handoff-from-proofs-state-request-addendum-utilization
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Addendum to `note:20260930T2002Z-handoff-from-proofs-state-request`: utilization failures and the proof remit's workloads

Daniel's priority 1 (20:13Z): shared infra, fast, one pool and one queue on the two servers. Please add two sections to your
handoff to `lanes/proofs/`:

7. **Utilization failures, last 48 h:** each time a node, pod or slot sat idle while work waited, a job died or restarted
   (cache races, full disks, guards killing pods, missing `send`), or a train stalled; with the cause, how long, and the fix
   if any (commit, note or run id).
8. **Workloads the proof remit runs:** for each kind (merge-train `check` runs, Lean builds and audits, lean-agreement,
   M0/M1 prover benchmarks, backend sweeps, red-team runs, anything else): where it runs (node 1 slots a/b/c, node 2, RunPod,
   the control pod), CPU or GPU and how many, how long one takes, how often, and how it's launched today (`research run`,
   launch scripts such as `launchv.sh`, Kueue, ad hoc pods).

I'll turn item 8 into the inventory for @infra's central queue. Items 7 and 8 matter more than the rest of the handoff's
tail, so send them with items 1–3 if you can.
