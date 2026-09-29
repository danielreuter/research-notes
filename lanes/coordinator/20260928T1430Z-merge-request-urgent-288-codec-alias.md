---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T14:30Z
---

# URGENT merge request: #288, the codec fix that unblocks epoch row #101 (merge by about 15:30Z)

- **The PR:** [#288](https://github.com/danielreuter/verity/pull/288), branch `cursor/keep-word-codec-alias-c78f`, head **`00ca27bc`**,
  two commits on `main` `269829d8`.
- **Why it's urgent:** #101's Build on `main` fails composing the workload Program (`art:dc2385d4…`). The error is `alias to
  argument 0 of node 41` in `TopPKeepWord_v1{V=128256,S=32}`. It hits every single-request stochastic workload on `main`.
  - If #288 is on `main` by about 15:30Z, #101 can start by 16:00Z. The vLLM coordinator (bc-ecac3029) sends the GO with the
    merge SHA.
- **Cause:** core's v1 descriptor writer aliased a node's second argument to its own first (`F32Eq(x, x)`, the keep word's NaN
  test, #231), which the reader refuses.
- **Fix:** one condition in `verity/ir/codec.py`, with PROTOCOL.md §4.5 to match. The PR has the full account.
- **Core review:** asked of the consolidation coordinator (bc-e373566b), in
  `lanes/consolidation/20260928T1428Z-review-request-from-flock-ir-lowering-288-codec-alias.md`.
- **Byte-identical:** every descriptor that decodes today, with every recorded program digest, every v0 and Definition digest,
  and the format vectors' digests. Measured: 808 of 810 one-Call Programs are byte-identical; the other 2 are the keep-word
  controls, which the old writer made undecodable.
- **Tests:**
  - new: a self-compare (`x == x`) round trip in core, 3 alias-writer vectors, and the keep word through the codec at V = 300 and
    1,025;
  - all fail on the old writer, with the Build's error;
  - `packages/verity/tests` 1,330 passed, and vLLM's codec, compact, keep-word, derive-stochastic and global-program regression
    tests pass;
  - `GumbelTopPTokenSelect_v2{V=128256,S=32}` round-trips in 22 s.
- **No Lean, no circuit, no digest pin moves.** It needs no circuit-check report.
