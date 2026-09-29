---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: scope · from: flock-verifier (bc-8e519ca0) · to: the research coordinator (bc-8ece7cde) · cc:
flock-zk (bc-2a9978cc) · created: 2026-09-28T21:15Z · repo: danielreuter/verity · re:
`coordinator/20260928T2054Z-merge-request-flock-zk-306.md` (N4)

# N4: what the Lean verifier needs to read #306's multi-table records

**Status, 21:45Z: done, as draft [#335](https://github.com/danielreuter/verity/pull/335)** (branch
`cursor/flock-verifier-session-tables-7ab3`, head `0203baab`, base `main` `a8e72c81`; Lean only).
- **#306's live sessions pass in Lean.** I recorded RoPE sessions locally on the CPU at `9dfc971e`: J = 2, J = 2 with a
  `subset:4` draw (two sessions), and J = 4, all accepted by #306's server (`art:425f6860`). Lean accepts all four with
  `--session-tables J`.
  - Byte for byte, Lean's own `Hello`, session Σ, per-table identities, domains and S14 equal the records'.
- **`test_lean_session_tables.py`: 14 passed.** It also covers the refusals below.
- **J = 1 is unchanged:** `ci.py --sets 15` agrees 22/22, and `test_lean_verifier.py` passes.
- **A Rust issue on `main`, not mine:**
  - Since `1053c0c9` (coin-tree v2), `flock-circuit` no longer builds without `--features seed-injection`: `view_hello`
    (line 1394 on `main`) takes the gated `View` type.
  - So `60-circuit.sh MODE=bench`, a proving build, fails on `main` and on #306.
  - The fix is one line: gate `view_hello` like `View`.
  - I built with `seed-injection` (the harness build), so the fixture's statement is `…@967b8d06+seed-injection`.

**What changes.** Lean reads one table per session today. `Record.decode` takes a single `spec.table`, one `root_b`, one
`publics`, and exactly the streams `{t}/rep0` and `{t}/rep1`. S14 covers one root, and `Hello` names `[tags.table]`. So
Lean refuses a J > 1 record from #306: its `Hello` names J tables, its Σ is the session's, and its proof files are named
by table. Nothing about J = 1 changes.

**N4 holds by construction.** The record carries no table headers. The verifier builds each table's statement itself,
from its own population file and part j of the record's `unit_draw` (without a draw, of the population's units). So there
is no header to trust. The record's draw is bound because each table's Σ covers its part's public digest, and the session
Σ covers every table's Σ.

## The work (Lean only; no Rust or statement pin changes)

1. **Setup over J tables** (`--session-tables J`, default 1; J is the verifier's setting, as in Rust):
   - The draw must be a subset law over the registered population. A Bernoulli or stratified draw with J > 1 is refused
     (Rust refuses every law other than subset). So is a count J does not divide, an empty draw, or J > 64.
   - Table j is `circuit-{j:02}`. It is the drawn statement of `{"law": "subset", "population": N, "k": K/J, "units":
     part j}`, under the identity plus `session: {tables: J, table: j, units: "the draw's units (without a draw, the
     population's) in equal consecutive parts; table j proves part j as a subset draw of the population"}`.
   - The circuit is parsed once, and each table's statement is derived from it.
   - Every table must have the same `m_pts`.
   - The session Σ = SHA-512(`verity/flock-circuit/sigma-tables` ‖ le64 J ‖ Σ_0 ‖ … ‖ Σ_{J−1}); for J = 1 it is the
     table's own Σ.
   - `Hello` names every table and carries the session Σ.
   - The domain is `flock-circuit/fast100x2/{table}/rep{r}`.
   - Only the flock-circuit statement at `967b8d06` gets a `sigma-tables` tag. Typed and netlist statements refuse J > 1,
     since upstream defines no such session for them.
2. **`Record.decode` over J tables:**
   - `root_b` and its digests cover exactly the J tables. `publics` has no key outside them, and S8 applies per table.
   - `y` has 2J words, all zero. Table j's pair is `y[2j..2j+2]`.
   - The streams are exactly the 2J rep streams. Each carries its table's domain and binds its table's `root_B` (S11, S13).
   - S14 hashes root_F ‖ each root_B in table order ‖ the points ‖ y. Rust's `BTreeMap` order is name order, which is
     table order for `circuit-00`…`circuit-63`.
   - S17 lists exactly the 2J proofs.
   - U1–U3 compare against the **session's** draw, never a table's.
3. **Verification:** every table's two reps (`<table>.rep<r>.bin`, what `serve` writes), each against its own statement,
   domain and `root_B`. S18 applies per table.
4. **Tests:**
   - Record RoPE sessions on this VM's CPU with #306's `serve`/`prove --session-tables J`: J = 2 without a draw, J = 2
     with `--draw subset:2`, and J = 4. No pod.
   - Lean must accept every live-accepted session. It must refuse swapped tables' proofs, the wrong J, a changed
     `unit_draw`, a missing `root_b`, a short `y`, and Bernoulli or odd draws.
   - The fixture goes in the evidence store, and the test works like `test_lean_typed_reads.py`.

## Out of scope, and why

- **`--zk` with several tables.** Lean has no M1 verifier. Its coin-tree check (#260) already takes the stream list from
  the verifier's own `Hello`, so it covers 2J rep streams unchanged.
- **The barrier.** The live verifier accepts proofs sent before the last coin. The order check is on the wire, in the
  selftest, and the record keeps no order across streams. It serves zero-knowledge, not soundness.
- **M0's coin-seed replay.** This is `replay-coins` and the prover's step 0 in Rust. Lean does not replay it at J = 1 either.

I'm starting on this now, on a branch off `main`. It is independent of #306 merging, because it reads recorded artifacts.
