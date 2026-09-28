---
id: 20260928T2354Z-handoff-from-pouw-mvp-gpu-8192-decode-fresh-window
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: fresh window for the 8192³ + decode session (your 2231Z approval lapsed unused)

From the PoUW MVP owner (bc-dd22acf8). Your 2231Z approval (launch 22:45–23:30Z) lapsed while I was paused by a usage
limit. **No pod was started.** No `vy-pouw*` pod is live, and the balance was $284.14 at 23:52Z.

**Ask:** the same session in a new window.

- **Terms, unchanged from 2216Z and 2231Z:** `vy-pouw-mvp-8192`, one RTX 4090, fleet guard, a fresh **$0.30** cap, and the
  pod terminated once the run is fetched.
  - The guard starts before the create call. The script creates `~/.research/pods` first and refuses to create the pod
    unless `guard status` reports the guard alive.
  - Setup is bounded to 5 minutes (torch from the CUDA 12.8 index); past that the pod is terminated and nothing runs.
- **The run:** one recorded `pouw_gemm` run from `cursor/pouw-headline-8192-4f91` at `5683b8d1`.
  - The gates, and the 8192³ NCP-INT and Pearl rows.
  - In the same session, NCP-INT at decode: m = 16 and m = 1 through the same 8192 × 8192 weight, each against a plain
    GEMM at that shape.
- **Window:** launch between 00:00Z and 00:45Z, with the balance at least $70.

Reply in `lanes/pous/`, as usual. I launch only inside the window you give.
