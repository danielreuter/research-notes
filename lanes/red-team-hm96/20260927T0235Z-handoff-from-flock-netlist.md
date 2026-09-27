lane: red-team-hm96 · kind: handoff · from: flock-netlist · created: 2026-09-27T02:35Z

# verity/flock-circuit's hm96-sha512 Merkle salts now come from ChaCha20 under a fresh per-proof OS key: this reverses "salts straight from the OS" (Daniel approved, 2026-09-27)

For review whenever you next look at hm96 users. PR #83 at b32e1a7b.

**What changed.**
- The proof's own Merkle trees (every Ligerito level) use `hm96-sha512/v1` leaves. They used to take a 192-byte salt per leaf
  straight from getrandom.
- Measured on one RTX A6000, SiLU·mul at 128 rows, m = 33: that cost +96% prover time. The cause is 670 MB of salts per
  proof, drawn, copied and uploaded.
- The salts are now a ChaCha20 expansion. Your F4 notes that `os.urandom` is itself ChaCha20-based, and salted-leaves (22:25Z)
  said ChaCha20 salts are "modelled as uniform like the OS generator's".
- The proof format is unchanged: each opening still carries its rows' salts.

**Exactly how** (`backends/flock/live/src/zk_hooks.rs` `LeafSalts`; device `cuda/sha512.cuh` `hm96_finish_leaves`):
- **Key:** 32 bytes from getrandom, drawn fresh per proof (one session, both reps). It is independent of the prover seed
  that keys the masks. An injected seed replaces it only in a test harness (cargo feature `seed-injection`).
- **Stream:** ChaCha20 with 20 rounds: "expand 32-byte k", the key, a 64-bit block counter (words 12–13) and a 64-bit nonce
  (words 14–15). It is checked against RFC 7539 §2.3.2.
- **Salt of leaf i in a tree with nonce `id`:** blocks 3i, 3i+1 and 3i+2, 192 bytes.
- **Tree ids:**
  - Level 0 is id 0. Both reps commit the same level-0 tree, which R1 binds to one root, so they reuse its salts, not the
    salts of different leaves.
  - Every later tree takes the next id from one per-proof counter across both reps, so no (id, block) pair repeats.
- **Where it's expanded:** on the device inside the leaf-finishing kernel, so no salt crosses PCIe. The host recomputes only
  the opened rows' salts for the proof.
- **Key hygiene:**
  - never written to disk, logs or the session record;
  - `LeafSalts` zeroes its key on drop (volatile writes), as does the copy handed to the device prover;
  - the C++ context zeroes its copy when the proof ends;
  - the per-proof kernel arguments are transient.
- **Pinned:** the leaf scheme in META and the backend identity says
  `"salt_source": "chacha20 expansion of a fresh 256-bit os key per proof, never reused or stored"`.

**What hiding rests on now.** Statistical given uniform salts, as before. The salts are uniform if ChaCha20 is a PRG under a uniform
256-bit key, the same modelling step as the OS generator's own ChaCha20. The key is used for nothing else. I suggest the wording
"statistical given uniform salts; salts from ChaCha20 under a fresh OS key".

**Checks:**
- negative `opened_salt_altered` (one flipped salt byte is rejected in both reps);
- `prover_is_deterministic` (an injected seed reproduces proofs byte for byte);
- CPU selftest 26/26 on RoPE;
- the GPU selftest on an L40S is running (r20260927-022832-8b16).

If you want this red-teamed like PR #88's committer, the pieces are above.
