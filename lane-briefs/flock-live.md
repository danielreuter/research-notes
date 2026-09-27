---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Lane brief: flock-live (cloud lane)

**Launch status:** READY (4:40 AM PT, Sep 25).

**Launch as:** a Cursor cloud agent in `danielreuter/verity`, base branch `main`. Give it this prompt:

> You are lane `flock-live`. First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1, then read `$RESEARCH_NOTES/kb/LANE-CONTRACT.md`. Your brief is
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/flock-live.md`. Run
> `research notes inbox flock-live`, and write your first checkpoint within 10 minutes.

## Why

red-team-flock did not grant `flock-128-r2`, the Flock 2^-128 profile: two sequential `Fast100` runs with live verifier
coins, 2^-195.5 on paper. The terms hold. What fails is the implementation around them:
- **The break:** the two reps aren't bound to one commitment, so rep 2 can prove a different witness (art:8d04b53f).
- **The gap:** no live-coin challenger exists. Flock's verifier is Fiat–Shamir only, which caps r2 at 2^-75.6.

Until R1–R8 hold and a red team re-audits the live challenger, the binary backend (and agkr-bound's route (a)) has no
2^-128 cell. This lane builds R1–R6, pins R7 and R8 in the verifier, and hands off to a re-audit.

## Read first

1. `$RESEARCH_NOTES/lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`: the verdicts, R1–R8, and §5's 10
   negatives. This is your specification.
2. `$RESEARCH_NOTES/lanes/coordinator/20260925T1130Z-handoff-from-red-team-flock.md` and
   `$RESEARCH_NOTES/kb/flock-prover.md`, including its "Red-team verdict on flock-128-r2" section.
3. `$RESEARCH_NOTES/lanes/flock-128/20260925T1018Z-report-flock-128.md` and its patches
   (`lanes/flock-128/evidence/flock-128-r2-{cpu-harness,gpu}.patch`, `pod-scripts/`): the profile and the harness you
   extend.
4. `$RESEARCH_NOTES/kb/live-verifier.md`: how B-Ligero's live verifier runs a session (own coins, session record), which is
   the pattern R8 asks for.
5. `$RESEARCH_NOTES/lanes/red-team-link/20260925T0957Z-report-red-team-link.md` §3–4: the link's coin ordering (R5
   depends on it).

## Build, in order

1. **R1, one commitment for both reps.** Either reuse one commitment per table across both reps, or check
   `root_rep0 == root_rep1` before any rep-1 coin is issued. The link binds that root. The commit is deterministic, so this
   should cost nothing; show that.
2. **The live-coin challenger (R2–R5), CPU path first.** A challenger that forwards every squeeze to a live verifier
   process, which draws its own coins.
   - R2: commit before coin, plus a final replay that checks every prover message against the coins actually issued.
   - R3: `fork_from_seed` becomes live. The merged opening's concurrent multipoint/anchor child must get live coins too,
     not an FS child from the fork seed.
   - R4: PoW and nonce sites return pure verifier coins.
   - R5: Flock's coins go out only after root_F, the link points and y are committed.
   - Fresh, independent coins per rep.
3. **R6, the GPU device-side live path.** Flock-CUDA squeezes on the device (`zc_challenger_device.cuh`). Give it a live
   path: coins from the verifier, delivered to the device in the right order. Cost it, since every round trip is latency
   the prover pays. Report the H100 BF16/FP8 prover time at 4096 VUs, live against FS, same pod.
4. **R7 and R8 in the verifier.** It pins `Fast100`, reps = 2 and the RS flavour from configuration, and rejects lone reps
   and AG-path (aarch64 r₁) proofs. The evidence a result carries is the live session record only.
5. **Negatives:** all 10 in red-team-flock's report §5, starting with "reps with different roots are rejected". Also: a
   replayed coin, a message sent after its coin, an FS transcript presented as live, a lone rep, and a Fast-profile proof.
   Every honest live session must verify.

## Where the work happens

- Flock (b684b12) and Flock-CUDA are external repos. Clone and patch them on your pods. Keep the patch series as text
  files under `$RESEARCH_NOTES/lanes/flock-live/evidence/`, and results on R2 (`research data put --preserve`, or
  `research run ... --custody-r2`).
- If the live session driver belongs in `verity` (next to the B-Ligero live verifier), put it on branch `lane/flock-live`
  and send the coordinator a merge-ready handoff when it passes. Don't touch B-Ligero's verifier.
- Pods: the cheapest CPU pod for steps 1, 2, 4 and 5, and one H100 for step 3. Terminate each as soon as you're done
  with it.

## Scope limits

- Don't change Flock's soundness parameters (flock-128-r2 stays `Fast100` × 2). If a condition can't be met without
  changing them, report it.
- Don't audit your own work. The re-audit is a separate red-team lane. Your job is to make it easy: a checklist mapping
  each of R1–R8 and each negative to code and to a test.
- Nothing you produce is a Table 2 cell until that re-audit grants the profile.

## Budget, FINAL and deliverables

- FINAL: 15:30Z hard (8:30 AM PT). Budget: $25 (pods).
- Your report in `$RESEARCH_NOTES/lanes/flock-live/`, with the R1–R8 checklist, the negatives table and the live-vs-FS
  costs.
- A handoff to `lanes/coordinator/` titled with the result, e.g. "flock-live: R1–R8 implemented, ready for re-audit; live
  H100 BF16 at 4096 = X s (Y× FS)". Copy it to `lanes/agkr-bound/` and `lanes/flock-glue/`.
- FINAL (`--require-pushed` if you pushed a branch). Then reply to whoever launched you with the checklist, the costs,
  artifact ids, pods, spend and the FINAL line.
