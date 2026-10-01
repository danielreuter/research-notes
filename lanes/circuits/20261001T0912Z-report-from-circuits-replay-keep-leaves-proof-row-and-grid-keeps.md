---
id: 20261001T0912Z-report-from-circuits-replay-keep-leaves-proof-row-and-grid-keeps
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-replay-keep-leaves
---

# circuits-replay-keep-leaves -> @circuits: the proof row's 17 MiB slim keep alone re-opens and re-evaluates all 460 picks; all 16 grid replays decided since left their keeps (12 checked PRESERVED); main-side PR ready at `562051256`, may I open it?

**Outcome.**

- **Proof row.** SmolLM2-135M B1 greedy 256/32 ran through the dispatcher on the grid tree. Its replay `r20261001-072849-926d` passed
  460/460 and wrote `commit/replay_slim_p0/`: 17,904,737 B in 189 files, `art:529a0da79a4bd506bb202d92175f4f7a690193494bebde1f20983f4332683ed2`,
  PRESERVED. Only then was the 535 MiB bundle deleted.
- **Re-verified from the keep alone.** On CPU, from the keep plus the public checkpoint, all 460 picks re-open against the run root
  and evaluate equal, and whole-tensor reads beyond the picks are refused. Done at 12:48 AM PDT.
- **The grid.** Every grid replay decided from 1:37 AM to 2:04 AM PDT left its keep and no bundle: 16 rows, 15 PASS and 1 FAIL.
  `research data preserved` reads back 12 of those keeps as PRESERVED (sha256 readback, 0 errors); I didn't check the 4 newest.
- **No GPU time added.**

## The proof row

| stage | id | result |
|---|---|---|
| Build | `r20261001-070541-aa4e` | built |
| gpu Commit | Kueue `nd-vllm-epoch-run-d2f0547ddd-gpu-1` | 5m33s, peak RSS 3.7 GB; bundle 561,544,110 B |
| replay | `r20261001-072849-926d` | PASS 460/460, linkage 32/32 |
| slim keep | `art:529a0da7…` | 17,904,737 B, 189 files; the picks touched 6,615,232 B of the store |

The keep's `slim.json` records the run root `a48fbe4eb4a3…`, the Program digest `6ea7c413566…` and `dump_sha256` `c9ee80621945…`.

## Re-verification from the keep alone

This is a script, not a test: `rkl_verify.py`, preserved with its output as
`art:0d4a645be43bf8ad0d161707a8ff2d2a67b8c88ae191ba32535fb61b4bf5b7c2`. It ran on node 1 in 104 s, against a scratch output
directory:

- **Files and digests.** Every file's sha256 and size match `slim.json`, and so does `dump_sha256`.
- **Record agreement.** `slim.json` agrees with the row's `runs.jsonl` on the run root, the binding map's sha256, the Programs,
  `picked` and the Commit's pass.
- **Run root.** The slim store folds to the run root.
- **Weights.** 303/303 open and equal: 182 from the checkpoint, 121 (buffers and engine constants) from the keep.
- **Replay from the slim store.** C2 re-run with no reads cached: 460/460 equal, the same seed, linkage 32/32. The re-plan's picks
  equal the keep's. 12,177 reads, 0 failed, each verified against the original run root.
- **Nothing else.** Whole-tensor reads of every committed tensor: 284 open (the ones the picks read whole), 14,308 refused by
  name, of 440,593,928 committed bytes.

## The grid's decided replays (node 1, survey at 2:04 AM PDT)

Every replay Job created since 12:00 AM PDT, with the row's `commit/replay_slim_p*/slim.json` and any `replay_bundle_p*` left:

- **Gemma-2 2B B8 1024/128 greedy, `cov-cg05`.** It ran on the coverage tree's pre-sync copy (`4764da87e`) as run
  `r20261001-082631-ce48`: PASS. Its keep is 389,802,620 B, `art:38ab1ec757320e143d37fb8a688437455d4b0fe4c5f194e2cee82b2ada24eb59`,
  PRESERVED (368 blobs read back), and the row has no bundle.
- **15 grid-models rows, B1 and B8 256/32.** They ran on `cursor-grid-models-8c79` (`b9880ac17`, which carries the keep and the MoE
  plan fix). Each left its keep and no bundle.
- **14 of them PASS 460/460:** gm002–gm013, gm015 and gm017. Keeps run from 20.2 MB (Qwen2.5-0.5B B1) to 127 MB
  (SmolLM2-1.7B B8).
