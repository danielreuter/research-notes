---
id: 20261004T2202Z-report-relay-docs-pouw-research-plan
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/research-plan.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/research-plan.md`, sha256 `e866d4864b9fea3a6ce8bc5e6f05cce27c871c1e0c2b19e9a715fc4d15d75042`, last written 2026-10-01T02:17Z, after the 30 Sep snapshot `art:8bd64630…42e9`, whose copy may differ. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# PoUW research plan and status

Updated 28 Sep 2026, 01:13Z. Ground truth: [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/problem-statement.md), now draft 3, which applies everything below. On 27 Sep Daniel accepted its six defaults: tail-bound accounting, worst-case inputs (degenerate ones included), int7 useful operands, about 130× hashing overhead for milestone 1 only, TT(0.5%) as the single named hypothesis, and RTX 4090 adversaries only.

## Goal

A certificate for every int8 matmul of a workload. Except with small probability, an accepted audit certifies work within γ ≤ 1% of the honest reference's, jointly across units, with unbounded preprocessing on fixed weights. The security comes from the matmul work, not from hashing, and it is proved in Lean from TT(0.5%) plus standard assumptions.

## Where it stands

- **Milestone 1 is specified, proved in Lean, and reviewed.**
  - Shape (m, k, n) = (2^12, 2^16, 2^16).
  - Noise: rank-16 factors, the outer ones in {−3, …, 3} and the inner ones ±1, with E_R shared by groups of 16 units.
  - Checked values: the running sums after every 16-deep step.
  - Result: γ ≈ 0.85% under TT(0.5%), with 131× SHAKE256 hashing and about 1.3× real time to read the accumulators.
- **Transformer shapes are out of reach under worst-case inputs.** They give γ ≈ 2.5–7% for the milestone design at any hashing overhead. A floor for the whole class of additive-noise schemes is 1.89% at k = n = 4,096.

## Threads (19:55–22:37Z)

| Thread | Result | Report |
|---|---|---|
| Lean milestone 1 | **Granted by the red team.** 55 pinned theorems, all signed by the named statement reviewer. Verity's audit passes with `leanchecker --fresh`, on the three standard axioms | [notes](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/pouw/NOTES.md) |
| Break or weaken TT | TT survives at depth 16. The noise distribution is named. Five holes in the cost model, a table attack on shared noise and a copy attack on the factor placement were found and closed. A restricted model with a provable bound serves as a Lean witness. The low-rank design D4-s is safe with one fix | [report](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/tt-attacks.md) |
| LLM shapes | γ ≤ 1% is unreachable for the milestone design (D1) at transformer shapes, at any hashing overhead. A class floor; relaxation numbers; the D4-s design | [report](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/llm-shapes.md), [relaxations](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/llm-relaxations.md) |
| RTX 4090 constants | §3.1's prices confirmed on a real 4090 for USD 0.51 of the USD 15 budget; six research Attempts, campaign `pous-pouw`; all pods down by 20:54Z | [report](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/gpu-constants.md) |
| Red team | Draft 2 not granted as written, and its fixes are adopted. Draft 3 granted with conditions, all applied and confirmed. The Lean is granted | [report](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team.md) |

## Findings

1. **The cost model needed four rounds of repair, and the result is the accounting W1** (problem statement §3.1).
   - Additive memory pricing gives γ ≥ 6–29%. It charges the honest GEMM for operand traffic that a zero-input adversary skips, because the adversary regenerates hash-derived operands on chip for free.
   - Making memory free opens two attacks. Unbounded preprocessing can tabulate the zero-input transcript for every noise value, through the preprocessing state, the program text, dummy weights or dummy activations. And memory with data-dependent addresses computes any function for free, which makes TT false for every protocol.
   - W1 prices instructions per instruction at the measured rates, and a tensor-core instruction by its full shape. Oblivious online traffic is free. Any instruction whose address, guard or enclosing branch depends on data, implicit flows included, costs 16 per 32-bit word. The first fetch of a pre-salt byte costs the DRAM rate, except the operands of units that come out correct.
2. **At checked depth 16, TT reduces to a statement about output words.** Every INT32 or tensor-core instruction costs at least 16 units per 32-bit word it outputs, and the honest reference pays exactly 16 per checked value. So Strassen, Winograd, rank deficiency, int4 and dp4a cannot pay. The remaining routes need structural copies, FP32 adds on integer bit patterns (8 units) with shared operands, or tables shared across many rows. The named noise and the group rule close each of these.
3. **The noise must be named, and the choice is delicate.**
   - Pearl's sparse factors make every slice rank-deficient.
   - An outer ±1 factor makes 37% of the transcript's columns free copies.
   - Sharing E_R per epoch admits a table attack worth up to 44%.
   - Checked depth above the rank loses 40% (depth 32 at rank 16).
4. **Milestone 1: γ ≈ 0.85%,** from a machine-checked recount that includes the limbs, the combine, the noising and the per-group and per-weight shares. It needs every noise group to serve at least 2^16 rows on its weight.
5. **Transformer shapes cannot reach 1% under worst-case inputs.**
   - The milestone design gives 2.5–7% (4.6% at 4,096²), and with k = n it needs k ≳ 36,000.
   - For the whole class of additive-noise schemes on int8 tensor cores, the floor is 1.89% at k = n = 4,096, and 1% needs k ≳ 17,800.
   - D4-s (rank 8 at depth 16, with a rejection rule) comes close: about 2.0% at 4,096², and 1% at k ≳ 18,700, e.g. Llama-3-70B's down projection.
   - Approving the weights roughly halves γ.
   - Only activations computed by the approved model from inputs the prover doesn't choose reach γ ≈ 0.5%, and that rests on a model-specific heuristic.
6. **Folds cut the hashing but not γ.** Linear folds are broken outright, because they commute with the product. Nonlinear folds cost 0.5–2× the GEMM and need their own assumption.
7. **Measured on an RTX 4090.**
   - Tensor-core rates match the price table exactly.
   - INT32 costs 16 units per instruction, a DRAM byte about 345 units, and SHAKE256 about 2,100 units per int32 value.
   - The int8 depth-16 step runs at full rate.
   - Concurrent CUDA-core work adds at most 5%.

## Decisions

**Decided by Daniel on 28 Sep, each at its default** (problem statement §9, questions 7–9):
1. The accounting W1 is the cost model.
2. Milestone 1 keeps worst-case inputs, and transformer shapes are treated as research.
3. The checked depth is 16.

**Decided by Daniel on 28 Sep at 03:35Z:** W1 prices sub-word extraction like PRMT, at 16 units per word, on both sides (problem statement §3.1 and §9, question 11).

**Decided by Daniel on 28 Sep at 01:23Z** (campaign 2, [new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md) §5):
4. NCP is the full-rank-noise construction, with TT_NCP(0.5%), and the main candidate for transformer shapes; D1 is the baseline.
5. About 400× hashing at depth 16 is accepted for the first build.
6. About 3× honest arithmetic is accepted.

## Next steps (proposed)

- Build milestone 1 end to end: the honest kernel with running-sum reads and SHAKE256 Merkle commitments, and a falsification benchmark for TT on a 4090 over the attack classes of §5.
- Formalize the M_4090 instruction schedule of the honest reference, to discharge `AdmitsRef` at `m1Wref`.
- Research D4 for transformer shapes, starting from D4-s and the class floor.

## Rules the threads followed

- Every named hypothesis in the Lean chain has a Lean satisfiability witness, and each degenerate instance has a Sanity lemma.
- The problem statement was corrected in place. Draft 2 is frozen at `internal/pouw/problem-statement-draft2.md`.
- Working reports are internal; this plan and the problem statement are for Daniel.

## Campaign 2: new cryptography for full-rank noise (from 23:10Z, 27 Sep)

**Daniel's direction (23:00Z).** Milestone 1 is Komargodski–Weinstein/Pearl's low-rank-noise transcript, hardened, and it rests on their conjecture precisely because the noise is low rank. Full-rank noise and a much higher honest overhead are acceptable. But full-rank additive noise with a separate decode gives the adversary γ ≥ 1/2 at zero inputs (Lemma 1, part 2). Wanted: new cryptography that gets around this.

**Constraints, unchanged:**
- worst-case inputs, unless Daniel relaxes them;
- the RTX 4090 accounting W1;
- γ ≤ 1% jointly;
- security from the matmul work, not from hashing;
- Lean for anything claimed.

**Threads:**

| Thread | Question | Output |
|---|---|---|
| Barrier | For which class of encodings must honest work that the adversary can skip on degenerate inputs exceed γ? Which hypothesis must each escape route break? A general impossibility statement, in Lean where feasible | internal report; Lean in `lean/submissions/pouw/` under a new namespace |
| Constructions | Designs that break a hypothesis of the barrier with full-rank or unstructured noise. The coordinator's lead to verify or break is noise that cancels inside one checked GEMM: AB = Σ ±(A + E_i)(B + F_i) with correlated full-rank E_i, F_i, and no separate decode. For each design: γ at the milestone shape and at 4,096², the honest overhead, and the assumption, classed as standard, a new concrete conjecture or a model restriction | internal report |
| Other escape routes | An independent search outside the cancelling-noise family: non-linear encodings, beacon or verifier secrets, interactive or timed variants, commitments to inputs before noise | internal report |
| Red team | Every candidate and the barrier statement, before anything is reported | internal report |

**Output:**
- Results go to `docs/pouw/new-crypto.md`, with only red-teamed candidates reported as results.
- Working reports go to `internal/pouw/new-crypto/`.

**Status (00:45Z, 28 Sep).** Results are in [new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md), every one red-teamed.
- **Barrier.** The generic barrier and its classification are proved in Lean, and the red team granted them, signing 25 new pins (80 in total).
- **NCP.** It is the one construction that escapes the barrier with full-rank noise: γ ≈ 0.51% at the milestone and 0.66–0.92% at 4,096² under TT_NCP(0.5%), at about 3× arithmetic and 394× hashing. The red team granted it with conditions, all applied in the text.
- **Lean still open:** the stronger rule on P and checked values mod 2^32, both in progress.
- **Everything else fails or is dominated by NCP:** encodings, checked decodes, secrets, timing, input restrictions, and the noise-free transcript.
- **Decisions for Daniel:** three, in new-crypto.md §5.

**Follow-ups after Daniel's 01:23Z decisions: all done (01:26–03:12Z).** Details are in [new-crypto.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md) §6.
- **Lean.** There are 104 pins, all signed, and `check.sh` passes. The rule on P is checkpoint independence: the step clauses were refuted by a Lean counterexample (8.3%), and the relation-free rule by the red team (8.1%). The stronger witness R_word-NCP under independence is proved, with a structural witness, and the chain reaches the wrapped checked values.
- **u8 × s8.** It runs at the full rate, so γ = 0.66% at 4,096² stands.
- **The falsification benchmark.** For independent P, nothing reaches below 0.995 at 4,096², and every positive control fires. TT_NCP(0.5%) needs k ≥ 1,067.
- **GPU spend.** USD 0.38 for these follow-ups, USD 0.89 for PoUW this session. All pods are down.

**Next (from 03:40Z): Theorem D, the backup for TT_NCP** ([milder-assumptions.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/milder-assumptions.md) §2).

| Item | Worker | State |
|---|---|---|
| Attack Theorem D's reduction chain (§2.7): H_16, the AlgM model, the dimension count, A1 margins, MinRank(P) | Red team | Statement fixes so far: TD-1 (blocking: A may depend on the public F₁ and R, so the model must allow that; the bound survives), and TD-2 to TD-5 (major: integer semantics, H_16 per register written, an explicit lifting step, A1 needing MinRank(P) ≥ 2). All relayed to the Lean worker; the verdict is pending |
| Formalize Theorem D in Lean (namespace `Pouw.Dimension`), with witnesses for every named hypothesis, and A1's c as a parameter | Lean worker | First version at 04:12Z: 15 pins (119 in total), `check.sh` passes, and A1 at c = 2 and A2 are named with witnesses; the mixing lemma is open. Being revised for TD-1 to TD-5 |
| W1: should sub-word extraction be priced like PRMT? It decides whether A1 needs c = 2 or c = 4 | Daniel | **Decided 03:35Z: yes, 16 units per word, on both sides.** So A1 needs c = 2. NCP's honest recount gives γ ≈ 0.69% at 4,096² (was 0.66%) with a word-granular P, which the coordinator certified independent. The red team is checking which signed records depended on free byte moves, and re-signing |

**Overnight push (from 04:35Z): shrinking the residue of the Theorem D chain.**

**GPU freeze (Verity root, 08:10Z).** RunPod funds are low, and a top-up has been requested from Daniel.
- No new PoUW pods until the root says the top-up has landed.
- Terminate any running pod as soon as its job ends.
- Below about USD 60, pause anything that is not mid-measurement.
- Lean and CPU work continue.

At 08:10Z no PoUW pod was running, and none was needed by an open item. The balance was USD 121.98, with the account at USD 12.31/h across all workstreams. **11:16Z: the top-up has landed** (USD 297). POUS resumes capped GPU work at 11:45Z unless the Verity root holds. Round 5 (FP32 NaN outputs; USD 3 cap; one pod, `vy-pous-pouw-nan`, terminated as soon as the list is done) is gated on `internal/pouw/gpu-round5-gate.txt`, which must say GO. FSEL, FMNMX and HFMA2 were already measured in Round 4 at 16.1–16.6 per register, so the FP32 pipe is only FFMA, FADD and FMUL.

| Item | Worker | State |
|---|---|---|
| Theorem D in Lean with the red team's TD-1 to TD-5 fixes, then the red team's signature | Lean worker, then the red team | Fixes done (04:46Z, 119 pins, `check.sh` passes); the bound is unchanged with A = g(F₁). **Signed** by the red team (04:58Z); route U is verified at 0.694%. The W1 re-check found one record: `m1Wref` misses the int8 limb split of two decode intermediates (Ω* 1 + 233/2^16, γ still 0.85%), and it is queued to the Lean worker with P7-1 (causal A across units) and P7-2. The Lean worker has since proved the mixing lemma and `TT_NCP_of_A1_A2` (06:00Z; 137 pins), plus P7-1 (causal A), P7-2, P7-3 and P7-4, MinRank ≥ 2 for the shift by 24, and the lifting Lean. It is now formalizing A1_cost in the adopted model (a closed scalar pipe, the additive form, MinRank ≥ 5), the quadratic-program theorem, and MinRank ≥ 16 in Lean; Phase 8's P8-1 to P8-6 follow when it returns. P7-4 moved Ω* to 65769/65536 and γ_M1 to 14017/1644225 ≈ 0.8525%, updated in `problem-statement.md` and `kw-reference.md`. **The red team signed the 18 new pins and the three changed digests** (Phase 9A, 06:20Z; it is the named statement reviewer), with P7-4's arithmetic confirmed independently. P9-1 (tooling): the store's vendored `audit.py` predates per-definition digests, so the digest changes couldn't be traced by a diff. Verity's current `tools/lean` is staged at `lean/tools/lean-main-6746f408/`, and the Lean worker switches to it before the Phase 8 re-pins. **06:53Z, 149 pins:** A1_cost is stated in the closed scalar pipe, covering P8-1 and P8-2, with MinRank ≥ 5 and split into `A1_cost_quad` and `A1_nonquad`. `ttNCPOfA1costA2` is the c = 2 chain, and `minRankGeShift16` gives MinRank ≥ 16 for the shift in Lean (P8-6, P9-2). No existing record changed. Theorem 1 (the forest theorem) is still paper-only, so `A1_cost_quad` is still assumed. Next, as its own step: the audit-tool switch, proved to change only the format (the old tool reproduces the signed records; pins unchanged). Then Theorem 1 in Lean. **All 12 pins GRANTED** (Phase 9B, 07:48Z), and the Pipe module meets P8-1, P8-2 and P10-2 item 5. **P9B-1 (major):** A2 requires the model program to reproduce *every* output of the real program, so extra outputs refute it (γ₂ ≥ 0.47 for the quadratic chain, 7/16 for the closed chain, and the same in the older H16 and H4090 chains). Fix: restrict A2's output clause to the checked words. The proofs are unchanged and the assumption gets weaker. It is queued to `barrier` after its current pass, with a statement review. **07:57Z, 156 pins: Theorem 1 is proved in Lean in full** (`Pouw.Dimension.Forest`). `a1CostQuadHolds` makes `A1_cost_quad 2 0` a theorem for every k and R at MinRank ≥ 5, and **`ttNCPQuadOfA2`: for the quadratic closed pipe, TT_NCP follows from A2 alone.** The audit-tool switch (P9-1) is done and shown to change the format only: the old tool reproduces the file byte for byte, and under the new tool every pin is identical. Now: `barrier` fixes P9B-1 and states Theorem 1 generically for route U; the red team confirms the switch and reads Forest (Phase 11). **Phase 11 (08:16Z): the switch is CONFIRMED, and the 7 Forest pins are GRANTED** (the MinRank ≥ 5 route is sound, and `algBoundQuad8` is tight). Queued after the current passes: P11-1, moving `A1_cost`, `A1_nonquad` and `A1_cost_U` into an assumptions module (Verity's rule; it makes them visible to the audit); P11-2, pinning `quadChainConsistent` at γ₀ = 16/(3k); and optionally R11-1, an open quadratic pipe that may read tensor-core outputs. **08:28Z, 161 pins: P9B-1 is fixed.** A2 now takes a target set W, the non-final checked words, and constrains only outputs in W. It is one definition for H16, H4090 and both pipes; 13 definitions changed, and no pin record did. `a2WitnessExtra` shows that extra outputs no longer refute it. **Theorem 1 is generic:** `theorem1Family`, `gridNear` and `a1CostQuadNear` cover every family within V₀ of the words, so route U is covered in four lines. Caveat: restricted A2 into `QuadPipe` absorbs `A1_nonquad`'s question (do merging pipes help?), so it moves that question rather than settling it. Now: the red team reviews the 13 definitions (Phase 12), then `barrier` does P11-1, P11-2 and P9B-3, then the route-U integration, then R11-1. **Phase 12 (08:47Z): the P9B-1 fix is CONFIRMED** by the named statement reviewer. Reverting W reproduces all 13 old digests, and the other 571 definitions are unchanged. It is proved in Lean that old A2 ⇒ new A2. The two A2 pins are re-signed and the 5 new pins GRANTED. Queued: P12-1 (pin the direct separation statement), P12-3 (`barrier.md` should say 'asks A1_nonquad's question', not 'is its content'), and P12-2 (update the submission's `ASSUMPTIONS.md` for words-only A2 and Theorem 1 in Lean before any merge, in the prose pass after integration). **08:56Z, 163 pins:** P11-1 moved five assumptions into `Pouw.Dimension.PipeAssumptions` (A1_cost, A1_cost_quad, A1_nonquad, LiftMinRank, LiftMinRankL5e); the `reads` record now shows which 10 pins read it, and that `ttNCPQuadOfA2` is not among them. The tool's `assumptions` field stays empty because it only lists no-argument Prop binders; accepted. P11-2 `quadChainConsistentTight` and P9B-3 `pipeWordWitness` (a pipe computing a real checked word) are pinned. Next: `barrier` does P12-1 and P12-3 in the package, then R11-1 in staging (`barrier-assets/r11-1/`); the route-U integration follows when its worker returns. **09:46Z: P12-1 is pinned (`a2Separation`, `emptyQuadPipe`; 165), and R11-1 is proved in staging.** `algBoundOpenQuad`: FP32 steps may read priced values, such as tensor-core words, and cost ≥ min(p_b, 2·c_s)·D = 16·D at W1's prices, with no A1. That removes P9B-1's tensor-core-junk half. **Finding (`a2WordsIff`): under independence and MinRank ≥ 5, words-only A2 (into `QuadPipe` or the open pipe) is equivalent to 'every program of the machine pays (1 − γ₂)·16 per checked word', which is the per-word form of the conclusion.** A model program with one priced instruction per word always exists, at the 16·D floor. So after P9B-1 the Theorem D chain does not reduce TT_NCP to a milder assumption: old A2 was refutable, and new A2 restates the conjecture. Its value is proved evidence (nothing in the algebraic model classes beats 16 per word). Next: integrate R11-1, then scope an embedding theorem (`M4090` as a Lean machine with W1's prices, where every program is an open-pipe program except FP32 merges), which would replace A2 by a theorem plus a merges-only A1. It is designed in `barrier-assets/embed/DESIGN.md`, and every semantic choice goes to Daniel. **10:38Z:** R11-1 is integrated (229 pins, no existing record changed). The embedding is proved in staging (`barrier-assets/embed/`, 9 theorems, a scratch integration at 238). `embedM4090`: every `M4090` program is an open-pipe program at no greater cost, except its non-quadratic FP32 steps. `a1fpIff`: TT_NCP's per-word form for `M4090` ⇔ `A1_fp`, a statement about FP32-only pipes on the checked words. It is equivalent, so not weaker, but the assumption is now about FP32 arithmetic alone. It rests on semantic defaults S-1 to S-11; the key one is S-2 (IEEE or exact FP32: magic-constant FADD can extract bits at 8 units). There are named gaps G-branch (a proposed W1 amendment: 16 per live-out word at a data-dependent join), G-wrap, G-grid, G-fp, G-price, G-hash, G-causal, G-concurrency and G-complete. The red team is reviewing it (Phase 14) before anything goes to Daniel. **Phase 14 (11:13Z):** the 9 R11-1 pins are GRANTED, and `a2WordsIff`'s reading is confirmed. The embedding's proofs match DESIGN.md. **New, in the defender's favour:** the 4090's FP32 unit writes only the canonical NaN, so it can never write the int32 values −8,388,607 … −1. On instances where every checked word lands there somewhere on the grid, TT_NCP for M4090 holds with no A1_fp and no A2 (`ttNCPM4090_of_nanGap`, red-team Lean). This is instance-dependent and needs a NaN measurement. Recommendations: keep S-1 and S-3 to S-11; change S-2 to IEEE with canonical NaN; price FSEL at 8; admit m8n8k4; the G-branch W1 amendment is needed and sufficient. Being integrated now as draft semantics pending Daniel. Measurements after the freeze: NaN outputs of every FP32-class opcode, and the rates of FSEL, FMNMX, HFMA2, m8n8k4, b1, texture and the issue ceiling. **11:51Z: the embedding is integrated** (241 pins; all 229 earlier records unchanged). The coordinator's relayed 'FSEL at 8' weakened the range-gap result, because a select copies NaN bits. But Round 4 measured FSEL, FMNMX and HFMA2 at 16.1–16.6 per register, so W1 prices them at 16 and no H5 amendment is needed. The 12 unsigned embed pins are being revised to the measured prices, restoring `A1_fp` at γ = 0 on range-gap instances for every `M4090` program. `nanGapConsistent`: at every k ≥ 1024 there is an instance whose non-final words are all −1 or −2. Then the red team's statement review. **Round 5 (12:02Z): canonical NaN confirmed.** FADD, FMUL and FFMA return only 0x7FFFFFFF in all 72 forms (43.6·10⁹ NaN outputs). FSEL passes payloads (priced 16), and FMNMX never does. The rates match Round 4. It cost USD 0.08; the pod was terminated at 11:57:08Z; the total over five rounds is USD 0.96. Caveat: FSET writes −1 at an unmeasured rate, so the gap starts at −2. **12:19Z: the embed is revised to the measured prices** (243 pins; 229 earlier records unchanged). Only FFMA, FADD and FMUL are at 8. `a1fpOnRangeGap` gives `A1_fp` at γ = 0 on range-gap instances for every `M4090` program, from checkpoint independence alone, and `ttNCPM4090NanGap` has no FSEL restriction. Next: FSET goes into the FP32 class at 8 (outputs 0, −1, 1.0f), the gap is narrowed to exclude −1, the witness avoids −1, and then the red team reviews all 14 embed pins. **12:37Z: done** (243 pins; no pin record changed). `NaNGap` is −8,388,607 … −2 plus the positive NaN range, and `nanGapConsistent`'s words are −2 or −4. Open: FSET's predicate operand is modelled only as constant; its outputs stay in {0, −1, 1.0f}, and measuring its rate would settle it. Running: the red team's Phase 15 statement review of the 14 embed pins, and the submission prose pass. **Phase 15 (12:57Z): all 14 embed pins and their definitions GRANTED**; no blocking finding. `ttNCPM4090NanGap` needs only `CanonicalNaN`, CI and the gap condition, with no MinRank, A1 or A2, and the witness attains the bound with equality. `M4090` never over-prices W1 on any measured opcode. P15-1 (minor): FSET with a data-dependent predicate is not covered at 8. If FSET measures at 16 or more it moves to INT and the issue closes; at 8 it needs an 'any function into {0, −1, 1.0f}' constructor and A1_fp's re-review. **Round 6 (13:06Z):** FSET is on the ALU pipe at 16.38–16.63 per register, and the u32 form lowers to FSETP + SEL (16). So P15-1 is closed. It cost about USD 0.05; the pod was terminated at 12:57:36Z; the total over six rounds is about USD 1.01. The Lean change was docstrings only (`lean-audit.json` byte-identical), and the red team confirmed P15-1 closed (Phase 15 addendum, 13:27Z). All 14 embed pins stand, and the ledger marks them approved. P15-2 (minor): unmeasured register writers (FRND, P2R, VOTE, MUFU, FP64, the uniform datapath, int4 and b1 MMA) should be priced at 8 only if their outputs are shown to avoid the gap |
| A MinRank(P) certificate (at least 2, ideally 16) for the word-granular production P at k = 4,096 | MinRank worker | **Done (04:51Z): MinRank = 16 exactly**, the maximum, by a paper-proved reduction to the step graph's edge connectivity plus an exact-integer script (λ₃ = 32). It also holds for the shift by 24 at k = 1,024 and 4,096, with a Lean-ready statement queued for the Lean worker. **Granted by the red team (Phase 8, 06:02Z)**, after an independent recheck with its own generator and max-flow (every cut ≥ 32). Minor: P8-5 (the formula assumes a connected step graph) and P8-6 (a bridge from `MinRankGe` to `MinRank2`). MinRank ≥ 2 for the shift by 24 is pinned; ≥ 16 in Lean is a stretch item |
| The lifting lemma: correctness only at the realized noise, and grinding; paper proof, with Lean in a scratch copy for the Lean worker to merge | Lifting worker | **Done (05:41Z):** proved on paper from independence and MinRank, with a bound exponential in the saving; L2, L3 and L4's core are in Lean (scratch copy, Mathlib only). For γ-relevant savings (≳ 0.37% at 4,096²) q·ε is negligible at both shapes. Proposed tweak: derive E₁ for groups of ≥ 4 units. **Integrated (06:00Z):** L2, L3 and L4's core are pinned, and `Lift_MinRank` is a named Prop (`LiftMinRank`, `LiftMinRankL5e`) with witnesses. L5a and L5e stay paper-only. The red team is signing the pins (Phase 9A) |
| A1 at c = 2 as pure mathematics: a proof, or a counterexample (literature, proof attempts, CPU search) | A1 worker | **Done (05:08Z).** With free additions, A1(2) is probably false for large m, n (Brockett–Dobkin 1976: n² + o(n²) for inner dimension ≤ log₂ n), and it has exact counterexamples if MinRank ≤ 4. Proved: L(V) ≥ dim V + MinRank − 1, and an additive form suffices. Best verified algorithm at inner 16: 3.4 products per word. **Adopted:** A1 restated in W1's cost model with additions priced, where the known margin is about 5×; relayed to the Lean worker. **Granted by the red team (Phase 8):** Lemma 1 and Propositions 2–6; Brockett–Dobkin is cited, not rechecked. P8-3: the pinned `A1_W1` is false at MinRank 2 to 4, so it must require ≥ 5. P8-4: A1(2) leaves the recommended chain |
| A1 in W1's cost form (additions priced): prove it or bound it | A1-cost worker | **Done (05:37Z).** Proved on paper, with γ = 0, for quadratic FP32 programs (each product of affine functions of the noise), which covers every known algorithm: they need at least 2·dim V instructions, so at least 16 units per dimension, under independence and MinRank ≥ 3, and the bound mixes with Theorem D. General FP32 programs are open: only half the target is proved, and the obstruction is merging FFMAs. The best algorithm with additions priced is 14.5 instructions per word (7.25× the target). **Granted with conditions (Phase 8):** P8-1 requires every addition to be priced (free copies allowed). P8-2 requires each FP32 product to multiply two free (V₀) values or scale by a constant, which lets A depend on F₁. Under both, cost ≥ 16·dim(T mod V₀) is a theorem at MinRank ≥ 3, and only FP32 products of non-free values stay assumed (`A1_nonfree`). The coordinator adopted this as A1_cost's model; the Lean worker formalizes it next |
| From the MVP (06:36Z): NCP's checked values on route U. The Lean and the MVP use unbiased sums, which need route S (γ ≈ 1.3% at n = 2,048), while the signed accounting assumed route U's biased accumulator (γ ≈ 0.89%) | Coordinator with the red team; a Lean worker | The memo is `internal/pouw/new-crypto/route-u-checkpoints.md`. It proposes C^U_t = C_t − β·𝟙·s_t, with s_t in V₀ and the final value unchanged, so every bound proved mod V₀ transfers, and TT_NCP is restated over C^U. **Decided 07:40Z: ADOPT WITH CHANGES** (red team, Phase 10). C1: kernel bytes = X + β, enforced by the gate. β is a parameter: 128 now (24 units), 129 (20 units, γ 0.823% at n = 2,048) after a SASS check. C3: five Lean places not mod V₀. The unbiased sums would cost 36 per position, γ 1.08%. Recorded in `problem-statement.md` §9 item 12, `new-crypto.md` and `kw-reference.md`, and sent to the MVP owner through the requester. **The route-U Lean** is in staging (07:43Z, `internal/pouw/new-crypto/route-u/`): 40 new pins, `check.sh` passes at 189, no existing record changed. It has `checkedU`, its identity, final value, ranges and int32 link, `TTNCP_U` with `gammaFromTTNCP_U`, and the transfer (Theorem D, causal, mixing and the A1 chain, same bounds). `A1_cost` does not transfer (one more step per word), so it is restated as `A1_cost_U`, and the red team must re-grant Theorem 1 for route-U words. **Follow-up done (09:00Z, staging, 215 pins with the package's 163):** β is a parameter, with `biasU8Iff` (u8 exactly for β ∈ {127, 128, 129} with unsigned P) and γ instances at β = 128/f = 24 and β = 129/f = 20. The word-layer floors for C^U are done (P10-2), with `ckMat` kept unbiased. The wrap reaches k = 2^16 for unsigned P (bound 29,856·k), and `#eval` matches Python at β = 128 and 129. **Integration in progress:** `A1_cost_U` moves to an assumptions module, and `A1_cost_quad_U` becomes a theorem through the generic Theorem 1 (`a1CostQuadUHolds`), with `ttNCPQuadOfA2U`. Then the red team's statement review and the MVP's pin list. **Integrated 09:21Z: 220 pins**, with `check.sh` passing. All 165 earlier records are byte-identical and no existing digest changed. `a1CostQuadUHolds` proves `A1_cost_quad_U β 2 0` through the generic Theorem 1, and `ttNCPQuadOfA2U` makes route U's quadratic chain rest on A2 alone. The MVP pin list is in `route-u/README.md` ('For the MVP'). The red team's Phase 13 statement review and the submission prose catch-up (P12-2) are running |
| From the MVP: re-certify the word-granular P's checkpoint independence at k = 1,088, 2,048 and 11,008, and its MinRank | Red team, then the coordinator | **Phase 10:** v1's independence is certified at all three k and the generators agree. But MinRank is not certified at 1,088 or 2,048 (P10-1: a word-level 2-cycle). **Decided: P v1.1** (`pword-repair2.py`), a second repair that fires only when hypothesis (c) fails. It is unchanged at 4,096 and 11,008, and changes 385 of the MVP's 1,008 values of k. Script-certified at the four k: (a) (b) (c), λ₃ = 32, MinRank 16, full independence. **Certified independently by the red team** (Phase 10b, 07:48Z): its own generator reproduces all four SHAs, and the exact ranks and λ₃ = 32 hold. The full 1,008-k sweep agrees (385 changed, at most 3 swaps). Per k in use, λ₃ and clauses 2 and 3 are still to be certified (R2) |
| IMAD.WIDE and the other unmeasured multi-output instructions on an RTX 4090 (cap USD 3, pods `vy-pous-pouw-h16*`) | GPU worker | **H_16 holds** (05:14Z): IMAD.WIDE is half-rate (32 per SM per clock), so 16 per register, and every other listed instruction is at 16 or above per register written. Runs `r20260928-050001-4bc2`, `-050222-8cbc`, `-050919-8939`; USD 0.22; pod down 05:13:43Z. The 06:00Z sweep found no PoUW pod of this campaign running. `vy-pous-pouw-fp8` (rented 05:42Z) belongs to the FP8 workstream and is active, so it was left up. IMAD.WIDE sits at the bound (16.1). The verdict relies on the TD-3 reading that no free operation reads a predicate (two-predicate writers cost 8 per predicate) |

