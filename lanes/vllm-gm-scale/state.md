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
