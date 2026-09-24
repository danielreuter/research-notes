---
id: integrator/20260924T0901Z-from-vllm-gm-scale-ready-03a68aa8
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-gm-scale
---
# vllm-gm-scale is ready to merge: `03a68aa8` (#23 B64 fresh GM-01 closed; one `fixtures.toml` comment, no code)

`origin/lane/vllm-gm-scale` = **`03a68aa8`**, one commit on staging `lane/vllm-cleanup-2@738e63f5`, which is post-retire-v1 and post-relayout. Merging it is a fast-forward if staging hasn't moved.

## Commit
- `03a68aa8`: adds a 5-line comment to row #23 in `integrations/vllm/tests/regression/fixtures.toml`, next to `class = "GREEN"`, in the style of #70's note. It records the fresh v2 GM-01 evidence. There's no code, test or contract change.

## Why there's no GM code
- The v2 merge's open cell ("fresh B64 global-match on the new acquisition path not completed") was the 8.3 h run. That run used the record checker by default. `6bf4a00b` (`lane/vllm-v2-gm-scale`) fixed it by making `fast` the default and relocating a staged Build's component dirs. It's been in staging since `68112222` and was in the sweep source `014563ac`.
- The sweep's Match `r20260923-233020-dc38` (with `ACQUIRE_ENGINE=v2`) ran GM-01 in-row: fast, 8 workers, 317 s, **PASS** (G1..G8, X-09, alternate `sequence`). Commit `ca81` then passed on that Match.
- Worker scaling on vyv-gm (32 vCPU) gave 880, 435, 360 and 339 s at 1, 8, 16 and 32 workers, with cgroup anon peaking at 19–37 GiB. X-09 scales. The remaining floor of about 290 s is the serial fold load plus two phases where the largest per-request legs straggle. GM-01 is not single-core-bound and is well under an hour at every setting, so the lane's Step 2 was not triggered.

## Acceptance
- Fresh GM-01 at `738e63f5`: Attempt **`r20260924-084953-66e6`** on vyv-gm, **preserved** on R2.
  - It used dc38's recorded command line; the only change is the relayout's module name `verity_vllm.check.global_match`.
  - Wall time 452 s, rc 0, verdict PASS, `failed_checks` empty.
  - `global_match.json` vs dc38: 37 timing fields differ, plus `impl.module` and `impl.source_sha256`, which are the checker's own identity (the relayout rewrote its imports). Nothing else differs.
  - `match_decomp.json` differs in 2 timing fields. `global_match_global_program.json` is byte-equal.
  - Inputs recorded: Build `art:ee33269a`, Match `art:d39b5ef8`, row-dir tar `art:50076ee1`.
- The harness lift of dc38 against the frozen #23 contract gives equal verdict fields. The expected exceptions are `fold_record_pins` (a new fold record) and, in `decomp_hashes`, `oracle.digest` (the Build epoch). All 64 per-request hashes are equal.
- The profile, py-spy data and scaling runs are preserved as `art:5a4512c21d00f7546b3942f1d74d92c0991d304137e746f5fe41edc50504dd8f`.
- `tests/regression/test_check_lifts.py` passes (5 tests), and `fixtures.toml` parses.

## Not done / for you
- The #23 harness candidate-mode table from the sweep was lost (f455's output) and was not regenerated. GM-01 itself doesn't need it.
- Pod `vyv-gm` is drained and terminated (its 1 attempt preserved).
