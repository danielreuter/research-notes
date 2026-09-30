---
id: 20260930T0815Z-report-kv-prefix-design
campaign: overnight-sep30
lane: build-v2-kv
kind: report
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

CHECKPOINT a309b142f (14:36Z) [open] post-merge A/B done: all 3 rows byte-identical across arms and to baselines; 1k target tip/main wall 0.66x, RSS 0.54x (1480/2231 s, 6.4/11.9 GiB). merge request note:20260930T1436Z-merge-request-build-v2-kv-517 sent; attempt 2 (1k row, 32 vCPU) r20260930-143337-636d running
CHECKPOINT a309b142f (14:14Z) [open] post-merge A/B: prefill rows identical across arms and to baseline; tip/main wall llama 0.75x, mistral 0.62x, RSS 0.68x/0.57x. tip 1k decode row 1480 s at 16 vCPU (main arm still deriving). tip run rc 3 only because the 1k row has no baseline row (stale harness copy; fixed). next: 1k digests, attempt 2
CHECKPOINT a309b142f (13:32Z) [open] post-merge same-time A/B running: main 1c10b00c+bench r20260930-133041-d53d (96-111) vs tip a309b142+bench r20260930-133103-9fef (112-127); rows llama/mistral prefill + Build owner's llama32-1b-1k:decode target. Inbox: steward submit.sh note n/a (no Kueue submits). ends ~14:35Z
CHECKPOINT a309b142f (12:26Z) [open] attempt 1 r20260930-095541-fa3e done: 6/6 rows digest-identical, 330 labels; prefill wall 0.55-0.67x of baseline. P10 lint failed on the branch: fixed (shared program.replay), main merged (a309b142), lint+1665 vllm+306 core tests pass. next 13:30Z: main-vs-a309b142 digest A/B, then merge request
CHECKPOINT ddeabc86 (10:39Z) [open] attempt 1 r20260930-095541-fa3e: 3 prefill rows rc 0, wall vs baseline llama 367/585 s, mistral 573/848, olmoe 640/1161; decode rows running (llama LP26), no foreign load on 96-127; digests checked at end, ~12:05Z
CHECKPOINT ddeabc86 (09:56Z) [open] A/B r20260930-092548-94d4: tip vs main same-time, digests identical; llama prefill wall 0.70x RSS 0.61x, mistral prefill wall 0.66x RSS 0.58x. attempt 1 (tip ddeabc86, 6 rows) r20260930-095541-fa3e running on 96-127, ends by 12:26Z
CHECKPOINT 720a8c3d (09:28Z) [open] A/B 8db4 failed: main arm refused at precheck (inherited the tip's RESEARCH_SOURCE_SHA); stopped, ab_run fixed. Rerun r20260930-092548-94d4 (2 prefill rows, both prechecks pass), check ~09:55Z. Build owner's 6451 shared 96-127 08:39-09:27. next: attempt 1 on tip, 6 rows, done by 12:28Z
CHECKPOINT 720a8c3d (08:47Z) [open] attempt 0 (c379497f, r20260930-072938-7ebd) done: 3 rows digest-identical to baseline; 165 labels (build-v2, attempt 0, noisy). A/B main 29f691be vs tip ddeabc86 r20260930-084525-8db4 on 96-111/112-127 running, check ~09:50Z. draft PR #517. next: attempt 1 on tip
CHECKPOINT ddeabc86 (08:14Z) [open] WAITING r20260930-072938-7ebd on vy-nebius-1 (mistral row, 2 llama rows digest-identical), check after 08:30Z; agent bc-57ddc507; next: label attempt 0, A/B main vs tip ddeabc86 on 96-127
# build-v2: key/value references shared as a prefix (Build plan change 3)

Branch `cursor/build-v2-kv-prefix-d717`. Every change is representational: the Program, its descriptor, the workload Program, the
manifest and the runtime correspondence are byte-identical to `main`'s. Only how the builder holds them in memory changes.

## The quadratic term

Call `t` of an attention layer reads the key and value rows of calls `0..t`. On `main` each call builds that reference sequence
afresh (`concat` of `t` rows), and every consumer of the Program then walks all `t` parts again:
- replay (`derive._substitute`) slices and re-concatenates them;
- the descriptor encoder flattens them and keys each part for its alias search;
- liveness marks every part;
- the correspondence emitter walks and locates every run;
- the decoder and the composition (`workload._remap`) copy and remap every part.

Over a prompt of `L` tokens that is `O(L²)` parts per layer in each of these passes, though the rows themselves are only `O(L)`.

## The change

`verity.ir.refs.PartLog` is an append-only list of parts. `log.cut(j, extra)` returns exactly `concat(parts[:j] + extra)` (the same
normalized value: empty parts dropped, broadcasts merged, contiguous `Affine` chains merged), and when the result is a `Concat` it
records `prefix = (log, j)`. `log.raw_cut` is the decoder's form (`Concat(parts[:j] + extra)`, not normalized, as the decoder built
before). A consumer that sees `prefix` does the work for the shared prefix once per log, memoized on the log, and only the tail per
call:

