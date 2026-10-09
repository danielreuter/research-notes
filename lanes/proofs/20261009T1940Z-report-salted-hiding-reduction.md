---
id: proofs/20261009T1940Z-report-salted-hiding-reduction
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-0e16e57e-9802-53aa-81a3-ac82cc7f2261
---


# Salted SHA-512's hiding: premises, A3, and what remains (Daniel's 4(b), 4(c))

rec-thm, 9 Oct. Branch `cursor/salted-hiding-reduction-95d4` off `main` 1d9cfaff1 (worktree `/tmp/wt-salted-2261`):
92dd600cb (the Lean), 3a5ee3811 and 0a493f155 (docstrings only), 61f479efd (the same docstring rewrapped, identical
up to line breaks). Build: `r20261009-174634-cf8b` (vy-nebius-1, at 92dd600cb) PASS; `r20261009-181827-0b24` at
0a493f155 PASS.

## Answer in short

No premise in `Security/` asks a computational property of SHA-512 for hiding, so there is no reduction to write: every
hiding step is statistical. hm96's leaf hiding (`Hm96Hiding`, T1) is the statistical distance of `(M·y, H(sp‖y))` from
`(U, H(sp‖y))` for a uniform salt `y`, and it is already proved at that distance with no premise
(`CROnly.hm96Hiding_gap`); the leftover hash lemma behind its size (`CROnly.sum_hidingGap_le`) reads of `H(sp‖·)` only
that it takes at most `2^512` values. The PRG premise on the salts was never a `Prop`: it was the models' uniform salt
draw plus the prose that the salts were a ChaCha20 stream. This branch takes every hiding theorem stated at uniform salts
to salts read from the operating system's bytes under A3 (`UniformRandomBytes`), which removes that step. The one named
hiding premise left is `hash-derived-key`, which is not a hardness assumption and admits no reduction (below); a bound
stated at the gap needs no premise at all, and the branch proves those forms.

## Inventory

### Named premises (`FlockSoundness.Assumptions`, `Security/Proofs/Flock/Soundness/Assumptions.lean`)

| Premise | What it says | Kind |
|---|---|---|
| `Hm96Hiding My c δ₁` (T1) | `(My y, c y)` within `δ₁` of `(U, c y)`, `y` uniform | statistical; proved at `δ₁ = hidingGap My c` (`CROnly.hm96Hiding_gap`) |
| `HashDerivedKey My c` = `Hm96Hiding My c 2^-193`; `Zk.HashDerivedKeyHm96` at hm96-sha512's `ZkView.My`, `ZkView.saltHash` | the pinned key `K*`'s gap is at most `2^-193` | claims id `hash-derived-key` (model `common-reference-string`); a fact about one constant |
| `UniformRandomBytes L t` (A3) | the byte source is independent uniform bytes | claims id `uniform/io-getrandombytes`; now also the salts' source |

Not hiding premises, listed so the inventory is closed: `SHA512CRStrict` / `SHA512CRExpected` (`cr/sha-512`: binding of
commitments and Merkle trees, never hiding); `KeyedStreamsUniform` (A4, `prf/sha-512`: the PoUW window draw's keyed
streams, not salts); `UniformSecret` (A5); `HmRowComputes`, `PadNonvanishing` (not cryptographic).

### Abstract hypotheses that are hiding statements

* `PrivateCircuit.Hides reg ε` (`Discharge/PrivateCircuit/Defs.lean`): the registration hides the program over the
  registrant's uniform salts. A hypothesis of `CircuitPrivate` and `CircuitIndist` (`PrivateCircuit/Statements.lean`);
  no guarantee in `lean-audit.json` takes it. On `main` nothing discharged it. (The session part of circuit privacy is
  already at the gap, `zkGap = ∑ⱼ 2·|Hidⱼ|·hidingGap(My, saltHash)`, with no hash premise.)

### The PRG premise on the salts (never a `Prop`)

