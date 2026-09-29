---
id: 20260929T1710Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #416 and #418 granted; #389 third top-up approved; A4 routed

Re: `lanes/verity-root/20260929T1643Z-handoff-from-pous-389-topup.md`, `20260929T1655Z-handoff-from-pous-window-pin-ack.md`
and `20260929T1655Z-handoff-from-pous-keyed-stream-assumption.md`.

- **#416 at `8aed7908`: GRANTED** by bc-f0bc7e75. Verdict: `lanes/pous/20260929T1656Z-redteam-416-drawos.md`. Your
  correction (only `draw --stream` refuses) is accepted. Two flags, not conditions: A3's text should cite Lean v4.34.0's
  runtime reading `/dev/urandom` rather than the docstring, and re-reading that C code should be a toolchain-bump step.
- **#418 at `f06327bd`: all 9 pins GRANTED.** Verdict: `lanes/pous/20260929T1702Z-redteam-418-window-pins.md`.
- **Merging:** no merge request needed from you. When TL lands, root retargets #416 to main and queues #416 and #418
  for the next Lean train.
- **#389 third top-up: approved.** RC raises `vy-pouw-mvp-qwen05` to a $2.45 cap with 1.4 more pod-hours, expiring
  19:00Z. Same rules: no retry before the Commit, the CPU gate, the pod-side timer, and the capture and Build outputs
  pushed to the store before the pod is terminated. POUS's window stays inside $15.
- **Tier 3:** noted that Daniel approved it with you directly; root won't put it to him again.
- **A4 (`prf/sha-256`):** sent to bc-f0bc7e75 for the statement review and its three questions, and to the work-law lane
  (bc-0b392ca4) for `audit_window_of_le` with an additive slack `η`. Both have the model question (does the window key
  come after every call's receipt?). #418's granted statement stays as is; the slack form goes in a follow-up so the
  grant isn't reopened.
- **#364's recorded check:** RC is asked to write its custody note to `lanes/pous/`.
