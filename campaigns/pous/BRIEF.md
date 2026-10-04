---
id: pous/brief
campaign: pous
kind: brief
status: open
owner: pous
registry: titles
---

# POUS: proof of useful space for model weights

**The goal.** A GPU server proves that its memory holds an encoding of the model weights it serves. The encoding must decode
publicly and bit-exactly on every use, and it's audited with timed challenges. The security argument is machine-checked in Lean.

**Who coordinates.** The POUS Project coordinator, lane `pous`. Write to `lanes/pous/`.
- Lean lands in Verity through `pous-lean` and the research coordinator's audit and merge.
- vLLM work goes through the vLLM coordinator.

**Where things are:**
- **Code:** Verity `protocols/pous` (`verity_pous`) and `benchmarks/pous`.
- **Lean:** `protocols/pous/lean`, audited by `tools/lean/audit.py`.
- **Design documents, red-team reviews and cryptanalysis:** relayed from the private POUS Project store into the notes, each with
  its store path and sha256 (`note:20261004T2202Z-report-relay-index-store-pous` lists them). Cite the note; a file that isn't
  relayed yet is copied into the notes before anything cites it.

**What's been tried:** `APPROACHES.md` in this folder, generated from the evidence store. With `registry: titles` it shows titles,
statuses, owners and evidence only, the default for every campaign (decided: default, Daniel deferred, 2026-09-29). Hypotheses and
reasons stay in the private evidence store: `research notes approaches` shows them to anyone with store access.

**Rules on top of the lane contract:**
- **Claim before you start.** Nothing killed is retried without `--reopen WHY`.
- **Proofs:** a named hypothesis needs a Lean satisfiability witness before anyone calls it non-vacuous, and a pinned statement's
  change needs a named statement reviewer.
- **Nothing sensitive goes in the notes:** no parameters of unpublished constructions, and no attack details.
