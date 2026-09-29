---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (bc-8ece7cde), for the next train
created: 2026-09-28T09:05Z
---

# Merge request: PR #268, the flock-circuit verifier refuses statements outside `Stmt.InRange`

- **The PR:** [#268](https://github.com/danielreuter/verity/pull/268), branch `cursor/flock-circuit-in-range-4d6a`, head
  **`2268905c`**, off `main` `3ba4d8b3`. It's marked ready, CPU only, and cost $0. It touches two files: `live/src/circuit.rs`
  and `live/src/bin/flock-circuit.rs`.
- **What it is:** the Rust half of the red team's step 4 (`private/red-team-reviews/m0-statement/block-limit-2-27.md`).
  - `Composite::parse` refuses `k_log > 26` or more than 1,024 public regions (`Stmt.InRange`).
  - `Stmt::new` refuses `m > 35` (PROTOCOL.md §16.5) or more than 64 link-point coordinates.
  - So an accepted statement is one the pinned table-soundness theorems cover.
- **Nothing existing changes:** no format, digest, pin or statement. Every recorded statement is inside the range. No Lean
  pin reads the Rust parser, so it needs no statement review. The Lean half is the verifier lane's.
- **Gates:**
  - `cargo test -p flock-live --lib`: 28 passed, including the new boundary test;
  - `flock-circuit selftest`: 32 of 32 cases pass, including the new `k_log_outside_the_proved_range_refused_at_load`,
    which is refused with the `Stmt.InRange` message;
  - `check` doesn't build this crate, so its steps equal `main`'s.
- **Next window (not in this PR):** the soundness lane extends `InRange` to `kLog ≤ 27`, then M0 raises this constant, the
  spec, the GPU guard and `K_MAX` together. The plan is in `20260928T0830Z-note-to-red-team-m0-block-limit-2-27.md`.

## Update 12:13Z: new head `01f41179`, adding the `LinkLayout` check the red team asked for

- **What:** `circuit_in_range` now also refuses a region whose free bits aren't distinct, at load. That's the `LinkLayout`
  hypothesis of the pinned table-soundness theorems. `Stmt::regions` concatenates two bit ranges per region, and nothing
  checked that they were disjoint.
- **The Lean side:** the verifier lane is adding the same check (`mkRegion`).
- **Gates:**
  - `cargo test --lib`: 28 passed, including a region with overlapping ranges, which is refused;
  - `selftest`: 32 of 32 on a class circuit, and `honest` is accepted on an attention circuit;
  - nothing recorded changes.
- **To merge:** #268 at **`01f41179`**. Superseded by the 12:20Z head below.

## Update 12:20Z: new head `0a241289`, adding the block checks the Lean verifier makes

- **What:** at load, before the regions are built, `block_in_range` refuses:
  - `k_log > 26`;
  - an hm96 range whose `slot_log` isn't in `[7, k_log]`;
  - a pinned constant column outside the block.

  Then `regions_in_range` checks the region count and distinct free bits. The block checks come first because
  `Stmt::regions` shifts by both `k_log` and the hm96 `slot_log`.
- **The Lean side:** the verifier lane is adding the same checks.
- **Gates:**
  - `cargo test --lib`: 32 passed, with one unit test per refusal;
  - `selftest`: 32 of 32 on a class circuit, and `honest` is accepted on an attention circuit;
  - nothing recorded changes.
- **To merge:** #268 at **`0a241289`**. Superseded by the 13:20Z head below.

## Update 13:20Z: granted, and the red team's N1 fix is in; new head `0494479e`

- **The grant:** the red team granted #268 (`private/red-team-reviews/m0-statement/pr282-pr268-refusals.md`), with one
  note, N1. `check()` shifted by every range's `slot_log` before only the hm96 range's was bounded.
- **The fix, `0494479e`:** the first step of `check()`, before any shift, as `HmRow.check` does:
  - it bounds `k_log` to `[7, 26]`;
  - for every range, it bounds `slot_log` to `[7, k_log]`;
  - for every range, it requires the slots inside the block, `pos0 + count ≤ 2^(k_log − slot_log)` (`range_in_block`).

  So an empty packed range can no longer carry an oversized `slot_log`. A shift of 64 or more is refused rather than
  panicking (debug) or wrapping (release), and a huge `pos0` can't wrap into the block. No valid statement is newly
  refused: any range that fits the block satisfies the bound.
- **Gates:**
  - `cargo test --lib`: 33 passed, including `every_range_slot_log_and_slots_are_bounded_before_any_shift`, which also
    passes in a debug build (the shift-of-64 case doesn't panic);
  - `selftest`: 32 of 32 on a class circuit, with the `k_log` 27 case refused at `check()`'s first step with the
    `Stmt.InRange` message;
  - `honest` is accepted on an attention circuit;
  - nothing recorded changes.
- **To merge:** #268 at **`0494479e`**.
