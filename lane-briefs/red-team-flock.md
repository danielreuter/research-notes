---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: red-team-flock (cloud lane)

**Launch status:** READY (4:05 AM PT, Sep 25). flock-128's parameters are in
`$RESEARCH_NOTES/lanes/coordinator/20260925T1055Z-handoff-from-flock-128.md`.

**The profile to audit, `flock-128-r2`:** two sequential runs of Flock b684b12 `Fast100`, each with its own live,
interactive verifier coins, drawn per round and fresh per repetition, with no grinding or PoW credit. flock-128 claims
2^-195.5 for the whole proof (CPU union; about 2^-194.5 for the GPU pair). Its accounting logs every challenger squeeze
(`site_census.rs`, `evidence/census/*.tsv`), gives each site a Schwartz–Zippel degree (`evidence/accounting.py`), takes the
Ligerito proximity terms from the TOML schedules (`evidence/configs/m3{0..3}_{fast,fast100}.toml`, Johnson regime eta 0.02,
BCH+25 list decoding), and says Fiat–Shamir can't reach 2^-128: the 2^60 state-restoration factor leaves two FS runs at
2^-75.6. Pay particular attention to:
- whether the live coins are fresh and independent across the two runs, and that nothing from run 1 is reused in run 2;
- whether "two sequential runs" really squares the error for every term, including terms a cheating prover could correlate
  across runs;
- the Johnson-regime / list-decoding claim behind the query term (the loosest term, -195.6);
- that the verifier refuses `Fast` schedules and FS transcripts when the profile is `flock-128-r2`.

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `red-team-flock`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/red-team-flock.md`. Run
> `research notes inbox red-team-flock`, and write your first checkpoint within 10 minutes.

## Goal

Audit the Flock prover (commit b684b12 plus flock-128's patches) at the **2^-128 profile** flock-128 defined, and decide
whether it grants a whole-proof soundness of 2^-128 under TABLES.md's accounting. This is the remaining condition, after
red-team-link's C1–C8, before the binary backend (and agkr-bound's route (a)) can produce Table 2 cells. Nothing here is a
cell yet.

## Read first

1. `$RESEARCH_NOTES/lanes/flock-128/` (its report, the accounting table, its parameter handoff to the coordinator, and its
   "what a Flock red team must audit" list). This is your scope.
2. `$RESEARCH_NOTES/lanes/red-team-link/20260925T0957Z-report-red-team-link.md`, §3 (composition: today's ~2^-100, PoW credit,
   GF(2^128) terms) and §4 (C1–C8).
3. `$RESEARCH_NOTES/kb/TABLES.md`: the whole-proof bound, how grinding / PoW credit is treated, interactive vs Fiat–Shamir
   coins, and "Red-team review of statement changes".
4. `$RESEARCH_NOTES/kb/flock-prover.md`, and the flock-bench / flock-bench-80gb / flock-glue reports for how Flock is run.

## Decide, each with a verdict (HOLDS / BREAK with a concrete attack / GAP with the missing condition)

1. **Term by term:** each soundness term in flock-128's table reaches its claimed bits at the stated parameters. Check the
   proximity / query terms, sumcheck over the stated field, batching and folding, the PCS opening, and every challenge's
   field size. Check that no term relies on grinding credit TABLES doesn't allow.
2. **Fiat–Shamir:** each challenge is derived after everything it must bind is committed; the transcript is seeded from the
   full statement, not only Flock's own commitment (red-team-link flagged this as an outright break); no reused or
   predictable coins.
3. **Implementation matches the accounting:** the verifier actually enforces the parameters: query counts, field
   extensions, and rejection of proofs made under the weaker profile. Try to get a 2^-100-profile proof accepted by a
   2^-128 verifier.
4. **Composition:** Flock's 2^-128 bound composed with the link's terms and the prime-field backend's bound. Is the whole
   proof still at or above 2^-128? State the total.
5. **Grant:** "CLASS GRANTED", "GRANTED WITH CONDITIONS: ..." or "NOT GRANTED: ...", for the profile, with the negatives an
   implementation must keep passing.

## Method and limits

- Paper and code review first. Demonstrate any attack on a pod (cheapest CPU pod; an H100 only if the attack is GPU-path
  specific), per the setup page's section 4. Keep patches and harnesses as small text files under your `evidence/`, and
  results on R2.
- Don't change Flock's parameters or flock-128's patches yourself. Report what's wrong.
- FINAL: flock-128 FINAL + 3 h, at most 17:30Z (10:30 AM PT). Budget: $15 (pods).

## Deliverables

- Your report in `$RESEARCH_NOTES/lanes/red-team-flock/`.
- A handoff to `lanes/coordinator/` whose title line is the grant verdict, copied to `lanes/flock-128/`, `lanes/agkr-bound/`
  and `lanes/flock-glue/`.
- FINAL (plain, or `--require-pushed` if you pushed a harness branch).
- Reply to whoever launched you with the verdicts, attack artifacts, pods, spend and the FINAL line.
