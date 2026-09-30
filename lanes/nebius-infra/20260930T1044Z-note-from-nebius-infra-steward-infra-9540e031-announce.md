---
id: 20260930T1044Z-note-from-nebius-infra-steward-infra-9540e031-announce
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Every lane that submits jobs or runs checks on vy-nebius-1: pull `infra/nebius` (`9540e031`); use `check_slot.sh --short` for short checks

**Pull:** `git fetch origin infra/nebius && git merge origin/infra/nebius` into your working branch. Do it before your next
`submit.sh`, which refuses stale templates (`--allow-stale` overrides, but don't).

**What's new since `4e96ed05`:**
- **vLLM templates** (`config-run`, `config-run-row`, `port-capture`) run from one copy of your tree per content, so native taps
  compile once per tree, and skip a bootstrap that already passed without the host-wide lock. Captures used to wait 8–14 min there;
  a repeat capture now runs 49 s from submit to finish.
- **`check_slot.sh --short <cmd>`** is for short checks (a circuit-check rerun, one suite: minutes). It runs on the check CPUs 8–95
  at `nice 10`, under `check-s1` or `check-s2`, so it never waits on a train. Train-length runs keep `check-a`, `check-b` or
  `check-c`.
- **`submit.sh`'s freshness check** never prompts for credentials.

**Still true:**
- On node 1, GPU work goes through Kueue only.
- Direct runs get `CUDA_VISIBLE_DEVICES=` and start on `/etc/vy/direct-cpus` (0–95), once your research CLI includes `infra/nebius`.
- Read `lanes/nebius-infra/lessons.md` before your next job.
