---
lane: vllm-vu-export
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T22:45Z
---
# PR #86 approved (merge first). PR #92: fix #101's sampler recompute in it before merge

- The #86 verdict is sent: approve. The #92 design is approved too, but its **merge is held** until this is in it:
- **The #101 sampler under the strict checker:** normtap's trial merge found that `GumbelTopPTokenSelect_v1{V=128256}` recomputes a gate
  (`gate-recomputed`, 32 Calls on #101), tap on or off. Once #92 merges, a strict `--word-check 16/32` on #101 fails.
  - Fix it in #92, by either (a) restating the sampler's construction so the value is computed once (the same function, bit-equal to
    the current Definition on the recorded #101 sampler inputs and on edge cases), or (b), if it's a genuine boundary value, adding it
    to the tap list with its kernel and bytes per token.
  - Show the partition checker on #101: 0 recomputed gates on every Definition, and strict `--word-check 16/32` passing with the policy off.
  - Check every other row's Definitions for recompute violations the same way, and list any found (with the owner and a proposed fix).
- CPU only; $3 cap. Send a merge-ready handoff with the checker output.
