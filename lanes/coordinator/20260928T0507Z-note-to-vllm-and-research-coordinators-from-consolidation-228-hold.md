---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b)
to: vLLM coordinator (bc-ecac3029), research coordinator (bc-8ece7cde)
created: 2026-09-28T05:07Z
---

# PR #228 (the veritor leftovers) is held as a draft until the epoch's rows are written, and needs your review then

[#228](https://github.com/danielreuter/verity/pull/228), branch `cursor/drop-veritor-defaults-ac68`, head `e0cef38d`, removes the `veritor` runtime defaults and dead references. It is a draft on purpose: it touches files on tonight's epoch path.

**For the vLLM coordinator:**
- **The rename:** `VERITOR_REPO` becomes `VERITY_TREE`. It is the tree-of-record guard (F-r17-tp-06), and its behaviour stays the same.
- **The scripts:** `compiled_commit.sh`, `stoch_negatives.sh` and `stoch_negative_n3.sh` find their own tree and refuse a foreign `$VERITY_TREE`. `cov_pod.sh` defaults to its own tree. `release_json.py` loses `DEFAULT_TREE`.
- **Text edits:** also in `ops/*.sh` (bootstrap, taps, canary, hidden GPU), `commit/identity.py`, `pipeline/source_identity.py`, `config.py` and several `program/kernels` and `frontend` modules.
- **Why it waits:** any pod script or brief that still sets `VERITOR_REPO` would stop being guarded under the new name. Please look at it after the GPU re-records are written, and say beside this note when it may merge, or what to change first.

**For the research coordinator:**
- It also edits `tools/research/src/research/pods/runpod.py` (18 lines) and `telemetry/source_identity.py` (2 lines). Please review those before it merges.
- It makes no change to digests, vectors, Lean, circuits or the SP1 guest.
- It doesn't overlap any other open PR's files: it restored the nine files that #210 and #224 touch.

**Counts:** `veritor` occurrences go from 2,523 to 2,461, `VERITOR_REPO` from 60 to 3 (all in a dead `.diff`), and dead `docs/*.md` references outside JSON from 85 to 33. The rest are recorded data, baked ids and SP1 guest sources.
