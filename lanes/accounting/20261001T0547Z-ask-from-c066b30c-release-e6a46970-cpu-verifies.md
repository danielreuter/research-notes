---
id: 20261001T0547Z-ask-from-c066b30c-release-e6a46970-cpu-verifies
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c), now the owner of bc-e6a46970's node-2 jobs (note:20261001T0536Z-order-from-compute-accounting-stop-24-old-agents); re note:20261001T0350Z-report-from-node2-ops-overnight-gate
---

# Ask, yes or no: release GPU 0's 52 held CPU verifies (`fp8gcver-*`, `fp8ver2-*`, `fp8chainver-die2..5`) to node 2's pous CPU slots tonight

- **What they are:** the CPU half of GPU 0's FP8 step check. The GPU half spent 5.1 GPU-h and is done.
  - 40 `fp8gcver-*` re-check the kept tiles (1.67e8 tiles, 2.1e10 words) bit for bit on the CPU.
  - 8 `fp8ver2-*` and 4 `fp8chainver-*` are the second fill's step and chain verifies. Die 0, 1, 6 and 7's chain verifies have already run (in `fill/done/`; I haven't read their passes yet).
  - node2-ops held all 52 at 03:50Z (8:50 PM PDT), as off your overnight list.
- **The question they answer:** does the sm_120 E4M3 step model hold, gated beyond control, on every tile the GPU check kept? This is the evidence behind #492 (W1), γ and the divisor. Until it runs, the 5.1 GPU-h of GPU checks back no claim.
- **Cost (Estimated by bc-e6a46970):**
  - About 17 CPU core-h for the 40 `fp8gcver`, plus the 12 smaller ones.
  - No GPU. They run at nice 19 on the pous slots (cores 96–127), at most about 9.5 GB per worker.
  - They pause during timed windows, as all fill does.
- **My recommendation: yes.** On your yes, node2-ops moves them back to `queue/`, and I add the question line its gate asks for to each header. Afterwards I read each unit's pass, preserve the small files and post the totals here.
- **If no,** they stay held, and I ask again at 8 AM PDT, when the overnight rule ends. The 98 GB of launch files stay on disk either way.
