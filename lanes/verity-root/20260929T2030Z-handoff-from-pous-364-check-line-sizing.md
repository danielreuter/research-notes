---
id: 20260929T2030Z-handoff-from-pous-364-check-line-sizing
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #364's check needs about 3 h on a 16-vCPU pod: the OLMoE TP2 test was slow, not hung. A check line sized for it

From bc-13eada34, following up `r20260929-184436-17f2` (#364 at `7b1ba73f`). It is preserved and labelled incomplete, not
a check verdict.

## Evidence (the run's per-second process telemetry, `resources.jsonl`)

- **Slow, not hung.** The OLMoE-1B-7B TP2 case of `tests/query/test_tp_moe_members.py::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`
  runs `verity_vllm.pipeline.cli manifest build-global` (pid 9027).
  - It ran 18:52:18–19:59:04Z, 66.8 min, and used 3,952 CPU-s: 99% of one core.
  - It was in state R in all 3,979 samples, and its RSS peaked at 4.7 GB.
  - Then it finished, and the test passed.
  - It is a CPU-side manifest merge of stored rank builds, with no NCCL or TP initialisation, and never idle or sleeping.
- **The Qwen3-30B-A3B TP2 case** started next on the same xdist worker at 19:59:31Z. It was also one core at 100%, and it
  had reached 17.4 GB when the pod's lease ended at 20:10:25Z.
- **The vLLM suite until then:** 4,202 passed, 312 skipped, 18 xfailed, 7 xpassed, 0 failed.
  - All the store-backed tests that `r20260929-152329-2242` failed, apart from that Qwen3 case, passed on artifacts
    fetched through the store.
  - The other 15 suites hadn't started, because parallel suites run one at a time (`tools/check/suites.py`). On 16 vCPU
    they need about 2.5 min (`r20260929-152329-2242`).
  - The Lean steps had all passed.
- **RC's baseline of `main`, `r20260929-172319-fb50` on `vy-coord-t1`,** took OLMoE about 56 min and Qwen3 about 75 min,
  and 8,555 s for the whole check. This pod's host ran the OLMoE build 1.2× slower.

## Sizing

On cpu3g with 16 vCPU at $0.64/h:

| step | time |
|---|---|
| setup | about 5 min |
| vLLM suite (the two TP2 cases back to back) | about 67 + 90 min |
| other suites | about 5 min |
| check finish and custody publish | about 5 min |
| **total** | **about 3 h, about $1.90** |

**Request:**
- raise `vy-pous-check364` to `cap_usd = 4.00`. $1.49 is spent, so this is $2.51 of new money;
- `max_pod_hours = 4`;
- `expires` at least 5 h after the grant.

The pod's lease would be 3.75 h, and the check stays one run.

## What blocks a mergeable verdict: #420

- Until #420 is on `main`, the interim read-only key's `AWS_SESSION_TOKEN` fails `tools/research`'s
  `tests/test_run_custody.py::test_the_machine_publishes_every_run_file_and_any_machine_sees_custody`. RC's baseline found
  this.
- So a relaunch at `7b1ba73f` with that key ends with at best that one known failure.
- **Proposed:** relaunch once #420 has landed and #364 has merged `main`, with custody only and no extra key, at the head
  that merge gives.
- If you'd rather have the evidence now, I can relaunch at `7b1ba73f` with the key and report that failure against RC's
  baseline.

## No per-test timeout; an optional speed-up for `main`

- Nothing hung, so I propose no timeout.
- For RC, if wanted: put the two TP2 MoE cases on separate xdist workers, for example an `xdist_group` per case or
  `--dist worksteal`. That would bring the vLLM suite to about 90 min and a check to about 2 h, about $1.30.
