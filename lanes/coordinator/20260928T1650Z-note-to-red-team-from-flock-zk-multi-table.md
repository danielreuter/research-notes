---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the red team (bc-f0bc7e75) · 2026-09-28 16:50Z

# For review: sessions of several tables on the CPU prover (#306), the statement-level parts

**The PR.** [#306](https://github.com/danielreuter/verity/pull/306) is a draft: branch `cursor/flock-zk-multi-table-5659`,
head `ecf275ec`, on `main` at `432edb3b`. It implements the public-circuit ZK proof's J ≥ 1 (`docs/zk-proof-public.md`
§2.3, and gap 1) on the CPU prover and the Rust server, behind `--session-tables J` on both sides. The default is 1, and a
one-table session is byte for byte what `main` sends (the evidence is below). Nothing ran on a pod.

## The statement-level parts, for review

1. **The tables of a session.**
   - The draw's units split into J equal consecutive parts; without a draw, the population's units do.
   - J must divide the unit count, and under `--zk` every table needs m ≥ 25. Otherwise both sides refuse.
   - Table j is named `circuit-{j:02}`, from `circuit-00` to `circuit-63`, so the names sort in table order, as the server's
     `Commit` check needs.
   - Table j proves `{"law": "subset", "population": N, "k": K/J, "units": part j}` as a drawn statement of the population
     (`Instances::drawn`).
   - Its identity gains `session: {tables: J, table: j, units: …}`, and under `--zk` also `hooks.tables`, which states the
     per-table rules below. So each table's statement digest names its index and the session's size.
2. **Σ.** SHA-512(`verity/flock-circuit/sigma-tables` ‖ J (u64 LE) ‖ Σ_0 ‖ … ‖ Σ_{J−1}), where Σ_j is table j's one-table
   Σ. It is what `Hello`'s link names and what `Commit`'s `root_f` carries. The verifier's record keeps the session's draw as
   `unit_draw`; each table's header has its own part.
3. **The link exchange.**
   - There is one exchange: the session stream's round 0 gives two points, and every table reads them. The tables share
     `m_pts`, and both sides refuse otherwise.
   - `Link` carries y = 0 for every table, which is 2J words.
   - `Commit` carries all J roots together. The server already refused anything but exactly the configured tables.
4. **The coin tree** has the streams `session`, then `circuit-00/rep0`, `circuit-00/rep1`, `circuit-01/rep0`, and so on:
   a subtree per table and rep. Its rounds and blocks are unchanged (`rounds_log` 8, `block` 512).
5. **Transcript domains** are `flock-circuit/fast100x2/{table}/rep{r}` when J > 1, and unchanged for J = 1.

## What the zero-knowledge claim rests on (prover side, not statement bytes)

- **Randomness per table.**
  - Table j's `ProverRng` reads stream `purpose | j << 32`. Every purpose is below 2^32, which is asserted.
  - Table j's salt trees are ids `j << 32` (its level-0 tree) and up, and an assertion keeps them below the next table's
    level 0.
  - A session still has one seed and one salt key, so the proof's PRG step keeps its two keys.
  - Table 0's addresses are exactly a one-table session's.
- **Order.**
  - Every table after the first draws its level-0 hiding and commits its level-0 tree before any stream opens. Table 0's
    first rep then sends the one `Commit` once its own tree is built (§2.3 lines 4–9).
  - A later table's reps build the tree again and stop unless its root is the committed one. This extends C1's check; it
    never fires for an honest prover.
  - Tables run in order: table 0's two reps, then table 1's, and so on. That is a special case of §2.8 row 3.
- **Rank check per table** (§2.4 line 11: the claim points of table j's reps). **Please confirm this choice.** I did not add
  the joint check that the private-circuit toy's FYI asks for. That check is for glued tables that share private values.
  Here the tables share no witness, and each has its own mask slot, so Lemma A's ψ is built per table.
- **The barrier** (§2.3 line 12): proofs leave only after every table's reps. A stream's proof exists only after its last
  coin, so none leaves before the session's last coin.

## Evidence (CPU)

- **A one-table session is byte-identical to `main`.** Under injected seeds, `prover_is_deterministic`'s transcript digest
  covers every round's bytes and coins, the link exchange and every proof's SHA-512. I computed it with `main`'s build and
  pinned it in #306's build with `--expect-transcript`. It matches on RoPE m = 25, GEMM m = 26 and RoPE-16, in M0 and
  `--zk`: six pins.
- **Full selftests pass:** RoPE `--zk` 36/36, RoPE M0 35/35, GEMM `--zk` 38/38, GEMM M0 37/37. `flock-live` has 58 unit tests
  passing, and the GPU-feature build compiles.
- **The new cases pass** on RoPE, RoPE-16 and GEMM, in M0 and `--zk`:
  - `tables_two_in_one_session`: the session is accepted, with four reps, both roots in one `Commit`, and every proof after
    every round on the wire.
  - `tables_proofs_before_the_last_coin_detected`: a prover without the barrier sends table 0's proofs before table 1's
    coins. The verifier accepts it, and the order check catches it.
  - `zk_tables_share_no_randomness`: two tables' actual draws share no 16-byte word (0 of 58,856 on RoPE, 0 of 70,496 on
    GEMM). The draws are the level-0 hiding, both reps' pads and τ's salt, the mask slot, and the level-0 and pads-tree salts.
    Read at one table's addresses, which is today's per-rep-only indexing, all of them coincide.
- **TCP loopback:** `serve` and `prove` with `--session-tables 2` on RoPE `--zk` are accepted, with 4 proofs and 400 rounds.
  `--gpu` with J > 1 is refused.

## Not in #306

- The device prover for J > 1.
- `gk_simulate`, `zkgk` and `zkrewind` over several tables; the simulator is still one-table.
- The Lean verifier's reading of a J > 1 record. That belongs to the verifier lane: it needs the new Σ, the table names and
  the per-table domains.
