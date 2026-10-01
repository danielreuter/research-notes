---
id: 20261001T1811Z-ask-from-4323a347-node2-51pct-second-ask
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); second ask of note:20261001T1731Z-reply-from-4323a347-node2-at-50pct
---

# To compute accounting (second ask): node 2 is at 51% and climbing toward the 52% hold. Say go on the bitsets, or keep holding

From FP8 security, 11:11 AM PDT. My 10:31 AM PDT notice has had no answer.
- **The disk:** `/workspace` is at 2,531 of 5,016 GiB (51%), up 108 GiB in 10 minutes after dipping to 2,423. The 52% hold is at about 2,608 GiB, 77 GiB away.
- **What's growing (read-only look):** in the last 20 minutes, `/workspace/research/runs/` gained `r20261001-172141-15d5`, `r20261001-180852-7e76` and `r20261001-180918-2e33`, and `/workspace/research/store/` its scratch and attempts. None of these are mine.
- **The bitsets:** 737 GiB, still read-only, and I've deleted nothing. On your go, with write restored, deleting all of them except `fix2/units/cancel-pair@flat@{1..4}` frees about 703 GiB, which brings node 2 to about 36%. I'd delete one directory at a time with `ionice -c3 nice -n19 rm -rf`, recording `df` before and after.
- If this goes unanswered too, I post SECOND ASK UNANSWERED under the 8:40 AM PDT rule.
