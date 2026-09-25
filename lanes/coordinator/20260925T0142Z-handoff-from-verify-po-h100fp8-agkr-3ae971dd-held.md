---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T01:42Z
---

# verified, label HELD: H100 FP8 A-GKR art:3ae971dd (merged LK; verdict art:e96f50ac registered, no label)

agkr-fp8's 01:32Z cell (3be6a35f, 0.328 s) uses the same merged-LK rewrite as the 4090 cell art:45c5be4a, here at model
`hopper_e4m3_wgmma_k32`. Under your 0050Z rule I registered PASS verdict art:e96f50ac and wrote **no label**. The H100 FP8
A-GKR cell in Table 2 stays art:2e7baba7 (0.688 s). When you send "release", I will label from this verdict
(`29-verdict-3ae971dd.sh HOLD=0 VID=art:e96f50ac`) and create no new verdict.
- main's `verity-gkr-verify` (a48eac01; the verifier is unchanged at 3be6a35f) on my pod accepts 3/3 (proof sha256
  0021aa91), taking 1.06-1.17 s each. The counts match the handoff: 703 slots, 1703 msgs, 17078296 bytes. The statement
  is byte-identical to 3be6a35f's export run on my pod, and public.bin has 0 mismatches against main's frozen fp8-hopper set.
- Rewrite: the same export with `--no-merge` reproduces the unmerged statement I verified for art:2e7baba7, byte for byte.
  `23-lk-merge-check.py` (main's parser) finds the dump to be exactly its tag-merge. It checks 139/139 queries, the
  bijective tag map over the 10 tables (R6 in place of ada's R5), and LK equal to the tagged union as a multiset (261968
  rows), with the first column unique and below P. This is a structural check only; I told red-team-lk.
- Negatives, all rejected: mutate 356/356; my public word +1 at VU 17; the producer's r6_key, shift_out, t_op_out and
  tnorm_out ("LogUp LK level 0: final check") and exp_plus, sign_flip, word_minus and word_plus (art:70bbba68) with my
  binary. Its honest case is accepted.
- Runs: verify r20260925-013458-825f, verdict r20260925-013819-badc.
- Three labels are now waiting for "release": art:45c5be4a (verdict art:df4d2c3c), art:dfbc86c4 (art:7d3aaf2e) and
  art:3ae971dd (art:e96f50ac).
