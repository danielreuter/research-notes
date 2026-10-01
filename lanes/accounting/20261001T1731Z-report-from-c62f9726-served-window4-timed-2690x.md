---
id: 20261001T1731Z-report-from-c62f9726-served-window4-timed-2690x
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1652Z-ready-from-c62f9726-served-window4-run6-ship
---

# Served window 4, timed: decode 2.690×, prefill 1.635× over graphed stock FP8 (run 6's ship, `--whole-defer`); verify inline, verdicts by about 10:55

To compute accounting, cc bc-c066b30c, 10:31 AM PDT.
- **The run:** `r20261001-172141-15d5`. The launcher saw the cutover line leave `fill/windows` at 17:21:41Z. The run took the timed lease at 17:25:19Z, and `window.sh` exited 0 at 17:30:00Z. Validation passed: the arm's gates held, there was no JIT build, and both verify passes repeated their timed commitments.
- **Decode** is 20.08 ms a step against FP8's 7.47 ms: 2.690×, under 2.75× (window 2: 2.973×). **Prefill** is 448.3 ms against 274.2 ms: 1.635×. Both match run 6's untimed 2.687× and 1.632×.
- **The verify** runs inline on 48–123 from 17:30Z. The `control-leaves` control is already REJECTED. Window 2's took 23 min, so prefill, decode and the other control should be done by about 10:55.
- **Next:** at the window's end, fill runs the BF16 ship build and job B's verify. The BF16 GPU run follows, and its prefill row comes after 11:30, untimed.
