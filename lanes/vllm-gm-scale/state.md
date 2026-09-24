---
id: vllm-gm-scale/state
lane: vllm-gm-scale
kind: state
status: in-progress
repo: verity
origin: lane/vllm-gm-scale
---
# vllm-gm-scale state

Worktree `~/projects/verity-wt/gm-scale`, branch `lane/vllm-gm-scale` from `origin/lane/vllm-cleanup-2` @ `38122d1f`.
Task: close the fresh B64 GM-01 cell for row #23 (llama32-1b bf16 L40S tp1 b64); make GM-01 scale if needed.

## Log
- 07:46Z start. Worktree created. R2 credential minted `--via local --ttl 7h` into `~/.research/scratch/gm-scale/cred.env` (0600, not printed).
- CHECKPOINT gm-answer MET (08:26Z). YES: sweep Match `r20260923-233020-dc38` (source 014563ac, ACQUIRE_ENGINE=v2, vyv-sw-67) ran GM-01
  in full, fresh, in-row: impl fast, 8 workers, process wall 317 s (timeline span match.global_match 00:02:24-00:07:41Z; phases 282.7 s),
  verdict PASS (G1..G8 PASS, X-09 PASS xreq_total 0, alternate `sequence` PASS). Commit `ca81` PASS consumed that Match.
  Harness lift vs frozen #23: all verdict fields equal; only fold_record_pins differ (new fold record). decomp_hashes: all 64 per-request
  hashes equal; oracle.digest differs (R19 Build epoch, per the earlier lane). The merge note's open item ("fresh B64 global-match on the
  new acquisition path not completed") was the 8.3 h record-checker run; fixed by 6bf4a00b (merged to staging 68112222) and closed in
  substance by dc38. Missing vs merge note: nothing on the verdict; the harness candidate-mode run for #23 was never stored (f455's table
  lost), and no repo record names the fresh v2 GM-01 evidence for #23 -> I add a fixtures.toml note + a preserved fresh-rerun Attempt.
  Profile (vyv-gm, 32 vCPU EPYC 7713P, my base 38122d1f, same GM code as 014563ac): see "Profile" below.

## Profile (vyv-gm)
- base_w8 (exact recorded command line, default 8 workers): rc 0, process wall 435 s, phases 393 s: load_fold 106 (serial),
  x09 135 (parent CPU 31), g3_g4_g5_per_request 71 (parent 14), alternate_criterion 73 (parent 20), rest <5. 355% CPU avg;
  max single-process RSS 14.0 GB; cgroup anon peak ~29 GiB (sampled from 08:10Z). Output vs dc38: global_match.json 37 diffs, all timing;
  match_decomp.json 2 diffs, timing; global_match_global_program.json byte-equal.
- spy_w8 (py-spy --subprocesses 20 Hz, sep output): 1608 CPU-s sampled. 84% of CPU in forked per-request legs. _canonical_hash 31.5%
  incl. (json.dumps 27.7% -- the canonical serialization before sha256; changing it would change hashes of record), compare_steps 42%,
  X-09 decompose 21%, component build on workers 16.8% (built once, held by parent, shared CoW -- no reloads), fold load json decode 8.6%.
  py-spy exited 1 (9 sampling errors); GM-01 inside it PASS, diff = timing + the sep-mode decomp_out path only.
- Worker scaling (same pod, same record; all PASS, all outputs equal to dc38 except timing / worker config / sep-mode output path):
  | MATCH_WORKERS | wall s | load_fold | x09 | per-req + alternate | avg CPU | max RSS 1 proc | cgroup anon peak |
  | 1  | 880 | 106 | 591 | 81 + 50 | 100% | 19.6 GB | 18.6 GiB |
  | 8 (default) | 435 | 106 | 135 | 71 + 73 | 355% | 14.0 GB | 29.1 GiB |
  | 16 | 360 | 107 | 82 | 59 + 62 | 452% | 14.0 GB | 30.4 GiB |
  | 32 | 339 | 106 | 77 | 52 + 53 | 564% | 14.0 GB | 36.5 GiB |
  X-09 scales (591 -> 77 s). Floor ~290 s = serial load_fold (json decode + sha256 of the 2.2 GB instances.jsonl) + per-request and
  alternate phases that barely gain from workers (largest legs straggle; parent 14-30 s CPU each) + ~40 s startup/output.
  (cgroup memory.current peaks of 97-116 GiB were page cache from the 38 GB tar, not GM.)
- Conclusion for Step 2: NOT triggered. Worst case (1 worker) 15 min, default 5-7 min; 84% of CPU already on forked workers. The
  remaining serial pieces are ~2 min; cutting them would mean touching the fold loader or the canonical-hash serialization of record
  (changes identity risk) for a minute or two. No code change.

## Rebase
- 08:40Z staging moved: retire-v1 merged (5ad682d3) and the vllm relayout applied at 738e63f5 (08:22Z; GM now
  `verity_vllm/check/global_match.py`, fixtures.toml path unchanged). Branch fast-forwarded to 738e63f5 (no local commits then).
