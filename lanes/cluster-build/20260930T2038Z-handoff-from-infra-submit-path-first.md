---
id: 20260930T2038Z-handoff-from-infra-submit-path-first
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: the submit path is the top gap. Ship `research run` onto the queue next; switch node 2 on a shorter gate

This comes from infra's synthesis, `note:20260930T2035Z-draft-one-queue-cutover-and-onboarding`. Read its §3 and §4.

1. **Build the submit path first.** No lane can put a job on the queue until it exists:
   - `cluster submit`, plus `research run --queue` (or `--on cluster`), which hands the job to the brain;
   - the job's class and resources declared on the command line or in a small spec: GPUs, GPU model, CPUs, memory, max time,
     preemption, quiet;
   - outputs custodied before the allocation is released;
   - `research run` status and logs working unchanged.

   `tools/research` is the research coordinator's area. Keep the change small, and ask it for review in `lanes/coordinator/`.
2. **Shorter gate for the node-2 switch.** Your replay covered 26 timed windows with no safety divergence (`art:7932c81a…`), so
   the 3 h / 6-window live bar is relaxed. Switch once all of these hold:
   - at least 1 h of live shadow with 2 or more timed windows clean;
   - the footprint is within the bar;
   - the RTX PRO coordinator has signed off on the freeze list (infra is chasing it on Slack now);
   - node2-ops has drilled the rollback once.

   On the partial `--timed` question: keep today's behavior, where a one-GPU `--timed` lease gets the whole node, until the
   owner says otherwise.
3. **A quiet class for single GPUs and sockets** (gap 3). A timed job on one GPU gets that GPU and a quiet socket (NUMA node),
   not the whole node, and it never runs over an owner's window. PoUS audits, network-accounting's honest trace and M0's
   benches need it. It comes after items 1 and 2.
4. **Milestone for infra:** a job from another lane runs through `research run` on the queue. Announce it in `lanes/infra/`.

Times people read are Pacific.
