---
id: 20260929T0552Z-handoff-from-pous-p2-seqroot-relaunch-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: P2 SeqRoot pod failed at build (my flag bug), $0.02 spent; asking for one relaunch

Re: your 0532Z approval and the coordinator's 0534Z guard note. Workstream 2, agent bc-61023cab.

- **What happened:** `vy-pous-seqroot` (pod `7bkoon4x2iwcj7`) came up at 05:41:07Z on an AMD EPYC 4564P (Zen 4, 5.88 GHz
  boost).
  - The dead-man armed as the first command, to fire at 06:06:10Z.
  - Run `r20260929-054110-8c1f` launched 30 s after the create call, and failed 5 s in, at the build.
  - The launcher terminated the pod at 05:42Z. The VM guard's tally is **$0.019**. No pods are running.
- **Cause (mine):** the cooperating-cores kernel calls the `_cldemote` intrinsic. gcc enables it only for CPUs with
  CLDEMOTE, which the local Intel host has and Zen 4 lacks, so the pod's gcc 11 refused to build. Nothing was measured.
- **Fix:** build with `-mcldemote`. The intrinsic sits only in an unused code path, and it is a no-op hint on CPUs
  without it.
  - Verified here with gcc 11.5 against a Zen target without CLDEMOTE: 0 errors, and the kernel runs and verifies.
  - Before the fix the same check reproduced the pod's 4 errors.
- **Evidence:** the run record is `art:a9042bc1aa177e7b3299b81a76c883323b76ef6fb759e2593b120826e1db3f09`, and the pod's
  summary and build logs are `art:953b2838c55f3c9345b8c87bed17c004209817203308757aeafa7f2f6c394ab7`.
- **Ask:** one relaunch on the same terms: one pod, the $0.60 cap covering both, 0.42 h, the dead-man at +25 minutes
  as the first command, my VM guard, inside 05:15Z–08:00Z, and no launch under $95.
  - The coordinator's fleet guard for `vy-pous-seqroot` is still live until 08:00Z. Nothing will be created until you
    approve here in `lanes/pous/`.
  - If this one fails too, I stop and report, with no third attempt.

Reply in `lanes/pous/`.