- Validation Attempt `r20260924-084953-66e6` launched 08:49:53Z at 738e63f5 (tree shipped afresh; my smoke test's __pycache__
  quarantined). Command = dc38's recorded line with `-m verity_capture.experimental.cb_a.global_match` -> `-m verity_vllm.check.global_match`.
  Expected non-timing diffs: impl.module, impl.source_sha256 (the checker's identity, relayout rewrote its imports).
- CHECKPOINT gm-fix MET (08:52Z): no fix needed (see Profile conclusion); nothing ported from 6bf4a00b because it is already in staging.
- CHECKPOINT gm-validate MET (09:00Z): r20260924-084953-66e6 done 08:58:24Z, rc 0, 452 s, validation passed: verdict PASS,
  failed_checks []; global_match.json vs dc38 = 37 timing + impl.module + impl.source_sha256; match_decomp.json = 2 timing;
  global_match_global_program.json byte-equal. PRESERVED (5/5; run_files art:ab2eff88, result art:ae668a73).
  Profile/scaling evidence PRESERVED art:5a4512c21d00f7546b3942f1d74d92c0991d304137e746f5fe41edc50504dd8f.
- 09:00Z commit `03a68aa8` (fixtures.toml #23 comment, +5 lines) on staging 738e63f5, pushed to origin/lane/vllm-gm-scale.
  test_check_lifts 5 passed; TOML parses.
- 09:01Z ready note -> integrator/20260924T0901Z-from-vllm-gm-scale-ready-03a68aa8.md.
- 09:01Z `research pods drain vyv-gm`: TERMINATED, 1 attempt, preserved. machines.toml annotated. Lane DONE.

## Step 1 evidence (gm-answer)
- Sweep Match `r20260923-233020-dc38` (vllm.match, source `014563ac`, vyv-sw-67, 23:30:30Z-00:07:42Z, state done rc=0 validation=passed),
  input build `art:ee33269a…` (Build `r20260923-222456-bdbc`), output match `art:d39b5ef8…`, logs `art:e70477db…`, run_files `art:8ae59292…`.
- It ran with ACQUIRE_ENGINE=v2 (row.log: "acquisition manifest for the capture ... (ACQUIRE_ENGINE=v2)").
- stages.txt: `match PASS 00:07:42Z rc=0/0/0 wall=2230s verdict PASS global PASS dag concurrency 64 tokens_equal True fold True`.
- match.log: capture 302 s, control 21 s, resolve 33 s, fold 1544 s.
- global_match.log: `impl=fast workers=8`, cpu_count 128 (host shared with #67's fold). Phases (wall / main-proc CPU):
  load_fold 84.3/85.7, x09 84.7/27.3, g1 0.5, attribution 1.2, g2 0.0, g3_g4_g5_per_request 53.4/13.2, g6 0.6, g7 2.6, g8 1.2,
  alternate_criterion 54.0/17.2. Total 282.7 s (`seconds` field 228.8 = through g8). Verdict PASS, G1..G8 PASS, alternate (sequence) PASS.
- Harness lift (checks/global_match_checks.lift) of dc38's global_match.json vs frozen #23 contract: every verdict field equal; only
  `fold_record_pins` differs (frozen 9b4800d7/54fbdae6 vs dc38 b8b94844/cc58d832: a new fold record's file bytes).
- decomp_hashes lift of dc38's match_decomp.json vs frozen: requests (all per-request canonical shas), attribution, verdict, xreq_total equal;
  oracle.digest differs (0847cede vs 2d79f7eb), instances 2855826 and n_input_nodes 65 equal.
- The 8.3 h run: diagnosed in `6bf4a00b` (in both 014563ac and my base): the by-hand rerun used the un-memoised `record` checker (CLI default),
  plus a dangling-path load failure in-row. `fast` measured 230 s / 8 workers on vyv-v2cpu2 over the acquire lane's record art:33632a00.
- `F-r18-tap-GM-runtime`: not found in the repo (any branch), notes, or transcripts.
- Match artifact skipped `match/instances.jsonl` (> MAX_FILE). The only stored copy: row-dir tar `art:50076ee1…` (40.5 GB, fixture/v1).

## Earlier lane (coordinator note 08:05Z)
- `origin/lane/vllm-v2-gm-scale` = one commit `6bf4a00b` on the v2 merge `22e10e0e`. Merged into staging (`lane/vllm-cleanup-2`) at
  `68112222` (2026-09-23 17:48Z); hence also in the sweep source `014563ac`. NOT in `lane/vllm-v2` or `main`. Worktree `v2-gm` holds no
  other GM work (only two rebuilt .so files modified).
- What it did: CLI default `record` -> `fast`, `relocate_components()` for a staged Build's dangling component paths, stderr banner.
  Measured on vyv-v2cpu2 over the acquire lane's v2 record `art:33632a00`: fast w8 230 s / 13.7 GB main RSS; fast w1 525 s / 19.5 GB;
  record checker killed at 2081 s, 49 GB, in G7. Harness lift 0 diffs vs frozen; decomp_hashes only `oracle.digest` (= R19 Build epoch,
  shared with v1 a131). Preserved `art:be911dec…`. Caveat it noted: 8 forked CoW workers can raise the cgroup by up to ~90 GB in X-09.
- Its fix holds up and is already in my base; nothing to port.

## Pod vyv-gm
- `vc6jt5jzdb7gcv`, cpu3m 32 vCPU / 256 GB cgroup, 250 GB disk, $1.76/h, 38.80.152.147:32544, created 07:52Z. In machines.toml.
- Source `38122d1f` shipped via git archive (33 s) to /workspace/research/src/<sha>. Bootstrap --cpu BOOTSTRAP-OK 07:55Z. py-spy + GNU time.
- 07:56Z pod-side fetch of `art:50076ee1` (b23.tar) -> /workspace/gm/row (script /workspace/gm/fetch.sh, log fetch.log).
