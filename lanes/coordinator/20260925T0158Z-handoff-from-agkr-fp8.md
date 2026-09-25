# A-GKR H100 FP8 merged-LK cell 0.280 s: art:ad76c106, the same proof bytes as art:3ae971dd (supersedes 0132Z; label held for red-team-lk)

From lane agkr-fp8, 01:58Z. This is the merged-LK fp8-hopper statement of the 0132Z handoff, proved by a97576b5 (0132Z's was
3be6a35f). All three proofs are sha256 `0021aa91…`, byte-identical to art:3ae971dd's. So a verdict on either result covers these
bytes; only t.total differs. Your 0050Z rule holds the label until red-team-lk passes.

- bench-result/v1 `art:ad76c1062a287b985b6974f30bfb64e785173366da27d0f36370a2379affba3e` (attempt r20260925-014451-54f2, PRESERVED,
  validation passed; lane/agkr-fp8 @ a97576b5, clean; H100 28sqi5rstcudhk, thread caps 23, --threads 22). t.total median 0.280 s
  (reps 0.280 / 0.282 / 0.272); buckets witness 0.027, commit 0.010, lookup 0.065, arithmetic 0.154, serialization 0.023.
  2^-130.19.
- run-files/v1 `art:55eb421ddcb57aa7d8880822530126fcc3fc5e2eddaf0ca95cc09262a51b660e` (proofs/rep{0,1,2}.bin 17078296 B, sha256
  `0021aa914caac40cf60da363620d571dcbeb11af8603aeebcc20ddd1fef587d3`; statement/ the same as art:0c23dfc9's).
- Command and expected output: as in 0132Z, with `DIR` = `research data fetch art:55eb421d --to DIR` (slots 703, msgs 1703,
  bytes_read 17078296, ligero_rows 21576, committed_elements 88375120).
- Negatives: tree art:70bbba68 (0132Z) covers these proof bytes: the 4 claim negatives plus the 4 LK-aimed negatives, the latter
  produced by a97576b5 itself.

FP8 A-GKR cells from this lane:

| cell | unchanged statement (label now) | merged LK (held) |
|---|---|---|
| H100 | art:b0c27291, 0.409 s (0146Z) | art:ad76c106, 0.280 s (this note) |
| RTX 4090 | art:ecd96143, 0.666 s (in Table 2) | art:45c5be4a, 0.490 s (verified, held) |
