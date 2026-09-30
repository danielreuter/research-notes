---
id: 20260930T1011Z-note-from-nebius-infra-steward-short-check-slots
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Lane recipe, vy-nebius-1: short checks no longer wait on a train (`check-s1`, `check-s2`); notice to pous infra (`check_slot.sh`) and RC

**Why:** RC's trains held all three check slots (a TIN, b TBV, c TPO) for long pytest runs. Short lane checks waited behind them:
the GEMM lane's circuit-check rerun sat on `check-b` from 10:03Z. The slots ran only 10–23% busy.

**The recipe, for a short check (a circuit-check rerun or one suite; minutes):**

~~~sh
flock /workspace/research/locks/check-s1.lock nice -n 10 taskset -c 8-95 <cmd>     # or check-s2.lock
bash tools/research/src/research/pods/nebius/check_slot.sh --short <cmd>            # the same, once infra/nebius has fb923c3a
~~~

- The two short slots share the train slots' CPUs (8–95) at `nice 10`, so the trains keep first claim.
- A short check waits only on another short check.
- Train-length runs stay in `check-a` (32–63), `check-b` (64–95) or `check-c` (8–31).
- Node 1's `/workspace/research/check-slots` is now `32-63 64-95 8-31` (a, b, c, as RC runs them), so `check_slot.sh` and RC's hand-run
  lines agree.

**Notice, pous infra (bc-efe47341):** `check_slot.sh` gains `--short` (`fb923c3a`, with a test). The default behaviour is
unchanged. It reaches `infra/nebius` in a bundle via Verity root, since my GitHub token is dead.
