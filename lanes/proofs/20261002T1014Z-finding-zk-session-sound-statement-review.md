---
id: proofs/20261002T1014Z-finding-zk-session-sound-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: open
repo: verity
origin: proofs bc-8416bc72
---

# `--zk` session soundness (`cursor/zk-session-sound-95d4` @ `7e1ed4faf`): statement review APPROVE

Reviewer @proofs read both `audit.py --update` outputs of FlockSoundness (`internal/proofs/e2e/zk-session-sound.md`,
"Audit --update, v1 (0bf5dd00f)" and "v2 (7e1ed4faf)"). Every record is new against main: 23 pins, all in
`FlockSoundness.Discharge.ZkSession`, 237 in the package. No main pin and no main definition changed; the main
definitions newly read (`opStep`, `opResult`, `Accounting.Level.pad*`, `Game.value`, …) are read as they are. v1 → v2
moved only branch-new records (the tables now run `repMaskedZK`; `repPadZK`/`repPadZK_couple` gone).

What the pinned statements say, and that it matches the worker's report:
- `inner_sound`: at fixed committed words `Ch, Cμ` and fixed rows, if no pads message `δ`-close to `Ch` in
  `RS[F, dom, s + nP]` makes every row vanish with `h_ab = h_fa·h_fb` (`InnerGood`), `innerGame` (ε, ρσ, γ over
  `nA + 3`, τ, β, y, `q` queries at `pos`) accepts with value ≤ `εInner = (N + 3)/|F| + (1 − δ)^q`, for `δ` ≤ the unique-
  decoding radius and `hpos` (positions at most uniform).
- `zk_compose`: `repZK` = pads commitment received, then the phase, then `innerGame` on the phase's rows. If at every
  `h` with the triple the phase's "verdict true ∧ all rows vanish at h" has value ≤ ε, the rep's value ≤ ε + εInner.
- Couplings (`zerocheckZK_couple`, `lincheckZK_couple`, `restZK_couple`, `repMaskedZK_couple`): "masked value at `h` ≤
  clear value" against `Model.zerocheck`/`lincheck`/`opening`/`repPad`. `restZK` receives `fc ← recv F` after level 0
  and before the inner proof, so the rows' constants are fixed before γ.
- `table_sound_pad_zk` / `tableAfterZK_sound`: accept ∧ ¬`CommittedPad` ≤ `padLinkError + (padRepError + εInner)²`.
- `sessionZK_sound(_any)`: `sessionZK` (all level-0 oracles sent, one link-point draw, every table's reps) per table ≤
  `bound`, and over all tables ≤ the sum.
- `zk_knowledgeSound`: `analysisZK` is `KnowledgeSound` at `ksAvgZK` (the largest table bound after each draw, averaged),
  given `LoweringSoundZK`; `zk_flock_count` discharges that from `UnitPlace` (`decodeOfPlace`).
- `zk_flock_count_execOS(_m1)`: `Pr[accept ∧ K ≤ |wrong|] ≤ miss(K) + ksAvgZK + δ_link` at `Law.execOS` over
  `Draw.Law.stratified` under `UniformRandomBytes` (A3), `LinkSound δlink` a named hypothesis; with every table `M1`,
  `ksAvgZK` becomes `2^-203`.
- Numbers: `εInner_le_m1` (|F| = 2^128, q = 168, N + 3 ≤ 2^13, δ ≥ 7/16 ⇒ ≤ 2^-114: (N+3)/2^128 ≤ 2^-115 and
  (9/16)^168 ≈ 2^-139), `relUDR_ge_m1` (8L ≤ N ⇒ UDR ≥ 7/16), `posLo_uniform` (`lo mod 2^b`), `TabZK.bound_le_m1`.
- `coin_fresh*`: per round, from `Hm96Hiding` taken as a hypothesis.

`TabZK` bundles `hpos`, `hL`, `hδ` and the schedule shape as fields, so every instance proves them; `M1` adds δ ≥ 7/16,
which with `hδ` needs rate ≤ 1/8 (`relUDR_ge_m1`). Non-vacuous as stated.

Limits a citation must carry (none blocks the grant; all are in the report's "Open guarantees"):
1. **The live verifier does not run this protocol yet**: it never absorbs `final_c'` (zk_veil.rs:1128), so a prover
   re-solves it after γ. The Lean protocol fixes it before γ. These theorems describe the live `--zk` verifier only
   after #793's fix (@old-circuits-and-proofs' ruling, Slack `1790935865.805159`); until then nothing calls `--zk` sound.
2. Interactive-oracle layer: every oracle is a message. The compiled `--zk` layer (ε_ks from caps, δ_link from
   `ecr/sha-512`, δ_tree) is open, so δ_link stays a hypothesis.
3. The coin step is proved per round and not composed: `Game` strategies see every coin.
4. No `--zk` executable refinement yet (`execAccept` for the `--zk` path).
5. `M1` covers m = 25, 26, 27 only.

Red-team targets: that the live inner proof's layout meets 8(np + nP) ≤ N and N + 3 ≤ 2^13 at M1; that `restZK`'s seven
rows are the live verifier's rows (zk_veil.rs, flock-circuit.rs `zk_constraints`) after the fix; and that `innerGame`'s
γ count (`nA + 3`) matches `cons.len()`.

Grant: `pr:812@7e1ed4faf70a702371f82c81666508d45697b9d8 grant statement-reviewer` (PR #812).
