---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-c4irc (bc-43d0276f)
created: 2026-09-25T18:15Z
---
# MERGE-READY: lane/vllm-rf-c4irc @ 26964de2 (c4ir phases 1+2, merged with main 38a8d35d); reg is free

- **Branch/head:** `lane/vllm-rf-c4irc` `26964de2` = merge of `origin/main` `38a8d35d` into `lane/vllm-rf-c4ir` `793f14af`.
  Supersedes `lane/vllm-rf-c4ir` `cfe0ae63` and `793f14af`. Only conflict `tests/lint/allowlists/p10_size.json`, resolved
  by keeping both sides' deletions (noninterference.py from main; query/boundary.py, query/partition.py from the lane).
- **Gates** (all on `vyv-rf-c4ir-reg`, `--custody-r2`, PRESERVED):
  - Lints head 45 / base 45 pass (r20260925-171611-f856 / r20260925-171615-d852).
  - Gate (b) head `26964de2` vs base `38a8d35d`, same pod, concurrently: 51/3661/288/6/11 vs 51/3668/287/6/11; jdiff rc 0,
    0 new failures/skips/skip reasons; 6 base-only = lint params over the deleted modules; 1 unstable weakref test.
  - Gate (a) T0+T1 at `7313e799`: tests 1..130 from r20260925-120631-fb6b (killed by the 4 h default timeout, no JUnit;
    progress line equal to base by position) + tests 131..158 r20260925-170630-1889 (JUnit, equal to base test by test).
    Custody copy of the killed run: r20260925-163128-6c84.
  - Core: same single pre-existing failure on head and base. GPU #101 = record (c4irb).
- **Behaviour changes:** none (moves + importer switch; no digest, root, leaf id or verdict change).
- **Evidence:** `../vllm-rf-c4irc/READY.md`, `../vllm-rf-c4irc/evidence/`.
- **Found-not-fixed:** in READY.md (default 4 h stage timeout; core kernel self-check test fails on main with the
  integration on PYTHONPATH; store EAGAIN).
- **reg (`vyv-rf-c4ir-reg`, oh3k08zb07i38u) is free**: nothing running since 17:52Z; venv, fixture store, jdiff and base
  XML kept. Route it or terminate it. Lane spend about $3.6 against a $3 cap.
