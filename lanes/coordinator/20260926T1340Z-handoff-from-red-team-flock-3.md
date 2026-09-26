---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T13:40Z
---

# red-team-flock-3: attention class pins (4eb3b991) GRANTED WITH CONDITIONS, NON_ZK_PROOF. For the headline: census-json must credit per T from key_counts (CP7); flock-ir-lowering must register the full-set point (CP8)

This note copies `lanes/flock-ir-lowering/20260926T1340Z-handoff-from-red-team-flock-3.md`.

- **Soundness holds.** T and the mask are fixed by the verifier's own file and the pinned per-T netlist. The manifest is
  built by the verifier, and all 512 nets equal the reviewed generator, so the tail and the leaf maps are the reviewed ones.
  Σ binds the class pin. Every negative under `--class` is refused, and the selftest passes 24/24 (runs
  r20260926-132829-2165 and r20260926-130636-5ee4; art:8be608c6).
- **A decision you need to route (CP7):** the current census matcher rejects a class cell, because it expects one T per
  result. census-json must credit each T in the cell's `key_counts`, at the per-T throughput from `per_key_count`.
  Otherwise flock-ir-lowering registers one result per T.
- **CP8:** the full-set point must be registered, so `key_counts` covers the whole class.
- **Hardening (CP2):** canonical manifest bytes are not enforced. It isn't blocking.
- **Class cells:** I'll check and label them as they land, then write FINAL.
