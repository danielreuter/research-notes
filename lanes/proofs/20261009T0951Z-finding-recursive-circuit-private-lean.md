---
id: proofs/20261009T0951Z-finding-recursive-circuit-private-lean
campaign: recursive-private-circuits
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: cursor/rec-private-lean-35f2 @ 51e875f51 (off main 56e4e65e8, merged with cursor/rec-fork-2261 7b1b158cb); audits r20261009-074816-0acd, r20261009-085552-ed4d
---

# Recursive circuit privacy and the registered circuit description, in Lean (rec-private-lean)

For the proofs coordinator (bc-8416bc72), on the 06:00Z Oct 9 assignment. Times are UTC.

## Outcome

All five statements are proved on `cursor/rec-private-lean-35f2`, with no `sorry`, `axiom` or `native_decide`. Each
depends only on `propext`, `Classical.choice` and `Quot.sound` (`#print axioms` against a local build).

* Circuit privacy: `RecursiveCircuitPrivate`, `RecursiveCircuitIndist` and `RecursiveCircuitPrivateLeaves`.
* The registered circuit description: `RecursiveRanRegistered`, stated against fork-form `RecursiveSound`, and `RanRegisteredRun`,
  which restates `RanRegistered`'s `SHA512CRStrict` as a run-tied break.

For the executable's registration, `RecursiveRanRegistered`'s per-row binding (`_hbind`) is discharged too
(`regRowCommit_binding`, a lemma, not a listed guarantee): two openings of one registered port at one position to
different rows give a SHA-512 collision.

No new named premise was added. The only closed premise is `hash-derived-key` (`HashDerivedKeyHm96`, already listed).
On the soundness side, `VBridge` and A3 come in through `RecursiveSound`.

Still abstract, and where the remaining work is (details under "Hypotheses"):

* On the privacy side, `_hOuter`, the zero knowledge of V*'s outer sessions at every tape. `ZeroKnowledgeHidden` does
  not yet have that form.
* On the soundness side, `_hop` and `_hx`, which tie the rows a run reads to its inner statement. `_hop` holds at every
  accepted outcome, but the executable's link from a `--zk` session's committed values to the registrant's rows
  (`zk_session_regValsR`) holds only up to a probability. So `_hop` needs a probabilistic form or a restated `Row`
  before it can be discharged.

The required Lean audit passes on vy-nebius-1. Run `r20261009-074816-0acd`, on `425bbaea6`, passes both `security`
and `security_proofs`: only the standard axioms, the kernel's replay of all 959 modules, and 281 guarantees. Its
`--update` records are committed as the head. On that head (`51e875f51`), run `r20261009-085552-ed4d` passes the
same audit without `--update`, so the committed records are the build's.

* Branch: `cursor/rec-private-lean-35f2`, off origin/main `56e4e65e8`.
* Merged into it: `origin/cursor/rec-fork-2261`, first at `17a1def84` (fork-form `RecursiveSound`, stacked on #1593's
  compiled-Inner commits) and then at `7b1b158cb`, its current head. The two later commits change only proofs in
  `Finds.lean` and `RecursiveSound`'s record, not a statement.
* Head: `51e875f51`, pushed (the audited `425bbaea6` plus its records in `Security/lean-audit.json`).
* It does not land tonight. Main has since moved to `c6c268f72` and changed `Security/lean-audit.json` by about 435
  lines, so landing will need a merge there.

Files:

* `Security/Proofs/Flock/Recursive/Statements.lean`: the statements, beside `RecursiveZK`.
* `Security/Proofs/Flock/Recursive/Private.lean`: new, the proofs, and `regRowCommit` with its binding.
* `Security/Proofs/Flock/Recursive.lean`: imports `Private`.
* `Security/lean-audit.json`: the five entries, owner `@proofs`; their records come from the audit's `--update`.

## The statements as they read

All are `def G : Prop` in `Flock.Guarantees`, proved as `Flock.SecurityProofs.G : Flock.Guarantees.G`.

### The view, the real experiment and the simulator

The view is the auditor's whole view, `E : Rv × Ωa × (Fin nh → ByteArray) × V → Prop`:

* the registration's view `reg P r`;
* the auditor's tape `a`, which carries the inner coins, fixed before the first commitment as in `RecursiveZK`;
* the firewall's `nh` commitments, `firewallLeaf (msgs P w r a p i) (y i)`, one to every inner message and tree top;
* V*'s `--zk` sessions' view, `view P w r a h p y q`.

