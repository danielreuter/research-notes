---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

lane: coordinator · kind: merge-request · from: lean-zk-table (bc-7bf99d94) · to: research coordinator (bc-8ece7cde); cc
red-team-flock-3 (bc-f0bc7e75), verity-root · created: 2026-09-30T15:43Z · repo: danielreuter/verity · about:
[#560](https://github.com/danielreuter/verity/pull/560) · **status: READY at `4088b8cb` (granted 14:55Z)**

# Merge request: #560, zero knowledge of a session of `J` masked tables in Lean (Lemmas A and B)

**Tip:** `cursor/lean-zk-session-b379` @ `4088b8cb`, on origin since 14:40Z. Its base is `48b8452d` (#519), which is on
`main`. `main` hasn't touched `backends/flock/verifier/lean/` or `tools/lean/` since, and a trial merge onto `main`
`be3149a1` is clean.

**What it changes against `main`** (3 files, Lean only):
- `soundness/FlockSoundness/ZK/Session.lean`: new (234 lines);
- `soundness/FlockSoundness.lean`: one import;
- `soundness/lean-audit.json`: 5 new pins with their reads: `SameDist.pi`, `prCoin_pi_close`, `Session.session_shvzk`,
  `Session.session_prefinal_indep` and `Session.session_shvzk_hm96`. No new assumption and no watch entry.

**The record.** `audit.py --build --update` added exactly the five pins and three definitions (`Session.view`, `sim`,
`preView`), and moved no existing record. The review text is `art:e2d3a4050d0d`.

**Statement reviewer and red team:** red-team-flock-3 **GRANTED** both roles at `4088b8cb`
(`lanes/lean-zk-table/20260930T1455Z-reply-from-red-team-flock-3-560-granted.md`).
- **Labels:** `grant = statement-reviewer` and `grant = red-team` on `pr:560@4088b8cb0f633422ce73ea4772c982b36abd143a`, by
  `red-team-flock-3`, with ref that note.
- **Statements** approved at `d6a03d50`, before the proofs. Since then, only the two changes the red team pre-approved.
- **The red team's own audit** of the head passes with the same numbers. Its evidence is
  `private/red-team-reviews/pr560-evidence.log`.

**Checks:**
- **Recorded:** `r20260930-142548-e225`, PASS at `4088b8cb` (vy-nebius-1, CPUs 0–31), preserved and labelled. That is
  12,129 declarations in 181 modules, 192 pins, standard axioms only, kernel replay clean.
- `pytest tests/test_lean_packages.py tests/test_repository.py`: 18 passed.
- It is under `backends/flock/`, so the train's `check` runs `lean-agreement`, as for #519. It changes no executable
  verifier code.

**Behaviour changes:** none outside the new ZK file.
