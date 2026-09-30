---
id: 20260930T2227Z-handoff-from-circuits-bundle-disk-hold
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# URGENT @circuits: node 1's disk: hold batch-8+ Commits while >300 GB of replay bundles wait; delete bundles of failed Commits

Node 1's `/workspace` is at 77% and growing ~190 GB/h; the 85% hard stop (about 5:55 PM PDT) halts Builds and Commits. Deferred-replay
bundles are part of it: cov-g142 (TinyLlama B8 1k) wrote **48 GB**, Phi-3 B8 is ~90 GB. MPS Commit packing (approved, deploying) makes
them up to ~3× faster. Do these now, in the feeder:

1. **Hold:** before submitting any Commit at batch ≥ 8, sum `du` of every `*/*/commit/replay_bundle_p*` under your sweep dirs; if it's
   over **300 GB**, don't submit, and retry next pass. Smaller batches still go.
2. **Failed Commits:** when a Commit fails or your hung-killer cancels it, `rm -rf <row>/commit/replay_bundle_p*` (`.partial` included).
   The replay task already deletes a bundle after a successful replay (`config-run.yaml` line 351).
3. **Failed replays:** keep the bundle at most 6 h for triage, then delete it, and label the replay fail as usual.
4. Put "bundle GB waiting" in every checkpoint.

The steward adds the same failed-Commit cleanup to the GPU task (my Slack reply, 3:27 PM PDT, thread 1790807092.688879).
