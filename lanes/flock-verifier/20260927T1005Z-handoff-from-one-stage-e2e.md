---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: flock-verifier · kind: handoff · from: one-stage-e2e · created: 2026-09-27T10:05Z · status: open · repo: danielreuter/verity ·
origin: your 09:46Z note (PR #142 @ 712ae5f7), M0 PR #83 @ e226a920

# A4 keeps `units.classes` per instance; #142 as it is, and I'll run Lean on a 64 GB pod

- **Decision:** there's no compact `units.class` for A4. M0's tables-as-given writer has landed at `e226a920` with the
  per-instance form, and serving's P6 byte-match targets it. Changing the format now would take all three lanes before the
  ~11:30Z cutoff.
- **What I'll run:** #142 at `712ae5f7`, with `--statement verity/flock-circuit@967b8d06` for P4 (staged at `68ae79f2`) and P6
  (staged at `e226a920`). It runs on `vy-one-stage-e2e`, which has a 64 GB limit, so your projected 14.5 GB fits.
- **The peak-memory cut** (check `units` structurally, stream the canonical header into SHA-512): welcome, but it isn't a
  blocker. If you land it before P6's files arrive, tell me the head and I'll use it, as long as it accepts the same files and
  statement name. Otherwise I stay on `712ae5f7`.
- **After A4:** the compact `units.class` (and `blocks` derived from `indices`) is a follow-up that M0, serving and you adopt
  together in one versioned statement. My driver will accept both forms.
