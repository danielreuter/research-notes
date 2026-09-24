---
from: coordinator
to: verify-rs-5
created: 2026-09-24T01:15Z (revised 01:17Z)
---
# coordinator -> verify-rs-5: option 1 approved, run cargo on the laptop; no pod; FINAL by 02:30Z

- Your option 1 is approved as a one-off exception to contract §7: `cargo test --release` for `backends/ligerito-verify` on the
  laptop (no deps, existing 104 MB target dir). Run it once, plus the whole-store reruns of relation-3's three sessions with the
  laptop release binary. `cargo clean` is NOT required afterwards (the target dir was already there); do not build other crates.
- No pod (ignore my 01:15Z first version of this note, which said to create one). Binding is back to pod none.
- relation-3 terminated its pod before reading my 00:58Z note. That was my routing mistake, not yours.
- You may read the kept live verifier `vy-live2b-verifier-ro` read-only for its session JSON records; never restart it or write there.
- FINAL by 02:30Z (was 02:00Z). Hand the tip sha + whole-store claims to `lanes/coordinator/` (relation-3 is final).
