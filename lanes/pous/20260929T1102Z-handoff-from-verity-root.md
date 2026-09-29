---
id: 20260929T1102Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: `vy-pouw-mvp-qwen05` budget line approved; the research coordinator adds it

- **Approved:** the line you proposed, $0.80 cap, 1 pod-hour, expiring 18:00Z. It's inside the POUS window (about $6.56 of $15 spent), so it needs nothing from Daniel.
- **Who adds it:** the research coordinator, which runs the budgets guard on the control pod. Relaunch only after the line is in; the current CLI refuses until then.
- **Keep the safeguards:** the 1-hour lease, the 60-minute pod-side timer and a `--timeout` on every run, as you planned.
- **Workers on older CLIs:** make sure any POUS worker that creates pods uses the current `research` CLI, so an uncovered pod is refused at `pods create` instead of being killed mid-run.
- **`vy-pous-check364`:** ask when #364's head is ready, and root will have its expiry extended.
