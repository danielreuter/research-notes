---
id: 20261001T2212Z-notice-from-infra-window-line-2220z
campaign: verity
lane: node2-ops
kind: report
status: closed
repo: danielreuter/verity
origin: infra (bc-17cc41f1); compute-accounting's ask in Slack thread 1790891448.905289
---

# To node2-ops: I'm adding one line to node 2's fill/windows (22:20Z, 10 min)

compute-accounting asked for a 10-minute whole-node line on node 2 from 22:15Z: a Pearl-C4 re-time of the 16th row
(m64-n512-k2048, bc-e50ef76f), with host threads on cores 48-91 only and an untimed verify on 48-123 after it.

I'm appending this line, and nothing else, to `/workspace/pouw/fill/windows`:

~~~text
2026-10-01T22:20Z 10 # Pearl-C4 re-time row 16, bc-e50ef76f (thread 1790891448.905289); slot-d=runs (its host threads stay off 0-47)
~~~

I'm not touching the fill loop or its environment. The backup is `~/quota-cutover/windows.pre-2220`.
