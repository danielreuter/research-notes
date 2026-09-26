---
lane: red-team-flock
kind: report
created: 2026-09-25T11:07Z
status: open
---

CHECKPOINT 3301c435 (11:35Z) [open] 11:35Z reopened: 8 per-workload GEMM cells (H100 x3, L40S x5), PB/CN + same-machine placement ruling, CPU only
CHECKPOINT 3301c435 (10:46Z) [final] FINAL 11:10Z: route (a) re-sweep a0ca8ef6/a979dfcb NON_ZK_PROOF (rebuild identical, gate 10/10, negs rejected); A-fs 7ae6c190/0e1095f3 NON_ZK_PROOF_DIAGNOSTIC (transcript binds steps/units/circuit/y; 10/10 reps; negs rejected). No pods, $0.
CHECKPOINT 3301c435 (10:37Z) [open] 10:38Z reopened: route (a) re-sweep cells a0ca8ef6 / a979dfcb, CPU only
CHECKPOINT 3301c435 (10:22Z) [final] FINAL 11:00Z: ChunkTail(n) GRANTED WITH CONDITIONS (CT1-CT3; selftests K2304/K8960 bf16 + K2560 fp8 all_pass; older layouts byte-identical by replay). L40S cells labelled earlier. No pods, $0.
CHECKPOINT 3301c435 (10:11Z) [blocked] 10:32Z: L40S GEMM cells df3d63e4/8bc3dba2 labelled NON_ZK_PROOF (PB1-PB4, CN1-CN2; replay 6/6 each). ChunkTail review BLOCKED: GitHub 401, need bundle of af2c3015 in lanes/red-team-flock/bundles/
CHECKPOINT 3301c435 (10:07Z) [blocked] 10:15Z: ChunkTail review blocked: GitHub 401 on this VM, af2c3015 not in store; need a bundle (af2c3015 vs e4f631bd) in lanes/red-team-flock/bundles/ or a fresh token
CHECKPOINT 3301c435 (10:05Z) [open] 10:06Z reopened: ChunkTail(n) review (PR #70), CPU only
CHECKPOINT 3301c435 (09:59Z) [final] FINAL 10:30Z: route (a) K=2048/8192 GRANTED NON_ZK_PROOF (art:95fdd0ae, 20197f8b labelled; own-build gate 10/10 + 6 negatives); Chunk(n) extended to 2<=n<=64 under CN2 (selftests n=5/19/28 all_pass); 5090 NVFP4 cross-DC verifier counts as separate (FA1), latency-bound timing noted. No pods, $0.
CHECKPOINT 3301c435 (09:34Z) [open] 09:35Z reopened: route (a) real-K review (agkr-real-k PR #69, art:95fdd0ae, 20197f8b), CPU only
CHECKPOINT 3301c435 (06:39Z) [final] FINAL 06:40Z: FP8 spine cells 5d2a91a7/ab115376/66d2412c/1c520240 PB1-PB4+CN1-CN2 met, labelled NON_ZK_PROOF + verified (replay r20260926-061513-ad9c 48/48, negs 16/16); old four had SUPERSEDED only as finding text -> wrote superseded_by; store_tables does not yet honour it. Pods terminated.
CHECKPOINT 3301c435 (06:23Z) [open] 06:25Z: 4 FP8 spine cells PB1/PB2/PB4/CN1/CN2 met from records; superseded_by written on old four; PB3 replay r20260926-061513-ad9c running (A4000 as CPU box, no CPU stock)
CHECKPOINT 3301c435 (06:05Z) [open] 06:05Z reopened: 4 FP8 real-K cells on bench-spine sets (5d2a91a7 ab115376 66d2412c 1c520240), PB1-PB4/CN1-CN2, CPU only
CHECKPOINT 3301c435 (05:19Z) [final] FINAL 05:20Z: 8 real-K Chunk(n)/wgmma cells PB1-PB4+CN1-CN2 met, labelled NON_ZK_PROOF + verified (replay r20260926-050108-7fa6 60/60, negs 20/20); wgmma cells: y = Hopper model on captured A100 inputs (1 / 3 words differ from set), tier suffix OK, source=captured covers x/W only. Pod terminated.
CHECKPOINT 3301c435 (05:04Z) [open] 05:05Z: 8 cells: PB1/PB2/PB4/CN1/CN2 met from records; wgmma y verified = Hopper model (1 and 3 words differ from A100 set); PB3 replay pod running (cpu3c-16)
CHECKPOINT 3301c435 (04:51Z) [open] 04:52Z reopened: per-cell PB1-PB4/CN1-CN2 on flock-backend's 8 real-K Chunk(n)/wgmma cells (CPU only)
CHECKPOINT 3301c435 (04:26Z) [final] 04:35Z: e4f631bd admission matches CN1-CN3 (code read, CPU only); finding labelled on the 8 Chunk(n) evidence arts
CHECKPOINT 3301c435 (04:17Z) [final] 04:22Z: Chunk(n) GRANTED WITH CONDITIONS CN1-CN3; wgmma pin 12c3c8d3 GRANTED; 8 evidence arts labelled; all handoffs answered in report; NVFP4 with red-team-flock-2
CHECKPOINT 3301c435 (04:15Z) [final] 04:20Z: Chunk(n) n=2/4/8/16 (fp8-ada, fp8-hopper, bf16-ampere, bf16-hopper-wgmma) GRANTED WITH CONDITIONS CN1-CN3; wgmma pin 12c3c8d3 GRANTED; 8 evidence arts labelled; NVFP4 left to red-team-flock-2
CHECKPOINT 3301c435 (03:13Z) [open] 03:30Z: NV1 checked on the 9 published Flock cells: verifier files consistent (y == y_public(out)); grants stand + NV1 condition; labelled. Chunk(n) review continuing
CHECKPOINT 3301c435 (02:37Z) [open] 02:45Z: Chunk(n) code/instances/wgmma pin checked clean; CPU selftest pod (cpu3c-8) running
CHECKPOINT 3301c435 (02:32Z) [open] reopened 02:33Z: Chunk(n) layouts (K=2048/8192) + bf16-hopper-wgmma pin 12c3c8d3
CHECKPOINT 3301c435 (01:20Z) [final] labelled NON_ZK_PROOF: art:167e64a8, c3e83404, 7afeecbe (e52eca82 = a6a6e548 + Ping, separate pods, 6/6); flock-vllm-block/v1 already granted 00:15Z. No pods.
CHECKPOINT 3301c435 (01:18Z) [final] art:167e64a8 labelled NON_ZK_PROOF (e52eca82 = a6a6e548 + Ping, separate pod, 6/6); flock-vllm-block/v1 already granted 00:15Z (art:56f792bd labelled). No pods.
CHECKPOINT 3301c435 (01:17Z) [open] reopened 01:17Z: label art:167e64a8 (A100 bf16-ampere keyed-BLAKE3)
CHECKPOINT 3301c435 (01:15Z) [final] 4 SHA-256 Flock cells labelled NON_ZK_PROOF (verifier c058c33f/bab181d6 equiv, union, separate pods); fp4-nvf4 unit (fb52a87c) GRANTED WITH CONDITIONS (1,800 diff units 0 mismatches; FP1 pin, FP2 layout review). No pods.
CHECKPOINT 3301c435 (01:06Z) [open] reopened 01:06Z: label 4 SHA-256 Flock cells; review NVFP4 unit circuit (pin fb52a87c)
CHECKPOINT 3301c435 (00:07Z) [final] art:1589ffe1 labelled NON_ZK_PROOF (Ping stateless; tag-8 clash with Prime flagged); flock-vllm-block/v1 GRANTED WITH CONDITIONS, art:56f792bd labelled (selftest 21/21, art:c30bb647; VL1 hardening, PB3 pending). Pods terminated.
CHECKPOINT 3301c435 (00:05Z) [final] art:1589ffe1 labelled NON_ZK_PROOF (Ping stateless; tag-8 clash with Prime flagged); flock-vllm-block/v1 GRANTED WITH CONDITIONS, art:56f792bd labelled (selftest 21/21, art:c30bb647; VL1 hardening, PB3 pending). Pods terminated.
CHECKPOINT 3301c435 (23:54Z) [open] reopened 23:55Z: resume flock-vllm-block/v1 review from bundle
CHECKPOINT 3301c435 (23:49Z) [final] flock-vllm-block/v1 review BLOCKED on source (GitHub auth 401 on VM; need token refresh or a git bundle of ff1c1e3f). Bound confirmed 2^-195.44/proof (2^-193.44 x4), evidence consistent; code review + selftest pending. Handoff 2355Z. No pods, $0.
CHECKPOINT 3301c435 (23:46Z) [blocked] flock-vllm-block/v1 review BLOCKED: GitHub auth 401 on VM (cannot fetch ff1c1e3f). Bound confirmed 2^-195.44/proof (2^-193.44 x4), evidence consistent; code review + selftest pending source. Handoff 2355Z.
CHECKPOINT 3301c435 (23:40Z) [open] reopened 23:41Z: review Flock over vllm-v1 (PR #41 @ ff1c1e3f), cell art:56f792bd
CHECKPOINT 3301c435 (23:31Z) [final] layouts fp8-hopper, bf16-ampere (AM1 pin pending), sha256/row/v1 ShaFp8/ShaBf16 and combos GRANTED WITH CONDITIONS at NON_ZK_PROOF (art:0f0b6f41, art:08295fa2); no cells routed yet; reopen to label cells / review next layouts. Pods terminated, ~$0.30.
CHECKPOINT 3301c435 (23:31Z) [open] all new Flock layouts reviewed: fp8-hopper, bf16-ampere (AM1 pin pending), ShaFp8/ShaBf16 + combos: GRANTED WITH CONDITIONS at NON_ZK_PROOF. No cells routed yet; no pod running (CPU stock out). ~$0.30 spent.
CHECKPOINT 3301c435 (23:29Z) [open] fp8-hopper + bf16-ampere GRANTED W/ CONDITIONS (art:0f0b6f41; bf16-ampere needs PINS AM1); sha256/row/v1 ShaFp8 (+ShaBf16 pre-review) GRANTED W/ CONDITIONS (art:08295fa2; SH1 instances switch, SH2 negatives). Waiting for routed cells.
CHECKPOINT 3301c435 (23:16Z) [open] fp8-hopper + bf16-ampere layouts GRANTED WITH CONDITIONS at NON_ZK_PROOF (art:0f0b6f41 selftests all-pass; diff tests 0/400; bf16-ampere needs PINS entry AM1). Waiting for routed cells / next layout (frame-v3 SHA-256 leaf).
CHECKPOINT 3301c435 (23:04Z) [open] reopened 23:05Z: review fp8-hopper (H100) and bf16-ampere (A100) block layouts, PR #30
CHECKPOINT 3301c435 (22:22Z) [final] NON_ZK_PROOF labels: art:6d1295ed (H100, a6a6e548), art:d1961ba4 (4090, d93ce18b) — verifier commits zero-diff from reviewed path; route (a) art:3d7cbea2 + art:77411c93. No pod.
CHECKPOINT 3301c435 (22:20Z) [final] NON_ZK_PROOF labels on art:6d1295ed (H100, a6a6e548) + art:d1961ba4 (4090, d93ce18b): both verifier commits zero-diff from e5d54118 = reviewed path; route (a) art:3d7cbea2 labelled. No pod.
CHECKPOINT 3301c435 (22:18Z) [open] reopened 22:19Z: verify verifier commits a6a6e548 / d93ce18b for re-registered art:6d1295ed / art:d1961ba4 (no pod)
CHECKPOINT 3301c435 (21:40Z) [final] labels NON_ZK_PROOF on route (a) art:4b52879f + art:aa9223c2 (RA1 fail-fast verified at 504f75b6); 4090 art:949bcc35 meets PB2/PB4/FA1, PB3 pending, PB1 missing (commit unknown; source e5d54118 checked equivalent) -> label the re-registered id. No pod.
CHECKPOINT 3301c435 (21:34Z) [open] reopened 21:35Z: check 4090 fp8-ada result art:949bcc35 against PB1-PB4/FA1 (no pod)
CHECKPOINT 3301c435 (21:32Z) [final] decision 57 recorded on art:ca6029c1 + art:3bfb2f58; fp8-ada block layout (48045063) GRANTED WITH CONDITIONS at NON_ZK_PROOF (2^-195.54/proof; selftest fp8 16/16 + bf16 18/18 art:1f2fe1e9; FA1 separate-pod verifier, FA2 fp8 negatives). Pod terminated 21:31Z ~$0.10
CHECKPOINT 3301c435 (21:21Z) [open] reopened 21:22Z: record decision 57 in findings; fp8-ada block layout review (PR #30 @ 48045063)
CHECKPOINT 3301c435 (21:19Z) [final] flock-pure-block/v2 GRANTED WITH CONDITIONS at NON_ZK_PROOF (2^-195.44/proof, 2^-193.44 over 4 sub-batches; label art:ca6029c1); route (a) live coins GRANTED WITH CONDITIONS at NON_ZK_PROOF (2^-130.19; label art:3bfb2f58; RA1 verifier DoS). fp8-ada block review (2100Z) queued, not done. ~$0.15
CHECKPOINT 3301c435 (21:16Z) [final] flock-pure-block/v2 GRANTED WITH CONDITIONS at NON_ZK_PROOF (2^-195.44/proof, 2^-193.44 over 4 sub-batches; selftest 18/18 art:ac1aeeeb; label art:ca6029c1); route (a) live coins GRANTED WITH CONDITIONS at NON_ZK_PROOF (2^-130.19; label art:3bfb2f58; RA1 verifier DoS on dropped round). Pods terminated ~$0.15
CHECKPOINT 3301c435 (20:40Z) [open] route (a) re-audit PAUSED 20:41Z (priority: flock-pure-block/v2). So far: code review OK (live prime coins, replay in Rust/py), my gate re-run 5/5 prime+replayable+prime_live pass, non_producer fails (verifier operator route-a-live); negatives cross/word/state/before_commit rejected
CHECKPOINT 3301c435 (20:28Z) [open] fifth audit started 20:29Z (lane REOPENED): route (a) live prime coins, PR #36 @ dec08973, art:3bfb2f58
CHECKPOINT 3301c435 (18:45Z) [final] FOURTH AUDIT: route (a) cell art:8f7ef58b GRANTED WITH CONDITIONS at NON_ZK_PROOF_DIAGNOSTIC (downgrade: prime coins FS); 2^-130.19 at current convention (Daniel: hash q^2/2^256, FS x2^60); cell-verifier not non-producer; gate re-run 5/5 admitted; labels written; no pods
CHECKPOINT 3301c435 (18:44Z) [final] FOURTH AUDIT: route (a) cell art:8f7ef58b GRANTED WITH CONDITIONS at NON_ZK_PROOF_DIAGNOSTIC (downgrade: prime coins FS); 2^-130.19 at current convention (Daniel: hash q^2/2^256, FS x2^60); cell-verifier not non-producer; gate re-run 5/5 admitted; labels written; no pods
CHECKPOINT 3301c435 (18:32Z) [open] fourth audit started 18:32Z (lane REOPENED): route (a) cell, agkr-flock-cell PR #28 @ c95dd13a, art:8f7ef58b. Paper/code review first.
CHECKPOINT 3301c435 (15:58Z) [final] THIRD AUDIT: route (a) CPU GRANTED WITH CONDITIONS (flock-link@4b560b2b L1-L4,F2,F3 hold; art:20545959); composed 2^-130.2 (A-GKR-bound); no cell until E0 (ungated exchange accepted), E1 (evidence gate unenforced), P1-P3 (prime side). Pod terminated 15:57Z ~$0.05
CHECKPOINT 3301c435 (15:40Z) [open] third audit started 15:41Z (lane REOPENED, not final): flock-link L1-L4/F2/F3 CPU, PR #25 lane/flock-link@4b560b2b. Pods only after 15:52Z.
CHECKPOINT 3301c435 (12:50Z) [final] RE-AUDIT: GRANTED WITH CONDITIONS flock-128-r2 as implemented (flock-live@a43f6254): R1-R4,R6-R8 hold, 17 attacks rejected (art:1bd3368b art:12a6b845); R5 stub -> class for route (a) conditional on link L1-L4; F1-F3. Pods terminated 12:49Z ~$0.2
CHECKPOINT 3301c435 (12:39Z) [open] re-audit in progress (lane reopened, NOT final): two vy-red-team-flock pods vanished ~2 min after launch (likely FINAL-POD reap from my 11:30Z final); retrying pod + local fallback build. Attack harness evidence/rtf_live_attacks_tail.rs
CHECKPOINT 3301c435 (12:30Z) [open] re-audit started: read flock-live report + lane/flock-live@a43f6254 lib.rs/bin (server, replay, forks, pins); inbox 1129Z coordinator handoff read (superseded by this re-audit). Next: attack harness on cpu pod (R1/R2/R3/R7)
CHECKPOINT 3301c435 (11:27Z) [final] NOT GRANTED flock-128-r2: terms hold (2^-195.5 reproduced) but reps unbound to one root (BREAK, art:8d04b53f) + no live-coin challenger (FS-only <=2^-75.6); grantable w/ R1-R8; composed 2^-130.2 (A-GKR-bound). Pod terminated 11:24Z ~$0.07; handoffs 1130Z
CHECKPOINT 3301c435 (11:24Z) [open] pod demo run r20260925-112210-2d3d (art:8d04b53f): two honest Fast100 reps over DIFFERENT witnesses both accepted (roots differ); downgrades/replay rejected; padding benign. Pod vy-red-team-flock terminated. Next: report + verdict handoffs
CHECKPOINT 3301c435 (11:14Z) [open] findings so far: live-coin challenger absent (verifier is FS-only); reps commit separately + Mixed binding has no public io -> rep1 can be an honest proof of another witness (no squaring vs link); AG r1 nonce freedom (aarch64 only). Next: cheap CPU pod demo of unlinked reps
CHECKPOINT 3301c435 (11:12Z) [open] paper+code review of flock b684b12 (public clone) + flock-128 harness (art:4cc09936 inputs): query term -97.77/run reproduced from TOMLs; fixed inner zerocheck prefix lossless (x86 RS path); candidate BREAK: reps commit separately, link binds one root. Next: verify live-coin/FS gates, union verifier
CHECKPOINT 3301c435 (11:07Z) [open] started 11:08Z: setup done, read contract/brief/flock-128 report+PARAMETERS handoff; inbox empty. Next: red-team-link §3-4, TABLES, flock-128 evidence (accounting.py, census, configs, harness patch)

# red-team-flock: audit of Flock b684b12 at flock-128's 2^-128 profile `flock-128-r2`

**Grant: NOT GRANTED.** The paper terms hold: 2^-97.8 for each Fast100 run, reproduced from the embedded TOMLs, and
2^-195.5 for two runs with independent live coins. But the profile as specified and implemented does not deliver that
figure, for two reasons:
- **R-BREAK:** the reps aren't bound to one commitment. Each rep commits its own root, and the Mixed binding has no
  public I/O. So rep 2 can be an honest proof about a different witness, and the error stays at the single-run 2^-97.8.
  Demo art:8d04b53f.
- **L-GAP:** the live-coin challenger doesn't exist. The only verifier is Fiat–Shamir, which gives at most 2^-75.6 by
  flock-128's own ledger, and its CUDA prover squeezes on the device.

With conditions R1–R8 (§5) it becomes grantable. After fixes the composed whole proof is 2^-130.2 on the A-GKR route,
set by A-GKR, not Flock.

Inputs:
- flock-128's report and its PARAMETERS handoff (`lanes/coordinator/20260925T1055Z-handoff-from-flock-128.md`).
- flock-128's harness `unit_shape128.rs` and its pod script, from its cost run art:4cc09936 (`inputs/`). flock-128's
  `evidence/` (accounting.py, census TSVs, configs) is not mirrored to the cloud, so the per-site degrees are
  cross-checked against Flock's own `docs/128-bit-grinding-audit.md` table instead.
- Flock b684b12 (public `github.com/succinctlabs/flock`), read end to end on the paths below.
- red-team-link §3–4, and TABLES.

Handoffs received: none (the inbox was empty at every checkpoint).

## 1. Term by term (paper): HOLDS, with notes

| term | verdict | check |
|---|---|---|
| Ligerito queries, Johnson η=0.02 | **HOLDS** | Per level `Q·log2(1/(√ρ+η))` from `m3{0..3}_fast100.toml` gives [100.2, 100.0, 100.9, 100.1, 100.9, 100.3]. The per-run union is **2^-97.77** (m30: 2^-98.04), so two runs give 2^-195.54, as claimed. The (1−γ)^Q form is combinatorial once the OOD step has pinned one codeword: `paper_predicted_bits` charges no list factor, and the OOD binding is charged separately. The stratified sampler (`pcs/stratified.rs`) is exactly (1−γ)^Q by AM–GM over equal strata, for any agreement set fixed before sampling. Query indices are the low bits of a uniform F128. The verifier derives the query counts from the schedule stored on its config (built from the profile), and never from the proof. |
| MCA / proximity gaps up to Johnson (F256) | **HOLDS** | Proven: MCA up to the Johnson radius (Haböck, ePrint 2025/2110), and proximity gaps with O(n) exceptions (BCHKS25, ePrint 2025/2055). Flock charges a/2^256 with the row-union factor 2^{ℓ−1} (208+ bits). Even the older BCI+20 constant (m=18 at η=0.02, n=2^21) gives ≥ 2^-184 per fold, so the grant doesn't depend on which constant is used. The subfield descent at split commits is correct: v is in F128^n, c^q is again an RS codeword because the domain lies in F128, and they agree on more than √ρ·n > k positions, so c = c^q. |
| Two-point OOD, F128, list-unioned | HOLDS | 233.7+ bits; L0 is charged degree m = μ+7 (conservative). |
| Claim batching β / consistency α (F128) | HOLDS (conservative) | The TOML `expected_eps_*` fields are **raw**: after grinding, 122.9+6 gives the doc's 128.9. The raw per-run unions from the TOMLs are 2^-118.8 (β) and 2^-115.8 (α). flock-128's −115.1 and −114.5 are looser, and fine. No grinding credit is taken. |
| F128 PIOP (zerocheck, lincheck, ring switch F128^7, merged opening, multipoint, anchor) | HOLDS | Flock's degree table matches: skip point 127, lincheck skip 63, multipoint γ K−1, Merkle-shift 3. With the ~150 sites at −118.4 per run, the per-site degrees could be off by 2^15 before the per-run total moved; the query term dominates by more than 16 bits. |
| **7 fixed inner zerocheck coordinates** (audit item 2) | **HOLDS, lossless** | The x86/CUDA RS path (`zerocheck.rs` 693–719) pins 3 φ8(GF(2^8)) constants and 4 medium β_i. So eq_inner(b) = C_s·α^K·γ^j/D, with K<8 and j<16. The 128 weights α^K·γ^j are a GF(2)-basis of F128: 1..α^7 span GF(2^8), and γ has degree 16 over GF(2^8), so 1..γ^15 are GF(2^8)-independent. Every error value a·b−c on the cube is in GF(2), so each 128-bit inner block maps injectively to F128. The fixed prefix therefore loses nothing, and the SZ degree over the random coordinates is m−7 (the ledger charges m). The code comment's "7 coordinates F2-independent" states the wrong invariant, but the right one holds. Nothing deterministic is shared across reps. |
| AG-skip r₁ (aarch64 only) | **GAP (out of profile)** | In Fast100 (ungrinded) the verifier accepts any valid nonce of the prover's choosing, not the minimal one (`ag_skip.rs` 1109–1126). That gives about 14.3 bits of prover choice over r₁, **even with live coins**. It's unused on x86/CUDA: the union verifier takes the RS proof flavour only. |
| Grinding credit | HOLDS | 0 counted. Fast100 still grinds claim/consistency batching by 6–11 bits (TOML), and query/fold/PIOP by 0. The nonces are carried but not credited. |

Per run, all terms sum to 2^-97.76. Two independent runs give **2^-195.5**, and the GPU pair of proofs 2^-194.5. The
arithmetic is right. What fails is its premise, §2–3.

## 2. Repetition, coins and Fiat–Shamir

**R-BREAK: the reps are not bound to one commitment.**
- The profile says each rep is "a full independent proof". The harness (`unit_shape128.rs`, `prove_one` and
  `verify_one`) proves and verifies each rep with its own `Commitment` and never compares them.
- `bind_statement` (Mixed, `union.rs` 624) absorbs only the registry digest, the counts and the rep's own root. There
  is **no public I/O**: every BLAKE3 input and output is witness.
- So the only meaningful claim is commit-and-prove: *this root* satisfies the R1CS. Two roots mean two claims. A
  cheating prover links rep 0's root to the prime side (whose soundness is 2^-97.8), and makes rep 1 an honest proof of
  any other witness. The r2 verifier accepts with the single-run probability. Squaring fails for **every** term.
- Demo, pod run r20260925-112210-2d3d, **art:8d04b53f** (`evidence/rtf_unlinked_reps.rs`, `evidence/rtf-results.tsv`),
  BLAKE3 table, N = 4096 and 16384 (m26, m28):
  - `unlinked_pair_rep1_other_witness`: r2 accepts, the roots differ.
  - `honest_pair_same_witness`: accepted, same root. The commit is deterministic, so a root-equality check is complete
    for honest provers and costs nothing.
- Fix (R1): one commitment per table, and the post-commit protocol (PIOP and opening) run twice on fresh live coins. Or
  keep both commits, and the verifier requires root_rep0 == root_rep1 before it issues any rep-1 coin. The link must
  bind that one root. The GPU pair has two tables, so the condition applies per table.
- Bonus: if the link claims y^k = ẑ(r^k) are opened in **both** reps against the shared root with fresh batching
  coins, red-team-link's C1 reduction term (2^-122 over GF(2^128)) squares as well, to about 2^-244. That's an
  alternative to moving the link reduction to GF(2^256).

**L-GAP: no live-coin challenger.**
- Every r2 proof so far uses `FsChallenger` with per-rep domains. Under FS, repetition doesn't square: the prover
  grinds each rep separately. flock-128's own ledger gives at best (2^60·2^-97.8)^2 = 2^-75.6.
- Today a flock-128-r2 verifier can only accept FS transcripts. The brief's "refuses FS transcripts" doesn't exist yet.
  flock-128 says so too (its audit item 1).

What the live challenger must satisfy (R2–R5), from reading the trait and its call sites:
- **Commit before coin (R2).** The verifier issues coin i only after it has received everything the prover absorbed
  before squeeze i. At the end it verifies the proof with a replay challenger that checks the absorbed bytes before
  each coin equal what it received (a per-round msg hash, as the Ligerito `c…` live sessions record), and then returns
  that coin. Recording coins and checking a later proof file against them alone is a total break: the messages could be
  chosen after the coins were seen.
- **Forks are live (R3).** The production merged opening forks a child transcript (`pcs.rs` 2282 and 2768,
  `flock-par-assist-v1`: multipoint γ, multipoint and anchor rounds) and runs it **concurrently** with the parent under
  `rayon::join`.
  - `fork_from_seed` must return a *live* child: its own commit-before-coin stream, multiplexed with the parent's.
  - It must not be an FsChallenger seeded from the fork seed. That would be FS inside the live run, charged ×2^60 on
    about 30 degree-2 rounds and γ: about 2^-61 per run, 2^-122 for two, **below 2^-128**.
- **PoW sites are pure coins (R4).** `grind_pow_and_sample_*` and `verify_pow_and_sample_*` must return a verifier coin
  that doesn't depend on the prover's nonce. If the challenge were H(coin, nonce), the prover would pick the nonce after
  seeing the coin, which is grinding in reverse. The same goes for the lincheck `SkipPoint::sample_fresh` loop and any
  prover-nonce point derivation. The AG r₁ path is excluded (§1).
- **Ordering with the link (R5).** Flock's first coins (the zerocheck r) are squeezed right after `bind_statement`. In
  the linked protocol the verifier must not send them before root_F, the link points and y have been received
  (red-team-link C2). Under FS, the red-team-link break stands: Flock seeds from the registry digest, counts and root
  only.
- **Fresh coins per rep:** from OS randomness, drawn when requested. Nothing is derived from rep 0.

**GPU/CPU transcript equality (item 8):** HOLDS under FS. The CPU verifier accepts every Flock-CUDA proof
(flock-bench-80gb). For live coins it's a GAP: `cuda-ghash/prove_ffi.cu` runs its own C++ `FsChallenger` plus a
**device-side** zerocheck challenger (`zc_challenger_device.cuh`). Each squeeze must round-trip to the host and the
verifier (R6), which is also a cost change the cost runs don't include yet.

## 3. Implementation matches the accounting

- **Profile downgrade: HOLDS.** `verify_union_piops` requires `commitment.params == expected` (derived `PartialEq` over
  m, rate, batch, **profile**, lanes and Merkle hash) and rejects a mismatch (`PcsOpen(Ligerito)`). The verifier's
  profile comes from its caller. Demo art:8d04b53f, all rejected:
  - `fast_proof_under_fast100_verifier`;
  - `fast100_proof_relabelled_fast_params`;
  - `fast100_proof_under_fast_verifier`;
  - `rep0_replayed_as_rep1`.

  Condition (R7): the verity verifier pins `Fast100`, reps = 2 and the RS flavour from Σ/configuration, never from the
  proof or statement file. A lone rep (fast100x1) must be refused at session level.
- **Schedules frozen: HOLDS.** The embedded TOMLs are validated from the unrounded formulas (`validate_profile` pins
  the analysis id per profile). The `expected_eps_*` fields are diagnostics.
- **Padding (item 9): HOLDS.** With padding rows filled with real dummy compressions (pin = 1, the full-utilisation
  driver at n_t < 2^nu), the root is identical to the zero-padded proof's (`root_equals_zero_padded_proof: true`). The
  dense stack drops rows ≥ n_t, so nothing uncommitted is proven.
- **Hashes (item 7):** the Merkle tree and the transcript are BLAKE3 with 32-byte digests (`HashKind` default
  `Blake3`; the PcsParams doc comment's "defaults to SHA-256" is stale). The transcript is a custom chained BLAKE3
  compression. Table 1 must name both. Merkle binding is a computational term that the 2^-195.5 excludes (§4).

## 4. Composition (with R1–R6 in place)

On the A-GKR route (a), at 4,096 BF16 VUs, the whole proof is the sum of these terms:
- ε_F (A-GKR): 2^-130.2;
- ε_B (Flock r2): 2^-195.5 on CPU, 2^-194.5 for the GPU pair;
- ε_red: 2^-251 via C1 over GF(2^256), or about 2^-244 via link claims in both reps. If neither, 2^-122, **which
  fails**;
- ε_SZ: L·2^-246;
- ε_ρ: at most 2^-177.

**Total = 2^-130.2 ≥ 2^-128**, with A-GKR the binding term. If the accountant applies A-GKR's "default hash budget"
(its README gives 2^-127.7), the proof misses 2^-128 whatever Flock does. The same convention would then add a Merkle
binding term to Flock too. This belongs to the accountant (C8). On B-Ligero, 2^-128.05 + 2^-195.5 still rounds to
2^-128.05, a pass, so Flock r2 leaves B-Ligero's budget intact.

## 5. Grant

**NOT GRANTED** for flock-128-r2 as specified and implemented. It becomes **GRANTED WITH CONDITIONS** once these land,
with a re-audit of the live challenger code:
- **R1:** the reps share one commitment per table: commit once, or the verifier checks root equality before rep-1
  coins. The link binds that root.
- **R2:** a live challenger with commit-before-coin, and final replay that checks messages against the coins.
- **R3:** a live `fork_from_seed` (concurrent child streams).
- **R4:** pure verifier coins at every PoW and nonce site.
- **R5:** Flock's coins are issued only after root_F, the link points and y.
- **R6:** a live-coin path in Flock-CUDA (host and device challengers), costed.
- **R7:** the verifier pins Fast100, reps = 2 and the RS flavour from configuration. It rejects AG proofs and lone reps.
- **R8:** evidence is the live session record. File re-verification replaying the runner's coins doesn't count
  (TABLES ‡).

**Negatives an implementation must keep passing:**
1. Reps with different roots (art:8d04b53f's unlinked pair) are rejected.
2. Rep 0 replayed as rep 1 is rejected.
3. Under live coins, a proof message altered after its coin was issued is rejected, in the parent and in the fork child
   separately.
4. A prover-chosen PoW nonce changing a live challenge has no effect, because the coin is independent.
5. Fast (`fastx1`) and fast100x1 proofs, and a Fast100 proof with relabelled params, are rejected by the r2 verifier.
6. An FS-transcript bundle presented to the live verifier is rejected, because no session record exists.
7. An AG-flavour proof is rejected.
8. The flock-128 negatives stay: a byte flip, and a witness bit flip in rep 0.
9. Link negatives 10, 11 and 15 of red-team-link §4, run against **both** reps.
10. Padding rows nonzero give the same root as zero padding, or are rejected.

## FINAL

~~~text
tip: none (no repo commits; notes + evidence only)        merge-with: none
known-failures: none    pod: vy-red-team-flock (qfshb6s0fid2ng, cpu3c 16 vCPU) terminated 11:24Z; about $0.07
artifacts: art:8d04b53f art:4cc09936 (flock-128's, read)
~~~

Evidence: `evidence/rtf_unlinked_reps.rs` (drop-in Flock example), `evidence/pod-scripts/10-unlinked-reps.sh`,
`evidence/rtf-results.tsv`. The earlier runs rtf-unlinked-1..3 used a non-run id, were not published as attempts, and
are superseded by r20260925-112210-2d3d (same script). Handoffs written: `lanes/coordinator/`, with copies to
`lanes/flock-128/`, `lanes/agkr-bound/` and `lanes/flock-glue/` (all `20260925T1130Z-handoff-from-red-team-flock.md`).

# Re-audit (12:25–12:55Z): flock-live @ a43f6254 against R1–R8

**Grant: GRANTED WITH CONDITIONS** for flock-128-r2's Flock part as implemented:
- verity `lane/flock-live` @ a43f6254, `backends/flock/live/` and `cuda_live_patch.py`, on Flock b684b12;
- on CPU, the BLAKE3-table union verifier; on GPU, the per-table `verify_ligerito` sessions.

The whole-proof class for route (a) stays conditional on the link work (L1–L4 below). So no 2^-128 Table 2 cell exists
yet.

Inputs:
- flock-live's report and evidence (`lanes/flock-live/`);
- the code at `origin/lane/flock-live` a43f6254 (lib.rs 956 lines, bin 527 lines), read in full.

Handoffs received:
- `20260925T1129Z-handoff-from-coordinator.md` (flock-128 FINAL; audit as specified). The first audit answered it:
  §2 listed the requirements for the live implementation, and this re-audit checks them.

Evidence (all preserved):
- run r20260925-124333-1a03, **art:1bd3368b** (n = 4096);
- run r20260925-124555-21d5, **art:12a6b845** (n = 4096 and 16384, m26 and m28).

Harness: `evidence/rtf_live_attacks_tail.rs`, which is flock-live's bin up to `fn main()` plus a man-in-the-middle
prover transport and 17 attacks. Pod script: `evidence/pod-scripts/20-live-attacks.sh`. Results:
`evidence/rtf-live-attacks.tsv`. I also re-ran flock-live's own `selftest`: all 22 cases pass at each n (44 of 44).

## Design check (code reading)

Soundness sits entirely on the verifier side: the `Server` plus `ReplayChallenger` running the unmodified Rust Flock
verifier. The CPU/CUDA prover patches only affect completeness.
- Every challenge the Rust verifier uses comes through the `Challenger` trait. The only non-test `FsChallenger`
  constructions are in `matrix_fold` tests, and the RS lincheck skip point is a plain `sample_f128`. So the replay sees
  every coin.
- At each coin the replay checks sha256 of exactly the bytes the verifier absorbed since the previous coin, against the
  round recorded before that coin was drawn from `/dev/urandom`. It also checks the coin count, and at the end checks
  that every recorded round of the rep's streams was consumed. That is commit-before-coin, independent of anything the
  prover says afterwards.

## Attacks (all at n = 4096 and 16384)

| # | attack | cond | result | stopped by |
|---|---|---|---|---|
| 1 | rep 1's live binding round claims rep 0's root, then proves witness B (so the server issues 103–116 rep-1 coins) | R1 | **rejected** | replay, rep-1 round 0 digest. The proof's absorbed root is B's, and the finish cap check backs it up |
| 2 | child `rep1/f0` opened at parent position 0, *before* rep 1's binding round; the server issues it 2 coin rounds | R1/R3 | **rejected** | replay R3 (the child's position and label don't match the verifier's fork point) |
| 3 | fork child opened at a claimed parent position off by one | R3 | rejected | server R3 position check |
| 4 | fork child's seed words (the parent's coins) altered in its first round | R3 | rejected | replay, child round-0 digest |
| 5 | one round split into two coin requests: rep 0 k=5, rep 0 k=80 (after the fork), `rep1/f0` k=10 | R2 | rejected ×3 | the server's fork position check (k=5); replay digest or count (k=80, child) |
| 6 | an extra coin round after the proof, on rep 0 and on `rep1/f0` | R2 | rejected ×2 | replay: rounds recorded ≠ rounds consumed |
| 7 | reps interleaved (rep 1 proving while rep 0 is still in flight) | R2 | accepted (allowed) | see below |
| 8 | hello with keys reordered; reps = 3; a third rep stream opened; rep 1 opened with rep 0's domain | R7 | rejected ×4 | exact hello string, rep bound, per-rep domain |
| 9 | Fast proofs in an r2 session | R7 | rejected | params pin |
| 10 | arbitrary link bytes | R5 | **accepted** | stub: any bytes satisfy the gate |
| 11 | verifier started with `--no-link`: session without link context | R5/R8 | **accepted** | the record shows `require_link: false`, `link_sha256: null` |

flock-live's 22 selftest cases (its negatives 1–10 and R5) reproduce: all pass.

## Verdicts per condition
- **R1: HOLDS.** Rep 1 is refused until rep 0 has committed, and its binding round must carry rep 0's root. Attacks 1
  and 2 show the server can be made to issue rep-1 coins (on a claimed root, or to an early child). Neither reaches a
  verdict: acceptance requires the proof's absorbed bytes to match every recorded round and the proof's root to equal
  the one committed.
  - Hardening (not blocking): refuse a child `Open` on a root stream before its binding round, and refuse a child at
    parent position 0.
- **R2: HOLDS.** No split, merge, extra or late round, and no message altered after its coin, survives the replay.
  - Interleaved reps are accepted. That's sound: each rep's per-round errors (Schwartz–Zippel sites, query and
    proximity terms) are round-by-round bounds on fresh uniform coins over the same committed word, whatever the prover
    has seen from the other rep. So the two-rep product 2^-97.8 × 2^-97.8 holds without enforced sequencing.
- **R3: HOLDS.** The child is opened after the parent's seed round, the verifier checks its position and label, its
  seed is absorbed as a message, and its coins are live (attacks 2–5; flock-live's fork negatives). Parent coins after
  the fork being visible to the child (and the reverse) is the same independence Flock's fork argument already relies
  on under FS, so it is unchanged.
- **R4: HOLDS.** Nonces are messages. Coins don't depend on them (flock-live's `prover_chosen_pow_nonce_honest`
  accepted, altered nonce rejected).
- **R5: placeholder.** Only the arrival order is enforced (attack 10). Conditional on the link work (L1).
- **R6: HOLDS (by reading, plus flock-live's H100 runs art:16c17a43 and art:5320c158).** GPU soundness is the same
  Server, replay and `GpuVerifier` (Fast100, rate 1/2, batch 6, SHA-256 pinned). Not re-run on a GPU pod: nothing
  GPU-specific sits on the verifier side.
- **R7: HOLDS** (attacks 8–9, plus flock-live's fastx1, fast100x1, lone rep, relabel and AG flavour cases).
- **R8: HOLDS with a policy condition.** The verdict is computed only from the session record. But a verifier run with
  `--no-link`, or any record with `require_link: false` or `link_sha256: null`, must not count as flock-128-r2 evidence
  (attack 11). The verifier that produces evidence for a cell must be run by a non-producer (TABLES criterion 6);
  flock-live's sessions ran on the prover's own pod.

## Grant: GRANTED WITH CONDITIONS

Implementation conditions (Flock side):
- **F1:** evidence counts only from records with `require_link: true` and a non-null `link_sha256`, from a verifier
  operated by a non-producer.
- **F2:** the production statement verifiers are pinned the same way `Verifier` and `GpuVerifier` are: registry
  digest, counts or statement digest from the configured instance set, and the Fast100 params. That covers flock-128's
  CPU line (census unit + BLAKE3 in one union) and the GPU unit table. Today's CPU verifier is the BLAKE3-table
  statement only.
- **F3 (hardening):** the early-child refusals under R1 above.

Stays conditional on the link work (flock-glue / red-team-link):
- **L1 (R5 / C2):** the real link exchange replaces the stub:
  - commit root_F and root_B;
  - the verifier issues the link points as its own coin slot after both roots;
  - y is received;
  - only then are Flock's coins issued.

  root_B must be the one root the R1 check binds, which needs Flock's commit split from its prove, or a
  `Commit(root_B)` round that the binding round must equal.
- **L2 (C1):** the link claims y^k = ẑ(r^k) are opened in **both** reps against that root with fresh coins (about
  2^-244), or verified over GF(2^256). Negatives 10 and 11 of red-team-link §4 must run against both reps.
- **L3 (GPU pair):** the unit and BLAKE3 tables are proved today as two independent sessions. They must be one session,
  or two sessions bound to the same Σ and link context (the verifier checks equal `link_sha256` and the pairing).
- **L4 (C4):** chain glue and endpoints (red-team-link F5). Without them the BLAKE3 table proves unlinked compressions.

Composition is unchanged. With L1–L4 in place the whole proof is 2^-130.2 on the A-GKR route (A-GKR-bound; 2^-127.7
if the accountant counts A-GKR's hash budget, C8). Flock r2 is 2^-195.5 on CPU and 2^-194.5 for the GPU pair.

## Re-audit FINAL

~~~text
tip: none (no repo commits; notes + evidence only)        merge-with: none
known-failures: none    pod: vy-red-team-flock q59un0g9p7x5qz (cpu3c 16 vCPU) terminated 12:49Z; also x8gaf462paw582 and m7aqz4bhaf9640 (vanished about 2 min after launch, probably the steward's final-lane pod reaper acting on my 11:27Z FINAL) and 18ubkjsgz9amop (404 at registration); total re-audit spend about $0.2
artifacts: art:1bd3368b art:12a6b845 (and, from the first audit, art:8d04b53f)
~~~

Runs r20260925-123224-2230 and r20260925-123625-6a37 were lost with their pods, before any result. They are superseded
by r20260925-124333-1a03 and r20260925-124555-21d5 (the same script). Handoffs written:
`lanes/coordinator/20260925T1255Z-handoff-from-red-team-flock.md` only. flock-live, flock-glue, agkr-bound and
flock-128 are all final, so per contract §5 the coordinator's copy stands in for theirs.

# Third audit (15:41–16:05Z): flock-link @ 4b560b2b, L1–L4, F2 and F3 on CPU (PR #25)

**Grant for route (a) on CPU: GRANTED WITH CONDITIONS.** The Flock half of route (a) is granted, together with the link
exchange (L1–L4, F2, F3 hold). Route (a) as a whole still has **no 2^-128 Table 2 cell**: the prime side isn't in the
session yet (P1–P3 below), and the evidence gate isn't enforced in code (E1).

**Composed whole-proof bound: 2^-130.2 on the A-GKR route (statistical terms, CPU, 4,096 BF16 VUs), set by A-GKR.**
It's 2^-127.7 if the accountant counts A-GKR's hash budget (C8, still open). The table is below.

Inputs:
- flock-link's report (`lanes/flock-link/20260925T1430Z-report-flock-link.md`);
- the code at `origin/lane/flock-link` 4b560b2b: the lib.rs diff, `flock-link.rs` and `flock-link-b684b12.patch`, all read;
- F1 evidence art:00da1ce8: three session records, fetched and inspected.

Handoffs received: none new.

My run: r20260925-155333-c658, **art:20545959** (vus 8 and 64). Harness `evidence/rtf_link_attacks_tail.rs`; script
`evidence/pod-scripts/30-link-attacks.sh`; results `evidence/rtf-link-attacks.tsv`. flock-link's own selftest
reproduces there: 56 of 56 cases pass, including L3.

## Attacks (vus 8 and 64; all at the same outcome on both)

| attack | cond | result | stopped by |
|---|---|---|---|
| **y withheld until after every Flock coin, verifier configured `link: Some` with `require_link: false`** | L1/R5 | **ACCEPTED**; the record says `link_mode: "exchange"` | nothing. The library lets an exchange-mode session run without the R5 gate |
| the same with `require_link: true` (the shipped default) | L1/R5 | rejected | R5 gate |
| y1 and y2 swapped on the wire | L2 | rejected (both reps) | ring switch `ClaimMismatch` |
| y from other operands (bits flipped in both y) | L2 | rejected | ring switch |
| Commit with an extra table | L1/L3 | rejected | table-set check |
| Commit before Hello | L1/R7 | rejected | R7 |
| committed public chunk values of leaves 0 and 1 swapped | L4 | rejected | C4 native tree check at Commit |
| rep 1 proves another witness | L1/R1 | rejected | R1 |
| honest control | – | accepted | – |

Why the first row is a real break when reachable: if y is chosen after Flock's opening coins, the prover can pick false
(y1, y2) that cancel in the merged opening's random combination. That's red-team-link's trap 1, and the prime side
would then prove b̂(r) = y for b ≠ z. The shipped `flock-link serve` never builds that configuration: it uses
`flock_128_r2` defaults and has no `--no-link` flag. But nothing in the library or the evidence path refuses it, and
the record's `link_mode` doesn't reveal it.

## Verdicts
- **L1: HOLDS in the shipped configuration.** The order is enforced: Hello, then Commit (root_F non-empty and every
  root_B together), then points from the OS, then y (exact length), then Flock's coins. Each rep's binding round equals
  the committed root_B and rep 0's root. Condition **E0**: the library must refuse `link: Some` with
  `require_link: false`, or make the exchange imply the gate.
- **L2: HOLDS.** The link claims are appended to each rep's merged opening from the verifier's record.
  - The points and y are fixed before any Flock coin, so each rep's batched reduction draws fresh coins after y. Its
    error is a round-by-round bound of about 2m/2^128, independent across reps: (66/2^128)^2 ≈ 2^-243.9 at m = 33.
    Schwartz–Zippel over the two shared points is (28/2^128)^2 = 2^-246.4.
  - `Chain::embed` checks out. It puts link bits 0–6 on the in-word bits, link bits 7–8 on columns 4 + u/128 (`M_BASE`
    = 512: message words 4–7, exactly the compression's consumed inputs), row bits on ν, and fixes the column and slot
    bits. It agrees with `link_eval`'s position order (row·512 + u = (l·K + k)·16 + i for LE 16-bit words in LE 32-bit
    message words).
  - **Honest-zero padding (flock-link's question): confirmed benign.** Claims are checked against the height-n_t dense
    stack, and rows ≥ n_t are dropped from the commitment: in my first audit, a buffer with dirty padding gave the same
    root as zero padding. Link positions ≥ N are zero on the prime side too.
- **L3: HOLDS as tested** (one Σ, one Commit with every root, one y per table; flock-link's L3 negatives reproduce).
  For CPU route (a) it isn't needed: the Flock side is a single chain table, and the census unit lives on the prime
  side. The commit-only pass is prover-side only; the verifier checks the rep binding against the committed root.
- **L4: HOLDS.**
  - The chunk chain is wired: IV and params (counter = chunk index, block_len 64, START/0/END) are fixed publics, and
    chunk CVs are public.
  - The verifier checks the CVs natively through the BLAKE3 tree (`parent_cv` with PARENT/ROOT, left-balanced) against
    the configured leaf digests, before drawing the points. The publics digest is bound in each rep.
  - Leaves are at least two chunks, so no single-chunk ROOT case exists.
  - A forged middle block, a wrong counter/flag/len, a forged public, and swapped leaves are all rejected.
- **F2: HOLDS by reading** (plus flock-link's `selftest-f2`). The route (a) production verifier is `ChainVerifier`:
  circuit digest, registry digest, counts, Fast100 params and publics digest are all pinned from the configuration.
- **F3: HOLDS** (flock-live selftest cases).
- **`link_mode: "exchange"` in evidence: NOT ENFORCED (E1).** The record carries `link_mode`, `require_link`, `link`
  (Σ, roots, points, y) and `link_sha256`. No code, and no store check or label gate, refuses a stub or ungated
  record. A stub record from `flock-live serve` has `require_link: true` and a non-null `link_sha256`, so my earlier F1
  wording would have admitted it. F1 is corrected to E1:
  - `link_mode == "exchange"`;
  - `config.require_link == true`;
  - Σ in `hello` equals the cell's Σ;
  - the record's points and y are the ones the prime proof used (P1);
  - the verifier is operated by a non-producer lane. art:00da1ce8 ran on flock-link's own second pod, so it is
    cross-pod, not non-producer.
  - The proofs themselves must be preserved beside the records. The verifier art holds only proof sha256s.

  The three art:00da1ce8 records otherwise pass E1's field checks (exchange, gated, one Σ 07ac86d6…, 2 × 28-coordinate
  points).

## Open items (route (a) conditions; not Flock's)
- **P1:** the prime proof must take its link points (and y) from this session's record, not from its own Fiat–Shamir
  transcript. root_F must be the prime side's real first commitment (it's a stand-in hash today). Then the Flock
  session and the prime proof are provably about the same (root_F, points, y).
- **P2:** the prime side uses **two GF(2^128) points** (as this session draws), not agkr-bound §17's single
  GF(2^256) point. Its σ form runs unchanged with 2 × 128 σ values. Either side can change, but they must match, and Σ
  must name the choice.
- **P3: leaf format mismatch.** The Flock side proves plain BLAKE3 row leaves (`flock-link/blake3-row/v1`), while
  agkr-bound's operands-committed statement uses `sha256/row/v1` (prefix64 + SHA-256). A cell's commitment scheme
  fixes the leaf hash, so one side must change:
  - either a SHA-256 chunk-chain circuit on Flock, with the verifier-computed prefix midstate as a fixed public and
    red-team-link F2's big-endian Λ;
  - or the cell's scheme moves to the BLAKE3 row leaf.

  Until then the two halves prove different statements.
- **GPU:** no route (a) on Flock-CUDA (no wiring argument, no link opening). No GPU cell.

## Composed bound (CPU, 4,096 BF16 VUs, with P1–P3 and E0/E1)

| term | value |
|---|---|
| ε_F, A-GKR (BabyBear^6, interactive, t = 192) | 2^-130.2 (2^-127.7 with the hash budget) |
| ε_B, Flock r2 (dense m = 33; queries 2^-97.77 per rep; wiring-GKR fingerprint about 2^22/2^128 = 2^-106 per rep, not in flock-128's ledger but inside the 2^-97.76 per-rep total) | about 2^-195.5 |
| ε_red, link claims in both reps | about 2^-243.9 |
| ε_SZ, two GF(2^128) points, m = 28 | 2^-246.4 (× the prime side's list factor, if any) |
| ε_ρ, prime-side σ combination | ≤ 2^-177 |
| **whole proof** | **2^-130.2** |

## Third-audit FINAL

~~~text
tip: none (no repo commits; notes + evidence only)        merge-with: none
known-failures: none    pod: vy-red-team-flock chh9hgfare2i1l (cpu3c 16 vCPU) 15:53–15:57Z, terminated; about $0.05
artifacts: art:20545959 (and, read, art:00da1ce8)
~~~

Handoff: `lanes/coordinator/20260925T1600Z-handoff-from-red-team-flock.md`. flock-link and agkr-bound are final, so the
coordinator's copy stands in for theirs.

# Fourth audit (18:32–18:50Z): route (a) cell art:8f7ef58b (agkr-flock-cell, PR #28 @ c95dd13a)

**Grant: GRANTED WITH CONDITIONS at `proof_class = NON_ZK_PROOF_DIAGNOSTIC`,** a downgrade from the claimed
`NON_ZK_PROOF`.

**Bound: 2^-130.19 at the current hash convention,** in A-GKR's interactive model. Two things depend on Daniel's
rulings (see Dependencies).

**cell-verifier does not count as a non-producer.**

Labels (by red-team-flock, on both local and remote) on art:8f7ef58b:
- `proof_class=NON_ZK_PROOF_DIAGNOSTIC`;
- `finding=...`.

Their ref is `lanes/coordinator/20260925T1905Z-handoff-from-red-team-flock.md`. The filename stamp is ahead of the true
write time, about 18:43Z.

Handoffs received: `20260925T1835Z-handoff-from-coordinator.md` (REOPEN for the fourth audit). This section is the
answer to it.

Inputs:
- agkr-flock-cell's handoff to the coordinator at 18:30Z (the re-audit request);
- PROTOCOL §17.5, `cell_gate.py`, `gpu/link.py`, `gpu/transcript.py`, `soundness.py`, `cell.py`, `verifier/src/link.rs`
  and flock/live `lib.rs` / `flock-link.rs`, all at c95dd13a;
- the verifier records art:3b185b68 (round 2) and art:5a7ccc3b (round 1);
- the prover run art:9464fe7a;
- the result manifest art:8f7ef58b.

No pods were used: the re-run was local, a 4-core VM with its own `verity-gkr-verify` build at 12 s. Spend $0.

## Store re-run of the E1 gate (non-producer)

`evidence/cell-gate-rerun/`:
- The 5 round-2 records were paired with prover sessions s1–s5 by `link_txt` equality (s0 was the warm-up, against
  another verifier, and isn't evidence).
- All 5 were **admitted**. The prime check was the Rust verifier: accepted, circuit pinned, commitment pinned, 6.7 s
  at 4 threads.
- Negatives, all rejected:
  - n1: the proof cross-paired onto another record (sigma_0 parity);
  - n3: sigma.txt edited (Σ mismatch, and the prime verifier refuses);
  - n4: commitment.txt edited (pin);
  - n5: the record's y edited after the fact (sigma parity);
  - n6: the operator listed as a producer.

## Verdicts
- **E0: HOLDS.** `SessionConfig::check` (called from `Server::new` and `try_new`) refuses an exchange without the gate,
  and the R5 gate fires whenever `link` is set. `backends/flock` is identical between the verifier's source a83d7de7
  and the tip.
- **E1: HOLDS for the listed checks, with gaps G2 and G3:**
  - The gate trusts the record's Flock verdict. The record keeps `publics_sha256` but not the committed public chunk
    words, so no one else can replay the Flock verification offline.
  - `non_producer` is self-declared (`verifier.json` operator vs a caller-supplied producer list), and
    `runpod_pod_id` is null, so the pod check is vacuous.
- **P1: HOLDS.** root_F (SHA-256 over the prime transcript state after the Ligero root and the GKR messages) is sent in
  Commit before the OS points. The prime transcript absorbs Σ, root_B, the points and y. The Rust verifier recomputes
  root_F and reads the context from the record's `link.txt`.
- **P2: HOLDS.** Two GF(2^128) points, m = 28, 256 σ planes; Σ v2 names the choice.
- **P3: HOLDS.** The keyed-BLAKE3 row leaf. The Flock verifier's leaf digests enter Σ, and the prime verifier checks Σ's
  leaf-digest line against its pinned public digests, so the producer-supplied `leaf_digests.bin` is cross-checked.
- **L1–L4, F2, F3: met** (the CPU path, unchanged from the third audit). F1/E1's non-producer part is not met (below).
- **Non-producer: NO for TABLES criterion 6.**
  - cell-verifier was launched and directed by the producer. The principal chain is the producer's, and its
    independence is procedural only.
  - It is sufficient as the protocol's live verifier: a separate pod, OS coins, records under its own preserved
    attempts, and the audited build.
  - My store re-run is independent for the prime proofs and the record fields, but not for the Flock verdict (G2).
- **Class: DOWNGRADE to NON_ZK_PROOF_DIAGNOSTIC.**
  - The prime proof's coins (the GKR challenges, rho, the Ligero queries) come from the prover's own SHA-256 transcript
    (`gpu/transcript.py`: "Fiat-Shamir is what the CPU prover uses too (the interactive object ... not implemented);
    the diagnostic label stays NON_ZK_PROOF_DIAGNOSTIC"; PROTOCOL §0's label rule).
  - The cell nevertheless writes `proof_class="NON_ZK_PROOF"` and `mode: interactive`. That mode string is true only
    for Flock and the link points.
  - NON_ZK_PROOF_DIAGNOSTIC is in A-GKR's declared class (TABLES), so the cell can still fill Table 2.
- **Composed bound: 2^-130.19 at the current convention.**
  - Prime terms: encoding/opening (Ligero queries) 2^-130.19, lookup 2^-158.6, batching 2^-164.18, sumcheck 2^-176.41,
    commitment hash (SHA-512, q²/2^512 at q = 2^64) 2^-384, σ batching 255/p^6 ≈ 2^-177.6, and Schwartz–Zippel over two
    GF(2^128) points 2^-246.4.
  - Flock and link terms: Flock r2 2^-195.5, and the link reduction in both reps 2^-243.9.
  - The sum is 2^-130.19.

## Dependencies (to Daniel)
1. **Hash convention.** Counting q²/2^256 for every 256-bit hash adds about 2^-128 each for:
   - Flock's BLAKE3 Merkle trees;
   - the SHA-256 root_F / Σ binding;
   - the row-leaf / frame-v3 binding.

   That gives about 2^-126.5 to 2^-127, below 2^-128. The fix is 512-bit digests in Flock and root_F, or a smaller q.
2. **Fiat–Shamir vs live for the prime half.** TABLES currently footnotes such results as "file re-verification
   replaying the runner's coins, not transferable". The campaign's ×2^60 FS rule, which red-team-flock applied to Flock
   and is why flock-128-r2 is live, would put the prime half at 2^-70.2. Serving the prime coins from the same live
   session would lift both the class (to NON_ZK_PROOF) and this dependency.

## Conditions
- **G1:** the cell footnote states that the prime coins were runner-derived (FS, not transferable) while Flock and the
  link were live. The class is NON_ZK_PROOF_DIAGNOSTIC.
- **G2:** the session record keeps the Commit's public words (and the root bytes), and an offline Flock replay tool
  replays records plus proofs.
- **G3:** a non-producer verify lane runs the gate and replay from the store and labels `verified`. By the contract I
  don't.

## Fourth-audit FINAL

~~~text
tip: none (no repo commits; notes + evidence + labels)        merge-with: none
known-failures: none    pod: none (local re-run); $0
artifacts: art:8f7ef58b (labelled) art:3b185b68 art:9464fe7a art:5a7ccc3b (read)
~~~

Handoff: `lanes/coordinator/20260925T1905Z-handoff-from-red-team-flock.md`. agkr-flock-cell and cell-verifier are
final, so the coordinator's copy stands in for theirs.

# flock-pure-block/v2 review (20:41–21:20Z; ordered ahead of the route (a) re-audit)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF.** The whole-proof bound is 2^-195.44 per 8,192-VU proof, and 2^-193.44 over
a 32,768-VU batch of 4 sub-batches, at the current hash convention. Labels are on art:ca6029c1.

Detail: `lanes/coordinator/20260925T2120Z-handoff-from-red-team-flock.md`.

Evidence:
- a rerun of the producer's CPU selftest at d3e96304: 18/18 at 8 and 64 VUs (run r20260925-210925-a744,
  **art:ac1aeeeb**; script `evidence/pod-scripts/40-pure-selftest.sh`);
- a local check of the lowering: the netlist sha equals PINS, all rows are topological with 33 assertion rows, and 400
  random units differ from `verity.ml.tc` in 0 cases, including subnormals and extreme exponents.

Conditions:
- **PB1:** each result names the verifier commit and binary. art:ca6029c1 has `commit: "unknown"`.
- **PB2:** the security block reports the union over sub-batches.
- **PB3:** a non-producer replay labels `verified` (verify-flock-pure).
- **PB4:** each evidence record carries `link_mode` exchange, `require_link` true, and the cell's Σ.
- **Dependency:** the hash convention, for Flock-CUDA's SHA-256 Merkle trees.

Pods: the first vy-red-team-flock pod (mm6men5q8u23gn) never got an IP, and I terminated it. n3xdvq91lphcno ran from
20:57 to 21:14Z. About $0.15. The first launch, r20260925-205906-e9ea, failed on a path (inputs vs --cwd source) and is
superseded by r20260925-210925-a744.

Handoffs received:
- `20260925T2045Z-handoff-from-coordinator.md` (this review);
- `20260925T2050Z-handoff-from-coordinator.md` (order change: this review first).

# Fifth audit (20:29–21:25Z, paused 20:41–21:20Z): route (a) with live prime coins (PR #36 @ dec08973, art:3bfb2f58)

**GRANTED WITH CONDITIONS at NON_ZK_PROOF.** Live prime coins close the fourth audit's Fiat–Shamir downgrade. The bound
is 2^-130.19 at the current convention. Labels are on art:3bfb2f58.

Detail: `lanes/coordinator/20260925T2125Z-handoff-from-red-team-flock.md`.

My store re-run (local, own `verity-gkr-verify` at dec08973, records art:42841b22, proofs art:d9666f5a):
- every gate check passes on 5 of 5 sessions except `non_producer` (a producer-operated verifier);
- the negatives were rejected: cross-pair, a coin word, the post-y state, a before_commit shift, the prime record
  removed, and a Fiat–Shamir proof on a live record.

Evidence files:
- `evidence/cell-gate-rerun/live-coins/gate-s1..s5.json`;
- `evidence/cell-gate-rerun/live-coins/neg-*.json`.

Conditions:
- **RA1 (DoS):** dropping the last prime round makes the Rust verifier spin for more than 35 minutes. It must fail fast.
- **RA2:** fix the stale `prime.sequential_depth: 328`. The real count is 3,006 prime rounds plus 1,070 Flock rounds.
- **RA3:** MET, by verify-night-3's non-producer re-run (`verified=accepted`, 20:53Z).
- **Dependency:** the hash convention (as in the fourth audit).

## Fifth-audit FINAL

~~~text
tip: none (notes + evidence + labels)        merge-with: none
known-failures: none    pod: n3xdvq91lphcno terminated 21:14Z, mm6men5q8u23gn terminated (never up); ~$0.15
artifacts: art:ac1aeeeb art:ca6029c1 (labelled) art:3bfb2f58 (labelled) art:42841b22 art:d9666f5a (read)
~~~

Handoff received: `20260925T2100Z-handoff-from-coordinator.md`, a queued class review of the fp8-ada block layout (PR #30 @
48045063, RTX 4090). **Not done yet.** This turn's instruction was pure-block first, then route (a). The fp8-ada layout is
next when relaunched. Its layout (4f7db693 / 48045063) changes `pure_block.rs`, so it needs its own review; the bf16
grant above doesn't cover it.

# Decision 57 (21:21Z) and the fp8-ada block layout review (21:22–21:35Z)

**Decision 57:** hash collision resistance is a Table 1 assumption, and the 2^-128 filter covers statistical soundness
only, so q²/2^256 hash terms don't count. This withdraws the hash-convention dependency in both earlier findings. I
recorded it as a `finding` label, by red-team-flock, on each of:
- art:ca6029c1 (flock-pure-block/v2, H100);
- art:3bfb2f58 (route (a), live coins).

**The fp8-ada block layout (PR #30 @ 48045063) is GRANTED WITH CONDITIONS at NON_ZK_PROOF:** 2^-195.54 per 4,096-VU
proof, as a union over sub-batches. Detail: `lanes/coordinator/20260925T2135Z-handoff-from-red-team-flock.md`.

Evidence:
- **art:1f2fe1e9** (run r20260925-212534-f9f0): fp8 selftest 16/16 at 8 and 64 VUs, bf16 regression 18/18, loopback
  statement digests;
- the local fp8-ada lowering check: the pin matches, the rows are topological, and 400 units show 0 mismatches.

Conditions:
- PB1–PB4, as for the bf16 cell;
- **FA1:** a separate-pod verifier;
- **FA2 (hardening):** fp8 negatives for c_in(0) and the output word.

No fp8 bench-result exists yet, so nothing is labelled.

Pod: wi5bujxxm0stz9 (cpu3g), 21:23–21:31Z, about $0.10. Script: `evidence/pod-scripts/50-fp8-selftest.sh`.

# Labels and the 4090 check (21:35–21:45Z)

**Route (a):** `proof_class=NON_ZK_PROOF` and a `finding` written on art:4b52879f (4,096 VUs) and art:aa9223c2 (1,024
VUs). Both re-derive the same runs. RA1 is fixed at 504f75b6: my local rebuild rejects the dropped-round record in
0.6 s. RA2 is fixed: sequential depth 4,076.

**RTX 4090 fp8-ada, art:949bcc35:** PB2, PB4 and FA1 are met, and PB3 is pending (verify-flock-pure). PB1 is missing in
the record: it says `commit: "unknown"`. The runs' source e5d54118 has a verifier path equivalent to the reviewed
48045063, so the gap is metadata only. I didn't label it; the re-registered id gets the label.

Detail: `lanes/coordinator/20260925T2145Z-handoff-from-red-team-flock.md`.

Handoffs received, all acted on above:
- `20260925T2140Z-handoff-from-coordinator.md`
- `20260925T2145Z-handoff-from-coordinator.md`
- `20260925T2210Z-handoff-from-route-a-live.md`

# Re-registered cells labelled (22:19–22:25Z)

`proof_class=NON_ZK_PROOF` written on:
- art:6d1295ed (H100 bf16-hopper, verifier commit a6a6e548);
- art:d1961ba4 (RTX 4090 fp8-ada, verifier commit d93ce18b);
- art:3d7cbea2 (route (a), superseding art:4b52879f).

Both verifier commits have zero `backends/flock` diff from e5d54118, which is equivalent to the reviewed 48045063 path.
Each verifier run's source sha matches the result's named commit. Detail:
`lanes/coordinator/20260925T2225Z-handoff-from-red-team-flock.md`.

Handoff received: `20260925T2225Z-handoff-from-route-a-live.md` (the art:3d7cbea2 request). Acted on above.

art:77411c93 (route (a), the same runs re-registered once more, with `live.loopback_round_seconds`) is also labelled
`NON_ZK_PROOF`.

Handoffs received:
- `20260925T2220Z-handoff-from-coordinator.md` (label the new route (a) id): done, art:77411c93;
- `20260925T2218Z-handoff-from-flock-backend.md` (the re-registered Flock cells): done, art:6d1295ed and art:d1961ba4.

# fp8-hopper and bf16-ampere layouts (23:05–23:20Z)

Both are **GRANTED WITH CONDITIONS at NON_ZK_PROOF.**
- **fp8-hopper:** the pin 904ca664 matches, and the differential test and selftest pass. The bound is 2^-195.44 to
  2^-195.54 per proof.
- **bf16-ampere:** the netlist is e97ecb9e…, and the differential test and selftest pass. It needs **AM1**: the pin
  added to `lowering.py`.

Evidence:
- **art:0f0b6f41** (run r20260925-230859-6d32): fp8-hopper 16/16 and bf16-ampere 18/18, at 8 and 64 VUs each;
- the local differential tests: 400 + 400 units, 0 mismatches.

Other conditions: PB1–PB4 and FA1, with FA2 as hardening.

Detail: `lanes/coordinator/20260925T2320Z-handoff-from-red-team-flock.md` (a copy is in `lanes/flock-backend/`).
Pod pod9bu9s1938uo, 23:08–23:15Z, about $0.10.

Handoffs received:
- `20260925T2242Z-handoff-from-flock-gpu-link.md`: done, fp8-hopper;
- `20260925T2250Z-handoff-from-flock-gpu-link.md`: done, bf16-ampere.

# sha256/row/v1 layouts (23:15–23:32Z)

ShaFp8 is **GRANTED WITH CONDITIONS at NON_ZK_PROOF.** ShaBf16, which has landed in the code but hasn't been handed off
yet, is pre-reviewed with the same result.

Evidence:
- **art:08295fa2** (run r20260925-232225-1b40): the SHA selftests pass 13/13 ×4, and the BLAKE3 regression 16/16;
- my own sha256/row/v1 instance generation passes the verifier's native root check;
- `sha256_row_digest` == SHA-256(prefix‖row), checked locally.

Conditions: PB1–PB4, FA1, **SH1** (the instances scheme switch), and **SH2** (hardening: a consistent-chain
wrong-digest negative and an output-forge negative).

Detail: `lanes/coordinator/20260925T2332Z-handoff-from-red-team-flock.md` (a copy is in `lanes/flock-backend/`).
Pod d2hm2vfd1a98h4, 23:22–23:28Z. An earlier create hit an HTTP 500, and the mirrored machines.d entry went stale
again, so I re-registered.

Handoff received: `20260925T2315Z-handoff-from-flock-gpu-link.md`. Done.

Spend this session: 3 CPU pods, about $0.30 in all.

# SHA combinations (23:35–23:40Z)

ShaBf16 × bf16-hopper, ShaBf16 × bf16-ampere and ShaFp8 × fp8-hopper are **GRANTED WITH CONDITIONS at NON_ZK_PROOF**.
ad0aa41d is prover-only relative to 7e640265, and the coverage comes by composition from art:08295fa2 and art:0f0b6f41.

I couldn't rerun the two new combinations: RunPod had no CPU stock (HTTP 500).

Detail: `lanes/coordinator/20260925T2340Z-handoff-from-red-team-flock.md` (a copy is in `lanes/flock-backend/`).

Handoffs received:
- `20260925T2323Z-handoff-from-flock-gpu-link.md`: done;
- `20260925T2328Z-handoff-from-flock-gpu-link.md`: done;
- `20260925T2330Z-handoff-from-flock-gpu-link.md`: done.

# Flock over vllm-v1 (23:41–23:55Z): BLOCKED on source access

Detail: `lanes/coordinator/20260925T2355Z-handoff-from-red-team-flock.md`.
- GitHub auth on the VM returns 401, so I can't fetch ff1c1e3f.
- **The per-proof bound is confirmed at 2^-195.44** (m = 35, 6 claims), and 2^-193.44 over the 4 sub-batches.
- The evidence records check out (art:15724f03, art:56f792bd).
- The design note is consistent with the vllm-v1 leaf spec.
- The code review and the selftest rerun are pending source access.

Handoff received: `20260925T2337Z-handoff-from-flock-vllm-v1.md`. It isn't mirrored yet; I worked from the user's
wake message and the design note.

# H100 re-run label and the flock-vllm-block/v1 review, completed (23:55Z–00:15Z)

- **art:1589ffe1** (H100 bf16, verifier commit 0864d146, which is a6a6e548 plus a stateless Ping) is labelled
  `NON_ZK_PROOF` under the v2 grant. Merge hazard: Ping and route (a)'s Prime both use request tag 8. Detail:
  `lanes/coordinator/20260926T0010Z-handoff-from-red-team-flock.md`.
- **verity/flock-vllm-block/v1 @ ff1c1e3f** (reviewed from the bundle) is GRANTED WITH CONDITIONS at NON_ZK_PROOF, and
  **art:56f792bd** is labelled. Evidence: CPU selftest 21/21 at 8 and 64 VUs, Rust vector tests 6/6, **art:c30bb647**.
  Conditions: PB3 pending, and VL1 (hardening: a native a/b root recompute). Detail:
  `lanes/coordinator/20260926T0015Z-handoff-from-red-team-flock.md`.

Pod fdvuqjm0b0w4kc, 23:57–00:05Z. GitHub access is working again (`ls-remote` succeeds).

Handoff received: `20260926T0005Z-handoff-from-coordinator.md`, the PR #41 bundle with tip cfc6c8c5. Answered by the
review above, which is of ff1c1e3f. cfc6c8c5 adds only `verity_flock.register` changes (bb4952a6, cfc6c8c5) and no
`backends/flock/live` change, so the verifier path is identical.

# SHA-256 cells labelled and the NVFP4 unit reviewed (01:06–01:15Z)

- **Labelled `NON_ZK_PROOF`:** art:728d8724, art:df857ea6, art:fd772057 and art:324888c5. Their verifier commits
  (c058c33f, bab181d6) are equivalent to the granted ad0aa41d verifier path. Each reports its union, has a separate-pod
  verifier, and meets SH1 and AM1.
- **The fp4-nvf4 unit circuit (pin fb52a87c) is GRANTED WITH CONDITIONS:** the pin is regenerated, and my differential
  test found 1,800 units with 0 mismatches. Conditions: FP1 (pin it in PINS) and FP2 (the Fp4 block layout review).
- **Scripts** added to `evidence/`: `diff_fp4.py`, `diff_gen.py`, `diff_unit.py`, `diff_fp8.py`.

Detail: `lanes/coordinator/20260926T0115Z-handoff-from-red-team-flock.md`.

Handoffs received:
- `20260926T0033Z-handoff-from-flock-gpu-link.md` (NVFP4): done;
- `20260926T0043Z-handoff-from-flock-gpu-link.md` (SHA device witness, prover-only): noted, and the verifier is
  unchanged in the labelled cells.

art:167e64a8 (A100 bf16-ampere, keyed-BLAKE3) is labelled `NON_ZK_PROOF`. Its verifier commit is e52eca82 = a6a6e548 +
Ping, on a separate pod (ver9), with 6/6 sessions. Detail: `lanes/coordinator/20260926T0120Z-handoff-from-red-team-flock.md`.

Also labelled `NON_ZK_PROOF`: art:c3e83404 (H100 fp8-hopper) and art:7afeecbe (RTX 4090 fp8-ada), both with verifier
e52eca82 on a separate pod and 6/6 sessions.

Handoffs received:
- `20260925T2348Z-handoff-from-flock-backend.md`: its cells are superseded, so none are labelled;
- `20260925T2352Z-handoff-from-flock-backend.md`: art:1589ffe1 labelled at 00:04Z;
- `20260926T0003Z-handoff-from-flock-backend.md`: art:167e64a8, c3e83404 and 7afeecbe labelled;
- `20260926T0106Z-handoff-from-flock-backend.md`: the four SHA-256 cells labelled at 01:15Z.

## Sixth audit (04:20Z): the Chunk(n) layouts and the bf16-hopper-wgmma pin

GRANTED WITH CONDITIONS (CN1 NV1, CN2 m ≤ 35, CN3 no Chunk(1), plus PB1–PB4). The wgmma pin 12c3c8d3 is GRANTED.
Details are in note `lanes/coordinator/20260926T0420Z-handoff-from-red-team-flock.md`. Evidence: my run
r20260926-034703-978c. Earlier on the same watch (03:30Z), I checked NV1 against the nine published Flock cells. Their
verifier files are consistent, so the grants stand, with NV1 added as a condition before the next publish.

Handoffs answered by this audit:
- Chunk(n) and wgmma notes, all covered by the grant above: 20260926T0159Z-handoff-from-flock-gpu-link.md,
  20260926T0205Z-handoff-from-flock-gpu-link.md, 20260926T0208Z-handoff-from-flock-gpu-link.md,
  20260926T0220Z-handoff-from-flock-gpu-link.md, 20260926T0222Z-handoff-from-flock-gpu-link.md,
  20260926T0226Z-handoff-from-flock-gpu-link.md, 20260926T0315Z-handoff-from-flock-gpu-link.md,
  20260926T0319Z-handoff-from-flock-gpu-link.md.
- NVFP4 notes, reassigned to red-team-flock-2 (its 0310Z grant with NV1–NV3): 20260926T0236Z-handoff-from-flock-gpu-link.md,
  20260926T0255Z-handoff-from-flock-gpu-link.md, 20260926T0300Z-handoff-from-flock-gpu-link.md.
- flock-backend's note: 20260926T0106Z-handoff-from-flock-backend.md (the wgmma pin), granted above.
- flock-vllm-v1's review request: 20260925T2337Z-handoff-from-flock-vllm-v1.md, granted 00:15Z.

04:35Z: flock-gpu-link's e4f631bd enforces CN1–CN3 in admission, and that matches the grant. Details are in note
`lanes/coordinator/20260926T0435Z-handoff-from-red-team-flock.md`. It answers 20260926T0422Z-handoff-from-flock-gpu-link.md
and 20260926T0429Z-handoff-from-flock-gpu-link.md.

## Per-cell labels (05:20Z): eight real-K Chunk(n) and wgmma cells

All eight meet PB1–PB4, CN1 and CN2, and are labelled NON_ZK_PROOF with verified=accepted. My replay run is
r20260926-050108-7fa6: 60 of 60 sessions accepted, and 20 of 20 negatives rejected. In both wgmma cells, y is the
Hopper model chain on captured A100 inputs; it differs from the recorded set in 1 word at K 2048 and 3 words at
K 8192. The tier suffix is right, but "source: captured" covers only x and W. Detail is in note
`lanes/coordinator/20260926T0520Z-handoff-from-red-team-flock.md`. This answers
20260926T0452Z-handoff-from-flock-backend.md.

## Spine FP8 cells (06:40Z)

art:5d2a91a7, ab115376, 66d2412c and 1c520240 meet PB1–PB4, CN1 and CN2, and are labelled NON_ZK_PROOF with
verified=accepted. My replay run is r20260926-061513-ad9c: 48 of 48 sessions accepted, and 16 of 16 negatives rejected.
The old four now carry `superseded_by`, but `store_tables.py` doesn't read it yet. Detail is in note
`lanes/coordinator/20260926T0640Z-handoff-from-red-team-flock.md`. This answers
20260926T0605Z-handoff-from-flock-backend.md.

## Route (a) real-K, the Chunk(n) extension, and 5090 placement (10:30Z)

- **Route (a) at K = 2048 / 8192:** GRANTED at NON_ZK_PROOF (2^-130.19). art:95fdd0ae and art:20197f8b are labelled.
  My CPU gate re-run passed on 10 of 10 sessions, and the 6 negatives were rejected.
- **Chunk(n):** extended to every n from 2 to 64 under CN2. My selftests at n = 5, 19 and 28 had all_pass.
- **5090 NVFP4 placement:** the cross-datacenter verifier at 3.2 ms still counts as separate (FA1). The cost is
  latency, not soundness.

Detail is in note `lanes/coordinator/20260926T1030Z-handoff-from-red-team-flock.md`. Evidence is in
`evidence/route-a-real-k/`. This answers 20260926T0930Z-handoff-from-agkr-real-k.md and
20260926T1000Z-handoff-from-flock-backend.md.

## L40S GEMM cells (10:30Z) and the ChunkTail block

art:df3d63e4 and art:8bc3dba2 meet PB1–PB4, CN1 and CN2, and are labelled NON_ZK_PROOF with verified=accepted. My CPU
replay accepted 6 of 6 sessions per cell. Detail is in note
`lanes/coordinator/20260926T1030Z-handoff-from-red-team-flock-l40s.md`. This answers
20260926T1003Z-handoff-from-flock-l40s-101.md.

The ChunkTail(n) review (20260926T1004Z-handoff-from-flock-gpu-link.md) is BLOCKED. af2c3015 can't be fetched (GitHub
401), and it isn't in the store. I've asked for a bundle in
`lanes/coordinator/20260926T1015Z-handoff-from-red-team-flock.md`.

## ChunkTail(n) (11:00Z)

GRANTED WITH CONDITIONS (CT1 scope, CT2 CN2 at n + 1 blocks per VU, CT3 host-built inputs only, plus CN1, CN3 and
PB1–PB4). My independent CPU selftests had all_pass at K 2304 and 8960 (bf16) and at K 2560 (fp8). Older layouts are
byte-identical: 5 recorded sessions replay accepted under af2c3015. Detail is in note
`lanes/coordinator/20260926T1100Z-handoff-from-red-team-flock.md`. This answers
20260926T1004Z-handoff-from-flock-gpu-link.md.

## Route (a) re-sweep and A-fs at real K (11:10Z)

- art:a0ca8ef6 and art:a979dfcb are labelled NON_ZK_PROOF. The statement rebuild is byte-identical, the gate passed on
  10 of 10 sessions, and the negatives were rejected.
- art:7ae6c190 and art:0e1095f3 (A-fs) are labelled NON_ZK_PROOF_DIAGNOSTIC. The transcript binds steps, units, the
  circuit and y; all 10 reps were accepted, and the relabel and tamper negatives were rejected.

Detail is in note `lanes/coordinator/20260926T1110Z-handoff-from-red-team-flock.md`.
