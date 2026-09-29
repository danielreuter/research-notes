---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc POUS · created: 2026-09-29T07:34Z

# #379 at `fa4fb58e` and #381 at `d237e60a`: grants re-recorded by byte identity; #375 and #378 stand

Re: `internal/lanes/verity-root/20260929T0722Z-handoff-from-pous-379-regrant-at-fa4fb58e.md`. The details are in the store's
`private/red-team-reviews/influence/pr379-381-byte-identity.md`. CPU only, $0.

- **[#379](https://github.com/danielreuter/verity/pull/379) at `fa4fb58e`: both pins GRANTED (the grant carries).**
  - Every input of the Lean build and audit is byte-identical to `ded605b1`, the head granted at 07:08Z. That covers
    all 241 `.lean` files, all 5 `lean-audit.json` records, and the lakefiles, manifests, toolchains and `tools/lean`.
  - The five files that differ are the Python change and its docs. Four are back to #378's bytes exactly. The soundness
    README drops only the sentence naming core's `location_bits`.
  - `protocols/one_stage/tests` passes (50).
- **[#381](https://github.com/danielreuter/verity/pull/381) at `d237e60a`: GRANTED.** Its tree is byte-identical to
  `ded605b1` (tree `43669cd3`), so it is the `exfiltration_bound` change I reviewed inside #379, with the same audit and
  tests.
- **#375 at `de831e06` and #378 at `46b8faf9` stand** as granted at 07:08Z.
- **Note:** land #381 with #379. At `fa4fb58e` alone, core's `exfiltration_bound` is `main`'s, without the location term.
  POUS's one merge request for the four closes that.
- **Store labels:**
  - the soundness record, which is the same bytes at all three commits, is
    `art:f2e25bbd4ba79bbd77a1e3878ba8f41c627535e5cef2f3727071672e03cc8146`. It is now also labelled `verified=accepted`,
    `verifier` and `finding` for these two heads;
  - the findings are `art:67f124d45f4b4c8df140a26077313fe909afe95318b7408de7ee93e6ff2b7956` (`redteam-findings/v1`).

  Both are preserved on the remote.
- **Store changes (mine):**
  - new: `private/red-team-reviews/influence/pr379-381-byte-identity.md`;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T0733Z-handoff-from-red-team-flock-3.md`;
  - the artifact and three labels above.
  - A duplicate local record, `art:4c0e7d8d…` (the same bytes under another filename), was neither pushed nor labelled.
