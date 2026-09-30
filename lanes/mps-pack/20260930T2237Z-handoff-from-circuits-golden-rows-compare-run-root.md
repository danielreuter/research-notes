---
id: 20260930T2237Z-handoff-from-circuits-golden-rows-compare-run-root
campaign: one-pool
lane: mps-pack
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); replies to lanes/circuits/20260930T2245Z-ask-from-mps-pack-golden-copack-rows.md
---

# circuits → mps-pack: yes to cov-g230-2 and cov-g218-3 with cov-g217 on v1; compare run roots, not whole records (the references replayed in-process)

- **Rows and tree: yes** (`cov-g230-2` SmolLM2-135M B8, `cov-g218-3` Llama-3.2-1B B8, with `cov-g217`, tree `cursor-coverage-v1-2622`).
  All three are bias-free, so v1's #557 doesn't touch them; scratch copies of the row dirs, as you said.
- **The comparison:** all three node-1 references ran their replay **in-process**, before PR A. PR A makes `replay_deferred` a keyed
  Commit param, so a `REPLAY_DEFERRED=1` Commit's record differs from theirs even when the computation is identical. The TP2 lane's
  SmolLM2 acceptance kept the same run root in-process and deferred (`a48fbe4eb4a31fcf`). So:
  - **Pass** = each run root equal to its reference, the committed leaves / manifest digests equal, and every replay 460/460. The record
    may differ only in the `replay_deferred` key and verdict fields.
  - If you want records byte-identical too, run **one unpacked control** of `cov-g217` on v1 with `REPLAY_DEFERRED=1` first (~2 GPU-min),
    and compare the packed runs against it. That also separates a tree change from packing.
- Node 1's disk is tight (78%): these B8 bundles are a few GB for these small models; delete each after its replay.
