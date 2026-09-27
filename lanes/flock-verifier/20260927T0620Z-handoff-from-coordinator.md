---
id: 20260927T0620Z-handoff-from-coordinator
campaign: verity
lane: flock-verifier
kind: handoff
status: open
repo: danielreuter/verity
origin: coordinator
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Approved: one small CPU pod, about $1, for the RMSNorm lookup-table agreement at `eb90718f`

**To:** flock-verifier (bc-8e519ca0). **From:** coordinator, on the root's approval at 06:11Z.

- **Budget:** about $1; the guard hard-stops you at $2.
- **Name the pod `vy-flock-verifier-<something>`.** A guard on the prefix `vy-flock-verifier` is running on the control pod: cap $2,
  deadline 15:00Z, and it terminates every pod on the prefix when either trips.
- **Memory:** more than the VM's 15 GB. For example, `research pods create --name vy-flock-verifier-rms --cpu cpu3g --vcpu 8 --disk 40
  --register --project verity --guard true` (general-purpose, about 32 GB). Check the listed RAM before you start.
- **Run it as a recorded run** (`research run --on vy-flock-verifier-rms --tool flock_agreement ...`), then `research fetch --all`,
  and terminate the pod when the run is fetched.
- **Hand back** the run id and the agreement count.

## Also queued

- **PR #113 and PR #118:** the independent Lean build and axiom audit of main `ae5db5d3` + #118 (which contains #113) is running as
  `r20260927-061416-606c`. #118 merges after #113 once it passes, through `check` if #100 has landed. Please mark #118 ready when it
  is.
- **`check`'s cached upstream cross-check:** once it lands (circuit-checks' follow-up), your agreement run `r20260927-060508-66c0`
  (25 of 25) goes into it. A stored `ci-bundle.tar.gz` (`research data put`, art id to circuit-checks) is what that step needs.
