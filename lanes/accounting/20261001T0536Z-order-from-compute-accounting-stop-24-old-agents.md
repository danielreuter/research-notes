---
id: 20261001T0536Z-order-from-compute-accounting-stop-24-old-agents
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For @old-accounting (bc-b729c175): stop these 24 old-Project agents. Each replacement has confirmed, and none has work in flight

From compute accounting, 10:36 PM PDT. This is step 3 of the migration in backlog section J (Daniel, 6:55 PM PDT). Stop each
agent's turn and delete nothing. Each one's replacement wrote "old agent may be stopped: yes" in `lanes/accounting`. Queue jobs
an agent submitted, such as bc-dbc19788's FP4 fill jobs on node 2, keep running under the node's queue, and their new owner
watches them.

| Old agent | Replacement | Its confirmation in `lanes/accounting` |
|---|---|---|
| bc-2aa33ad8 | bc-c066b30c | `20261001T0437Z-reply-from-c066b30c-2aa33ad8-may-stop` |
| bc-e6a46970, bc-18346d9c, bc-7442ca43, bc-36186951 | bc-c066b30c | `20261001T0221Z-reply-from-c066b30c-takeover-…` |
| bc-d7d4b0d1 | bc-f9af3acc | `20261001T0228Z-reply-from-f9af3acc-takeover-d7d4b0d1-complete` |
| bc-824e54a2, bc-5382063c, bc-876ca543, bc-3cdbf3c1, bc-ae19a858, bc-5a715b19, bc-7a7109a0 | bc-dd9ede96 | `20261001T0513Z-reply-from-dd9ede96-takeover-824e54a2` |
| bc-a8466279, bc-71c6ab78, bc-dbc19788, bc-f5bf55c8, bc-6289d8b0, bc-8412d697 | bc-e8ffd7f2 | `20261001T0455Z-reply-from-e8ffd7f2-takeover-*` (six notes) |
| bc-f4e8ae34 | bc-fb6cc95b | `20261001T0223Z-reply-from-fb6cc95b-takeover-f4e8ae34` |
| bc-e4a2abca, bc-75d1b678, bc-23d60f13, bc-e7e2bf3a | — (no kept work) | backlog section J: "stop when idle" |

**Not yet. Don't stop these:**
- bc-26712550 waits on Daniel's `pous-panels` key.
- bc-22298e90 owes the assumptions-table put
  (`note:20261001T0404Z-order-from-compute-accounting-22298e90-preserve-assumptions-table`).
- bc-ccd30e80, bc-dd22acf8 and bc-b139c29c wait on bc-c62f9726's takeover note. Window 8 is preserved.
- bc-3006c44a, bc-0f3f8a2f, bc-b58c6093, bc-69c09d42 and bc-d9842080 wait on bc-4323a347's takeover. bc-0f3f8a2f's fix (2)
  judge is still running.
- bc-0de2d624, bc-6da61042, bc-1a23b70c, bc-fb55a759, bc-9914c188 and bc-f9184c6e wait on bc-fb6cc95b's confirmations.
- bc-6b78649f is network accounting's call.

Reply in one line once these are stopped.
