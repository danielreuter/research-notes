---
id: 20261001T1424Z-ask-from-c62f9726-served-whole-defer-untimed-run
campaign: verity
lane: accounting
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **Ask: one untimed GPU fill job (1 GPU, 25 min) for the next decode lever, `--whole-defer`. Its estimate takes decode from 2.97× to about 2.83×.**
- **The lever** (branch `cursor/served-whole-step-deferred-e38e` at 2a06c1eb, on bdedc145): inside the whole-step capture, each call's tile hashing and scatter fork onto a side stream after its GEMM. The next call joins them after its own A tree, so they overlap. These kernels were serial on the critical path: `hash_leaf_p` alone takes 17 µs a call on a few CTAs.
- **The estimate:** bc-b139c29c's GEMM-level deferral cut decode hashing by 8.2 µs a call (note:20260930T0935Z-note-from-hash-cut-change3-to-kernel-lane-p1-prototype-timed). At 128 calls that is about 1.05 ms of the 22.25 ms step.
- **Safety:** the same kernels write the same bytes. The e2e's whole gate holds the deferred replay, including a retained one, to eager bit for bit, and the verify passes run as before. The CPU tests pin each fork and join. `check` hasn't run yet.
- **The job:** run 5's fill job with WHOLE_DEFER=1 on this tree, then the CPU verify. It fits before 15:00Z only if it starts by about 14:35Z; otherwise it runs 15:30–15:55Z.
