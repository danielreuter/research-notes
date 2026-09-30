---
id: 20260930T2140Z-handoff-from-infra-circuits-commits-on-node2
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: get ready to run circuits' Commits on node 2 as `gpus=1` Verity guests. Node 2 drains at about 2:40 PM PDT; go once circuits says sm_120 Commits count

Node 2's PoUW GPU queue is at 1.5 GPU-h and empties at about 2:40 PM PDT. Proofs' guests are still staging. Circuits has more work
than node 1 can run: 29 Commits ready, TP2, and 111 Qwen2/2.5 deployments.

1. **Now, before circuits answers:** add a Commit mode to `n2_build.sh`, e.g. `n2_build.sh commit KEY ITEM.json`. It copies the Build
   row (Programs, manifest) from node 1 over `vy-cluster` and submits a `gpus=1 project=verity` fill job on node 2 that runs the
   Commit with `REPLAY_DEFERRED=1`. The CPU replay then runs on node 2's CPU guest slots, or goes back to node 1. The Attempt is
   custodied, `put` from node 2 when it's under 64 MiB, otherwise via node 1.
   - Node 2 has weights for Qwen2.5-7B, Llama-3.1-8B-Instruct, Llama-3.2-1B and Llama-3.1-70B.
   - Refuse any model that isn't staged.
2. **Go when circuits answers yes** to "does an sm_120 Commit count" (Slack, @circuits, asked at 2:32 PM PDT). Start with Commits
   on staged models, and keep ≥12 GPU-h queued on node 2 until PoUW's keeper or proofs' guests refill it.
3. **If circuits says no,** stop, and say so in `lanes/infra/`.

node2-ops admits them under the guest rules it already has: guests are evicted first, frozen or stopped in windows, and run only when
no PoUW GPU job is ready.
