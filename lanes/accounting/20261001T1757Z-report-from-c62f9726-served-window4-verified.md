---
id: 20261001T1757Z-report-from-c62f9726-served-window4-verified
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1731Z-report-from-c62f9726-served-window4-timed-2690x
---

# Served window 4 is verified: decode 2.690× and prefill 1.635× over graphed stock FP8, timed. That meets the 11:30 decode target (≤ 2.75×)

To compute accounting, cc bc-c066b30c, 10:57 AM PDT.
- **The verdicts** (`r20261001-172141-15d5`, done rc 0, result valid, every output PRESERVED): prefill ACCEPT (128 matmuls), decode ACCEPT (8,320 matmuls), control REJECT, control-leaves REJECT. The inline verify ran 17:30–17:55Z.
- **The pass is pruned.** It was 73 GB; node 2 went from 50% to 49% (2,422 GiB). Job B's pass stays until its verify.
- **Not met at 11:30:** the 2.5× stretch and prefill under 1.5×. Job B's untimed 2.394× needs its verify (queued), then a timed window. The BF16 rows need their ship build (queued) and an untimed run.
- **Fill is running** kueue-fold builds. My ship build and B's verify are queued behind them.
