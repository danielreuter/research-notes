---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T04:47Z
---

# main now pins A-GKR circuits (PR #13, c1891d48): merge main into your branch, add the E4M3/NVFP4 pin lines, give the bound variant its own relation name

- `verity-gkr-verify --relation R` now rejects circuit files not in the compiled-in pin list (`backends/gkr/verifier/pins.txt`,
  `src/pins.rs`); `bench_result.py` counts a rep only when the verdict says `circuit_pinned`. Only bf16-ampere and bf16-hopper are
  pinned on main. Design + the exact E4M3 / NVFP4 lines to add: the Project store doc
  `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/agkr-circuit-pin.md`.
- For your integration (step 1): merge origin/main (>= c1891d48) into lane/agkr-bound, add the fp8-ada, fp8-hopper and fp4-nvf4 pin
  lines for the statements the verified cells use (incl. the merged-LK ones), rebuild the verifier on your pod (Rust >= 1.89), and
  confirm `--relation` accepts the verified cells' statements. Stale verifier binaries on pods fail validation until rebuilt.
- For the bound variant (step 2): give it its own relation name(s) and pin lines; never reuse an existing relation name for a
  different statement.
