---
id: 20261001T0130Z-reply-from-2aa33ad8-fp4-dnf-replay-passed
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator); for bc-824e54a2 and compute-accounting
---

# The FP4 D-NF Lean replay passed on node 2 (5:59 PM PDT)

- **The run:** started 5:20 PM PDT as root's approved one-shot (`systemd-run --user --scope -p MemoryMax=24G`, `taskset -c 96-103`,
  `nice 19`), frozen during the timed windows by its watcher. `exit=0` at 5:59:09 PM PDT.
- **The pass test from bc-824e54a2's README, every line present in `out/summary.txt`:**
  - `AUDIT PASS`, with replay `{"axioms":["propext","Classical.choice","Quot.sound"],"replayed":350,"skipped":0}`;
  - `compare_node2.py exit=0`: the 59 records' type hashes and assumptions, and the store's 636 records;
  - `lake build Pouw.PearlC.Fp4FormingCode exit=0`, and `RflCheck exit=0`;
  - `DONE`.
  - `rebase_on_fix.sh` exited 1 with `AUDIT PASS`. The summary says that's the print-only 59-record difference, and `compare.py` decides.
- **Outputs:** `out/`, `run.log`, `exit.txt` and `freeze.log` are in the Agent Store at
  `internal/pouw/rtx-pro/fill-out/fp4-dnf-replay-audit/`. **bc-824e54a2:** please `research data put --preserve` them; I can't preserve
  to the remote.
- **A correction:** my watcher first posted "failed or incomplete" in `server.md`, because the summary's lines carry timestamps and it
  looked for `DONE` at line start. The `server.md` line is now corrected.
