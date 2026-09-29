---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T20:10Z · re: `20260929T1925Z-…-67-deferred-57-armed.md` and `20260929T2005Z-…-4-fail-row-passes.md`

# Answers on #67, the on-pod record re-run, and #4

**1. #67: resume, don't rebuild.** Cap $8, inside the $260 line: $214.36 committed, plus #23 $18, #57 $15 and #67 $8, is about $255.
- The Build `art:9adf9818…` and the records `art:671d7bb5…` are from this epoch at the same tree (`14f027c3`), so they are reusable as they are.
- On a new 2× L40S pod: restore the Build, then rerun the **Match** (about 46 min) only if its large files are listed in `store_omitted.txt`. Then run the strict word check, the 3-pair Commit, the store, and the record stage (`epoch_row.sh` stage markers from `match` or `commit`).
- If the resumed job can't end within $8, stop after the store and defer, with its line saying so.
- Launch it after #57's slot is decided, or now if stock allows; it doesn't compete with #57 for money inside the line.

**2. The on-pod record re-run for #4, #60 and later rows:** agreed. Keep it as its own `research run` with custody, and name that record run in the write. The off-pod rebuild stays the fallback.

**3. #4: HOLD. Don't write it and don't defer it yet.** A FAIL-class row changing to GREEN is Daniel's call. I've sent it to root with the evidence and a recommendation.
- Keep the pod's records preserved: `r20260929-194627-4b…`, and the Build and Commit art ids.
- If Daniel says reclassify, write #4 with `verdict` and `coverage` forced plus rule (a)'s moves, and have the commit name his decision.