Every ZK theorem draws salts uniformly from `ZkView.Salt` (1536 bits). The prose said the leaf salts were a ChaCha20
expansion of an OS key (`ZK/Session.lean` "the PRG step", the Soundness `README.md`, `DESIGN.md` §6); on `main` the prover's
`LeafSalts` is that expansion. Under 4(a) (bc-ad20837e, `cursor/flock-os-salts-95d4`) every leaf's 192 bytes come from
`getrandom`; Python registrants already use `os.urandom(SALT_BYTES)` (`verity_flock/circuit.py`), and the recursive
audit's firewall reads its salts from `os.urandom` (`verity_flock/rec_live.py`, `rand = os.urandom`).

### Users of `Hm96Hiding` (all generic in `δ₁`)

`ZK/Hiding.lean` (the leaf swaps), `ZK/RealLeaves.lean` (`ideal_leaves_swap_fintype`, `real_leaves_swap_fintype`,
`table_shvzk_hm96`), `ZK/Abort.lean`, `ZK/Session.lean`, `ZK/GK/Link.lean`, `ZK/AdaptivePrefinal.lean`,
`Discharge/ZkCoins/Leaf.lean` (`hiding_fun`), and on this branch `Recursive/Guarantees.lean` (`recursiveZK_le`). No
guarantee takes `Hm96Hiding` at a free `δ₁`: the guarantees instantiate it through `hash-derived-key`, and circuit
privacy's session bound (`PrivateCircuit/Privacy.lean`, not a guarantee) at the gap.

### Users of `hash-derived-key` (`Zk.HashDerivedKeyHm96`), and the guarantees that take it

Users: `Discharge/FailClosed/One.lean` (3 theorems), `FailClosed/Composed.lean`, `FailClosed/ZkHidden.lean`,
`Discharge/Composed/Headline.lean` (3), `Discharge/ZkEveryCoin/Headline.lean` (3), `Discharge/ZkHidden/View.lean` (4),
`ZeroKnowledgeHidden/Statement.lean` (`_hKey`), `Recursive/Statements.lean` (`RecursiveZK`), and on this branch
`Recursive/OsSalts.lean` (`recursiveZK_os`).

Guarantees (`Security/lean-audit.json`), all three frozen with the tag `hash`:

* `Flock.SecurityProofs.RecursiveZK` (frozen: hash, obligation, no-function);
* `Flock.SecurityProofs.ZeroKnowledgeHidden` (frozen: hash, scope; `_hKey`);
* `FlockSoundness.Discharge.FailClosed.flock_verify_sound` (frozen: hash, world-unlisted; its `ViewZ` conjunct).

