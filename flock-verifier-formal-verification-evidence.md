---
cursor:
  subagentId: "bc-7e2e5d34-e769-50e1-b0f4-2b53bf6e3dd0"
---

# Evidence for the Flock-verifier formal-verification study

Backs [`docs/flock-verifier-formal-verification.md`](../docs/flock-verifier-formal-verification.md). Collected Sat Sep 26, 2026, 7:00–8:00 PM UTC on the agent VM: Intel Xeon, 4 vCPUs with AVX-512, SHA-NI and PCLMULQDQ, 15 GB. No pods, no repository changes. Everything ran in `/tmp`, which does not persist.

## 1. The two X posts

X returns 403 to fetchers; both were read through the fxtwitter API (`api.fxtwitter.com/status/<id>` and `/2/thread/<id>`).

- **Quang Dao, May 12, 2026 (`2054320851433218375`), an 11-post thread.** Introduces VCVio (`github.com/Verified-zkEVM/VCV-io`), "a base layer for crypto proofs in Lean", with Devon Tuma, Alexander Hicks, James Waters and Nick Hopper; companion paper ePrint 2026/899. Oracle computations are free monads over polynomial functors, with handlers for logging, caching, reprogramming and rewinding. The program logic extends Loom (POPL 2026), with EasyCrypt-like tactics built on Lean's `mvcgen`. It claims the first foundational mechanization of the Bellare–Neven forking lemma, and Schnorr EUF-CMA without rewindability axioms. ArkLib adopts it as its base layer. The roadmap includes "verifying extracted Rust code". The last post credits Vitalik's Merkle-binding proof.
- **Vitalik Buterin, May 11, 2026 (`2053868260257353866`), replying to his own `2053868202443100265`.** The parent says "Getting increasingly bullish on just vibe-coding the important things in Lean", linking ArkLib and zkSecurity's post "The Final Form of Software Development" (Yoichi Hirai, Apr 29, 2026: agents write RISC-V assembly plus Lean proofs, 200–600 commits a day). The reply shows `theorem getPutativeRootWithHash_binding` in namespace `InductiveMerkleTree`: two proofs for different leaves at one index that give the same root yield a hash collision, proved by induction on the index. He adds that a reviewer need only check the theorem's statement and that Lean accepts it, and that "you can even write live production code (including eg. CLI tools) directly in Lean".

## 2. Repositories read (commit, size, admitted proofs)

| Repository | Commit (date) | Size | `sorry` |
|---|---|---|---|
| succinctlabs/flock | `b684b12` | flock-core 79,443 lines, flock-prover 52,648, flock-field 3,851, flock-merkle 2,268, flock-transcript 3,084 | — |
| Verified-zkEVM/ArkLib | `40c6adef` (Sep 26, 2026), Lean 4.34.0 | 908 files, 274,538 lines | see below |
| Verified-zkEVM/VCV-io | `f5119c64` (Sep 26, 2026) | 1,003 files, 258,863 lines | 29 |
| Verified-zkEVM/CompPoly | `631e72b0` (Sep 25, 2026), Lean 4.34.0 | binary fields: GHASH 3,822 lines, AES 428, additive NTT 5,617, towers 10,079 | 0, and no `native_decide` |

**ArkLib by area** (files, lines, `sorry` occurrences):

| Area | Files | Lines | `sorry` |
|---|---|---|---|
| ProofSystem/Sumcheck (all admits in the legacy `Spec/SingleRound.lean`; `Interaction/` has none) | 21 | 4,863 | 14 |
| ProofSystem/RingSwitching (Packing sumcheck phase 9, batching phase 5) | 15 | 3,407 | 18 |
| ProofSystem/Binius (Binary Basefold and FRI-Binius) | 11 | 6,769 | 32 |
| ProofSystem/Fri, BatchedFri, Stir, Spartan | 3, 3, 6, 1 | 1,205, 1,169, 1,370, 430 | 4, 6, 4, 8 |
| Data/CodingTheory/ReedSolomon, JohnsonBound, GuruswamiSudan, HiddenDerivative, PolishchukSpielman | 126, 6, 4, 119, 4 | 32,600, 2,380, 2,983, 29,271, 952 | 0 each |
| Data/CodingTheory/ProximityGap | 51 | 30,202 | 22 |
| Data/CodingTheory/ListDecodability | 20 | 12,164 | 6 |
| OracleReduction/FiatShamir, BCS, Composition, Security | 12, 1, 17, 20 | 1,767, 84, 4,553, 9,341 | 20, 2, 7, 17 |
| Interaction (the new typed layer) | 24 | 5,526 | 0 |

