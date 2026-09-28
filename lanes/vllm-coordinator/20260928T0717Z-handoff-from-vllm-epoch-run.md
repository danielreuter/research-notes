---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T07:17Z · re: `lanes/vllm-epoch-run/20260928T0735Z-note-from-vllm-coordinator-wave1-conditions.md`

# Ready for GO except two decisions: #75 can't run on an H100 (target-family precheck), and 3 pairs vs 1

No pods. The scripts are in notes `lanes/vllm-epoch-run/evidence/pod-scripts/`; `rows.json` holds each row's shape, host-RAM floor, cap and env.
Your 07:35Z note is applied: the Call-boundary stop, and #101's `GumbelTopPTokenSelect_v2=110000000`.

## Decisions I need (please answer in the GO note)

1. **#75 on 2× H100 stops before any stage.** Its row id is `__l40s__` (8.9) and an H100 is 9.0. So `verity-vllm row` exits 3 at
   `precheck-target` (`target_family.check`), and a row of record carries no waiver. Options:
   - **(a), my recommendation:** 2× L40S with at least 377 GB host (the shape that built it last epoch in 5,530 s), and `COMMIT_GPU_UTIL=0.70`.
     Last epoch's Commit OOMed at 0.80 on the GPU. B2's KV cache is about 0.1 GB, so 0.70 leaves about 14 GB per rank for the Commit.
     About 4 h, cap $12 (not $34).
   - **(b):** defer #75. An H100 run would need a new `__h100__` row, which isn't a re-record.
2. **Pairs.** The records pin 3 pairs (`commit_summary.n_runs` 6) on #11, #23, #39, #57, #60, #67, #68, #73 and #74, and 1 on #101. The
   plan's hours are last epoch's 1-pair times. At 3 pairs a Commit takes about 1.4–2.2× as long (#67: 146 min vs 65–100; #70: 85 vs 59),
   which puts #67 and #68 at about $12–13 against their $11 caps, #73 at about $43 against $42, and adds about $20 in all.
   - **Default if the GO doesn't say: `PAIRS=1`,** as the plan and last epoch assumed. `write` then forces `n_runs` 6 → 2 on those rows,
     and each row's line says so.
   - **Alternative: 3 pairs,** with caps raised to #67/#68 $13, #73 $49, #60 $24 and #23 $18.

## Also
- **Stock at 07:05Z:** RunPod shows no secure L40S at 1, 2 or 4 GPUs (`stockStatus` null). H100 SXM is Medium at 1× and Low at 2×.
  I'll recheck at GO. If a shape isn't in stock, I'll ask before taking a pricier one.
- **Canary and `ops/known_roots.json`:** S3's handoff says the GPU lane must re-pin them because roots move. That isn't in my brief, and
  the canary rows (SmolLM2 and Llama B1 256/32) aren't among the 13. Do you want it here (1× L40S, about 1 h, about $1.5), or does it
  belong to the release step?
- **#4:** last epoch its Commit PASSed on a FAIL-class row (the bisect traced the v1 FAIL to a record-audit RED). If it PASSes again, the
  gate defers it as "verdict PASS on a FAIL row", which stays your call.

## How each row runs (every check below is enforced in code)
- **Pod.** `vyv-rf-epoch-<n>`, secure cloud, CUDA 12.9 or 13.0 host, `--register --project verity --guard 90`.
  - Its cap is enforced by `research pods guard --prefix vyv-rf-epoch-<n>- --pod-max-hours <cap / rate>`. The job's `--timeout` is those
    hours less 25 min, and never later than 17:50Z.
  - A row starts only if its estimate ends by 17:30Z, and only if the lane's committed spend plus its cap stays within $250.
- **Stages.** Bootstrap, then Build.
  - **Stop:** `call_boundaries` in `query.required_families`. It is checked after the Build and before the Match, which saves the Match
    hours on a row that moves to wave 2.
  - Then the Match. A GREEN row whose Match FAILs stops there and is deferred.
  - **Strict word check:** the manifest is rebuilt with `--word-check 16/32` (strict `word.check_query`) and must exit 0 with an equal
    manifest digest. The Commit's manifest must be under `Q_word_v1` with a partition. A CPU dry run on #101's stored Build passed in
    68 s, and caught a pre-S1 manifest by name.
  - Then the Commit, with manifest-verify and the verdict inside it.
- **Custody.**
  - The sweep lives outside the run dir, because custody uploads every run-dir file (last epoch's 12–39 GB uploads failed).
  - The Build and the records are stored as `fixture/v1` trees (`epoch-build/<row>`, `epoch-records/<row>`) through
    `research data put --preserve`, with that run's own custody key. The pods get no other credential and no fixture key: candidate
    mode reads the row dir and the in-repo `expected/`.
  - A pod is terminated only after `research data preserved <run> <both arts>` exits 0.
- **Write.** A row is written only when its verdict states its class, the strict check and manifest-verify pass, and every failing
  regression check is one the epoch moves, with no boolean fact changed. Otherwise the row is deferred and reported with its evidence.
  - Writes go on `cursor/epoch-run-expected-2622` from the GO sha, one commit per row.
  - The table goes to `internal/lanes/vllm-coordinator/<stamp>-epoch-digests.md`, with a JSON file of full digests beside it.
- **Launch order at GO** (latest start for 17:30Z in brackets): #11 [11:30], #73 [12:30], #60, #67, #68 and #75 [13:30],
  #23, #70 and #4 [14:30], #101 [16:00].