| Pass | File | What is shared |
|---|---|---|
| attention rule | `rules/common.py` `kv_logs`, `vllm_bindings/attention.py`, `rules/profile.py` | one key log and one value log per layer; call `t` cuts `P` rows |
| replay | `frontend/derive.py` `_substitute` | the substituted log per source log |
| encoder | `verity/ir/codec.py` `_flat_keys` | the part keys of the log's parts; the alias search itself is unchanged |
| decoder | `codec.py` `_decode_refs` | an alias to the whole log so far extends it |
| liveness | `verity/ir/liveness.py` `mark` | the prefix is marked once per body |
| runs | `refs.py` `prefix_runs` | the log's runs |
| correspondence | `frontend/emit.py` `_arg_runs`, `_locate_shared` | the located spans of the log's runs |
| composition | `program/workload.py` `_remap` | the remapped log per source log |

Other exact changes on the branch:
- `Concat.slice` bisects to the parts in range instead of visiting all of them;
- `Ctx.rebind` reads a storage base's alias group from a reverse index instead of scanning every node;
- the v1 encoder interns each type object and callee object once per descriptor, and skips revisiting a definition object;
- `derive_report` reuses the flat digest for a flat Program instead of encoding it a second time;
- the manifest logs how long it waited for the machine-wide component-pool lock.

The descriptor's alias rule and every serialized byte are as on `main`: the digest depends only on each argument's flat part
sequence, and every cut has the flat parts `concat` gives. `tests/ir/test_part_log.py` checks cut against `concat` on randomized
part lists (broadcasts, empties, chains, `Explicit`, `Strided`, nested `Concat`), and that encoding, decoding and liveness of cuts
equal those of `concat`. `tests/program/test_workload_program.py` checks that the composition's log path gives the same body
encoding. No Definition or circuit changes, so `circuit-check` has nothing new to check.

## Same-time A/B, main against tip (09:26–09:53Z)

Run `r20260930-092548-94d4` ran main 29f691be on CPUs 96–111 and tip ddeabc86 on 112–127 at the same time:
- each arm had its own `TMPDIR`, so neither waited on the machine's manifest lock;
- serial derives, no unit-rule cache, no Program cache.

Both rows are byte-identical across the arms and to build-v1's baseline (workload, manifest, component and correspondence digests,
gates).

| Row | Build wall, tip vs main | CPU-s, tip vs main | Peak RSS GiB, tip vs main |
|---|---|---|---|
| llama32-1b prefill | 395 vs 562 s (0.70×) | 625 vs 805 (0.78×) | 2.30 vs 3.78 (0.61×) |
| mistral-7b prefill | 589 vs 891 s (0.66×) | 980 vs 1296 (0.76×) | 3.69 vs 6.41 (0.58×) |

- **Where the time goes:** the derive spans (request and per-LP requests) and the global program shrink; the manifest is unchanged.
- **Where the memory goes:** the RSS drop comes from 3936d722, where the composition remaps each key/value log once. Attempt 0
  (c379497f) lacked it and matched main's RSS.
- **No labels on the A/B.** Its two arms share one run, and the dashboard reads one point per ref per run.
- **An earlier A/B failed.** `r20260930-084525-8db4`'s main arm inherited the tip's `RESEARCH_SOURCE_SHA`, and the row precheck
  refused it; `ab_run.py` now sets each arm's own.
