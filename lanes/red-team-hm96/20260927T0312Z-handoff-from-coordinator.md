---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: red-team-hm96 · kind: handoff · from: coordinator · created: 2026-09-27T03:12Z

# Quick grant review: M0's HM96 salts from ChaCha20 under a fresh per-proof OS key (PR #83 @ b32e1a7b)

Daniel approved the change. M0 (flock-netlist) described it in `lanes/red-team-hm96/20260927T0235Z-handoff-from-flock-netlist.md`:
- the proof's `hm96-sha512/v1` Merkle salts are now a ChaCha20 expansion of a fresh 256-bit getrandom key per proof;
- they're expanded on the device (`zk_hooks.rs` `LeafSalts`, `cuda/sha512.cuh` `hm96_finish_leaves`);
- the key is never stored or logged, and is zeroed on drop.

**Please check, quickly (a code read plus the RFC vector and a CPU test):**
1. **Key hygiene:**
   - one fresh key per proof, independent of the mask seed;
   - never written to disk, logs or the session record;
   - zeroed on the host and the device copy;
   - `seed-injection` is test-only and can't be built into a proving binary.
2. **Stream layout, with no salt reuse:**
   - leaf i takes blocks 3i..3i+2 under nonce `id`;
   - level 0 is shared by both reps, and R1 binds that one root;
   - every later tree takes a fresh id from one per-proof counter across both reps.
   - Show that no (id, block) pair repeats across trees, reps or retries, and that the 64-bit counter can't wrap at our sizes.
3. **What hiding now rests on:** the statistical-hiding claim (hm96 §8) with salts modelled as uniform, plus ChaCha20's
   PRF security under a fresh key.
   - The expected verdict: no assumption beyond the OS generator's, which is itself ChaCha20.
   - Say so, or name the extra assumption.

**Verdict to** `lanes/coordinator/`: grant, grant with conditions, or refuse, with numbered findings. CPU only, under $1.
