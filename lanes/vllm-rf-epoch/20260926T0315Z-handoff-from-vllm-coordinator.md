---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T03:15Z
---
# NEW TASK (root-approved): bisect #4 and #23. Budget $10, CPU first. Deadline 08:00Z

Daniel wants the two unexplained verdict changes explained tonight. For each row, report **the offending commit** and whether it's
a **product bug**, a **test expectation** (the record expects the wrong thing), or **expected behaviour** (an accepted change, so
the record is re-baselined with a reason). Keep your pods terminated unless a step needs one. Name new pods
`vyv-rf-epoch-bisect-*`.

**Step 0: free, no GPU. Name the failing check from the records.**
- #4 (FAIL-class, Commit now PASS): read why the record expects FAIL (`tests/regression/expected/<#4 row>.json`: `commit_summary`
  and the failing check or class; the `fixtures.toml` decisions). Compare with your epoch Commit's checks (preserved copies
  `r20260926-020557-*` and `-021148-*`). Name the check that went FAIL → PASS.
  - If it's a verdict or C2 rule, re-evaluate it on CPU from the recorded Commit outputs with `verity-vllm verdict from-record`
    at trees before and after the suspect commits: main `33e4d8d1` (a4), then each merge that touched that rule (b2vb, b1, c1, m32
    `271a0952`, and your epoch commits). That's a CPU bisect.
- #23 (GREEN, Match now NO FOLD): read which fold stage fails (`fold_summary` and `resolution.json` in your preserved Match copy).
  List the commits that touched it: b5patb (the patterns split), b4 (hooks and capture), b5vab (vllm_adapter), b5vc (bindings),
  and epoch items 1 (v2 Ampere step) and 2 (profile id).

**Step 1: only if step 0 doesn't pin it.**
- #23: capture once on one L40S (Build + Match at current main, **without** epoch commits, with `sampled_proofs` on PYTHONPATH).
  - If NO FOLD reproduces, it's on main, not the epoch: re-fold that capture on CPU at each candidate merge (b5pat's re-fold
    approach, `derived_*` profile) to find the commit.
  - If main folds fine, re-fold your epoch capture on CPU with `30427930` and `a784d421` each reverted.
- #4: a GPU Commit only if the flip can't be evaluated from records. Use one L40S, at main without the epoch, reusing a Build if you
  can.

**Report:** a handoff to `lanes/vllm-coordinator/` titled "BISECT #4 #23": per row, the check, the commit, the classification, the
evidence runs, and a proposed fix or re-baseline reason. The coordinator folds it into `docs/vllm-epoch-review.md`. Use the
no-waiting rule while jobs run.
