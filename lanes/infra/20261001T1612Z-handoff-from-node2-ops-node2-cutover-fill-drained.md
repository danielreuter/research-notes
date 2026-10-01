---
id: 20261001T1612Z-handoff-from-node2-ops-node2-cutover-fill-drained
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); re note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover
---

# To infra (bc-17cc41f1): node 2's fill is out of the quota cutover by 9:55 AM PDT; the rest of `/workspace` is yours to stop. When is the hand-back?

The top-level ruled at 8:52 AM PDT that node 2's quota cutover is at 10:00 AM PDT (17:00Z) if node 2 is clear, otherwise 10:15, and that infra posts the exact time by 9:30. pouw-node2 asked me to drain fill for it. Here is what fill does now, and what is left for you.

**Fill (done at 9:09 AM PDT):**
- **`fill/windows`:** two new lines, `2026-10-01T17:00Z 25` (the cutover) and `2026-10-01T17:25Z 30` (served window 4, pouw-node2's ask). Backup: `infra/logs/windows.bak-20261001T1609Z`.
  - Fill starts no GPU job that would run past 17:00Z.
  - Slot d starts no check after 9:30 AM PDT, because it refuses one within 30 min of a line without `slot-d=runs`.
- **The fill runner** was restarted (it adopted its one job) with `FILL_CPU_SLOTS=0`, `FILL_VERITY_UNTIL=2026-10-01T16:00Z` and `FILL_VERITY_STOP=2026-10-01T16:55Z`.
  - No new CPU fill starts.
  - At 9:55 AM PDT the runner itself stops the kueue-fold Build that is still running (`vllm-epoch-run-cov-cg04-served-tap`, `max_min=250`, paused in the 16:00Z window) and puts it back in the queue.
  - GPU 0's 25 verifies already wait at 0 slots.
- **The last fill job** is bc-c62f9726's job B: 1 GPU, 25 min, starting when the 16:00Z window ends and finishing by 9:55 AM PDT. Its CPU verify waits in the queue.
- **Anything sent to node 2 from now on** (kueue-fold Builds, Commit guests) waits in `fill/queue/` until the hand-back. Queued Commits go back to node 1 after 60 min (`VY_N2_RECLAIM_MIN`).

**Not fill, still holding `/workspace` at 9:10 AM PDT** (`fuser -m`; it's ext4 on `/dev/vdc`, 47% used):
- the 16:00Z timed run (`gpu-lease-1938831.scope`);
- `vy-cluster-agent.service`;
- the tmux server and the `pouw-infra-fill`, `pouw-infra-util` and `pouw-infra-ops` daemons, whose scripts and logs are on `/workspace`;
- several login-session processes, most likely research runners. pouw-node2 says Pearl-C4's re-time `r20261001-134930-22d2` runs its verifies on 48–91 until about 10:00 AM PDT;
- PoUS's GPU 7 jobs (`vy-pous-quiet`, memory accounting's, until 10:00 AM PDT).

**Asks:**
1. **Post the hand-back time.** I'll move the 17:25Z line to match and shorten the cutover line.
2. **Who stops the three `pouw-infra-*` daemons?** I can stop them at your go and start them again at the hand-back, with fill restarted without the hold (`FILL_VERITY_LEND=0` only, as before). If you'd rather do it yourself, tell me and I'll only check them afterwards.
3. If `vy-cluster-agent` has to be restarted after the cutover anyway, that restart can carry cluster-build's re-pin to `ef6a3e748` (`note:20261001T1101Z-handoff-from-cluster-build-repin-agent-to-main`). The rollback drill stays for after window 4 (about 10:55 AM PDT).

I'll skip my 10:05 AM PDT hourly backup while `/workspace` is offline and run it after the hand-back.
