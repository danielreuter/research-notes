---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T11:04Z · repo: danielreuter/verity

# Merge request: #392, the satisfiability witnesses for `twoStage_influence` and `audit_exfiltration`, at `8628dd4a`

[#392](https://github.com/danielreuter/verity/pull/392), branch `cursor/influence-witness-two-stage-exfil-30a8`, head
`8628dd4a`. Please merge exactly this head; it has not moved since the grant. The PR is still marked draft.

**What it adds.** Three pins in `soundness/FlockSoundness/Audit/InfluenceWitness.lean`, the statement reviewer's 19i witnesses
(bc-89770364, X-IR-4):
- `Two.influence` and `Two.accepts`: every hypothesis of `twoStage_influence`, `AnchorsSound₂` among them, holds on a
  two-stage audit that accepts;
- `Ex.exfil`: `audit_exfiltration`'s eight hypotheses hold together, for a one-bit message.

It touches only the soundness package: that module, `Check.lean`, `Audit/README.md` and `lean-audit.json`.

**Review.** bc-f0bc7e75 granted it at `8628dd4a` (`internal/lanes/red-team-flock-3/20260929T1046Z-answer-from-red-team-flock-3-392-verdict.md`):
- the record is `art:966f1932330fb89260c48a97ae0f44c639fbab0a23bcbfe458507aaa2e2e7f59`, labelled `verified=accepted`;
- the findings are `art:ad414d815e3b29cd91d79b210e6fde05882908e469b012d02029ba8965abb697`;
- #381's 38 records are unchanged, and the only new reads are the witnesses' own definitions.

**It doesn't merge cleanly: the soundness `lean-audit.json` conflicts, and nothing else does.**
- #392 branched from `d237e60a`, before T7 landed #362's 13 work-law pins. Against today's `main` the two sides add
  different pins: #392 adds 3 and `main` has 13 that #392 lacks. Both also update the `reads` entries of four modules,
  `Audit.Law`, `Audit.OneStage`, `Game.Basic` and `Game.Prob`.
- #402 (request `20260929T1103Z-merge-request-stratified-miss-402.md`) conflicts with it the same way, and so will T12
  (#374 → #390).
- No pin is touched by both sides, so the resolution needs no new review.

**Trial resolution on today's `main`** (`d7a58582`, T11) with #402 merged first, not pushed:
1. Merge `38d9be9a`. It is clean.
2. Merge `8628dd4a`, and resolve `lean-audit.json` as follows:
   - take the union of the pins;
   - for each `reads` module, take the union of its pins and, for each definition, the hash from the side that changed it;
   - `lake build` the soundness package, then run `audit.py backends/flock/verifier/lean/soundness --update --no-replay`,
     which rewrites the digests from the build.
3. Check the result:
   - all 55 pin records equal their own side's byte for byte (52 from `main` + #402, 3 from #392);
   - all 75 `reads` entries equal the three-way merge;
   - `roots`, `assumptions`, `meaning`, `upstream` and `dependencies` equal `main`'s.
4. The plain `audit.py` with kernel replay then passes: 8,107 declarations, 117 modules, 55 pins, standard axioms.

   The resolved file's sha256 begins `5f84e679`; any other base gives other bytes by the same steps.

**Checks.** `check` needs `lean-agreement`, since the PR touches `backends/flock/`. The train's recorded check is its gate.
I have no pods and made no spend.

**Update, 11:24Z: `main` moved to `c90669f3` (T10c, with #374).** I repeated the trial there with the same steps:
- `main` + #402: 61 pins;
- + #392: 64 pins;
- every pin record equals its own side's, and the audit passes with 8,134 declarations.

The sha256 above belongs to the `d7a58582` trial. #406's request (`20260929T1124Z-merge-request-exfiltration-stratified-vectors-406.md`)
has the T14 trial.
