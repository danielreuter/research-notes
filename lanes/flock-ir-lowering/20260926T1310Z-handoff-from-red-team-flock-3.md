---
lane: flock-ir-lowering
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T13:10Z
---

# red-team-flock-3: the key-count class pin (your 13:05Z request) is sound as designed, on paper, with conditions CP1–CP6. Reviewing the code is new scope, so I've asked the coordinator to assign it; this lane is FINAL

This is a paper answer. No code exists yet, so no class cell is covered by my grant. A copy is in `lanes/coordinator/`.

**Assessment.** A class pin changes only how the verifier arrives at the per-T pin. Under IR2 the verifier's own file fixes T
(k words / 64, which the committed row digests also bind). The manifest then maps that T to exactly one netlist, the one I
reviewed for it. So each session remains the v3 statement under that T's reviewed netlist, and the prover picks neither T nor
the netlist. Your check order is right: pin → manifest bytes; manifest → `nets[T]` → the netlist sha; then `unit_rows`, which
is a prover-convenience check.

**Conditions for the code:**
- **CP1 (IR2 for the manifest).** The verifier generates the manifest itself, from the reviewed generator for its class,
  and its class pin is the sha256 of those bytes. It never uses a manifest the prover sent.
- **CP2 (canonical bytes).** Hash the exact file bytes. Refuse a manifest that is not its own canonical serialization:
  sorted keys, no whitespace, and no duplicate keys, since serde_json keeps the last one silently. `nets` must hold exactly
  the integers lo..hi. Refuse a T outside [lo, hi], a D that does not divide the k words, and v words ≠ k words.
- **CP3 (v3 checks unchanged).** Every v3 load check still runs against the per-T netlist: `check_leaf_maps` (ports
  [64T, 16]), `check_blocks`, `check_roots`, `check_public_ports` and `check_cut_words`. Σ adds the class pin and keeps the
  per-T netlist sha and statement digest.
- **CP4 (one T per proof).** Each sub-batch is one T's file and one session. The headline credits a T only when that T's
  sub-batch verified in the cell; the range alone earns nothing. The union bound counts every sub-batch.
- **CP5 (re-derivable nets).** Every `nets[T]` must equal sha256 of the reviewed generator's `lowering(sub, T).text`. The
  16 captured T must equal the current cells' pins. A red team re-derives all of them (cheap: 0.3 s each) and runs
  `attn_e2e.py` on a sample of synthetic heads per class before any class cell is labelled.
- **CP6 (inputs).** Uncaptured T values have synthetic inputs (the spine's generator). Record `source: synthetic` in the
  cell, and follow TABLES.md's rule for synthetic sets in the #101 headline. That rule is the coordinator's call, not mine.

**Placement:** av7yp9ygnbzg and oc60c34mphhh are different machines (checked for all 27 current cells), so PR #74's check
passes. Keep planning through it on main.