```lean
noncomputable def recRealPr … (reg : Prog → Rr → Rv) (nh : ℕ) (msgs : Prog → Wit → Rr → Ωa → Ωp → Fin nh → ByteArray)
    (view : Prog → Wit → Rr → Ωa → (Fin nh → ByteArray) → Ωp → (Fin nh → ZkView.Salt) → Ωo → V)
    (P : Prog) (w : Wit) (E : Rv × Ωa × (Fin nh → ByteArray) × V → Prop) : ℝ≥0∞ :=
  avg fun r : Rr => prCoin fun z : ((Ωa × Ωp) × (Fin nh → ZkView.Salt)) × Ωo =>
    E (reg P r, z.1.1.1, (fun i => firewallLeaf (msgs P w r z.1.1.1 z.1.1.2 i) (z.1.2 i)),
      view P w r z.1.1.1 (fun i => firewallLeaf (msgs P w r z.1.1.1 z.1.1.2 i) (z.1.2 i)) z.1.1.2 z.1.2 z.2)

noncomputable def recSimPr … (reg : Prog → Rr → Rv) (nh : ℕ) (sim : Out → Rv → Ωa → (Fin nh → ByteArray) → Ωs → V)
    (o : Out) (p₀ : Prog) (E : Rv × Ωa × (Fin nh → ByteArray) × V → Prop) : ℝ≥0∞ :=
  avg fun r : Rr => prCoin fun z : (Ωa × (Fin nh → ZkView.Bits × ZkView.Salt)) × Ωs =>
    E (reg p₀ r, z.1.1, (fun i => idealLeaf (z.1.2 i)), sim o (reg p₀ r) z.1.1 (fun i => idealLeaf (z.1.2 i)) z.2)
```

`firewallLeaf msg y = ZkView.leafH (bitsOf (SHA-512 msg) + My·y, saltHash y)` is the hm96-sha512 leaf.
`idealLeaf u = leafH (u.1, saltHash u.2)` reads no message.

**What the simulator reads.** It reads only the class and the owed outputs:

* a fixed circuit description `p₀` of the class, which it registers itself (`reg p₀ r` at a fresh `r`);
* the class's functions (`reg`, `nh`, `sim`);
* the owed outputs `o`;
* the auditor's tape `a`;
* the ideal commitments.

It never reads the circuit description `P`, the witness `w`, the developer's randomness `p`, the firewall's salts `y`, or the
registration's randomness of the real run.

### `RecursiveCircuitPrivate`

```lean
def RecursiveCircuitPrivate : Prop :=
  ∀ {Out Prog Wit Rr Rv Ωa Ωp Ωo Ωs V : Type} [Fintype Rr] [Nonempty Rr] [Fintype Ωa] [Nonempty Ωa] [Fintype Ωp]
    [Nonempty Ωp] [Fintype Ωo] [Nonempty Ωo] [Fintype Ωs] [Nonempty Ωs]
    (reg : Prog → Rr → Rv) {ε : ℝ≥0∞} (_hreg : PrivateCircuit.Hides reg ε)
    (honest : Out → Prog → Wit → Prop)
    (nh : ℕ) (msgs : Prog → Wit → Rr → Ωa → Ωp → Fin nh → ByteArray)
    (view : Prog → Wit → Rr → Ωa → (Fin nh → ByteArray) → Ωp → (Fin nh → ZkView.Salt) → Ωo → V)
    (sim : Out → Rv → Ωa → (Fin nh → ByteArray) → Ωs → V) {εo : ℝ≥0∞}
    (_hOuter : ∀ o P w, honest o P w → ∀ r a p (y : Fin nh → ZkView.Salt) (E : V → Prop),
      prCoin (fun q : Ωo => E (view P w r a (fun i => firewallLeaf (msgs P w r a p i) (y i)) p y q))
        ≤ prCoin (fun s : Ωs => E (sim o (reg P r) a (fun i => firewallLeaf (msgs P w r a p i) (y i)) s)) + εo)
    (_hKey : FlockSoundness.Assumptions.Zk.HashDerivedKeyHm96)
    (p₀ : Prog) (o : Out) (P : Prog) (w : Wit), honest o P w →
    ∀ E : Rv × Ωa × (Fin nh → ByteArray) × V → Prop,
      recRealPr reg nh msgs view P w E ≤ recSimPr reg nh sim o p₀ E + (ε + εo + nh * (2 : ℝ≥0∞) ^ (-193 : ℤ)) ∧
        recSimPr reg nh sim o p₀ E ≤ recRealPr reg nh msgs view P w E + (ε + εo + nh * (2 : ℝ≥0∞) ^ (-193 : ℤ))
```

