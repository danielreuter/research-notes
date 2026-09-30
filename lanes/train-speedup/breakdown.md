---
cursor:
  subagentId: "bc-8e199f0d-8659-5bbc-8056-197f69ba9ff8"
lane: train-speedup
kind: report
created: 2026-09-30T06:55Z
status: open
---

# Where merge-train wall time goes (measured 06:55Z)

**Sources:**
- all 60 `check@1` Attempts in the evidence store since Sep 29 12:00Z, with their step records (`result` meta);
- `suites.json` and `lean-audit.log` from the `run_files` of the 30 that ran since 20:44Z;
- TLN's live run `r20260930-060431-64e5` on vy-nebius-1;
- RC's checkpoints for the train-level times.

Scripts: `/tmp/m/{steps,hits}.py` on this VM.

## 1. The 55-minute MoE tests are gone

#443 (fast `build-global`) and #444 (per-test verdicts) are on `main`. Since about 01:00Z, checks take:

| Kind of check | Wall | Critical step |
|---|---|---|
| Recheck after `main` moved, with a pack | 3–9 min | circuit-check on the changed targets (4–8 min); lean-suites (6 min) |
| Tools or vLLM train (TNB, TVE) | 15–17 min | pytest: the vLLM suite, 738–876 s on 6 workers |
| Lean train (TI2R, TX2) | 27–46 min | the Lean group: lean-audit 26–29 min, then lean-suites 6 min, then agreement 10 min |

Before #443, checks took 83–120 min. The two MoE tests now take 264 s and 388 s on t10, and 234 s and 433 s on nebius.

## 2. Critical path by step (misses only)

- **lean-audit, 26–40 min.** The four packages are audited one after another:
  - controls about 3.5 min;
  - `lean` 0.5–3.5 min;
  - `level3` 6.5–11 min;
  - `soundness` 16–28 min: its build takes 10–13 min, and its kernel replay 5–7.5 min, single-threaded;
  - POUS 1–2.7 min.

  `soundness` requires `level3` by path, so those two must run in order. Controls, `lean` and POUS need not. A Lean train pays for the
  audit twice: once in its re-hash or regeneration run (the same `audit.py --build`), and again in its check.
- **The vLLM suite, 12–15 min.** It has 4,280 tests, 50 CPU-min of test time. On 6 workers the longest-processing-time bound is
  501 s, but the suite took 876 s. On 16 workers the bound is 389 s (the Qwen3 test), but it took 709 s. The gap is scheduling:
  xdist's `worksteal` hands each worker a contiguous block of tests, and the two MoE tests sit in `tests/query/`, late in collection
  order, so they start late.
- **circuit-check, 4.7–8 min** when it misses; every target missed in TVE.
- **lean-suites, 5–18 min.** These are the `verity-flock` and lean-audit suites, 39 CPU-min, run after lean-audit.
- **lean-agreement, 10–15 min**, only when a train touches `backends/flock/`.

## 3. How often the caches hit (30 checks, 20:44Z–05:57Z)

- **Suites:** 254 of 596 suite runs came from cache (43%). The vLLM suite came from cache in 11 of 30 checks and ran in 19.
- **Per-test verdicts: never reused.** `reused` = 0 in all 30 checks, over 156,163 test executions, although each run keeps thousands.
  A per-test key keeps the suite's package sources whole. The vLLM suite's inputs include `tools/research`, `packages/verity`,
  `protocols/*`, `tools/check/suites.py` and `fixtures/artifacts.json`. So any infra, POUS or core PR reruns all 4,280 vLLM tests,
  and every per-test key misses with it.
- **vy-nebius-1 reuses nothing from the pods.** Its `uv` picks the system Python 3.12.3; the pods run uv's managed 3.14.7. Suite keys
  and circuit-check keys include the Python version. TLN imported the pack (5,423 entries), then ran 0 of 17 suites from cache and hit
  0 of 1,110 circuit-check targets.

## 4. Train level (RC's checkpoints)

| Train | Check | From check end to `main` |
|---|---|---|
| TX2 (Lean) | 45.6 min | 31 min |
| TNB (tools) | 14.8 min | 4 min |
| TVE (vLLM) | 17.0 min | about 17 min |

