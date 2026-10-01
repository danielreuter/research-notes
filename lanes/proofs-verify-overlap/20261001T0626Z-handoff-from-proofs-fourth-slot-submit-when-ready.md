---
id: 20261001T0626Z-handoff-from-proofs-fourth-slot-submit-when-ready
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Four prover slots now: submit the pair as soon as it's ready

Infra, 11:21 PM PDT: provers run on cores 128–191, four 16-core slots (nominal CPU 64), and may borrow every idle node-1
GPU (up to 8). Commits still take GPUs back.

- **Your submit rule changes:** submit when provers' CPU use is **32 or less** (two free slots of 64), not 16. Check:
  `sudo -n k3s kubectl get clusterqueue provers -o jsonpath="{.status.flavorsUsage}"`.
- At 11:25 PM PDT, 48 of 64 were in use: a BF16 point, flock-fp's K=16384 staging and one arch CPU job. The BF16 point
  ends within minutes. Until your pair has submitted, the lanes and arch hold at most 2 slots, so two stay yours.
- If only one slot is free when you're ready, submit the first leg and the second when the next slot frees. Both legs in
  the same hour is enough.
- Then report phases beside step 4's (148.7 s, `r20261001-044422-bc17`), and the held seconds per job. Console reads that number from
  `/workspace/usage/overnight/proofs.json`, so tell me the run ids and I'll update it.

**Node 1's window:** queues hold at 5:10 AM PDT, nothing new starts after 5:15, and `/workspace` is offline 5:40–5:55.
Submit nothing after 5:05 that could still be running at 5:35.

**Next, after the pair (goal 2's remaining gap, about 88 s → 50 s):** Daniel asked (11:11 PM PDT) whether the pre-timing
check could run once per pod or GPU session instead of once per job. Plan it so a GPU session proves N points back to back after a single
preflight, where each point's record cites the session's preflight record. Send me the design and the expected seconds
per point (about 46 + 42/N s by my estimate) before building it.

**Naming (Daniel, 11:11 PM PDT):** the pre-timing check is the **preflight check**, never the "gate". Use that word in
notes and reports from now on. The code rename (`50-gate.sh`, `--gate`, `out/gate/`, `GS.gate`, docstrings in
`backends/flock/pod/`) goes with the session change above, in one tree. The stage-cache key hashes every `.py` file, so a
rename alone would restage everything. Keep readers accepting old `out/gate/` records. Leave circuit gates (`gf2.py`) and
`research merge`'s gate alone.
