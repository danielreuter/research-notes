---
id: 20261001T0102Z-handoff-from-proofs-widen-prover-cpus
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Can node 1's dispatcher give `provers` jobs more than cores 96-159? The hillclimb lanes contend there while 0-95 and 160-191 sit idle

Node 1 at 6:01 PM PDT:
- 192 cores. In total, cores 0-95 were about 3 cores busy, cores 96-159 about 6, and cores 160-191 about 0.5.
- 7 of 8 GPUs idle, load average 14.

The dispatcher runs every job under `taskset -c 96-159`. That's four 16-core slices, so at most four hillclimb jobs run
cleanly at once, and points keep coming back flagged `cpu-slice-shared` (shared cores make the CPU-bound verifier, and
so the session overhead, unreliable). proofs-bf16-hill's slice locks (`cpu-slices.sh`, `/workspace/jobs/slices`) now keep
lanes apart, but each lane gets only two slices.

**Ask:** widen the `provers` / `prover-bench` CPU range to 0-191, or whatever isn't reserved, say 32-191. That's ten
16-core slices, enough for one clean job per GPU. If something owns 0-95, tell me what and I'll stay out. This is a
config change, not more spend: the GPUs are already ours and idle.
