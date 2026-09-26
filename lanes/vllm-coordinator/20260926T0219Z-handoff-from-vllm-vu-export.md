---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T02:19Z
---

# Handoff from vllm-vu-export: VU export default-on in `verity-vllm row` (Daniel's request), for your merge and the epoch (02:19Z)


Daniel asked for the exporter to run by default in the row scripts, so every passing run produces its data. It's on PR [#42](https://github.com/danielreuter/verity/pull/42) at head `8c4d381d`. I haven't touched the epoch lane's branch or pods; getting it into the epoch is your call.

**Behaviour changes**
- `CommitConfig.vu_export` (`--vu-export`, env `VU_EXPORT`) defaults to `1`. `verity-vllm row`'s Commit command then gets `--vu-export-dir`, and `VU_EXPORT=0` opts out.
- The export goes to `$RESEARCH_RUN_DIR/vu-export/<row>` under a research run, so `--custody-r2` preserves it with the run. Outside a research run it goes to `<row dir>/vu-export`. A `provenance.json` there records the row key, research run and source SHA.
- Default limits: 256 VUs per family, a forked pool of 8 workers (the replay's pre-warm and `gc.freeze` pattern), and a 600 s budget. It runs serially when the store is device-retained.

**Record-neutral, with two effects**
- It runs only after pair 0's replay PASSes and its value source is filed, and it never reaches a verdict: no Program, manifest, root, verdict or allowlist changes.
- It does add Commit wall time: up to about 600 s plus the fork. #101 took 823 s serially, 583 s of it in the Gumbel sampling rows, and should be under 150 s with 8 workers.
- It adds data per row: about 190 MB for #101. That sits in the run dir, so custody uploads it.

**Not covered:** TP rows. `pipeline/tp/commit.py` has no hook yet.

**Tests:** head `8c4d381d` on vyv-vu-export-g1, run `r20260926-021658-3bcd`: `tests/pipeline/test_vu_export.py`, `tests/lint`, `tests/check/test_sampled_replay*.py`, `tests/pipeline/test_cli.py` and `tests/pipeline/test_row*.py`, with 0 failures.

**Asks**
1. Merge #42 through the research coordinator when it suits you.
2. For the epoch: cherry-pick `8c4d381d` plus the exporter commits, or rebase after the merge. Only you can decide whether the epoch's recording tree may change mid-sweep. The change is digest-neutral, but it does change the tree identity.
3. Extend the 03:00Z vyv deadline for `vyv-vu-export-g1`. #4's Commit has been running since 01:50Z and uses 84 GB, well under the 188 GB on the pod. I expect it to end around 03:15Z.
