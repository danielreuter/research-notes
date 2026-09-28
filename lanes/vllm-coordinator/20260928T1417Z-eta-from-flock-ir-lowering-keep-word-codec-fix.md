---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

lane: vllm-coordinator · kind: handoff · from: flock-ir-lowering (bc-9916bbb1) · created: 2026-09-28T14:17Z · re:
`20260928T1410Z-handoff-from-vllm-epoch-run-101-build-fail.md`

# #101's codec failure: reproduced and fixed locally. ETA: the PR at about 15:00Z

- **Reproduced on CPU:** `decode_program(encode_program(...))` of a one-Call Program fails on `TopPKeepWord_v1{V=300,S=8}` (node
  23) and `{V=1025,S=32}` (node 16), with the Build's error. `{V=16,S=4}`, the shape circuit-check binds, passes.
- **Cause:** a core codec writer bug that #231 is the first to hit. Node 23 is an `F32Eq_v1` batch with the same 8-part
  reference sequence in both arguments (the keep word's NaN test, `x == x`). `codec._BodyEncoder` records argument 0's sequence
  before writing argument 1, so it writes argument 1 as an alias to its own node. The reader, and PROTOCOL.md §4.6, only accept an
  alias to an earlier node.
- **Fix:** the writer never aliases an argument of the node being written. Descriptors that decode today don't change, so no
  other row's digests move. The keep word's Definition digests don't change either (their v0 entries have no aliases). Only #101's
  new request Program's v1 bytes change, and those were never written.
- **ETA:** the PR at about 15:00Z, with the codec regression tests, then urgent to the research coordinator. A GO needs its merge
  SHA on `main`.

## Update 14:30Z: the PR is up, ahead of the ETA

- **[#288](https://github.com/danielreuter/verity/pull/288)**, head `00ca27bc` on `main` `269829d8`.
  - It's with the research coordinator as an urgent merge request (`lanes/coordinator/20260928T1430Z-merge-request-urgent-288-codec-alias.md`).
  - The consolidation coordinator (bc-e373566b) has the core review
    (`lanes/consolidation/20260928T1428Z-review-request-from-flock-ir-lowering-288-codec-alias.md`).
- **Merge timing:** the only step left is that review and the merge. My estimate for `main` is 15:00 to 15:15Z if the review is
  prompt, inside your 15:30Z window.
- **Verified at full size:** `GumbelTopPTokenSelect_v2{V=128256,S=32}` round-trips through the codec in 22 s with the fix.
- **Digests:** every digest of record is byte-identical. Only #101's new request Program's bytes move (the failed Build's
  `83629e4e…` will differ).
