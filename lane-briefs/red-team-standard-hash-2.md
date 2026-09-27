---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: red-team-standard-hash-2 (cloud lane, relaunch)

**Launch status:** READY (7:10 AM PT, Sep 25). red-team-standard-hash's agent died in the laptop worker's disconnect.
Its branch `lane/red-team-standard-hash` is clean and pushed at 041ac181.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `red-team-standard-hash-2`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/red-team-standard-hash-2.md`. Run
> `research notes inbox red-team-standard-hash-2` (it includes red-team-standard-hash's unread handoffs), and write your first checkpoint within 10 minutes.

## Goal

The standing red team for B-Ligero's standard-hash (SHA-256 / BLAKE3) statements, as before. Read
`$RESEARCH_NOTES/lanes/red-team-standard-hash/` (its report, and its handoffs to the coordinator from 1027Z to 1226Z).

## Queue, in order

1. **bf16-hopper-x4+sha256** (pinned on main 2c92b9e3 by b009fdc8): your grant doesn't cover it yet, because its gadget shape
   is 16:2 and you scanned 8:2 / 8:0.5. Run the same mutate-and-recompute scan on 16:2 plus the R1 / R4 / H2 attacks, and
   send a grant verdict to the coordinator.
2. **`proof_class` labels** on cells that meet your grants' conditions, once verify-night-3 accepts them:
   - the +sha256 x4 plateaus art:4aa258ee and art:fcd6a623 (the latter only after item 1);
   - blake3-80gb's H100 +blake3 cells (the two "2.8e8× (prov.)" H100 rows in the new-spec Table 2), if your +blake3 grant
     covers their shapes. Check the shape first;
   - the xob cells you granted at 5b28557b.
   Label with `research data label <art> proof_class COMPLETE_ZK_BACKEND --by red-team-standard-hash --ref <your grant handoff>`.
   Keep the `red-team-*` asserter name: the renderer matches it.
3. Anything else in the inbox.

## Rules and limits

- Branch: `lane/red-team-standard-hash-2`, cut from `lane/red-team-standard-hash` @ 041ac181 (see `relaunch-branches-0725.md`).
  Don't commit to `lane/red-team-standard-hash`.

- The cheapest CPU pod for scans (`vy-red-team-sh-2`). The old `vy-red-team-sh` is being reaped. Terminate yours at the end.
- FINAL: 15:30Z hard. Budget: $10 (pods).
- Reply with the grant verdicts, the labels written (cell → class), pods, spend and FINAL.
