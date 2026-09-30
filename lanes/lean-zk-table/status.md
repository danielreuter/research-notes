---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

# lean-zk-table: status

**Lane:** `lean-zk-table` (agent bc-7bf99d94-2cfe-5639-8b30-4de8d243b379). **Branch:** `cursor/lean-zk-table-b379`, from #245's
head `21b0edb0` (the ZK stack #227 → #239 → #245). **Builds:** vy-nebius-1, my own tree
`/workspace/research/trees/lean-zk-table` (dependencies copied, not shared), CPUs 0–31.

## Plan (07:50Z)

Files in `soundness/FlockSoundness/ZK/`:
- `Dist.lean`: equal distributions over uniform randomness (`SameDist`), post-processing, constant fibers.
- `Table.lean`: one masked table at fixed verifier coins. The reference prover (masked ring switch, level-0 padding and
  extra lanes, pads on every exposed value, the inner proof; hm96 leaves opened or ideal), its view, and `S_shvzk` (§3.2).
  The clear (upstream) values are parameters: the masking is concrete, the ZK theorem holds for any upstream.
- `SHVZK.lean`: Lemma A's instance (the translation of `u`, `R`, `h`, `μ`, through `card_fiber_eq_of_triShift`), Lemma B's
  rows in `card_seq_masked`'s form, and `table_shvzk`.
- `Complete.lean`: completeness of what masking adds: the inner proof's check, and the padded level 0 read through
  `Model.padColumn` equals the clear encoding of `y₁'` (§4.3's identity (★)).

## Log
- 07:29Z started; 07:46Z tree on vy-nebius-1, soundness build running.