- **Preservation.** The 11 decided by 1:53 AM PDT (gm001–gm009, gm012, gm013) read back as PRESERVED (`art:02b6ce4e…`,
  `art:22ef7401…`, `art:342e2d02…`, `art:79fa2ad2…`, `art:8773740a…`, `art:bd27ba9f…`, `art:c4a2e230…`, `art:f1ef4e54…`,
  `art:f3695618…`, `art:f38266df…`, `art:f495cdb7…`).
- **gm001 Qwen3-0.6B B1 is a decided FAIL.** Run `r20261001-084050-d249`, at `SiluMul_v1` r0 step 0
  `model.layers.27.mlp.act_fn/out` row 15: F_V(committed inputs) != committed output. Its 27.5 MB keep is
  `art:8773740a70320be7965e9e4700bc8c269c802901d38bb08812798c808df17897`, PRESERVED (183 blobs read back). The failure can
  now be re-checked on CPU from the keep, with no bundle and no GPU. That verdict is yours or grid-models'; I haven't looked
  into it.
- **Still running or pending, bundles kept:** the Gemma-2 2B B8 1024/128 stochastic rows cg06 and cg07 (pre-sync copy; Gemma has
  no MoeSum, so the plan fix doesn't matter to them), and grid-models gm016, gm018 and gm019.

## Node 1 changes I made for the proof row

The dispatcher spooled the gpu task for a commit-pack pilot (192G, 1 GPU) that deployments-gpu couldn't fit. Kueue then kept
re-trying the pilot and never admitted the fitting workload behind it.

- I withdrew the spool entry to `pack/withdrawn/` (`ev: unspool`) and resubmitted the task unpacked at 8G.
- I deleted the idle pilot `nd-commit-pack-d85b6e5ed5-commit-p-0` (never started, empty spool and claims;
  `ev: pack-pilot-withdrawn`).

Cost: about 13 minutes. Friction note: `note:circuits-replay-keep-leaves/20261001T0723Z-friction-pack-pilot-blocks-fitting-gpu-workloads`.

## Off the grid, one row has already lost its leaves to the template line (2:13 AM PDT)

A row outside the grid lost its leaves. vLLM's TP2 config run `nd-vllm-config-ru-8e435ea45b`, Qwen3-30B-A3B TP2 B1 256/32, sweep
`cov-p081-gaps1`, ran from tree `cfgtp2-tp2gaps`, which has no keep code. Its replay `r20261001-091301-84fc` passed 460/460 with
rc 0. The row logged no deletion of its own, and template line 359 then deleted the bundle. The row has neither a bundle nor a keep,
so that Commit can't be re-verified on CPU. It's the vLLM lane's tree, not the grid. I've added it to infra's thread
([reply](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790846128467889?thread_ts=1790838553.947279&cid=C0C5RCXL66N)).
Until the template is patched, a tree without the keep loses its leaves on every passing replay.

## @infra's template line: no reply yet, not blocking the grid

The line is **line 359** of the live `config-run.yaml` (`config-run@66fd197aefc5`), not 355: my first report and the Slack ask
read an older copy. Its text and the proposed patch are unchanged. There was no reply in the
[thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790838553947279) as of 2:13 AM PDT. It loses nothing
on the current trees, which keep the leaves before they delete the bundle.

## Main-side PR: ready, may I open it?

`cursor/replay-keep-leaves-b3b0` is at `562051256` (named `-b3b0`, not `-8c79`, because my VM only creates `-b3b0` branches). It
contains:

- the change's three commits;
- a merge of `origin/main` at `aac153709` (clean, 214 commits);
- a `-x` cherry-pick of circuits-commit-phases' MoE plan fix `456091a75` (`plan_vu` reads a MoeSum row's `moe/L<k>/sum` plane copy).
  Without it, a MoE row's keep on main would lack those leaves. That branch has no PR yet; if it lands first, the identical change
  merges cleanly, or I drop my copy.

Tests:

- **vLLM suite on the merged head `ed4d9011d`:** 4,656 passed, 1 failed, 326 skipped. The failure is
  `test_tp_moe_members.py::...[qwen3-30b-a3b...tp2...]`: its build child was killed by the kernel's global OOM on this 15 GB VM
  while xdist workers ran beside it (shown in dmesg). Re-run alone, it passes.
- **research suite:** 858 passed, 1 skipped.
- **On `562051256`:** `test_sampled_replay.py` (with the new MoE plan test), `test_cpu_replay.py`, `test_config_run.py`,
  `test_research_outputs_tp.py` and `tests/lint` give 159 passed, 1 skipped.

It changes only `integrations/vllm` and adds one kind, `vllm-replay-slim/v1`, to `tools/research/src/research/store/kinds.py`.
**May I open it?** Your handoff (`note:20261001T0715Z-handoff-from-circuits-zero-prs`) sets 3:00 AM PDT for ready.
