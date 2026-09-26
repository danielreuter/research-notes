---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T05:16Z
---
# MERGE-READY admission fix: `lane/vllm-rf-admit` 02b3be03 (base origin/main 7289e3ad)

**Commits** (on 7289e3ad):
- `7b9558b7`: `git cherry-pick -x 89cd9d1a`. `commit.admission_lag(wl) = global_program.workload_target(wl).lag()`, the broad except
  is gone, and it adds `tests/pipeline/test_admission_commit.py`. The one conflict was `p10_size.json`: commit.py `main` is capped at
  the merged size, **1770** (main had 1776; the fix removes 6 lines from `main`). The module stays at 2939. The cherry-picked message
  still says "1913 -> 1907", which are the epoch branch's numbers (no amend).
- `02b3be03`: two lint follow-ups the cherry-pick needed on main. The `[moe R17-1]` round tag is dropped from `admission_lag`'s
  docstring (P11). The now-stale P7 `broad-except` entry for commit.py `main` is deleted. **No allowlist grows.**

**Gates.** One pod, vyv-rf-m32-admit: 1x RTX A4000 host, GPU hidden with `CUDA_VISIBLE_DEVICES=-1`, 128 cpus. Every CPU shape
returned "no instances available". I used `gate-tools/gate_b2.sh`: a git clone of the shipped sha, clone = shipped (0 differing
entries), `verity_sampled_proofs importable` on both sides.
- Base 7289e3ad: r20260926-031830-2411 (with bootstrap). Head 02b3be03: r20260926-041141-1cd3. Both PRESERVED. The earlier head
  7b9558b7, r20260926-031940-f369, is also PRESERVED (evidence only).
- **Collected:** base 4123, head 4124 (+1, the new test). `tests.check.test_sampled_replay*` has 96 testcases on each side and
  `tests.commit.test_challenge` has 15.
- **Gate (b)** (`baseline-jdiff.py` 363304c0, run on the VM over the pulled XMLs): base 3801 passed / 30 failed / 286 skipped /
  6 xfailed; head 3802 / 30 / 286 / 6. Outcome changes 0, new failures 0, new skips 0, new skip reasons 0. Only in head:
  `test_admission_commit::test_the_commit_admission_counts_the_declared_lag` (passed). All 11 tests in `test_admission_commit.py`
  pass. Evidence: `lanes/vllm-rf-m32/evidence/admit-jdiff-base-vs-02b3be03.txt`.
- For comparison, 7b9558b7 against base shows exactly the two lint regressions that 02b3be03 fixes (P7 stale entry, P11 doc-round):
  `evidence/admit-jdiff-base-vs-7b9558b7.txt`.
- **Lints:** rc 1 on both sides, with the same single failure. **Main already fails
  `test_no_by_name_rules::test_every_by_name_rule_is_allowlisted`**: `vu_export.py:478/481` `verify_set` path predicates
  (`fam in ("Gemm_v1", "Gemm_v2")`, `fam in ("Attention_v3", "Attention_v2")`) are not in `by_name_allowlist.json`. The assertion
  lines at base and head are identical (`evidence/admit-lints-base-vs-02b3be03.txt`). This branch doesn't touch it. It belongs to
  whoever owns vu_export (found-not-fixed).

**Digest-neutral:** no check reads `admission_*.json`, and the declared lag equals the old fallback of 1 on every regression row.
No GPU row was run.

**Process note:** my first in-pod jdiff copy was an empty file, which piped `ssh cat >` turned into 0 bytes. The "rc 0" it gave
meant nothing. The numbers above come from the real tool run on the VM.

**Pod:** vyv-rf-m32-admit terminated 05:15Z. Task 3 spend about $0.50 of $3. Lane total about $9.
