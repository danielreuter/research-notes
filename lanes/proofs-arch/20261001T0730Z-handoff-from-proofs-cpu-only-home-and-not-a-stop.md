---
id: 20261001T0730Z-handoff-from-proofs-cpu-only-home-and-not-a-stop-proofs-arch
campaign: overnight
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# CPU-only work goes to node 2's provers range; 7:50 AM PDT is not a stop

Re `note:20261001T0724Z-handoff-from-proofs-arch-provers-submit-in-error`: the stub was the right fix. Thanks for saying so.

- **Where CPU-only work goes:** node 2's cores 128–191 are proofs' (infra, `note:20261001T0703Z-note-from-infra-node2-prover-cores-live`).
  Put the old-fold half as a node-1-format item with `"gpus": 0` and its `QUESTION` in node 1's
  `/workspace/jobs/ready-n2/proofs-arch/`. [proofs-n2-hill](bc-f0eeea0e-2215-5745-b587-8de6ca061478) takes it when a slot is
  free and no GPU point is waiting, pinned to a clean slice. Nothing there may run past 14:50Z unless I say the range is
  extended, and nothing is placed 20 min before 10:00, 11:30, 13:00 and 14:00Z.
- Node 1's `provers` stays for GPU points.
- **Daniel, 12:22 AM PDT: nobody stops before he wakes (about 9:20 AM PDT).** After the old-fold half, keep going on the next
  question in your list. Stop only when the list is done, and then write here what you'd run next.
- **Anything that needs Daniel:** write it in `lanes/proofs/` as `needs-daniel:` with your recommendation, and carry on.
