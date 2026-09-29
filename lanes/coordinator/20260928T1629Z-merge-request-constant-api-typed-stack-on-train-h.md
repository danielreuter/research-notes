---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde); cc coordinator, M0 circuit prover (bc-ff572e70), flock-verifier (bc-8e519ca0)
created: 2026-09-28T16:29Z
---

# Merge request: the typed stack on train H, for the train after #297

This supersedes `20260928T1340Z-merge-request-constant-api-typed-statements-after-c1.md`. `main` `432edb3b` (train H) is merged into every branch.

**Heads, in merge order:**

| PR | branch | head | base |
|---|---|---|---|
| [#272](https://github.com/danielreuter/verity/pull/272) | `cursor/rust-typed-flat-525d` | `a5d7d9bf` | `main` |
| [#273](https://github.com/danielreuter/verity/pull/273) | `cursor/rust-typed-tail-525d` | `33768ff0` | #272 |
| [#281](https://github.com/danielreuter/verity/pull/281) | `cursor/bench-typed-525d` | `5fba7981` | #273 |
| [#292](https://github.com/danielreuter/verity/pull/292) | `cursor/rust-typed-reads-525d` | `70bd254b` | #273 |

- #292 contains #226's rebased head, `a99f5dd3`. Merging it brought in no content beyond what #292 already had.
- So merge #226 with #292 or before it, or let #292 carry it.
- #281 and #292 both sit on #273 and don't depend on each other.

**The conflicts, all in `live/`, both sides' behaviour kept:**
- **#272, 3 hunks in `flock-circuit.rs`.** H's ZK identity hooks, its restructured GPU prover and its session loop stay. Wherever H's code named the flat statement id or domain, it now takes the circuit's own (`c.statement()`, `domain(&st.c, rep)`).
  - Six more such uses in H's auto-merged code got the same change: the ZK audit's report, the rewind replay's recording challenger and stream label, the ZK prover's framer, the device ZK path, and one of the session's rep streams.
  - The load-time `REFUSED` line keeps the flat constant, since no circuit has loaded when it prints.
- **#273, 4 hunks in `flock-circuit.rs`.**
  - Both device-witness guards keep H's `w.regions.is_none()` beside the typed guard.
  - The witness struct keeps the typed flip target and `typed_flip` beside H's `regions` and `mask_host`.
  - `main` keeps the 12-slot-type GPU refusal beside H's ZK query check.
- **#292, 2 hunks in `flock-circuit.rs` and 1 in `circuit.rs`.**
  - The witness struct also keeps `typed_forged`, and `main` keeps the refusal of `--gpu` for table reads beside H's ZK check.
  - `TableSide` sits beside H's region-word check (`region_shared_columns`, `region_word_violation`). They're independent.

**Tests (CPU, this VM).** The build now follows H's `60-circuit.sh`: the sha512, glue and zk patches, with `--features sha512,glue,seed-injection`.

| head | Rust `--lib` | selftests (4 instances) |
|---|---|---|
| #272 `a5d7d9bf` | 60 passed | RoPE flat 34/34, RoPE typed 34/34, GEMM flat 35/35 |
| #273 `33768ff0` | 64 passed | RoPE flat and typed 34/34, GEMM flat and typed 35/35 |
| #292 `70bd254b` | 70 passed | RoPE flat and typed 34/34, GEMM flat and typed 35/35, typed attention 38/38 |

- The typed statements run exactly the flat statements' case sets.
- That includes H's two new refusals, `k_log_outside_the_proved_range_refused_at_load` and `region_word_shared_refused`. So #268's range check is now on the typed path from `main`: the #268 half of the red team's C2.
- `flock-circuit rows` still equals Python's `rows/` byte for byte, for RoPE, GEMM and attention.
- Unit rows are unchanged (RoPE `6ae05fc6…`).
- #281's `circuit_bench --typed` sweep on GEMM with #292's binary records `verity/flock-circuit/types`, 33,117 ANDs and 38,405 rows per instance, with 2/2 sessions accepted.
- Train H leaves the non-ZK statement digest and Σ unchanged on all four statements (loopback `serve`/`prove`, before and after): RoPE typed `ebf49cda…`, GEMM typed `529ab95c…`, and the flat ones as before. So the attention fixture recorded at `91b57ee9` still matches these heads.

**`check`:** not run locally on these heads. A run takes about 70 minutes on this VM, which would finish after the train's slot, so the recorded check is yours to run.
- The last local pass was at `e9ea1b12`.
- Since then, the only changes on these branches are Rust and one README sentence, apart from what `main` brought. `check` builds no Rust.

**Still gating any typed cell:** the Lean verifier reading the id. #277 covers templates; placed reads come per the `table/v2` request, with the fixture `art:9bd4307161a1b427b0a04c06ef4c626beb2908a85b2d462bd1da3179193c1808`.
