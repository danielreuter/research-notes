---
id: 20260930T0815Z-merge-request-train-speedup-498-508
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# Merge request (infra priority: faster checks): #508 and #498, with #495; #509 once root OKs it

| PR | Head | Change | Measured |
|---|---|---|---|
| [#508](https://github.com/danielreuter/verity/pull/508) | `cursor/lean-audit-parallel-9ff8` | The Lean audit runs its packages side by side. A build waits only for the builds it requires, and only the first `setup.sh` of each toolchain runs alone. | Cold, 32 vCPU each, vy-nebius-1: `main` 2,145 s against **1,564 s** (−27%). Both PASS: `r20260930-065348-2054` and `r20260930-071142-f9e7`. A Lean train pays for the audit twice (re-hash, then check). |
| [#498](https://github.com/danielreuter/verity/pull/498) | `cursor/suites-heavy-first-9ff8` | In parallel suites, the longest tests start at the heads of the xdist workers' shares. | An order only. By the longest-processing-time bound, the vLLM suite drops from 709–876 s to about 450–550 s. |
| [#495](https://github.com/danielreuter/verity/pull/495) | `43ec23e5` | The vLLM row test no longer creates `/workspace/cp`. | Needed for any check on vy-nebius-1. Earlier merge request: 07:52Z. |

- **Tests:**
  - `tools/lean` 22 pass, with a new event-ordered scheduling test.
  - `tools/check` 110 pass; the heavy-first placement is checked against the pinned xdist's own `worksteal` split.
  - The wall-clock and repository lints pass.
- **Merges:** the three merge pairwise with no conflicts.
- **Cost:**
  - #508 changes `tools/lean/`, which is in every Lean package's key, so its train runs one cold Lean audit.
  - #498 changes `tools/check/suites.py` and the guard, which are in every suite's key, so its train reruns every suite once.
  - Put them in one train so the cold run is paid once: about 25 min on a nebius slot.
- **Better, if you can wait about 30 min:** take the per-test traced-keys branch in place of #498.
  - Branch `cursor/per-test-traced-keys-9ff8`, the change root asked for. It already contains #498 and pays the same one cold rerun.
  - I'll file its merge request with the vy-nebius-1 measurement as soon as that run ends (`r20260930-080922-8337`).
- **[#509](https://github.com/danielreuter/verity/pull/509),** tree-identical landing in `research merge`: ready, but it changes a gate rule, so it waits for root's OK.
