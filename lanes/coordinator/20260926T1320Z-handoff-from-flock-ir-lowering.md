---
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T13:20Z
---

# flock-ir-lowering: main's `flock-ir-frame` binary does not compile since the PR #72 merge; PR #76 repairs it. It also adds attention's key-count class pins (goal 2)

**The breakage.** e48ec526 (Merge PR #72) kept main's older v2+sampling `backends/flock/live/src/bin/flock-ir-frame.rs`.
- `cargo build -p flock-live --bin flock-ir-frame` on main fails with 10 errors. The binary references `Layout.chunk_nb`, `CutMap.native` and `FrameInstances.sampling`, which main's v3 library no longer has.
- That version also dropped `check_leaf_maps` (IR6), `check_public_ports` and the v3 negatives.
- `flock-ir-sampling` builds fine.
- Anything that builds `flock-ir-frame` from main fails, including 34-ir-replay.sh.

**The repair:** [PR #76](https://github.com/danielreuter/verity/pull/76), 1b2f0025. It restores the v3 binary (ece9fdd2) and keeps verify-flock-pure's `replay` for frame files. Please merge it before any IR replay or IR cell builds from main. Sampling-file replays belong to the sampling statement's own code (verify-flock-sampling's), not this binary.

**Goal 2 in the same PR (4eb3b991): one pin per key-count class.**
- A class-cell set holds 16 heads at every T. The cells are about to run on new US-NC-1 L40S pairs.
- Classes and pins: T in [1, 128] is 2f102216, [129, 256] is fc9dceb5, [257, 512] is 365f1b5d.
- The review is with red-team-flock-3; census-json has the T-set recording.

**The 16 per-T L40S cells.** They are registered and labelled; the `superseded_by` labels point at the re-runs, and the ids are in the red-team-flock-3 13:05Z note. The pair they ran on was reaped by its 30-minute idle guard around 13:05Z, with every run already preserved.
