---
id: red-team-plain-leaves/20261006T1058Z-finding-pr1318-regrant
campaign: flock
lane: red-team-plain-leaves
kind: finding
status: final
repo: verity
origin: pr:1318@f74a2905a516e84948d755ec302e1931970bcdd3
---

# red-team-plain-leaves: PR #1318 re-review at `f74a2905a` (GRANT)

## Verdict: GRANT

My verdict on PR #1318 at `f74a2905a516e84948d755ec302e1931970bcdd3` is GRANT. This review follows
`note:red-team-plain-leaves/20261006T0855Z-finding-pr1318-review`, my NO-GRANT at `1b9bdd83c`. The new head is a
fast-forward of that one, and the delta (`4596b8b4d`, `f74a2905a`) implements fix (a), which resolves B1. I found no
blocking issue.

## B1 is resolved

- **The refusal.** `verifyCmd` now refuses any statement with `tags.plainLeaves`, with or without `--zk`, and returns 2
  with "refused: …, a statement with plain SHA-512 leaves (flock-leaf/sha512-unsalted): a form the soundness proof does
  not cover yet".
- **Its placement.** The check comes after the argument checks and before `statementInputs`, so no input is read first.
- **No other path accepts the statement.** `verify` is the only command that returns a verdict on a session. The two other
  commands that resolve a statement, `statement` and `region-words`, return none.
- **What it matches.** `plainLeaves` compares `pinnedLeafScheme` with `leafSchemePlain`, so it also catches any derived
  tags that keep that leaf scheme.
- **What is unchanged.** The other files are as I approved them at `1b9bdd83c`: the tag in `Tags.all` (so `statement`
  still prints digest `59130006…`), `Setup.openedSalts`, `verifyRep`/`shapeOf`, and `verity/Security/lean-audit.json`.
- **No record changes.** No Lean file imports `FlockVerify`, and the verifier package's audit passes in compare mode at
  the head.
- **The docs.** PROTOCOL.md §16.15, the README and the PR body now say the statement is identified but refused until a
  soundness headline covers it.

## Evidence I checked

| Run (vy-nebius-2, source `f74a2905a`) | What it shows |
|---|---|
| `r20261006-092407-7eef` (`art:0b0214ba3c28daa503cea8c3c7fe4f07631c8eb0342e49c1505a69ec57f9cd05`) | `test_lean_plain_leaves.py`: 6 passed, both slow modes included. `audit.py --build` on `backends/flock/verifier/lean`: PASS, 5562 declarations, axioms `propext`, `Classical.choice` and `Quot.sound`, 7 guarantees. |
| `r20261006-100230-6f66` (`art:72985203cfe260a9227abdf77ba218847e90f6a48b15c239f81da1a474e97fdf`) | One `lake build`, then `suites.py flock`: 690 passed, 0 failed, 0 errors. Its record lists all six plain-leaf tests as passed. |

- **Why `r20261006-092407-7eef` exited 1.** Its first suite step had 27 setup errors, from 16 workers building `.lake`
  from cold at once. `r20261006-100230-6f66` built once first and passed.
- **The negative control is behavioral.** In `r20261006-092407-7eef`, with `1b9bdd83c`'s `FlockVerify.lean` (rebuilt by
  the test), 2 of the 6 tests fail. Plain mode reads its inputs and exits 1 with "no such file or directory", and `--zk`
  exits 2 but with the old message.
- **Locally at `f74a2905a`.** The four fast tests pass: `4 passed, 2 deselected`.
- **The ruling the PR cites.** The 2026-10-03 (6:46 PM PDT) ruling exists in `.agents/skills/lean-proofs/SKILL.md`.

I ran no new pod job. The real inner session is on node 1 only, and checking it there would exercise the same refusal
branch the slow test already covers with absent inputs.

## Loose ends (non-blocking)

Both are documentation only. Neither changes behavior or any record:

- `plainLeaves` is read by no guarantee.
- The PR's additions to `Flock/Tags.lean` left `reads['Flock.Tags']` unchanged, so a docstring edit there changes no
  record.

Fixing them changes bytes, though, so the grant would not carry. I would re-grant a delta that touches only these two
comments on a quick read.

### L1. The `Tags.plainLeaves` docstring is stale

The docstring (`Flock/Tags.lean`) still says "so `verify --zk` refuses it". Replace it with:

`/-- A statement whose trees have plain SHA-512 leaves (leafSchemePlain), ZK off: verify refuses it with or without --zk
until a soundness headline covers plain leaves; upstream's --zk refuses it too. -/`

### L2. The script comment names the wrong refusal

In `85-rec-reprice.sh`, line 22 says the inner check is "--coins os, which Lean's tags refuse while they pin hm96
leaves". But line 503 still runs `--statement verity/flock-circuit+plain-leaves`, which `verify`'s proof-coverage check
refuses (exit 2) before reading anything. The restored base comment described the base's command,
`--statement verity/flock-circuit`. My fix (a) text asked for the base's wording, which was imprecise.

Replace lines 22–23 with:

`--coins os, on verity/flock-circuit+plain-leaves, which Lean's verify refuses (exit 2) until a soundness headline covers
plain leaves; ZK_LEAN=1: also today's --zk session; LEVELS=none: neither of V*'s)`

The behavior is already right: the script only echoes `inner lean exit $?` and does not fail on it.

### Carried from the first review

The PR body says test 3 shows that "Lean decodes" the empty `opened_salts`. Test 3 compares source text; it decodes no
proof.

## Label

`grant red-team` on `pr:1318@f74a2905a516e84948d755ec302e1931970bcdd3`, by `red-team-plain-leaves`, with this note as
its ref. `research data labels … --key grant --remote` reports it on both the local and the remote store:

`pr:1318@f74a2905a516e84948d755ec302e1931970bcdd3: 1 on both, 0 local only, 0 remote only` /
`both 2026-10-06T10:59:15Z grant=red-team by red-team-plain-leaves ref note:red-team-plain-leaves/20261006T1058Z-finding-pr1318-regrant`
