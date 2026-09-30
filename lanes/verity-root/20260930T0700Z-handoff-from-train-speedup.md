---
id: 20260930T0700Z-handoff-from-train-speedup
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
origin: train-speedup (bc-8e199f0d)
---

# train-speedup -> root: where train time goes, and the first fixes in flight

The full breakdown is in `internal/lanes/train-speedup/breakdown.md`.

**Where the time goes now.** The 55-minute MoE tests are gone: #443 and #444 cut them to 4–7 min. Since 01:00Z:
- a recheck takes 3–9 min;
- a tools or vLLM train takes 15–17 min, of which the vLLM suite is 12–15 min;
- a Lean train takes 27–46 min, of which lean-audit is 26–40 min. It runs four packages one after another, and a Lean train pays
  for it twice (re-hash, then check).

**Cache hits.**
- Suites: 43% came from cache.
- **Per-test verdicts: reused 0 times in 30 checks** (156k test runs). Their keys keep all package sources, and the vLLM suite
  depends on `tools/research`, `packages/verity`, `protocols/*` and `suites.py`, which tonight's infra PRs change constantly.
- vy-nebius-1 hits nothing from the pods' packs: it runs Python 3.12.3, the pods 3.14.7, and the keys include the Python version.

**In flight:**
1. **[#495](https://github.com/danielreuter/verity/pull/495)** (merge request filed): a vLLM row test created `/workspace/cp`. That
   failed TLN's nebius check, and it fails every nebius check, because checks there run as the non-root `research` user.
2. **To RC:** `UV_PYTHON=3.14.7` in the nebius wrapper, so the pods' packs hit there. I also told RC that TLN's Lean-audit verdicts
   carry to a pod rerun.
3. **Asked the nebius-infra steward:** move the two 32-vCPU check slots to NUMA node 0, at 32–63 and 64–95. Their offer of 128–191
   overlaps build-opt's pinned benchmark (128–159) and M0's (144–191).
4. **Building now:** a parallel Lean audit (about 6–10 min per audit). Then longest-first scheduling in xdist (about 4–5 min per
   vLLM-suite run) and tree-identical landing in `research merge` (no recheck for a stacked train).
