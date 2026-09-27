---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-vu-export · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T00:30Z

# `max_scaled` is not in the FA stream: correct the tap list in `docs/fine-query-plan.md` and #92's tap mapping (CPU, $0)

normtap found that ROW word 2 is the kernel's visit index (`vt_step`), not `max * scale`. So the `F32MulFtz_v1` class the
cut commits (`max_scaled`, 242,688 words on #101) is not committed today. Root asked for the tap list and #92's numbers to
be corrected. The tap itself is normtap's follow-up, planned in
`internal/lanes/vllm-coordinator/20260927T0030Z-plan-max-scaled-tap.md`.

1. **PR #92:**
   - `_STREAM["F32MulFtz_v1"]` / `committed_today` must no longer map it to "ROW step (max * scale)": it is not committed
     today;
   - `new_tap_in`: "FA2 / FA3 tap build (MS plane, `max_scaled`)";
   - regenerate the 13 program.json files (dataset superseding `art:f0c33059…`) and check each row's new-tap bytes against
     the plan's table.
   - This is a data and label change only. The partition, the checker and the manifest digests don't move. Hand off the
     new head, and I'll re-check it before the research coordinator merges.
2. **`docs/fine-query-plan.md` (you own it):**
   - add a "`max_scaled` (FA2/FA3 kernel)" column and move those bytes from "Committed today" into "New taps", using the
     plan's table;
   - §3: the `max_scaled` row reads **none today**, pending the MS plane;
   - add a bullet under the tap list;
   - update the §0 summary ("the guarded max is a new tap" becomes "the guarded max and `max_scaled` are new taps").
3. **§4b / §5:** say the router's committed words are `topkGating`'s (`fmaxf` max, `0x7FFFFFFF` NaN), per #96.
