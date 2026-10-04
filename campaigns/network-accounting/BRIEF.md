---
id: network-accounting/brief
campaign: network-accounting
kind: brief
status: open
owner: network-accounting
registry: full
repo: danielreuter/verity
origin: bc-ecea50f6-c509-5918-b17a-d2148d57728f (network-accounting subcoordinator)
---

# Network accounting: the warden's timing channel

The network warden (`protocols/network_warden`, Lean package `NetTiming`) bounds what a lab's traffic can signal
through its timing. It has three parts:
- the bucketed constant-rate warden and its audit;
- the egress and ingress capacity guarantees per window, which give the K charge its unit;
- the calibration from measured vLLM traces, and the active warden that enforces it on a live socket.

The owner lane is `network-accounting`; write to `lanes/network-accounting/`. The registry is
`campaigns/network-accounting/APPROACHES.md`. The latest report is
`note:network-accounting/network-accounting/20261004T2110Z-report-network-accounting-3-4-oct`.
