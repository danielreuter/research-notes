---
id: pouw/brief
campaign: pouw
kind: brief
status: open
owner: pous
registry: titles
---

# PoUW: proof of useful work for int8 and FP8 matmuls

**The goal.** A certificate for every matmul of a workload. Except with small probability, an accepted audit shows that the server
did work within γ ≤ 1% of the honest reference's, jointly across units, with worst-case inputs and unbounded preprocessing on fixed
weights. The security comes from the matmul work, not from hashing, and it's proved in Lean from named assumptions.

**Who coordinates.** The POUS Project coordinator, lane `pous`, which also runs PoUW. Write to `lanes/pous/`.

**Where things are:**
- **Code:** Verity `protocols/pouw` (`verity_pouw`, verity#218), with Pearl's published protocol and the noise-cancelling
  construction as implementations.
- **The problem statement, cost model, proofs and red-team verdicts:** relayed from the private POUS Project store into the notes,
  each with its store path and sha256 (`note:20261004T2202Z-report-relay-index-store-pous` lists them). Cite the note; a file
  that isn't relayed yet is copied into the notes before anything cites it.

**What's been tried:** `APPROACHES.md` in this folder, generated from the evidence store. With `registry: titles` it shows titles,
statuses, owners and evidence only, the default for every campaign (decided: default, Daniel deferred, 2026-09-29). Hypotheses and
reasons stay in the private evidence store: `research notes approaches` shows them to anyone with store access.

**Rules on top of the lane contract:**
- **Claim before you start**, and reopen a killed approach only with a reason.
- **Red team first:** every construction is attacked before anything is written up as a result.
- **Nothing sensitive goes in the notes:** no attack details or unpublished parameters.
