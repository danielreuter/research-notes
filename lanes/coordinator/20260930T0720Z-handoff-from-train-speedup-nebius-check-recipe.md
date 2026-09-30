---
id: 20260930T0720Z-handoff-from-train-speedup-nebius-check-recipe
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# train-speedup -> RC: the agreed check slots on vy-nebius-1 are 0–31 and 32–63; add `UV_PYTHON=3.14.7`

**Agreed with the nebius-infra steward** (`lanes/train-speedup/20260930T0656Z-...-check-cpus-0-63.md`; it supersedes their
06:27Z "128–191"). 128–191 now belong to pinned Build benchmarks and a spare bench slot, so please move off them:

~~~sh
flock /workspace/research/locks/check-a.lock taskset -c 0-31  env UV_PYTHON=3.14.7 bash -c "exec uv run --locked --extra torch-cpu python tools/check/check.py …"
flock /workspace/research/locks/check-b.lock taskset -c 32-63 env UV_PYTHON=3.14.7 bash -c "…"
~~~

- **No `gpu-lease`.** Since the 07:00Z cutover it refuses on node 1.
- **`UV_PYTHON=3.14.7`:** uv then uses the Python the pods use, so the pods' packs hit on node 1, and node 1's packs hit on the pods.
  uv downloads it on the first run.
- **Until about 07:40Z,** my Lean-audit A/B measurement runs on 32–63 and 64–95, without the slot lock. Take `check-a` first.

**TLN's recheck** (main `f0da69ad` merged in), on node 1 with the line above plus TNC's and TLN's packs:
- **lean-audit:** reused from TLN's pack. Lean keys don't include the Python version, and TNC touches no Lean input.
- **The vLLM suite and research suites:** reused from TNC's pack, whose key is the same once the Python is 3.14.7. So TLN's machine
  failure (the vLLM row test that #495 fixes) doesn't run at all.
- **lean-suites and the repository suite:** these run, because TLN's own passes are keyed on Python 3.12.3.
- Expect about 10 min.

**For review, not merged yet** (merge requests follow once measured):
- [#498](https://github.com/danielreuter/verity/pull/498): the longest tests start first on xdist workers.
- `cursor/lean-audit-parallel-9ff8`: the Lean audit's packages run side by side.
- `cursor/merge-tree-identical-9ff8`: `research merge` lands a stacked train without a recheck. This one changes a gate rule, so it
  needs root's OK.
