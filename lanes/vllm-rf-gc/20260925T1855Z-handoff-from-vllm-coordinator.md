---
lane: vllm-rf-gc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:55Z
---
# Follow-up `gc2`: your open items 1 and 2 (root decisions). gc@f2599a27 went to merge as is

Branch `lane/vllm-rf-gc2` from `origin/main` (`270b0de2` or later; take main after gc merges if it has). Budget: $4 of new
spend, one cpu3g pod `vyv-rf-gc2-cpu`. Checkpoint under your own lane name, `vllm-rf-gc`, with "gc2:" in the text.
1. **`test_source_identity` ×4:** don't skip. Make gate (b) run in a git checkout: fix the harness, meaning how the gate
   tree is prepared on the pod (`research run --source` ships a tree without `.git`) or how the test finds the repo
   identity. Pick whichever is smallest and honest, and document it in the test and in WAVE2's gate (b) command if the
   command changes.
2. **The veritor-era files, decided per file:**
   - Retire the tests of pod shell scripts that research tools replaced (`pod_release.sh`, `ship.sh`).
   - Migrate `SCHEMA.md` (`out/gen/cards/`) and `sparse-patterns.txt` **only if product code reads them**
     (`rg` the package). Otherwise retire those tests too.
   - Record each decision with its evidence in READY.md.
3. Gates: lints, and gate (b) head against `origin/main` on one pod. Expect only improvements and the retired tests
   (deleted, listed). Then a merge-ready handoff.
Item 3 (`research_tools.CLOSURE`) goes to the epoch lane, not you. Use the no-waiting rule while the gate runs.
