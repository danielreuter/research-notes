---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator, the train after #289's
created: 2026-09-29T01:50Z
---

# Merge request: PR #327 (the host bucket), after #289; heads for #314, #289 and #327

| PR | Head | On |
|---|---|---|
| [#314](https://github.com/danielreuter/verity/pull/314) | `e33f7606b7c34c254461bf80d2eb62f4996c0a98` | `main` `5810574d` (post-#134) |
| [#289](https://github.com/danielreuter/verity/pull/289) | `5e5713fbe5368107757985326d6e5ab832a9f292` | `main` `b4fd93e9` (post-X), with #314 |
| [#327](https://github.com/danielreuter/verity/pull/327) | `6491cb37e5be4b09a609d10371f058de124768fc` | #289 `5e5713fb` |

- **#327:**
  - It's ready, and stacked on #289, so it merges after #289.
  - It changes the prover only. No statement or pin moves, so there's no statement reviewer.
  - It needs the agreement inputs, since it changes `backends/flock/`.
- **#327's results** (the sweep's L40S, m = 34):
  - median prove 3.055 → 1.202 s (K = 2,048) and 3.956 → 1.401 s (K = 8,192), in run `r20260928-213503-2861`;
  - host time 0.77–1.33 s → 3–6 ms per rep;
  - byte identity passes in `r20260928-214548-6d0c`.
- **#327's merge onto #289:** conflicts in `flock-circuit.rs`, the same two calls as #289's (#281's `domain`), both kept. The GPU builds compile and `gpu_circuit::tests` pass.
