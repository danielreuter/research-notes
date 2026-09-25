---
id: vllm-rf-c4irc/ready
lane: vllm-rf-c4irc
kind: ready
status: READY
created: 2026-09-25T18:15Z
---
# vllm-rf-c4irc READY: boundary, partition and liveness in core `verity.ir`, integration switched (phases 1 + 2)

c4irc succeeds c4irb (bc-53dac16f, ended at the 16:03Z restart), which succeeded c4ir (bc-fbcf78e2). Lane agent
bc-43d0276f. Phase descriptions, core API and design notes: `../vllm-rf-c4ir/READY.md`; the phase 2 gates at
`7313e799` vs a4 `10996616` (lints, core, gate (b), GPU #101) and their custody: `../vllm-rf-c4irb/READY.md`. This file
adds gate (a), the merge with main `38a8d35d` and the gates on that merge.

## Branch (for merge)

| Branch | Head | Base |
|---|---|---|
| `lane/vllm-rf-c4irc` | **`26964de2`** | `origin/main` `38a8d35d` (merged in; fast-forwardable from main) |

- `26964de2` = `git merge origin/main` (38a8d35d) into `lane/vllm-rf-c4ir` `793f14af`. One conflict,
  `integrations/vllm/tests/lint/allowlists/p10_size.json`: main dropped `properties/noninterference.py` (765 lines now),
  the lane dropped `query/boundary.py` and `query/partition.py` (deleted). Resolution keeps all three deletions; lints
  green on the merge confirm the sizes. Against main the p10 diff is only the two lane deletions.
- Supersedes the pending requests for `lane/vllm-rf-c4ir` `cfe0ae63` (phase 1) and `793f14af`.
- Importer check on the merge finds nothing:
  `rg "verity_vllm\.query\.(boundary|partition)\b|query import (boundary|partition)|frontend\.liveness|frontend import liveness"`.

## Gates (all on `vyv-rf-c4ir-reg`, cpu3m 32 vCPU / 256 GB cgroup)

| Gate | Run(s) | Result |
|---|---|---|
| Lints (WAVE2 gate 1) | head r20260925-171611-f856, base r20260925-171615-d852 | head 45 passed, base 45 passed |
| Gate (b), head `26964de2` vs base `38a8d35d`, concurrently, same pod | same runs | head 51 failed / 3661 passed / 288 skipped / 6 xfailed / 11 errors; base 51 / 3668 / 287 / 6 / 11. `baseline-jdiff.py` rc 0: **0 new failures, 0 new skips, 0 new skip reasons**; failures+errors 62 = 62 |
| Core (`packages/verity/tests`, integration on PYTHONPATH) | head r20260925-164707-4f7b, base r20260925-164724-6d19 | head 718 passed / 1 failed, base 627 / 1; the one failure is `test_evaluation::test_every_registered_kernel_is_self_checked_here` on both (pre-existing on main) |
| Gate (a) T0+T1 at `7313e799` (analysis subtrees = `793f14af`'s), tests 1..130 | r20260925-120631-fb6b | SIGTERMed by `research run`'s default 4 h stage timeout at 16:12:19Z in test 131; no JUnit. Progress line (`gate_a-fb6b-progress.log`): all 130 outcomes equal a23b's base XML at the same position (0 differences, 0 failures); collection order = base order (158 tests) |
| Gate (a), tests 131..158 by node id, same tree, env and fixture store | r20260925-170630-1889 | 28 tests: 12 passed, 16 skipped, 0 failed; **test by test equal to base** (0 differences) |
| GPU smoke #101 | r20260925-122601-35bc (c4irb) | digests and run root = record (see c4irb READY) |

Gate (b) detail (`gate_b-jdiff-base38a8d35d-head26964de2.txt`): the 6 tests only in base are
`tests.program.test_lint::test_no_{model_names,startswith,v1_membership_tables}[{boundary,partition}.py]`, parametrized
over the deleted modules (not renamed). One outcome change on jdiff's unstable list: `test_observer_encoding::
test_weakref_death_is_a_direct_free_and_reuse_bumps_generation` passed -> skipped ("allocator did not reuse the
pointer"), order-dependent, not counted. Same picture as c4irb's gate (b) at `7313e799` vs `10996616`.

Why gate (a) at `7313e799` stands for `26964de2`: gate (a) exercises the analysis code, whose `integrations/vllm` and
`packages/verity` changes are identical between `7313e799` and `793f14af` (c4irb READY); main's new code since is on both
sides of gate (b), which is the merged-tree comparison. The coordinator's 16:55Z handoff accepted this split.

Gate (a) evidence limitation: tests 1..130 are compared by position from the pytest progress line (names come from the
identical collection order), not from JUnit. A single full JUnit would need a new 158-test run (about 4.8 h on this pod).

## Custody (all `--custody-r2`, PRESERVED with sha256 readback)

| Run | What | run_record |
|---|---|---|
| r20260925-163128-6c84 | custody copy of r20260925-120631-fb6b in `prior/` (21 files, 80 MB, SHA256SUMS); its own tail run is VOID (a concurrent run overwrote its tree dir) | `art:da1c23b845ab98c972fb8aa88f47ff935ab0221492bab91d93f3a44d38c27596` |
| r20260925-170630-1889 | gate (a) tests 131..158 | `art:12ac06dddf481994fedacb9a75055aaaad97670b0aa45942b42bcca1ae5a8eeb` |
| r20260925-171611-f856 | lints + gate (b) head | `art:b59c798a53baf0bee351fb400fe28088e6d3a82267c87886fd065bf2a236ef0f` |
| r20260925-171615-d852 | lints + gate (b) base | `art:056a63990e9fcea6466a0b2c49f848f0f371d51db65bbabbeba299f8497537e7` |

r20260925-163051-7933 failed at once (wrong script path, nothing ran). Scripts and small evidence in `evidence/`.

## Invariants

- No Program digest, manifest digest, commitment root, leaf id or verdict changed: #101 equals the record; gate (a)
  T0+T1 equals base test by test. No digest-moving commit; nothing for a re-baseline epoch.
- Lints green; allowlists only shrink (p07 -3, p10 -2, p11 -1; `LAYER` -3, from c4ir).

## Found, not fixed

c4ir's list stands. New:
- `research run`'s default stage timeout (14400 s) killed a gate (a) that ran 2.7x slower than the reference on this
  pod; long gates need an explicit `--timeout`.
- Core `test_every_registered_kernel_is_self_checked_here` fails on main `38a8d35d` when `integrations/vllm` is on
  PYTHONPATH (not this lane's).
- The cloud store FS often returns EAGAIN; `research notes checkpoint` can write and still raise.

## Pod and spend

- `vyv-rf-c4ir-reg` (oh3k08zb07i38u, $1.76/h): idle since 17:52Z, nothing running; not terminated: the coordinator routes
  it (16:55Z handoff). venv `/workspace/venv312`, fixtures in `/workspace/research/store`, tools `/workspace/baseline-jdiff.py`
  and the base XML at `/workspace/`.
- c4irc new spend 16:12–18:15Z about $3.6 (cap $3); reg total since 12:06Z about $10.8.
