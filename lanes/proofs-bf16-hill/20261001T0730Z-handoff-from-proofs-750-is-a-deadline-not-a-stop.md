---
id: 20261001T0730Z-handoff-from-proofs-750-is-a-deadline-not-a-stop-proofs-bf16-hill
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# 7:50 AM PDT is a deadline, not a stop: keep climbing until Daniel is up (about 9:20 AM PDT) and after

Daniel, 12:22 AM PDT: nobody stops before he wakes. 7:50 AM PDT is the deadline for the overnight set, not an end time.

- **Past 7:50 AM PDT (14:50Z):** keep climbing every K, with the next untried lever after each step's clean points. Don't wind
  down for the deadline. Stop only when the ladder is done (idle beats padded), and then write here what you'd run next.
- **Node 1's window still holds:** nothing submitted after 5:05 AM PDT (12:05Z) that could run past 5:35; queues hold at 5:10;
  `/workspace` is offline 5:40–5:55. Resume at 5:55 AM PDT (12:55Z) once `/workspace` is back, and re-run any point the
  window cut. A preempted point is re-run, not reported.
- **Node 2 is granted:** cores 128–191 are proofs' provers' (infra, `note:20261001T0703Z-note-from-infra-node2-prover-cores-live`).
  Put node-1-format items in node 1's `/workspace/jobs/ready-n2/proofs-bf16-hill/` once
  [proofs-n2-hill](bc-f0eeea0e-2215-5745-b587-8de6ca061478) posts its parity result in this lane. The range ends at 14:50Z
  unless I tell you it's extended (I've asked). No placement there 20 min before 10:00, 11:30, 13:00 and 14:00Z.
- Your kcompactd1 and slot-176 findings went to infra directly, which is right. If a point lands on either again, add its run
  id to that note rather than re-running in a loop.
- **Anything that needs Daniel:** write it in `lanes/proofs/` as `needs-daniel:` with your recommendation, and carry on with
  something else. I put it on his morning list.
