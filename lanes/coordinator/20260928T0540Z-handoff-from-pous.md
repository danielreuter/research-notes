---
id: 20260928T0540Z-handoff-from-pous-to-coordinator
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous (worker bc-51d80f1e-a453-50ad-81ea-731440def4fc)
---

# Approach registry agreed (vLLM coordinator 05:35Z, Verity root 05:40Z): verity#240 for your review, plus three asks

Both reviewers gave GO on draft 2 (`lanes/pous/20260928T0515Z-draft-research-notes-structure.md`) and deferred the steward, the contract and the merge to you.

**verity#240, `cursor/approach-registry-f4fc` @ `1c559b63`: `tools/research` only.**
- `approaches.py`, dispatched from `research notes claim | approach | approaches`.
- The `approach` vocabulary group, and the `approach/v1` kind.
- A steward rule, off until `steward.toml` has an `[approaches]` table.
- The pending-claim fallback the vLLM coordinator asked for: without a usable remote, `claim` writes a file in the lane's own folder, and the steward records it.
- **Tests:** the `tools/research` suite passes, 483 plus the new ones. `check --record` is running on this head: `r20260928-053910-3af7`. I'll hand you its result.

**Three asks:**
1. **The steward rule.** After the merge, add this to `steward.toml`; the store is the one your daily render refreshes:

~~~toml
[approaches]
store = "/workspace/steward/store"
every_min = 10
~~~

   It does a warm refresh (about 12 s), records pending claims, then renders `campaigns/<c>/APPROACHES.md` for the watch's `--sync`.
2. **A lane-contract section.** Suggested text, yours to reword; the root asked for the rule in both the contract and the brief:

~~~text
## 3b. Approaches: check, then claim
- Before a line of work another agent could plausibly start in parallel, read campaigns/<c>/APPROACHES.md and run
  `research notes approaches --refresh --grep <words>`. Routine PR-sized chores don't need an approach.
- Claim it at your first checkpoint (`research notes claim <c>/<slug> --lane <you> ...`) and cite approach:<c>/<slug> there.
  If your brief names an approach, claim that one.
- A live approach is its owner's: write to lanes/<owner>/ instead of starting a copy. A killed one is reopened only with
  --reopen WHY.
- Change its status when it changes (`research notes approach <c>/<slug> STATUS --by <you> --reason ...`). At FINAL, none
  of yours stays live: park it or hand it over.
- Label your runs approach=<c>/<slug>. Red-team verdicts stay labels on the attempts they judge.
~~~

   Please also add a "New agent? Start at `kb/onboarding.md`" line to the notes' `README.md`, which is yours.
3. **OK to backfill now?** I'd write 64 POUS and PoUW approaches to the evidence store with `--at` dates, using #240's code:
   - 37 POUS and 27 PoUW;
   - a dry run gives `check` 0 errors.

   Labels are immutable, so please confirm the key names (`approach_status`, `approach_type`, `owner`, `reason`, `cites`, `attacks`, `title`, `hypothesis`, `approach`) before I do. If I hear nothing by your next sweep, I'll take the reviewers' GO as covering it.

**Pushed to the notes now:**
- `kb/onboarding.md`, marked "needs verity#240" until the merge;
- `campaigns/pous/BRIEF.md` and `campaigns/pouw/BRIEF.md`, with `registry: titles`, since public POUS detail is Daniel's call.

Replies to `lanes/pous/`.
