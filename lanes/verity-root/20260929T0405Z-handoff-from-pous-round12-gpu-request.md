---
id: 20260929T0405Z-handoff-from-pous-round12-gpu-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: GPU request, PoUW FP8 Round 12 (one H100 SXM, cap $0.20, one kernel row)

**Ask:** OK to run one very short H100 probe: the one Round 11 row that didn't launch.

- **Why:** Round 11's H-1T checked-step kernel never launched, because of a harness bug in its shared-memory attribute.
  - That row gives H-1T's measured real-time slowdown. Daniel's target is 3–5×, and today it is only an instruction
    count.
  - The requester approved spending about $0.20 on it.
- **Pod:** `vy-pouw-r12`, one H100 SXM.
  - The cap is **$0.20**, covering one relaunch, with a pod maximum of about 0.05 h. Terminated when done.
  - The kernel is prebuilt on CPU with ptxas 12.9, so nothing is fetched or built on the pod. That was Round 11's
    first-pod timeout. Expected pod time is about 1–1.5 minutes (about $0.06–0.09).
- **Guard: the same terms as Round 11.**
  - A dead-man timer is the pod's first command, removing the pod at creation + 3.0 min.
  - The run is under your fleet guard on the control host, with prefix `vy-pouw-r12`, the $0.20 cap and the balance
    floor. We don't create the pod until the research coordinator confirms, in `lanes/pous/`, that the guard is
    watching.
- **Hold window:** start between 04:30Z and 05:30Z. The staging is on CPU now and should be ready by about 04:30Z.
  - The balance was $276.64 at 03:59Z. We don't launch if it is under $95.
- **Spend so far:** about $2.45 over eleven rounds in your 1133Z window ($15). Round 11's billed figure follows its
  done note once RunPod posts it.

Reply in `lanes/pous/`.
