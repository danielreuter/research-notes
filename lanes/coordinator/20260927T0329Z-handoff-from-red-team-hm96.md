---
cursor:
  subagentId: "bc-6d082f2c-9c48-534c-9ae6-46bf3724b4a7"
---

lane: coordinator · kind: handoff · from: red-team-hm96 · created: 2026-09-27T03:29Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ b32e1a7b

# red-team-hm96: M0's ChaCha20 hm96 salts (PR #83 @ b32e1a7b) are GRANTED WITH ONE CONDITION, due before M1's masks and not blocking #83's merge

**Verdict: GRANT WITH CONDITIONS.** Key hygiene holds, no (id, block) pair repeats across trees, reps or retries, and hiding rests
on no assumption beyond the OS generator's.

- **C1, before M1's masking lands:** make the shared level-0 stream fail closed (finding 1). It's a few lines plus a negative test.
- Please forward C1 to flock-netlist (M0/M1).

## Findings

1. **F1: the level-0 id is shared across reps, and nothing on the prover side checks the tree it covers. Low, open (C1).**
   - **How id 0 is assigned.** Both reps give their first tree nonce 0. On the GPU, `hm96_tree(ctx, 0)` returns 0 for whatever tree
     the device builds first. On the CPU, `hm96::next_tree_salts` hands the first tree the id-0 salts and checks only its leaf
     count.
   - **When that is safe.** Only while each rep's first tree is the same level-0 tree over identical columns. Today it holds:
     `wt1 = wt0.clone()`, `NoMask`, and a deterministic encoding. M0's L40S selftest confirms it: its honest two-rep runs bind one
     root (R1), which would fail if tree 0 weren't level 0.
   - **How it could break.** A per-rep level-0 mask or pad in M1, or a reordered Flock prover, would reuse id-0 salts over
     different leaves. The verifier would refuse on R1, but only after both reps' openings (salts and sibling leaf hashes) had left.
     For a low-entropy column, a known salt makes the other rep's leaf searchable.
   - **Fix:**
     - before any proof is sent, the prover checks that rep 1's level-0 root equals rep 0's, and stops otherwise (the
       `reps_with_different_witness` negative keeps its cheating path);
     - the device callback refuses id 0 for a tree whose leaf count isn't level 0's.
2. **F2: the salt contexts are process-global. Info.** The device keeps `g_hm96` in `sha512.cuh`, and the CPU keeps a `static CTX`
   in `flock_merkle::hm96`.
   - Sessions run sequentially today, in both the `prove` loop and the selftest.
   - Two concurrent proofs in one process would clobber each other's key, tree counter and level-0 salts.
   - Fail-closed fix: `Hm96Guard` and `hm96::begin` should refuse when a context is already installed.
3. **F3: some copies of the key aren't zeroed. Info.**
   - `gpu_circuit.rs` makes a heap copy, `key_guard` (a `Vec`). It's zeroed after the FFI call, but a panic between its creation
     and that point frees it unzeroed.
   - Moving `LeafSalts` (the return from `for_seed`, then into the `Mutex` and the `Arc`) can leave stack copies.
   - Kernel parameters and the kernel's local `yw[48]` are transient.
   - The witness sits in the same memory, so there's no new exposure. Still, a `Drop`-zeroing wrapper for `key_guard` and a
     heap-pinned key would close it.
4. **F4: the CPU path keeps every tree's salts until the session ends. Info.** `SaltContext.by_root` and `level0` are then freed
   without zeroing, as before this change. The salts derive from the key, so exposing them equals exposing the key for that proof.
   The device path keeps no salts.
5. **F5: the tests could be tighter. Info.**
   - `chacha20_block_matches_rfc7539` checks only 16 of the block's 64 bytes. I checked all 64 in both the Rust and the device
     code.
   - A device-vs-host salt vector would be cheap to add.
   - `leaf_scheme_seeded_salts_refused` now refuses salts from the *prover seed*, which is correct, but its name is stale.
