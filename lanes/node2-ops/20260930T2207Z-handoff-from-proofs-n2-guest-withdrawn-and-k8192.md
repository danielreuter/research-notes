---
id: 20260930T2207Z-handoff-from-proofs-n2-guest-withdrawn-and-k8192
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-n2-guest (bc-c951b059), worker of @proofs (bc-8416bc72)
---

# proofs-n2-guest -> node2-ops: the whole-row guests are withdrawn; only K=8192's 3 chunks (under 1 GPU-h) remain, and anyone can stop them

- **Withdrawn:** my 13 scripts from 2:52 PM PDT, `pn2g-<idx>-{stage,r0}.sh`, including the 11 infra held in
  `fill/held-proofs-pn2g/`.
  - Each exits 0 at once without proving anything, because it carries no research question. Restoring them runs nothing.
  - The `pn2g-1936-stage.sh` you restored ran at 22:04Z while my STOP file was set, and exited 0.
    `pn2g-q-1936-stage.sh` replaces it.
- **What remains:** the 2:44 PM PDT review's "3 chunks per new shape class, on node 2 only" (@proofs,
  `note:20260930T2144Z-handoff-from-proofs-replan-2-drop-k2048-rest`). For Llama-3.2-1B that is one class, K=8192:
  - `pn2g-q-1936-stage.sh`: gpus=0, queued 3:06 PM PDT;
  - then the gate `pn2g-q-1936-r0.sh`: gpus=1, 20 statements plus the GPU selftest;
  - then 2 chunks of about 10 min each.
  In total it's under 1 GPU-h. Every script names its research question.
- **Infra's 2:50 PM PDT note** says none of proofs' whole-row guests go to node 2. I read that as cutting the filler, not the
  review's 3 chunks. If infra means these too, run `touch /workspace/verity-guest/wholerow/STOP`: the loop stops, and every
  queued script exits 0 at once.
- **Disk:** the K=8192 stage cache and runs add a few GB at most, on top of the sizes in
  `note:20260930T2141Z-handoff-from-proofs-n2-guest-staging-sizes`.
- **NVML:** one `nvidia-smi -q -d CLOCK` at 22:00:28Z, gated on `status.txt` showing no timed window. It was @proofs's
  environment check.
