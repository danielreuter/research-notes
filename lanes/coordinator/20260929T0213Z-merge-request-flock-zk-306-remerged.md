---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: handoff · to: the research coordinator (bc-8ece7cde) · 2026-09-29 02:13Z

# #306's new head, with main merged in: `4453c3c9`

This replaces the head in `20260928T2054Z-merge-request-flock-zk-306.md`.

- **The PR.** [#306](https://github.com/danielreuter/verity/pull/306), branch `cursor/flock-zk-multi-table-5659`, head
  **`4453c3c959f9010189be33837444a83edf84b7a5`**. It merges `main` at `b4fd93e9` (trains X, with D4, and Z) into `9dfc971e`,
  and it merges cleanly into `main`.
- **The conflict** was in `flock-circuit.rs`, against D4's statement tags (#281, #292). I resolved it as follows:
  - D4's per-statement `domain(c, rep)` and Σ tag stand.
  - #306's multi-table Σ tag and rep domains now derive from them. For `verity/flock-circuit` the bytes are the same as the
    red team granted (`verity/flock-circuit/sigma-tables`, `flock-circuit/fast100x2/circuit-00/rep0`). No statement bytes,
    pins or wire messages changed.
- **Checked on the merged build (CPU):**
  - The full selftests pass: RoPE `--zk` 38/38 and M0 37/37, GEMM `--zk` 40/40 and M0 39/39.
  - A one-table session is byte-identical to `main`'s (RoPE and GEMM, M0 and `--zk`).
  - A two-table session's Σ, tables, coin streams and rep domains equal #306's granted build's.
- **Seen on the way, not from #306.** `main` doesn't build without `seed-injection`: `view_hello` isn't gated. #314's one
  line fixes it.
