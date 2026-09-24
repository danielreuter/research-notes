---
lane: coordinator
kind: handoff
to: wave-5090-2
created: 2026-09-24T04:08Z
---
# coordinator -> wave-5090-2: the 5090 committed cell (column 2) is yours; merge lane/fp4-port after the bare rounds

fp4-port-2's pod is an RTX 4090, so its bench is relative evidence only; it cannot produce the 5090 cell. The port is
validated: `lane/fp4-port` @ 1aa1f00e (3 commits on main 24f252b1), gates 0 failures, bare proofs byte-identical to main,
committed proofs byte-identical to fp4-decode-3 (sys_id 8c6d260c; Rust pin fp4-nvf4+hash table 8dad2d28).

After your bare live rounds on ver8 finish:
1. In your worktree: `git merge lane/fp4-port` (dry-run merge with your 04141baf is clean).
2. Sync to the prover AND ver8; rebuild ligero-verify on ver8 from that tree (the pin is in Rust) and restart live_serve.
3. Measure fp4-nvf4+poseidon2 with the bare settings (4096 VUs, interactive ZK, p4, 3 rounds alternating bare/committed,
   local + live same-DC). Record the merge commit as the code, and fp4-port 1aa1f00e in the note.
Budget raised to $5 total; deadline unchanged (06:30Z). Drop the old 2-vCPU verifier once you no longer need it.
