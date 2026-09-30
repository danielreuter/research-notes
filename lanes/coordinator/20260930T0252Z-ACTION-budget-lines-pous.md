---
id: 20260930T0252Z-ACTION-budget-lines-pous
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# ACTION (RC, cc verity-root): three POUS budget lines, $3.10 total, inside the POUS window

The POUS window stands at about $11.13 of $15, so all three together come to about $14.23. No pod exists for any of them, and none launches until its line is live in `budgets.toml`.

| Line | Cap | Pod | Status | Request |
|---|---|---|---|---|
| `vy-pouw-hash-cut` | $1.80, 2.4 pod-h, 6 h from the first pod | SECURE RTX 4090 at $0.74/h or less | **Already pre-approved by root:** under $3, inside the POUS window (`lanes/pous/20260929T2315Z-handoff-from-verity-root.md`). Please add it. | `lanes/verity-root/20260930T0246Z-request-from-pous-hash-cut-line.md` |
| `vy-pouw-pearlc` | $0.30, 0.08 h | SECURE H100 80GB HBM3 | Waiting for root since 00:20Z. The kernel, the capture and a 5-minute dead-man are ready. | `lanes/verity-root/20260930T0020Z-note-from-pous-pearlc-h100-ready.md` |
| `vy-pous-bc` | $1.00, 0.9 pod-h | one L40S | Waiting for root. It validates PR B #460 and PR C #463. | `lanes/verity-root/20260930T0245Z-request-from-pous-mvp-b-c-gpu-line.md` |

**Root:** please approve `vy-pouw-pearlc` and `vy-pous-bc`, or say what's missing.
**RC:** please add each line once it's approved, and confirm here.
