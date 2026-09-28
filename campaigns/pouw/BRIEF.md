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
- **The problem statement, cost model, proofs and red-team verdicts:** the POUS Project store, which is private. Registry entries
  cite them as `store:pous/<path>`.

**What's been tried:** `APPROACHES.md` in this folder, generated from the evidence store. With `registry: titles` it shows titles,
statuses, owners and evidence only, until Daniel decides how much the public notes may carry.

**Rules on top of the lane contract:**
- **Claim before you start**, and reopen a killed approach only with a reason.
- **Red team first:** every construction is attacked before anything is written up as a result.
- **Nothing sensitive goes in the notes:** no attack details or unpublished parameters.
