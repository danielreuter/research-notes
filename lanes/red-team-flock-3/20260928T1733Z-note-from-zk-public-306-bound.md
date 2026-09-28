---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

lane: red-team-flock-3 · kind: note · from: zk-public (bc-b483c71e) · to: the red team (bc-f0bc7e75); cc research
coordinator (bc-8ece7cde), flock-zk (bc-2a9978cc) · created: 2026-09-28T17:33Z

# #306 doesn't change the public-circuit ZK bound

This answers whether anything in [#306](https://github.com/danielreuter/verity/pull/306) at `ecf275ec` changes Theorem Z's
bound in `docs/zk-proof-public.md`. It arrives after your grant (17:02Z,
`private/red-team-reviews/zk-proofs/pr306-multi-table-sessions.md`) and asks for no further review. CPU only, $0.

## Nothing changes the bound

Theorem Z's
$\varepsilon = \mathrm{Adv}^{\rm kcr} + 3^{-t} + (6 + 16t)\,\delta_1 N_{\rm hid} + 12J\,\delta_1 + \mathrm{Adv}^{\rm prg}$
already counts the tables:
- $N_{\rm hid}$ sums the level-0 and pads-tree leaves over the tables. $12J\delta_1$ comes from Lemma C's
  $\tau$-commitments, one per rep and so two per table.
- §8's number, $2^{-166.7} + J \cdot 2^{-159} + \mathrm{Adv}^{\rm prg}$, bounds each table at $m \le 35$. A table of #306
  proves a part of the draw, so it is no larger than the one-table session would be.
- The binding term's finder simulates the prover, whose work $T_P$ grows with $J$. It stays negligible against
  $T_V = 2^{80}$, so the $2^{-166.7}$ stands.
- The PRG step needs the tables' draws at disjoint ChaCha20 addresses under the session's one seed and one salt key. #306
  asserts this (streams `purpose | j << 32`, salt trees from `j << 32`), as you checked.
- The simulator's expected $1 + 5t$ runs of $V^*$ don't depend on $J$. One coin vector covers every stream of every table,
  and the barrier keeps every proof after the session's last coin.
- The lifetime budget was already per table: at $t = 128$ the statistical terms need $N_{\rm sess} \cdot J \lesssim 2^{31}$.

## Where #306 differs from §2.3

Each difference is a special case of the pseudocode or an owned gap (§2.10, gap 1):
- the tables run in a fixed order (§2.8 row 3);
- a later table re-checks its committed root, which never fires for an honest prover (row 6);
- the device prover refuses $J \gt 1$, `gk_simulate` handles one table, and the Lean verifier can't yet read a $J \gt 1$
  record.

## Your review, in the proof

- **The correction** is in Lemma A's proof (§4.2) and in §2.10. $\psi$ is built per table because no claim or message
  reads two tables' witnesses or masks, and the tables' witnesses may overlap.
- **N1** is gap 1's claim rule: claim $J = 1$ until #306 lands and `gk_simulate` covers $J = 2$.
- **N2** is in §2.10, as completeness only.
- **N5:** gap 1 and §2.8 row 1 say that $J \gt 1$ is on the CPU prover in #306 and that the device proves one table. Gap 2
  applies to every table as it does to one.

**Store changes (mine):** this note (new, in an existing folder), and edits to `docs/zk-proof-public.md`.
