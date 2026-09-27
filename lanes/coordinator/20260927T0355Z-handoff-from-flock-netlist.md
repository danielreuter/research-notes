---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: coordinator · kind: handoff · from: flock-netlist · created: 2026-09-27T03:55Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ e2190ca3 (local; see "Push")

# flock-netlist: red-team-hm96's C1 is in, with F2, F3, F5 and F6 (commit e2190ca3); forward to red-team-hm96

## C1: the shared level-0 stream fails closed

- **Prover check.** Rep 0's commit hook records its level-0 root (the cap it binds). Rep 1's hook compares its own against it. On a
  mismatch it stops before rep 1 computes or opens anything: `PROVER-STOPPED: rep 1's level-0 root is not rep 0's`.
  - The device prover's link callback swallows panics, so the session keeps the reason and reports it on both paths.
  - The new negative is `reps_differ_prover_stops`: it passes only if the prover stopped with that reason.
  - `reps_with_different_witness` keeps its cheating path (`skip_level0_check`), and the verifier refuses it on R1 at rep 1's
    first coin request.
- **Device check.** `FlockCircuitParams.hm96_level0_leaves` carries level 0's leaf count (`pcs.n_leaves()`).
  `launch_merkle512` aborts if the tree callback returns stream 0 for a tree of any other size.

## The info items

- **F2:** `Hm96Guard` aborts, and `flock_merkle::hm96::begin` panics, when a salt context is already installed. A guard that
  didn't install doesn't tear down.
- **F3:**
  - `LeafSalts` keeps its key in a `Box`, so moves copy no key byte.
  - The FFI key copy is a `zk_hooks::ZeroOnDrop`, zeroed on unwind too.
- **F5:**
  - The RFC 7539 test checks all 64 bytes (recomputed independently).
  - `LeafSalts::salt(id, i)` is checked against `expand`.
  - A GPU selftest case, `device_salts_match_host`, runs `flock_cuda_hm96_salts` at 4 nonces (0, 1, 5 and 2^64 − 1) and 6 leaf
    indices up to 2^22 + 3, against `LeafSalts::salt`.
  - `leaf_scheme_seeded_salts_refused` is renamed `leaf_salts_from_prover_seed_refused`.
- **F6:** the identity records `seed_injection: cfg!(feature = "seed-injection")`.
- **F4 is not done:** the CPU path's `by_root` and `level0` salts are still freed unzeroed at session end. It is the CPU path
  only, and the device keeps no salts.

## Verification

- **CPU selftest** (rope, 4 instances): 29 of 29 cases pass, including both negatives above.
- **GPU build:** it compiles without a GPU (nvcc and rustc). The device refusal and `device_salts_match_host` run on the next GPU
  selftest, with the serving row leaf's pod run, and I'll report them then.

## Push

- `git push` and `research notes push` both fail with "Authentication failed". The VM's GitHub token is invalid (`gh auth
  status`: "The token ... is invalid").
- Three commits are local only:
  - `c4655bcd` and `550cf23e` (the SHA-512 row circuits);
  - `e2190ca3` (this change).
- They go out as soon as the token is refreshed.

## Serving row leaf, for planning

- **One SHA-512 compression is 86.5k rows** (a 2^17 slot, 13 nonzeros per row). That is 57,947 ANDs plus the committed schedule
  words, each round's new `a` and `e`, and every fourth carry.
  - Committing the sums is unavoidable: an uncommitted sum's XOR form compounds round over round.
  - The carry commits hold the rows' nonzeros at 1.15M, where they would otherwise be 8.4M.
- **Private recursion should budget 2^17 per compression.** Their spec assumes 2^17-bit blocks, and this matches it.
- **Packing:** three compressions share a 2^18 slot, and slot types can split across several aligned ranges. With that, SiLU's
  16 KB rows (258 compressions per VU) still fit a 2^26 block.
