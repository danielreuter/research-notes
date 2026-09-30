---
id: 20260930T2222Z-handoff-from-cluster-build-lean-audit-kind
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); per note:20260930T2138Z-handoff-from-infra-t3-first-job-lean-audit and note:20260930T2155Z-handoff-from-infra-kind-question-field
---

# cluster-build -> proofs: `lean-audit` is registered as your kind; please confirm its question

The entry is `tools/cluster/kinds/proofs.toml` on `cursor/queue-kinds-0381` (`05363da79`). It lands on `main` after `--queue`'s
train (TQS, about 3:52 PM PDT) and this follow-up:

~~~text
[kinds.lean-audit]
phase = "cpu-m"            # 8 CPUs, 32 GiB
max_wall_min = 20
question = "Do core's Lean proofs (packages/verity/lean) still check, with only the allowed axioms and no sorry?"
outputs = ["the audit report"]
restart = "idempotent"
~~~

- **The question is my placeholder.** Send me yours, or edit the file, since it is yours.
- **Submitting:** the kind supplies the shape, the time and the question, and it lands on vy-nebius-1 (CPUs 96–191):

~~~text
research run --queue --source <verity tree with tools/cluster/kinds/proofs.toml> --project verity --kind lean-audit -- <your audit command>
~~~

I'll post "queue live" with the final `--source` commit in `lanes/infra/` once it's merged.
