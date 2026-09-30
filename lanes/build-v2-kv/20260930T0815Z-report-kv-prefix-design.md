---
id: 20260930T0815Z-report-kv-prefix-design
campaign: overnight-sep30
lane: build-v2-kv
kind: report
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

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
