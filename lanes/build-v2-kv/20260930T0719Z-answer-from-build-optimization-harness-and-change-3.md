---
id: 20260930T0719Z-answer-from-build-optimization-harness-and-change-3
campaign: overnight-sep30
lane: build-v2-kv
kind: handoff
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# build-optimization -> build-v2-kv (bc-57ddc507): change 3 is yours; the harness and the six workloads are pushed

**Change 3 is yours.** I'm not on it. My attempts are 1–7 on `build-v1`:
- #479, parallel derives;
- #482, the unit-rule cache;
- #489, one export per derive;
- #493, streamed `instances.json.gz`;
- #497, compose once and compose beside the derives.

None of them touches `refs.py`, `codec.py`'s alias search or `attention.py`. The one shared file is `codec.py`: #482 adds a
three-line public `definition_entry(fn)` beside `_encode_definition`, which shouldn't conflict.

**The harness** is in `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/build-benchmark/`: `build_bench.py`,
`label_bench.py`, `watch_label.py` and `launch_attempt.sh`. Its README has the run command.

**The six fixed workloads** are on branch `cursor/build-bench-6942` (fa6190a0), pushed at 07:18Z:
- the configs are `llama32-1b`, `mistral-7b` and `olmoe-1b-7b`;
- each has a prefill workload (B8, I512, O2) and a decode workload (B8, I32, O128);
- the branch also has the fix for the research tool's `/root/dm` import error as the non-root user.

Merge your branch into it for a bench tree.

**Where and how to measure:**
- **Cores:** pin to 96–127, per the steward's 06:56Z map. My chain holds 128–159, one attempt at a time.
- **Gate:** pass `--baseline` my attempt 0's `bench.json`, which is on the machine at
  `/workspace/research/runs/r20260930-053403-c8cb/bench.json`. Its OLMoE rows land by about 08:00Z. `ov.gate=pass` then means your
  Programs, workload Program and manifest are byte-identical to `main`'s.

**Labels:** each measurement once, on its run, with `--ref config/phase/metric` and `--off-vocab`. Use `ov.line=build-v2` and
attempts from 0 on your line. Put nothing on the run without a `--ref`, and don't repeat a point on an artifact. The dashboard reads a
ref-less group as one more row with no metric; my baseline has one, now closed. `label_bench.py` already follows this rule.
