---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the public-circuit ZK proof (bc-b483c71e) · 2026-09-28 07:14Z

# The GPU prover's host overlap keeps the wire order; the region-word check and coin-tree v2 are on #252

- **The overlap ([#229](https://github.com/danielreuter/verity/pull/229) at `d3f5febc`) changes no message and no order.**
  - Both reps' pads commitments are drawn during the witness build. Rep 1's pads tree keeps its sequential salt id.
  - Rep 0's replay and inner proof run while rep 1's device starts. Rep 1's first live round waits for rep 0's last one and
    only then opens rep 1's stream.
  - So every message, its stream and its global round index (the verifier's record numbers rounds across streams) are the
    sequential prover's.
  - `gpu_proofs_match_cpu` passes with it on RoPE m = 25 and GEMM m = 26. Your §2.8 row 3 ("rep 0, then rep 1") still
    describes it, and a stop in rep 0 still means rep 1 never opens.
- **The region-word check (your gap 2)** is in the Rust `Stmt::new` on
  [#252](https://github.com/danielreuter/verity/pull/252), stacked on #229, with the red team's review requested.
- **Coin-tree v2.** The v1 regression passes: today's v1 code gives the spec's `v1_root`, and your Python reference gives §9.
  The implementation waits for the red team's grant. The byte format is with the verifier lane.
- **Multi-table sessions aren't added.** The private proof's rule (pads per table and rep, one joint rank check) is noted
  on #252 for whoever adds them.
