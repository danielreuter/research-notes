---
id: 20261001T0224Z-handoff-from-circuits-621-p10-ratchet
campaign: verity
lane: vllm-coverage-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: URGENT. #621 fails train TGN on the P10 size ratchet. Bring `query_population` back to at most 373 lines, then send the new head to @old-circuits-and-proofs

- **The failure:** TGN (the Gemma-2 six) failed only on P10. #621 grows `verity_vllm/check/replay/coverage.py::query_population` from 373 to 378 lines,
  and recorded sizes can only shrink. The epoch run's 01:28Z report flagged the same thing.
- **The fix, on #621's own branch:** take at least 5 lines out of `query_population`, either by splitting a helper out or by tightening it.
  - Don't raise the recorded size in `p10_size.json`.
  - Keep the behaviour unchanged, and run #621's regression tests and `tests/lint`.
- **Then:** push the branch, and post #621's new head sha in one line to @old-circuits-and-proofs on Slack. The research coordinator runs the trains.
  - Copy @circuits on that post.
  - The other five Gemma-2 PRs are already checking as train TGO, so don't touch them.
- **When:** now. This is the only thing between the Gemma-2 fixes and main.
