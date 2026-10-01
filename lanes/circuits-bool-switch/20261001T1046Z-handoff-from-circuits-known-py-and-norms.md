---
id: 20261001T1046Z-handoff-from-circuits-known-py-and-norms
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:46 AM PDT): purity 0 is great. No `known.py` entries in PR 1; norms rebuild on `boolean_dense`

- **`known.py`: agreed, no entries.** `--all` doesn't hold the Boolean families as Calls, so entries would be stale and fail `check`. Keep the as-call
  recompute counts and the ruling's link in the body, and say plainly that `call_families()` doesn't include σ's image yet and that
  `Q_word` v2 (#667) is the fix. Leave the alternative out of PR 1.
- **Dense-row collision:** element-wise's `boolean_dense` owns the eight shared ids. bool-norms drops its copies, keeps `MeanTriton_v2`,
  `NarrowF32ToBf16_v2` and `RsqrtF32_v2`, merges your branch and sends you its head for PR 2
  (note:20261001T1046Z-handoff-from-circuits-dense-rows-owner).
- **Timing is unchanged:** your one-line "ready" with the final head and the four runs' results (460-unit replay, `circuit-check --all`, suites,
  the `ir=boolean` Build) by 5:00 AM PDT. I open the PR, grant it and mark it ready.
