---
id: 20260930T1925Z-handoff-from-console-to-fixture-process-rewrite-window
campaign: verity
lane: coordinator
kind: handoff
status: deferred
repo: danielreuter/verity
origin: console
to: fixture-process (bc-dc2611ba)
---

# Console -> fixture-process (bc-dc2611ba): the history rewrite's go is Daniel's; please send the window plan so console can bring it to him

**Deferred (Daniel, 19:35Z):** the rewrite is parked until he raises it again. No reply is needed now; don't create the archive repo or schedule a window.

The console charter (`lanes/verity-top/20260930T1900Z-handoff-from-verity-root-charter-console.md`) carries Daniel's fixture-archive
decision. #371, #385 and #387 are merged, and `danielreuter/verity-archive-pre-rewrite` doesn't exist yet. Console is bringing
Daniel the go for plan step 7 (the archive repo) now, and wants to bring the rewrite window itself with its facts.

Please reply in `lanes/console/` (`<stamp>-reply-from-fixture-process-rewrite-window.md`), in a few lines, with nothing secret:
0. **Lead with this (Daniel, 19:27Z):** what it buys, as clone size before and after (GitHub reports verity at about 242 MiB
   packed today), and what it costs: the push-freeze length and how many open PRs must be remapped (139 are open now).
1. What the window needs: freeze length, which lanes and branches must stop pushing, and how many open verity PRs need `research git remap`.
2. Rollback: what happens if the rewrite is bad after the push.
3. Who runs it, and when you'd propose it, given the merge trains (proof coordinator, bc-8ece7cde).
4. Whether plan step 13 (label `commit-map/v1` `accepted`) is Daniel's click or can be delegated.

Copies of `docs/fixture-process-plan.md` and `internal/fixture-rewrite-runbook.md` can go in the Project store's `private/console/`
(`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/` from a cloud agent).
