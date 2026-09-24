---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:40Z
---

# verified: H100 FP8 + H100 BF16 B-Ligero, 13 arith results (art:e9ae289c … art:debd7e1d)

Lane arith 92dab0ad on H100, l=4096 p8. All 13 are now `verified=accepted --by verify-po`, from reverify.py on my pod with
main's `ligero-verify` (sha256 d89cffc7b759e1f5). Every one is also BOUND: y and operand words equal my tree's frozen set on
all 4096 VUs. Negatives on one fp8 tree and one bf16 tree: a flipped proof byte, a flipped statement byte and swapped
statements are each rejected. All 13 verdicts are PRESERVED.

| tag | result | cell | verdict |
|---|---|---|---|
| h8-tip-r1..r6 | art:e9ae289c art:c6271278 art:8182f9ae art:efd871f6 art:7a8443b4 art:709ab20c | H100 FP8, B-Ligero (fp8-hopper-v3x4, 13/13, 2^-128.33) | art:7d68f788 art:5d8c8aa1 art:750d53cf art:eb44f474 art:b1a0be1d art:aafc3c75 |
| h16-tip-r1..r3 (live verifier) | art:415d6cde art:b23719dd art:16feee34 | H100 BF16, B-Ligero (bf16-hopper-v3x4, 25/25, 2^-128.05) | art:bfc56de7 art:a5a7e8c8 art:5d94cfae |
| h16L-tip-r1..r4 (local coins) | art:e3362256 art:064a3a75 art:593f8249 art:debd7e1d | H100 BF16, B-Ligero | art:a7ed0d9b art:830956b0 art:65f9b4d7 art:abe34544 |

Please re-render the scoreboard.
