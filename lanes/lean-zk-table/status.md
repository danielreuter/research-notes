---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

# lean-zk-table: status

**Lane:** `lean-zk-table` (agent bc-7bf99d94-2cfe-5639-8b30-4de8d243b379). **PR:** [#519](https://github.com/danielreuter/verity/pull/519),
branch `cursor/lean-zk-table-b379`, stacked on #245 `21b0edb0` with `main` `cc0f4688` merged. **Builds:** vy-nebius-1, own tree
`/workspace/research/trees/lean-zk-table` (dependencies copied, not shared), CPUs 0–31. No new spend.

## Results (08:55Z)

All proved, 0 `sorry`, axioms `propext`, `Classical.choice`, `Quot.sound` only (checked with `#print axioms` on the node).

| Theorem | What it says | Assumptions |
|---|---|---|
| `FlockSoundness.ZK.Table.table_shvzk` | Lemma B in world `W₁`: the reference prover's view (pre-final and final messages, hm96 leaves opened or ideal) and `S_shvzk(x, e)` are equally distributed | non-degenerate `e` (`Rank`, `W^r` bijective, `β ≠ 0`); T4 (`PadOnto`, `PadsOnto`); H_reg; `InnerHolds` (row (xi)) |
| `…Table.table_prefinal_translate`, `…table_prefinal_indep` | Lemma A in `W₀`: a translation of `u`, `R`, `h`, `μ` (each reading earlier blocks) maps one witness's pre-final view to another's; equal distributions via `card_fiber_eq_of_triShift` | `Rank`, `W^r` bijective, `β ≠ 0`, H_reg for both |
| `…Table.star` | (★): extra-lane entries are determined by the other entries, `y₁'`, `ȳ` | none |
| `FlockSoundness.ZK.padColumn_honest` | completeness vs `Model.padColumn`: the honest padded table's column is the codeword of `y₁'` | char 2 |
| `…Table.inner_complete` | the masked verifier's inner check passes on the reference prover | `InnerHolds` |
| `FlockSoundness.ZK.padOnto_M1` | row (ii) for M1's code | **`PadNonvanishing`** (`X_L + κ ≠ 0`), `A.Correct` |
| `FlockSoundness.ZK.ideal_leaf_swap` | T1: one hm96 leaf → ideal changes any event's probability by ≤ `δ₁` | **`Hm96Hiding`** (HDK) |

Named assumptions added to `FlockSoundness.Assumptions`: `Hm96Hiding`, `PadNonvanishing`; `upstream` watch entries
`hm96-hiding`, `pad-nonvanishing` (0 hits at the pin).

**On paper still:** the `N_hid`-leaf hybrid lifting `W₁` to real leaves; T6's extraction; T7's generating function; the
Goldreich–Kahan hybrids; the clear protocol's completeness (zerocheck, lincheck, ring switch, Ligerito on `y₁'`).

## Log
- 07:29Z started; 07:46Z tree on vy-nebius-1.
- 08:12Z `table_shvzk` proved; 08:25Z Lemma A proved; 08:40Z completeness, T1, assumptions; `main` merged in.
- 08:44Z asked zk-public for wording (`lanes/zk-public/20260930T0844Z-handoff-from-lean-zk-table.md`).
- 08:55Z PR #519 (draft); `audit.py --update` running.
