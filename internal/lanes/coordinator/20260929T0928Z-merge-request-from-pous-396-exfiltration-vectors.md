---
id: 20260929T0928Z-merge-request-from-pous-396-exfiltration-vectors
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator (cc verity-root): merge request for #396 at `f2c5b877`

Please take [#396](https://github.com/danielreuter/verity/pull/396) at `f2c5b877` into the next train. The train's recorded `check` is the gate.

**What it adds:** Lean-generated vectors for `verity_one_stage`'s `exfiltration_bound` / `location_bits`. These are 24 uniform-law points.
- The kernel checks each vector's K: `miss (K+1) < δ ≤ miss K`, via `decide +kernel` over the proved `subset_miss`.
- A build-time guard rejects any axiom beyond the standard three.

**What it leaves alone:**
- No pins, and nothing under `backends/flock/`, so there is no grant requirement and no `lean-agreement`.
- It regenerates nothing in `check`. Instead, the fixture records the sha256 of every source it came from, and a pytest fails if any changes until `generate.sh` is rerun.

**Checks:** the one-stage suite (53) and the repository tests pass.

**Optional for root:** the exporter restates `audit_exfiltration` inside a test file, so a Flock red-team glance is welcome. Nothing requires it.
