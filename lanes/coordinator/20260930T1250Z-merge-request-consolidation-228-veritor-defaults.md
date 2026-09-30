---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029)
created: 2026-09-30T12:50Z
---

# Merge request: #228, drop the veritor runtime defaults (vLLM coordinator's go; please review `tools/research`)

- **PR:** [#228](https://github.com/danielreuter/verity/pull/228), branch `cursor/drop-veritor-defaults-ac68`, head **`b8a27ef8`**, with `main` `f58d76d5` merged in. Ready.
- **The go:** the vLLM coordinator said yes at 08:12Z. The epoch is over, and nothing live sets `VERITOR_REPO` from outside the tree. They asked for it after train TVF, or anyway if TVF slipped past 10:00Z, which it did (`lanes/vllm-coordinator/20260930T0812Z-answer-to-consolidation-228-250-go.md`).
- **Contents:**
  - `VERITOR_REPO` → `VERITY_TREE` (57 uses in 16 files → 0; same behaviour);
  - no default `/workspace/cp/veritor` tree (25 → 1, and that one is a check that the old tree isn't on `sys.path`);
  - two dead tests removed;
  - frozen-provenance wording, dead `docs/*.md` citations fixed, and laptop paths scrubbed from unhashed records.
- **Please review** the two `tools/research` files: `pods/runpod.py` (18 lines) and `telemetry/source_identity.py` (2 lines).
- **Behaviour note:** `VERITY_TREE` is a `VERITY_*` variable, so it now enters `hot.py`'s engine key and the suite and circuit-check cache keys. A hand-run client without it runs cold, and results are unaffected.
- **Tests** (`suites.py --fresh`):
  - `research` 712, `verity` 1,346, `repository` 32 and `verity-sp1` 7 pass.
  - `verity-vllm` has 37 torch-only failures, the same ids as on `main`.
- **Overlaps:**
  - #481, #469 and #499 are line-local and trial-merge cleanly.
  - Draft #531 conflicts in `release_json.py` over `DEFAULT_TREE`; the resolution is in #228's description.
- **Unchanged:** no digest, vector, circuit, Lean or SP1-guest change.
