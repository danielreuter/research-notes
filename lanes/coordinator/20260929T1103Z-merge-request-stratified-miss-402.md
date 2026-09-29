---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T11:03Z · repo: danielreuter/verity

# Merge request: #402, the stratified count curve (`stratified_miss_eq_greedy`), at `38d9be9a`

[#402](https://github.com/danielreuter/verity/pull/402), branch `cursor/stratified-miss-greedy-30a8`, head `38d9be9a`. Please
merge exactly this head; it has not moved since the grant. The PR is still marked draft.

**What it adds.** `soundness/FlockSoundness/Audit/StratifiedMiss.lean` and one pin, `Law.stratified_miss_eq_greedy`.
- A count vector `a` that some `τ ∈ (0, 1]` separates attains the stratified law's `miss` at `∑ a`, which is
  `∏ s C(n_s − a_s, k_s)/C(n_s, k_s)`. Separated means every factor `a` takes is at least `τ`, and every factor it leaves is
  at most `τ`.
- It discharges `audit_exfiltration`'s `hk : miss (K + 1) < δ` for stratified laws such as A4's floored ones.
- It touches only the soundness package: the new module, `FlockSoundness.lean`, `Check.lean`, `Audit/README.md` and
  `lean-audit.json`.

**Review.** bc-f0bc7e75 granted it at `38d9be9a` (`internal/lanes/red-team-flock-3/20260929T1040Z-answer-from-red-team-flock-3-402-verdict.md`):
- the record is `art:606e3c232cf8c905a5436bb682b103eb1cdd797107b39136d28370859a614049`, labelled `verified=accepted`;
- the findings are `art:a24132ad214e30f84ac05e0c021bf9e91b2c5f97c71dab69a5066c706f0b596b`;
- `main`'s 51 records are unchanged, and the only new reads are `stratumEscape` and `stratumRatio`;
- N1 (non-blocking) is for #396's exporter, not this PR: certify the separation for an exported τ exactly, in rationals.
  [#406](https://github.com/danielreuter/verity/pull/406) does that, stacked on #396 with #402 merged in. It is a draft,
  not part of this request.

**Trial merge on today's `main`** (`d7a58582`, T11), not pushed.
- It merges with no conflicts and builds in 4,206 jobs.
- The soundness audit passes against the merged records without re-recording: 8,082 declarations, 117 modules, 52 pins,
  standard axioms. These are the red team's counts at `ad349a3b`.
- So #402 needs no re-record on the current `main`.

**Interaction with other trains.**
- It conflicts with #392 (request `20260929T1104Z-merge-request-influence-witnesses-392.md`) in the soundness
  `lean-audit.json` only.
- It will conflict the same way with T12 (#374 → #390), which also adds soundness pins.
- The conflict is mechanical: the union of the pins, and each `reads` module's pins and definition hashes, followed by
  `audit.py --update --no-replay` on the built tree. #392's request has it worked through, with the check that no pin record
  changes.

**Checks.** `check` needs `lean-agreement`, since the PR touches `backends/flock/`. The train's recorded check is its gate.
I have no pods and made no spend.
