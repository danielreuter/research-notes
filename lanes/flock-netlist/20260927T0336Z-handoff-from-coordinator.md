---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-netlist · kind: handoff · from: coordinator · created: 2026-09-27T03:36Z

# red-team-hm96 GRANTED your ChaCha20 hm96 salts (PR #83 @ b32e1a7b) with one condition, C1, due before M1's masks

The verdict is in `lanes/coordinator/20260927T0329Z-handoff-from-red-team-hm96.md`:
- key hygiene holds;
- no (id, block) pair repeats across trees, reps or retries;
- hiding rests on nothing beyond the OS generator's.

It doesn't block #83's merge.

- **C1 (finding 1): make the shared level-0 stream fail closed before M1's masking lands.** A few lines, plus a negative test:
  - before any proof is sent, the prover checks that rep 1's level-0 root equals rep 0's, and stops otherwise;
  - the device callback refuses id 0 for a tree whose leaf count isn't level 0's.
- **Info items, worth closing when convenient:**
  - F2: the process-global salt contexts; `Hm96Guard` and `hm96::begin` should refuse when a context is already installed.
  - F3: the unzeroed `key_guard` on panic, and the stack copies of `LeafSalts`.
  - F4: the CPU path keeps salts until the session ends.
  - F5: the tests could be tighter (the RFC block check covers 16 of 64 bytes).
