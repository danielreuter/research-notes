---
lane: vllm-verify-optins
kind: report
created: 2026-09-27T06:14Z
status: open
---

CHECKPOINT 8515c79e (06:41Z) [open] GO (coordinator 0640Z, cap $10). POD START 06:41Z vyv-rf-verify-optins-cpu = RunPod l32zhicuc7ce1b, cpu5m 16 vCPU/128 GB (~$1.04/h; the 32-vCPU shapes had no stock), guard 90, registered; expected end ~12:30Z. Handoff renamed 0640Z -> vllm-coordinator/20260927T0626Z-handoff-from-vllm-verify-optins.md. #74 on the VM so far: cross_call 0 recomputes on 5/9 stored Programs both ways; FP8 member check recorded 186,480 violations / 36.47 G recomputed gates -> SHARED_SCALE 0 / 0 (+287.2 M committed words). Next: bootstrap + smoke Build
CHECKPOINT 8515c79e (06:26Z) [open] ESTIMATE sent: internal/lanes/vllm-coordinator/20260927T0640Z-handoff-from-vllm-verify-optins.md (one cpu5m 32/256 pod ~4.2 h ~$8.8, cap $10); verification merge cursor/verify-optins-merge-a795 @ b7a4092a (main ae5db5d3 + #98 + #105/#102 + #106 + #109, 2 additive conflicts); no pod until GO; preparing scripts on the VM
CHECKPOINT 8515c79e (06:21Z) [open] recon: Builds are GPU-free (meta export + declared target); plan = one CPU pod runs real Builds of #57 (off/once) and #73 (off/check-inf) + #74 off, SHARED_SCALE by substitution on the stored #74 Programs; record digests + stored Programs located (art:5e925a59 / f9439154 / 9d14bd11); #74 value check needs real x_s: no stored run has values -> evaluating a Program prefix on CPU; estimate to vllm-coordinator next
CHECKPOINT 8515c79e (06:14Z) [open] started 06:14Z, agent bc-a80fa085; notes direct; #105/#106/#109 all OPEN (not on main 3040ac1f..ae5db5d3) -> local merge of PR heads b0a12771/df13126f/39e3b24c; CPU first, no pod yet; next: merge + locate recorded Builds for #57/#73/#74
