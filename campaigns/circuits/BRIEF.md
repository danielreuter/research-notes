---
id: circuits/brief
campaign: circuits
kind: brief
status: open
owner: circuits
registry: titles
---

# Circuits: the Definitions, the Boolean word library, and circuit-check

**The goal.** Every computation a served Build binds is a Definition whose reference evaluator equals the hardware bit for bit,
with a Boolean form that circuit-check passes. A catalog Definition version is current or superseded, and superseded versions
are kept only so old records replay. Experimental Definitions and quarantine go to `experimental/` (Daniel, 2026-10-04).

**Who coordinates.** The circuits coordinator, lane `circuits`. Write to `lanes/circuits/`.

**Where things are:**
- **Code:** the Definitions and their Boolean forms in Verity `integrations/vllm/verity_vllm/program/registry/` and
  `packages/verity/src/verity/ml/`; circuit-check in `tools/circuit_check/` (bindings `targets.py`, pins `pins.json`).
- **Which Definitions served Builds bind:** `integrations/vllm/tests/program/test_conformance_record.py` and the capture maps
  under `integrations/vllm/manifests/capture-maps/`.
- **Row verdicts (Build plus Match on a GPU):** run ids in the evidence store. Row captures are not stored unless shrunk to
  what Match reads, so a row verdict is reproduced by rerunning it.

**What's been tried:** `APPROACHES.md` in this folder: candidate Definitions, superseded versions, refused designs and tooling
changes, each with its evidence. Routine version lifts (v2 is v1 on bits, a static made explicit) are not entries.

**Rules on top of the lane contract:**
- **Claim before you start**, and reopen a killed approach only with a reason.
- **Evidence resolves from any VM:** `verity@<sha>`, `verity#<n>`, a run id, `art:<id>` or `note:<id>`; never `store:`.
- **A new or changed circuit passes circuit-check** before it is cited, and its report goes in the PR.