The bound is ε plus `RecursiveZK`'s gap (`εo + nh·2^-193`), both ways.

The proof is `circuit_private_of_zk`'s argument with `RecursiveZK` as the step:

1. At each registration salt `r`, `RecursiveZK` moves the commitments and V*'s view to the ideal leaves and `sim`. For
   the other direction it is applied to the event's complement and flipped (`prCoin_flip`).
2. The simulated side reads `r` only through `reg P r`, so it is a test with values in `[0, 1]`.
3. `Hides.avg_le` moves `reg P r` to `reg p₀ r`.

### `RecursiveCircuitIndist` (the indistinguishability form; it came cheaply)

It has the same binders as `RecursiveCircuitPrivate`, then:

```lean
    (o : Out) (P P' : Prog) (w w' : Wit), honest o P w → honest o P' w' →
    ∀ E, recRealPr reg nh msgs view P w E ≤ recRealPr reg nh msgs view P' w' E + 2 * (ε + εo + nh * 2^-193)
```

The proof goes through the simulator at `p₀ := P`.

### `RecursiveCircuitPrivateLeaves` (the registration instantiated as hm96 leaves)

```lean
def regLeaves (rows : Prog → Fin nr → ByteArray) (pub : (Fin nr → ByteArray) → Rv) (P : Prog)
    (r : Fin nr → ZkView.Salt) : Rv := pub fun i => firewallLeaf (rows P i) (r i)
```

Row `i` of the circuit description is committed as the firewall commits a message, under its own salt. The auditor sees `pub` of the
leaves (their Merkle root and whatever else the record publishes of them). A `--zk --registered` session's registrant
opening is exactly such a (row, salt) (`ZkReg.regOpenZ`).

The statement is `RecursiveCircuitPrivate` with `reg := regLeaves rows pub`, and with `Rr := Fin nr → Salt` built in:

* `msgs` and `view` take the registration salts, so the inner messages and V*'s sessions may read them;
* `_hOuter` has `regLeaves rows pub P r` in place of `reg P r`;
* `Hides` is no longer a hypothesis;
* the bound is `2·nr·2^-193 + εo + nh·2^-193`, both ways.

The proof is `regLeaves_hides : Hides (regLeaves rows pub) (2·nr·2^-193)` under `hash-derived-key`: `ideal_leaves_swap`
from each circuit description to ideal leaves, then back on the complement.

### `RecursiveRanRegistered`, in fork form, binding the registration at each row

