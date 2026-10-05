---
id: 20261004T2359Z-report-node-side-move-audit
campaign: migration
lane: infra
kind: report
status: open
repo: verity
origin: infra coordinator's worker (bc-840a95cf)
---

to: infra, top's layout worker (`cursor/layout-move-c3b2`). This audits the node side (n1 = vy-nebius-1, n2 =
vy-nebius-2) for repo paths and Python module names that the layout move changes. Destinations come from
`note:20261004T2125Z-draft-move-map-core`, `-protocols`, `-backends-integrations-tools` and `-move-inventory`. The
audit used origin/main (worktree `/tmp/wt-nodeaudit`) and read-only inspection of both nodes. `tools/move/layout.py`
isn't on any branch yet, so this note gives exact strings rather than checking the script's output.

## Verdict

Nothing on either node breaks when the move lands. Every live job runs from a tree pinned to a commit from before
the move, and every installed unit and binary names only paths that stay (`tools/research/`, `tools/cluster/`,
`integrations/vllm`, `benchmarks/pouw`) or plain absolute node paths. The risk is in the research package. Its
strings name paths and modules at whatever commit it runs against, and node jobs read them through the research
snapshot that each run ships to `/workspace/research/tool/<sha>`. One live binary on both nodes, `vy-node-sweep`,
must be hand-edited rather than rewritten. See the next section.

## Missed by a plain path rewrite (read first)

