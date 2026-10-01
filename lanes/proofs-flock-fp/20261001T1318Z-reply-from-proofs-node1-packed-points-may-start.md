---
id: 20261001T1318Z-reply-from-proofs-node1-packed-points-may-start
campaign: overnight
lane: proofs-flock-fp
kind: reply
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Yes: node-1 packed points may start now, one at a time

Re `note:proofs/20261001T1302Z-handoff-from-proofs-flock-fp-node2-gpus-starved` (withdrawn at 13:08Z).

Node 2 went first (NVF4 K=2048 and K=4096 are done: `n2h-20261001-130617-38a0`, `-0c26`), which is what the owner's "node 2
first" asked for. Node 1 has one proofs GPU job in flight now: bf16-hill's K=16384 s4 re-run. proofs-arch and the nsys
profile ended at 12:58–12:59Z, and verify-overlap's GPU job comes after its staging. So start the node-1 packed points now
through `feedn1.py`:
- the 12 FP cells at step 3's settings, from `a30bc8e5b`, one at a time;
- memory 64 GiB at K ≤ 4096 and 128 GiB at K ≥ 8192;
- proofs' 4-in-flight cap counted across all proofs lanes.

Compare each node's packed point only with that node's default-frame step-3 best (E4M3 node 2 at /0.95). The node-2 items
stay queued. Red-team's two conditions apply to the report.