`EndToEnd`, `EndToEndHidden`, `EndToEndRegistered` (and their `Drawn` forms) and `RecursiveSound` take A3 for the
verifier's unit draw (frozen `world-unlisted`), not for hiding; their `hash` tag is for the finders' collision bounds
(`TableCRZ`, `LinkCRZC`, the fork finders'), which is binding.

### Outside Lean

PoUW's hm96 trees (`verity/core/protocols/pouw/audit.py`): leaf `i`'s salt is `hm96_salt(salt_key, nonce, i)`, ChaCha20
blocks `3i … 3i+2` under a prover key `salt_key = os.urandom(32)` (`new_salt_key` in the vLLM integration). That is a
PRG step, but PoUW's Lean (`Properties/Proofs/Pouw/Commit.lean`) states only the commitment format and binding, no
hiding, so it is a statement nobody has written rather than a premise to remove. C-Flock's masks and Reed–Solomon
padding stay a ChaCha20 expansion (`ProverRng`) under 4(a); the ZK theorems draw them uniformly, which is the same
unstated PRG step.

## What's proved (on the branch)

`Security/Proofs/Flock/Soundness/Discharge/ZkView/OsSalts.lean` (new, namespace `FlockSoundness.Discharge.ZkView`):

* `saltOfBytes : (Fin 192 → Fin 256) → Salt` (bit `t` is bit `t mod 8` of byte `t / 8`), `saltOfBytes_injective`, and
  `saltEquiv : (Fin 192 → Fin 256) ≃ Salt`, `saltsEquiv n` for `n` salts: 192 OS bytes are exactly one salt.
* `saltBytes_saltOfBytes`, `leaf_os`: the executable's `Hm96.Default512.leaf x (streamOf b)` at the OS's bytes `b` is
  the model's `leafH (bitsOf x + My (saltOfBytes b), saltHash (saltOfBytes b))`.
* `prCoin_os`, `prCoin_os_prod`: under A3 an event of the decoded salts has its uniform-salt probability.
* `hm96Hiding_os`: `Hm96Hiding` at any `δ₁` holds of the OS's salts under A3; `hm96Sha512_os`: at
  `ofReal (hidingGap My saltHash)` with no premise but A3.
* `ideal_leaves_swap_os`: the ideal-leaf swap of `n` leaves at the OS's salts, within `n·δ₁`.
* `hides_os`: a `PrivateCircuit.Hides` statement over uniform salts transports to the OS's salts under A3.
* `hides_leaves`: a registration of hm96 leaves `H(x p i + My yᵢ, c yᵢ)` satisfies `PrivateCircuit.Hides` at
  `2·|ι|·δ₁` from `Hm96Hiding` alone. `hides_leaves_os`: at the OS's salts under A3, at
  `2·n·ofReal (hidingGap My saltHash)` with no other premise. This is the first discharge of `Hides` for hm96-leaf
  registrations on top of `main`.

`Security/Proofs/Flock/Recursive/Guarantees.lean` (edited): `recursiveZK_le`, `RecursiveZK` at any hm96 bound `δ`
(`+ εo + nh·δ`) from `Hm96Hiding`; `RecursiveZK` is now its instance at `2^-193`, so its statement is unchanged.

`Security/Proofs/Flock/Recursive/OsSalts.lean` (new, namespace `Flock.SecurityProofs`):

* `firewallLeaf_os`: the firewall's executable leaf at OS bytes `b` is `firewallLeaf msg (saltOfBytes b)`.
* `recursiveZK_gap`: `RecursiveZK` with no premise on the commitments, at `εo + nh·hidingGap(My, saltHash)`.
* `recursiveZK_os_le`, `recursiveZK_os`, `recursiveZK_os_gap`: the same with the firewall's salts decoded from `nh`
  streams of 192 bytes of a source meeting A3: at any `δ`, at `2^-193` under `hash-derived-key`, and at the gap with no
  premise but A3.

No new axiom, `sorry`, `native_decide` or kernel bypass; no guarantee's statement changed, so `lean-audit.json` and its
lock are untouched. `Recursive/Property.lean` and `Audit.lean` are untouched.

## Docstrings and premise list (4(c))

A3 now names the salts wherever the OS's bytes are used for them: `Assumptions.lean` (A3's title and a paragraph on the
salts; `Hm96Hiding` says it is statistical and needs no computational property of SHA-512; `HashDerivedKey` says it is
the common-reference-string step with no reduction; the module docstring), `ZK/Session.lean` (the PRG step now covers
only masks and padding), `Recursive/Statements.lean` (`firewallLeaf`, `RecursiveZK`; the id `uniform/os-random` there is
now `uniform/io-getrandombytes`), and in `Security/Proofs/Flock/Soundness/`: `ASSUMPTIONS.md` (A3's row and heading, a
"The salts" bullet, the A6 line, a paragraph on statistical hiding and `hash-derived-key`), `README.md` and `DESIGN.md`
§6 (ChaCha's caveat now covers masks and padding only). The roots `Proofs/Flock/Recursive.lean` and
`Proofs/Flock/Soundness.lean` import the two new modules.

## Build

* `r20261009-174634-cf8b`, vy-nebius-1, tree 92dd600cb (all the Lean), `lean_changed.py --records Security/Proofs`:
  `records rc=0`, `AUDIT … Security/Proofs: PASS`, 61783 declarations in 961 modules, axioms `propext`,
  `Classical.choice`, `Quot.sound` only, 0 escapes, build 1751 s. Both new modules and the edited one built with no
  warning (`Built Proofs.Flock.Soundness.Discharge.ZkView.OsSalts`, `Built Proofs.Flock.Recursive.Guarantees`,
  `Built Proofs.Flock.Recursive.OsSalts`). A `lean-fast/v1` result (no kernel replay), as records builds are.
* `r20261009-181827-0b24`, vy-nebius-1, tree 0a493f155 (the branch head; adds only docstrings to
  `Assumptions.lean`): `records rc=0`, `AUDIT … Security/Proofs: PASS`, the same 61783 declarations in 961 modules and
  the same three axioms, build 1932 s (queued for the slot 18:18–18:51Z). The head, 61f479efd, rewraps that docstring
  and is identical to 0a493f155 up to line breaks; it was not built again.

## Which premises are gone

* The PRG premise on the salts, for C-Flock's leaf salts, the firewall's commitments and hm96-leaf registrations: every
  hiding theorem now has an `_os` form that takes A3 instead. (It was never a `Prop`, so nothing is deleted from
  `Assumptions`; what goes is the step in the prose and the gap between the models' uniform draw and the code.)
* `PrivateCircuit.Hides` as an open hypothesis, for hm96-leaf registrations: `hides_leaves_os` proves it from A3.
* `hash-derived-key`, for any theorem stated at the gap: `recursiveZK_gap`, `recursiveZK_os_gap`, `hm96Sha512_os`,
  `hides_leaves_os` take no hash premise.

## Named properties that remain

* **A3 (`UniformRandomBytes`, `uniform/io-getrandombytes`)**: now the salts' source as well as the unit draw's. It is
  still `world-unlisted` in the audit (`shape.premises` is empty); listing it is a claims and process change, not mine.
* **`hash-derived-key` (`HashDerivedKey`, `Zk.HashDerivedKeyHm96`)**, wherever a bound is stated at the number
  `2^-193` rather than at the gap: the three frozen guarantees above. No reduction exists to write. `K*` is one public
  constant: there is no secret and no adversary, and "`K*` is a bad key" is a fact about a constant, not a set an
  algorithm is asked to find. hm96 §3 proves the average over keys is `2^-257` (`CROnly.hm96_sha512_sum`) and that at
  most `2^-64` of keys exceed `2^-193` (`hm96_sha512_bad_keys`); that `K*` is not one of them is the CRS step.
* **The masks' and padding's PRG step** (ChaCha20 `ProverRng`), outside 4(a): still no `Prop`, still in the prose.
* **No computational property of SHA-512 enters hiding anywhere.** `cr/sha-512` stays, for binding only.

## Recommendations (for the coordinator to take to Daniel)

1. Restate `RecursiveZK`, `ZeroKnowledgeHidden` and `flock_verify_sound`'s `ViewZ` at the gap, `hidingGap My saltHash`,
   as `recursiveZK_gap` does. That drops the `hash` freeze tag from all three, in line with the 2026-10-08 ruling ("a
   guarantee never assumes a hash or a signature… no advantage bounds"). It changes guarantee statements, so it is
   Daniel's call. For `RecursiveZK` the proof exists (`recursiveZK_gap`). For the other two it is the same mechanical
   step as `recursiveZK_le`, not done here: their `hKey` reaches only `table_shvzk_hm96`, which is generic in `δ₁`
   (`ZkHidden/View.lean`, `FailClosed/One.lean`), so each `hKey` binder becomes `hm96Hiding_gap My saltHash`.
2. Or draw the hm96 key per session from the OS (A3). That removes `hash-derived-key` outright, at the averaged bound
   `2^-257` (`CROnly.hm96_sha512_sum`), as `ZkCoins.CommittedLeHm96` already does for committed coins. It is a format
   change (the key moves into the session).
3. Widen the claims entry `Instance("io-getrandombytes", "IO.getRandomBytes")` to say it also covers `getrandom` and
   `os.urandom` for salts.
4. Optionally make `RecursiveZK` itself take the OS's salts (`recursiveZK_os`); that also changes a guarantee's
   statement.
5. Masks and padding: read them from the OS too, or name the PRG step as a `Prop` (a ChaCha20 PRG assumption with an
   `η`), so it stops living in prose.
6. PoUW's hm96 salts: if PoUW is to claim hiding, its `hm96_salt` ChaCha20 expansion needs either OS salts or a named
   PRG premise; today it has neither a statement nor a premise.
