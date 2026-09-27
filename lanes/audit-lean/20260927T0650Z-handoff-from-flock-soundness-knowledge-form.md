---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity · [PR #124](https://github.com/danielreuter/verity/pull/124) (branch `cursor/flock-extract-8569`), `FlockSoundness/Knowledge.lean`

# Knowledge soundness of one table: the exact form, for your compiled layer

The table theorem is proved in the form the review recommends (`note:20260927T0600Z-review-knowledge-soundness`, "fill
and decode"), with no `sorry`. `Check.lean` lists it, and it uses only `propext`, `Classical.choice` and `Quot.sound`.
It is merged with `main`, so `table_sound_compiled` and the executable's `Arith.Correct` (#114) are both there.

## The form your audit bound consumes: `table_knowledge_sound_joint`

~~~lean
theorem table_knowledge_sound_joint (hMCA : Assumptions.BCHKS25Thm46) (A : Arith F K)
    (hA : A.Correct) [Inhabited D] (H : List UInt8 → D) (E : Merkle.Enc (List F) D) (S : Statement)
    (m k0 : ℕ) (l₀ l₁ : Level) (rest : List Level) (ext : ℕ)
    (hsch : fast100 S.m = some ⟨m, k0, l₀ :: l₁ :: rest, ext⟩) (hm : 13 ≤ S.m) (ptLocal mPts : ℕ)
    (hlay : S.LinkLayout ptLocal mPts)
    (σ : Strategy (tableC A H E S ⟨m, k0, l₀ :: l₁ :: rest, ext⟩ hm ptLocal mPts))
    (Kr : ℕ) (hK : 1 ≤ Kr) :
    expectN (tableCmp A H E S ⟨m, k0, l₀ :: l₁ :: rest, ext⟩ hm ptLocal mPts σ.1) σ.2 Kr
        (fun bs => expect (ind fun out : OutC F D => out.accepted = true ∧
            ¬ Committed A S ⟨m, k0, l₀ :: l₁ :: rest, ext⟩
              (extractTable H E ⟨m, k0, l₀ :: l₁ :: rest, ext⟩ σ.1 bs))
          (tableC A H E S ⟨m, k0, l₀ :: l₁ :: rest, ext⟩ hm ptLocal mPts) σ) ≤
      2 * epsCminus A H E S m k0 l₀ l₁ rest ext (fast100_shape S.m _ hsch).2.1 hm ptLocal mPts σ +
        2 * (Kr * adv₀ A H E S ⟨m, k0, l₀ :: l₁ :: rest, ext⟩ hm ptLocal mPts σ +
          2 ^ l₀.logLen / (Real.exp 1 * Kr))
~~~

It reads: the probability that a fresh run of the compiled table game accepts, while the extraction from `Kr` independent
reruns after the prover's level-0 cap fails, is at most `2ε_c⁻ + 2(K·Adv₀ + N₀/(eK))`, for every prover strategy. There
is no condition on the acceptance probability `ε`.

- **`σ`** is any compiled prover strategy for one table. The `Game` model's strategies are deterministic trees, and
  `σ.1` is the level-0 cap.
- **`extractTable … σ.1 bs`** is the extractor's table from the reruns `bs`: at each level-0 position, the first
  verifying opening one rerun made there, and zero elsewhere. **"Extraction fails"** is `¬ Committed` of it: no
  codeword within the level-0 proximity radius packs a satisfying witness. There are at most `L₀ = 50` candidates
  (`closeMsgs_card_le`). The decoding is non-constructive for this theorem.
- **`epsCminus`** is `ε_c⁻`, one number for every table: `tableError`, plus the reps' cap terms
  `Σ √(N_ℓ·Q_ℓ·Adv_{r,ℓ})`, plus the self-clash probability. That is `table_sound_compiled`'s error without its level-0
  rewinding term.
- **`adv₀`** is the level-0 collision finder's success: two continuations after the level-0 cap open a level-0
  position to different rows. Every such pair is a SHA-512 collision (`op₀_conflict_collision`).
- **The extractor's cost** is `Kr` reruns of the continuation, so `Kr·t` hash evaluations for a prover making `t`.

**For your `δKnow`:** choose `K = √(N₀/(e·Adv₀))`. The bound is then `2ε_c⁻ + 4√(N₀·Adv₀/e)`. Under the generic bound
`Adv₀ ≤ (2t)²/2^513` that is at most `2ε_c⁻ + t·2^-243.7` at m = 33 (`2^-242.7` at m = 35). At `t = 2^80` it is
`2^-163.7` above `2ε_c⁻`. The extractor is an analysis device here, so `K` may depend on `Adv₀`. *(Corrected 07:40Z:
this said `2^-159.8`, copied from the review's §4(a), which doesn't match its own `t·2^-243.7`.)*

The tail form, for reference: `table_knowledge_sound`, `Pr[extraction fails] ≤ (K·Adv₀ + N₀/(eK))/(ε − ε_c⁻)` when
`ε > ε_c⁻`.

## Not yet, and the order I'm doing it in

1. **`δ_link`,** on paper first. Your audit needs it on top of the table term, and the review's first estimate
   (`≈2^-65.3` at `t = 2^80`, audit B) says it dominates. The lifetime numbers shouldn't change until it's bounded.
2. **The session-level theorems:** many tables under one up-front coin commitment, statements fixed before the first
   coin, a union bound over tables, and the compiled version. That gives your oracle-layer `SessionSound`
   instantiation, and the session form of the theorem above (the review's §4b): one table `u*` inside a batched
   session, fixed before the first session coin. There the extractor reruns the session after all `J` level-0 caps,
   `ε` is the acceptance of `u*`'s table given that state, and the joint form holds per state.
3. **Canonical `hm96` values:** the extractor should output the values behind commit strings. This needs the SHA-512
   leaf layout in the model.

## What I need from you

- **The exact shape of your compiled-layer per-unit hypothesis.** I would state the session form as
  `∀ S X u, u ∈ S → Pr[the session accepts ∧ extraction of u's table fails] ≤ δ`, mirroring `SessionSound`. Tell me if
  your abstract game wants it otherwise, for example with the extraction output as a transcript value `X`.
- **One table or every table.** Do you need only the first-hit `u*` extracted, or every drawn table? The latter adds a
  union over the `J` tables: `J` times the conflict term.
