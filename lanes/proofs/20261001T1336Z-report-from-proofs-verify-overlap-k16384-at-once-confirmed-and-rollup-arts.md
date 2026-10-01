---
id: 20261001T1336Z-report-from-proofs-verify-overlap-k16384-at-once-confirmed-and-rollup-arts
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d), re your 6:31 AM PDT yes to both; follows note:proofs/20261001T1325Z-report-from-proofs-verify-overlap-preflight-at-once-and-hill-session-howto
---

# K=16384's preflight cases run at once under the corrected bound (138.7 s), and the K=2048 roll-up cites its arts

to: proofs (bc-8416bc72). I opened no PR.

## The K=16384 confirmation: yes, within free memory, and 10.8 s under bf16-hill's 149.5 s

- **Run:** `r20261001-133255-08ec`, on tree `65c230902` (`POINTS=0`, 128 GiB, one GPU, 6:32–6:36 AM PDT, rc 0). Its check
  record is `art:08af98458bc74e2ff001e265f7e235033d2192823cb621dbc05b7bc3487c9a7a`.
  - No staging job was needed: the stage cache keys on the Python packages, and `65c230902` changes only
    `74-gemm-hill.sh`. The record shows `stage_cached`.
  - In flight with it: one flock-fp GPU job, so Proofs had 2 of its 4.
- **The guard:** 3 × 20480 MiB is 61440 MiB, within the 97250 MiB free, so all three cases ran at once with no fallback.
  Together they peaked at 50456 MiB; the pod's host memory peaked at 53.0 GB, with no OOM kill.
- **The check took 138.7 s,** against:
  - 149.5 s for bf16-hill's unguarded at-once run (`r20261001-090316-6c85`);
  - 251.1 s one at a time (`r20261001-131526-f969`).

  Running at once saves 112 s (45%) against running in order.

| case | wall s | exit | device peak MiB |
|---|---|---|---|
| `gpu_paths_agree` | 58.2 | 0 | 17828 |
| `gpu_proofs_match_cpu` | 56.6 | 0 | 16444 |
| `verify_ahead_matches_serial` | 57.2 | 0 | 16444 |

Every case passed, with proofs and transcripts equal. The statement digest (`5021e06a…`) and the proof bytes (740162 per
rep) are unchanged. The largest case peak is 13% under its 20480 MiB bound.

## The shared K=2048 roll-up now cites my session's arts

- **What changed:** I ran `gemm_hill.py rollup --attempt r20261001-092917-8b05 --run-dir ...` on
  `/workspace/usage/hillclimb/bf16-GemmCoordinate_v2-K2048.json` at 6:31 AM PDT. It printed "29 points (0 added, 10 now
  citing their arts)".
- **The diff after,** checked row by row as JSON:
  - my 10 rows gained `arts` and nothing else;
  - the other 19 rows are identical;
  - at the top level only `updated_utc` changed.
- **The copy from before:** `/tmp/pvo-rollup-backup/bf16-GemmCoordinate_v2-K2048.before-arts-20261001T1331Z.json` on node 1
  (sha256 `b1c85ac9e9eac650…`). Since node 1's `/tmp` isn't durable, it is also preserved as
  `art:241ed5f79dbde3c05cca7a92343addff45c09b929c2d9e5a5079d8a175061791`. My lane directory on node 1 belongs to the pods'
  user, so the copy couldn't go there.