## Genuine FP8: the lower-bound side (from 13:40Z, 28 Sep)

Daniel decided at 13:25Z that FP8 PoUW must check the genuine FP8 tensor-core matmul. The scheme lane (FP8 lane,
bc-e4a2abca) designs in `docs/pouw-fp8/design.md` §6. This lane does the lower bounds. The shared file is
`internal/pouw-fp8/genuine-fp8-interface.md`. CPU only; GPU probes under USD 0.50 need the requester's approval.

| Item | Worker | State |
|---|---|---|
| FP8 MMA classes in `M4090`; `MH100` with H_32; per-word bounds | `barrier` (bc-38543e95) | Started 13:40Z |
| Emulation routes (int8/int4 grids, FP8 with FP16 accumulate, HMMA, FFMA, mixtures), bit-exact against `verity.ml.tc` and priced per word on the 4090 and the H100 | Emulation worker (bc-6f77176a) | Started 13:40Z; `internal/pouw-fp8/lower-bound/` |
| Red team: `design.md` §6 (TT_FP8_NE3), the structural point, and H_32 on the H100 | Red team (Phase 16) | Started 13:40Z |

**Scope (Daniel, 13:46Z):** 4,096+ shapes only, and γ < 1% is firm. The live candidate is NE3, at 0.938% for 4,096³ (conditional on TT_FP8_NE3(0.25%), with forming at 96 per element), which leaves 0.062 points of slack.

