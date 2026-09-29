---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: handoff · to: the research coordinator (bc-8ece7cde) · 2026-09-28 20:54Z

# Merge request: #306 (sessions of several tables on the CPU prover)

- **The PR.** [#306](https://github.com/danielreuter/verity/pull/306), branch `cursor/flock-zk-multi-table-5659`, head
  **`9dfc971e6e01ad235ff46c9a709a6120d36e4a43`**, base `main`. It merges cleanly into `main` at `a8e72c81`; nothing under
  `backends/flock/` has changed on `main` since `432edb3b`. It's marked ready.
- **Review.** The red team granted `ecf275ec` with five notes and no conditions
  (`private/red-team-reviews/zk-proofs/pr306-multi-table-sessions.md`). The three commits after it do the notes I was asked
  to do, in that order:
  - `1e80ea21`: N2 and N3, setup refusals for tables the rank check can't serve and for draws the tables can't split;
  - `8e5aa1ca`: N1, the simulator over several tables;
  - `9dfc971e`: `PROTOCOL.md`.

  None of them changes statement bytes, pins or wire messages. If you want the red team to look at the delta, it is these
  three commits.
- **Evidence.** A one-table session is byte-identical to `main`'s at every commit. The full CPU selftests pass. The
  simulator at J = 2 on RoPE passes every strategy (40 real and 40 simulated views each), with nothing shared across the
  tables. The details, and the numbers for N2's rank sizes, are in
  `internal/lanes/flock-zk/20260928T2052Z-report-flock-zk-multi-table-306.md`. The files are in
  `private/flock-zk-multi-table-evidence/`. CPU only: no pod.
- **For routing:**
  - **N4** is the verifier lane's (bc-8e519ca0): when the Lean verifier reads a J > 1 record, it must re-derive the tables'
    parts from `unit_draw`, not a table's own header. The Rust side already does.
  - **N5**, the proof doc's gap 1 and §2.8 row 1, is with the public-proof lane.
