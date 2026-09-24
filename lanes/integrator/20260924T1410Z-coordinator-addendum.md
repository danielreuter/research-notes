---
id: integrator/20260924T1410Z-coordinator-addendum
lane: integrator
kind: report
status: final
repo: verity
created: 2026-09-24T14:10Z
origin: coordinator eb746331
---
# Coordinator addendum to int-final (20260924T1352Z-final)

- **Staging tip is now `f0810a11`.** It is `f16703a2` plus a `--no-ff` merge of `lane/vllm-gm-scale` `03a68aa8`, which adds 5 comment lines to row #23 in `tests/regression/fixtures.toml` recording the fresh v2 GM-01 evidence. int-final left it out. The merge is comment-only: `test_check_lifts.py` 5/5 and `fixtures.toml` parses (vyv-sw-57, venv312). The harness counts in int-final (fA-final 14 pass / 10 skip / 0 F, fB-final 59 pass / 75 skip / 0 F at `f16703a2`) still hold.
- **Corrected run ids.** At the merged tree `f16703a2`: #57 Commit PASS is `r20260924-103124-47d5` (verdict `art:bad7b21c`), and #67 Commit PASS is `r20260924-102613-0196` (verdict `art:51826b81`). int-final's `r20260924-075409` is the earlier #57 PASS at `2c5e038b`. The #23 fresh GM-01 PASS at `738e63f5` is `r20260924-084953-66e6`. With these, the sweep has 7/7 v2 Commits passing.
- **Gap.** The unit gates were not re-run at `f16703a2` (the stale-import repair, 3 files). The 57-fix lane ran the pod tests at `f16703a2` (156 pass, 4 skip, 0 F), including the new `tests/test_imports_resolve.py`, and the final harness ran at `f16703a2`.
- **New failure to look at:** research `test_pythonpath` fails after the relayout (+1 F vs rv1), per int-final.
- **Evidence** is in `final-evidence/` next to this note:
  - `cpu2-harness.tgz`: gates logs + junit, fA-final junit.
  - `cpu3-harness.tgz`: fB-final junit + log.
  - `sw57-lane-logs.tgz`: headless agent stream logs for integrator and retire-v1. `*.dup-killed` is the duplicate integrator killed at 09:05Z; `*.opus-failed` is the Opus launch attempts that hit the usage limit.
