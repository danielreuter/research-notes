---
id: 20261001T0203Z-handoff-from-bc-22298e90-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: statement red team (bc-22298e90)
---

# Migration handoff from bc-22298e90, the PoUW statement reviewer (red team): nothing in flight; every open review is GO; three follow-ups wait on others

The statement reviewer reads staged Lean pins and rates GO or NO-GO: do the pins say what the lanes claim, do the definitions
match the design docs, do the γ figures recompute. It records statement-reviewer grant labels only when ordered. The verdicts are
in the Project store's `internal/pouw/red-team/` and next to their staging (the notes repo is public, so the reviews stay out of
it).

## 1. Branches and PRs

- **None.** I own no verity branch or PR.
- My only commits are replies in this lane, on the notes repo's `main`, via `research notes sync`.

## 2. Runs and jobs in flight

- **None.** I started no research run and no fill job. My Lean builds were local scratch builds, all finished.
- **One thing to stop: my 30-minute wake timer** (a cursor-subscriptions timer on this agent). I'll remove it when my turn is
  stopped.

## 3. Half-done state, and what was only on my VM

- **My scratch Lean checks are now in the store,** at `internal/pouw/red-team/statement-reviewer-scratch-checks/` (23 files,
  with a `README.md` saying which build tree each runs in and which verdict it backs).
- **The build trees** (`/tmp/rv/*build`) are rebuildable from the store as that README says, so nothing is lost with the VM.
- **Labels I recorded** (evidence store, `grant = statement-reviewer`):
  - rev2 on `art:cc8cf5fe…` (5:51 AM PDT 30 Sep, with the F2 caveat);
  - the combined rev2 + add-on + `SaltDead` delta on M1's `art:c482fce4…` (10:45 AM PDT, which cleared the caveat).

## 4. Each kept item: state, and the next step

These match `20261001T0205Z-reply-from-old-accounting-full-backlog.md`.

- **RowSeed (M3), backlog line 61: GO on all 28** (6:43 PM PDT), after `FragDraw` was restaged as a named `Prop`.
  - Verdict: `red-team/statement-review-m3-rowseed.md`.
  - Next: bc-5382063c's replay audit (line 62) must pass before pinning.
  - The merge handoff must name the statement reviewer.
  - Then Daniel decides `-h3` (line 166).
- **FP4 D-NF pins, line 63: GO** (4:40 PM PDT), with both open points accepted, and the node-2 replay checked (6:43 PM PDT).
  - Verdict: `red-team/statement-review-fp4-dnf-rule.md`.
  - The FP4 γ set (line 48) is therefore unblocked on my side.
  - Next: the assessor's grant of `tt-out/fp4-sm120`, then the merge. A statement-reviewer label goes on the merge snapshot
    only when compute-accounting orders it.
  - The line for `red-team/ratings.md` is at the end of my verdict, for the assessor to append; that file is theirs.
- **v2-hot (M2b), lines 28–34 and 66: parked with fix (2).**
  - What I GO'd: the 11 protocol pins, the 65 compositions and `W_ref ≥ 0` lemma, the row guard, and the charged TT_OUT at
    8,192³ plus its extension, with the width caveat met.
  - The one open condition, the block table rebuilt on the audited floors, is moot unless fix (2) passes.
  - Next, only if fix (2) passes: review bc-b58c6093's t₀ = 0 docstring restage of `NoAlignedExactRegionHot.lean`.
  - Verdicts: `cheap-binding/ttout-lean-staging/v2-hot/statement-review.md`,
    `red-team/statement-review-v2-hot-charged-ttout.md` and `…-extended.md`.
- **FP4 forming ρ_D (an earlier GO, conditional):** condition 3 waits on #534 merging, which is still open.
  - Verdict: `fp4-forming-lean/statement-review.md`.
  - Next: confirm when #534 lands.
- **What I'd stop:** the PoUS red-team queue (line 125: drop). I'd also do no more charged-route v2-hot reviews, since that route
  is dead.

## 5. Traps for my successor

- **The store's FUSE mount returns EAGAIN** on reads and writes. Retry with a sleep.
  - `sed -i` can fail at its rename and leave a temp file in the folder.
  - Append, or use an edit tool, and check that nothing was duplicated.
- **The `research` CLI on a stale checkout** (`/workspace` main at `18783baf`) lacks the `grant` label key and `notes sync`. Use a
  detached worktree at origin/main (`62ce91fa` or later), and check labels with `research data labels <art> --remote`.
- **A notes sync push can lose a race** (`cannot lock ref`). Rerun the sync; it rebases.
- **The audit's `assumptions` field lists only closed `Prop`s.** A named assumption applied to a theorem's variables, like
  rev1's TT_OUT or `FragDraw`, shows only in the signature and under `reads`. Check those, not the field.
- **Build hygiene.** Put scratch `.lean` files at a tree's root, never in `Pouw/`, or the audit flags an orphan. Concrete E4M3
  byte facts need `decide +kernel`; plain `decide` stalls.
- **Ownership.** Never edit another agent's file (`ratings.md`, `coordinator-inbox.md`, any staging README). Write your own and
  cross-link it.
