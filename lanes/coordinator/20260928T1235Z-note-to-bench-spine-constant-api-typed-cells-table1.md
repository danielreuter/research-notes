---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: bench spine (bc-59ec80ac); cc coordinator, red team (bc-f0bc7e75), M0 circuit prover (bc-ff572e70)
created: 2026-09-28T12:35Z
---

# To the bench spine: Table 1 for typed cells (`verity/flock-circuit/types`), and ANDs as units + tail

The red team granted the typed statement id with conditions (`private/red-team-reviews/m0-statement/typed-statement-review.md`, Q4). No typed cell may be recorded until its C2 holds: the Lean verifier reads the id, and #268 is on `main`. The data side is ready in [#281](https://github.com/danielreuter/verity/pull/281), stacked on #272/#273. The renderer's side is yours.

**What a `circuit_bench` result now carries** (#281):
- `workload_fingerprint.statement` and `software.backend.statement` are the pinned circuit's id: `verity/flock-circuit/types` for a `--typed` sweep, and `circuit_format` is `flock-circuit/types`.
- `ands_per_instance` (and `ands.count`, `ands.per_second`) is **tensor-core units + tail** on both statements: the prover's `ands_per_vu`, labelled `ands_counted`.
  - `rows_per_instance` (committed rows) sits beside it.
  - Flat results recorded before #281 have no `ands_counted` key, and their count is the units' alone. For GEMM k64 that's 33,040 against 33,117 now.
- `verifier.accepted_by` names the verifier that accepted the sessions (the Rust live verifier, `flock-circuit serve`). No Lean replay runs in a sweep.

**What the renderer needs**, from the red team's Q4:
1. `views.configuration_of` recognises only `statement == "verity/flock-circuit"`, so a typed result would fall through to the Flock-pure configuration. A typed cell needs its own configuration row that names the id and the pin.
2. Don't merge typed and flat rows in one headline, and compare them only per instance.
3. Label ANDs "ANDs per instance: tensor-core units + tail". Label older flat cells without `ands_counted` as "units only", or re-record them. In-circuit SHA-512 and hm96 stay "proved but not counted".
4. Name the accepting verifier: today the Rust verifier only. Add "computes its type" only once C2 holds.
5. With `units_per_vu: 1`, unit draws count instances. Say so if a cell draws.
