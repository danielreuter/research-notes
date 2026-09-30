---
id: 20260930T2230Z-report-stage-prove-split
campaign: verity
lane: proofs-rows
kind: report
status: final
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), worker of @proofs (bc-8416bc72)
---

CHECKPOINT none (23:00Z) [final] Stood down per 2252Z. I missed it on the first pass: the 73-sweep-shape.sh swap (56a6066e) was live in backend-sweep-2's tree from 3:54 to 3:56 PM PDT, then restored from .bak (now bd7c7e63, no .bak left); no run started on it. Backfill Job nd-proofs-rows-c38abf8279-prover-b-0 was deleted before admission. tmux proofs-rows-split had already exited on its own; I killed nothing. Removed node-1 /workspace/jobs/proofs-rows/{cache-a,cache-b,flock} (0.43 GB) and {summaries,sweep} (1.8 MB), keeping measure/ and tools/ (88 KB), plus my node /tmp scratch. Earlier completed Job 75532431fe was left in place (Complete, no GPU). Backlog: note:20260930T2257Z-handoff-from-proofs-rows-73-hardlink-prune (the diff; test freed 0.08 GB with hashes unchanged; prune dry run found 31 entries, 3.06 GB; PRUNE=1 on the branch frees nothing as written).
CHECKPOINT afb4bd35 (22:25Z) [open] split built; CPU stage byte-identical to GPU stage, saves 201 s GPU per cache miss; its one GPU chunk split-prove-f1e4d147-m1 queued in backfill since 3:13 PM PDT; no feeder (note:20260930T2230Z-report-stage-prove-split)
# proofs-rows: the stage/prove split works and stages byte-identical statements on CPU; stood down before its GPU chunk ran

Replies to `note:20260930T2142Z-handoff-from-proofs-replan-stop-rows-do-stage-split`,
`note:20260930T2147Z-handoff-from-proofs-gumbel-unit-reporting` and `note:20260930T2153Z-handoff-from-proofs-name-the-question`.
Question: "does staging a chunk in a CPU-only job cut GPU-held minutes, with byte-identical proofs?"

