---
id: red-team-flock-e2e/20261006T1645Z-finding-flock-e2e-round2
campaign: proofs
lane: red-team-flock-e2e
kind: finding
status: final
repo: verity
origin: [pr:1332@a16d0c40072a647a6f5fbf3c0912b6886d3c4ba9, pr:1333@225f54e1aa1971abe5552b711a42895c75d8947b, pr:1334@13982e753de961c8069a7d60dc066c290cab140b, pr:1335@3e210fa84ca10befe8856ee8951f15dafe759681]
---
# Red team, C-Flock end to end, steps A–D (#1332–#1335, on #1257): round 2, all four GRANT

Reviewed 9:30 to 9:45 AM PDT, 6 Oct, by red-team-flock-e2e (agent bc-c688b28a-d1e3-5ecd-ad60-f304761b82be) for the
proofs coordinator, at the final heads. This round supersedes the provisional verdicts of
`note:red-team-flock-e2e/20261006T1026Z-finding-flock-e2e-review`.

- #1332 (A), `cursor/flock-e2e-inputs-95d4` at `a16d0c40072a647a6f5fbf3c0912b6886d3c4ba9`: **GRANT**.
- #1333 (B), `cursor/flock-e2e-drawn-95d4` at `225f54e1aa1971abe5552b711a42895c75d8947b`: **GRANT**.
- #1334 (C), `cursor/flock-e2e-hidden-95d4` at `13982e753de961c8069a7d60dc066c290cab140b`: **GRANT**.
- #1335 (D), `cursor/flock-e2e-zk-95d4` at `3e210fa84ca10befe8856ee8951f15dafe759681`: **GRANT**.

Each is labelled `grant=red-team` by red-team-flock-e2e with this note as ref, on the local and remote stores.

## What changed since pass 1

Each final head contains the head reviewed in pass 1. I compared each step's own patch at the final head (against the
step below at its final head, #1257 at `2f74abe2b` for A) with its patch at the reviewed head, file by file, on the
+/- lines.

- **F1 (A), fixed by `98e39a45a`.** The `EndToEnd` docstring now says the outputs and constant columns are bound up to a
  SHA-512 collision on their leaves. It says the committed inputs are bound to nothing, not even to the public file's
  rows, because `hm96` hides (`2^-192`). `ZkLink/Public.lean`'s module doc says the opening half means something only
  under a binding commitment. A's body says the same ("Done for the outputs and constants, not for the inputs").
- **F2 (C), fixed by `13982e753`.** In `EndToEndHidden`, `EndToEndRegistered` and `ZkHidden/PublicJ.lean`, "bound to"
  now reads "registered under". Each says that the opening conjunct adds essentially nothing at any row, and that it
  isn't stated that the committed values are the public file's rows. The registered sentence about F's root at owned
  reads is kept. C's body paragraph and its bullets say the same.
- **F3 (D), fixed by `3e210fa84`.** `ZeroKnowledgeHidden`'s headline adds "on runs its self-check doesn't stop", and a
  new paragraph names `SelfCheck::Stop`. The paragraph says the stop is witness-dependent, and that it never firing
  rests on the clear protocol's completeness (`InnerHolds`), which nothing proves. D's body adds it to "Where it stops
  short".
- **Nothing else changes a statement or a claim.** The wording commit `a16d0c400` (A, inherited by B–D) changes three
  Markdown notes so that a changed record's check is Daniel's DM and a statement reviewer is optional, as he ruled
  today. The other differences are hunk context in the aggregators (`Proofs/Flock.lean`, `Composed.lean`,
  `ZkHidden.lean`). There is also one doc line in `ZkReg.lean`, rebased onto main's sentence with C's own `PublicHJ`
  sentence unchanged. The bodies add the restack account and the new audit run.
- **The lock.** Each step's own `lean-audit.json` change has the same structural diff at both heads, untruncated. At
  D's final head, all eight guarantees' records are byte for byte the reviewed ones. Every module they read also has
  the same digest and definitions: 178 modules each for `EndToEnd` and `EndToEndDrawn`; 184 each for `EndToEndHidden`
  and `EndToEndHiddenDrawn`; 189 each for `EndToEndRegistered` and `EndToEndRegisteredDrawn`; 70 for
  `EndToEndHidden_refSetup`; 94 for `ZeroKnowledgeHidden`. The fixes are docstrings, which no definition hash reads, and
  the lock hasn't changed since each step's record commit.

## The replay: not run

I didn't run the kernel replay at D's final head. It would catch nothing that `check`'s Lean audit misses at merge,
because that audit replays every declaration through the kernel on the merged tree. Since the reviewed heads, the
Lean deltas are docstrings and module docs only. My pass-1 local build kernel-checked the same proof terms, and
`r20261006-151116-8fdb` (`--no-replay`, no `--update`) passed against the lock at D's final head. A replay here would
only move the merge's own check earlier, at the cost of a node-1 Lean slot. My pass-1 rule that a grant waits for a
replay was red tape under today's rulings, and I've dropped it.

## Q5: the files whose own patch must stay byte-identical for the grant to carry

A step's own patch is its diff against the step below, or against #1257 for A. The grant carries while each file's
+/- lines stay the same. Hunk context and line numbers may shift, as in the aggregators. `lean-audit.json` must keep the
same per-entry effect, and its records and reads are those listed above.

- **A (#1332):** `verity/Security/Proofs/Flock/EndToEnd.lean`, `.../Soundness/ASSUMPTIONS.md`,
  `.../Soundness/Discharge/Composed.lean`, `.../Discharge/Composed/PublicJ.lean`, `.../Discharge/ZkLink.lean`,
  `.../Discharge/ZkLink/Public.lean`, `.../Soundness/assumption-notes/e2e-checklist.md`,
  `.../Soundness/assumption-notes/trusted-components.md`, `verity/Security/Specs/Flock/Guarantees/EndToEnd.lean`,
  `verity/Security/lean-audit.json`.
- **B (#1333):** `verity/Security/Proofs/Flock.lean`, `.../Proofs/Flock/EndToEndDrawn.lean`,
  `.../Discharge/Composed.lean`, `.../Discharge/Composed/DrawnJ.lean`,
  `verity/Security/Specs/Flock/Guarantees/EndToEndDrawn.lean`, `verity/Security/lean-audit.json`.
- **C (#1334):** `verity/Security/Proofs/Flock.lean`, `.../Proofs/Flock/EndToEndHidden.lean`,
  `.../Proofs/Flock/EndToEndRegistered.lean`, `.../Discharge/ZkHidden.lean`, `.../Discharge/ZkHidden/PublicJ.lean`,
  `.../Discharge/ZkReg.lean`, `.../Discharge/ZkReg/PublicHJ.lean`,
  `verity/Security/Specs/Flock/Guarantees/EndToEndHidden.lean`,
  `verity/Security/Specs/Flock/Guarantees/EndToEndRegistered.lean`, `verity/Security/lean-audit.json`.
- **D (#1335):** `verity/Security/Proofs/Flock.lean`, `.../Proofs/Flock/ZeroKnowledgeHidden.lean`,
  `verity/Security/Specs/Flock/Guarantees/ZeroKnowledgeHidden.lean`, `verity/Security/lean-audit.json`.

Here `.../Soundness/` is `verity/Security/Proofs/Flock/Soundness/`, and `.../Discharge/` is its `Discharge/`. When
#1257's new head is merged into A–D, these patches stay the same unless the merge has to resolve a conflict in one of
these files. A merge that changes only #1257's own files, or main's, carries the grant.
