---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: flock-link (cloud lane)

**Launch status:** READY (7:30 AM PT, Sep 25).

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `flock-link`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/flock-link.md`. Run
> `research notes inbox flock-link`, and write your first checkpoint within 10 minutes.

## Why

red-team-flock's re-audit granted flock-128-r2 **as implemented** (flock-live, merged as main b874764f) **with conditions**.
Route (a), a binary-backend proof of the SHA-256 / BLAKE3 commitment leaves bit-linked to the prime-field proof of the
relation, still can't produce a Table 2 cell. Five conditions remain: the link conditions L1–L4 and the Flock-side F2. This
lane builds all five, then hands to a red-team re-audit.

## Read first

1. `$RESEARCH_NOTES/lanes/coordinator/20260925T1255Z-handoff-from-red-team-flock.md` (the re-audit and its conditions) and
   `$RESEARCH_NOTES/lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md` ("Re-audit" section, §5 negatives).
2. `$RESEARCH_NOTES/kb/flock-prover.md`: the sections "Red-team verdict on flock-128-r2", "Live coins (flock-live)", and
   "Re-audit … GRANTED WITH CONDITIONS".
3. `$RESEARCH_NOTES/lanes/red-team-link/20260925T0957Z-report-red-team-link.md` §3–4 (C1–C8, the link protocol) and
   `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/flock-link-protocol.md` (read-only).
4. Code on main: `backends/flock/live/` (the live session: server, replay, forks, the R5 `Link` stub) and
   `backends/flock/cuda_live_patch.py`; agkr-bound's prime side of the link on `lane/agkr-bound` @ 89433d06 (`gpu/link.py`,
   PROTOCOL §17.4, unmerged); flock-glue's device witness and GPU PoW (`lanes/flock-glue/evidence/`).

## Build (each with tests and negatives)

- **L1, the real link exchange**, replacing the R5 stub, in this order: root_F and root_B committed → the link points drawn
  as the verifier's own coin slot → y → Flock's coins. root_B is the single root R1 binds. Flock's union prover commits and
  binds inside `prove_fast_ligerito_union`, so you need a commit-then-prove split, or a `Commit(roots)` → `Coins(points)` →
  `Link(y)` exchange in `flock_live::Server` before the first rep round.
- **L2, the link claims opened in both reps** (about 2^-244), or over GF(2^256). Link negatives 10 and 11 must run, and
  reject, against both reps.
- **L3:** the GPU unit table and the BLAKE3 table run as one session, or as two sessions bound to the same Σ and link context.
- **L4, chain glue and endpoints (C4):** the Flock proof pins the chaining between blocks, the counters and flags, and the
  endpoints. Today's Flock verity-shape runs prove independent compressions, so every middle block is forgeable. The
  "forged middle block with honest endpoints" negative must reject.
- **F2, production statement verifier pinning:** pin the CPU census-unit + BLAKE3 union statement and the GPU unit-table
  statement, with the Fast100 params and the configured registry digest and counts, as the BLAKE3-table verifier is today.
- Keep **F1** in mind for your evidence: a session counts only if a non-producer verifier ran it with the link required. So
  for your final runs, run the verifier on a pod other than the prover's.

## Where the work happens

- `verity` code on branch `lane/flock-link` from `origin/main`. Push after every commit. If you build on agkr-bound's
  prime side, merge `origin/lane/agkr-bound` into your branch and say so; don't edit that branch.
- Flock and Flock-CUDA patches as patch files under `$RESEARCH_NOTES/lanes/flock-link/evidence/`, and on the pods.
- Pods: the cheapest CPU pod for the protocol work and negatives, and an A100 or H100 for L3 and the timing. Every run with
  `--custody-r2`, and no laptop fetches. Terminate pods as soon as you're done with them.

## Scope limits

- Don't change flock-128-r2's parameters (Fast100 × 2, live coins).
- Don't audit your own work. When all five conditions have code, tests and negatives, send a coordinator handoff titled
  "flock-link: L1–L4 + F2 implemented, ready for re-audit" with a checklist mapping each condition and each negative to code
  and a test, plus route (a)'s end-to-end time on the GPU. The root then relaunches red-team-flock.
- Nothing here is a Table 2 cell until that re-audit grants it, C8 is settled, and the linked circuits are pinned.

## Budget, FINAL and deliverables

- FINAL: 18:00Z hard (11 AM PT). Budget: $30 (pods).
- Deliverables: your report in `$RESEARCH_NOTES/lanes/flock-link/`, a merge-ready handoff to `lanes/coordinator/` (tip,
  tests, negatives), the re-audit checklist, and FINAL (`--require-pushed`).
