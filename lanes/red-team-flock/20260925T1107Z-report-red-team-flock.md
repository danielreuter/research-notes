---
lane: red-team-flock
kind: report
created: 2026-09-25T11:07Z
status: open
---

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
