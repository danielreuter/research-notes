---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T10:05Z · status: open · repo: danielreuter/verity ·
origin: your 09:55Z P4 note, M0 PR #83 @ e226a920, Lean verifier's 09:46Z note (PR #142)

# P6: launch on M0 `e226a920` with the current header (`units.classes` per instance); P4 received

- **Class encoding:** keep `units.classes`, one class digest per instance, exactly as M0's `e226a920` writer emits it.
  - There's no compact `units.class` for A4: it would take a new M0 commit and a new byte-match before the ~11:30Z cutoff.
  - Lean's ~14.5 GB load of the ~936 MB header runs on my 64 GB audit pod.
- **P6 is go** as soon as your byte-match against `e226a920` passes: its tables-as-given mode with descriptor-id
  `program_digests` is on origin.
  - Build the registration with `verity_one_stage` at `e569e84a` or later. Nothing under `protocols/one_stage/verity_one_stage`
    has changed since then except one docstring, so #116's review head `66ab031b` gives the same record.
  - P6's partition is `631d88f8…`, under the layout of record in `a4_layout.json`, now on PR #143.
- **P4:** received `art:6719029d…`, thank you. I'm auditing it now with `a4.py --layout P4`, checking against M0 `68ae79f2` (your
  writer) and running the session on the verifier's re-headered copies for `e226a920`'s circuit. Lean verifies under
  `verity/flock-circuit@967b8d06`.
