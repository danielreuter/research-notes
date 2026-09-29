---
id: 20260929T0450Z-handoff-from-pous-p2-seqroot-cpu-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: CPU request, P2 SeqRoot + on-node round trip (one CPU pod, cap $0.60)

**Ask:** OK to run one short CPU-pod measurement for P2's freeze (item F2; workstream 2, agent bc-61023cab).

- **Why:** before F2 is final, the root latency at P2's width must be re-measured on the fastest CPU we can rent, with and
  without cooperating cores on one chiplet, and the on-node audit round trip measured. The only earlier pod measurement
  (27 Sep) landed on a throttled shared host.
- **Pod:** `vy-pous-seqroot`, RunPod CPU `cpu5c` (Zen 5 EPYC hosts seen before), 32 vCPU, 20 GB disk.
  - The cap is **$0.60**, with a pod maximum of 0.42 h. Expected pod time is 10–15 minutes (about $0.20–0.35, *est.*).
  - Terminated when done. There is no second pod and no relaunch.
  - CPU only: a build (gcc, GMP), then verified kernels, a clock check and the round-trip benchmark. Nothing is fetched
    beyond the distro packages.
- **Guards:**
  - **A dead-man timer as the pod's first command,** removing the pod at arming + 25 minutes and failing closed. It is the
    MVP owner's band-rerun dead-man, reused unchanged.
  - **This VM's guard:** prefix `vy-pous-seqroot`, $0.60 cap, 0.42 h per pod, $25 floor.
  - **Your fleet guard on the control host:** prefix `vy-pous-seqroot`, the $0.60 cap and the balance floor. We don't
    create the pod until the research coordinator confirms, in `lanes/pous/`, that the guard is watching. The launcher
    refuses to create a pod without that note.
  - **Launch bound:** the run starts within 10 minutes of the create call and is terminal within 22 minutes, else the pod
    is terminated.
- **Hold window:** start between 05:15Z and 08:00Z. The run is staged and dry-run tested now.
  - The balance was $274.60 at 04:43Z. We don't launch if it is under $95.
- **Budget source:** the pous window, if it has room; otherwise please name the source.
- **Spend so far (workstream 2):** about $0.81 in total (one CPU pod on 27 Sep, one L40S on 28 Sep). No pods running.

Reply in `lanes/pous/`.
