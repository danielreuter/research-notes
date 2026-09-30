---
id: 20260930T2021Z-handoff-from-proofs-relay-proof-workers
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (new proofs coordinator bc-8416bc72, Slack @proofs, notes lane `proofs`)
---

# verity-root: the proof charter's workers are yours, not the old RC's. Please relay their results to `lanes/proofs/` until they finish

The old research coordinator runs only four agents (`note:20260930T2020Z-handoff-from-coordinator-state`). The charter's
other workers (`note:20260930T1900Z-handoff-from-verity-root-charter-proof`) are your lanes:
- M0 bc-ff572e70 (running: #21 next, benches on node 1's `provers` queue);
- flock-verifier bc-8e519ca0 and audit-lean bc-a0c5a22f (waiting on the #434 → #430 → #441 train);
- GEMM relation bc-590cc416 (#538 → #550, `hk32` left);
- refinement bc-159ce83b (#432 conflicts);
- soundness bc-9e538dc5; draw law bc-0b392ca4; value binding; ZK table; ZK public/private; consolidation bc-e373566b; M1
  bc-2a9978cc;
- the red team bc-f0bc7e75 (silent since 9:45 AM PDT).

I'm the proofs coordinator now, and I can't wake another Project's agents. Please:
1. **Relay** each result from these workers that changes a plan to `lanes/proofs/`, until each finishes. Send M0's first,
   and any red-team verdict.
2. **Tell each running worker** (M0 especially) to put `lanes/proofs/` on its handoffs, beside yours.
3. **Hold** new work for them. Daniel's 1:16 PM PDT priorities hold new backlog work until infra settles the one queue.
   In-flight work finishes. I've logged their open PRs as backlog in the Project store (`internal/proofs/state.md`).
4. **Once you close,** I treat them as read-only sources: a fresh proofs worker takes over whatever is still needed,
   seeded with their PRs, branches and transcripts.
