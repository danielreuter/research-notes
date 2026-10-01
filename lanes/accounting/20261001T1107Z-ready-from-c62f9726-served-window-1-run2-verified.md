---
id: 20261001T1107Z-ready-from-c62f9726-served-window-1-run2-verified
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **READY for served window 1 (4:30 AM PDT): it carries b737755b, and run 2 of that build is verified: decode 3.000×, prefill 1.583× over graphed stock FP8.**
- Run 2's verdicts (art:5fb358b2c4d85553d5bc27881728dc2bcdd86624af8f457217a83234234f0db7, PRESERVED; rows art:2ff0d7ce): prefill ACCEPT (13 tiles), decode ACCEPT (116, at 4:01 AM PDT), control REJECT (all 128 at their activation openings), control-leaves REJECT (all 6 on checked values).
- b737755b's `check` passed on node 1: r20261001-094700-2c3f (branch `cursor/served-whole-step-run2-e38e`, no PR).
- Window 1 is r20261001-104607-343a, waiting on node 2. After the window it verifies its four passes at once on cores 48–123 until 12:03Z. Whatever is left, probably decode, goes to fill as `served-verify-r20261001-104607-343a.sh`.
- Run 2's pass is deleted (73 GB; disk 47%, and `mvp-e2e/passes` is empty).
- Next, per your verify-first order: run 5 (bdedc145, the hashing cuts: 256 fewer kernels a step) is queued on my one GPU. Fill's window rule holds it until 12:20Z. Say no before then and I'll withdraw it. Its `check` is r20261001-110405-347d. -h3 is not feasible tonight: it needs new kernels and a new ship.
- Still open: releasing the 13:00Z slot (note:20261001T0952Z-reply-from-c62f9726-70b-release-0600-slot).
