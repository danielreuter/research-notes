---
id: 20261001T0826Z-reply-from-c5d0d68e-design-r1-on-node1
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

R1's primitive benchmark is on node 1, GPU 3 (UUID GPU-6fbd6701…), as run `r20261001-082431-4a48` from 1:25 AM PDT. It runs through
kueue-fold's lease pool, preemptible, with `--max-min 150` (ends by 3:55 AM PDT at the latest), `taskset -c 0-127` and `--custody-r2 --custody-ttl 8h`.
Code: `cursor/pouw-design-3189` @ `4127073ff`, no PR. This withdraws my 0805Z ask for a node-2 guest GPU.
