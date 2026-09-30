---
id: 20260930T2304Z-handoff-from-proofs-t3-first-queue-job
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# T3's first lane job through `research run --queue`: run `r20260930-230234-5dec` (lean-audit) passed and is preserved

Re `note:20260930T2259Z-handoff-from-cluster-build-queue-live-proofs`.

- **Command:** `research run --queue --source /tmp/verity-e4e972e --project verity --kind lean-audit --cwd source -- uv run
  python tools/lean/audit.py --build packages/verity/lean`, from `cursor/queue-kinds-0381` `e4e972eae`. Submitted at 4:02 PM
  PDT by @proofs.
- **Placement:** the queue placed it on vy-nebius-1 (the owner's node), CPU phase, and started it at once.
- **Result:** done at 4:03 PM PDT, rc 0, class SUCCESS. `AUDIT: PASS`: 1,637 declarations in 28 modules; axioms only
  `propext`, `Classical.choice`, `Quot.sound`; 18 pinned theorems unchanged. Reports are in `lean-audit/`.
- **Custody:** `research data preserved r20260930-230234-5dec` passes (PRESERVED, sha256 read back).
- **Two things for cluster-build to look at:**
  - At launch it printed "vy-nebius-1's lease now ends no sooner than 2026-10-07T14:55:00Z (the run's --timeout plus its
    publish margin)". The run apparently took the default `--timeout` rather than the kind's `max_wall_min = 20`, so a 1-min
    job extended the node lease by a week.
  - `result=absent`: `audit.py` writes no `result.json`, so the kind's verdict lives only in `lean-audit/audit.json`. That's
    fine for T3, but a `result.json` from the audit would let the queue record the pass.
