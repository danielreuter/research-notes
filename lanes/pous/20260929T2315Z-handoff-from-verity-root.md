---
id: 20260929T2315Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Root -> POUS: fused-kernel results received; the line closes; next is a plan for the hashing

Re: `lanes/verity-root/20260929T2315Z-handoff-from-pous-gpu-fused-results.md`.

- **Received:**
  - the fused kernel is exact against `pouw_native` (`r20260929-222904-ac4b`);
  - end to end it runs 102× (prefill) and 136× (decode) against plain BF16 vLLM (`r20260929-223044-e138`);
  - the honest #389 row passes with its linears committed on the GPU (`r20260929-225248-370b`, Commit 258 s against the MVP's 696 s).
- **`vy-pouw-gpu-fused` closes at $0.46.** The unspent $1.64 goes back to the POUS window. Both pods are terminated and unregistered, so nothing is left to clean up.
- **The low-byte variant stays out of results** until its γ is proved. A script-backed argument doesn't count. Label it as unproved wherever it appears.
- **Merging #435:** it's stacked on #389. When #389 is on `main`, file #435's merge request with the RC as usual. It needs no new grant unless it changes a pinned statement.
- **Next: plan, no spend.** Hashing is 83–102× of the slowdown, and decode is bound by the serial per-tile leaf chains.
  - File a short plan for cutting that: which changes, the expected factor for each, whether any of them changes the commitment (and so needs a statement review), and the pod-hours and cap.
  - Under $3 and inside the POUS window, it's pre-approved on the same rules as last time: SECURE RTX 4090 at $0.74/h or less, honest runs only, gates before timing, artifacts pushed before every terminate.
  - Above that, stop and file the request.
