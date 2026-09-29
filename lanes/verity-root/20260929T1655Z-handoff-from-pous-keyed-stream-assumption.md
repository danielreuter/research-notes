---
id: 20260929T1655Z-handoff-from-pous-keyed-stream-assumption
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (bc-f0bc7e75, cc work-law lane bc-0b392ca4): A4, the keyed-stream assumption `prf/sha-256`, for review before it's built on

From POUS's Lean lane, the author of #408, #412 and #416. Daniel approved tier 3 for the PoUW circuit's keyed draws: #364's
`Traced.draw` calls `plan.draw`, which calls `Key.subset` on `verity.randomness`'s SHA-256 counter-mode streams under one
window key. `verity.randomness` is core, so the assumption that chain rests on comes to you first. Nothing builds on it
until you've read it.

The code is on branch `cursor/keyed-draw-tier3-30a8` at `a8bb57e2`, stacked on #416; no PR yet:
- `backends/flock/verifier/lean/soundness/FlockSoundness/Randomness.lean`: the spec;
- `FlockSoundness/Assumptions.lean`: A4.

## A correction to my window-pin review

`Key.subset(k, n, index)` is **not** `Flock.Draw.subset` on one stream. Swap `i` draws `_uniform(n − i)` from its own
stream at index `("s", *index, i)`, so a `k`-subset reads `k` streams. My review said the two were tied by
`test_unit_draw_samplers_are_the_exact_reduction`; they aren't. That test ties `Flock.Draw.subset` to a single-stream Python
reference. So the chain needs its own escape theorem for the per-swap sampler, not an equality.

## What A4 reads: a Lean spec of `verity.randomness` v1

`Randomness.lean` restates the byte formats and samplers executably, on the verifier's FIPS 180-4 `Flock.Sha256.hash`:
- `frame` and `frames`;
- `derive`;
- `block` and `stream`: block `c` is `SHA-256(STREAM_TAG || key || frames(index) || be8 c)`;
- `uniformOn`: `Key._uniform`, which is `Flock.Draw.uniform` from the stream's start;
- `subset`, per swap, as Python's loop.

It **reproduces `packages/verity/tests/randomness/vectors.json` byte for byte**: every frame, derived key, stream, shard
key, uniform value, Bernoulli bit and subset in all three cases. Python's `Key` will also be held to more Lean-generated
vectors, the Lean-first norm.

## A4, verbatim

~~~lean
/-- **Assumption 4 (`prf/sha-256`): `verity.randomness`'s keyed streams at distinct indices pass a test as independent
uniform bytes do, up to `η`**, for the PoUW window draw. … -/
def KeyedStreamsUniform (S : ℕ) (domain : String) (context : List (String × Randomness.Part)) {m : ℕ}
    (idx : Fin m → List Randomness.Part) (L : Fin m → ℕ) (E : (Fin m → ByteArray) → Prop) (η : ℝ≥0∞) : Prop :=
  (∀ i j, Randomness.frames (idx i) = Randomness.frames (idx j) → i = j) →
    prCoin (fun src : Fin S → Fin 256 => E fun i =>
        Randomness.stream (Randomness.derive ⟨Array.ofFn fun b => UInt8.ofFin (src b)⟩ domain context) (idx i) (L i)) ≤
      prCoin (fun f : (i : Fin m) → Fin (L i) → Fin 256 => E fun i => ⟨Array.ofFn fun b => UInt8.ofFin (f i b)⟩) + η
~~~

**In words:** for a uniform verifier secret of `S` bytes, the derived key's streams at indices whose framings are pairwise
distinct pass the test `E` with at most the probability that independent uniform streams of the same lengths do, plus `η`.

**Why per test, as A2 is per finder.** For every test the statement would be refutable: `2^(8S)` sources give at most that
many stream tuples, so no concrete SHA-256 makes longer streams exactly uniform. The theorems take A4 for one test each,
`E_B`: the window draw computed from the streams misses the committed set `B`. That test is efficient: it runs the sampler
and checks `B`. `η` then enters their bound.

**What it assumes of SHA-256:** it is a pseudorandom function keyed by a secret prefix, on the inputs `verity.randomness`
hashes, for both `derive` (the source's frame first) and `stream` (the key first).
- **The stream inputs are prefix-free.** `frames(index)` is framed with its length, and the counter is a fixed 8 bytes,
  so no input is a proper prefix of another and length extension doesn't apply.
- **Distinctness is on the framings,** the bytes actually hashed. The chain proves them distinct from:
  - distinct call indices, through admission inside the draw (#364's X-SPC-107 fix);
  - distinct stratum names within a call;
  - distinct swap numbers.
- **A4 also assumes the verifier's secret is uniform.**

**Claims id:** `prf/sha-256`, with a new property `prf` beside `cr`, `ecr`, `xof`, `sis` and `uniform`, on the existing
instance `sha-256`. It's on the branch in `verity.claims`, with a test. `ASSUMPTIONS.md`'s A4 entry follows your read.

## How the chain uses it

1. The per-swap sampler's escape. Over independent uniform per-swap streams, the spec's `subset` misses `B` with at most
   `C(n − |B|, k)/C(n, k)`: #408's pool argument, one stream per step.
2. The window lemma. C per-call `plan.draw`s under one key, with admission and call units offset into the window's, form
   one `Law.stratified` over the window's (call, template) strata.
3. With A4 at `E_B`, the live window draw misses `B` with at most `(Law.stratified σ k hk).escape B + η`.
4. Root's window pin then gives `2^-40 + η + ε_ks + δ_link` at the sizing of record, **if `audit_window_of_le` takes an
   additive slack**; see below.
5. Each spec is tied to its Python by Lean-generated vectors: `plan.draw` and the window loop once #364 and its X-SPC-107
   fix land. As in #416, the bound holds for every stream budget `L`, and the unbounded Python stream is the limit.

## Asks

- **bc-f0bc7e75:** a statement review of A4 and of the spec definitions it reads (`frames`, `derive`, `stream`), with
  three questions:
  1. **`prf/sha-256`, or `random-oracle`?** Is the PRF on prefix-free inputs the right primitive statement, or would you
     rather name the random oracle already in `verity.claims`?
  2. **Should η stay symbolic?** The alternative is a concrete form, for example `T/2^(min(256, 8S))` for a test of `T`
     hash evaluations.
  3. **Split out the secret's uniformity?** It could be an A3-style claim for the verifier's key holder.
- **Work-law lane (bc-0b392ca4):** please state `audit_window_of_le` with a slack. Take
  `hL : ∀ B, L.escape B ≤ (Law.stratified σ k hk).escape B + η`, and bound by `… + η + ε_ks + δ_link`. The proof is
  unchanged (`audit_profile`, then `iSup₂_le`). The keyed draw needs the `η`.
- **Both, on the model:** does the window key come after every call's receipt? The audit has one committed set before one
  draw. If a window's calls were drawn as they arrive under one key, later calls' wrong sets could depend on earlier
  draws, which is outside `audit_profile`.
