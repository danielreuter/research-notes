---
cursor:
  subagentId: "bc-340e9d74-a552-5f6a-b63d-a5e3ca84320c"
---

lane: vllm-coordinator · kind: handoff · from: vllm-serving-view (bc-340e9d74) · created: 2026-09-27T04:59Z

# Serving view done, and #4 and #101 record Builds stored. Pod terminated at 04:57Z, about $2.05. PR #108 is merge-ready.

## Pod: `vyv-rf-serving-view-g1` (1× L40S secure, $1.09/h), 03:04Z–04:57Z, about $2.05 of the $4 cap. Terminated.

The run was `r20260927-030516-24a5`: Build stage only, at the record run's source `11d453e0`. The record run it reproduces is
`r20260926-035624-a133`.

| Row | Reproduced | Build artifact (PRESERVED) |
|---|---|---|
| #101 | request Program `ccc21347…` and manifest `90f81868…`, both equal to the record (build 109 s) | `art:9cb3a4df0eb3e23b98783651eed56c087df1cf9d84ff8d7c630e20ef8695a4d0` (33 files, 17.5 MB) |
| #4 | all 16 recorded request Programs (r0..r15); step `476536f3`, workload `80163555`, manifest `3bbd860f…`, 246,503 identities, all equal to the record's build line (build 4,476 s) | `art:8578b716ed8c0653824360d3cf4a4a1493c4336b171000830cb1fbdeb5ccb5f8` (161 files, 841 MB) |

- #4's extra `build_request` digest `aadcc238…` is the LP=1024 / T=127 configuration-shaped component, not a request's Program.
  `program_graphs.py` and the view read only the `build_request_LP*` directories.
- Both artifacts are the Build directories as written; sha256 of every file equals the pod's.
- **Program graphs** from the record Builds, with `param_inputs`, are `art:983c79f84d68821fd07e60d7cad4f88446d88906b8080fc2ec050af420d528c2`
  (#4 made on the pod, #101 on CPU from the same Build). `catalog` and `with_word_rules` are not applied (`regen13 --finish` does
  both). This is the export lane's input for the #4 / #101 redraw.
- **The pod graph step for #101 exited rc 1.** The cause was my `main` tarball, which lacked `integrations/vllm/workloads/`. The Build
  was unaffected; I fixed it on the pod before #4's graph ran.

## View: `internal/datasets/serving-view/` = `art:10eeb72d03a2054ed218f4fd6d2af12a96e05cc0130172d36c6e36b80962027e` (PRESERVED)

Contents: a README for the docs-site worker, `index.json`, #101's view and site tree on the record Build, and #70's TP-rank
exercise (2 of its 8 request Programs, both ranks).

Every check on #101 passed:

- 46,654 Calls, each in exactly one of 4,736 leaves;
- gates equal the address-map span (18,805,632,558);
- all 32 of the chronology's recorded step ranges agree;
- 260 of 260 group ids agree, and so do Q_word units (273,995,039) and committed words (64,169,215), against the graph from the
  same Build;
- the KV-cache edges are exactly `rotary_emb → attn` (K) and `qkv_proj → attn` (V);
- there are two structures: prefill, and one shared by all 31 decode steps.

On #70, 167,396 Calls and 4,752 collective edges (paired by `peers_<k>[lo:hi]`) gave 0 word mismatches.

## Merge-ready: [PR #108](https://github.com/danielreuter/verity/pull/108), `cursor/vllm-serving-view-320c` @ `17e9df25` (base `main` `fa662029`)

- **Change:** a new `integrations/vllm/verity_vllm/pipeline/serving_view.py`, new `tests/pipeline/test_serving_view.py`, and one
  CLI entry (`serving-view`) in `pipeline/cli.py`.
- **Tests:** pod run `r20260927-033638-e4e7` (PRESERVED): 115 passed, 1 skipped, 0 failed. It covered `test_serving_view`,
  `test_program_graph`, `tests/lint` (P8 and P10 clean), `test_cli` and `test_sampled_replay`.
  - The earlier run `r20260927-033325-c954` failed P8 (the literal "Sampler") and P10 (`serving_view` was 204 lines). `17e9df25`
    fixes both.
- **Did not change:** no Program, manifest, digest, Definition, query or partition; no allowlist grows. The partition checker
  doesn't apply, because nothing restates a Definition or partition. The view reads Q_word via `query.word.unit_rule` and changes
  nothing in it.

## Found, not fixed

- **`--custody-r2` preserved only the run's `evidence/`** (plus the record and telemetry), not `builds/` or `program-graphs/`. Any
  lane that relies on custody for Build outputs has to `research data put` them from the VM before terminating, as I did here.
- **`main`'s regression record for #101 still pins the r19 Program `079ee0a8…`**, while the headline record is `ccc21347…`
  (`11d453e0`). A Build of #101 at `main` has not been tried.
- **A lane's checkpoints all append to its first report file**, whose name keeps the first stamp
  (`20260927T0256Z-report-vllm-serving-view.md`). A sweep that reads the filename sees the lane as stale.
