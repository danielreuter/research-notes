---
id: 20260930T1530Z-handoff-from-nebius-infra-steward-4-waiting-342242c3
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Up to 4 cells may wait in Kueue now, not 2 (postmortem, until the dispatcher runs); `infra/nebius` `342242c3` enforces it

- **The cap:** `submit.sh` now refuses a `config-run` / `config-run-row` submission (exit 4) when 4 coverage cells already wait for
  `circuits`. It refuses any submission when 6 jobs wait in both queues together, which keeps 2 of SkyPilot's 8 launch slots for
  prover jobs. Admitted and finished workloads don't count.
- **Also in `342242c3`:** the TP2 lane's GPU-task lines (postmortem action 4a).
  - The Triton cache is per tree, on eager rows only.
  - The shared JIT build directories apply only to trees that carry #561's staged sources.
  - Once a tree has #561, a Commit stops rebuilding `hidden_gpu_tree`: SmolLM2's GPU hold drops from 436 s to about 85 s.
- **Without GitHub:** the store's `artifacts/nebius/infra-nebius-342242c3.bundle`, sha256
  `17c6cbf78e90816f17a27bc2588a58d100d73ff8ed187d510ef041bd75041f9c`. It needs `8f777377`.

  ~~~bash
  git fetch <bundle> infra/nebius:refs/remotes/origin/infra/nebius && git merge origin/infra/nebius
  ~~~
