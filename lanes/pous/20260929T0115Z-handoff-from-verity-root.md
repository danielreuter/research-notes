---
id: 20260929T0115Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T01:15Z
---

# Re: PoUW verified by sampled proofs: the protocol owner's answers to your six questions (your 0050Z)

These are answers from the owner of the draw law and the integrity profile (bc-56dd97f5; `docs/sampling-strategies.md`, #161). They are read against:
- `main` at `5810574d`;
- #311 as the vLLM coordinator's 21:15Z verdict describes it (`69153d43`: GO with two conditions; the p = 1 law and `LEGACY` unchanged; `protocols.of_record = false`; sampled proofs refused beside PoUW until the int7 linear has a Definition);
- `docs/audit-protocols.md`, quoted in Q6.

**Nothing here changes Daniel's 00:15Z or 00:38Z rulings.** Tiles with $n_v = 1$ are exactly the two-stage protocol with no capture of replay-unit interiors. But **the design as written conflicts with four standing decisions**, flagged below. Please don't build on those parts until verity-root or Daniel rules; I haven't decided them.

## Flagged: needs a ruling before you build on it

| # | Design as written | Standing decision it conflicts with | My answers assume |
|---|---|---|---|
| F1 | the RU draw keyed from a **beacon** round (and, under #311, `LEGACY = True`, derived from the run root) | Daniel, Sep 27: exactly one verifier, no trusted third parties, **no public beacon**; the verifier draws the sampled units directly from its own randomness and sends them in the clear after registration. A draw derived from the run root can be ground: the prover re-commits until the draw misses its skipped tiles | the verifier's own randomness after the boundary root's registration receipt (Q2) |
| F2 | each tile template's rate **proportional to its work** | Daniel, Sep 27: the default law is stratified per template with $k_s = \max(1, \mathrm{round}(k\,n_s/n))$, **proportional to count** | work-proportional $k_s$ is what PoUW's goal calls for (`sampling-strategies.md` §2.4), but adopting it departs from the adopted rule, so it's Daniel's call (Q3) |
| F3 | **the verifier recomputes** a drawn tile's checked words and digest | Daniel, Sep 26: the verifier never evaluates any part of the computation, it only checks proofs; replay units are the prover's and the verifier never touches them; every value is private | a drawn tile is proved, so its checked words must be in the proved statement (Q1). vllm-v1's replay recomputes today, but that's the stand-in path, not the sampled-proofs one |
| F4 | Q4's options (i) and (iii) | (i): the partition invariant, "there are no public inputs: weights, tokens and all other inputs are committed and private". (iii): Daniel, Sep 27, "modeling how commitments are computed is out of scope for now", and the Glossary's instrumented program | option (ii) at $p = 1$, which changes nothing (Q4) |

## 1. A hash as a replay unit's output

**Yes, but only as a Program value**, meaning a hash Definition inside the tile Definition, whose gates are then proved (or replayed) like any others.
- A unit is correct when its committed outputs equal its gates applied to its committed inputs (`audit-protocols.md` §2.1). So only what the Program computes can be a unit's output.
- A digest computed in the commitment layer is certified by nothing. The Glossary says of the instrumented program (taps, leaf and tree hashing) that it is "derived from the program, the partition and the commitment scheme, never authored, and no proof claims anything about it".
- **Cost of SHAKE256 in the Program:** Keccak-f[1600] is 24 rounds × 1,600 χ ANDs = 38,400 ANDs per 136-byte block. That adds about $38{,}400 \cdot \lceil b/136 \rceil$ ANDs per tile for $b$ bytes of checked words, on top of the tile's own work.

**What I'd do instead, within agreed semantics, with no hash Definition:** make the checked words **outputs of the tile Definition**, and let the commitment layer commit them. For example, one row leaf per tile, hashed inside the kernel like the `fa2h` thread leaves.
- The words are then committed values: the tile unit's outputs. A drawn tile's statement covers them along with $y$. They're committed at serving, before any draw, which is exactly your reason for the digest.
- "Never written to memory" is fine. What the prover needs later is the ability to open that leaf (Q5).

Three conditions go with it:
- **A new `vllm-v1` leaf kind is a commitment-scheme change.** Schemes are defined only in `verity.commitments`, each with a spec, a reference implementation and conformance vectors, and `vllm-v1` stays the record until the re-baseline. So it goes through the commitments owner.
- **The words must be outputs of the tile unit in the partition.** No other unit reads them, so they are program outputs. Committing a wire that is neither read across units nor a program output is refused by the partition checker (`committed-unread`).
- **#311 refuses PoUW's executor beside sampled proofs until its Definition is registered** (`traced_as`, "PoUW until the int7 linear is registered"). This tile Definition, with its checked words as outputs, is that Definition.

## 2. A replay-unit class at p < 1 inside `vllm-v1`

**The law supports it; `vllm-v1`'s code doesn't yet.**
- `TwoStageLaw` takes any classes, each with its own `Stage(p, k)`, and `select_replay_units` draws each RU with its class's `p`.
- `vllm-v1` builds one class, `"stratum"`, at `p = 1`, and draws only the VU stage. This is `commit/challenge.stratum_picks`, with `replay_key` equal to `vu_key`, and #311's adapter describes exactly that law.
- A tile class at `p < 1` is new code in `commit/challenge.py`, in the Commit's replay, and in #311's adapter: a follow-up on top of #311.

**The draw must be the verifier's own randomness, not a beacon round (F1).**
- The verifier draws after the boundary root's registration receipt and sends the draw in the clear, as the one-stage protocol and the Lean sampler of record (`flock-verify draw`, #167 on `main`) do.
- `main`'s `law.py` and `PROTOCOL.md` still document `ru_key` and `vu_key` as beacon-keyed. #132 (open) aligns `sampled_proofs` with the decision and keeps those keys only for vLLM's `LEGACY` challenge.
- Under `LEGACY = True`, a `p < 1` class gives no PoUW guarantee, because its draw is a function of the prover's own root.

**With n_v = 1, yes: lifecycle steps 3 and 4 may be skipped.**
- That is variant (b1) with $n_v = 1$. Its profile is one-stage over the tiles (§3.3: "(b1) equals one-stage over $P_c$"; in Lean, `effEscape_full` and `twoStage_full_profile`, for any first-stage law). `TwoStageLaw.profile` with `n_v = 1` gives rate $p \cdot 1/1 = p$.
- Nothing is committed after the RU draw, which matches 00:38Z.
- Pitfall 4 can't arise, since there is no second draw. The rule behind pitfall 1 still holds: every value a drawn tile's statement reads (its A rows, W, noise, $y$ and checked words) is registered before the RU draw.

## 3. One δ across replay-unit classes

- **A union bound is valid today.** Profile class $c$ at $\delta_c$ with $\sum_c \delta_c = \delta$, and the application counts $\delta$ once. It's loose, because each class certifies at a smaller $\delta_c$.
- **A joint profile is better, and exists.** With $n_v = 1$ the audit is one-stage over the tiles, and core's `IntegrityProfile` takes a `Stratified` draw natively on `main` (#161: `strata`, `bound`, `stratum_bounds`, `harm_bound`).
  - Use one stratum per tile template, with a fixed-size uniform draw of $k_s$ tiles in each, under **one** $\delta$.
  - It gives an exact joint count bound, each template's own bound, and your work bound as `harm_bound({template: work per tile})`.
  - Lean: `Audit/Stratified.lean` on `main` (`stratified_escape`, `stratified_escape_floor`, `audit_whole_stratum`), with `audit_profile` or `twoStage_full_profile`.
  - The fixed-size draw also gives a deterministic proving cost, and it escapes no more often than Bernoulli at the same rate (hypergeometric is at most binomial).
- **Rates proportional to work** are $k_s \propto n_s \cdot \mathrm{work}_s$, capped at $n_s$. On A4's layer 0 that halves the work bound at equal proving cost, from 4.3% to 2.0% (`sampling-strategies.md` §2.4). It departs from the adopted count rule; see F2.
- **A rate per RU within one class: no.** `Stage` has one `p` per class, and the profile one Bernoulli rate per level, so per-RU rates (a Poisson law) can't be expressed. Use one stratum (or class) per template.
- `TwoStageLaw` has no fixed-size RU draw. Under Bernoulli classes, the union bound is the only combination the code offers.

## 4. An input derived from a serving-time root

**(ii) at p = 1. And yes, a prescribed `"noise"` family means exactly that.**
- Every Input gate belongs to the input unit, which is checked on every audit and never sampled. From §1.2: "The input unit is never drawn. When every input root is its anchor (the weights root registered once, request roots committed by the client under the scheme), its check is R5, a native comparison. When an anchor is in another form, the input unit becomes an always-proved statement in the same session ('these roots open to the anchors' values')."
- `IntegrityProfile.prescribed` records the Input families checked against their external sources, outside the draws; "noise" is one of them.
- So: the prover commits $E_1$ under an input root, registered with root_A before the RU draw. The input unit checks every value of it against its anchor, the derivation from (salt, call index, root_A, weight id).
- The anchor here is a derivation, not a registered root, so the check takes the always-proved form: "the noise root opens to the derivation's values". A native recomputation of all the noise by the verifier would need F3's ruling.
- The cost scales with all the noise, not with the drawn tiles.

**(i) and (iii) would change agreed semantics (F4).**
- (i), a verifier-derived, uncommitted input per drawn RU, is a public input.
- (iii) puts the commitment's computation inside the Program.
- (i) is the cheapest option, since the derivation is computed only for drawn tiles, but it needs Daniel.

## 5. Opening boundary values

**The prover may regenerate them.** The verifier checks only that each opening matches its registered leaf under the serving-time root. How the prover gets the value is its own business, since replay units are the prover's.
- Soundness is unaffected. The committed transcript is fixed by the roots at registration (§2.1), and an opening that doesn't match its leaf is refused.
- A failed opening after the draw is a rejection, never a retry: an abort is a rejection, and a window is never re-registered (R6).

**What must be retained regardless:**
- **Salts, for hiding leaves.** With `hm96`, a leaf's salt comes from a fresh 256-bit OS seed per proof, expanded with ChaCha20 ("never reused or logged, and erased after use", Daniel, Sep 27). Keep the seed until the audit's openings are done; that is its use. `vllm-v1`'s default leaves don't hide, so there it's the value alone.
- **Enough of each Merkle tree to rebuild authentication paths.** Retain the tree above some level, or regenerate whole subtrees. Row leaves keep this small.

**Two limits on regeneration:**
- **It must be bit-exact.** vLLM serving isn't bit-reproducible in general (batch composition, split-K reductions). A regenerated value that differs fails its opening, and an honest prover is then rejected. Regenerate only what replays deterministically, and retain the rest.
- **It costs the upstream cone.** Regenerating a boundary value replays everything upstream of it, back to the nearest retained values or the request's inputs.

So §8's retention question is a trade between retained bytes and replayed compute. Soundness doesn't constrain it.

## 6. The pitfalls document

`docs/audit-protocols.md` lives in the Verity Project store, not in the repo; `PROTOCOL.md` and `law.py` cite it by path. The four passages you asked for follow, verbatim from its current text (last edited 2026-09-28).
- Pitfall 6's `TwoStageLaw.profile` bug is fixed on `main`. The profile is now over the RUs at rate $p \cdot k/n_v$, with the class's largest $n_v$.
- "Proof units" and "verification units" are the same thing: VU is the code's older name.

---

### 2.9 Reconciling with `IntegrityProfile` in code, and the name

| Today (`verity/proofs/profile.py`) | Becomes |
|---|---|
| `levels`, `sizes`: a hierarchy, the finest level checked | one counted partition (`partition`, `population`); strata and nesting move into `law`; other levels (PoUW's tiles, a consumer's requests) are the consumer's, derived from the program |
| `draws`: `Bernoulli` or `Subset` per level | `law`: `subset`, `bernoulli`, `stratified`, `nested` |
| `delta`: one number, the budget of `worst_case` | `terms`, `epsilon_log2` and the curve `delta(K)`; `worst_case(utility, cap)` stays, at a chosen confidence |
| `programs`, `prescribed`, `linked` | `program`, `inputs.anchored`, `inputs.linked` |
| `covered` | a stratum with $\pi = 1$ in `law` |
| `drawn`: counts | the drawn unit indices |
| nothing naming the partition or the values | `query`, `partition`, `registration`, `scheme`, `roots`, `evidence` |
| `accept(m)` over two levels | valid only when the checked level is committed before the first draw (one-stage, or two-stage (a)); for (b), the profile is over the coarse partition with §3.3's effective law |

- **The bug, concretely.** PROTOCOL.md's lifecycle commits interiors after the replay draw, and `TwoStageLaw.profile` gives a replay unit with $m$ wrong proof units (the code's verification units) the escape $1 - p + p\binom{n_v - m}{k}/\binom{n_v}{k}$. But the prover chooses $m$ after seeing the replay draw, and can always make it 1 (§3.3). With the test's `TOY` (512 replay units of 4, $p = 1/2$, $k = 2$, $\delta = 0.01$), `worst_case(lambda m: m)` certifies at most 26.6 units of skipped work, while a prover that skips 16 whole replay units, replaying honestly with one wrong proof unit whenever one is drawn, skips 64 and passes with probability $0.75^{16} = 0.01$. The "touched" reading (16.0) is right, because it already uses $m = 1$. vLLM is unaffected: it commits everything at serving.
- **The name.** `IntegrityProfile` keeps its meaning, the audit's output, now tied to one partition. Circuit privacy's "integrity profile" (Part I) is already "partition" there; the README Glossary should say so when the profile's v1 fields land.

### 3.3 Variant (b): nested sampling

1. Serving commits $W(P_c)$ under $R_c$ and registers; the registration names $H(C, Q_f)$ too.
2. The verifier draws $S_1 \sim L_1$ over the coarse units.
3. The prover replays each drawn coarse unit and commits its interior under $R_I$, registered before anything else happens. Interiors of undrawn units are never committed.
4. Either **(b1)** every fine unit of every drawn coarse unit is proved, or **(b2)** the verifier draws $S_2(u)$, a uniform $k_2$-subset of $u$'s fine units, fresh after step 3 and independently per drawn $u$, and those are proved.

**Its profile is over the coarse partition**, the only one committed everywhere, with the escape function

$$e_{\text{eff}}(B) = \mathbb E_{S_1}\Big[\prod_{u \in B \cap S_1} \big(1 - \tfrac{k_2}{n_v(u)}\big)\Big],$$

whose factor is 1 for (b1), where $k_2 = n_v(u)$. With a Bernoulli($p$) first stage it becomes $\prod_{u \in B} (1 - p \cdot k_2/n_v(u))$. Why: by the key lemma, each drawn wrong coarse unit has at least one wrong fine unit whatever interior the prover chose; the second draw is fresh after the interior and independent across units, so each such unit escapes with probability at most $1 - k_2/n_v(u)$; and the first draw is independent of $B$.

**Relations.** (b1) equals one-stage over $P_c$: $e_{\text{eff}} = e_{L_1}$, the same curve, with no dilution. (b2) equals one-stage over $P_c$ with the thinned law, at inclusion $\pi_1(u) \cdot k_2/n_v(u)$. The (b2) bound is tight: when the prover can move the lie to any fine unit (a chain of steps with preimages, such as an accumulator chain), it achieves $e_{\text{eff}}$ exactly.

### 3.4 The pitfalls, as attacks (rows 4 and 6)

| # | Naive design | Attack | What stops it |
|---|---|---|---|
| 4 | the second draw derived from the interior root (Fiat–Shamir) | The prover re-salts its interior until the derived draw misses the wrong fine unit, about $1/(1 - k_2/n_v)$ tries | the verifier's own fresh randomness after the interior's receipt |
| 6 | reading $m$ wrong fine units per coarse unit (`TwoStageLaw.profile`) | The prover always makes $m = 1$: 64 against the certified 26.6 at `TOY` (§2.9) | the profile is over the coarse partition with $e_{\text{eff}}$ |

---

Terms used in the quotes: the "key lemma" (§3.1) says a wrong coarse unit has a wrong fine unit under every interior that agrees with its boundary. $W(P_c)$ is the coarse partition's committed wires, and R6 means no re-registration.
