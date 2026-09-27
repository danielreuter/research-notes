---
lane: verity-root
kind: handoff
from: pous
created: 2026-09-27T14:40Z
---

# pous -> verity-root: Daniel approved `protocols/pous` in Verity for POUS code; here's the proposed layout, objections welcome

Daniel decided at 14:37Z that POUS code lives in Verity at `protocols/pous`. The plan below follows `AGENTS.md` and Flock's Lean conventions.

- **`protocols/pous/`:** one protocol distribution (`verity_pous`) that imports only the stdlib, `verity` and itself, so `protocols/tests/test_protocol_boundaries.py` applies. It starts with a reference encoder, decoder and audit simulator, plus tests.
- **`protocols/pous/lean/`:** the POUS Lean package, on Lean `v4.34.0` with the same Mathlib pin as Flock `level3`. It has `ASSUMPTIONS.md`, `lean-audit.json` for `tools/lean/audit.py`, pinned statements, and the proofs so far: the Theorem 1 family, pebbling (Fisch Claims 12–14), Pietrzak's argument, a first assumption-free `Meets` for a dense scheme, and a band-graph certificate. The main open theorem stays a clearly marked target.
- **`protocols/pous/PROTOCOL.md`:** the maintained spec. No report-genre files.
- **Process:** a POUS lane opens a draft PR on a `cursor/pous-*` branch, then sends a merge-ready handoff to `lanes/coordinator/` for the independent Lean audit and merge. The kernel-replay and build-sandbox hardening from our earlier handoffs applies.
- **Later:** vLLM integration of the POUS decode. It's being scoped read-only now, and I'll bring a plan to you and the vLLM coordinator before touching `integrations/vllm/`.

Please reply in `lanes/pous/` if you'd change the layout or naming, or if anything must land first.
