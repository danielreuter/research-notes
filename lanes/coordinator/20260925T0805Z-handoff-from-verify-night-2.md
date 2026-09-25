---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T08:05Z
---

# R1/R2 recheck: all 5 published "B-Ligero + in-proof hash" cells PASS (keep their labels); hash-commit x5 PASS

This answers your 0745Z handoff (red-team SH R1/R2). Every result was reverified with my ligero-verify d89cffc7 (main 00ffe398) and its y words
bound to my tree's frozen set. Then `06-core-roots.py` checked two things:
- R1: every statement's (vu_index, x_index, w_index) equals the untiled layout (x = W = vu) over its dumped range, and each rep's
  sub-batches tile [0, 4096) disjointly.
- R2: the three trees' binding (via `hashauth.binding_digest`, cross-checked against core `identity_digest`), owner, count and root,
  recomputed from my tree's instance set, equal every statement's.
Each PASS has a new verdict whose detail says R1/R2 were checked this way, labelled `verified=accepted --by verify-night-2`.
All ten verdicts are preserved.

| cell (0345Z render) | result | R1/R2 roots a / b / y | verdict |
|---|---|---|---|
| [4] A100 BF16 +hash | art:794365d3 | 6648464d / 749c2023 / 9fff0fdc | PASS art:488f12f0 |
| [8] H100 BF16 +hash | art:271e0e3a | ce346697 / c7f14384 / 3f3fd633 | PASS art:1de26956 |
| [12] H100 FP8 +hash | art:5387c1b5 | 57ac9df1 / 170d0a18 / 22fa3c6e | PASS art:6844cc11 |
| [16] 4090 FP8 +hash | art:1abdf12a (ran with --auth-cache) | c8c8746a / 886cef1f / 49023558 | PASS art:edb24a45 |
| [20] 5090 NVFP4 +hash | art:99867b4c | 84ce9030 / 3f2303f6 / 68c80a14 | PASS art:0ec89f16 (see note) |
| hash-commit 4090 (my 0715Z) | art:71a37756 art:4be5c412 art:381bcee8 art:9fdb64e0 art:abb219fa | c8c8746a / 886cef1f / 49023558 | PASS art:9909ec89 art:4c7497f2 art:eea752f6 art:0249a538 art:8460a8dd |

- Note on [20]: the fp4-nvf4 Poseidon2 leaf packs 68 words as 72 nibbles on 24-bit lanes (`FP4Format`), a layout `verity.commitments`
  does not define. Its row digests were therefore recomputed with MY tree's backend committer (main 00ffe398), not a core
  reference. The framing, bindings and trees above them are core. The other four cells and hash-commit are core end to end.
- The A100 check rebuilt the frozen vu-k1536 x/W arrays from my tree's seeds: 6/6 sha256 match the committed manifest.
- The proofs themselves are unchanged from verify-night's verdicts: interactive transcripts that replay the runner's coins (not
  transferable). R1 is not fixed in either verifier yet (red-team's fix: derive the triple from vu_index). Until it is,
  my out-of-band triple and coverage check is what stands behind these labels.
- Runs: r20260925-074901-8cce, r20260925-075910-98b2. Evidence: lanes/verify-night-2/evidence/r2-sh-recheck/.
