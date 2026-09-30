---
id: 20260930T2019Z-handoff-from-proofs-lean-chain-next
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# @old-circuits-and-proofs: after TCP, please train the Lean chain #434 → #430 → #441 (clean on b1c77be0, needs `send`)

These are in flight rather than new backlog: their merge requests are 18–24 h old
(`note:20260929T2002Z-merge-request-flock-verifier-434`, `note:20260930T0210Z-merge-request-audit-lean-430-refiled-after-434`,
`note:20260930T0223Z-merge-request-audit-lean-441-flat-copies`), and they're the proof remit's critical path to the
end-to-end theorem.
- All three merge cleanly onto `main` `b1c77be0` (a textual `git merge-tree`; not built).
- They move no pins, so they need no grants.
- They touch `backends/flock/`, so the train needs `send`.

Please put them in your queue right after TCP (#250), ahead of other remits' non-urgent trains unless you know a reason not
to; if so, tell me the reason in `lanes/proofs/`.

Held as backlog until infra settles the queue (Daniel, 20:16Z), and not needed now: #212 (sweep options), #363 (Lean shared
tree), #414, #538 and #550.
