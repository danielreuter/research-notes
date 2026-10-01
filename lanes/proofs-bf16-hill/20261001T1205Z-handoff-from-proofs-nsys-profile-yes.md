---
id: 20261001T1205Z-handoff-from-proofs-nsys-profile-yes
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Two node-1 GPU jobs at 12:55Z: the K=16384 s4 re-run and one nsys profile

The research owner's yes, 4:54 AM PDT (Slack `1790855684.072569`): "yes to the one nsys profile. The C-Flock changes
(zerocheck, Ligerito, lincheck at K=16384) come back to me with the profile, and agree them with M0 (flock-netlist) before any
edit, since M0 owns the prover."

At 12:55Z or later on node 1 (nothing starts there 12:15–12:55Z; `/workspace` is offline 12:40–12:55Z):
1. **The clean K=16384 s4 re-run** (128 GiB), if NUMA node 1 has room, per `note:proofs-bf16-hill/20261001T1145Z-…`. The
   question: does the 2.61e7 best hold on a clean slice? If there's no room, 2.61e7 stands.
2. **One nsys profile of a K=2048 session** (64 GiB, one GPU job, minutes). The question: where a prove's time goes, so
   that the zerocheck, Ligerito and lincheck targets are chosen from the profile. Publish it as an `art:`.
3. Then write the profile up in `lanes/proofs/`, with the changes you'd make and each one's expected share. Make no C-Flock
   edit: I take it to the owner, and it's agreed with M0 (flock-netlist) first.

Keep proofs' node-1 GPU jobs at 4 or fewer in flight; proofs-arch and verify-overlap each submit one at 12:55Z too.
`source ~/.proofs-env/env.sh` (this VM) for the tokens. Never print it or paste any of its values anywhere.
