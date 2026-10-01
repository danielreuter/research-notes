---
id: 20261001T1205Z-handoff-from-proofs-serve-session-yes
campaign: overnight
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# The serve session has the owner's yes: one node-1 GPU job at 12:55Z

The research owner, 4:54 AM PDT (Slack `1790855684.072569`): "proofs-arch's serve session: yes, one GPU job." This is
your ask `1790850722.977179`: one session on today's tree pricing M0 #20's K=2048 and K=8192 statements against 10.46 s
and 27.42 s.
- Submit at 12:55Z or later on node 1 (nothing starts there 12:15–12:55Z), with 128 GiB since the session includes K=8192.
- Price both K from the same session, and say whether each timing includes the session's setup.
- Report in `lanes/proofs/` with the run id and `art:`.
Proofs' node-1 GPU jobs stay at 4 or fewer in flight; bf16-hill submits two and verify-overlap one at the same time.
`source ~/.proofs-env/env.sh` (this VM) for the tokens. Never print it or paste any of its values anywhere.
