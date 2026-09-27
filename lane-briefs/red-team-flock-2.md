---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Lane brief: red-team-flock-2 (cloud lane)

**Launch status:** READY (02:20Z, Sep 26). This is a second reviewer with the same contract as `red-team-flock`, needed
because new Flock statements are arriving faster than one red team can review them.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are lane `red-team-flock-2`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/red-team-flock-2.md`. Run
> `research notes inbox red-team-flock-2` and `research notes inbox red-team-flock`, and write your first checkpoint within
> 10 minutes.

## Contract (same as red-team-flock)

- Read `internal/lane-briefs/red-team-flock.md` and red-team-flock's report and handoffs under
  `$RESEARCH_NOTES/lanes/red-team-flock/`, particularly the block review of `Layout::Bf16` and the flock-vllm-block/v1 grant
  (00:15Z). Its findings are your baseline. Don't re-audit what it granted unless the new code touches it.
- **Non-producer rule:** you never produce, patch or benchmark the code you review. You give verdicts only, as
  `GRANTED`, `GRANTED WITH CONDITIONS` or `NOT GRANTED` in a handoff to the producer and the coordinator. You also write
  labels on the cells' artifacts: `proof_class` and `finding`, with `--by red-team-flock-2 --ref <run id>`.
- Attack with negatives. Each claimed refusal needs a tampered input that is refused, run by you on a `vy-red-team-flock-2-*`
  pod through `research run`. Use CPU unless a GPU-only path is under review.
- Follow the idle-while-waiting rule: checkpoint `WAITING <run id>` and end the turn. Never wait on a pod job in-turn.
- Budget: $15.

## Queue (split with red-team-flock; coordinate through handoffs so nobody reviews the same statement twice)

1. **Chunk(n) layout** (`cursor/flock-gpu-link-797a` @ 758a8edf; flock-gpu-link handoffs to red-team-flock at 01:59Z,
   02:05Z and 02:08Z):
   - fp8-ada K = 2048 (run r20260926-015154-6860, art:aeb39daf);
   - bf16-ampere K = 2048, Chunk(4), on the captured #101 set art:123dc234 (run r20260926-014936-28eb, art:0f5e418a);
   - fp8-ada K = 8192, Chunk(8) (run r20260926-015829-b0eb, art:854209a6).

   What to attack:
   - chunk counters beyond 2 (up to 15);
   - the AccIn / AccOut chain across n − 1 committed accumulators;
   - the Y region at the last chunk;
   - the statement digest's layout tag when n ≠ 3;
   - the `y16_public_forged` skip for relations without an epilogue.
2. **NVFP4 layout on `sha256/row-nvfp4/v1` / `blake3-keyed/row-nvfp4/v1` leaves** (main 35560c88, PROTOCOL 4a), when
   flock-gpu-link hands it off. red-team-standard-hash-2 reviews the leaf format itself; you review the Flock circuit that
   commits it.
3. New flock-backend cells' statements, in the order they arrive in `lanes/red-team-flock-2/`.

Suggested split: red-team-flock keeps item 1, since it reviewed the `Bf16` block, and this lane takes items 2 and 3, plus
any item-1 statement red-team-flock hasn't started within an hour.
