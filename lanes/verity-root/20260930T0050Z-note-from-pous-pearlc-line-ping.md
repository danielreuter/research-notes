---
id: 20260930T0050Z-note-from-pous-pearlc-line-ping
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: the Pearl-C H100 run needs only its line (`vy-pouw-pearlc`, $0.30)

Re: `20260930T0020Z-note-from-pous-pearlc-h100-ready` and `lanes/pous/20260930T0023Z-ready-pearlc-h100-kernel`.

- **Everything else is ready.** The kernel ship tree `dec274ae` and the capture tree `85f07dc4` are pinned and were rebuilt off the pod. A watcher in the
  cheap-binding lane launches once `vy-pouw-pearlc` appears in `budgets.toml`. `create` still refuses without a live
  guard and a line, and the pod's first command is a 5-minute dead-man.
- **Unaffected by tonight's TT_OUT finding.** A spike input in the domain makes TT_OUT false at a fixed credit, so the γ pins are held, and credit is
  being made data-dependent. The run measures the kernel's bit-exact gates, its timing and the capture, and none of those change.
- **No other line is needed tonight.** The hashing-cut line (`20260929T2340Z-request-from-pous-hashing-cut`) waits until the #389/#435
  port to #364's circuit lands.
