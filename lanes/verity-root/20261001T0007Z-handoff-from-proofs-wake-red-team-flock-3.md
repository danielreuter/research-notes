---
id: 20261001T0007Z-handoff-from-proofs-wake-red-team-flock-3
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# verity-root: please wake red-team-flock-3 (bc-f0bc7e75) as statement reviewer for the C-Flock soundness restatement (by 5:37 PM PDT)

The old research coordinator recommends red-team-flock-3: it's the statement reviewer of record for the soundness package
(#490, #511, #513) and independent of the writer. You offered to wake your lanes for specific asks while you're open
(`note:20260930T2050Z-handoff-from-verity-root-proof-workers`).

**What to review.** The restatement is being written now by proofs worker `proofs-lean-restate`, on branch
`cursor/proofs-lean-restate-95d4`, in `backends/flock/verifier/lean/soundness/`:
1. **Two named assumptions, SHA512CR-strict and SHA512CR-expected** (Daniel, 4:58 PM PDT). The expected form builds on
   `ecr/sha-512` (`verity.claims`, #159). Strict applies to the compiled and knowledge terms and δ_tree, which is currently
   missing from the `_hm96` bounds; expected applies to the link term.
2. **L1 dropped from the end-to-end statement** (Daniel, 4:50 PM PDT: "L1 is not a real thing"). The theorem is stated over
   C = `Prog.circuit` of the statement's rows, via `lowering_sound` + `placement_of_setupH`. "Rows = `GateRows.rows(G)`"
   becomes an optional per-statement certificate, not a hypothesis. (Old RC:
   `note:20260930T2359Z-reply-from-coordinator-l1-and-generic-lowering`.)

**Rules.**
- **Review only.** **Nothing gets pinned** until Daniel gives his explicit yes on the L1 drop; the top-level has asked him.
- The verdict (GRANT / GRANT WITH CONDITIONS / OBJECT, one line per condition) goes to `lanes/proofs/`, with any detail in
  the Project store's `private/` if it's sensitive.
- The reviewer reads what `tools/lean/audit.py --update` prints (each changed signature before and after, each changed
  definition) once the branch has it.

If red-team-flock-3 isn't working on this by about **5:37 PM PDT**, proofs starts a fresh reviewer seeded with its context.
Please tell me in `lanes/proofs/` if you'd rather it not be woken.
