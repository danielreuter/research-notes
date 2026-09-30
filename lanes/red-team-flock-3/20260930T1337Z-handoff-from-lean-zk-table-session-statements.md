lane: red-team-flock-3 · kind: handoff · from: lean-zk-table (bc-7bf99d94) · to: red team (bc-f0bc7e75), as statement
reviewer; cc the research coordinator (bc-8ece7cde) · created: 2026-09-30T13:37Z · repo: danielreuter/verity · about: the
next ZK step after #519, the product over a session's `J` tables; **statement review before the proofs**, please

# Statements for review: Lemma A and Lemma B for a session of `J` tables (`ZK/Session.lean`, `d6a03d50`)

- **Where:** a new branch `cursor/lean-zk-session-b379` off #519's head `48b8452d`, one new file,
  `backends/flock/verifier/lean/soundness/FlockSoundness/ZK/Session.lean`.
- **The commit:** `d6a03d50`. It is in the Project store's `artifacts/cursor-lean-zk-session-b379-d6a03d50.bundle`
  until the root pushes it. The bundle needs `48b8452d`, which is on origin.
- **The proofs are `sorry` stubs.** I'll write them once you agree the statements; nothing is pinned yet.

**Why this step.** zk-public's list of what stays on paper after #519 has "the product over a session's `J` tables".
#519's Lemmas A and B are per table, and the paper's are per session. The product rests on two facts, both in the
file's docstring:
- the tables' randomness is disjoint (§2.2: `purpose | j << 32` streams and per-table salt trees, independent after the
  PRG step);
- no claim or message reads two tables' witnesses or masks.

So at fixed coins the session's view is the tuple of per-table views, each on its own table's randomness. The tables'
witnesses may overlap; they are fixed.

**The statements:**

| Name | Says |
|---|---|
| `SameDist.pi` | For independent components, equal distributions per component give equal distributions of the tuples. |
| `prCoin_pi_close` | For independent components: if every event on component `j` has probability under `f j` at most its probability under `g j` plus `ε j`, then every event on the tuple has probability under the `f`s at most its probability under the `g`s plus `Σ_j ε j`. |
| `Session.session_shvzk` | Lemma B in `W₁` for the session: `SameDist (view T w) (sim T w0)`. It assumes each table's `table_shvzk` hypotheses (`Rank`, `PadOnto`, `W^r` bijective, `PadsOnto`, `β ≠ 0`, H_reg, `InnerHolds`). |
| `Session.session_prefinal_indep` | Lemma A at a non-degenerate coin vector, for the session. It assumes each table's `Rank`, `W^r` bijective, `β ≠ 0`, and H_reg for both witness tuples. |
| `Session.session_shvzk_hm96` | Lemma B with real leaves: every event on the session's view is within `Σ_j 2·|Hid_j|·δ₁`, in both directions. It assumes each table's `Hm96Hiding` with one `δ₁`, plus the hypotheses above. |

Here `view T w ω = fun j => (T j).view (w j) (ω j)`, and `sim` and `preView` likewise. Each table is a `Table` at the
session's fixed coins, so the verifier's shared messages (the link points, the coin commitment) are in each table's
parameters.

**Where to push:**
1. **Independence.** Is modelling the session's randomness as `∀ j, (T j).Rand`, independent across tables, faithful to
   §2.2 after the PRG step?
2. **The leaves.** Can `hT1` hold per table with one `δ₁` for the whole session (one pinned hm96 key), and is
   `Σ_j 2·|Hid_j|·δ₁` the right sum?
3. **What it leaves out.** Is anything shared across tables missing? The level-0 commitment is one `Commit` with every
   table's cap. In the model, each cap is a function of that table's leaves, so the tuple carries all of them.

Please answer in `lanes/lean-zk-table/`.
