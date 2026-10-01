---
id: 20261001T0352Z-handoff-from-circuits-g217-passed-gemma-next
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: g217 passed at 6:06 PM PDT, so drop the hold on n082–n084. The Gemma-2 33 go once the advisor says yes. EOS fix in progress

- **The node-2 gate passed.** cov-g217 on node 2 is `r20261001-005853-d296` (5:58–6:06 PM PDT): its run root equals node 1's. n082, n083 and
  n084 (Qwen2.5-0.5B B1 on node 2, 460/460) count: drop the held wording and put them in your headline counts, still with `ov.node 2`.
  Thanks for the labelling fix.
- **Node 1 is idle** at 8:50 PM PDT: all 8 GPUs at 0 MiB, and nothing waiting in the pacer (cap now 1 TB, disk 29%). TP2's 13 are paced 2 at a
  time, and two Builds are running.
- **Gemma-2:** your six-row subset passes, and its fixes are on main (TGO). I've asked @old-circuits-and-proofs for the overnight yes on the
  other 33 `grid_deferred_gemma2` deployments. As soon as that yes is on Slack (thread 1790826524.716879 or a reply to me), release them,
  below B8 first. Use the research question "Do Gemma-2-2B's softcap, normalizer and tied-embedding Programs hold across the grid's batch
  sizes, sampling modes and lengths on sm_120?". MPS packing is on tonight for the pack's own B8 list, so eligible Gemma-2 B8 rows may run
  packed, labelled `ov.mps_packed`.
- **Early EOS (your 0145Z finding):** Daniel decided to record the generated tokens beside the Commit, with no `ignore_eos`. The worker
  circuits-commit-tokens is building it on main (`internal/circuits/commit-tokens-record.md`). Keep g160 and n105 labelled fail with their
  cause, and rerun them when the fix lands; I'll tell you.
