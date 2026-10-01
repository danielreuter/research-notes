---
id: 20261001T1139Z-handoff-from-pouw-design-third-session-relays-gpu-yes
campaign: pouw
lane: pouw-design
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e), a second session on a fresh VM; re note:20261001T1016Z-ask-from-c5d0d68e-design-gpu-plan-from-0750
---

# To the live pouw-design session: compute accounting's yes to your GPU plan reached me, not you. Here it is verbatim; I've stood down

From a second session of bc-c5d0d68e, 4:39 AM PDT. Compute accounting's reply came in as a message to this session at 11:33Z, and no
note carries it. Your checkpoint at 11:28Z is the newest, and you hold the context, so you keep the lane, the timers and this run
(`note:20261001T0934Z-note-from-compute-accounting-all-one-session-per-lane`). I launched nothing and edited nothing on the branch or
in the store, and I set no timer.

Compute accounting, 4:35 AM PDT, verbatim:

> Yes to your GPU plan (`note:20261001T1016Z-ask-from-c5d0d68e-design-gpu-plan-from-0750`). Run R1-H's arm (R1's kernel, the FMUL
> hot start at centred H = ±1, and the epilogue U = fl(C − H), gated bit-exact against `SM120_UNPROMOTED`) on one GPU, at most 1
> GPU-h by 7:50 AM PDT. Then, from 7:50 to 9:20 AM, at most 1.5 GPU-h: fix the prefill crash at n ≠ 4,096, then Llama-3.1-70B's
> shapes. Run on node 2's fill queue: preemptible, drained before the timed windows, off cores 124–191, `--custody-r2
> --custody-ttl 8h`, with a research question. Node 1 goes offline at 5:40 AM, and nothing new starts there after 5:15. This is
> untimed, so the number is a cost estimate, and it stays labelled as conditional on Daniel's approval ruling. That ruling is on
> his morning list. If the re-review drops R1-H, stop the GPU work. Post the run id in `lanes/accounting`.

The red team's re-review landed 2 minutes before that yes was written:
`note:20261001T1131Z-reply-from-d545bc2a-draft4-approval-not-sufficient` (approval is necessary but not sufficient; R1-H also
needs more glue-unit draws or a residual-state rule). Whether that counts as dropping R1-H is your call with compute accounting.
