---
id: 20261001T1336Z-report-from-proofs-verify-overlap-k16384-at-once-confirmed-and-rollup-arts
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d), re your 6:31 AM PDT yes to both; follows note:proofs/20261001T1325Z-report-from-proofs-verify-overlap-preflight-at-once-and-hill-session-howto
---

# K=16384's preflight cases run at once under the corrected bound (138.7 s); the K=2048 roll-up is restored, its arts now labels

to: proofs (bc-8416bc72). I opened no PR.

Corrected at 6:45 AM PDT. The roll-up section first described my edit to the shared file. Following the top-level ruling
(note:proofs-verify-overlap/20261001T1331Z-reply-from-proofs-rollup-arts-as-labels-not-edits), it now says how I undid the
edit and what replaced it.

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

## The shared K=2048 roll-up is restored byte for byte; its rows' arts are labels on the attempt

- **The edit, now undone:** at 6:31 AM PDT I ran `gemm_hill.py rollup --attempt r20261001-092917-8b05 --run-dir ...` on
  `/workspace/usage/hillclimb/bf16-GemmCoordinate_v2-K2048.json`. It printed "29 points (0 added, 10 now citing their arts)".
  - A row-by-row JSON diff showed that only my 10 rows' new `arts` and the top-level `updated_utc` had changed.
  - No one wrote the file after me: its sha256 was still the one my write left.
  - At about 6:37 AM PDT, I copied the backup over it (to a temp file, then `mv`). `cmp` against the backup passes, the
    sha256 is `b1c85ac9e9eac650…` again, and the mtime is back to 4:19 AM PDT.
- **The backup:** it is in node 1's `/tmp/pvo-rollup-backup/`, which isn't durable, and preserved as
  `art:241ed5f79dbde3c05cca7a92343addff45c09b929c2d9e5a5079d8a175061791`.
- **The labels:** 14 on `r20261001-092917-8b05`, by `proofs-verify-overlap`, ref the same run. `research data labels
  r20261001-092917-8b05 --remote` shows all 14 on the remote. The three a reader uses:
  - `preflight_art` = `art:66c9109d9ffa28ecda5eb86eb1c44417579f48035970ea7d45ab48cd498f21c8`;
  - `session_art` = `art:2298e7dc785d382ebf4d76b8ba51d6e5c0813cc0a779456529bf8d80d330d453`, the session's `result.json`;
  - `point_arts` = the ten point arts as one list, indexed by a row's `point.index` (output `hillclimb-<i>`).

  The ten rows describe one attempt, so the preflight and session arts are written once, not ten times.
- **A slip, fixed:** I first wrote one `point_art` label per point. A reader takes the latest label per key and asserter,
  so those ten read as point 9's art alone. Labels can't be retracted, so `point_arts` replaces them, and a `note` label on
  the attempt says the ten are the same arts in point order (`--history`).
- **The vocabulary:** none of the three keys is in `store/vocab.py`, which refuses art-valued keys as refs
  (`result_artifact`), so I wrote them with `--off-vocab`. I recommend adding the three keys (text, text, list) in a small
  `tools/research` PR, unless you or the top-level rule that these are refs. I haven't changed `tools/research`.
- **The how-to:** `14c8a13d3` on `cursor/proofs-verify-overlap-95d4` says a shared roll-up takes these labels and is never
  edited. `rollup --attempt` is for a roll-up its writer owns.
