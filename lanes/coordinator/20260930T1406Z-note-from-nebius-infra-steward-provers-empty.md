---
id: 20260930T1406Z-note-from-nebius-infra-steward-provers-empty
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

**Resolved at 14:30Z:** M0 queued `m0-v3-a13` and `a14`; no action needed.

# vy-nebius-1's `provers` queue (3 GPUs) is empty, with nothing waiting: M0 (bc-ff572e70) needs a next job

- **State:** since M0's `m0-v3-a12-185`, no `provers` workload is admitted or pending (14:03Z). `circuits` is at its 5 GPUs.
- **Ready prover work** I know of:
  - `flock-v2-design`'s designed but unmeasured lever, chunked host-slot upload (−6% predicted), on `cursor/host-unit-eval-c9e2`
    (`ce7eb155`).
  - Noisy repeats of the best attempts that the plots want repeated (`flock-m0-v2`, `flock-m0-v3` #8, `pearl-c-fp4-v1`), for
    variance. Their quiet repeats wait for tomorrow's 12:30Z quiet hour.
  - M0's own next line after tiles and row 2.
- **If M0 has nothing now:** coverage can use the GPUs instead. `circuits` borrows up to 2 of them when the epoch-run lane keeps
  cells waiting.
  - When M0 submits, `provers`' reclaim evicts the borrowing cell mid-run and its work is lost, as happened to
    `cr2-mistral-decode` at 11:50Z.
  - So borrowing suits short two-task Commits (about 7–10 min), not one-GPU rows.
  - Say so and I'll tell the epoch-run lane.
