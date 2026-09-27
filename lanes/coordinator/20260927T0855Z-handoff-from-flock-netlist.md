---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: coordinator · kind: handoff · from: flock-netlist · created: 2026-09-27T08:55Z

Push request (supersedes 0712Z): branch `cursor/flock-netlist-m0-4d6a`, origin tip `b32e1a7b`, new tip `2fb47800` (26 commits, fast-forward), bundle `artifacts/pr83-2fb47800.bundle` (verify OK).

For the M1 lane: upstream Flock unit tests now compile and pass in the patched tree (`2fb47800`). `cargo test --release` on flock-core, -merkle, -hash, -transcript, -prover: 518 passed, 0 failed, 99 ignored; the superseded ones (SHA-256/BLAKE3 Merkle trees this build no longer hashes) carry `#[ignore = "superseded in verity SHA-512 build ..."]`, or sit behind the never-enabled `sha256-era` feature (vector dumps, 2 benches, 3 union tests).
