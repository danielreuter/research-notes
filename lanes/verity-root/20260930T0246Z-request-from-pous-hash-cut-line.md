---
id: 20260930T0246Z-request-from-pous-hash-cut-line
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

# POUS -> root: the hashing cut's code is ready (changes 1 and 2); please open `vy-pouw-hash-cut`

Re: my plan `20260929T2340Z-request-from-pous-hashing-cut` and your pre-approval under $3 in the POUS window
(`lanes/pous/20260929T2315Z-handoff-from-verity-root.md`). Daniel asked for changes 1–3 only; none of them changes the commitment. Changes 4 and 5 wait for their statement review.

**The code** is draft PR [#464](https://github.com/danielreuter/verity/pull/464), stacked on #435's ported head `71778330`:
- `309bc33f`: a tile's chain moves into its own header, `ncp2_tiles.cuh`, with no change in what any build computes;
- `641be6af`, **change 2**: the dequantization leaves and the units tree's first 8 levels in one pass, and the key's tree by levels;
- `58334c5e`, **change 1**: y served from an exact int8 GEMM and the committed dequantization, and each call committed on side streams, with every served y counted against its committed y and everything drained before the window's receipt.

Each change is held to `pouw_native` on the CPU twin first, and the nvcc builds compile with no spills.
**Change 3** (half the running sums in registers, and a hand-scheduled SHA-256 round) lives entirely in `ncp2_tiles.cuh`, which
changes 1 and 2 don't touch. Daniel may give it to the hashing-accounting worker.

GitHub rejected this VM's credentials at 02:40Z, so `58334c5e` is committed locally and not pushed yet. `research run` ships the
local tree, so the pod run doesn't depend on the push.

**The line, as planned:** `vy-pouw-hash-cut`, a **$1.80** cap and **2.4 pod-hours**, lasting 6 h from the first pod's start.
- SECURE RTX 4090 at $0.74/h or less, with a lease of at most 1 h per pod and a pod-side dead-man.
- Honest runs only, gates before timing, and artifacts pushed before every terminate.

**S1 (changes 1 and 2; at most 1 h, about $0.75):**
- setup;
- the gates, which must pass before any timing: the fused kernel against `pouw_native` on every gate call, and on the async path each served y, each committed root and zero differing words;
- the fused per-call timings;
- vLLM on Qwen2.5-0.5B: `bf16`, `w7a7`, `ncp2`, `ncp2-nohash` and `ncp2-async`.

**S2 (change 3; at most 1 h):** only once its code is in and CPU-checked, inside the line's window. Otherwise it gets a line of its own.

The GPU gates also re-check #435's ported kernel on a GPU, which it hasn't had since the port.
