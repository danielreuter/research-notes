---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: red-team-flock-3 · kind: handoff · from: flock-verifier (bc-8e519ca0) · to: red-team-flock-3 (bc-f0bc7e75) · cc:
the research coordinator · created: 2026-09-28T21:55Z · repo: danielreuter/verity

# Review: #335, the Lean verifier on sessions of several tables (#306's N4)

[#335](https://github.com/danielreuter/verity/pull/335) at **`a30afbd5`**, on `main` `a8e72c81`. It is Lean only: no Rust
change, no new pin, and no change to an existing pin. It is N4 from #306's review: when Lean reads a J > 1 record, it must
derive each table's part from `unit_draw`, never from a table's header. The spec is `PROTOCOL.md` §16.11. The scope note is
`coordinator/20260928T2115Z-scope-flock-verifier-n4-multi-table-records.md`.

## What it accepts

- **J is the verifier's setting.** It comes from `verify --session-tables J`, default 1, as in Rust. Only
  `verity/flock-circuit@967b8d06` (and `+seed-injection`) has `Tags.manyTables`; any other statement refuses J > 1.
- **The tables (`Stmt.setupTables`).**
  - The units are the record's draw's, or without a draw the population's `0 … N−1`.
  - The draw must be a `subset` law of the registered population. Refused: a Bernoulli or stratified draw, J > 64, no
    units, or a count J doesn't divide.
  - Table j (`circuit-{j:02}`) is §16.10's drawn statement of `{"law": "subset", "population": N, "k": K/J, "units": part
    j}`, over the verifier's own population file.
  - Its identity is the statement's plus `session: {tables, table, units: <upstream's text>}`, so each table's digest
    differs.
  - Every table has the same `m_pts`.
- **The session.**
  - Σ = SHA-512(`verity/flock-circuit/sigma-tables` ‖ le64 J ‖ Σ_0 ‖ … ‖ Σ_{J−1}). `root_F = Σ` (S6).
  - `Hello` names the tables in order, and S2 compares it byte for byte.
  - A table's domain is `flock-circuit/fast100x2/<t>/rep<r>`.
- **The record checks (§5.3 over every table).**
  - Per table: S5, S7, S8 and S13.
  - S10: `y` has 2J words, all zero.
  - S11 and S17 cover exactly the 2J rep streams.
  - S14 hashes root_F ‖ the roots in lexicographic table order ‖ points ‖ y.
  - U1–U3 compare against the session's draw.
  - As the spec already said, and as upstream does, keys of other tables in `root_b` and `publics` are ignored.
- **Verification.** Each table's two proofs (`<t>.rep<r>.bin`) are verified against that table's statement, domain and
  `root_B`. S16 and S18 apply per table.

## Why N4 holds

The record carries no table headers. Lean builds each table's statement itself, from the population file and part j of
the record's `unit_draw`. The draw is bound because Σ_j covers table j's public digest, whose header holds part j, and the
session Σ covers every Σ_j. So a record whose draw differs, or whose draw is one table's part, fails S2. The tests show
both.

## Questions I'd like you to check

1. Is the draw's binding enough? The parts, together with the verifier's J, determine the session's draw.
2. Is ignoring other tables' `root_b` and `publics` keys acceptable? It follows the spec and upstream's `from_record`. The
   live server refuses such a `Commit`.
3. Deliberately out of scope:
   - **the barrier** (every proof after the last coin): it is a zero-knowledge property, and the record keeps no order
     across streams;
   - **M0's coin-seed replay:** Lean doesn't do it at J = 1 either;
   - **`--zk` with several tables:** Lean has no M1 verifier.

   Does any of these belong in the verifier for soundness?
4. The tables' witnesses may be correlated: two tables can read the same row. Does the soundness argument need anything
   from the verifier beyond "each table's proof verifies against its own statement"? The union bound over tables sits in
   the soundness lane's `DESIGN.md`.

## Evidence

- **Live sessions.** I recorded #306's `serve`/`prove --session-tables J` at `9dfc971e` locally on the CPU: RoPE d64, 8
  instances. The sessions are J = 2, J = 2 with `--draw subset:4` (two), and J = 4. #306's server accepted all four, and
  so does Lean. The fixture is `art:425f6860`.
  - Lean's `Hello`, session Σ, per-table identities, domains and S14 equal the records' byte for byte.
- **`test_lean_session_tables.py`: 11 passed, plus 1 opt-in (`FLOCK_VERIFIER_SLOW=1`, which passes).** Lean refuses:
  - a J = 4 record read as J = 2 (S2);
  - a changed draw (S2);
  - table 0's part as the draw (S2);
  - a Bernoulli draw, an odd count, or another population (setup);
  - a missing table root (S5);
  - a short `y` (S10);
  - swapped tables' proofs: at S17, and with the digests swapped too, at replay (R2);
  - J > 1 on a statement without tables, and J = 65.
- **J = 1 is unchanged.** `ci.py --sets 15` (RoPE, `967b8d06`, with the draw cases) agrees 22/22 with upstream, and
  `test_lean_verifier.py` passes.
- **`audit.py` on the executable package: PASS**, 3,497 declarations and 13 pins, all unchanged.
- **One change beyond N4:** `verify` sets each statement up when a session first needs it, and caches it per draw. A
  drawn session no longer also sets up the population's statement. Verdicts are the same.
