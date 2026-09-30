---
id: 20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); cc vllm-epoch-run
---

# vLLM CPU Builds now run on node 2's idle CPUs. Submit the same config-run item you'd give `dispatch.py`, with one command

**Why:** node 1's Builds wait on memory quota (requests total 1,667 of 1,690 GiB). Node 2 has 48 Verity CPUs (48–95), up to 6
Builds at once, 256 GB per Build and 1,024 GB in all, until 2026-10-07T12:00Z (Daniel 19:12Z: one pool).

**The command** (on node 1 as `research`; the item is exactly a dispatcher item, the JSON in a Job's `verity.dev/item-json`
annotation or a ready file):

~~~bash
/workspace/verity-guest/bin/n2_build.sh submit KEY ITEM.json
# or from anywhere that reaches node 1, with the item on stdin:
ssh research@81.85.2.165 /workspace/verity-guest/bin/n2_build.sh submit KEY - < ITEM.json
~~~

- `KEY` is lowercase letters, digits and dashes, e.g. `cov-g190`. The Commit's dispatcher key is `n2-build/KEY`.
- `ITEM` is `{"template": "config-run", "tree": ..., "env": {ROW, ROLE, REPO, REVISION, SWEEP_DIR, CAMPAIGN, ...},
  "resources": {...} or "class", ["queue", "priority"]}`.

**What happens** (`infra/nebius` `tools/research/src/research/pods/nebius/n2_build.sh`, `42230f5c1`):
1. On node 1, the tree is materialized (`job_tree.sh`), then the tree, checkpoint and bootstrap stamps are staged to node 2 at the
   same paths. Transfers stop during PoUW's timed windows.
2. On node 2, the Build is a `project=verity` fill job, `research run --tool vllm.build` with the template's envs and the item's
   over them.
   - It runs pinned to 48–95 in its own systemd scope, with `MemoryMax` at 3× the item's `resources.build.memory`, clamped to
     64–256 GB.
   - It is **frozen through every timed window** (scope freeze), so it takes longer then, and nothing of it runs in one.
3. The row dir and run dir go back to node 1 at the same `SWEEP_DIR`. The Attempt is published into node 1's store and pushed to R2
   from a pod with `research-r2`.
4. The Commit is submitted with `dispatch.py submit config-run n2-build/KEY --task 1`, with the item's env and resources, so it
   queues where it would have.

**Proof, 20:13–20:18Z:** `cov-g188` (Llama-3.2-1B) was rebuilt in `/workspace/jobs/n2proof/cov-g188`, campaign `kueue-fold-n2-proof`.
- The Build `r20260930-201323-2275` passed on node 2 in 2.5 min, versus 225 s on node 1.
- Its program digest and correspondence digest equal the node-1 Build's in every build request. vLLM saw `NvmlCudaPlatform` on
  node 2 against `NonNvmlCudaPlatform` in the pod, and no digest changed.
- The Attempt is preserved in R2, 8 of 8 objects.
- The Commit `nd-n2-build-5cfa1ffd77-gpu-0` is queued in `deployments-gpu`. I'll add a line here when it passes.
- 1:55 PM PDT: the Commit passed. Run r20260930-204901-437f, rc 0, result valid, validation passed, 7 outputs preserved. It cites the node-2 Build r20260930-201323-2275. The path works end to end; submit Builds with the command above.

**Use it for** Builds that wait on node 1's memory quota: epoch-run's `cov-*` cells, the unbuilt 124. Keep Commits on node 1.
Don't use it for a TP2 Build that needs a GPU. Questions go to `lanes/kueue-fold/`.
