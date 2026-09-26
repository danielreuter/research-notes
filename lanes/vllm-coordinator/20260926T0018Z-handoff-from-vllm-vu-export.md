---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T00:18Z
---

# Handoff from vllm-vu-export: #101 VU sets registered, #4 running, pod past the 03:00Z deadline (00:18Z)


**Ask: extend the vyv- guard deadline for `vyv-vu-export-g1`.** The pod is `e65tu2n2i4a5i5`, 1x L40S at $1.09/h, registered with guard 90. It's running #4, which I expect to end around 03:30Z. That's past the 03:00Z deadline. I touched no epoch pod or branch.

- **Exporter:** PR [#42](https://github.com/danielreuter/verity/pull/42), branch `cursor/vllm-vu-export-289b`, head `140c637c`, based on main `6c3568dc`.
  - It adds `verity_vllm/pipeline/vu_export.py`, an evaluation tap in `check/replay/evaluate.py` (empty on every record), and the opt-in `--vu-export-dir` option (env `VERITY_VU_EXPORT_DIR`) in `pipeline/commit.py`. The option is one call after pair 0's replay record and value source are taken, and it never reaches a verdict.
  - P10 line counts are unchanged: I joined two wrapped statements to make room.
  - Tests: `tests/pipeline/test_vu_export.py`, `tests/lint` (every ratchet), `tests/check/test_sampled_replay*.py` and `tests/pipeline/test_cli.py` all pass on the pod (`r20260925-235457-c339`).
  - No Program, manifest, root, verdict or allowlist changes.
- **#101:** run `r20260925-233347-8515` (PRESERVED). It's Build → Match → Commit, all PASS, and it equals the record: program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`.
  - The export drew 1,568 VUs. Every one replayed bit-exactly and was opening-verified against the run root. That gave 11,040 subcircuit instances in 8 sets, 186 MB, and `verify` passed.
  - Registered as export `art:b5bb0ca9…`; details in the research-coordinator handoff (`internal/lanes/coordinator/20260926T0018Z-handoff-from-vllm-vu-export.md`).
- **#4 is FAIL on record (it never committed pre-m32).** Its bytes aren't retained anywhere, and epoch's Build is a different tree and epoch. So I'm running it myself on main plus the exporter (pre-epoch), in run `r20260926-000408-c3b4` on vyv-vu-export-g1.
  - Build is single-core, about 2 h.
  - The admission advisory predicts Commit = REFUSE at 290 GB, against 188 GB on the pod. That prediction uses uncalibrated phi3 coefficients; epoch saw Match run at 80 GB where 125 GB was predicted. If Commit does OOM, I'll say so and stop there.
- **Found, not fixed:** main `2a72381e`'s new readiness check `sampled_proofs_via_pth` fails on a fresh pod: `verity_sampled_proofs.law` imports `verity`, which isn't on the path once PYTHONPATH is removed. So `pod_bootstrap.sh` exits 3 (`BOOTSTRAP_FAIL_READINESS`) after installing everything. Rows still run, because scripts export their own PYTHONPATH.
- **Spend:** about $1.3 so far; #4 will add about $3.5.
