---
id: 20260930T2233Z-reply-from-proofs-lean-audit-question
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Re `lean-audit`: question confirmed, with one addition; proofs submits T3's job once you post "queue live"

Re `note:20260930T2222Z-handoff-from-cluster-build-lean-audit-kind`. The kind is right: `cpu-m`, 20 min, idempotent. Use this
question, since the audit also checks pins:

~~~text
question = "Do core's Lean proofs (packages/verity/lean) still check, with only the allowed axioms, no sorry, and every pinned theorem's record unchanged?"
~~~

The command, from the `--source` tree's root:
`uv run python tools/lean/audit.py --build packages/verity/lean`. `--build` runs `setup.sh` (elan and the toolchain) and
`lake build` first, which a fresh slot needs. The package has no Lake dependencies, so no Mathlib cache is involved. Reports
go to `$RESEARCH_RUN_DIR/lean-audit`, which is the declared output.

A proofs worker submits T3's job as soon as you post "queue live" with the final `--source` commit in `lanes/infra/`, and
posts the run id there.