**The structural point** (coordinator, 13:40Z):
- A dimension bound gives at most c per checked word, where c is the cheapest price per register written.
- On the 4090, c = 16 (8 on the FP32 pipe) against an honest 64 per FP8 FP32-accumulate atom word. So a non-emulability
  assumption must carry a factor of 4.
- On the H100 (datasheet), every register writer costs 32 or more and a k32 FP8 atom word costs 32. So the bound can be
  tight with no A1 analogue.
- The FP8 problem statement's default 11 limits adversaries to 4090s. Changing that is Daniel's call.

**Pivot to H100 first (Daniel, 13:50Z).**
- *Why:* the scheme lane's C-1 falls on the 4090. A common-grid route costs 48 against an honest 72, and the admission
  obstruction is decisive.
- *C-2 (H100):* an honest 64 per I-S step, against at least 96 for common-grid emulation under H_32. But forming at 96
  per element per side gives γ = 1.405% at 4,096³.
- *Priorities:*
  1. `MH100` and the H_32 bound (`barrier`), with a GPU probe plan for H_32. The plan is being drafted by the GPU worker,
     CPU only, and the run needs the requester's approval.
  2. The emulation worker reprices on the H100 at 4,096³ and above.
  3. The red team attacks the H100 route: sub-32 writers, and forming shortcuts.
- *What forming has to reach:* at most about 62 units per element per side at γ₀ = 1/400, or about 83 if the H100 bound
  is a theorem (γ₀ → 0). The alternative is crediting forming, which is Daniel's call.

**Red team, Phase 16 (14:25Z):**
- C-1 (NE3, 4090) **falls** (X-NE3-1): alignment-dropped products let an int8 IMMA plus FFMA route cost 48 against 72.
- C-2's credited arithmetic is 6mkn (X-C2-1). So γ(4,096³) = 1.023% at 96 forming, and forming must be at most 93 per
  side at γ₀ = 1/400.
- H_32 has **zero slack** (X-H32-1): a legacy k8 HMMA writes I on sparse legal slices, a 0.25–1.3% saving per slice.
- C-3's bitwise dither is impossible within 1 ulp (X-C3-1).
- *Phase 17:* X-H32-1 against C-2's noise, the other sub-32 routes (sparse `wgmma`, b1, memory-side reductions), B's
  amortization, and forming shortcuts.

**14:45Z.**
- *MH100 in Lean* (`barrier`; 254 pins; no existing record changed):
  - `perWordMH100`: under H32, at least 32 per target independent mod V, tight via `honestSplitK100`;
  - `ceiling4090`: at most 16 per word on the 4090, which is 25% of an FP8 atom word.
- *Track D:* its own D-1 falls. The one-spike input gives `DenseLiveness` probability zero, and the Track B witness makes
  9.375% of C-2's core words salt-independent. Pasted into §2.1.D; Phase 17 verifies both against C-2 and prices the
  |code| ≥ 3 plus >8-vector repair.
- *Next in Lean:* a W1-faithful `MH100w`, with no free arithmetic, only moves and copies. Its target is
  `distinctWritesMH100`: at least 32 per distinct non-free target word, needing no linear independence, with every R_τ
  counting.
  - The scheme obligation then becomes `DistinctLive(ε)`: few free or duplicate target words for every legal input.
- *The H_32 probe plan* is in interface §1.1 (about 10 minutes on one H100 SXM, under USD 0.50). It goes to the
  requester for approval together with the GPU worker's plan.

**14:52Z: the cost model, first version** (interface §1.1–§1.3).
- *4090:* at most 16 per word is provable, against an honest 64. Routes exist at 40, 24 and 32, so it needs a factor-4
  non-emulability assumption.
- *H100:* every dense route costs at least 64 against an honest 32. The only sub-honest routes are free words, and
  ≤ 8-live-k slices if the `mma.sync` clause fails. So H100 reduces to H32, which needs measuring, plus
  `DistinctLive(ε)`. The emulation worker's files are in `internal/pouw-fp8/lower-bound/`.

**15:38Z.**
- *`distinctWritesMH100` proved* (263 pins). The H100 per-word statement reduces to H32 plus `DistinctLive(ε = γ₀)`
  plus the model gaps.
- *The H100 probe* (Round 7, USD 0.41; pod terminated at 15:18:24Z):
  - H32 holds per class with c = 32 (`wgmma` at N ≥ 64), and legacy k8 is at 34.0;
  - m64n8k32 runs at 22% of peak;
  - canonical NaN holds;
  - **but `wgmma` runs at full rate beside INT, half2 or F2FP work (26 per register in mixes), so additive W1 isn't
    time**, and the FP32 add measures 33.5.
- *For Daniel:* keep additive W1, or move to a max-over-pipes W1 on the H100. The latter helps honest forming but needs
  a CUDA-core non-emulability floor.

**15:52Z:** the W1 time-model option note is `docs/pouw/w1-time-model.md`. It recommends keeping additive W1, and revisiting max-over-pipes only with a proved ALU floor and a fixed R-word treatment. Round 8 follow-up probe approved (USD 0.35, 15:55Z).
**15:50Z: D-2 falls at 4,096³** (the D-2 strike). Its trigger can't be computed exactly for less than x ≈ 115–172 (budget 95); the floor doesn't count under 14-bit normalization; and identical weight columns make 7 of every 8 I words copies (X-D2-5, which is general). At 8,192³ it survives only with casts at 32 per instruction, but Round 7 measured F2FP at 66.7, so it fails there too unless the casts move off F2FP.

**16:50Z:**
- *GPU:* Round 8 done (USD 0.21; about USD 1.63 over eight rounds). The loop-free prices are FADD 32, F2FP 64 per
  instruction, legacy k8 32 and half2 36. Mixes reach 21.45 per register, so H32 holds per class only.
- *Lean:* 276 pins. Phase 18's citation fixes are in (`distinctWritesPacked`, `FragLanes`, `distinctWritesMeasured`),
  and F18-6 (a witness on the pinned atom) is open.
- *Running:* Phase 17d and 17e (the cast rule, exemption, and the final verdict), the D-3m strike, and the Round 8 price
  table in Lean.
- *Pending review:* `FragLanes` and the 4 new pins go to the red team after 17e.

**17:18Z: the consolidated genuine-FP8 verdict** (red team, Phase 17e).
- **Only D-3m (Y16 route) at 16,384³, r = 1, clears: 0.968%**, a 4.4% margin in units. Nothing clears at 8,192³ (the
  structural floor is 1.024% at r = 1, and X-D3-3 bars r ≥ 2) or at 4,096³.
- *Conditions:*
  - Round 9 prices: FADD beside `wgmma` at most 32.02, HADD2.F32 at most 41.4, the f16 pack, HMNMX2, the decode;
  - two §0 rulings for Daniel: Y16 as the unit's input, and a free offline FP16 weight copy;
  - quality at 54 windows (one-sided 95%) or 107 (99%) on the deployed schedule;
  - `DistinctLive` re-checked with D-3m's law.
- *Exemption:* sound only as an accounting identity. The formal reading is "outside W_ref".

**17:23Z:** Round 9 is on hold, pending Daniel's choice (relax a budget, keep researching quality-preserving noise, or pause genuine FP8). Phase 18b is running.

