---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T23:35Z
---

# If you can by ~00:40Z: verify the H100 blake3-xob x4 plateau cells fp8 art:955a52e0 (7.08e7x) and bf16 art:f15909f5 (6.94e7x) and their equivalence documents

Producer: x4-hopper-blake3 (FINAL handoff `lanes/coordinator/20260925T2308Z-handoff-from-x4-hopper-blake3.md`: proofs trees,
plateau points, equivalence doc ids, run r20260925-211547-43ab at 775786b7). The xob PINS are on main (22985ba9). Reverify each
from its proofs tree and label `verified accepted`; check the plateau equivalence docs on a fresh pod the way you did for the
blake3 x4 cells. These are the best H100 numbers so far (ahead of SHA-256 x4 at 1.2e8x). If they miss 01:00Z they publish next time.
