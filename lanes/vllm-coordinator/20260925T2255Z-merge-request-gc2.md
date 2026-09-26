---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: gc2, gate (b) harness follow-ups (test-side only), from vLLM coordinator bc-ecac3029, 22:55Z

- **Merge:** `lane/vllm-rf-gc2` @ **`a0ec1083`**, `--no-ff`. Test files only:
  - `0a043f11` retires the `pod_release.sh` checks;
  - `1c6efa53` retires the `ship.sh` and `sparse-patterns` checks;
  - `1ec0c565` retires the SCHEMA.md half of the card test;
  - `6f95928a` is a `test_source_identity` docstring (it needs a git checkout);
  - `a0ec1083` makes G4c read the integration's files.
  Plus a two-parent merge of main `7da00370`.
- **Recheck against main `5f8d8789`:** clean, and every ratchet lint runnable without pytest passes on the merged tree
  (39/39). The one shared file is `tests/program/test_harden_guards.py` (b5vc).
- **A known gap after the merge, with a follow-up:** b5vc's hunk builds G4c's `vllm_bindings` list with
  `glob(os.path.join(ROOT, ...))`, where `ROOT` is the stale path gc2 found. On the merged tree that glob returns nothing,
  so G4c skips the 13 `vllm_bindings/*.py` files, silently. The merged tree isn't worse than main today (main's G4c
  checks nothing at all), but it isn't the fix. Lane gc makes the follow-up right after this lands: in that glob,
  `ROOT` becomes `INTEGRATION`, with `test_harden_guards.py` run on a pod. The G4b/G1-G4b/G5 stale-ROOT uses are in the
  same follow-up.
- **Gates** (on vyv-rf-gc2-cpu, in git clones of the shipped sha, with `protocols/sampled_proofs` on PYTHONPATH):
  - lints rc 0 on both sides;
  - base `r20260925-205634-fe83`: 41 F / 11 E / 287 S; head `r20260925-205636-fd0a`: 35 F / 11 E / 286 S;
  - jdiff rc 0: 0 new failures or skips, 7 retired (deleted/renamed, listed), 2 renames pass;
  - `test_source_identity` ×4 passes on both sides (git checkout).
- **Root decisions, as carried out:** the harness runs gate (b) in a git clone (no skips); veritor files: the pod-script
  tests are retired, and SCHEMA.md/sparse-patterns are retired too, because no product code reads them (evidence in
  READY.md).
- **Finding:** without `protocols/sampled_proofs` on PYTHONPATH, a post-#29 tree loses about 437 tests at collection
  (35 files) and gets 31 more failures, on **both** sides, so a jdiff stays clean.
  `lanes/vllm-rf-gc/evidence/gc2-bootstrap-gap-unfixed-vs-fixed-base.txt`.
- **Evidence:** `lanes/vllm-rf-gc/READY.md` (gc2 section), `lanes/vllm-rf-gc/evidence/`; handoff
  `lanes/vllm-coordinator/20260925T2245Z-handoff-from-vllm-rf-gc.md`. Pod terminated; about $4.84 of $6.

