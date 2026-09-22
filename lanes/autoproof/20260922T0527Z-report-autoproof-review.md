---
id: r20-proof/autoproof/20260922T0527Z-report-autoproof-review
campaign: r20-proof
lane: autoproof
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/autoproof_review.md
---

# autoproof review (lane/autoproof, 2026-09-22, read-only over `/Users/danielreuter/projects/autoproof`)

Subject HEAD `aae75b30` (2026-07-16) on `cursor/split-correction-prover-a6e2`; the M/R research lives on `origin/{M1..M8,R1..R17}-claude`
and `origin/checkpoint/gpt-m10-20260711`. Every path below is relative to the autoproof checkout; `origin/X:path` means "file on that branch".
Conversion to our metric: autoproof's rho = prover s / (MACs / 6.3808e14 NVFP4 MAC/s) (`metrics/native_baseline.json`, `FOUNDATION.md` C7);
ours = prover s per 1536-MAC VU / 9.85 ps = prover s/MAC / 6.41e-15. So **overhead_ours = 4.09 x rho_autoproof** at equal prover seconds
per MAC. That equates a 5090 prover with an A100 prover and an NVFP4 relation with our BF16 one, so use it for orders of magnitude only.

## 1. What autoproof is

**Statement.** Bit-exact **NVFP4** (E2M1 elements, UE4M3 block-16 scales) GEMM as executed by the Blackwell RTX 5090
`mma.sync ... kind::mxf4nvf4 ... m16n8k64` instruction, FP32 accumulate, identity epilogue, no BF16 anywhere: `FOUNDATION.md` section 1
and section 4 ("Formats -- scope ruling 2026-07-11: NVFP4 only"; BF16 is "CANON/FLOOR control only"), `fp4-ref/src/native.rs:64-67`
(`ElementFormat::Bf16 => None`) and `:130` (`assert!(fmt != Bf16, "bf16 has no NATIVE model")`). The measured semantics ("model5",
`spec/SEMANTICS.lock.v1.json`): per instruction, 4 exact 16-term integer group dots, lossless scale application, then a five-way align-add
in which the four terms and the carried FP32 accumulator are truncated toward zero at a common lsb = max(E1-41, ilog2(acc)-35, hot ? -19 :
-inf), summed exactly, normalised RZ. Pinned on silicon 1,574,998/1,574,998 (`probes/results/probe3_*.json`, `RESEARCH_LOG.md` 2026-07-11
10:45), after the MMA-Sim single-window hypothesis was refuted (142,270 mismatches). Determinism 3,000/3,000 runs; the 6.3808e14 MAC/s
denominator is cuBLASLt's own fastest algorithm, which is already split-K=1 (determinism tax ~0%).

**Proof systems and fields.** Goldilocks throughout (a BabyBear port was priced, never built), hand-rolled: `prover/src/{field,ligero,merkle,
sha256,mle}.rs`, `cargo tree -p prover` = `serde_json` + `spec` only. Rate-1/4 Ligero over SHA-256 Merkle (128 queries), batched matmul
sumcheck for the group dots (M3), a zerocheck over 216 committed trace columns per firing with 167 LogUp lookups into three tables
(2^16 range, 64-entry shift, 128-entry UE4M3 decode) and 138 constraints (M5/M6, `origin/M6-claude:memos/M6-commitment-decision.md`
section 1), LogUp fractions de-committed by a Habock fractional-sum GKR (v2). Non-ZK, publicly verifiable, Fiat-Shamir. The HEAD prover
(`prover/src/scr.rs`) is a different, later artifact: "split-reference correction" (SCR), a full-opening non-ZK FLOOR that proves a
*cheap exact bilinear reference* and a bounded XOR-correction length to the served output -- explicitly "does not prove native Blackwell
execution" (`memos/split-reference-correction-v1.md`).

**State.** Gates M0-M5 passed (`STATUS.md` "Milestone board"); M6 delivered its decision; M8 (GPU prover) delivered; a 17-memo R-program
killed, in order: structured shift gates (R1, 1.78x not 3-5x), binary fields (R2), dispute protocol (R3, rejected by the user), VOLE (R4/R5,
measured), lattice/Ajtai commit (R6, 0xPARC applebees measured 2.3 GB/s), IMMA-for-zerocheck and Poseidon2 (R7, measured), statistical
two-path gadget (R8, 1.26x), lookup recast (R9, field estimate 7.2x low), thin/thick trace split (R10). Then a pivot to "restrict the
numerics" (R12-R17) produced a *priced, never built* design whose cost depends on real-traffic rounding sparsity. The last commits (July 15-21)
are the SCR prover, an 0xPARC applebees re-run, and ~300 KB of RunPod campaign-controller code (`campaigns/scr_applebees_overnight/`).
Post-July documents (`sift-context-dump-*.md`, `model-proof-competition-*.md`) are syntheses for the veritor paper, not new measurements.

