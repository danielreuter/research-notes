---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

# PR for `cursor/lean-zk-session-b379` (base `main`, after #519)

**Head:** `4088b8cb`. **Bundle:** `artifacts/cursor-lean-zk-session-b379-4088b8cb.bundle`, ref
`refs/heads/cursor/lean-zk-session-b379`; it needs `48b8452d`, which is on origin.

**Title:**

flock soundness (ZK): Lemmas A and B for a session of J masked tables, in Lean; stacked on #519

**Body:**

~~~markdown
Stacked on [#519](https://github.com/danielreuter/verity/pull/519) (`48b8452d`), which proves Lemmas A and B of the public-circuit zero-knowledge proof (`docs/zk-proof-public.md` §4.2, §4.3) for one masked table. The paper's lemmas are per session, with `J` tables. This PR proves the product over tables, which #519 listed as still on paper. Until #519 lands, the diff includes it.

This PR's own change:
- one new file, `backends/flock/verifier/lean/soundness/FlockSoundness/ZK/Session.lean`;
- one import in `FlockSoundness.lean`;
- five pins in `lean-audit.json`.

There are 0 `sorry`, and the axioms are `propext`, `Classical.choice` and `Quot.sound` only. No new assumption.

## Why a product suffices

- **The tables' randomness is disjoint.** Table `j` reads its own ChaCha20 stream, `purpose | j << 32`, and its own salt trees. After the PRG step, which is the one `J = 1` already takes, these are independent uniform draws (§2.2).
- **No claim or message reads two tables' witnesses or masks.** So at fixed coins the session's view is the tuple of the tables' views, each a function of its own table's randomness. The tables' witnesses may overlap; they are fixed.
- **The link exchange carries only public values.** It is the one place the tables meet:
  - the link points are the verifier's coins;
  - `Link(0)` is the constant 0 for every table;
  - each table's region claims at the shared points send their public values (H_reg).

  The session's other framing (`Register`, `Hello`, the one `Commit` with every table's cap) is a public function of the statement, the coins and the tables' views.

## The pins

| Theorem | Says |
|---|---|
| `SameDist.pi` | For independent components, equal distributions per component give equal distributions of the tuples. |
| `prCoin_pi_close` | For independent components, closeness adds up: if every event on component `j` has probability under `f j` at most its probability under `g j` plus `ε j`, then every event on the tuple has probability under the `f`s at most its probability under the `g`s plus `Σ_j ε j`. The proof swaps one component at a time, with the others part of the experiment. |
| `Session.session_shvzk` | Lemma B in world `W₁` for a session: the session's view and the tuple of `S_shvzk` outputs have the same distribution. It takes `table_shvzk`'s hypotheses for every table. |
| `Session.session_prefinal_indep` | Lemma A at a non-degenerate coin vector, for a session. It takes `table_prefinal_indep`'s hypotheses for every table. |
| `Session.session_shvzk_hm96` | Lemma B with real hm96 leaves for a session: every event on the session's view is within `Σ_j 2·|Hid_j|·δ₁`, in both directions. That is at most the paper's `2·δ₁·N_hid`, with `N_hid` summed over the session's tables. It takes `table_shvzk_hm96`'s hypotheses for every table, and one `δ₁` (one pinned hm96 key per session). |

## How to cite it

As for #519:
- cite Lemma B under the clear protocol's completeness (`InnerHolds`);
- cite `δ₁ = 2^-193` only with the pinned key's caveat (`hash-derived-key`).

## Still on paper

- Lemma A's refusal cases, with the schedule; T5 needs them for Lemma C.
- The Goldreich–Kahan hybrids.
- T6's extraction.
- T7's generating function.
- The clear protocol's completeness.

## Checks

- **Audit:** `audit.py --build --update` records exactly the five new pins and three new definitions (`Session.view`, `sim`, `preView`), and moves no existing record. Its review text is `art:e2d3a4050d0d`.
- **Recorded audit:** `r20260930-142548-e225` at `4088b8cb`, compare mode with kernel replay, passes: 12,129 declarations in 181 modules, 192 pins, standard axioms only. It ran on vy-nebius-1, CPUs 0–31, and is preserved and labelled `ov.ws=security`.
- **Tests:** `pytest tests/test_lean_packages.py tests/test_repository.py`: 18 passed.
- **Records:** `SameDist.pi` `7b540101`, `prCoin_pi_close` `7709325b`, `session_shvzk` `5e83d86b`, `session_prefinal_indep` `c357e92d`, `session_shvzk_hm96` `d48e109c`.

## Review

- **Statements:** the red team (red-team-flock-3, bc-f0bc7e75) approved all five at `d6a03d50`, before the proofs (`lanes/lean-zk-table/20260930T1405Z-reply-from-red-team-flock-3-session-statements.md`).
- **Changes since approval:** only the two it pre-approved:
  - `omit [Fintype K] [DecidableEq K]` on `session_prefinal_indep`, which only generalizes it;
  - the docstring note on the link exchange.
- **Grant:** both roles, on this PR's head, after the recorded audit.
~~~
