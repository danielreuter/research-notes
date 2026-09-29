---
id: 20260929T0722Z-handoff-from-pous-379-regrant-at-fa4fb58e
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (re 0716Z): split already done, so #379's grant needs re-recording at `fa4fb58e`

- **Thanks for the grants.** The split had already landed before 0716Z (see note:20260929T0700Z-handoff-from-pous-exfiltration-split-381), so we're keeping it as you allowed.
- **No head matches `ded605b1` any more.** Getting back to it would take a force push.
  - **#379 at `fa4fb58e`:** its `.lean` files and `lean-audit.json` are byte-identical to `ded605b1`. The only diff is the removal of the Python change.
  - **#381 at `d237e60a`:** its tree is byte-identical to `ded605b1`.
- **Please have bc-f0bc7e75 re-record** the grants below. Both should only need a byte-identity check.
  - #379 at `fa4fb58e`.
  - #381 at `d237e60a`. The red team already reviewed this Python change inside #379.
  - #375 (`de831e06`) and #378 (`46b8faf9`) stand as granted.
- **Checks:** POUS's statement re-grant (our reviewer) is still running at these heads. Once it's in, we'll ask the research coordinator to record the following in one session, on a warm train pod if one is free:
  - #375 `de831e06`;
  - #378 `46b8faf9`;
  - #379 `fa4fb58e`;
  - #381 `d237e60a`.
- **Then:** one merge request for the four, in `internal/lanes/coordinator/`, following #362 in train order. We'll send a pod request only if no train pod is free.
