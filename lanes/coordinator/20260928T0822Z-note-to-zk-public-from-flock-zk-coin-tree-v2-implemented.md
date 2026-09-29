---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the public-circuit ZK proof (bc-b483c71e) · 2026-09-28 08:22Z

# Coin-tree v2 is implemented on #258; #229 and #252 are with the coordinator

- **[#258](https://github.com/danielreuter/verity/pull/258)** (`1053c0c9`) implements `docs/coin-tree-v2.md`: the prover's
  side and the Rust server. It reproduces every §9 vector, and the red team has it for review.
  - The prover's `Hello` nonce comes from the OS, per session.
  - The simulator draws one nonce per simulated session. The extraction, the estimation runs and the rewinds all restart
    after that `Hello`, as your `S_t` does.
  - The server takes one `Hello` per session, so the session key is never reused and leaves only in the answer (the red
    team's clarification).
  - When it lands, your §2.8 gains the v2 row for C1's code side.
- **[#229](https://github.com/danielreuter/verity/pull/229)** (the GPU port) and
  **[#252](https://github.com/danielreuter/verity/pull/252)** (the region-word check, granted at `2198c19c`) are with the
  research coordinator for merge, in that order. With #252 merged and the Lean side landed, your gap 2 closes.
