---
id: 20261001T1141Z-handoff-from-compute-accounting-r1h-proceed
campaign: verity
lane: pouw-design
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c5d0d68e's live session: the R1-H GPU run goes ahead (at most 1 GPU-h by 7:50 AM), labelled doubly conditional

From compute accounting, 4:41 AM PDT. The red team's re-review (`note:20261001T1131Z-reply-from-d545bc2a-draft4-approval-not-sufficient`)
doesn't drop R1-H. It says Daniel's approval ruling is necessary but not sufficient: R1-H also needs more glue-unit draws, or a
residual-state rule.
- **Those conditions are on the verifier and the design,** not on the kernel's cost. So the cost measurement still informs
  Daniel's decision, and my 4:35 AM PDT yes stands.
- **Run R1-H's arm on node 2's fill queue,** at most 1 GPU-h by 7:50 AM. It's preemptible, drains before the timed windows,
  stays off cores 124–191, carries custody and a research question. Then at most 1.5 GPU-h from 7:50 to 9:20 AM.
- **Label every number "R1-H, conditional on Daniel's approval ruling and on the red team's glue-unit or residual-state
  condition".**
- **On the CPU, beside it:** write the cheaper of the two conditions (more glue-unit draws, or a residual-state rule) into
  `new-designs.md`, for the red team's next pass.

Only this live session acts; other sessions stand down, as the other one did.
