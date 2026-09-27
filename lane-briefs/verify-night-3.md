---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: verify-night-3 (cloud lane, relaunch of verify-night-2)

**Launch status:** READY (7:10 AM PT, Sep 25). verify-night-2's agent died in the laptop worker's disconnect
(about 5:30–6:50 AM PT). Its branch `lane/verify-night-2` is clean and pushed at 2c92b9e3.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `verify-night-3`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/verify-night-3.md`. Run
> `research notes inbox verify-night-3` (it includes verify-night-2's unread handoffs), and write your first checkpoint within 10 minutes.

## Goal

The standing non-producer verifier for Table 2 cells, as before. Read `$RESEARCH_NOTES/lanes/verify-night-2/` (its report
and last checkpoint: "27 done, 4/4 accepted; equiv 6fdeed7e accepted; pod disk hit 98%").

## Queue, in order (the inbox has the full requests)

1. **x4 instance-equivalence:** art:d9b3724d (x4 8192) and art:b6f2e1df (x4 32768), from b-ligero-standard-hash, in PR #21's
   shape. Re-run each `--check` and record `verified=accepted` if it reproduces. Together with art:6b6d4484, this lets the x4
   plateau take the 4090 BLAKE3 cell.
2. **+sha256 x4 cells** (b-ligero-sha256), from main 2c92b9e3 or later: art:4aa258ee (fp8-hopper-x4+sha256, 32768 plateau,
   proofs art:61842848) and art:fcd6a623 (bf16-hopper-x4+sha256, 8192, proofs art:c25cac59). Name the commit in the label ref.
3. **H100 +blake3 cells** (blake3-80gb): the results behind the new-spec Table 2's two "2.8e8× (prov.)" H100 keyed-BLAKE3
   rows. The inbox and blake3-80gb's last checkpoint have the ids. Verify them if they aren't yet.
4. **xob cells** (b-ligero-standard-hash; red team granted fp8-ada+blake3-xob / fp8-ada-x4+blake3-xob at 5b28557b), and
   poseidon-v1's 5090 NVFP4 pair (art:70f275ac, art:6740eb22) if still unverified.

## Rules and limits

- Branch: `lane/verify-night-3`, cut from `lane/verify-night-2` @ 2c92b9e3 (see `relaunch-branches-0725.md`). Don't commit
  to `lane/verify-night-2`.

- Create a fresh cheapest CPU pod (`vy-verify-night-3`). Don't reuse vy-verify-night-2 (98% disk; the reaper is taking it).
  Terminate the pod when you're done.
- Re-verify with main's `reverify.py` + `ligero-verify` at the commit each grant names. Footnote: file re-verification
  (runner's coins), not transferable.
- After each accepted cell the red team has granted, send red-team-standard-hash-2 a one-line handoff, so it can write
  the `proof_class` label.
- FINAL: 15:30Z hard. Budget: $12 (pods).
- Reply to whoever launched you with the verdicts (artifact → verdict artifact), pods, spend and FINAL.
