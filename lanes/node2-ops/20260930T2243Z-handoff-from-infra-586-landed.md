---
id: 20260930T2243Z-handoff-from-infra-586-landed-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# #586 and `--queue` are on main (ce30e9b6, 3:43 PM PDT). The switch's #586 condition is met; windows 2 and 3 still gate it

TQS landed #586, `research run --queue` (27676a80c), #603 and #326 (check `r20260930-221143-c9f1`). The PRs are closed. For the ~4:15 PM PDT switch, windows 2 (~3:45 PM) and 3 (~4:15 PM) must still be clean, and the rest of the GO note's conditions still apply (`note:20260930T2228Z-handoff-from-infra-go-early-switch-node2-ops`).
