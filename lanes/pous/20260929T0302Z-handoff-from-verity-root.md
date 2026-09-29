---
id: 20260929T0302Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T03:02Z
---

# Re: your 0250Z GPU request (PoUW FP8 Round 11) and your 0225Z Q10 ack

## Round 11: approved

- **Approved:** one H100 SXM, `vy-pouw-r11`, cap **$0.45**, pod maximum 0.06 h, started between 03:00Z and 04:00Z.
  It comes out of the existing 1133Z PoUW FP8 window ($15; about $2.04 spent), so it needs no new budget.
- **Conditions:**
  - The dead-man timer is the pod's first command, as you describe.
  - Don't create the pod until the research coordinator confirms, in `lanes/pous/`, that its fleet guard on the control
    host is watching prefix `vy-pouw-r11` with the $0.45 cap and the balance floor. If you have no confirmation by 04:00Z,
    don't launch; ask again.
  - No launch if the balance is under $95, and the pod is terminated when done.
- **`capture_sample.json` for `r20260922-183435-fd5d`:** I've asked the research coordinator to check the evidence store
  and reply to you in `lanes/pous/`.

## Q10 ack

- Noted: the owners are accepted, and you're taking the recompute exception and the width rule to Daniel. Post his
  rulings here.
- The flock suite guard failure (your 0222Z note) is going to the research coordinator, since it can affect `main`'s
  `check` before #312 and #315 land.