6. **F6: `seed-injection` isn't recorded in the identity. Info.**
   - Only `60-circuit.sh MODE=selftest` enables the feature, and every cell run rebuilds with `MODE=build`.
   - `ProverSeed::injected` and `inject_coin_seed` are reachable only from the `prover_is_deterministic` selftest; every proving
     session uses `ProverSeed::from_os()`.
   - The backend identity doesn't record the feature, so only `binary.sha256` distinguishes the builds. Pinning
     `cfg!(feature = "seed-injection")` in the identity would make a cell run from a selftest binary visible.

## What holds

- **Key hygiene.**
  - The key is one 32-byte `getrandom` draw per session, which is per proof and covers both reps.
  - It is independent of the mask seed: in the OS case `for_seed` ignores `seed.seed`. If `getrandom` fails, the prover refuses
    to continue.
  - Nothing prints, serializes or records it: `LeafSalts` has no `Debug` or `Clone`, and it appears in no JSON or log line.
  - It is zeroed with volatile writes in `LeafSalts::drop`, in `key_guard` after the FFI call, and in `~Hm96Guard` for the C++
    copy. `hm96_opened_salts` zeroes its temporary.
- **Stream layout.** Leaf i of tree `id` takes ChaCha20 blocks 3i, 3i+1 and 3i+2 under nonce `id`.
  - `LeafSalts.next` starts at 1, so id 0 is only ever level 0, and every later tree on both paths takes `next_id()` from the one
    per-session counter shared by both reps.
  - A retry of a failed session builds a new `LeafSalts`, so a new key. A failed rep ends the session, and a rebuilt device tree
    would take a fresh id.
- **Counter wrap.** A 64-bit counter and nonce in both the Rust and CUDA code. 670 MB of salts per proof is 3.5 M leaves, or
  10.5 M blocks, which is about 2^23.3, far below 2^64.
- **CPU test** (`chacha_salts_check.py`, 9 of 9). It compares M0's Rust `chacha20_block` (extracted verbatim), M0's device
  `chacha20_block` and `hm96_salt` (built for the host with g++), an RFC 7539 implementation, and OpenSSL:
  - all four agree on the full RFC 7539 §2.3.2 block;
  - they agree on 1,555 blocks, including the 2^32 carry and 2^64 − 1 counters and nonces;
  - they agree on 300 salts;
  - a model of the session's id schedule has no (id, block) collision.
- **GPU evidence.** M0's L40S selftest ran at a clean `b32e1a7b` (`r20260927-022832-8b16`) and every case passed on three
  templates (30, 26 and 27 cases). That includes honest, `opened_salt_altered`, `reps_with_different_witness`,
  `leaf_key_witness_refused` and `prover_is_deterministic`.
- **What hiding rests on.**
  - The claim is hm96's statistical bound given uniform salts, plus the PRF security of 20-round ChaCha20 under a uniform 256-bit
    `getrandom` key. The inputs are distinct, and there are at most about 2^23 of them per proof. The key is independent of hm96's
    pinned key, as the lemma requires.
  - The verifier sees raw ChaCha20 blocks at the openings it chose, which standard PRF security (adaptive queries) covers.
  - Linux's `getrandom` is itself ChaCha20 keyed from the entropy pool, so this adds no assumption beyond the OS generator's.
  - The differences are custody: a single key per proof instead of 670 MB of salts, and no kernel-style key erasure during the
    proof. Neither exposes anything the witness in memory doesn't already.
  - M0's wording holds: "statistical given uniform salts; salts from ChaCha20 under a fresh OS key". hm96 §3 already treats a
    seeded ChaCha20 stream as the same modelling convention, and no new claim id is needed.

## Evidence

- **Artifact:** `art:145996e9c209ca518420a7c98f46094750bf652887116fa4152cd5382176786c` (redteam-findings/v1), preserved.
- **Script:** `lanes/red-team-hm96/evidence/chacha_salts_check.py`.
- **Label:** `finding` by red-team-hm96 on `r20260927-022832-8b16`, with ref `art:145996e9`.
- **Cost:** CPU only, $0.
