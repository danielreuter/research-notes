---
id: 20261001T0005Z-handoff-from-proofs-advisor-notes
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# You're now the top priority (advisor, 5:04 PM PDT). Don't fork M0's pipelining

- The advisor puts verifier overlap **first**: with whole-session overhead, every BF16 step is ~8× verifier-bound until it
  lands.
- `flock-circuit` `serve`/`prove` is M0's code (lane flock-netlist, PR #554). Build on #554's tip, and keep
  `FC_PIPELINE_DEPTH` / `FC_HOST_PREPIN` semantics unchanged so the two don't fork. Write a short note to
  `lanes/flock-netlist/<stamp>-handoff-from-proofs-verify-overlap.md` describing the change. M0 isn't taking new work, but
  its lane should know.
- Use ~24 vCPU per job, and the batched session (`--session-tables J`).
