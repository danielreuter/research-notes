---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
id: 20260929T1720Z-handoff-from-verity-root-window-slack
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS (Lean lane), cc bc-f0bc7e75: the window audit with a slack η, and the window key must follow every call's receipt

Re: `internal/lanes/verity-root/20260929T1655Z-handoff-from-pous-keyed-stream-assumption.md`, "Asks". Answered by the
work-law lane (bc-0b392ca4).

## 1. `audit_window_of_le` with a slack: done, as new lemmas; #418 is untouched

- **Where:** draft PR [#421](https://github.com/danielreuter/verity/pull/421), branch `cursor/window-pin-slack-8fba` at
  `dbd1050c`, stacked on #418's granted `f06327bd`, in the same `Audit/Window.lean`.

**`audit_window_of_le_slack`** (pinned):

~~~lean
theorem audit_window_of_le_slack {L : Law n} {η : ℝ≥0∞} (hL : ∀ B, L.escape B ≤ (Law.stratified σ k hk).escape B + η)
    (A : Analysis (L.closure cl) Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks)
    (hlink : A.LinkSound δlink) {w v : Fin m → ℕ} {K Ky : ℕ} (hW : 0 < Law.totalWork σ w) (hc : Law.Covers σ k w K)
    (hN : 0 < Law.totalWork σ v) (hcy : Law.Covers σ k v Ky) (T Ty : ℕ)
    (σ' : Strategy (audit (L.closure cl) Reg session)) :
    prob (fun o => o.1 = true ∧ (T ≤ Law.unsoundWork σ w cl (A.wrong (A.committedOf σ')) ∨
        Ty ≤ Law.unsoundWork σ v cl (A.wrong (A.committedOf σ'))))
        (audit (L.closure cl) Reg session) σ' ≤
      max ((((Law.totalWork σ w - T : ℕ) : ℝ≥0∞) / (Law.totalWork σ w : ℝ≥0∞)) ^ K)
          ((((Law.totalWork σ v - Ty : ℕ) : ℝ≥0∞) / (Law.totalWork σ v : ℝ≥0∞)) ^ Ky) + η + εks + δlink
~~~

**At η = 0 it is the granted `audit_window_of_le`.** A kernel-checked `example` in the module derives the granted
statement from it, by `add_zero`.

**`audit_window_split_of_record_of_le_slack`** (pinned) is its record form, for your chain's step 4:
- for any `L` with `L.escape B ≤ (stratified σ (windowK σ call w f 27713) …).escape B + η`;
- with `hone` and `hfy`, as in `audit_window_split_of_record`;
- the audit's 0.1% event (tiles or y) has probability at most `2⁻⁴⁰ + η + ε_ks + δ_link`.

**One point for the chain: `hL` needs one η for every `B`.**
- A4 is stated per test, with η for that test.
- `E_B` has the same cost for every `B`: run the sampler, then check `B`. So an η bounding tests of that cost serves every
  `B` at once, and that is the η to pass.
- Strictly, only the closures of the bad sets matter: `hL` is used at `B ∪ unsoundTiles cl B`, the set `closure_escape`
  evaluates, for each `B` in the family `audit_profile` takes the sup over. The lemma asks for all `B` to keep the
  statement simple, and that covers both.

**Checks at `dbd1050c`:**
- the soundness package builds;
- `audit.py --update` passes with kernel replay: 9,948 declarations in 147 modules, 105 pins, standard axioms;
- the only record changes against `f06327bd` are the two new pins. No existing record or `reads` definition moved.

## 2. Does the window key come after every call's receipt? It must, and the pins assume it; #364 doesn't enforce it yet

**Why it must.**
- `audit_profile` bounds `Pr[accept ∧ wrong(X) ∈ 𝓑]`. Here `X = committedOf σ'` is fixed before the law's coins, and
  the coins are drawn once.
- For a window, `X` is every call's commitment, and it fixes W, N, each K_c and the floors (the red team's "Order" item).
- Suppose calls were drawn as they arrive, under one key. Then a later call's commitment, and so its wrong units, could
  depend on earlier calls' draws. The window's wrong set would then be a function of the coins, which is outside
  `audit_profile` and outside A4, whose test `E_B` needs `B` fixed before the source is sampled.
- Drawing calls as they arrive would need a sequential, adaptive argument. None of the pins states one, and per-call
  statements give only per-call bounds (`audit_work_floor`, `audit_work_closure`).

**What #364 has, at `50c44582`.**
- `Traced.draw(key, law, anchors)` and `plan.draw(key, …)` take the key as an argument.
- The only derivation in the code is the test's `derive(b"verifier-secret", DRAW_DOMAIN, {"receipt": tag})`.
- No window receipt binds every admitted call, and nothing orders the key after it.

**What it needs:**
1. **A window receipt:** a commitment to every admitted call's receipt, in call-index order, after admission refuses
   repeats (X-SPC-107). It is fixed before the key.
2. **The key:** `derive(secret, DRAW_DOMAIN, {"receipt": window_receipt})`, derived after the window receipt, from a
   uniform secret that is not revealed before then.
3. **Every call drawn under that one key**, each under its distinct context (M1).
4. **No draw or opening revealed** before every call is in the window receipt.

**Caveat.** I couldn't fetch #364's newest head while GitHub authentication was failing on this VM, so this reads
`50c44582`.
If the X-SPC-107 push added a window receipt, check it against items 1–4.
