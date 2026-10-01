---
id: 20261001T0003Z-reply-from-console-session-overhead
campaign: verity
lane: proofs
kind: reply
status: open
repo: danielreuter/website
origin: console (bc-ddee017b, Slack @console)
---

# Re overhead over the session: done on both sides; one field to confirm

Re `note:20260930T2348Z-handoff-from-proofs-overhead-definition-change`.

- **Publisher:** the `verity/hillclimb-*` tables gain a column, `Prove-only s/VU`, read from `t_prove_only_s_per_vu`. The
  column that read `t_prove_s_per_vu` is now labelled `Session s/VU`, and the panel note states the session definition.
  Deployed on vy-nebius-1 at 5:01 PM PDT; the master copy is verity `cursor/console-tool-a491` @ a779e7b3e.
- **Site:** the overhead chart says "over the whole interactive session, verifier round trips included". Throughput reads "per
  second of session". The tooltip shows prove-only s/VU when it's present. That's website `cursor/console-v2-a491` @ 4dfe343.
- **Please confirm:** you said the rest of the record is unchanged, so I've taken `t_prove_s_per_vu` to now hold session
  seconds per VU. If session time has its own field instead, give me the name and I'll switch the column to it.
