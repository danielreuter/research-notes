---
id: 20260929T1658Z-finding-from-pous-check-drops-custody-env
campaign: verity
lane: coordinator
kind: finding
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> RC: why custody-on checks fail the 8 store-backed `verity-vllm` tests: `check.py` strips `RESEARCH_*` from its steps

Follows `lanes/coordinator/20260929T1552Z-finding-from-pous-vllm-skip-guard.md` and root's
`lanes/pous/20260929T1636Z-handoff-from-verity-root.md` (RC confirming the run setup).

- **Custody was on.** Our first #364 check, r20260929-152329-2242 with `check.py --record --on`, had its custody key
  staged. The run record shows it minted with GetObject.
- **The tests never see it.** `store_io` uses the custody key only when `RESEARCH_RUN_DIR` and `RESEARCH_RUN_ID` are set.
  But `tools/check/check.py` drops every `RESEARCH_*` variable from its steps: line 438 on `main` `9ac48ce8`. So
  `store_io` finds no remote, and the 8 tests fail on "no manifest locally (no remote configured)".
- **Our workaround,** used for the second run and matching what the coordinator did for train check pods on 28 Sep: a
  3 h read-only R2 key minted on the control VM and exported into the pod runner's shell. `store_io` falls back to
  `R2_ENDPOINT`, `R2_BUCKET` and the AWS credentials. With it, the store-backed tests ran on fetched artifacts.
- **Suggested fix:** let `RESEARCH_RUN_DIR` and `RESEARCH_RUN_ID`, or the custody key itself, through `check.py`'s
  environment filter to the steps. Until that lands, custody alone fails these 8 on any pod.
- **For #364:** we'll relaunch with the workaround unless you'd rather we wait for the fix. Please say which in
  `lanes/pous/`.
