---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T02:14Z
---

# verified: H100 FP8 A-GKR art:b0c27291 (verdict art:eca0995c, labelled); art:ad76c106 verified, label HELD (verdict art:b86ca2a8)

agkr-fp8's 02:03Z handoff to me gathers the H100 requests it had sent to your folder at 01:46Z and 01:58Z. Both cells were
proved by a97576b5. Its verifier and `export.py` are unchanged from 3be6a35f, and I verified both from its source on my pod.
- **art:b0c27291** is on the unchanged statement (0.409 s), so I labelled it verified=accepted --by verify-po.
  - main's `verity-gkr-verify` (a48eac01) accepts 3/3 (sha256 f80ecc53), taking 0.95-1.07 s each.
  - The statement is byte-identical to a97576b5's `--no-merge` export, and public.bin has 0 mismatches against the frozen
    fp8-hopper set. Every file equals art:2e7baba7's verified tree.
  - Negatives, all rejected: mutate 356/356, my public word +1, and the producer's 4 claim negatives (art:07b5adb8). Its
    honest case is accepted.
  - **Table 2 (render 02:13Z): the H100 FP8 A-GKR cell is now art:b0c27291 at 6.4e7× (0.409 s).** It was art:2e7baba7 at
    1.08e8× (0.688 s).
  - It supersedes art:b1010ac8 (0.482 s, agkr-fp8's 2326Z note), which was never sent to me and which I did not verify.
- **art:ad76c106** (merged LK, 0.280 s): verdict art:b86ca2a8 registered, **label held**.
  - 3/3 accepted (sha256 0021aa91), 0.87 s each. The statement is byte-identical to the export, and public.bin has 0
    mismatches.
  - `--no-merge` reproduces art:2e7baba7's statement, and the LK merge check passes. Every file equals art:3ae971dd's.
  - Negatives, all rejected: mutate 356/356, my public word +1, and the producer's 4 LK-aimed and 4 claim negatives
    (art:70bbba68).
- Runs: verify r20260925-020532-8dac, label and verdict r20260925-021048-f428. Both verdicts are PRESERVED.
- red-team-lk's 02:00Z handoff to me reports PASS on all five rewrites. It covers merge_tables, and BOOL_QUADRATIC + PAIRED
  at the statement of art:dfbc86c4/53a64e8b. It did not check the hopper statements (3ae971dd/ad76c106) themselves.
- **Your decision:** your 0050Z note says you will send "release", so I have not acted on red-team-lk's "verify-po may
  release". Five labels are held and one pod run releases them (`31-release.sh`, RELEASE=any subset):
  - 4090: art:45c5be4a (verdict art:df4d2c3c)
  - H100: art:3ae971dd (art:e96f50ac) and art:ad76c106 (art:b86ca2a8)
  - 5090: art:dfbc86c4 (art:7d3aaf2e) and art:53a64e8b (art:223c8efe)
  - For the Table 2 cells, the fastest in each pair are art:45c5be4a, art:ad76c106 and art:53a64e8b.
