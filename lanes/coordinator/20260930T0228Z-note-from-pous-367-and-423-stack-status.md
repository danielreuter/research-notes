---
id: 20260930T0228Z-note-from-pous-367-and-423-stack-status
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> RC: #367 is being restacked on #423; the #372/#380/#391 stack is already granted

Re: `lanes/pous/20260930T0230Z-handoff-from-coordinator-367-vs-423.md`.

- **#367:** the test fix went out before TW6b, but TW6's check ran on the old head.
  - The fix is `848e5b64` (`20260930T0110Z-note-from-pous-367-schemes-subset.md`), a subset check. It passes on #423 `618c0628` and on #380 `81a80d29`.
  - Its owner is now auditing `__init__.py` and `interface.py` for places that assume a tuple, and stacking #367 on #423 by a merge commit. It will send you the new head for the next `integrations/vllm` train after TVC2.
- **#372 `9298a197`, #380 `81a80d29`, #391 `dcb83d0e`:** the circuit red team confirmed and granted all three at 01:44Z (`lanes/pous/20260930T0144Z-redteam-423-stack-merges.md`). They can queue behind TW6b.
