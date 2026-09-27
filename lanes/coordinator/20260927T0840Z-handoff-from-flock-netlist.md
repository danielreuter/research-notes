---
id: coordinator/20260927T0840Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# PR #83 pushed directly at 68ae79f2; M1's upstream tests fixed

- **Push:** `git push` works again from this VM. `cursor/flock-netlist-m0-4d6a` is at `68ae79f2` on origin (fast-forward from
  `25519ba1`), so no bundle is needed; ignore any pending bundle request.
- **For M1 (bc-2a9978cc):** upstream Flock's unit tests now compile and pass in the patched tree (`2fb47800`). `cargo test
  --release -p flock-core -p flock-merkle -p flock-hash -p flock-transcript -p flock-prover`: 518 passed, 0 failed, 99 ignored.
  - The ignored tests are upstream's SHA-256-era and BLAKE3 targets, marked `#[ignore = "superseded in verity's SHA-512 build:
    …"]` or behind a `sha256-era` feature, and are covered by the `flock-circuit` selftests.
  - The patch file is `backends/flock/flock-sha512-b684b12.patch`.
- **Also since `25519ba1`:** the `unit_draw_session` selftest fix (`adfae8c0`) and the `circuit_bench` pin composed with the
  set's instance statics (`c871bff3`).
- **`68ae79f2`:** the backend identity's `hashes` text said `sha256` for the round digest, statement digest and Σ, which are
  SHA-512 since `eb90718f`; it now says `sha512`. New statement digests differ in value; the e2e bindings (`e51e2b86`) are
  unchanged. flock-verifier and one-stage-e2e have a one-line notice.
