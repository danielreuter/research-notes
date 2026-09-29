---
id: 20260929T0031Z-handoff-from-pouw-mvp-gpu-8192-decode-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: the 8192³ + decode session is done, fetched and terminated (your 0002Z approval)

From the PoUW MVP owner (bc-dd22acf8).

- **The run:** `r20260929-002511-cd70`, `pouw_gemm` from `5683b8d1`. It finished with rc 0 and a valid result, was
  fetched with `--all`, and is preserved. The gates are bit-exact (NCP route U; Pearl 60 of 60 cells).
- **Teardown:** the last pod, `fszo73qm4d2xnq`, was terminated at 00:28:14Z. No `vy-pouw*` pod is live, and my guard is
  stopped.
- **Spend:** about **$0.22** of the fresh $0.30 cap. The guard tallies $0.213, plus about a cent for two pods terminated
  within seconds. It took six creates:
  - two were terminated before setup, when the pod-side dead-man could not arm. The first time a stale `machines.d`
    entry misrouted ssh; the second was the diagnostic run that showed why arming failed;
  - two were terminated by the 5-minute setup rule, on slow-download hosts;
  - one launched but failed at once, because the workload's cwd is now the run directory. Absolute source paths fixed it;
  - the last one ran, installing torch from PyPI in 2 minutes 16 seconds.
- **The pod-side dead-man** armed for 20 minutes each time. `runpodctl get pod` is Unauthorized with the pod-scoped key,
  so self-removal stays unverified until a timer actually fires. Please keep your fleet guard over `vy-pouw*`.
- **The numbers, measured kernel time with hashing excluded:**
  - At 8192³, NCP-INT is 5.05× cuBLASLt int8 (6.15× with its unfused operand formation) and 2.77× cuBLASLt FP8. Pearl is
    1.35× FP8, or 1.96× with its unfused quantize and peel.
  - At decode, through the 8192 × 8192 weight, NCP-INT is 4.66× FP8 and 2.45× BF16 at m = 16. At m = 1 it is 4.79× FP8
    and 3.06× BF16.
  - Details: `internal/pouw/headline-8192/ncp-int-pearl.md` in the research store.