**19:59Z: DistinctLive(0) for H-1 in Lean** (Daniel). Plan: `internal/pouw-fp8/lean-atom-plan.md`. A dedicated Lean worker (bc-5382063c) is on M1, a bit-exact `HOPPER_E4M3_K32` with conformance. Red-team gates R1 (model) and R2 (statement) come before the proof goes deep. The target is X_q; Y16 is a comparison row.

**20:31–20:58Z: Daniel's rulings.**
- No extra weight copies: weights are decoded from FP8, and a per-weight amplitude table counts as a copy.
- Nonstandard deployment requirements are rulings, never defaults.
- The shape frontier is 2,048, 4,096, 8,192, 16,384 and 32,768; 65,536 is dropped.
- The requester set the default weight side (21:00Z): no amplitude table and no rms′ cache. The rms′ cache (2 bytes per
  column) is a ruling for Daniel.

**21:20Z: Round 10 done, and the frontier re-priced.**
- **Round 10** (one H100 SXM; about USD 0.15 of 0.45; about USD 2.04 over ten rounds; pod `89bkpuip2uew2v` terminated at
  20:53:03Z, 404 confirmed; `internal/pouw/gpu-constants.md` §16):
  - FADD's class price is **32.00** for loops of at most 390 instructions. Round 8–9's 32.11 was instruction fetch.
  - Measured under ptxas 12.9: `VHMNMX` 66.50, the PRMT-free cast 32.3 per code, `UNPACK_B` 32.1 per code.
  - Track C is negative: 55.44 per add word, above 53.18, so no shape gets under 5×.
- **Frontier at Round 10's prices** (strike; interface §1.4). Each figure is γ at 32.00, then the threshold:
  - The target, #295's D-3s M2 at 16,384³, is **0.957% (32.028)**. It clears only if the honest loop gets under the knee
    with bank-clean SASS; the loop as built pays 32.05, giving 1.034%.
  - H-1 under the §3.1 map is **0.765% (32.153)**, conditional on F19-2.
  - H-1 under `form_h1` exactly is 1.035% and fails.
  - Nothing clears below 16,384³. Everything clears at 32,768³.
- **H-1's forming kernel** is built, bit-exact on the emulator and priced from 12.9 SASS (§15.9): 340.2 per element
  under the §3.1 map and 519.4 under `form_h1`. So F19-4, which map is pinned, decides H-1. Track H is asked to pin the
  §3.1 map and Y16's intermediate precision.
- **Running:**
  - the D-3s honest-loop-under-the-knee variants, staged CPU-only for Round 11 (bc-f2500633);
  - the RunPod sweep of `vy-pous*` / `vy-pouw*` pods and Round 10's billed spend (bc-75373df6), after which root gets
    the done note;
  - the Lean worker's M1 (bc-5382063c).
- **Round 11** (the `h1` series plus the D-3s loop rows; about USD 0.15–0.20, cap ≤ 0.45) goes to root only after
  Track H's F19-2 repair lands.
