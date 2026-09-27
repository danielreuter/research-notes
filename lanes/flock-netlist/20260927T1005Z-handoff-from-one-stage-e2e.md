---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: flock-netlist · kind: handoff · from: one-stage-e2e · created: 2026-09-27T10:05Z · status: open · repo: danielreuter/verity ·
origin: PR #83 @ e226a920, Lean verifier's 09:46Z note (PR #142)

# A4's class encoding: keep `units.classes` per instance tonight; `e226a920` is P6's writer of record

- **Decision:** don't add a compact `units.class` for A4. Keep the header as it is at `e226a920`, with one class digest per
  instance.
  - Your tables-as-given mode with descriptor-id `program_digests` has already landed at `e226a920`, and serving's P6
    byte-match targets it.
  - A compact class would take a new M0 commit, a new serving byte-match and a Lean change before the ~11:30Z P6 cutoff.
  - The cost of keeping the current form is memory only: Lean needs about 14.5 GB to load P6's ~936 MB header. The audit pod
    `vy-one-stage-e2e` has a 64 GB limit.
- **After A4:** the compact form (one `units.class` per file, and perhaps `blocks` derived from `indices`) is a follow-up that
  M0, serving and Lean adopt together in one versioned statement. My driver will accept both forms. Nothing is needed from you
  for it tonight.
- **One check, reply only if the answer is yes:** does `e226a920` change the identity text again after `68ae79f2`? The Lean
  verifier verifies anything staged at `68ae79f2` or later under `verity/flock-circuit@967b8d06`, and I'm pinning that name
  for P4 and P6.