**Measured numbers** (all RTX 5090 sm_120 unless stated; `STATUS.md` board, `origin/M8-claude:memos/M8-gpu-floor.md`,
`metrics/SCR_benchmark_model_tile_20260716.json`):

~~~text
artifact                         relation                 shape        prover        rho_autoproof   overhead_ours(x4.09)  class
M5 CPU zerocheck (Xeon 6530x2)   exact native NVFP4       512^3        1,353 s       6.4e9           2.6e10                NON_ZK_PROOF
M8 GPU, same scheme              exact native NVFP4       512^3        9.15 s        4.3e7           1.8e8                 NON_ZK_PROOF
M8 GPU                           exact native NVFP4       256^3        2.19 s        8.3e7           3.4e8                 NON_ZK_PROOF
SCR v1 CPU full-opening          bilinear ref + XOR bits  1024x256x1024 8.88 s       2.1e7           8.6e7                 FLOOR, not native
M6 arm(b)v2 diet, priced         exact native NVFP4       --           --            1.1e5 (locked)  4.5e5                 projection
R7 repriced at measured rates    exact native NVFP4       --           --            4.2e5/8.1e5     1.7e6/3.3e6           projection
R12-R17 "certs-everywhere"       exact native, data-dep.  4096x512x4096 --           3.0e3-5.1e3     1.2e4-2.1e4           DESIGN-EST, unbuilt
~~~

M8's 512^3 wall is 516 committed B/MAC full-trace (TR commit 4.0 s + openings 2.2 s of 9.15 s); field work (the deg-12 zerocheck) was 0.87 s.
Structural caveat for the comparison: the NVFP4 transducer fires once per 64 MACs (group dots are exact integers), our BF16 step is lossy once
per 8 products with per-product alignment; per 64 MACs our checker has ~1,224 lookups vs their 167. Scaling their measured-rate floor by that
~7x lands at ~1.2e7 in our metric -- consistent with our modelled A ~1e7 / B ~1.4e7 (`note:r20-proof/tensor-cost/20260922T0450Z-report-tensor`), a useful independent sanity check.

**Soundness.** Asserted via the mutation battery (`gates/battery.py`, FOUNDATION section 7: 1000/1000 rejections per class, UNIQUENESS
0/400) and silicon replay 3001/3001; the SCR profile's argument is "the verifier recomputes everything" (`memos/SCR-security-ledger.md`).
No z3, no formal statement of soundness error for the Ligero/sumcheck profile; the M10 statement was made a "theorem" on paper only
(`origin/R16-claude:memos/M10-statement-v2.md`). Two concrete forgeries were found and fixed (section 2, item 1).

## 2. Ideas worth taking

