---
id: 20260930T1917Z-draft-from-verity-root-runpod-spend-and-check-pod-policy
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: verity-root
---

> Copy of verity-root's `docs/, notes.md, preferences.md, internal/lanes/*`, posted for infra on request
> (`note:20260930T1905Z-handoff-from-infra-alert-sink-one-change-and-docs`). Links of the form
> `/cursor/stores/bc-36415049-…/docs/X.md` point into verity-root's store; ask verity-root for any you need.

# RunPod spend history and the "no check pods left" policy

Pulled from verity-root's `docs/` (morning-report-sep30, infra-overview, spend-broker-via-site, backend-sweep, restructure/infra), `notes.md`, `preferences.md` and `internal/lanes/*`. Times UTC unless marked PT. Key names only; no values.

## Policy now

- **No RunPod check pods left** (restructure/infra, 17:35Z Sep 30): checks moved to the Nebius cluster (node 1, `vy-nebius-1`) through the dispatcher, so the CI pool (`vy-coord-*`) was drained. On-demand buying (bursting to RunPod when the cluster is full) is **not built**.
- **Root approves no new RunPod spend** (since ~Sep 30 early UTC; the root/research line was at ~$458–459 of $480). RunPod coverage cells held since 11:26 PM PT Sep 29. Lanes asking for lines (e.g. POUS hash-cut, #433) were told: no RunPod line; use node 2 or node 1's Kueue.
- **Decision pending with Daniel** (morning-report-sep30 §5.1): raise the line by $450 to $930; or keep $480 and restrict RunPod to check pods; or keep $480 for checks plus a separate capped coverage line. **Root's recommendation:** keep $480, restrict RunPod to check pods; if L40S/A100/H100 coverage columns are wanted this week (only RunPod has those GPUs), approve a capped line such as the existing `vyv-cov-` $150 line, not a blanket $450.
- **Daniel's standing preferences:** RunPod auto-tops-up, so a low balance is not a blocker and needs no top-up request or balance gate; spend caps and guards are the controls (Sep 29). Merge velocity beats CI spend: a larger CI pool (~$120/day standing, more on backlog days) over trains waiting on pods (Sep 29). Borrow/self-host rather than new paid services; compute capacity is the exception (Daniel chose a standing cluster).

## Mechanism

- Every project pod needs a line in the notes repo's `budgets.toml`: name prefix, total or rolling-24h cap, expiry, max pod age. Lane asks in `lanes/coordinator/`; Daniel approves via root (or within an existing cap); RC commits; the budgets guard (the only guard, since #358/#370) picks it up within a minute. Expiry blocks new pods only; running pods end on their leases.
- Other bounds: per-pod lease and idle guard; the guard's $25 balance floor (a tripwire given auto-reload). Not capped by us: network volumes (`verity-r19-evidence`, 700 GB), R2, Vercel, Cursor.
- Proposed: the site as sole RunPod-key holder and spend broker (docs/spend-broker-via-site.md; infra-overview "Step 2").

## Lines and envelopes

| Line | Cap | Notes |
|---|---|---|
| research / root line | $380 → $480 (Daniel, 05:02Z Sep 29) | $451.54 at 06:25Z Sep 29; ~$459 (96%) at 5:17 AM PT Sep 30 |
| `vy-coord-` (CI pool) | $65/day, until Oct 6, 168 h pods | 2 always-on, up to 8 queued; `vy-coord-t1` at $1.09/h; now no pods (checks on node 1) |
| `vyv-rf-epoch-` (vLLM epoch) | $260 | closed at ~$210 (guard read $215.23, 05:25Z Sep 30) |
| `vyv-cov-` (vLLM coverage) | $150 | live in guard since 06:22Z Sep 29; cells held |
| `vyb-` (backend GPU sweep) | $100 → $250, 10 $/h | $82 of $250 spent; ~525 L40S GPU-h |
| small lines | M0 $5 ($2.06 spent), sm_120 port $60 (~$12–24), flock-netlist $5, pouw-mvp $1.80, pous-check364 $1.50, `vy-train-` ~$22.55 | mostly expired |

## Timeline

- **Sep 22–23:** balance $296.21 (12:00Z Sep 22) → $202.11 (12:05Z Sep 23).
- **Sep 28:** backend sweep under `vyb-` from 02:56Z; 07:33Z POUS flags ~5.6 h runway at the burn; 10:45Z balance $100.70; 11:03Z top-up to $297.13 (~+$200 of ~$450 asked); root hold lifted for approved budgets only (epoch wave 1 ~$147, sweep ≤$250, research ≤$380); 11:37Z sweep capped at $7.55/h because the balance was shared with the epoch.
- **Sep 29:** 05:02Z research line to $480; CI pool line $65/day created; 06:25Z $451.54 of $480 (94%); 13:04Z balance $252.14, $132.96 uncommitted after caps; RunPod auto-reload noted, balance gates dropped.
- **Sep 30:** 05:25Z balance $134, epoch closed; Nebius servers (~$29.60/h, ~$710/day, hard stop Oct 1 ~10 PM PT, moving to Oct 7 8 AM PT per Daniel) take GPU work and checks; RunPod check pods gone; root approves no new RunPod spend.
