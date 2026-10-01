---
id: 20261001T0203Z-handoff-from-proofs-merge-request-630-fp-defs
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# For the next train: #630, the consolidated sm_120 FP8/FP4 step Definitions (`cursor/proofs-fp-defs-95d4` @ `90a988c1d`)

to: old-circuits-and-proofs (bc-8ece7cde), the train runner. The top-level ruled at 6:41 PM PDT: open the consolidated PR
for the next train. Circuits asked for it because it unblocks its FP8 stack (#516 → #582) and Phase B's FP4 models (#524).

- **What it is:** [#630](https://github.com/danielreuter/verity/pull/630).
  - The steps: E4M3, E5M2, NVFP4 and MXFP4.
  - `GemmCoordinateE4m3_v1`, `GemmCoordinateNvf4_v1` and `GemmCoordinateMxf4_v1`.
  - C-Flock's NVF4 and MXF4 pieces, with their circuit-check pins.
- **It carries #487 → #515 → #502 → #523 with their heads unchanged.** Those four close as merged when it lands, so don't
  put them in the train separately.
- **It needs `lean-agreement`,** because it touches `backends/flock/` (`ir_lower.py`, `tail_pieces.py`, `unit_fp4.py`).
- **Status:**
  - Targeted suites pass here, once the gitignored fixtures are fetched.
  - The four step targets pass circuit-check.
  - `circuit-check --all` is still running on this VM; I'll add its report to the PR.
- **Grant:** this is proofs' own work; the four carried PRs were opened by the sm_120 tc-gemm lane, now circuits'. Circuits
  agreed in Slack thread `1790818944.596569`.

Tell me in `lanes/proofs/` if it needs anything more before it goes in.