1. **Two red-team findings to check in our own gadgets** (`origin/M6-claude:memos/M6-commitment-decision.md` section 1, "two soundness
   lessons"). (a) *+p-shadow*: for a dynamic truncation `q*2^s + r = P` checked mod p, a second solution `q' ~ q + p/2^s` lands inside the
   honest quotient window when the window is not tight relative to p; they staged every truncation at <= 12 bits with loose-limbed quotients.
   (b) *scaled range lookups are unsound*: checking `v*2^j in [0,2^16)` alone admits fractional v. Our `AlignState`/`AlignProduct`/`Normalise`
   (`checker/gadgets.py:232-442`) use exactly this shape (`ctx.lt_pow(r, ipow, W)`), sound over Goldilocks because r and q are separately
   range-checked and W=48 < 64 -- but the tensor-core decision moves us to **BabyBear (31 bits)**, where `q*pow + r = M*2^acc_shift` cannot
   hold in one field identity and must be limbed; both attacks apply to whatever the fields lane emits. Lanes: checker-min, a-packed (BabyBear
   embedding), red team. Saving: none; risk avoided: a forgery class already found once in a sibling design. Evidence: fixed in their prover,
   battery-tested; not a proof.
2. **Measured GPU hash and field rates, one card, validated kernels** (`origin/R7-claude:memos/R7-tensor-exchange-rates.md`,
   `bench/r7/*.cu`, `metrics/R7_*_1783816672.json`; independently re-run by R17). SHA-256 in Ligero column layout 1.22e12 B/s register
   microbench, **136 GB/s achieved streaming in a real commit pipeline at 41.7% occupancy** (`origin/R17-claude:memos/R17-sol-verification.md`,
   `STATUS.md` 02:40 section item 1); Blake3 compression 1.65e12 B/s microbench; **Poseidon2-BabyBear width-16: 1.1e11 B/s, 24 muls/byte,
   loses 11x to SHA-256 on GPU**. Maps to hash-gpu and to `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor` uncertainty 2 (20-192 GB/s spans 1.7e7-9.5e6 for A): 136 GB/s sits in our
   upper-middle band, and it says do not spend the night on an arithmetic hash for prover cost. Risk: 5090 SIMT != A100/H100; their rate is
   SHA-256 not Blake3.
3. **Limb-IGEMM BabyBear matmul at 63-69% of INT8 peak** (`origin/R7-claude:bench/r7/limbgemm.cu`, `metrics/R7_limbgemm_*.json`): balanced
   signed 8-bit 4-limb decomposition through cuBLASLt, mod-p fixup, exact vs CPU at two shapes, 1.8-2.1e13 field-MAC/s end to end on a
   4096^2x16384 statement (6x over CUDA-core). Maps to a-packed and to the encoder rows of `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor` (dense matrix DFT / Brakedown). It is a
   measured utilisation anchor for the *dense* parts, far above our 0.172 calibration; R7's companion finding is that a multi-column
   zerocheck point-eval has no contraction and stayed SIMT (2.0e12 BB ops/s) -- a caution for the A-kernel lane's sumcheck-as-matmul mapping
   (TensorZKP's degree-2 layout is what we assume; theirs was degree-12 over 216 columns). Risk: cuBLASLt-shaped, not a sumcheck round.
4. **Measured LogUp fraction-tree cost**: 73.0 ops/leaf, bandwidth-bound at 6.95e11 (BB) / 3.63e11 (GL) ops/s on the 5090 -- 2.8x below the
   zerocheck rate -- and it became their single largest term (R7 section 4b). Our 306 lookups/unit x 96 = 29k lookups/VU -> ~2.1e6 ops/VU ->
   ~3 us/VU ~ 3e5 overhead on SIMT at their rate: not binding for us, but it is a measured price for the "Hadamard/SIMT bucket" in `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor`
   uncertainty 3, and their fix list (pad-slot elimination, Gruen eq-factor, constant-numerator leaves, level fusion; <= 2x total) is directly
   our Track A lookup-integration to-do. Also the v2 trick "leaf denominators discharged inside the zerocheck, numerators verifier-evaluated,
   nothing extra committed" (M6 section 1). Lanes: A, B.
5. **Decomposable dynamic shift (Jolt trick) applied to the transducer** (`origin/R5-claude:memos/R4-vole-and-lookups.md` section B2):
   replicate the shift amount into every chunk index; truncation distributes exactly over disjoint-bit chunks (discarded parts sum to < 1),
   so a 25-bit x 6-bit-shift lookup becomes chunked <= 2^19 subtables with no carry correction. Priced (not built) as 216 columns -> 105
   values per firing, 2.4x advice compression. Maps to checker-min (our ALIGN/POW/NORM tables and the 306 lookups/unit). Risk: R9 measured
   its field side 7.2x above the estimate; the compression is real, the cost of proving it was not.
6. **In-circuit recomputation does not beat committed advice** (`M6-commitment-decision.md` sections 2b-4): the bit-exact align/normalise
   firing costs ~10^4 affine-bilinear GKR gates when recomputed (align 3,208, scale-mul 3,192, normalise 1,446, ...), and lookups compress
   that 20-30x -- so pure GKR recomputation (arm c) converges with committing the lookup trace (arm b) at ~1e5. Maps to Track A's
   hint-free branch 2 ("nothing extra committed, depth 630"): it is a measured warning that removing hint columns only pays if the lookups
   stay lookups inside GKR; do not recompute bit surgery as gates. Evidence: differential-validated circuit census, 1,200 rows vs oracle.
7. **VOLE, measured on the reference implementation** (`origin/R5-claude:memos/R5-vole-treaty-links.md` section 1): emp-zk QuickSilver
   4.59e6 mult gates/s/thread (matches the paper), **2.40e6 committed values/s/thread end to end with Ferret inline; input authentication
   0.47 us/value dominates advice-heavy statements; a VOLE-native ROM lookup costs 10.93 us = 26.2 committed-value equivalents**; the
   arithmetic-only ceiling is 26x faster (1.18e8 gates/s). Maps to Track C: our modelled 3e6 (`note:r20-proof/tensor-cost/20260922T0450Z-report-tensor`) assumes 83k correlations and
   64k multiplication checks per VU on a GPU; at their CPU rate one VU is ~35 ms/thread (~3.5e9 per thread, ~2e8 on 16 cores). The c-vole
   lane should state how our 29k lookups/VU are realised under VOLE (direct constraints? LogUp-over-VOLE at ~2 elements/lookup is priced
   there as D' and has no implementation) and what the protocol tax (Ferret expansion, authentication, IO glue) is on its CPU pod. Their
   KILL verdict does not transfer (it required public verifiability and priced a NIC axis we do not have); the constants do.
8. **Gate-owned uniqueness attacker and battery vocabulary** (`gates/uniqueness_attack.py`, `gates/battery.py`, `FOUNDATION.md` section 7):
   +0/-0 swaps against value-vs-bit comparison, one-ulp/sign/exponent-bit edits, row/column permutations, proof cross-pairing, statement
   re-serialisation, LOCKFILE_SWAP. Cheap to mirror as additional `vu-k1536-neg` negatives and as red-team checks on every backend's
   verifier. Lanes: all; red team.
9. **Reduction-order-free exact field sums make GPU transcripts bit-identical to the CPU prover** (`M8-gpu-floor.md`): every kernel port was
   checked by `cmp` on proof bytes plus 47 differential tests, including VRAM-adaptive fallback paths. A testing discipline for hash-gpu and
   a-packed, not a saving.
10. **The exactness-lemma / first-lossy-op census method** (`memos/M0.5-exactness-lemma.md`, `gates/m0.5/check_lemma.py`; R8 distributions
    `origin/R9-claude:memos/R8-statistical-path.md` section 1): on 61M real NVFP4 firings zero lossy truncations, shift range <= 15 in 99.6%.
    For BF16 x BF16 -> FP32 with K=1536 the analogue does not hold (16-bit products, 24-bit accumulator: the group step is lossy on ordinary
    data), so the two-path design they measured at only 1.26x is not for us; the *census tooling idea* (per-gadget hint-range histograms
    over the 3,456 real Qwen coordinates) is cheap and would tell the checker-min lane which tables are oversized.

## 3. What to ignore

- **The entire priced ladder R12-R17 (3.0e3 -> 5.1e3 -> 8.6e3 rho, "flagship < 1e4")**. DESIGN-EST on a relation ("certs-everywhere
  advice-patched bilinear", `STATUS.md` DESIGN RULING 19:55 PT) whose cost is data-dependent and rests on NVFP4 real traffic being almost
  never lossy; its adversarial floor is 1.2e5 (STATUS R15 item 3), it was never built, one accounting bug already withdrew a "5e3 ADOPT"
  (STATUS 07:50 FINDING 1), and its own commitment leg measured 56x above its priced share (STATUS 02:40 item 1). None of it is a proof.
- **STATUS.md's 1,290 lines of campaign narrative** (three "rulings" a day, twelve unmerged memos from a second model family, a "protocol
  gap now FOUR sessions deep"). Signal-to-noise is low; the memos on the branches are the artifacts, and only R7/R17/M6/M8/R5 carry
  measurements relevant to us.
- **The pre-registered rho ~ 1e3 prediction** (`FOUNDATION.md` section 11): missed by 100-800x at measured rates; the campaign's honest
  conclusion is that the exact transducer costs ~1e4 bit-gates per firing and every proof-system change re-denominates it.
- **SCR and the "approximate/relaxed unit" program** (`prover/src/scr.rs`, `sift-context-dump-approximate-proofs.md`): proves a different
  relation (single-rounding bilinear reference + correction bits) and reveals the witness. Relevant to the outer Verity planner someday,
  irrelevant to the frozen target tonight.
- **0xPARC applebees numbers** (`bench/APPLEBEES.md`, `memos/0xparc-matmul-full-model-gap.md`): INT16xINT8 lattice prover, incomplete
  statement ("no terminal opening"), 1.47e5 vs stock NVFP4; for the lattice scout only as a data point that Ajtai commit measured 2.3 GB/s
  on a 5090 (R6), 40x under hash.
- **Campaign/pod infrastructure** (`campaigns/scr_applebees_overnight/` ~300 KB, `run_loop.sh`, `DEPLOY.md`, `pod-snapshots/`): the
  previous agent's RunPod controller; we have `tools/research`.
- **Competition primer/research docs** (`model-proof-competition-*.md`, 127 KB): plain-language synthesis, no new evidence.
- M2 commit-and-open, R3 dispute tier, Z2 audit calculus: rejected by the user there for reasons that hold here too.

## 4. Reusable code (list only; nothing copied tonight)

No LICENSE file anywhere in the repo (`ls LICENSE*` empty, no `license` field in any `Cargo.toml`); it is the user's own private repo, so
provenance is "danielreuter/exact-inference-proving, commit X, agent-written", and the coordinator decides.

~~~text
what                                              where                                                        note
GPU microbenches: SHA-256/Blake3 column chains,   origin/R7-claude:bench/r7/{hashes,poseidon2,limbgemm,        CUDA sm_120, self-validating, emit metrics JSON;
Poseidon2-BB16, limb-IGEMM BabyBear via cuBLASLt,   layout_a,layout_b,layout_c,fraclevel}.cu, Makefile           the hash + limbgemm benches are the first thing
fold+eval sumcheck, frac-GKR level round                                                                       hash-gpu / a-packed could re-run on vy-g2 / vy-g4
Measured results for the above                    origin/R7-claude:metrics/R7_*_1783816672.json               plus memos/checks/r7_ladder.py recomputes the memo
Uniqueness attacker + mutation battery            gates/uniqueness_attack.py, gates/battery.py                 Python stdlib only; pattern for extra negatives
Habock fractional-sum GKR LogUp de-commit         origin/M6-claude:prover/src/m6prove.rs, m6core.rs            Goldilocks, hand-rolled; design reference only
Ligero (rate 1/4, 128 q) + SHA-256 Merkle + MLE   prover/src/{ligero,merkle,sha256,mle,field}.rs (HEAD)        no plonky3; ours already has equivalents
NVFP4 silicon corpus + probe harness              probes/results/probe{2,3}_*.json (6 MB), origin/M1-claude    Blackwell NVFP4 only; not our format
                                                    probes/src/bin/*.rs, spec/SEMANTICS.lock.v1.json
Exactness-lemma checker                           gates/m0.5/check_lemma.py                                    FP4-specific arithmetic; method only
16-term int group-dot CUDA kernel                 bench/scr_cuda/groupdot.cu                                   trivial; i16 output; 0.115 ms at 1024x256x1024
~~~

## 5. Discrepancies with `verity.ml.tc.silicon`

None to log. autoproof has **no BF16 tensor-core model** (`fp4-ref/src/native.rs:64-67,130`; `fp4-ref/src/bitref.rs:15,31`;
`FOUNDATION.md` section 4 de-scopes BF16), its only pinned semantics is Blackwell sm_120 NVFP4 `m16n8k64`, and it never ran on an A100 or
any BF16 instruction. Nothing there can agree or disagree with `AMPERE_BF16_M16N8K16` (groups (8,8), width 25, floor -132, WP1 zero
mismatches). Two informational notes, not entries:

- Structural analogy worth knowing: Blackwell's NVFP4 path also truncates toward zero and normalises RZ, but keeps 12 guard bits under the
  accumulator mantissa (W2=36) and 42 bits under the largest addend (W1=42), fires once per 64 MACs, and has a scale-exponent "hot clip"
  (`spec/SEMANTICS.lock.v1.json` gdfs_model). A future Blackwell BF16 pipeline in `silicon.py` should not be assumed to be Ampere's (8,8)/25.
- `sift-context-dump-approximate-proofs.md` section 6 states that veritor's `hawkeye_ampere_groupsum_fp8e4m3_v0` "matches no real hardware
  (18.3% single-tile agreement on Ada)". Our `silicon.py:314-323` already labels that pipeline `arch="synthetic"`; the Ada E4M3 pipeline
  (`ADA_E4M3_M16N8K32`) is the validated one. Consistent; no action.

## Verdict

Not a hill-climb to reuse, a measured negative result to respect: exact FP transducer proving over hash-PCS/sumcheck/lookups floors at
~1e5 rho on their sparser relation (1.7e6-3.3e6 in our metric at measured 5090 rates), reached the same way from five directions, and the
sub-1e4 numbers that dominate STATUS.md are unbuilt data-dependent designs for NVFP4 traffic that our BF16 target does not resemble.
The transferable value is the small set of validated GPU measurements (SHA/Blake3/Poseidon2 rates, limb-IGEMM utilisation, LogUp tree
cost, emp-zk VOLE constants) and two forgery classes to test our BabyBear embedding against.