- **TLN (Lean)** started at 04:28Z. It ran two re-hash runs, one lost to a stale Flock.Draw. Its check started at 06:04Z on nebius and
  failed on a machine-specific test.
- **Parallel trains:** three run on `main` side by side. Each one that lands second merges `main` in and rechecks, 3–9 min plus a
  turn of RC's.
- **Launch losses tonight:** two runs killed at launch, a pytest failure caused by the machine (the next item), and a cold nebius
  cache.

## 5. What vy-nebius-1 exposed

- **A non-hermetic test:** `test_target_family` created `/workspace/cp`, which the non-root `research` user can't. It is fixed in #495.
- **Different Python:** 3.12.3 there against the pods' 3.14.7. Fix: `UV_PYTHON=3.14.7` in the check wrapper.
- **CPU overlap:** checks at 160–191 overlap M0's pinned 144–191, and the steward's offer of 128–159 overlaps build-opt's pinned
  benchmark. I proposed NUMA-0 slots of 32–63 and 64–95.
- **Plenty of headroom:** the host ran at load 14–22 of 192 vCPU at 06:28Z.

## 6. Plan, ranked by train time saved per effort

| # | Change | Saves | State |
|---|---|---|---|
| 1 | #495: row tests keep their build dir under `tmp_path` | unblocks every nebius check | PR, merge request in |
| 2 | `UV_PYTHON=3.14.7` on nebius; slots on NUMA 0 | about 10–15 min per nebius check: pod packs hit | told RC; asked the steward |
| 3 | `audit.py --all`: controls and independent packages in parallel, and `soundness`'s build overlapping `level3`'s replay | about 6–10 min per Lean audit, which runs twice per Lean train | building |
| 4 | Longest tests first in parallel suites: the guard spaces known-heavy tests across the workers' first shares | about 4–5 min per vLLM-suite run (19 of 30 checks) | next |
| 5 | Tree-identical landing in `research merge` (merge-workflow review, change 7) | the recheck plus RC's turn for every stacked train; lets RC check B-on-A speculatively and land it without a recheck | next |
| 6 | For the Lean org: replay soundness in chunks; keep each package's own `.lake/build` warm like its dependencies | 5–7 min and 5–10 min per Lean audit | proposal only (gate-semantics review) |
| 7 | For bc-1555924a/bc-d66f1270: per-test keys over executed files | per-test reuse above 0 | proposal only |

## 7. Status (08:50Z)

| Change | PR | Measured | State |
|---|---|---|---|
| Row tests keep their build dir under `tmp_path` | [#495](https://github.com/danielreuter/verity/pull/495) | unblocks nebius checks | merge request 07:52Z |
| `UV_PYTHON=3.14.7`; slots 32–63 and 64–95 | none (RC's wrapper) | pod packs now hit on nebius | root decided; told RC 07:25Z |
| Parallel Lean audit | [#508](https://github.com/danielreuter/verity/pull/508) | 2,145 s → 1,564 s cold on 32 vCPU (−27%) | merge request 08:15Z |
| Longest tests first | [#498](https://github.com/danielreuter/verity/pull/498) | by the longest-processing-time bound only | contained in #512 |
| Per-test keys narrowed to the traced reads | [#512](https://github.com/danielreuter/verity/pull/512) | an infra-only `tools/research` edit: 251 run, 4,031 reused, 55 s (was a full 660–950 s rerun); 332 of 365 modules traced | merge request 08:45Z |
| Tree-identical landing | [#509](https://github.com/danielreuter/verity/pull/509) | removes the recheck for a stacked train | waiting for root's OK (gate rule) |

**Train suggested to RC:** #495, #508, #512, and #509 once root OKs it. It pays one cold rerun (about 25 min on a nebius slot); every
later train then reuses per test.

**Evidence:** the A/B runs `r20260930-065348-2054` (Lean audit, `main`) and `r20260930-071142-f9e7` (#508), and
`r20260930-080922-8337` (#512, cold then after the infra edit), all in campaign `train-speedup`.

**Still open, as proposals:**
- **Soundness replay in chunks:** 450 s of single-threaded kernel replay on the Lean critical path.
- **A warm `.lake/build` per package:** 660 s of soundness build.

Both change the audit's trust argument, so they are for the Lean org.
