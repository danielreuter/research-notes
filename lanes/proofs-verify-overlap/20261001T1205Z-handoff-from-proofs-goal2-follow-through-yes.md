---
id: 20261001T1205Z-handoff-from-proofs-goal2-follow-through-yes
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Goal 2's follow-through has the owner's yes

The research owner, 4:54 AM PDT (Slack `1790855684.072569`): "Goal 2 follow-through: yes. For the three GPU cases run at
once at K >= 4096, use the same rule as before: record peak device memory per case and fall back to running them in order
when the sum would pass the GPU's free memory."
1. **The how-to** so hill points run in sessions, each citing its session's `art:` id. Write it on your branch now (CPU). It
   opens as a PR only after 7:50 AM PDT, since a PR opened tonight must land by 7:50.
2. **The preflight's three GPU cases at once at K ≥ 4096** (43–148 s per job, serial today). One GPU job on node 1 at 12:55Z
   or later (nothing starts there 12:15–12:55Z), with 128 GiB at K ≥ 8192. Record each case's own wall time, exit code and
   peak device memory, and fall back to running them in order when their sum would pass the GPU's free memory. The question:
   how much of the preflight's 26–148 s per job running them at once saves.
Report in `lanes/proofs/` with run ids. Proofs' node-1 GPU jobs stay at 4 or fewer in flight; bf16-hill submits two and
proofs-arch one at the same time. `source ~/.proofs-env/env.sh` (this VM) for the tokens. Never print it or paste any of its
values anywhere.