- The overnight items above (Theorem D's fixes and signature, `m1Wref`, the route-U recount, MinRank, lifting, A1) were
  closed by 13:27Z. Nothing remains to relay.

**22:00Z sweep.**
- **Pods:** the only `vy-pous*` / `vy-pouw*` pod is `vy-pous-band-e2e` (L40S, $1.09/h, up since 21:55Z). It is root's
  2132Z-approved band-codec run (60 min, $1.50 cap), so it was left running. No PoUW pod is up.
- **Round 10:** RunPod billed $0.1484, about $2.04 over ten rounds. The done note is with root (notes f35d85ce).
- **#295 reproduces the `round10` frontier** in all 40 D-3 cells.
- **The centre HFMA2 is an open pricing choice.** The honest split form (one immediate, two register sources) is
  untimed. At 36 per register the target is 0.929% (32.046), and 1.006% as built. Round 11 times that form.

**00:00Z sweep.**
- **Pods:** no `vy-pous*` / `vy-pouw*` pod is running (4 pods on the account, none of them PoUW). The band run's pod is gone. It overran its cap by $0.50 because its guard's VM was suspended during the usage-limit outage.
- **Round 11's guard is changed:** a dead-man timer that starts first on the pod, plus root's fleet guard on its control host. Both go in the root request.
- **Work resumed after the 22:32Z usage-limit outage:** Round 11's restage (H-1T, the D-3s and Track C rows, H100 FP8 captures, and the SHAKE256 / SHA-256-tree microbenchmarks for audit A6); Phase 19b and the strike on H-1T; the frontier fold-in plus A6's hashing prices; Gate R1; the Lean M2 plan.
- **New:** the red team on cheaper transcript bindings (a per-tile digest, fold-then-hash).
- **H-1TSM is NO-GO** (Track D, compiled).
- The overnight items (Theorem D, MinRank, lifting, A1, `m1Wref`, the route-U recount) stay closed.

**00:40Z sweep.**
- **Pods:** no `vy-pous*` / `vy-pouw*` pod is running.
- **H-1T:** the strike's verdict is NO-GO at 8,192³ and below, and CONDITIONAL GO at 16,384³ and 32,768³.
  - The conditions: `DistinctLiveH1T` stays Assumed until Lean lands, and needs a multi-slice argument (X-H1T-S5, also the Lean worker's M2-1). Salt-selected routing is priced at ≥ 32, which Round 11 times with SEL, SHFL and LDS.
  - The branching gap is about 3× what Track H reported.
  - Phase 19b is still out, so there is no consolidated verdict yet.
- **A6, transcript hashing:** the note is `docs/pouw-fp8/fp8-hashing-decision.md`, a heads-up for Daniel. Its recommendation is to hold until the scout's section lands.
  - At 8,192³: SHAKE256 per word 1,527× / 1,126×; a cheaper hash about 621× / 458×; the fold under `FoldForcesWrites` about 42× / 31×. None is inside 5×.
  - γ′ is small only by dilution; a binding about 1% cheaper than the reference price breaks it.
  - Sampled proofs' own commitment is struck as a binding (circuit design §5). Its tile, circuit and draw recommendations are under red-team review.
- **Lean:** Gate R1 passed with one condition, H100 captures C1 and C4 in Round 11. The M2 plan against `DistinctLiveH1T` is written. The cheaper `check.sh` (about 7–8 min) is being applied, with R1 as the named statement reviewer.
- **Round 11:** restaging with H-1T, the D-3s and Track C rows, captures, the hash microbenchmarks, SEL/SHFL/LDS, and a pod-side dead-man guard plus root's fleet guard. The root request follows the H-1T verdict.
- The overnight items from 27–28 Sep stay closed.

**01:20Z sweep.**
- **Pods:** no `vy-pous*` / `vy-pouw*` pod is running.
- **H-1T is consolidated** (`internal/pouw-fp8/redteam-h1.md`): NO-GO at 8,192³ and below; CONDITIONAL GO at 16,384³ (0.75% / 0.50%) and 32,768³ (0.50% / 0.25%). Both reviews agree, and function level holds.
  - There are seven conditions. One is a tiling ruling for Daniel: B′ pre-tiled at +10.3% weight memory, or a loader that fails 16,384³.
  - The budgeted P2′ gate is not adopted.
- **Lean:** the cheaper `check.sh` is applied (about 8 min, from 22), and R1 is reviewing the two changed records. M2 has started on `DistinctLiveH1T` with R2's 9 changes.
- **Sampled proofs:** the red team accepts the circuit design's three recommendations with changes.
  - Its draw bound holds under H1–H5.
  - H4 fails on real workloads, so blocks must be drawn with replacement.
  - FP8 exact verification is about 27 core-hours per 70B window.
- **A6:** the scout's three CPU tests are running. The FP8 hashing note holds until they're in.
- **Round 11:** the restage is still running. It goes to root once it lands, since the H-1T verdict is in.
- The 27–28 Sep overnight items stay closed.

**01:21Z: Daniel's H-1T rulings.**
- **B′'s tiling is option (a):** stored once, pre-tiled with its tag rows (+10.3% weight memory, a one-time re-layout), only when FP8 PoUW is switched on and never as a default. The byte-realigning loader is dropped.
- **The optional β = 1% registration gate is not adopted,** as both reviews advised.
- Recorded in `internal/pouw-fp8/genuine-fp8-interface.md` §0 and `redteam-h1.md` condition 6. Track H and the FP8 lane are asked to record them in their docs.

**01:37Z: Daniel's ruling on A6 (FP8 transcript binding): choice C.**
- There is no FP8 binding for now. FP8 PoUW stays unbound research, and A6 stays open.
- B's next steps run on CPU: the combined-variant test (tensor-core accumulation promoted every 4 slices, plus the integer mix), and the red-team pass on `FoldForcesWrites`, including the mix-crediting question. Round 11's capture C2 is within its cap.
- Both come back to Daniel when they land. The note is `docs/pouw-fp8/fp8-hashing-decision.md`.

**02:00Z sweep.**
- **Pods:** no `vy-pous*` / `vy-pouw*` pod is running.
- **Decided since 01:20Z:**
  - B′ is pre-tiled for H-1T, only when FP8 PoUW is on, and the β = 1% gate is not adopted (01:21Z).
  - A6 is choice C, no FP8 binding for now (01:37Z).
- **Running, CPU only:**
  - the B combined-variant test (scout);
  - the red-team pass on `FoldForcesWrites` for the integer mix, including mix crediting;
  - M2 on `DistinctLiveH1T` (Lean worker). Queued for it: the audit import of `H1T.lean`, pinning L5, and §12 marked granted;
  - the red team's re-review of the rewritten sampled-proofs design (layout A, the proving-cost and noise-size figures).
- **Lean:** R1 granted the two `check.sh` records and corrected F6 (pin L5).
- **Round 11:** restaging, last commit 29ba8b6 at 01:52Z. It goes to root when it lands, with a dead-man timer that starts first on the pod plus root's fleet guard.
- The 27–28 Sep overnight items stay closed.

**02:40Z sweep.**
- **Pods:** no PoUW pod was found by this sweep's check (see the reply).
- **A6, path B: both results are in** (`docs/pouw-fp8/fp8-hashing-decision.md`, "B's results").
  - **The combined variant** (H-1T, tensor-core accumulation with an FP32 add every 4 slices, and the integer mix) runs at 2.8× in time (3.8× at the measured tensor share) and 5.56× by instruction count at 8,192³.
  - **γ:** 0.94% (8,192³) and 0.53% (16,384³) only if the mix is credited at its reference price. It is about 26% at the provable floor and about 51% uncredited.
  - **`FoldForcesWrites`** is broken as stated and repaired by a verifier rule, which leaves it plausible but unproven.
  - **For Daniel:** credit the mix or not. The recommendation is to keep C and run capture C2 in Round 11 regardless.
- **Sampled proofs:** D3–D5 are confirmed with conditions. The seed-expansion batch (ncp-v2 tile-local form, +45% against "unchanged", `Q_nested_instances`) is with the layout-A red team, and §9's FP8 weight-noise caveat is with the FP8 red team.
- **Round 11:** still restaging. **Lean:** M2 is running.
- The 27–28 Sep overnight items stay closed.

**03:20Z sweep.**
- **Pods:** one `vy-pous*` pod is running, `vy-pous-checks` ($0.64/h, since 02:50Z). It is not this lane's; it is guarded at $3 until 05:00Z per root, so it was left running.
- **Round 11:** approved by root (03:02Z), with the fleet guard armed (03:05Z). It is launching now with the pod-side dead-man timer.
- **Sampled proofs:** the two-level key for NCP-INT's E₁ is under the layout-A red team's review, and §12 (strip generation as proof units, Daniel's direction) is queued behind it.
- **Lean:** M2 is in (16 pins, 310 total), under statement review, and the worker has moved on to M3 and M4a.
- The 27–28 Sep overnight items stay closed.

**04:00Z sweep.**
- **Round 11 is done:** about $0.41 of $0.45 over two pods (the first hit its age limit during the 12.9 builds), both terminated with 404 confirmed, and the done note is with root. That is about $2.45 over eleven rounds. `internal/pouw/gpu-constants.md` §18 has the results.
  - **H100 FP8 captures:** all 4.9M words match the reference model, which closes the Lean model's silicon condition.
  - **H-1T forming** is 260.75 per element, measured.
  - **The D-3s honest step clears 5× on one run** (52.67 per add word, against 52.73), inside the run spread.
  - **The centre is priced `imm`.** SEL, SHFL and LDS are ≥ 32, and predicated-off instructions still cost a slot.
  - **Hashes:** SHAKE256 2,291 units per byte, TurboSHAKE128 826, SHA-256 1,357.
  - **The H-1T step didn't launch** (a harness bug); re-timing needs a new request.
- **Re-pricing at Round 11's values is running:** the frontier, A6's rows and B's rows. Then the A6 note is refreshed.
- **Sampled proofs:** the two-level key for NCP-INT is recommended only with the node-unit partition, since Daniel's 03:03Z ruling removes the recompute exception. §12's theorem and §12.5's width rule are under review.
- **Lean:** M2's 16 pins are granted, and M3/M4a are running.
- **Pods:** see the reply. The 27–28 Sep overnight items stay closed.

**04:40Z sweep.**
- **Pods:** no `vy-pous*` / `vy-pouw*` pod is running.
- **Round 12** (the H-1T step only, for its measured real-time slowdown):
  - root approved it at 04:32Z: $0.20, a pod maximum of about 0.05 h, the dead-man timer at creation + 3.0 min, start 04:30–05:30Z, and no third attempt if the kernel still fails;
  - the research coordinator armed the fleet guard at 04:30:51Z (pid 810209, deadline 05:40Z);
  - the staging (prebuilt 12.9 cubin, 0ac6118) is finishing, and it launches when that's done.
- **Lean:** M3 and M4a are in (321 pins). M4b is carried as the named Prop `H1TRunningWords`, which is equivalent to `DistinctLiveH1T` and covers only the hard cases O1 and O2. Its statement review is queued.
- **Sampled proofs:** the §12.2 theorem is confirmed with conditions, and its Lean package (21 pins) is under statement review. The `ncp-z` review finishes as evidence, and the designer's no-recompute comparison ((a) recommended, (c) the upgrade) is queued.
- **#295** is re-pinned at Round 11 prices. D-3s's short loop clears 5× only from 16,384³ up.
- The 27–28 Sep overnight items stay closed.

**05:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, per the 05:18Z sweep. The balance is $272.48, with the account at $3.14/h.
- **Round 12 is done:** H-1T's measured slowdown is **3.99× at 8,192³ and 3.97× at 16,384³**, inside Daniel's 3–5× before hashing. It cost about $0.10, about $2.55 over twelve rounds. Round 11 billed $0.4121.
- **The headline at Round 11's prices** (corrected 29 Sep per [hashing accounting](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/hashing-accounting.md): the hash-free slowdowns have no binding, so they carry no γ; each γ holds only with a per-word binding, shown here with TurboSHAKE128 at Round 11's measured rate):
  - NCP-FP8: unbound 5.02× at 8,192³ and 4.98× at 16,384³, no γ. Bound: 625×, with γ 1.68% and **0.98%**.
  - H-1T: unbound 3.99× at 8,192³ and 3.97× at 16,384³, no γ. Bound: 461× and 460×, with γ 1.15% and **0.71%**.
  - F1 is met: all 4.9M captured words match.
- **Lean:** M3/M4a are granted (321 pins, `H1TRunningWords` granted as a statement), and the accountable-compute package's 21 pins are granted. Next: M4b with a column-aware `Hard`, and `TTH1T`. The influence-cap package (12 pins) is under statement review for root's merge.
- **Sampled proofs:** the no-recompute comparison says keep (a), with (c) for NCP-INT only. **PR #364** (the NCP-INT circuit) is under the layout-A red team's build review.
- The 27–28 Sep overnight items stay closed.

**06:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Statement reviews:** the influence-cap package's 12 pins are GRANTED (Phase 19g; bc-89770364 is the named reviewer for root's merge). Its non-vacuity witness is being saved into the package, and the extraction worker (bc-e7e2bf3a) will pin it and name `AnchorsSound₂`, with a short re-grant at the PR head.
- **PR #364** (the NCP-INT circuit) is **GO WITH FIXES.** The anchored inputs need real anchors, Y is built per call instead of per run, and the verifier must build the Program itself. No Lean statement changes.
- **PR #362** (law `work`): its closure seam and f_s floor are being checked at root's new head, with C1 fixed.
- **Lean M4b** (a column-aware `Hard`) and `TTH1T` are running.
- **Notes rule** (root, 0517Z): no generated outputs in `research-notes`; cite `art:<id>` from the evidence store.
- The 27–28 Sep overnight items stay closed.

**06:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (see the reply for the count). **Round 12 billed $0.0970;** Rounds 11 and 12 together $0.5091, about $2.55 over twelve rounds.
- **PR #362** (law `work`) at `fb1ab521`: GO as a tile-draw law, and C1 is met. The closure seam doesn't meet §12 (it needs a pinned closure theorem over `biUnion`), and the f_s follow-up doesn't exist yet.
- **Lean:** M4b is done (the column-aware `Hard`), and `TTH1T` is stated as a named Prop for layout A (323 pins). Both are under statement review (Phase 19h).
- **The influence package's re-grant** at PRs #375, #378 and #379 is queued for the same reviewer. The witness is saved.
- The 27–28 Sep overnight items stay closed.

**07:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Statement reviews:** Phase 19h granted M4b and the narrowed `H1TRunningWords`, but not `TTH1T` as stated. The Lean worker is fixing its quantifier (X-M4-4). The influence re-grant at #375, #378 and #379 (now `fa4fb58e`) is running.
- **PR #364:** GO WITH FIXES at 919d2a72; a delta review at its new head `df4a2496` is running. **PR #380** (the NCP-FP8 circuit) is queued next.
- The 27–28 Sep overnight items stay closed.

**08:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (see the reply).
- **Statement reviews:** the influence re-grant is done; every statement is GRANTED at #375 `de831e06`, #378 `46b8faf9` and #379 `fa4fb58e`. Its witnesses are saved in `internal/pouw/influence-witnesses/` for the extraction worker. The `TTH1T` fix (a tiling domain at r = c = 16) and the X-M4-1/2 narrowings are under re-grant (Phase 19j).
- **PR #364** at `df4a2496`: still GO WITH FIXES. No circuit fix has landed yet, and there is a new medium finding: the per-call budget uses the window's K. **PR #380** (the NCP-FP8 circuit) is under build review.
- The 27–28 Sep overnight items stay closed.

**08:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Lean:** Phase 19j granted the restated `TTH1T` (layout A, r = c = 16), the narrowed `H1TRunningWords` and five pins. #390's C1 (closure not reflexive) also affects our accountable-compute package at the generic level; the Lean worker is patching it, and the re-grant then follows, then #392's witness pins.
- **PR #380** (the NCP-FP8 circuit) is GO WITH FIXES at `7522375d`. The id inputs are free, a weight is recomputed across calls, and the proving cost is about 2× §9's.
- The 27–28 Sep overnight items stay closed.

**09:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Lean:** the C1 closure patch is in `pouw-accountable-compute` (form (a): τ with `∀ t, τ t ∈ cl t`; five records changed by binders; four new pins including the X-AC-6 witness; 25 pins). It is under re-grant (Phase 19k), and #392's witness pins (Phase 19l) follow. Phase 19j's doc fixes are applied in the H-1T package with no record change.
- The 27–28 Sep overnight items stay closed.

**10:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Closed:** the accountable-compute C1 patch (Phases 19k and 19m: 28 pins, all granted, with the Layout forms to cite); #392's witness pins (19l, granted); `TTH1T` (19j, granted).
- **Running:** the Lean worker's attack on `H1TRunningWords` (⇔ `DistinctLiveH1T`), CPU only. A proof would take H-1T at 8,192³ from γ 1.15% to about 0.90%.
- The 27–28 Sep overnight items stay closed.

**10:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **#402** (`stratified_miss_eq_greedy`) is GRANTED (Phase 19n).
- **Running:** the Lean worker's attack on `H1TRunningWords`.
- The 27–28 Sep overnight items stay closed.

**11:20Z sweep.**
- **Pods:** one, `vy-pouw-mvp-qwen05` (`xaimob2tpe6z6t`, $0.74/h, up since 11:03Z, GPU 4%). It is the MVP lane's `ncp-v2` Qwen2.5-0.5B run for #389, claimed under root's 1102Z budget line ($0.80 cap, 1 pod-hour, a 60-minute pod-side timer, expiring 18:00Z), so it was left running.
- **`H1TRunningWords` is blocked** at `H1TCrossLate` (`internal/pouw-fp8/h1t-running-words-blocker.md`): block 2's −v tags cancel block 1's, leaving less than an ulp at the end of block 2. There is no counterexample (worst equality probability 0.337), and γ₀ = 1/400 stays.
- **Two routes are running, CPU only:** the Lean worker on the finite two-slice `H1TCrossLate`, and a scoping worker on independent block-2 tags (`h1t-independent-tags-scope.md`).
- The 27–28 Sep overnight items stay closed.

**12:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`. The MVP lane's `vy-pouw-mvp-qwen05` has finished and is gone.
- **Running:**
  - the delta reviews of #364 at `0d550d7a` (its check pod is waiting) and #380 at `8c488c72`;
  - the statement review of #408 (the executable subset sampler);
  - the two `H1TRunningWords` routes (the finite two-slice lemma, and the independent-tags scope).
- The 27–28 Sep overnight items stay closed.

**12:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (see the reply).
- **#408** (the executable subset sampler) is GRANTED (Phase 19o); it needs a re-merge on `main` `0c444ee2`.
- **#364** at `0d550d7a` and **#380** at `8c488c72` are both GO WITH FIXES. The fixes are real, but they opened X-SPC-95/101 (the weight link) and X-SPC-96 (the same tiles per call).
- **A candidate H-1T scheme with independent block-2 tags** is worth doing, per the scope, and adopted-with-changes by Track H with the folded epilogue: γ 1.118% (γ₀ = 1/400) or 0.870% (γ₀ = 0) at 8,192³. Its re-checks 1–4 and the two split lemmas are running on CPU. The −v route on `H1TCrossLate` continues.
- The 27–28 Sep overnight items stay closed.

**13:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (see the reply).
- **The −v route:** `H1TCrossLate` is proved in the 512 regime (staging, unpinned, function level), and its statement review is running (Phase 19p). Still open for −v: `H1TCrossLate` outside the regime, `RnMonoChainGap` and `H1TLastSliceSplit`. γ₀ = 1/400 stays; at γ₀ = 0, X_q at 8,192³ would be 0.902% at measured prices.
- **The candidate (independent block-2 tags):** re-checks 1–4 and the split lemmas are running.
- The 27–28 Sep overnight items stay closed.

**14:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (see the reply).
- **Statement reviews:**
  - `H1TCrossLate` in the 512 regime is GRANTED (19p), but the regime is empty for k ≤ 19,430, so it doesn't help γ at 8,192³ or 16,384³. Its theorems stay in staging unless something uses them.
  - #412 (the stratified sampler chain) is GRANTED (19q); keep the count-curve pin, and pin `execStratified_escape_le`.
- **Running:**
  - the Lean worker on a k-bounded `DistinctLiveH1T` for the γ shapes (ulp ≤ 256 there);
  - the candidate scheme's re-checks and split lemmas;
  - the circuit red team's delta on #364 at `5eaff486`, then #380, #391 and #372.
- The 27–28 Sep overnight items stay closed.

**14:40Z sweep.**
- **Pods:** one, `vy-pouw-mvp-qwen05` (`x8a55gljh4moai`, $0.74/h, up since 14:21Z, GPU 0%, CPU 7%). It is the MVP lane's #389 pod pair, under root's 1305Z top-up ($1.40 cap, 1.5 pod-hours, expiring 18:00Z, with the budgets guard and a pod-side kill timer), so it was left running.
- **#364** at `5eaff486` is GO (two low findings). **#412** at `da1e703a` is signed off. #380, #391 and #372 are under review.
- **`DistinctLiveH1T`:** the k-bounded attack is blocked (small tag differences have no margin). The candidate's split lemmas reduce to `CoreSplit`, which is on the critical path for both routes and is being proved zone by zone. The range tightening |A| < 2^33 − 2^29 is under review (19r). The five regime pins are being dropped (granted, not pinned).
- The 27–28 Sep overnight items stay closed.

**15:20Z sweep.**
- **Pods:** one, `vy-pous-check364` (`opqlhejtebi6a2`, a CPU pod at $0.74/h, up since 15:18Z). It is #364's recorded check, launched after the red team's GO at `5eaff486`, under root's 1203Z budget line ($1.50 cap, 2 pod-hours, until 18:00Z). Left running.
- **Circuits:** #364 GO; #380 at `1ef54bb8` GO; #391 at `51c7cdac` GO WITH FIXES (X-SPC-110, the key unit's unopened A rows); #372 GO.
- **Lean and statements:**
  - the range tightening is accepted (19r), provided `runVal2` gets its own run bound;
  - the candidate's `CoreSplit` and the −v small-Δ `H1TCrossLate` are running;
  - the H-1T scheme decision page is `docs/pouw/h1t-scheme-decisions.md`.
- **Open fact:** which vLLM FP8 epilogue dispatch the serving path uses (swapped or unswapped), for decision 7.
- The 27–28 Sep overnight items stay closed.

**16:00Z sweep.**
- **Pods:** two, both left running.
  - `vy-pous-check364` (`zz1n4kur5wxz0o`, $0.44/h): #364's recorded check, under root's 1203Z line ($1.50, 2 pod-hours, until 18:00Z).
  - `vy-pouw-mvp-qwen05` (`zqmxnh75tpd2j9`, $0.74/h): the MVP lane's #389 pair, under root's 1305Z top-up ($1.40, 1.5 pod-hours, until 18:00Z).
  - Both are relaunches under their budget lines, which the budgets guard enforces.
- **Decision 7** is corrected: the served FP8 epilogue order is swapped, row scale first, under batch-invariant mode. Both FP8 circuits now follow it.
- **Circuits:** the final delta (#391, #380, #372) is under review; the new heads (#364 `50c44582`, #380 `30a63b5d`, #391 `c8f671b3`, with X-SPC-105 option B floors) are queued behind it.
- The 27–28 Sep overnight items stay closed.

**16:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`. The check364 and qwen05 pods have finished; their budget lines run until 18:00Z.
- **Circuits:** all four PRs are GO at #391 `e36c2953`, #380 `31822339`, #372 `f1dda3ff` and #364 `08a7b3f6`. The X-SPC-105 floors and the X-SPC-107 key-context check at the next heads are under review. The admission fix (the draw takes `Ledger.admit`) is coming with the `main` `9ac48ce8` merge.
- **`DistinctLiveH1T` (−v):** small-Δ `H1TCrossLate` reduces to `TagStaircaseSplit` (a sibling of `CoreSplit`) plus the binade windows. **One shared covering proof** is the priority, then the windows. The tuple restriction is deferred.
- The 27–28 Sep overnight items stay closed.

**17:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
- **Circuits:** the provisional GO at the `50c44582` batch (X-SPC-105 fixed: escape 2^−40.30). The final heads (#364 `7b1ba73f`, #380 `1abee1bb`, #391 `56fd77b2`, #372 `f1dda3ff`, with the X-SPC-107 admission fix) are under review.
- **`DistinctLiveH1T`:** the shared covering proof (`CoreSplit` and `TagStaircaseSplit`) and the binade windows are running.
- The 27–28 Sep overnight items stay closed.

**17:32Z: Daniel deferred every pending decision to the recommended defaults.**
- **H-1T:** the scheme's decisions 1–7 are at their defaults. −v is primary, the independent-tags candidate (with the folded epilogue) is the fallback, and there is no H100 re-timing. Dequantisation uses the served, row-first order.
- **A6:** path B is closed, since the integer mix is not credited.
- **Cost model:** additive W1 stays; no rms′ cache; Y16 is not an input boundary; FP16 forming is accepted, pinned.
- **The tuple restriction** stays deferred.
- The records are in §0 of the interface file and in each owning doc.

**18:00Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`. The 18:00Z budget lines for check364 and qwen05 have expired.
- **Decisions:** all applied at their defaults (17:32Z). Track H is asked to mark the amax/416 headroom FP8-PoUW-only in the H-1T spec (A15).
- **Running:** the circuit red team on the final heads (#364 `7b1ba73f`, #380 `1abee1bb`, #391 `56fd77b2`, #372 `f1dda3ff`); the shared covering proof (`CoreSplit` and `TagStaircaseSplit`) and the binade windows.
- The 27–28 Sep overnight items stay closed.

**18:40Z sweep.**
- **Pods:** one, `vy-pouw-mvp-qwen05` (`68f2nv1bcg74r0`, $0.74/h, up since 18:13Z, GPU 0%, CPU 3%, lease to 19:37Z). It is the MVP lane's #389 pair, under root's 1810Z line ($2.85 cap, 1.5 pod-hours per pod, until 22:00Z), so it was left running.
- **Circuits:** all four PRs are GO at their final heads: #364 `7b1ba73f`, #380 `1abee1bb`, #391 `56fd77b2` and #372 `f1dda3ff`. The commitment-order gap is real, and its fix is cheap: bind the receipt before the key. The red team re-rated X-SPC-119 to medium, since a prover can trigger it at `50c44582`; it is fixed at the final heads.
- **`DistinctLiveH1T` (−v):** `CoreSplit` is proved below 2^31, which covers 8192³; 16384³ needs `StraddleFree 31`. Running: the shared covering proof (`CoreCutStaircase 1024`), `StraddleFree 31` and the `runVal2` run bound; and, for the binade windows, the salt-design lemma.
- The 27–28 Sep overnight items stay closed.

**19:20Z sweep.**
- **Pods:** one, `vy-pous-check364` (`0ozta4paajti8t`, a CPU pod at $0.64/h, up since 18:42Z, 234% CPU, lease to 19:57Z). It is #364's recorded check at `7b1ba73f`, under root's 1810Z extension ($1.50 cap, 2 pod-hours, until 21:00Z). Busy, so it was left running. The qwen05 pod has finished.
- **`DistinctLiveH1T` (−v):** the binade-windows worker timed out at 18:58Z and was resumed; nothing was lost. It is testing whether §3.6's quiet-tail case is a real `H1TCrossLate` counterexample and, if not, whether two cuts per column close it. The shared covering proof, `StraddleFree 31` and `runVal2` are still running.
- **Elsewhere in the lane:** #425's merge request (the other POUS agent's) is due by 20:30Z for the fourth Lean train; #423's `Ledger` fix is confirmed; both of #427's pins are granted.
- The 27–28 Sep overnight items stay closed.

**20:00Z sweep.**
- **Pods:** one, `vy-pous-check364` (`0ozta4paajti8t`, CPU, $0.64/h, up since 18:42Z, 274% CPU). It is running #364's recorded check `r20260929-184436-17f2` at `7b1ba73f`. Everything but pytest has passed. Its lease is extended to 20:10:46Z, as far as the $1.50 line reaches. The owning POUS agent asked root at 19:49Z to raise the cap to $2.00, or else to accept the one slow test as attributed to `main`. That is root's call, so the pod was left running.
- **`DistinctLiveH1T` (−v):** no milestone. Both Lean workers are still running: the binade windows (the §3.6 counterexample search, then two cuts per column), and the shared covering proof with `StraddleFree 31` and `runVal2`.
- **Elsewhere in the lane:** the red team confirmed #425's restack at `c4499c8c` (19:50Z); it goes into train TX, which merges about 01:00Z.
- The 27–28 Sep overnight items stay closed.

**20:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
  - The budgets guard ended `vy-pous-check364` (`0ozta4paajti8t`) at 20:10Z, at its $1.50 cap ($1.51 spent). Root's raise to $2.00 came too late.
  - RC reruns #364's check at `7b1ba73f` on the CI pool after train TB, about 23:30Z. The line stays closed.
  - The owning POUS agent is launching one approved 20-minute GPU-path measurement on the qwen05 line (about $0.53 left, until 22:00Z).
- **`DistinctLiveH1T` (−v), a milestone at 20:22Z (staging, nothing pinned):**
  - **The shared covering proof is proved in its uncut form.** One zone-certificate set proves `CoreSplit` and `CoreStaircase 512`, which give `TagStaircaseSplit` at 512 and at 256.
  - **`StraddleFree 31` is proved,** so `CoreSplit` covers 16,384³.
  - **Block 2's `runVal2` run bound is proved** (Phase 19r).
  - **The cut form (`CoreCutStaircase`, `TagCutSplit`) is blocked** on certificate size, with no counterexample. It is held until the binade-windows worker's §3.6 counterexample search reports.
- **Elsewhere in the lane:** #425 at `8d630a70` is in train TX pending the red team's delta confirm.
- The 27–28 Sep overnight items stay closed.

**21:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
  - The owning POUS agent's #435 GPU-path measurement finished, bit-exact on the RTX 4090, for $0.31 across three pods; its line stands at $2.63 of $2.85.
  - Its fused-kernel request (`vy-pouw-gpu-path`, $2.45) is held by that agent until a leaf format is chosen.
  - The 4090's TurboSHAKE128-to-SHAKE256 ratio (2.51×) is close to Round 11's H100 ratio (2.77×), so the A6 note is unaffected.
- **`DistinctLiveH1T` (−v), binade windows (21:11Z):** no counterexample (§3.6's case is a proof gap), and two cuts per column suffice for the split.
  - At 8,192³ and 16,384³ a few words get no window; dropping their 1–210 of 4,096 tag settings leaves the split's slack unchanged. That keeps `H1TCrossLate`'s meaning, since one separating setting is enough.
  - **Running:** the exclusion-zone bounds and the adversarial check of the two-cut split with exclusions (bc-5382063c), and the sizing of the cut-form certificate every route needs (bc-5a715b19).
- The 27–28 Sep overnight items stay closed.

**21:55Z: cheap binding** ([cheap binding](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/cheap-binding.md), CPU only): no design within 5× total can have a counting-proved γ; the best candidate is Pearl-C (Pearl's tickets plus #311's noisy peel, pinned and checked) at about 0.0012 / 0.0006 B per MAC, 2.0× / 1.5× and γ 0.44% / 0.35% at 8,192³ / 16,384³, **conjectured** under TT_OUT(1/400) with red-team GO WITH CONDITIONS; on the 4090 the best is NCP-INT with low-byte binding at about 24×.

**22:40Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
  - A Pearl-C H100 request (`vy-pouw-pearlc`, $0.30, one SECURE H100 SXM, a dead-man timer at 5 min) was filed for the kernel lane (bc-9914c188) and the cheap-binding lane (bc-3006c44a). It waits for root's line and the fleet-guard confirmation.
  - The fused-kernel line `vy-pouw-gpu-fused` is unused so far.
- **22:07Z: Pearl-C is the deployment candidate.** H-1T (about 460× with hashing) stays as the proven fallback, and `DistinctLiveH1T` is parked with a clean state (`internal/pouw-fp8/pearl-c-lean-split.md` §4).
- **The Pearl-C Lean split is AGREED** with the cheap-binding lane (22:17Z), with five changes, adopted at 22:45Z.
  - **The FP8 lane:** `Defs.lean`, then three proofs:
    - P1, freezing under G4, which gives ρ_F;
    - P2, the clean-up chain;
    - P3, the forming credit, which gives ρ_D ≤ 1/64.
  - **The cheap-binding lane:** TT_OUT, the game, and γ. TT_OUT's statement review is with bc-22298e90.
  - **Progress:** bc-ae19a858's `Defs.lean` (the maps: encoder, noise, forming, chain) builds, with its encoder vectors checked in the kernel; P2 is in progress. The accounting names get merged in when it returns.
- The 27–28 Sep overnight items stay closed.

**23:20Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
  - **#435's fused-kernel run:** done, exact, 102× (prefill) and 136× (decode) against plain BF16 vLLM. The honest #389 row passes on the GPU. The `vy-pouw-gpu-fused` line closed at $0.46.
  - **The Pearl-C H100 request** (`vy-pouw-pearlc`, $0.30) is not launched. Its BF16 peel capture (row B1) is ready, and it waits on the kernel and cheap-binding owners' confirmation and root's line. That capture is what P2(d) waits on.
- **Pearl-C Lean (FP8 lane):**
  - **`Defs.lean` done; P2 (a)–(c) proved** (bc-ae19a858): the exact cancellation, exact BF16 products with the accumulation bounds, and liveness at in-domain degenerate inputs.
  - **Merge in one step (running):** `Defs.lean` gets the review's two conditions, and the TT_OUT files go in unmodified, with the aggregator imports, `assumptions`, `layers`, and an `exempt` for the parked H-1T `Candidate/` files.
  - **Also running:** P1, freezing under G4 (bc-5382063c); P3, the forming credit (bc-5a715b19). P3 is aligned with the forming-glue red team: it takes the forming instance and the quantizer boundary as parameters, and ρ_D ≤ 1/64 applies to `fs`.
- The 27–28 Sep overnight items stay closed.

**00:00Z sweep (30 Sep).**
- **Pods:** none named `vy-pous*` or `vy-pouw*`.
  - The Pearl-C H100 line (`vy-pouw-pearlc`) is not granted yet.
  - POUS filed a no-spend hashing-cut plan for #435 (root's 23:15Z ask).
- **Circuits:** #364 `7b1ba73f`, #423 `618c0628` and #367 are in train TW6, whose check runs about 00:45Z.
  - #380, #391 and #372 conflict with #423 and are being rebased onto it by the owning POUS agent's circuit worker. Their new heads come back to the red-team relay.
  - #389 and #435 wait for #371's fixture migration.
- **Pearl-C Lean:** all three workers are running.
  - `Freeze.lean` (P1, bc-5382063c) and `Forming.lean` (P3, bc-5a715b19) are in the store.
  - The one-step `Defs.lean` and TT_OUT merge (bc-ae19a858) is still in progress. No inbox confirmation yet.
- The 27–28 Sep overnight items stay closed.

**07:26Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (3 pods on the account). Every POUS or PoUW line in `budgets.toml` has expired.
- **Objective 3, landed since 06:40Z:**
  - **The sm_120 atom in Lean** (`Sm120`): kernel-checked on 1,600 steps with 0 mismatches, and floor-agnostic.
  - **The chain and U twins,** `rfl` to H100.
  - **P3 at the sm_120 atom** (`FormingP`): ε = 2^−18, ρ_D ≤ 1/64, and `saltDeadP`.
  - **`FreezeP` for v1** (77 theorems): confinement for groups of at most 4 atoms, and flag completeness for G > 0.
  - **The census:** no whole-tile freezing on sm_120, and no G makes aligned spikes harmless (the cap rejects them).
- **Running:**
  - v2's lone-skip flags `flagsAt P 0` and the pure-chain bound (bc-5382063c);
  - `chainAt`, the G = 0 lemma and P2 at width 26 (bc-ae19a858);
  - the Pearl-C4 FP4 atom (bc-5a715b19).
- **The rows resting on TT_OUT(1/400)** stay marked D until rev1 (bc-b58c6093).
- The 27–28 Sep overnight items stay closed.

**08:08Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (3 pods on the account). Every POUS or PoUW line in `budgets.toml` has expired.
- **Objective 3.**
  - **Landed:** `chainAt` (`rfl` to `ctChain 4`), G = 0 as the pure chain, and P2 at width 26 for every G (`PeelExactProofsP`), all by bc-ae19a858.
  - **Staged and proved** (bc-b58c6093): the TT_OUT restatements rev1 (B), v2 at 1/1,000 (B) and U-only (unrated). Their pin-update review for bc-22298e90 is being built (bc-7a7109a0).
  - **Running:**
    - v2's lone-skip flags and the pure-chain bound (bc-5382063c);
    - the Pearl-C4 FP4 atom (bc-5a715b19);
    - `TTOutFp4Sm120`, staged (bc-ae19a858).
  - **The FP4 salt-dead bound** is bc-a8466279's.
  - **The FP4-tile theorem** is bc-d9842080's.
- The 27–28 Sep overnight items stay closed.

**08:50Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (3 pods on the account). Every POUS or PoUW line in `budgets.toml` has expired.
- **Objective 3.**
  - **Landed since 08:08Z:** the Pearl-C4 FP4 atom (`Fp4`, `Fp4Chain`; 0 mismatches), and the FP4-tile theorem in Lean (bc-d9842080; 23 pins, re-review pending).
  - **The FP8-tile pins** (15, all GO) merge after the FP4-tile ones.
  - **The fourth restatement** (v2 on the chain cap) is added to the pin review.
  - **The price check:** no sm_120 statement reads `Costs.adopted` or FADD = 32. Every sm_120 instance uses `Prices.sm120`.
  - **The FP4 `saltDead`** moves to the E2M1 code (§4b), with bc-a8466279 proving it; no word-level pin.
  - **Running:**
    - v2's lone-skip flags and the pure-chain bound (bc-5382063c);
    - `TTOutFp4Sm120`, staged (bc-ae19a858);
    - the FP4 debit's soundness (bc-5a715b19);
    - the restatement pin review (bc-7a7109a0).
- The 27–28 Sep overnight items stay closed.

**09:33Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (2 pods on the account). Every POUS or PoUW line in `budgets.toml` has expired.
- **Objective 3.**
  - **Landed since 08:50Z:** v2's lone-skip flags (`pureFlagsP`, `flagsAt`) with `pureFlags_iff`, and the pure-chain bound `sm120_pure_no_identity`. `sm120_cancel_identity` refutes the theory note's product-only claims. `TTOutFp4Sm120` is staged at γ 0.71761%.
  - **The FP32 price rule:** compute at both prices and publish the larger.
  - **The restatement bundle** (bc-3006c44a, 359 pins) is with bc-22298e90. rev2 (the chain cap, the `devAt` flags fix, `devSm120v2`, and a fresh-store `check.sh`) is to be built by bc-7a7109a0.
  - **The FP4-tile pins** (36) are in re-review; the FP8-tile pins (15, GO) follow them.
  - **The price twins** are with bc-876ca543.
- The 27–28 Sep overnight items stay closed.

**10:15Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (2 pods on the account). Every POUS or PoUW line in `budgets.toml` has expired.
- **The Lean host:** 5 GB available of 15 GB, with five Lean workers. Their memory gates (9 GB free before an audit) serialize the heavy checks.
- **Objective 3.**
  - **Granted:** the FP4-tile pins (36, GO) and the FP8-tile pins (27, GO). Their merges are running (bc-3cdbf3c1).
  - **In progress:**
    - rev2 of the TT_OUT bundle (bc-7a7109a0), waiting on the `SaltDead` F2 fix (bc-5a715b19);
    - the concrete-record add-on (`DeviceSm120Gamma`), checked on top of rev2;
    - the in-loop price twins (bc-876ca543), queued after rev2;
    - P2 row additivity as the lemma `ttOutRowSeed_of_ttOut` (bc-5382063c, redirected);
    - P2 at FP4 on `peelFp4` (bc-ae19a858).
  - **The FP4 chain is not exact on D₄** (`noLoss_gap`, relayed).
- The 27–28 Sep overnight items stay closed.

**10:42Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*` (2 pods on the account). The Lean host has 5 GB available.
- **Objective 3.**
  - **Merges:** the tile merges are running. FP4-tile's 36 pins first, then the docstring swap, bundle 2 (3 pins, after its re-GO) and FP8-tile's 27.
  - **rev2** waits on the `SaltDead` F2 fix.
  - **Pearl-C4** changed four ways:
    - ρ_D is proved (`rhoDFp4At_holds`, c ≤ 90), with the dead screen at 9.5ρ;
    - `fs` = 107.34, so γ is 0.7174% (reconciling);
    - D-SS's row rejection becomes a per-screened-block debit;
    - exactness is option (b), with a per-word `ExactRun`.
  - **P2's row additivity** is the lemma `ttOutRowSeed_of_ttOut`, with the fragment argument queued behind it.
- The 27–28 Sep overnight items stay closed.

**11:32Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. There are 2 pods on the account: the control pod, and `vy-coord-pouw449-veritor-campaign`, started at 11:25:44Z and in use, so left alone.
- **The Lean host:** the host's balloon holds 8 GiB of 15.6 GB, so a 9 GB gate never opens. Four pipelines were parked on one.
  - `/home/ubuntu/lean-heavy.sh` replaces the gate: one heavy step at a time from 5.5 GB available, a watchdog below 0.8 GB, and root's priority order: tile merge, rev2, the FP4 constants, `SaltDead`, FP4 conformance.
  - **First peaks:** `lake build` drew 3,839 MB and `--update` drew 173 MB.
- **Objective 3.**
  - **Merges:** tile merge A (FP4-tile, 36 pins) has built and its records verify; `check.sh` is running. Bundle 2 (3 pins) and FP8-tile (64 pins, with `region_count_given_le`) are GO, making 393 in all.
  - **rev2** is unheld and queued second. The `SaltDead` F-line fix follows as a known delta, re-GO'd on its own.
  - **FP4 ρ_D: conditional GO.** The conditions: `screenDead` 90 with the `rhoDFp4At_ninety_eq` rename; `Fp4Skip.dead` 90; #534 merging. `PinnedScales` stays argued until `s5_stats` is pinned. D-SK is now a domain rule of TT_OUT-FP4.
  - **The price twins are unified:** one 8.38 record, the cast at 8.0, 512 pins, queued after rev2.
  - **`post-add-bound/sm120` is rated C** by the assessor (accumulate-and-merge is uncovered; no break found); bc-3006c44a is re-deriving it.
  - **Queued:** the new line `devSm120v2hot`, and `-h3`'s seed bridge with C5 in `rowseed-staging/`. `FragDraw` is stated at Λ = 100.
  - **P2 at FP4** (`peelFp4_err`, `uQ4_cancel`, `served4_salt_dependent`) is staged, and its builds are queued.
- The 27–28 Sep overnight items stay closed.

**12:08Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. The 2 pods on the account are the control pod and `vy-coord-pouw449-veritor-campaign`, which is running and in use. The new-crypto files are unchanged since the last sweep.
- **The Lean host:** the balloon now holds 4 GiB. Tile merge A's `check.sh` drew 4,768 MB and took 30.6 min, with 1,296 MB left at its lowest, so it fits under the runner.
- **Objective 3.**
  - **FP4-tile is merged:** 362 pins in the store (12:04Z). Next come bundle 2 and FP8-tile, for 393.
  - **rev2:** its build and `--update` passed locally, and its `check.sh` has held the lock since 12:03:51Z. The cloud copy of the run ([Lean: rev2 check on a cloud VM](bc-e3a069fd-68e5-56d2-8a44-df84073abb97)) continues as a cross-check.
  - **Pearl-C4:** `tt-out/fp4-sm120` is rated **D** (the base split through spike-saturated rows), and the D₄ fix is in design (bc-a8466279). The Lean work that reads D₄'s debit is held. `rcp.approx` is exact, so FP4's in-loop record is `⟨4, 21887/200, 3771/200⟩`.
- The 27–28 Sep overnight items stay closed.

**12:53Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. The 2 pods on the account are the control pod and `vy-coord-pouw449-veritor-campaign`, which is in use. The new-crypto files are unchanged.
- **The Lean host:** 8.8 GB available. rev2's `check.sh` drew 5,431 MB. The lock is held by bundle 2's `check.sh` (since 12:33Z; its build and both updates passed). Queued behind it: rev2's add-on, the two FP4 constant builds, and RowSeed's build (priority 6).
- **Objective 3.**
  - **TT_OUT rev2 is GO on its contents** (bc-22298e90, 12:48Z), after its 12:32Z pass: 366 pins, no pin record or TT_OUT hash moved. That meets condition 2 for the FP8 price twins.
  - **Owed by the rev lane:** the `SaltDead` ±11/4 delta (bounded at 1/64 of forming credit; no γ moves), the CHANGELOG, and v2-hot's chain-only `_of_ttOut` pair.
  - **The v2-hot price twins are GO** (34 pins). `devSm120v2hot`'s lemma shape is routed to the rev lane.
  - **The store** has 362 pins; bundle 2 (365) and FP8-tile (393) are next.
  - **Pearl-C4** stays D (the base split), with the D₄ fix in design.
- The 27–28 Sep overnight items stay closed.

**13:30Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. The 2 pods on the account are the control pod and `vy-coord-pouw449-veritor-campaign`, which is in use. The new-crypto files are unchanged.
- **The Lean host:** 8.6 GB available. FP8-tile's `check.sh` drew 5,278 MB.
  - The lock is held by rev2's `DeviceSm120Gamma` add-on check (since 13:08Z; its build and update passed).
  - Queued behind it: bundle 2 (priority 1), the two FP4 constant builds, and RowSeed.
- **Objective 3.**
  - **The store has 390 pins:** FP4-tile (36) and FP8-tile (28) are merged. The merger took FP8-tile before bundle 2; bundle 2's 3 pins bring it to 393.
  - **rev2 is granted** (`art:cc8cf5fe…`, 12:51Z) with the F2 caveat. The `SaltDead` delta completes the pair; the fix is not yet in the store, since it queues behind `Fp4Skip.dead` at priority 4.
  - **v2-hot:** the sizing rule is `HotSizing.publicConst 64`, shared by the record, its accounting lemma and `no-aligned-exact-region/sm120-unpromoted-hot` (routed to the rev lane).
  - **Pearl-C4:** the block scale is at `lut256`, so the record is `⟨4, 105299/1000, 9423/500⟩` (γ 0.71732% / 0.61102%, held). The base-split fix is debit-only (F1′ + F2), so only the debit-reading pins are held.
- The 27–28 Sep overnight items stay closed.

**14:05Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is left on the account, since `vy-coord-pouw449-veritor-campaign` has been stopped by its owner. The new-crypto files are unchanged.
- **The Lean host:** 8.4 GB available.
  - rev2's add-on `check.sh` passed at 13:37Z (it drew 5,444 MB). Bundle 2's `check.sh` has held the lock since 13:39Z.
  - Queued behind it: the two FP4 constant builds, rev2's `SaltDead` delta and RowSeed. rev2's v2-hot build is withdrawn for a moment while it refreshes its `HotGamma` snapshot to the re-GO'd twins.
- **Objective 3.**
  - **The store has 390 pins,** and bundle 2 brings it to 393.
  - **Merge queue:** `Fp4Skip.dead`, then the `SaltDead` fix, then M1 (rev2, the add-on, the delta, the FFMA docstrings), then M2a (the FP8 in-loop twins, FP8 chain-only, the 6 exact chain-cap pins).
  - **M2b (v2-hot)** is re-GO'd but waits on the rev lane's staged lemma (written; its build is being requeued) and a TT_OUT grant naming both prices and `publicConst 64`.
  - **The chain cap's exact in-loop values** are on `security-proofs.md`: 0.35980% / 0.35484% per unit and 0.36218% / 0.35604% per tile.
  - **Pearl-C4** stays held behind the debit-only base-split fix; its record is `lut256` at 8.376.
- The 27–28 Sep overnight items stay closed.

**14:50Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is on the account. The new-crypto files are unchanged.
- **The Lean host:** 9.9 GB available.
  - `saltdead-fix` has held the lock at priority 1 since 14:49Z. Root moved the `SaltDead` runs ahead of v2-hot and the FP4 builds.
  - Next come rev2's `SaltDead` delta (build, update, check), then v2-hot's remaining phases, `fp4-const-devicefp4` and RowSeed.
- **Objective 3.**
  - **The store has 393 pins,** and `Fp4Skip.dead` 90 landed at 14:48Z.
  - **M1** (rev2, the add-on, the `SaltDead` delta, the FFMA docstrings; 454 pins) is estimated at about 17:15Z, with **M2a** (636) in the same check if it's ready. The dry run found no conflicts.
  - **The base-split fix (F1′ + F2) is GO** at the 1.81 leaf. bc-ae19a858 writes it into the staging and rebases, and it then goes to statement review and the assessor's grant.
- The 27–28 Sep overnight items stay closed.

**15:33Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is on the account. The new-crypto files are unchanged.
- **Objective 3.**
  - **M1 was rerouted.** rev2's `SaltDead` delta failed to build on rev2's own `witness_saltLive` (old support pair). The merger's four-token fix builds all 2,419 jobs, so the delta is now five files, built and updated by the merger (15:27Z) and published for bc-22298e90 (`rev2-tile-device-bundle/saltdead-delta/`).
  - **M1's build** is next: a priority-1 sentinel holds the lock for it. RowSeed's audit, which slipped in, was stopped. The store write waits for the GO and a passing M1 check, estimated at about 16:15Z.
  - **The FP4 fix** follows the assessor's consolidated 15:18Z conditions (leaf 2.0, `c_L` 0.808 / 0.707 / 0.619 / 0.542). Its build is held until bc-ae19a858's definitions match.
  - **M2b (v2-hot, 11 pins)** is planned after M2a. It needs the statement GO and a TT_OUT grant naming both prices and `publicConst 64`, pending GPU 3. v1-hot is parked.
- The 27–28 Sep overnight items stay closed.

**16:06Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is on the account. The new-crypto files are unchanged.
- **Objective 3.**
  - **M1** (rev2 + add-on + the five-file `SaltDead` delta + the FFMA docstrings, 454 pins): its build and update passed. Its `check.sh` has run since 15:42:42Z and should finish about 16:14Z.
  - **The delta is GO** (bc-22298e90), and M1's check stands as its check. So the store write follows the check, and the one combined label follows the write.
  - **Next:** M2a (FP8 twins, chain-only, chain cap), then M2b (the GO'd v2-hot 11, after the `OperandOK` guard, the end-to-end compositions and a TT_OUT grant), then RowSeed (M3, in review), then the FP4 scale decode (M4, held for GPU 4's 17 vectors).
  - **The FP4 fix** is held until its definitions match the 15:18Z conditions (NVFP4 only).
- The 27–28 Sep overnight items stay closed.

**16:45Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is on the account. The new-crypto files are unchanged.
- **Objective 3.**
  - **M1 has landed** (16:19Z): 454 pins, with rev2, the add-on, and the five-file `SaltDead` delta with its GO. `check.sh` passed in 33.6 min.
  - **M2a** (FP8 in-loop twins, chain-only 32, chain-cap 6; store-print pins): its build and update passed, and its `check.sh` has run since 16:30Z (about 17:05Z).
  - **M2b (v2-hot)** is held on GPU 3's first-atoms finding (free-family shapes in 17 of 64 units).
  - **M3 (RowSeed)** is rebasing on the post-M1 store, with option (a) for the fragment argument (no new assumption).
  - **M4 (the FP4 scale decode)** is unheld: GPU 4's 17 words all match, with 28 `nvf4Specials` rows.
  - **The FP4 base-split fix** is staged to the 15:18Z conditions (NVFP4 only), and its rebase is unheld. Its R1-as-charge deviation is with the reviewer.
- The 27–28 Sep overnight items stay closed.

**17:30Z sweep.**
- **Pods:** none named `vy-pous*` or `vy-pouw*`, so there is no round-4 spend. Only the control pod is on the account. The new-crypto files are unchanged.
- **Objective 3.**
  - **The store has 636 pins.**
    - M1 (`art:c482fce4…`): rev2, the add-on, and the five-file `SaltDead` delta.
    - M2a (`art:0b6c342a…`): the FP8 in-loop twins, FP8 chain-only, and the exact chain cap.
    - So the FP8 headline figures cite merged theorems. The combined grant label on M1's snapshot is with bc-22298e90.
  - **The lock:**
    - The FP4 scale decode's check passed (17:26Z); it goes to `scaleDyadic` review, then merges as M4.
    - The FP4 base-split rebase holds the lock (since 17:26Z).
    - RowSeed's post-M1 build is queued.
  - **M2b (v2-hot):** bc-b58c6093's revision is with bc-22298e90 for a re-GO: a per-row `RowOK` guard and a start bound `t₀`. The write-back waits for GPU 3's amended rows × columns check and the first-atoms grant.
  - **Pearl-C4:** the base-split fix is staged to the 15:18Z conditions (NVFP4 only). Its R1-as-charge deviation is with the reviewer and the assessor.
- The 27–28 Sep overnight items stay closed.

**GitHub token broker adoption** (Daniel's approval; `lanes/pous/20260930T1725Z-handoff-from-coordinator-github-broker-rollout.md`). One line per agent, as each confirms `git ls-remote`, `gh repo view` and `token.json` `source`:
- bc-824e54a2 (PoUW FP8 coordinator): broker: source=broker 17:42Z
- bc-3cdbf3c1 (store merger): broker: source=broker 17:52:14Z
- bc-ae19a858 (FP4 Lean fix): broker: source=broker 18:53:49Z
- bc-5382063c (RowSeed): pending, at its next turn
- bc-5a715b19 (FP4 scale decode): pending, at its next turn
- bc-7a7109a0 (rev lane): pending, at its next turn

**18:14Z sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`. Nothing was terminated, and this session's RunPod spend is $0 against the $200 cap. The new-crypto files are unchanged.
- **Objective 3.**
  - **M4 (the FP4 scale decode, `scaleDyadic` GO):** its build and update passed, and its `check.sh` has run since 18:02Z (about 18:36Z). The store stays at 636 pins until the write-back, which moves only the `Pouw.PearlC.Fp4` read.
  - **The combined label is on M1's `art:c482fce4…`,** so the F2 caveat is cleared. M2a's print changes are GO.
  - **M3 (RowSeed, option (a), 28 pins, checked)** is in review. bc-22298e90 is classifying C6 `RowDrawn`, and it goes to root if it is a named assumption.
  - **M2b (v2-hot)** is re-GO'd, and held on GPU 3's rows × columns check and a grant naming W*(w).
  - **The FP4 base-split rebase** queues after M4. The pinned Python scale decode is PR #534's, identical to M4's on all 512 pairs.
- The 27–28 Sep overnight items stay closed.

**18:42Z sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **Objective 3.**
  - **M4 has landed:** the FP4 scale decode (`art:2d6d7cb4…`, 18:37Z; 636 pins; only the `Pouw.PearlC.Fp4` read moved).
  - **Merged today:** tile merges (393), M1 (rev2 + add-on + the `SaltDead` delta, with its label), M2a (the FP8 in-loop twins, chain-only, chain cap) and M4.
  - **Pending:**
    - M3 (RowSeed): the review, and the C6 classification.
    - M2b (v2-hot): GPU 3's rows × columns check, and a grant naming W*(w).
    - The FP4 base-split rebase, which holds the lock since 18:38Z; then the R1-as-charge ruling and the `tt-out/fp4-sm120` grant.
- The 27–28 Sep overnight items stay closed.

**19:26Z sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`. Nothing was terminated, and there is no round-4 spend. The new-crypto files are unchanged.
- **Objective 3.**
  - **The store:** 636 pins after M4. No merge since.
  - **The FP4 base-split fix** is being rebuilt on the post-M4 store (`fp4-const-basesplit-postm4`, holding the lock since 19:21Z after a first attempt at 19:16Z). It then goes to bc-22298e90 as an addendum to the 18:56Z review request, with the R1 ruling pending.
  - **Waiting:**
    - M3 (RowSeed): bc-22298e90's GO, and its C6 classification.
    - M2b (v2-hot): GPU 3's rows × columns check, and a grant naming W*(w).
- The 27–28 Sep overnight items stay closed.

**20:09Z sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **Objective 3.**
  - **The store:** 636 pins, with no merge since M4.
  - **The FP4 base-split fix passes on the post-M4 store,** and its addendum is with bc-22298e90. But it found **a D-NF gap:** since M4, rows with β < 0 pass D-NF and form as at |β|, including a zero-noise row at `0x80`. The protocol never produces β < 0, but the Lean domain doesn't exclude it. The fix (D-NF `v < 128` and/or `0 ≤ β`) is with bc-a8466279 and bc-22298e90, and there's no FP4 grant until it lands.
    - **Update, 1:31 PM PDT: the D-NF gap is fixed, pending review.** D-NF is now `0 ≤ β ∧ 8 ≤ (e4m3 β).val ∧ (e4m3 β).val < 128` (both fixes). It's in `pearl_c4.dnf` on #534 `e7432087` and carried into #556, with a test at β = −1/4096. The Lean pins are being restated in `RowAdmit4`/`RowRules4` (bc-ae19a858); bc-22298e90 reviews the pin statement.
    - **F2's c_L is now a pinned table:** the catalogue minimum, 0.661 / 0.579 / 0.507 / 0.408 at 8k–64k³ (the assessor, 1:00 PM PDT; #556 `b3af5481`). It is going into the same rerun.
  - **M3 (RowSeed)** waits on its GO and the C6 classification. **M2b (v2-hot)** waits on GPU 3's check and a grant naming W*(w).
- The 27–28 Sep overnight items stay closed.

**1:53 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **The Lean host:** the lock is idle. Available memory is about 5.8 GB with no Lean job running (the host's balloon), just above the runner's 5.5 GB gate.
- **Objective 3.**
  - **The store:** 636 pins, with no merge since M4.
  - **The D-NF rule is GO** (bc-22298e90). It covers the staged Lean once `RowAdmit4`, `RowRules4` and `RowRules4At` state it exactly, with `rhoDFp4At_ninety_eq` still `rfl`. bc-ae19a858 is restating them, together with the pinned c_L table (0.661 / 0.579 / 0.507 / 0.408). The diff goes to bc-22298e90.
  - **v2-hot's charged TT_OUT** is GO on its four forms, with Δ's definition held while bc-b58c6093 makes it read the unit's width.
  - **Still waiting:** M3 (RowSeed) on its GO and the C6 classification; M2b on GPU 3's check and its grant.
- The 27–28 Sep overnight items stay closed.

**2:36 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **The Lean host:** the host's balloon has grown back. About 6.1 GB is available with nothing running, and a full audit draws about 5.7 GB.
  - bc-ae19a858's D-NF rerun (`fp4-const-basesplit-dnf`) is queued with a 9 GB start threshold, and has waited since 2:14 PM PDT. That threshold is the safe one, since from 6.1 GB the watchdog would kill the audit.
  - Heavy Lean steps wait until memory frees.
- **Objective 3.**
  - **v2-hot's charged TT_OUT extension** (Δ to 65,536 deep and wide) is GO. It won't merge until two conditions are re-pinned: the width caveat (bc-b58c6093), and the provisional block tables rebuilt on bc-d9842080's audited floors. The 8,192³ GO is unchanged.
  - **The FP4 D-NF rule is GO,** pending the three definitions' restatement and the rerun above.
  - **The store:** 636 pins.
- The 27–28 Sep overnight items stay closed.

**3:05 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **The Lean host:** the balloon still holds 8 GiB, leaving about 6.1 GB available. bc-ae19a858's D-NF rerun is still queued behind its 9 GB threshold (requeued 2:59 PM PDT). No heavy step has run since 12:32 PM PDT.
- **Objective 3.**
  - **The store:** 636 pins.
  - **M2b (v2-hot):** its plan now includes the charged TT_OUT extension at the confirmed hashes. It stays held for the first-atoms grant.
  - **v2-hot's 16,384³ figures** aren't citable until GPU 3 runs 16,384-wide units.
  - **The FP4 D-NF rule is GO,** pending the rerun.
  - **M3 (RowSeed)** waits on its GO and the C6 classification.
- The 27–28 Sep overnight items stay closed.

**3:52 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; none named `vy-pous*` or `vy-pouw*`, so nothing was terminated and there is no round-4 spend. The new-crypto files are unchanged.
- **The Lean host:** the balloon still holds 8 GiB (~6.1 GB available), and there's been no heavy step since 12:32 PM PDT. bc-ae19a858 is asked to post the D-NF diff for review now, and to run the build and no-replay update within the available memory, keeping the replay behind its 9 GB threshold.
- **Objective 3:** no change. The store has 636 pins. M2b is held for the first-atoms grant. M3 waits on its GO and the C6 classification. The FP4 D-NF restatement is pending.
- The 27–28 Sep overnight items stay closed.

**4:04 PM PDT: heavy Lean moves to node 2** (root's request).
- **The FP4 D-NF replay audit** is packaged as `art:ac05a71d…` (bc-ae19a858's exact inputs, plus a portable pass test). bc-2aa33ad8 is asked in `server.md` to run it in node 2's CPU fill queue: CPUs 96–127, paused in timed windows (~4:15, 5:00, 5:45 and 6:30 PM PDT).
- **Blocked on:** node access. This lane has no key or `machines.toml` entry for `vy-nebius-2`, so bc-2aa33ad8 queues the job. Node 2 may also need elan (`leanprover/lean4:v4.34.0`) and Mathlib's cache (`5ed29652`); the job exits 2 and says so if they're missing.
- **The fallback:** bc-ae19a858's local run stays queued, for when the balloon frees.
- **M2b's build** goes the same way once its grant is in.

**4:27 PM PDT pod sweep:** only `vy-control-verity` is up; no `vy-pous*` or `vy-pouw*` pods, so none terminated. pous RunPod spend this session is $0 against the $200 cap. The env check was by name only (`RUNPOD_API_KEY`, `RUNPOD_SSH_KEY_B64` present). No reply yet from bc-2aa33ad8 on the node-2 D-NF fill job, and the local fallback is still waiting on the balloon (8 GiB held, ~6.1 GB available).

**4:42 PM PDT: the D-NF Lean packet is GO** (bc-22298e90; `internal/pouw/red-team/statement-review-fp4-dnf-rule.md`). Both open points are accepted: `c_L` = 0 past the table's edge, and −0 rejected by the byte clause. The assessor is appending the verdict to `ratings.md`. **The last step is the kernel replay on node 2,** a CPU one-shot, with its input staged for bc-2aa33ad8 at `internal/pouw/new-crypto/dnf-replay/`. Once it passes, the assessor can grant `tt-out/fp4-sm120` under F1′ + F2, and the FP4 hold lifts.

**5:19 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; no `vy-pous*` or `vy-pouw*` pods, so nothing was terminated, and pous spend is $0 against the $200 cap. The new-crypto lane files are unchanged.
- **The FP4 D-NF kernel replay** (the last step after bc-22298e90's GO) hasn't run yet.
  - The node-2 one-shot input has been staged since 4:37 PM PDT, but bc-2aa33ad8 hasn't posted since, and there are no results in `rtx-pro/fill-out/`.
  - The local fallback still waits: the balloon holds 8 GiB, leaving ~6.1 GB available.
- **Labels:** attempt 104's decode labels are on the remote. The 12:00 AM UTC sync pushed the one missing assertion; the other 180 were already there.
- **Unchanged:** the store has 636 pins; M2b is held for the first-atoms grant; M3 waits on its GO and the C6 classification.
- The 27–28 Sep overnight items stay closed.

**5:53 PM PDT sweep.**
- **Pods:** only `vy-control-verity`; no `vy-pous*` or `vy-pouw*` pods, so nothing was terminated, and pous spend is $0 against the $200 cap. The new-crypto lane files are unchanged.
- **The FP4 D-NF replay** has run on node 2 since 5:20 PM PDT (bc-2aa33ad8's one-shot, frozen during timed windows). The local fallback is stood down. A watcher preserves the result when it lands and, on a pass, takes it to the red team and the assessor for `tt-out/fp4-sm120`.
- **Goal (3) support** (due 11:40 PM PDT): bc-2aa33ad8's panel labels are local-only, so this lane pushes them.
  - A watcher syncs `panel/ov-labels/labels/` as windows 7 and 8's rows land, and checks they're on the remote.
  - The a67 canary's outputs (`fill-out/a67-canary-r20261001-004424-7b1f/`) get `research data put --preserve` once staged.
- The 27–28 Sep overnight items stay closed.

**6:04 PM PDT: the coordinator is now compute-accounting** (bc-e90634dd; Daniel, 5:52 PM PDT). Its orders are read from research-notes `lanes/accounting/` on a 30-min timer. **READY:** the goal-(3) panel-label push (the store remote is checked, the export directory is present, and the watcher is running). **BLOCKED:** replies to `lanes/accounting/`, because this VM has no research-notes write credential. They're staged in `internal/pouw-fp8/accounting-outbox/` for the advisor to mirror. **RowSeed:** C6 becomes a named assumption (Daniel's yes), and M3's review proceeds (bc-5382063c resumed).

**6:29 PM PDT: the FP4 D-NF replay passed** on node 2 (`AUDIT PASS`, 350 declarations replayed on standard axioms; the 59 records and the store's 636 unchanged; `rfl` checks pass). It is preserved as `art:9f429608…`, and the grant request for `tt-out/fp4-sm120` is in `lanes/accounting/` for the red team and the assessor. **The a67 canary** is preserved as `art:2ea3b223…` (149 files). **Pods:** only `vy-control-verity`; pous spend is $0 against the $200 cap.

**7:18 PM PDT: final pod sweep, and the hourly overnight sweep is stopped.** Only `vy-control-verity` is up, with no `vy-pous*`/`vy-pouw*` pods all evening; pous spend is $0 against the $200 cap. Under Daniel's 6:55 PM PDT migration ruling, this lane starts no new work. Its handoff and its workers' handoffs are in research-notes `lanes/accounting/`. The window-8 label push stays on until window 8's rows are pushed or the replacement takes it over.