**1. Feeder.** None was started: no tmux `proofs-rows-feed`, and no next-coordinate items. Nothing to stop. The brief's scope
doesn't hold anyway: Llama-3.2-1B's only GEMM coordinate after K=2048 is K=8192 (#1936), which node 2 now covers.

**2. The split.** `tools/73-sweep-shape.sh` is backend-sweep-2's at `70e99f57`, plus:
- `MODE=shape STAGE_ONLY=1`: `MODE=stage`'s exact statement on CPU. It writes a marker with the files' sha256, via `tools/stage_mark.py`.
- `REQUIRE_STAGED=1`: the GPU job exits 3 before the prover when there's no marker, and after it when the job staged the
  shape itself or proved other bytes.
- The split's SUMMARY fields.

Recipes: `note:20260930T2225Z-handoff-from-proofs-rows-stage-prove-split-recipe` (node 2) and
`note:20260930T2225Z-handoff-from-proofs-rows-stage-prove-split` (sweep2-feed).

**3. Measured** (K=2048, #1551, node 1, prover `e484a335…`; driver `tools/split_measure.py`, tmux `proofs-rows-split`):

| | GPU held before the prove | GPU held per statement | Statement files |
|---|---|---|---|
| current way, cache missed (r0, `r20260930-210621-2a46`) | 231 s | 8.23 s | reference |
| current way, cache hit (r5000, `r20260930-214647-a70b`) | 30 s | 8.40 s | r0's |
| split: CPU stage job (`r20260930-220702-2e96`, gpus 0) | 0 | none | identical to r0's (sha256 of all three) |
| split: its GPU chunk (`split-prove-f1e4d147-m1`, 10 statements) | queued | queued | queued |

- **The CPU job:** 198 s of staging on 2 CPUs, 8.8 GB peak, 227 s job. It wrote the same cache key as r0's GPU job (`cdef5bd8…`).
- **Saving:** 201 s (3.4 GPU-min) on each chunk that would miss the cache (every tree change), and 0 on a hit.
- **The bigger cost:** the loopback verifier's round (about 6.5 s of `wait_s`) runs in series in the GPU job, and the prove is
  1.02 s. The K=2048 row is therefore about 115–117 GPU-held hours, not 14.2.
- **The GPU chunk** (backfill) has waited since 3:13 PM PDT. All 8 GPUs are in use (`deployments-gpu` 5 of 5, `provers` 3 of 3),
  with 16 `deployments-gpu`, 2 `provers` and 1 earlier backfill workload ahead. When it runs, the driver writes
  `/workspace/jobs/proofs-rows/measure/split-m1.json`. It holds GPU-held seconds, before-prove seconds and the statement digest
  against r0's (`2b7bd0d9…`).
- **Withdrawn:** I had also queued a current-way GPU chunk, `current-f1e4d147-m1`, before reading Daniel's 2:53 PM PDT rule. I
  deleted its Job at 3:14 PM PDT, before admission. So `log.jsonl` shows its submit with no end.

**4. Gumbel.** In `MODE=sampled`, the SUMMARY lists `sampled_units`, `units_proved`, `units_not_proved`, `units_excluded` (name and
why) and `fully_provable`. Tested on the b8 top-p deployment's draw, with synthetic results. The coordinator's recipe, with the
greedy `TokenSelect` caveat: `note:20260930T2225Z-handoff-from-proofs-rows-gumbel-unit-reporting`.

**Labels:** `label`, `question` (off-vocab: `note:proofs-rows/20260930T2230Z-friction-question-label-not-in-vocab`) and `note` on
the stage run. Node 1 has no store remote, so the GPU chunk's run must be labelled from a VM with write-through. When
`measure.log` says `measured`:

```bash
RUN=$(research pods ssh vy-nebius-1 -- jq -r .run /workspace/jobs/proofs-rows/summaries/split-prove-f1e4d147-m1.json)
research data label $RUN label "measurements on #554's draft prover key; the 4×4 tile statement is not yet reviewed: not verified table rows" --by proofs-rows
research data label $RUN question "does staging a chunk in a CPU-only job cut GPU-held minutes, with byte-identical proofs?" --by proofs-rows --off-vocab
research data label $RUN note "proofs-rows stage/prove split: the GPU chunk (10 statements, REQUIRE_STAGED=1) of shape f1e4d147 on r20260930-220702-2e96's CPU stage; see /workspace/jobs/proofs-rows/measure/split-m1.json" --by proofs-rows
```

**Node 1 state (final, 3:59 PM PDT):**
- The GPU chunk never ran. I deleted Job `nd-proofs-rows-c38abf8279-prover-b-0` before admission, at about 3:54 PM PDT. tmux
  `proofs-rows-split` had already exited (last log line 22:52:42Z); I killed nothing. `split-m1.json` will not be written,
  so the labels recipe has no run to label.
- `/workspace/jobs/proofs-rows/` keeps only `measure/` and `tools/` (88 KB; 73 at `d349d1e2`, the measured version).
  I removed `cache-a/`, `cache-b/` and `flock/` (0.43 GB), `summaries/` and `sweep/` (1.8 MB), and my node `/tmp` scratch.
- Earlier chunk Job `nd-proofs-rows-75532431fe-prover-b-0` is left as it is (`Complete`, no GPU held).
- `/workspace/jobs/ready/proofs-rows/` (empty) and `/workspace/research/trees/proofs-rows/` (the tree) are unchanged.
- No `art:` ids: node 1 has no store remote, so the runs are cited by run id only.

**The 73 swap into backend-sweep-2's tree:** it was live from 3:54 to 3:56 PM PDT. I restored it from `.bak` after reading the
stand-down, and the file is `bd7c7e63` again, with no `.bak` left. No run started on it. The diff is backlog:
`note:20260930T2257Z-handoff-from-proofs-rows-73-hardlink-prune`.

**Handoffs:**
- `20260930T2142Z-handoff-from-proofs-replan-stop-rows-do-stage-split.md`: done (sections 1–3).
- `20260930T2147Z-handoff-from-proofs-gumbel-unit-reporting.md`: done (section 4).
- `20260930T2153Z-handoff-from-proofs-name-the-question.md`: done (the question line above, and the labels).
- `20260930T2227Z-handoff-from-proofs-disk-discipline.md`: scratch deleted (0.43 GB); my stage run predates it.
- `20260930T2228Z-handoff-from-proofs-urgent-dedupe-script-first.md`: superseded by the 2230Z cancel, then by the 3:36 PM PDT go.
- `20260930T2230Z-handoff-from-proofs-cancel-dedupe-script.md`: followed until the 3:36 PM PDT go.
- `20260930T2241Z-handoff-from-proofs-one-swap-with-gumbel.md`: built into the swap; now backlog.
- `20260930T2244Z-handoff-from-proofs-swap-deletes-sampled-classes.md`: dropped, per 2246Z.
- `20260930T2246Z-handoff-from-proofs-rebase-on-live-script.md`: rebased on `bd7c7e63`; now backlog.
- `20260930T2252Z-handoff-from-proofs-stand-down.md`: done (swap restored, Job deleted, scratch removed, FINAL written).
