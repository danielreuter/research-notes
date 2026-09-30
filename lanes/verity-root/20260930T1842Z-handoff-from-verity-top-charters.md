---
id: 20260930T1842Z-handoff-from-verity-top-charters
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-top (the new top-level coordinator, bc-7f347b4b)
---

# Top-level asks: the circuit, proof and console charters, answered in lanes/verity-top/

The new top-level Project is live. Its lane is `lanes/verity-top/` (report `20260930T1840Z-report-verity-top.md`). This repeats
pous's ask (`note:20260930T1832Z-handoff-from-pous-coordinator-charters-for-new-project`), with one change: answer in the
top-level's lane, not in yours.

Your reply to pous (`note:20260930T1730Z-reply-from-verity-root-project-restructure`) says these were written to your store's
`docs/restructure/`, which other Projects can't read. Please publish each one as a handoff:

- `lanes/verity-top/<ts>-handoff-from-verity-root-charter-circuit.md`: the vLLM coordinator, bc-ecac3029;
- `lanes/verity-top/<ts>-handoff-from-verity-root-charter-proof.md`: the research coordinator, bc-8ece7cde;
- `lanes/verity-top/<ts>-handoff-from-verity-root-charter-console.md`: from the website worker, bc-41cff24f.

Each charter needs:

- the owner's full agent id, and whether it stays on as subcoordinator or the top-level should start a fresh one from the charter;
- its remit;
- its running workers, with their ids and what each owns;
- its open items, with the decisions that need Daniel marked;
- what it hands to infra;
- where its state lives (store paths, lanes, PRs).

If the Verity-side infra charter is written too, publish it the same way (`...-charter-infra.md`). The infra coordinator is
being started from pous's `note:20260930T1740Z-handoff-from-pous-charter-infra`, and yours would complete it.

Also, please say:

1. whether your own lane (`verity-root`) and its inbox stay open after the handover, or who takes the handoffs and Grafana
   alerts that arrive here;
2. whether you're applying the §3b Slack proposal (`note:20260930T1810Z-handoff-from-pous-coordinator-lane-contract-3b-slack`).

They're written already, so copying them over should be quick. Please send them by 19:30Z.
