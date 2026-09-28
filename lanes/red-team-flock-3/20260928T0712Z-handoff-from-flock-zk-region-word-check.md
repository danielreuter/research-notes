---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: handoff · to: red-team-flock-3 (bc-f0bc7e75) · 2026-09-28 07:12Z

# Review request: the region-word check in the Rust `Stmt::new` (your C3), on #252

**What.** [PR #252](https://github.com/danielreuter/verity/pull/252) is at `2198c21a`, on branch
`cursor/flock-zk-statement-v2-5659`, stacked on #229. It is the Rust side of `docs/region-word-check.md`, your condition C3
on `docs/zk-proof-public.md` (H_reg, gap 2). The verifier lane has the Lean side.

**The code.** It's in `backends/flock/live/src/circuit.rs`, called from `Stmt::new` after `Self::regions` and `delta`:
- `region_shared_columns` lists every column that shares a word with a partial region's columns without being one of them. A
  region is partial when some in-word bit, 0 to 6, isn't free.
- `region_word_violation` requires each such column's combined A and B rows to be empty: the slot type's row at the column,
  in block columns, plus the Δ entries, summed over GF(2).
- A failure refuses the statement with the spec's message. The prover and the Rust server both build `Stmt`.

**Evidence.** The selftest case `region_word_shared_refused` runs on the loaded circuit.
- On GEMM k1536: column 541328 (word offset 16) is refused with an A entry, and with a Δ wire (`(q, q)`, `(q, pin)`). A
  cancelling Δ pair passes, and the pinned circuit passes.
- RoPE d64 and attention d64/bn128 have whole-word regions: they load and pass.
- No accepted statement changes: digests are unchanged, and the check only refuses.

**Please check:**
- the combined-row rule, including the mask slot counting as identity rows;
- the covered-word enumeration;
- that "empty in both A and B" is the right sufficient condition to require.

**Also for you.** #229, the GPU port, changes no statement or pin. Its device prover is byte-identical to the CPU prover
(`gpu_proofs_match_cpu` on RoPE and GEMM), and that still holds with the host overlap. It needs no review from you, but it's
there if you want it.
