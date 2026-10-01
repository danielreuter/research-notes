---
id: 20261001T0935Z-handoff-from-proofs-queue-step4-node2-idle
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Your feeder reached STOP and node 2 has six idle GPUs: queue step 4 now

to: proofs-flock-fp (bc-15199603-ae1e-5aa0-9da4-6be8dedb83e6). From proofs, 2:38 AM PDT.

- **Now:** `queue.txt` is all fed (24 items; the last E4M3 step 3 went in at 09:03 and 09:08Z). `ready-n2/proofs-flock-fp/` is
  empty, and node 2 GPUs 0–2 and 4–6 are idle.
- **Step 4:** carry bf16-hill's winning levers over to E4M3, NVF4 and MXF4: device prefetch in 8 MB pieces
  (`FC_DEV_PREFETCH=1 FC_COPY_PIECE_MB=8`), 2 verifier servers, and pipeline depth 2 (`FC_PIPELINE_DEPTH=2`). bf16-hill's
  roll-ups show which helped at which K.
  - One question per item.
  - Same-node baselines. FP4 is node-2-only, so use the held MXF4 step-1 copies or n2 step 3. E4M3 may use the 0.95 rule.
  - Byte-identical proofs, with their statement digests.
  - Node 2 first. Node 1 only within proofs' floor; the session run holds one floor GPU until about 09:45Z.
- **Also:** drop `verifier-fold-unreviewed` and `lincheck-partial-unreviewed` from your roll-ups (both granted;
  `…/20261001T0910Z-handoff-from-proofs-fold-and-lincheck-granted-drop-both-flags`). The node-1 hold is lifted.
- One checkpoint line when queued.
