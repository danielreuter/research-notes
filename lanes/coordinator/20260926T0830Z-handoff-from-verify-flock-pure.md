---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T08:30Z
---

# verify-flock-pure: the four elementwise flock-ir-frame/v2 cells are verified=accepted as file re-verifications (dd27fdab, 8a07b80f, 9563d2c8, 63553a6c); pod terminated 08:28Z; about $0.3

Replay run r20260926-075751-1b20 (rc 0, preserved), on a separate CPU pod, vy-verify-flock-pure.

- **Verifier build:** flock-ir-frame had no replay command, so I added one. It's on lane/verify-flock-ir @ 17baf43e, which is
  cursor/flock-ir-lowering-c78f c53d9148 (it includes b4e05b48) plus the replay subcommand and `backends/flock/pod/34-ir-replay.sh`.
  The cells' verifiers ran c53d9148.
- **IR2:** I fetched each captured input set from the store (content digests as in the results) and staged the instance
  files myself through `ir_frame.stage`, the same function the verifier pod uses. Every staged file passes the binary's own
  load checks before any replay: unit order, the block table, the frame-v3 roots, and the cut words against the pinned tail
  on the sha256-pinned MUFU tables. They also match the verifier pod's files by sha256. The regenerated netlist is byte-equal
  to the verifier's and hashes to its pin.
- **Each session's checks:** replayed with the recorded coins. Σ, the honest run outputs (the publics), check_digests and
  link_sha256 are recomputed here, the proof files are the recorded ones, and both reps must sit on the committed root.
- **Negatives:** 12 tampered-record negatives on one session per cell all behaved as expected: 9 rejected, 1 accepted as it
  must be, and 2 info coins that an honest proof doesn't depend on.

| cell | result | input set | verifier run | sessions accepted | staged files = verifier's | plateau proofs = recorded |
|---|---|---|---|---|---|---|
| RoPE | art:dd27fdab | art:16825154 | r20260926-065044-3f05 | 24/24 | 4/4 | 12/12 |
| SiLU·mul | art:8a07b80f | art:d3e2d9b1 | r20260926-065811-7419 | 96/96 | 16/16 | 48/48 |
| RMSNorm fused | art:9563d2c8 | art:a261c0c2 | r20260926-063231-f0c1 | 30/30 | 5/5 | 12/12 |
| RMSNorm Triton | art:63553a6c | art:9582a734 | r20260926-064134-3bf2 | 30/30 | 5/5 | 12/12 |

- Recorded coins are replayed, so this is not transferable evidence.
- This answers red-team-flock-2's pending condition that a non-producer replay be done. IR6, the producer-staged hardening,
  isn't exercised here, because both sides staged their own files.
- **Your 08:20Z ask, "lowering from main":** the recorded sessions are at c53d9148, so their Σ binds the c53d9148 pins, and
  main's lowering (2f55d2d3, IR6) pins differently.
  - The difference is only the LEAVES line. On my VM, main's netlist for each cell's own input set, with the LEAVES line
    removed, is byte-identical to the cell's netlist: rope 933c4ef8 → 2eaa652f, silu 823415f4 → c7605b5c, fused
    e7b8dd88 → 47d75396, triton 6490d5e8 → 950d95a1.
  - So I replayed under the cells' own statement, c53d9148, which is the one red-team-flock-2 granted. A replay with main's
    binary would refuse at Σ by construction.
  - Cells re-run under IR6 would need their own replay.
