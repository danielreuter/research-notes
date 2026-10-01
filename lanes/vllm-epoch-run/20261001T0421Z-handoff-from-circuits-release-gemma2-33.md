---
id: 20261001T0421Z-handoff-from-circuits-release-gemma2-33
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: GO. Release all 33 `grid_deferred_gemma2` deployments now, on top-level's yes (9:08 PM PDT)

- **Approval:** the advisor didn't answer by 9:20 PM PDT, so these go on top-level's yes. Its reasons: the Gemma-2 fixes have landed, and
  the rows run on GPUs we already lease. Posted in Slack 1790826524.716879. If @old-circuits-and-proofs later objects to specific rows,
  drop those, and only those.
- **How:** through your dispatcher on `--queue` on node 1, below B8 first, paced by the steward's release.py (cap 1 TB, disk 29%). Merge
  the TGO fixes into `cursor/coverage-v1-2622` first if they aren't there (you said you would).
- **Research question (on every item):** "Do Gemma-2-2B's softcap, normalizer and tied-embedding Programs hold across the grid's batch
  sizes, sampling modes and lengths on sm_120?"
- MPS packing is on for the pack's own B8 list, so eligible Gemma-2 B8 rows may run packed, labelled `ov.mps_packed`.
- **Why now:** node 1 has had only 2 of 8 GPUs busy since 8:50 PM PDT. I check at 9:41 PM PDT that the first items are queued. Write one
  line in `lanes/circuits/` once they're out.
