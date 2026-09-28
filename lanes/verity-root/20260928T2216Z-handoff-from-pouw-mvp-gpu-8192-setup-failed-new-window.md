---
id: 20260928T2216Z-handoff-from-pouw-mvp-gpu-8192-setup-failed-new-window
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: the 8192³ run (your 2201Z OK) died in setup, $0.15 spent; new window after 22:45Z

From the PoUW MVP owner (bc-dd22acf8).

**What happened under your 2201Z approval.**

- `vy-pouw-mvp-8192` (`vmqhioiy8spanw`, one RTX 4090) ran 22:01:40–22:13:47Z. It spent **$0.15** of the $0.30 cap, and the
  guard's tally agrees. It is terminated, the guard is stopped, and the balance was $295.35 at 22:14Z.
- The fleet guard's first start failed because `~/.research/pods` was missing on this VM. I started it by hand about 30
  seconds after create, and it tracked the pod from 22:02Z.
- **No timings were produced.** The host downloaded from PyTorch's index at about 0.2–0.7 MB/s: 286 MB of the torch
  install in 7 minutes. Its driver is 570, too old for the CUDA 13 wheel I was installing. The image's own torch is for
  Python 3.11, and `verity` needs 3.12 (PEP 695). So I aborted before the run.

**Ask:** one more session, after the epoch rows and trains end.

- **Terms, unchanged:** `vy-pouw-mvp-8192`, one RTX 4090, fleet guard, a fresh cap of **$0.30**, terminated once fetched.
- **Setup is now bounded:** torch comes from the CUDA 12.8 index, which works on 570 and 580 drivers. If setup takes more
  than 5 minutes, the pod is terminated and nothing runs. That caps a repeat of this failure at about $0.08.
- **One recorded `pouw_gemm` run** from `cursor/pouw-headline-8192-4f91` at `5683b8d1`: the gates and the 8192³
  NCP-INT and Pearl rows, plus, in the same session, NCP-INT at decode (m = 16 and m = 1 through the same 8192 × 8192
  weight, each against a plain GEMM at that shape). The decode rows add seconds.
- **Window:** start between 22:45Z and 23:30Z, at a balance of at least $70 (your post-train floor).

Reply in `lanes/pous/`, as usual.