Specific statements checked:
- `rs_mcaError_le_in_johnson_range` (`ProximityGap/CapacityBounds.lean`) is `sorry -- ABF26-T4.12; external admit [BCHKS25 Thm 4.6]`, and its docstring says every Johnson-range witness in the tree is admit-backed.
- `RS_correlatedAgreement_affineLines` (BCIKS20 Thm 1.4): proved in the unique-decoding regime; the list-decoding branch is `sorry -- TODO: theorem 5.1`.
- `rs_epsCa_le_in_unique_decoding_range` (BCHKS25 Thm 1.3) and `rs_mcaError_le_of_le_relUDR` (BCIKS20, unique decoding): proved and "axiom-clean".
- AHIV22 (Ligero's Lemmas 4.3–4.5): proved. DG25 (interleaved-code gaps): 2 admits left in `MainResults.lean`.
- `docs/design/00-current-status.md` (dated Sep 26, 2026): sumcheck is the only protocol with full native soundness on the typed layer. FRI and Spartan slices are next (phase 3). The oracle-elimination compiler, typed BCS and Fiat–Shamir are phase 6, blocked on PolyFun and VCVio gaps. Legacy unrestricted composition theorems "remain admitted".
- VCVio's `Interop/`: "dormant" at its Lean 4.31 baseline. hax fails under 4.31, and the Aeneas bridge is disabled pending revalidation.
- CompPoly `Fields/Binary/Aes/Ghash.lean` proves the AES-to-GHASH field embedding and cites Flock's `crates/flock-field/src/phi8.rs` at revision `3877687`.

**Upstream Flock structure relevant to extraction:**
- `unsafe` occurrences: flock-core 242, flock-field 115, flock-merkle 36.
- 430 rayon parallel-iterator uses in flock-core, and 27 `dyn` uses in `verifier.rs` and `lincheck.rs`.
- Functions whose names contain `verif`: 5,513 lines over every variant. Our path, `verify_ligerito_extra`, is `verify_core_with_grinding` plus `verify_opening_batch_ligerito_mixed_with_grinding`.
- GF(2^256) is GF(2^128)[u]/(u² + u + x⁻¹), and φ₈ embeds AES-form GF(2^8) into GHASH-form GF(2^128).

## 3. Our live path (read from `backends/flock/live/src/lib.rs`)

- `Server` issues a coin only after it holds the preceding round. Its per-round work is recording `sha256(content)` and drawing OS coins.
- `Server::finish` runs the verifier for every table and every rep over the record, through `ReplayChallenger`: each squeeze checks the proof's framed bytes against the recorded SHA-256, then returns the recorded coin. So verification is already a replay after the session, off the coin path.
- Grinding is disabled: R4, where `verify_pow` only absorbs the nonce.
- Upstream's `FsChallenger` offers SHA-256, tree BLAKE3 and chained BLAKE3 (transcript-v2). In live mode no challenge is derived from a transcript hash.

## 4. Rust verifier measurements (upstream benches, `cargo +stable bench`, `target-cpu=native`)

The benches `verifier_hash_count` and `verifier_mul_count` needed stable Rust 1.98 (edition 2024). `verifier_hash_count` needed a one-line local fix for bit-rot, `proof.pcs_open.inner.ligerito`. The workload is upstream's BLAKE3 R1CS, verified single-threaded.

| m (K compressions) | Verify time | SHA-256 compressions (leaf + pair + PoW) | BLAKE3 FS compressions (est.) | Opening check (`verify_opening_batch_ligerito_mixed`) |
|---|---|---|---|---|
| 22 (256) | 12.2 ms | 5,771 | ≈ 912 | 0.73 ms |
| 26 (4,096) | 11.2 ms | 9,324 | ≈ 1,066 | — |
| 30 (65,536) | 13.9–14.1 ms | 13,293 | ≈ 1,223 | 1.65 ms |

- The `VERIFY_TRACE` split at m = 22 is ring switching 0.15 ms, jagged Frobenius assist 0.31 ms, and the whole opening batch 0.73 ms of 12.2 ms. So roughly 85% is the zerocheck and lincheck replay, including building the statement's constraint-matrix structure.
- `verifier_mul_count`, BLAKE3 boolean (K = 256, m = 22): 191,545 GF(2^128) multiplications and 425 inversions per verify.
- Production figures from [`docs/flock-gpu-route.md`](../docs/flock-gpu-route.md): verifier replay 0.11–0.19 s per 4,096-VU chain-table session, and 0.26 s per 8,192-VU pure-block session, both with 2 reps.

## 5. Lean versus Rust microbenchmarks

Lean 4.34.0 was installed with elan; `lake build` compiles through C with its default release flags. Rust 1.98.1 used `-C target-cpu=native`. Each operation is a dependent chain, so these are latencies.

| Operation | Rust | Lean, naive idioms | Lean, careful idioms |
|---|---|---|---|
| GF(2^128) GHASH multiply | 10.0 ns (flock-field, PCLMULQDQ); 892 ns (portable bit loop) | 2,895–3,022 ns (`for` bit loop); 4,650–4,684 ns (window table in a `Vector`) | 355 ns (branchless tail recursion); 196 ns (nibble tail recursion) |
| BLAKE3 compression | 78.6 ns (`blake3::hash` of 64 B); 11.2 ns per block in bulk (64 MiB) | 1,194–1,254 ns (`Vector UInt32 16` state) | 67.1 ns (scalar-field structures) |
| SHA-256 compression | 54.6 ns (one 55-byte message, SHA-NI); 33.5 ns per block in bulk | 1,147–1,164 ns | 422 ns (tail recursion, 16-word rolling schedule) |
| F128 XOR-gather, 2^20-entry table, random index | 3.39 ns | 35.6–36.2 ns (`Array F128`, boxed elements) | — |

Correctness cross-checks:
- One million chained multiplications x ← x·y + 1 give `15009e6758b61b29 9696b0e810c228d8` in all four Lean variants, flock-field's PCLMULQDQ multiply and the portable Rust multiply (Rust test `same_chain_as_lean`).
- The BLAKE3 variants agree with each other (`2dafcb74 561263b`), and so do the SHA-256 variants (`2105bb5b 7b06e54f`).

Why naive Lean is slow: `for` loops with several `mut` words carry their state boxed, core Lean has no unboxed `UInt64` array (only `ByteArray` and `FloatArray`), and `Array F128` stores pointers to heap objects. Tail-recursive functions on `UInt64` arguments and structures with scalar fields compile to unboxed C.

Careful kernels (Lean):

```lean
structure F128 where
  lo : UInt64
  hi : UInt64

def clmulNib (a b : UInt64) (k lo hi : UInt64) : F128 :=
  if k == 16 then ⟨lo, hi⟩ else
    let s := 60 - 4 * k
    let nib := (a >>> s) &&& 15
    let hi := (hi <<< 4) ||| (lo >>> 60)
    let lo := lo <<< 4
    let m0 := (0 : UInt64) - (nib &&& 1)
    let m1 := (0 : UInt64) - ((nib >>> 1) &&& 1)
    let m2 := (0 : UInt64) - ((nib >>> 2) &&& 1)
    let m3 := (0 : UInt64) - ((nib >>> 3) &&& 1)
    let lo := lo ^^^ (b &&& m0) ^^^ ((b <<< 1) &&& m1) ^^^ ((b <<< 2) &&& m2) ^^^ ((b <<< 3) &&& m3)
    let hi := hi ^^^ ((b >>> 63) &&& m1) ^^^ ((b >>> 62) &&& m2) ^^^ ((b >>> 61) &&& m3)
    clmulNib a b (k + 1) lo hi
termination_by 16 - k.toNat
decreasing_by all_goals sorry   -- benchmark only

-- reduction modulo x^128 + x^7 + x^2 + x + 1 of (r0, r1, r2, r3), lowest word first
def reduce (r0 r1 r2 r3 : UInt64) : F128 :=
  let t := r3
  let r1 := r1 ^^^ t ^^^ (t <<< 1) ^^^ (t <<< 2) ^^^ (t <<< 7)
  let r2 := r2 ^^^ (t >>> 63) ^^^ (t >>> 62) ^^^ (t >>> 57)
  let r0 := r0 ^^^ r2 ^^^ (r2 <<< 1) ^^^ (r2 <<< 2) ^^^ (r2 <<< 7)
  let r1 := r1 ^^^ (r2 >>> 63) ^^^ (r2 >>> 62) ^^^ (r2 >>> 57)
  ⟨r0, r1⟩
```

The multiply is four `clmulNib` products (lo·lo, lo·hi, hi·lo, hi·hi) combined into (r0, r1, r2, r3) and reduced. BLAKE3 keeps its 16-word state in a structure of 16 `UInt32` fields, with the G function returning a 4-field structure that the compiler inlines away. SHA-256 runs its 64 rounds as a tail-recursive function over an 8-field state and a 16-field rolling message schedule.

One transcription pitfall that differential tests catch: Lean's `UInt64` shifts are taken modulo 64 (`b >>> 64 = b`), unlike Rust, so the high word of a carryless product needs `(b >>> 1) >>> (63 - i)`.

## 6. External sources used

- Microsoft's SymCrypt report, arXiv 2609.15648 (Sep 14, 2026), and its README:
  - 16.7k lines of Rust verified with 237k lines of Lean, about 5.1k theorems written by agents.
  - The ML-KEM NTT layer first took about six months; now "about a week for an agent and a few days of human review" per added algorithm.
  - The trust base is the Lean kernel, `bv_decide`, and Charon/Aeneas with its std axioms.
  - Pins: Lean 4.31, Rust nightly-2026-06-01.
- Runtime Verification, arXiv 2605.30106 (May 2026):
  - Plonky3 FRI fold and round scheduling via Aeneas or hax, with ArkLib, CompPoly and AI provers.
  - Toolchain drift: Aeneas and ArkLib could not share a file (`BitVec.toNat_pow`).
  - Generics with trait bounds, parallel iterators and external crates needed hand-written monomorphic models.
  - `fold_step_is_foldNth_eval` is still stated with `sorry`.
- hax blog 2026: the Lean backend is experimental and routes through Aeneas as of 0.4.0.
- Kani, arXiv 2607.01504; Rust std verification, arXiv 2606.17374: Kani is in verify-rust-std CI, and Verus is under review.
- Lean kernel bug #14576 (July 2026): an axiom-free proof of False through metaprogramming, fixed in #14577 and #14582. An out-of-date nanoda also accepted it because of a separate bug of its own. Postmortem: leodemoura.github.io, Aug 1, 2026.
- Isabelle AFP "The Sumcheck Protocol" (Garvía Bosshard, Bootle, Sprenger; CSF 2024).
- zkLean (Galois; Jolt extractor), Clean (zkSecurity; channels, 2026).
- zk.golf GF(2) challenges "SHA-256 Compression, canonical (identity-C) form" and "BLAKE3 Compression", described as "the Flock encoding discipline".
- OpenVM formal verification (constraints only; assumes the proof system) and SP1 Hypercube (62 opcodes against Sail).
- Ligerito, ePrint 2025/1187: its §6.3 guarantees are unique-decoding and rely on AER24, DG24 and BCIKS.
