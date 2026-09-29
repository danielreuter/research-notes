---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: report · 2026-09-28 20:52Z

# #306 after the red team's grant: N2 and N3 done, the simulator at J = 2 (N1)

The red team granted [#306](https://github.com/danielreuter/verity/pull/306) at `ecf275ec`
(`private/red-team-reviews/zk-proofs/pr306-multi-table-sessions.md`) with five notes and no conditions. On the same branch:
- `1e80ea21` does N2 and N3;
- `8e5aa1ca` does N1, the simulator;
- `9dfc971e` updates `PROTOCOL.md`.

N4 is already how the code reads the law. N5 belongs to the public-proof lane. Everything ran on CPU on this VM; no pod.
Evidence is in `private/flock-zk-multi-table-evidence/`.

## N2: the rank check's sizing per table

- **The refusal.** `zk_shape_ok` refuses a `--zk` statement, or a table of a split session, that has fewer than
  128·4 + 64 mask words. The rank check at a table's last opening covers four claim points (ab and c, both reps), and a
  table with fewer than 512 words can never pass it.
  - Both sides check this when the statement is built, before `Hello`: `main` checks the population, and `session_tables`
    checks every table and every drawn one-table statement.
  - The 64 extra words keep a refused coin rare: for uniformly random rows, rank falls short with probability below
    2^(512 − N).
- **The sizes, measured with loopback `--zk` sessions** (the prover's `ZKRANK` lines, every check of every table):

  | set (units) | J | m per table | smallest table's mask words | need at 4 points | smallest rank at 4 points |
  |---|---|---|---|---|---|
  | RoPE (4) | 1, 2, 4 | 25 | 1024 | 512 | 512 |
  | GEMM (4) | 1, 2, 4 | 26 | 1024 | 512 | 512 |
  | RoPE-16 (16) | 1, 2, 4, 8 | 25 | 1024 | 512 | 512 |

- **Why the tables never shrink.** m ≥ 25 at these templates' `k_log` (22, and 23 for GEMM) already forces at least 8
  blocks, and each block has 2^(14−7) = 128 mask words. So splitting doesn't reduce a table's mask slot below 1024 words.
  The refusal matters for templates with a larger `k_log`, where m ≥ 25 allows fewer blocks.
- **A limit found on the way.** RoPE-16 at J = 16 (one unit per table) was killed for memory at about 10.8 GB resident,
  on this 15 GB VM. The prover holds every table's statement and witness at once, because the one `Commit` needs every root
  first. J = 8 runs.

## N3: Bernoulli draws, and draws the tables can't split

- **At configuration.** With `--session-tables` above 1, the server now refuses these at startup, before any session:
  - a Bernoulli law;
  - a subset law whose k the tables don't divide, or whose tables `--zk` can't prove. A subset law's table shapes depend
    on k alone, so the server probes them with a draw of the first k units.
  - a `--draw-file` it can't split.

  CLI check on RoPE-16, J = 2: `--draw bernoulli:1/2`, `--draw subset:3` and `--draw subset:40` are refused;
  `--draw subset:4` and no draw serve.
- **On both sides after `Register`,** as before, and the same rule: `session_tables` refuses a Bernoulli draw for J > 1.
  The selftest `tables_unsplittable_draw_refused` covers a Bernoulli draw, an odd count, and a subset draw of every unit
  (which splits).
- **A fix on the way.** `serve` used to build its server once per connection, so configuration errors surfaced only when
  a session arrived, and J > 1 without a draw rebuilt every table's statement per session. The configuration (`Serving`)
  is now checked and built once, when the server starts.

## N1: the simulator on sessions of two tables

- **The code.** `extracted`, `rewind`, `fresh_dummy` and `gk_simulate` take the session's tables. `zkrewind` and `zkgk`
  take `--session-tables J`.
  - A rewind simulates every stream and replays the session in the prover's order: the tables' streams one after
    another, the one `Commit` with every root inside table 0's rep 0, and every proof after the last round.
  - V*'s targeted round is table 0's rep 0's.
  - Proof and relation lines name their table.
  - `zk_rewind_stats.py` tests each table's proofs and relations as their own classes. It also fails a strategy in which
    table j has a value equal to table 0's, for the same view and rep, in every view (`across_tables`). A synthetic test
    shows that shared randomness fails it.
- **The run.** RoPE, J = 2 (two tables of m = 25), 40 real and 40 simulated views for each of the six strategies. It took
  125 min, and `zkgk` (40 attempts, `--reuse-dummy`) took 12 min.

  | V* | complete views, real / simulated | how views end (p) | extraction runs reaching the proofs | estimation runs | rewinds | simulator failures |
  |---|---|---|---|---|---|---|
  | honest | 40 / 40, all accepted | 1.0 | 40 of 40 | 160 | 40 | 0 |
  | abort | 14 / 18, all accepted | 0.70 | 18 of 40 | 181 | 64 | 0 |
  | adaptive-coins | 17 / 14, all accepted | 0.74 | 14 of 40 | 147 | 51 | 0 |
  | zero-beta | 0 / 0 (every view stops at table 0's β round) | identical | 0 of 40 | 0 | 0 | 0 |
  | cap-gated | 20 / 24, all accepted | 0.51 | 24 of 40 | 194 | 49 | 0 |
  | late-gated | 21 / 22, all accepted | 1.0 | 22 of 40 | 164 | 35 | 0 |

- **Nothing is shared across the tables.** `across_tables` is 0 for every class of every strategy with complete views.
  Each table's 11 proof classes and 2 relation classes are tested apart.
- **The statistics pass as a family.** Over 688 tests the smallest p-value is 3.2·10^-4, Bonferroni-adjusted 0.22.
  - Per test at α = 10^-3, one test missed: the real side's xor test on table 1's `inner_y`, in the abort strategy. It
    reads only the real views.
  - I registered a check in advance: rerun the abort strategy with 40 fresh views per kind, expecting p > 10^-3 for that
    class. The rerun gives 0.30, and all 136 of the abort strategy's tests pass.
- **The rewinds are independent trials:**
  - cap-gated: 22 of 40 real sessions complete and 21 of 40 fresh rewinds (p = 1.0). Rewinds on the reused dummy
    complete 1 time (p = 1.4·10^-7).
  - late-gated: 16 real and 24 fresh (p = 0.12). Rewinds on the reused dummy complete 40 times (p = 7.7·10^-10).
- **Timing.** A two-table real session takes about 3.7 s and a simulation about 17 s, against about 1.4 s and 3.6 s with
  one table. Harnesses now hand `session` the population's split (`Plan.split`), so repeated sessions don't rebuild every
  table's statement. `prove --session-tables J` does the same.

## N4 and N5

- **N4.** The Rust server and prover already take the session's law from `unit_draw`:
  - `config_of` for J > 1 records the session's draw;
  - `from_record`'s U1 check compares against that draw;
  - a table's header carries only its part.

  The Lean verifier's reading of a J > 1 record belongs to the verifier lane (bc-8e519ca0). It must re-derive the parts from
  `unit_draw`, as the red team says, and not trust a table's header.
- **N5.** The public-proof lane is updating gap 1 and §2.8 row 1.

## One-table sessions stay byte-identical, and the suites pass

- `prover_is_deterministic`'s transcript digests match `main`'s at every commit:
  - at `1e80ea21`: RoPE, GEMM and RoPE-16, M0 and `--zk`;
  - at `8e5aa1ca`: RoPE and GEMM, M0 and `--zk`.
- Full CPU selftests at `8e5aa1ca`: RoPE `--zk` 37/37 and M0 36/36; GEMM `--zk` 39/39 and M0 38/38.
- Python: the flock tests pass (264 passed, 64 skipped), and so does `tests/test_repository.py`. `flock-live` has 58 unit
  tests passing.

## Evidence (`private/flock-zk-multi-table-evidence/`)

- `zkrewind40-J2-9dfc971e.tsv.gz` and `zkgk40-J2-9dfc971e.tsv`: the run.
- `zk-rewind-stats-J2-9dfc971e.json`: its statistics.
- `zkrewind40-J2-abort-rerun-9dfc971e.tsv.gz` and `zk-rewind-stats-J2-abort-rerun-9dfc971e.json`: the abort rerun.
- `rank-check-sizes-per-J.tsv`: N2's table.
- `one-table-pins-ecf275ec.tsv`, `one-table-pins-1e80ea21.tsv` and `one-table-pins-9dfc971e.tsv`: the byte-identity
  digests. The last is from the build of `8e5aa1ca`, whose source `9dfc971e` shares.
- `selftest-{rope,gemm}-{zk,m0}-9dfc971e.tsv`: the suites.

The code at `9dfc971e` equals the tested build's source; that commit changes only `PROTOCOL.md`.