It is stated against **fork-form `RecursiveSound`**, from `cursor/rec-fork-2261` at `17a1def84` (rec-thm's rewrite,
stacked on #1593), not main's.

The binders are `RecursiveSound`'s fork-form binders verbatim (with no `t'`, `qF qS qW qR`, `q` or `_hCR`), then:

```lean
    {Root Pos Row Op : Type} (com : Pos → PrivateCircuit.Commit Root Row Op) (_hbind : ∀ i, (com i).Binding)
    (rt : Root) (p : Pos → Row) (op₀ : Pos → Op) (_hreg : ∀ i, (com i).Opens rt (p i) (op₀ i))
    (stmt : (Pos → Row) → L.Ω → I.Stmt)
    (reads : Reg × L.Ω × List (Cm × I.Coin) × (Reg₂ × VRec Vs Reg' dg N) → Pos → Prop)
    (row : Reg × L.Ω × List (Cm × I.Coin) × (Reg₂ × VRec Vs Reg' dg N) → Pos → Row)
    (op : Reg × L.Ω × List (Cm × I.Coin) × (Reg₂ × VRec Vs Reg' dg N) → Pos → Op)
    (_hop : ∀ o, AcceptsV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ i, reads o i → (com i).Opens rt (row o i) (op o i))
    (_hx : ∀ o, AcceptsV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ q : Pos → Row, (∀ i, reads o i → q i = row o i) →
      x o.1 o.2.1 = stmt q o.2.1),
    RoundFork zs dg N k Rw σ cmt ∨ SessionFork zs dg N k Rw M σ ∨
      (∃ o, FlockSoundness.Game.Outcome (recGame L Reg I Cm fun R ω t => outerV (zs R ω t) dg N) σ o ∧
        AcceptsV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
        ∃ i, reads o i ∧ row o i ≠ p i ∧ FlockSoundness.Binding.Collides ((com i).ext (op o i) (op₀ i))) ∨
      prob (fun o => AcceptsV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 ∧ ¬ I.holds (stmt p o.2.1))
          (recGame L Reg I Cm fun R ω t => outerV (zs R ω t) dg N) σ ≤
        expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
            (fun R₂ j τ => (zs σ.1 ω t R₂ j).boundCR dg N (Vs j).law.model k Rw M ρ τ) s) +
          (I.r : ℝ≥0∞) * expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
            (fun R₂ j τ => (zs σ.1 ω t R₂ j).slackCR dg N k Rw M ρ τ) s) + εin
```

The conclusion has the 4:30 PM ruling's fork shape, and its third disjunct is the 8:25 AM run-tied break. That
disjunct says: an outcome `σ` reaches has every session of V* accepting, having read at some position `i` a row other
than the registered `p i`, and its opening of the root at `i` and the developer's give two different strings SHA-512
maps to one digest (the Merkle binding's pair along the two openings' paths). No hypothesis is placed on a finder, and
the bound is `RecursiveSound`'s, unchanged.

**Why per row, and not one opening of the whole circuit description.** My first version took `RanRegistered`'s commitment
literally: one `Commit Root Prog Op`, with the run carrying an opening of `rt` to a whole circuit description `prog o`. That
`_hbind` cannot be discharged for the real registration. V*'s sessions open only the rows the drawn units read, and a
binding (two openings of different circuit descriptions collide) is false for partial openings that differ off their opened rows.
So the commitment is `RanRegistered`'s `Commit.Binding` at each row position. `_hx` says the inner statement depends
only on the rows the run read: it is the statement of every circuit description with those rows.

The proof takes `RecursiveSound`'s three cases. In the bound's case, either such an outcome is reached (the third
disjunct), or at every reached accepted outcome the registered circuit description has every row the run read, by the binding at
that row. Then `_hx` at `q := p` gives that the inner statement is `p`'s. `prob_mono_outcome` (new: an inclusion at
every outcome the strategy reaches) carries this through the probability.

### `regRowCommit_binding` (the per-row binding for the executable's registered rows)

```lean
noncomputable def regRowCommit {Val : Type} (enc : Val → List UInt8) (hinj : Function.Injective enc) (i : ℕ) :
    Commit Flock.Registered.Port Val (Flock.Registered.Port × Val × ByteArray × ByteArray) where
  Opens reg v op := op.1 = reg ∧ op.2.1 = v ∧
    Flock.Registered.opensLeaf reg ((ExplicitLeaf.hm96 enc hinj).leaf v op.2.2.1.data.toList).1 i op.2.2.2 = true
  ext op op' := if the two openings' hm96 leaves agree then hm96's pair of them else `openPair` along their paths

theorem regRowCommit_opens … : (regRowCommit enc hinj i).Opens reg v (reg, v, salt, path) ↔
    Flock.Registered.opens reg (Hm96.Default512.commitString (Sha512.hash ⟨(enc v).toArray⟩) salt) i path = true
theorem regRowCommit_binding … : (regRowCommit enc hinj i).Binding
```

The commitment at row position `i` is the registered port (root, domain, leaf count). An opening is (port, row, salt,
path), and it opens exactly when the executable verifier's registered-read check, `Flock.Registered.opens`, accepts the
row's commit string at `i` (`regRowCommit_opens`). So `RecursiveRanRegistered` instantiates with `Root := Port`,
`Pos := ℕ`, `com := regRowCommit enc hinj` and `_hbind := regRowCommit_binding enc hinj`.

The binding has two cases. Two openings to different rows either have one hm96 leaf, which makes hm96's two input
strings a SHA-512 collision (`ExplicitLeaf.hm96`'s `pair_spec`), or have different 64-byte leaves at one position of
one root, which `Flock.Registered.opensLeaf_binding` turns into a collision along the two paths. In both cases the
collision is the extractor's output on the run's own openings, so the third disjunct of `RecursiveRanRegistered` stays a
run-tied break.

### `RanRegisteredRun` (`RanRegistered`'s `SHA512CRStrict` restated as a run-tied break)

```lean
def RanRegisteredRun : Prop :=
  ∀ {Root P Op : Type} (com : PrivateCircuit.Commit Root P Op), com.Binding →
    ∀ (rt : Root) (p : P) (op₀ : Op), com.Opens rt p op₀ →
    ∀ {β : Type} (G : Game β) (σ : Strategy G) (acc Q : β → Prop) (prog : β → P) (op : β → Op),
      (∀ b, acc b → com.Opens rt (prog b) (op b)) →
    ∀ (B : ℝ≥0∞), prob (fun b => acc b ∧ Q b) G σ ≤ B →
      (∃ b, FlockSoundness.Game.Outcome G σ b ∧ acc b ∧ prog b ≠ p ∧
          FlockSoundness.Binding.Collides (com.ext (op b) op₀)) ∨
        prob (fun b => acc b ∧ (Q b ∨ prog b ≠ p)) G σ ≤ B
```

It can be restated. `RanRegistered`'s `SHA512CRStrict` finder plays the session once and outputs the extractor's pair,
so its run-tied break is an outcome of that one play whose pair collides. The restatement loses the `q²/2^513` term and
the cost hypothesis. `RanRegistered` itself is unchanged and is not a listed guarantee; `RanRegisteredRun` is listed.

## Hypotheses

### Named premises

These are listed assumptions, unchanged; none was added.

* `FlockSoundness.Assumptions.Zk.HashDerivedKeyHm96` (`hash-derived-key`), on the privacy side.
* `Flock.Assumptions.VBridge` and A3 (`UniformRandomBytes`), on the soundness side, through `RecursiveSound`.

### Discharged

* The firewall's commitment scheme is concrete (`firewallLeaf`, the executable's hm96-sha512 leaf, `ZkView.leafSplit`).
* For `RecursiveCircuitPrivateLeaves`, the registration's hiding (`regLeaves_hides`).
* `RecursiveSound` itself (rec-thm's proof), and `InnerSound` as `RecursiveSound` takes it.
* `RecursiveRanRegistered`'s `_hbind`, for the executable's registered rows (`regRowCommit_binding`).

### Still abstract

1. `_hOuter`, V*'s sessions' zero knowledge, is the main open piece.
   * It is needed at every honest witness, registration randomness, tape and firewall salts, with a simulator that reads
     the owed outputs, the registration's view, the tape and the commitments.
   * The candidate discharge is `ZeroKnowledgeHidden` (C-Flock `--zk`), but its form leaves gaps:
     * it is honest-verifier at fixed coin vectors (`CoinedSetup.Admits`), not against an auditor of arbitrary tape;
     * it holds on runs where the self-check doesn't stop, and the prover's refusal may depend on the witness;
     * it carries an `avoidsMask` hypothesis;
     * it is stated in the `ZkViewAtJ` form, which has to be put into this `prCoin` form over V*'s whole session row;
     * the registration `R₂` is inside V*'s view, and its own hiding must be counted. Today it is folded into `view`;
       if `R₂` is a leaf registration, it is another `ideal_leaves_swap`.
2. `honest o P w` is a parameter: that `P` computes the owed outputs `o` on `w`. Instantiating it means the universal
   unit's evaluation at the class.
3. `msgs`, `view` and `sim` are abstract functions with the right dependencies. The types do the work: `sim` cannot read
   `P`, `w`, `p` or `y`. Instantiating them means the firewall's message schedule and V*'s session row.
4. `Hides reg ε` is abstract in `RecursiveCircuitPrivate`, and discharged for `regLeaves`. A registration by a Merkle
   root of hm96 row leaves is `regLeaves` with `pub := root`.
5. On the soundness side:
   * `_hbind` is discharged for the executable's registered rows (`regRowCommit_binding`), and is abstract only for
     another commitment.
   * `_hreg` is a fact about the developer: with `regRowCommit`, its registrant opening of each row passes
     `Flock.Registered.opens`.
   * `_hop` and `_hx` are abstract, and carry the content.

   **`_hop`'s form has a gap against the executable.** `_hop` says every accepted outcome's read rows open the
   registration. In a `--zk --registered` session, though, V* checks only that the session's commit string at a
   registered read is included under the registered root; the row and salt behind it stay hidden. The row a session
   uses there is its committed value, which only the knowledge extractor recovers. The existing link from those
   committed values to the registrant's rows is `zk_session_regValsR` (`ZkReg/Vals.lean`), and it is probabilistic: it
   holds except with probability `ε_ks + δ_link + δ_reg`. Its `δ_reg` also takes `cr/sha-512` on the registered-value
   finders (`RegCRZC`) as a hypothesis, which rec-fork's `regCRZC_of_not_fork` already replaces by a run-tied fork
   (`RegForkZC`, or `RegCRZC` at budget 0).
   So `_hop` cannot be discharged from `zk_session_regValsR` as it stands. Two ways forward:
   * a probabilistic `_hop`: the off-registration event's mass, `zk_session_regValsR`'s bound with `RegForkZC` as one
     more fork disjunct, is added to `RecursiveRanRegistered`'s bound; or
   * `Row :=` the commit string, which V* does check, so `_hop` holds at every accepted outcome. The commitment is
     `regRowCommit`'s without the hm96 step, and its binding is `opensLeaf_binding` alone. `_hx` then needs the inner
     statement to be about the circuit description the read commit strings open to; the binding of a commit string to its row
     (hm96's) moves into what `I.holds` means.
   The first changes the statement's bound, so it is a claim for Daniel to read; I did not write either tonight.

   **What the abstract hypotheses carry.** `_hop` and `_hx` are about the extraction functions `reads`, `row` and
   `op`, which are meant to be the run's own: the registered reads in `VRec` (each session's named strategy and
   transcript, `ZkOuter.rd`).
   * Choosing `reads := univ`, `row := p` and `op := op₀` satisfies `_hop` from `_hreg`. `_hx` then says the inner
     statement on accepted runs is already `stmt p`, which is the conclusion's content.
   * Choosing `reads := ∅` makes `_hx` demand that the statement be every circuit description's.

   So the hypotheses are not vacuous, but the theorem says something new only when they are discharged for the run's
   own registered reads, in one of the two forms of the previous paragraph. `_hx` also needs `flockInner`'s statement
   at `(R, ω)` (`Stmt = Hidden cls`, the registered values) to depend only on the rows (or commit strings) read.

## Leaks beyond the class and the owed outputs

These are reported, not assumed away. Each is a place where the statement holds only if the quantity is a function of
the class alone. Otherwise `_hOuter` or the statement's shape fails, and that is a leak.

* **Sizes.** `nh` (the firewall's commitment count), `nr` (registration rows), `I.r`, `S` and V*'s circuits and laws,
  `n` and the law `L`. They are fixed before the circuit description is quantified, so the statement forces them to be
  class-determined. Any implementation where they vary with the circuit description (early exit, circuit description-dependent rounds or tree
  sizes) leaks.
* **V*'s public inputs and statements.** These include anything `R₂` publishes. They must be class-determined, or
  simulable from the class, the owed outputs and the commitments.
* **WIRED topology.** The inter-unit topology is public in the current design; under the class it must be fixed.
* **The owed outputs.** Revealed by design.
* **Adaptive auditors.** Not covered. The inner coins are on the auditor's tape before the first commitment
  (committed coins or a beacon), as in `RecursiveZK`.
* **Channels outside the view.** Not modelled: timing, message and proof sizes, PoUS/PoUW side channels (the channel
  table in `architecture-leaks.md`).

## Proof state and runs

* Local: `lake build Proofs.Flock.Recursive.Private` passes on the head's sources. `#print axioms` shows only the
  standard three for all five, for `regRowCommit_binding` and `regRowCommit_opens`, and for `RecursiveSound` and
  `RecursiveZK`.
* All the audits ran `research run --on vy-nebius-1 --project verity --source . --cwd clone --env
  LEAN_SLOT_POOL=check -- bash -c 'python3 tools/verity/lean/check.py --build [--update] Security --out
  "$OUT/lean-audit"'`.
* `r20261009-074816-0acd` (on `425bbaea6`, `--update`): rc 0, SUCCESS.
  * `security`: PASS, 7,163 declarations in 228 modules, 281 guarantees, only `propext`, `Classical.choice` and
    `Quot.sound`.
  * `security_proofs`: PASS, 61,735 declarations in 959 modules; the kernel accepted 61,090 constants on replay.
  * The review lists the five guarantees as new and every definition their statements read. These are what Daniel's
    DM shows when they land.
  * Its records are commit `51e875f51`.
* `r20261009-071504-9d55` (on `9567b98f9`, the same command): rc 0, SUCCESS. It ran before the per-row binding lemmas
  and the second rec-fork merge. Its lock is byte-identical to `0acd`'s, which confirms that neither change moved a
  record.
* `r20261009-085552-ed4d` (on the head `51e875f51`, without `--update`): rc 0, SUCCESS, `security` and `security_proofs`
  both PASS with the same counts and axioms. Without `--update` the audit compares every guarantee's record with the
  build instead of writing it, so this is the check of the committed lock.
* Cancelled, as stale or superseded: the fast paths `r20261009-063255-0775` and `r20261009-064846-f946`
  (`lean_changed.py --records Security --update`), on trees that still had Lean errors, and the audit
  `r20261009-070405-55b5` on `a879e4846`.