1. **`tools/research/src/research/pods/health.py:58`** builds a dotted module in an f-string,
   `-m backends.direct.ligero.pod_health`. A slash-path rewrite doesn't see it. Its `REF =
   Path("backends/direct/ligero/pod_health_ref.json")` on the same file is a plain path and will be caught.
2. **`tools/research/src/research/store/tools_registry.py`** holds `module:attr` specs in dotted form (list below).
   A slash-path map misses all of them unless the module map is applied to string literals too.
3. **`notes.py:1431` and `store/parity.py:168`** build `f"verity_numerical.bench.{mod}"`. Only the prefix appears
   literally, and `mod` is `tables` or `drilldown`. The ci answer in the backends map already puts both files on
   `move-check`'s allowlist (#1140), but they render a source tree at a given commit. A plain rewrite breaks renders
   of commits before the move, so pick the module by whether the tree has `backends/numerical/` (see item 5).
4. **Nested Lake packages.** `backends/flock/verifier/lean/level3` and `.../lean/soundness` go to
   `security_proofs/flock/`, but their parent prefix goes to `verity/protocols/verification/flock/lean`. The path map
   must apply the two nested entries before the parent, or both land under the verifier.
5. **Commit-aware readers** read a path at a commit through `git show` or a source tree. A rewrite makes them fail
   on every commit before the move, so each needs a fallback to the old path, following `queue.RULES_BEFORE_MOVE`:
   - `queue.py:666` `LEAN_BUILDS = ("backends/flock/verifier/lean",)`.
   - `jobs/cli.py:110` `UPSTREAM = "backends/flock/verifier/upstream.json"`, read by `_show(commit, path)`.
   - The numerical render module in item 3.
6. **`/usr/local/bin/vy-node-sweep`** on n1 and n2 (md5 `7129426e…`). It is installed from the unmerged infra branch
   `cursor/steward-home-2-558b` (`tools/research/src/research/pods/nebius/node_sweep.sh`), so the move PR doesn't
   carry it. Lines 207-208 list the Lean package paths and glob over every source tree:
   `for p in $SRC/*/backends/flock/verifier/lean{,/level3,/soundness}/.lake/packages.rs-trash-*`.
   A prefix rewrite breaks the brace group, and trees from before the move remain on disk (249 under
   `/workspace/research/src` on n2). So the sweep must glob both layouts. Infra edits it by hand on that branch and
   redeploys. The move script must leave it alone if that branch lands first.

## Table

| location | what it references | old -> new | owner | action |
|---|---|---|---|---|
| `research/store/tools_registry.py` | `flock_pure`, `flock_class_sweep` specs | `backends.flock.tool:` -> `benchmarks.flock.tool:` | infra | (a) |
| `research/store/tools_registry.py` | `flock_agreement` spec | `backends.flock.verifier.tool:` -> `tools.lean_agreement.tool:` | infra | (a) |
| `research/store/tools_registry.py` | `bench_vu`, `ligero_verify_batch`, `bench_vu_fp8`, `bench_vu_fp4` | `backends.direct.ligero.` -> `archive.direct.ligero.` | infra | (a) |
| `research/store/tools_registry.py` | `a_gpu_prove` spec | `backends.gkr.gpu.tool:` -> `archive.gkr.gpu.tool:` | infra | (a) |
| `research/pods/health.py:58` | f-string `-m` module | `backends.direct.ligero.pod_health` -> `archive.direct.ligero.pod_health` | infra | (a) |
| `research/pods/health.py` `REF` | health reference file | `backends/direct/ligero/pod_health_ref.json` -> `archive/direct/ligero/pod_health_ref.json` | infra | (a) |
| `research/queue.py:666` `LEAN_BUILDS` | Lean build dir at a commit | `backends/flock/verifier/lean` -> `verity/protocols/verification/flock/lean` | infra | (a), plus an old-path fallback |
| `research/jobs/cli.py:110` `UPSTREAM` | upstream pin via `git show` | `backends/flock/verifier/upstream.json` -> `tools/lean_agreement/upstream.json` | infra | (a), plus an old-path fallback |
| `research/notes.py:1431`, `store/parity.py:168` | render module f-string | `verity_numerical.bench.` -> `benchmarks.numerical.` | infra, ci | (a), plus a tree-dependent choice |
| `research/pods/nebius/provers.sh:5` (`/usr/local/bin/vy-provers` on n2) | comment only | `backends/flock/pod/cpu-slices.sh` -> `benchmarks/flock/cpu-slices.sh` | infra | (a), then (b) at leisure |
| `/usr/local/bin/vy-node-sweep` (n1, n2; branch `cursor/steward-home-2-558b`) | Lake trash glob over all trees | both layouts must be listed | infra | (b), hand-edited, not rewritten |
| `deploy.toml` entries whose `src` moves to `infra/nebius/` | `user-cpuset.conf`, `dispatch-n1.env`, `vy-keeper-n{1,2}.service`, `vy-keeper.timer`, `vy-lean-cache-daily.*`, `infra-pool-publish.*`, `n2-custody.*`, `sky/store_evict_src.conf`, `vy-cluster-agent.service`'s `by` | `tools/research/src/research/pods/nebius/` -> `infra/nebius/` | infra | (b) |
| `deploy.toml` `[[tree]]` to `/workspace/jobs/dispatch/infra/nebius` | the sky job YAMLs | src `tools/research/src/research/pods/nebius` -> `infra/nebius` | infra | (b) |
| `deploy.toml`, other entries | `tools/research/...` code, `tools/cluster` | unchanged | infra | (d) |
| n1 dispatcher `taken/` items (prover-bench, prover-dev) | CMDs `bash backends/flock/pod/74-gemm-hill.sh`, `73-sweep-shape.sh`, `python3 backends/flock/pod/vllm_overhead.py`; PYTHONPATH `$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/backends/flock/python` | `backends/flock/pod/` -> `benchmarks/flock/`; PYTHONPATH from `research.pythonpath` | proofs | (c) when the next item names a post-move tree |
| n2 fill `running/pous-vllm-e2e-series-f4a5eee3-*.sh` (renews itself) | `SHA=f4a5eee3…`, PYTHONPATH `$TREE/packages/verity/src:…:$TREE/protocols/{sampled_proofs,pous,pouw}` | rebuild PYTHONPATH from `research.pythonpath` | memory-accounting (bc-15ada664) | (d) while pinned; (c) when the SHA is bumped |
| n2 fill `held-overnight/aw-advdebit-{a,b,c}-0e4b2442.sh`, `aw-debit7bfold-bbb9521d.sh` | absolute `/workspace/research/src/<old sha>/packages/verity/src`, `benchmarks/pouw/approved_weights/` | unchanged while pinned | compute-accounting (bc-8412d697) | (d); (c) if regenerated after the move |
| n1 `/workspace/jobs/gm-label/label_loop.py` (live) | `NODE_TREE=/workspace/research/trees/cursor-grid-boundary-gm-827a`, `{NODE_TREE}/packages/verity/src` | `packages/verity/src` -> repo root | circuits | (d); (c) if circuits moves that tree past the move |
| n1 `/workspace/jobs/gm-feed/gm_feed.py` (idle) | `integrations/vllm/.../tp/lease.py` | unchanged | circuits | (d) |
| `vy-cluster-agent.service` | `@SOURCE@/tools/cluster/src`, `descriptions/nebius.toml` | unchanged | infra | (d) |
| `n2_commit.sh`, `n2_build.sh`, `sky/vllm_bootstrap.sh`, `config-run*.yaml`, `port-capture.yaml`, `dispatch.py:623` | `integrations/vllm`, `verity_vllm.pipeline.*` | unchanged | infra | (d) |
| `sky/jobs/prover-{bench,dev}.yaml` | `PYTHONPATH=$SRC/tools/research/src`, then the owner's `$CMD` | unchanged (the CMD is the owner's) | infra | (d) |
| console `/workspace/research/console/{verity_console,util_collect}.py` | matches main's md5s, no moved paths | unchanged | console | (d) |
| comments in `pods/connect.py:14`, `fill_runner.py:135`, `weights.tsv`, `vm_setup.sh:52` | `backends/direct/ligero/live.py` (archive), others stay | optional comment fix | infra | (a) for `connect.py` only, cosmetic; else (d) |
| n2 `cpu-sets`, `windows`, `max-min`, empty fill queue; `/tmp/n2-q-close.sh`, `locks/quick-slot-widen.sh` | no repo paths | none | infra | (d) |
| keeper (`/workspace/research/keep`), Lean cache (`/usr/local/lib/vy-lean-cache`) | not installed on either node | none | infra | (d) |
| crontabs (research, root, `/etc/cron.d`) | only atop, e2scrub_all, sysstat | none | none | (d) |

## Operational notes for the redeploy

- **Old research snapshots.** A run launched from a research copy older than the move ships that copy as
  `/workspace/research/tool/<sha>`. Against a tree from after the move, its `tools_registry` specs and its
  `LEAN_BUILDS` and `UPSTREAM` constants point at old paths. Launchers on control pods and VMs should update their
  research checkout when the move lands. The old-path fallbacks above keep the reverse case working: new research
  against an old tree.
- **Warm Lean dependencies go cold once.** check keys `cache_dir()/lean-deps` by manifest bytes and toolchain. The
  move changes the `require path` lines in the nested lakefiles, so the first check after the move on each node
  rebuilds Mathlib and ArkLib cold. Plan one slow check per node. It doesn't fail, it just takes longer.
- **Templates are pinned.** The dispatcher pins each item to a copy of its template (`templates.by-sha`), so
  redeploying the `[[tree]]` doesn't change queued items.
- **Hand-written PYTHONPATHs** in owners' jobs (proofs, memory-accounting) should switch to `research.pythonpath`,
  which derives the path from the pyprojects and follows any later move without edits.
- No node file needs editing before the move lands. Infra's redeploy after landing amounts to `research pods
  deploy` from the merged tree plus the `vy-node-sweep` edit.

## Exact strings for the move script's maps

Path map, in this order:
- `backends/flock/verifier/lean/level3` -> `security_proofs/flock/level3`
- `backends/flock/verifier/lean/soundness` -> `security_proofs/flock/soundness`
- `backends/flock/verifier/lean` -> `verity/protocols/verification/flock/lean`
- `backends/flock/verifier/upstream.json` -> `tools/lean_agreement/upstream.json`
- `backends/direct/ligero/pod_health_ref.json` -> `archive/direct/ligero/pod_health_ref.json`
- `backends/flock/pod/cpu-slices.sh` -> `benchmarks/flock/cpu-slices.sh`
- `backends/direct/ligero/live.py` -> `archive/direct/ligero/live.py` (comment in `pods/connect.py`)

Module map, applied to string literals in `tools/research/src/research/`:
- `backends.flock.tool:FLOCK_PURE` -> `benchmarks.flock.tool:FLOCK_PURE`
- `backends.flock.tool:FLOCK_CLASS_SWEEP` -> `benchmarks.flock.tool:FLOCK_CLASS_SWEEP`
- `backends.flock.verifier.tool:FLOCK_AGREEMENT` -> `tools.lean_agreement.tool:FLOCK_AGREEMENT`
- `backends.direct.ligero.` -> `archive.direct.ligero.` (the four registry specs and `health.py:58`'s f-string)
- `backends.gkr.gpu.tool:A_GPU_PROVE` -> `archive.gkr.gpu.tool:A_GPU_PROVE`
- `verity_numerical.bench.` -> `benchmarks.numerical.` (`notes.py:1431`, `store/parity.py:168`, with the
  tree-dependent choice)

Hand edits, not map entries: the fallbacks for `queue.LEAN_BUILDS` and `jobs/cli.UPSTREAM`, and `node_sweep.sh`.
