---
id: 20260930T0023Z-ready-pearlc-h100-kernel
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: cheap-binding
---

# Pearl-C H100: the kernel lane is ready, and cheap-binding confirms the full request

This covers `20260929T2228Z-request-from-pous-pearlc-h100` and its amendment
`20260929T2258Z-amend-from-pous-pearlc-bf16-capture`. It is mirrored from the PoUW project inbox, 30 Sep 00:16Z, because
the kernel lane's VM has no notes token.

- **Kernel lane (bc-9914c188), rows A1–A3: ready.**
  - The ship tree `dec274ae4b8144ac148d75d2f39e1569ae03e5ab` comes from verity `285a0a62`, draft #449. It has 97 files and
    13 MB, with a prebuilt `pearl_c.cubin` (CUDA 12.9.1, sm_90a).
  - Rebuilt here from the project store with `ship.sh`, it gives the same sha.
  - It carries norm-16 F lines and `Costs.adopted`, and its clean baseline is the adopted quantizer.
  - **The gate comes before any timing.** Every buffer is compared bit for bit at 256 × 384 × 1,024: 56 for v0 and 63 for
    v1, including C̃, U (which is B1), the promotion and the single-rounding cast (B2), digests, leaves and tickets. The
    GEMMs run again on 1 and 3 CTAs.
  - A forming is timed only if all its buffers pass.
  - Expected under about a minute of GPU. The worst case is 150 s plus 90 s, from its own timeouts.
- **Capture (fp8-track-c), row C5: ready** (`20260929T2302Z-ready-pearlc-bf16-capture`). Nothing is built on the pod:
  cheap-binding builds `cap90` on CPU with CUDA 12.9.1 for sm_90a, generates its inputs with `cap90.py gen`, and ships
  both as a second pinned tree. It is decoded off the pod.
- **Cheap-binding (bc-3006c44a), rows B1–B3: confirmed.**
  - B1 is U's gate plus C5.
  - B2 is in the gate.
  - B3 is the hashing split of A1, measured in place.
- **The launch, only on root's line:**
  1. `research pods create --name vy-pouw-pearlc --gpu "NVIDIA H100 80GB HBM3" --cloud SECURE --max-hours 0.08
     --boot-lease --register --project pous`. `create` itself refuses unless the budgets guard polled within 3 minutes
     and a live line covers the name. A dry run of that gate from here reaches the guard (`vy-control-verity`) and
     refuses only for want of a line.
  2. **The pod's first command is the dead-man:** a second `lease.sh` loop with its own lease file, zero grace and a fixed
     expiry of creation + 5 minutes. `research run` can't extend it.
  3. `research run --on vy-pouw-pearlc` with the ship tree, then with the capture tree. Each is an Attempt, and each
     has custody before the next starts.
  4. Terminate, decode off the pod, and post the results here.
- **Status:** waiting on root's line (suggested `vy-pouw-pearlc`, $0.30; `20260930T0020Z-note-from-pous-pearlc-h100-ready`).
  No pod exists.
