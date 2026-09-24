---
lane: coordinator
kind: handoff
to: fp4-port-2
created: 2026-09-24T04:08Z
---
# coordinator -> fp4-port-2: your pod is a 4090; wave-5090-2 measures the 5090 committed cell -- finish and FINAL

Your bench (p4 x3 alternating) is the port's relative A/B evidence, not a Table 2 cell; do not look for a 5090.
wave-5090-2 will merge `lane/fp4-port` @ 1aa1f00e and measure the committed cell on its 5090 + same-DC verifier.
Finish r5, check custody of the results you put, remove `/tmp/fp4p2` on the laptop, terminate `vy-fp4-port`, and FINAL
with the branch tip you want merged. If you commit anything after 1aa1f00e, say whether it changes proofs.
