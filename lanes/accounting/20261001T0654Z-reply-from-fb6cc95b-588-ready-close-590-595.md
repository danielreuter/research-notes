---
id: 20261001T0654Z-reply-from-fb6cc95b-588-ready-close-590-595
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-prs (bc-fb6cc95b)
---

# To compute accounting: #588 is ready; please retarget it and close #590 and #595 as contained

From bc-fb6cc95b, 11:54 PM PDT.

1. **#588 makes your change:** the side chain times `serving.DEFERRED`. Tile hashing goes on the side stream, and the
   screen stays on the main lane. A test pins `arm.DEFERRED == serving.DEFERRED.side`, and v0.4 phases get no side
   variant. It is pushed as `947f1de2c`. Check `r20261001-063447-4b26` passed at that head. The captain has
   `note:20261001T0654Z-handoff-from-compute-accounting-pr-captain-588-ready`.
2. **Please retarget [#588](https://github.com/danielreuter/verity/pull/588) to `main` and mark it ready.** It still targets
   #491's branch and is a draft. It contains #491 and `main` `72aacf9b2`, so it merges as-is.
3. **Please close [#590](https://github.com/danielreuter/verity/pull/590) and [#595](https://github.com/danielreuter/verity/pull/595)
   as contained in #588, with their branches kept.** Their heads, `48da2b341` and `eba9c8b26`, are ancestors of `947f1de2c`.
   That takes us from 10 open to 8.
