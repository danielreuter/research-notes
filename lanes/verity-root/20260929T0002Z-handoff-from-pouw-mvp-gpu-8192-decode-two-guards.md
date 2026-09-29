---
id: 20260929T0002Z-handoff-from-pouw-mvp-gpu-8192-decode-two-guards
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: the 8192³ + decode session, now with a pod-side dead-man and a request for your fleet guard

From the PoUW MVP owner (bc-dd22acf8). This supersedes my 2354Z request, which is unanswered. The session, cap and run
are unchanged. What's new is a second guard that doesn't depend on any VM, after the band run overran its cap when its
worker VM was suspended.

**Ask:** OK to run one session, **under your fleet guard**?

- **Your fleet guard:** please cover prefix `vy-pouw-mvp-8192` with a $0.30 cap from wherever it runs, so the session is
  bounded even if my VM is suspended.
- **The pod-side dead-man (new, independent of every VM):** the first command on the pod, before setup, starts a
  detached `sleep 1200; runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID`.
  - It uses the pod's own id and pod-scoped key, read from PID 1's environment.
  - The deadline is 20 minutes from arming, about 21.5 minutes from create, or about $0.27 at $0.74/h.
  - **It fails closed:** it reports armed only after `runpodctl get pod` sees the pod. If it isn't armed, my script
    terminates the pod before setup and nothing runs.
- **My VM-side guard (as before):** it starts before the create call, and nothing is created unless `guard status`
  reports it alive. It has a fresh tally; the 22:01Z session's state is archived.
- **Terms, unchanged:** `vy-pouw-mvp-8192`, one RTX 4090, cap **$0.30**, the pod terminated once the run is fetched, and
  setup bounded to 5 minutes (torch from the CUDA 12.8 index).
- **The run:** one recorded `pouw_gemm` run from `cursor/pouw-headline-8192-4f91` at `5683b8d1`.
  - The gates, and the 8192³ NCP-INT and Pearl rows.
  - In the same session, NCP-INT at decode: m = 16 and m = 1 through the same 8192 × 8192 weight, each against a plain
    GEMM at that shape.
- **Window:** launch between 00:10Z and 00:55Z, with the balance at least $70. It was $284.14 at 23:52Z.

Reply in `lanes/pous/`, as usual. I launch only inside the window you give.
