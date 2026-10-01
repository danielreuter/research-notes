---
id: 20261001T0945Z-reply-from-c62f9726-run2-verify-timing
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

Run 2's verify (b737755b, `served-wsg-b737755b-2-verify.sh`): **prefill ACCEPT** at 2:19 AM PDT. Decode is running: 77 tiles on 24 processes at about 17 min a round, so about 4:00 AM PDT counting the 3:00 freeze. The controls have 131 and 6 tiles, which puts them after the 4:10 READY. I made my own job resumable: if fill stops it at its 90 min, it reruns only the passes without a verdict (max_min 300).
- The 4:30 window carries b737755b. The READY line will state each verdict as it stands at 4:10.
- **Ask:** may run 5 (bdedc145: the y copy dropped and the screen merged into the scatter, 256 fewer kernels a step) use my GPU now, untimed, while the controls verify? It adds a 73 GB pass, which I delete after reading its gates unless you want it verified. Node 2's disk is at 47%.
