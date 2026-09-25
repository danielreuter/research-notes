---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-gc
created: 2026-09-25T22:45Z
---
# MERGE-READY gc2: lane/vllm-rf-gc2 @ a0ec1083 (base 7da00370)

- Commits (test files only): 0a043f11 retire pod_release.sh checks; 1c6efa53 retire ship.sh + sparse-patterns checks; 1ec0c565 retire the
  SCHEMA.md half of the card test; 6f95928a test_source_identity docstring (needs a git checkout); a0ec1083 G4c reads the integration's
  files (b5vc). Merge of origin/main 7da00370 at 0c49886a.
- Gates on vyv-rf-gc2-cpu in git clones of the shipped sha, sampled_proofs on PYTHONPATH: lints rc 0 both; base r20260925-205634-fe83
  41 F / 11 E / 287 S, head r20260925-205636-fd0a 35 F / 11 E / 286 S; jdiff rc 0: 0 new fail/skip, 7 retired (deleted/renamed), 2 renames pass.
  test_source_identity x4 pass on both sides.
- Bootstrap gap: without sampled_proofs the same base had 35 files erroring at collection (~437 tests) + 31 failures, hidden on both
  sides. Evidence and per-file list: lanes/vllm-rf-gc/evidence/.
- WAVE2 gate (b) text should say: run from a git clone of $RESEARCH_SOURCE_SHA out of <root>/git/verity.git (script evidence/gate_b2.sh).
- Found, not fixed: G4b/G1-G4b/G5 in test_harden_guards use the same stale ROOT (EVIDENCE, DERIVE_STEP, G5 PYTHONPATH); see READY.md.
- vyv-rf-gc2-cpu terminated; spend ~$4.84 of $6. Full record: lanes/vllm-rf-gc/READY.md (gc2 section on top).
