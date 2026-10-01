---
id: 20261001T1153Z-report-from-circuits-gemma-sampler-cg02-04-pass-460
campaign: verity
lane: circuits
kind: report
status: final
repo: danielreuter/verity
origin: circuits-gemma-sampler
cursor:
  subagentId: "bc-0918173f-aaba-5a55-a671-49c9887db9ee"
---

# circuits-gemma-sampler -> @circuits (4:53 AM PDT, final): all three Gemma-2 B1 stochastic reruns pass 460/460 with the grid cell's env, and no code change was needed

**Outcome.**

- cg04-2, cg02-2 and cg03-2 all pass. Each Build's strict word check passes under Q_word_v1{X=16,W=32}, with the sampler Call one unit
  (MAX_GATES raised to 225000000), and each replay is 460/460 equal with 0 mismatches.
- There is no branch, no PR and no run-branch commit, so there's nothing to land by 7:50 AM. circuit-check doesn't apply because no circuit
  changed.
- Why no Definition fix: note:20261001T0953Z-report-from-circuits-gemma-sampler-no-definition-fix-env-rerun. In short, only root-level
  sampler Calls with committed interior values get cut separately (option 1), and that's Daniel's call.

| key | row | Build (wall, word check) | Commit (GPU-held) | replay, config PASS | run root |
|---|---|---|---|---|---|
| `cov-cg04-2` | B1 i256/o32 Gumbel p1 | `r20261001-094742-4b9c` (761 s; 0 rules cut, cache, 39 s) | `r20261001-100125-c1fc`, **12.6 min** (754 s) | `r20261001-101957-173a`, 10:23:39Z | `c22469530fd2f335` |
| `cov-cg02-2` | B1 i1024/o128 top-p p0.95 | `r20261001-100333-12f4` (2815 s; 1790 rules cut in 333 s) | `r20261001-105114-894a`, **35.2 min** (2112 s) | `r20261001-112716-10c1`, 11:42:20Z | `3e7d938b40888310` |
| `cov-cg03-2` | B1 i1024/o128 Gumbel p1 | `r20261001-100533-74ef` (2835 s; 0 cut, 74 s) | `r20261001-105650-c540`, **36.1 min** (2168 s) | `r20261001-113536-dc1e`, 11:48:37Z | `2951884c98d4098f` |

- **Manifests:** at o32, 301,328 Calls give 716,676,853 units over 45.7G gates (35,045 identities). At o128, 1,208,144 Calls give
  3,188,349,605 units over 187.6G gates (138,917 identities).
- **Commits:** all ran on node 1 GPUs, admitted at once, with no offload. Each left its slim keep (40.8 MB, 127 MiB, …) and deleted its bundle.
- **Where the GPU-held time went** (seconds):

  | row | engine build | committer setup | instrumented warm-up | instrumented pair |
  |---|---:|---:|---:|---:|
  | cg04-2 | 213 | 75 | 119 | 143 |
  | cg02-2 | 193 | 324 | 534 | 573 |
  | cg03-2 | 185 | 315 | 474 | 736 |

  - cg02-2's warm-up was 532 s of hashing on the saturated 96–127,176–191 slice (load average 100–216).
  - cg01, alone at 05:09Z, took 21 min. circuits-commit-phases counts about 32 idle GPU-minutes each for cg02-2 and cg03-2
    (note:20261001T1135Z-report-from-circuits-commit-phases-held-idle-since-1030z).
- **Build memory:** cg04-2 peaked at 16.7 GiB RSS on its 48G request.

**Notes.**

- **Labels:** vllm-epoch-run is asked to adopt `cov-cg02-2`, `cov-cg03-2` and `cov-cg04-2` in its labeller
  (note:20261001T0957Z-handoff-from-circuits-gemma-sampler-cg02-04-reruns). The copy of `label_loop.py` in the notes doesn't list them yet,
  so nudge them if the coverage table needs these rows. n032, n033 and n034 keep their (correct) fail labels.
- **Dispatcher pitfall (mine, fixed in flight):** `dispatch.py submit --priority P` pins every task of the item to P, so the Commit and
  replay lose the template's `circuits-gpu` (600). I lifted cg04-2's replay to 600 and dropped `priority` from cg02-2's and cg03-2's item
  annotations, so their Commits and replays ran at 600. Don't pass `--priority` to config-run.
- **Possible follow-up (main only, not tonight):** `word._name` could print the gates and the limit for `too-large`. The rule entry already
  has them (`{'class': 'too-large', 'gates': 204337818, 'limit': 24000000}`), but the message says only "too-large, 32 Call(s)", which is how
  this read as a width problem. Changing `word.py` on the grid tree would invalidate every cached unit rule, so it belongs on main.
- I'm submitting no other Gemma-2 row. circuits-commit-phases' plan-tree settings
  (note:20261001T1043Z-handoff-from-circuits-commit-phases-gemma-on-plan-tree) are noted for whoever runs the next one.
