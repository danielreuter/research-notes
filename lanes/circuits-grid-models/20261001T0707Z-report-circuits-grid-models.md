---
lane: circuits-grid-models
kind: report
created: 2026-10-01T07:07Z
status: final
---

CHECKPOINT b9880ac17 (19:47Z) [final] 12:52 PM PDT: 449 ended on both nodes (434 at 11:30; floor 450), 36 models / 15 families, every failure named; FINAL written; open for circuits: big_cap 14 (1802Z), pack bundle cap (1920Z)
CHECKPOINT b9880ac17 (19:47Z) [final] 12:50 PM PDT: 449 ended on both nodes (434 at 11:30; floor 450), 36 models / 15 families, every failure named; FINAL written; open for circuits: big_cap 14 (1802Z), pack bundle cap (1920Z)
CHECKPOINT b9880ac17 (19:44Z) [open] 12:45 PM PDT: grid 242 ended; pack queue draining (4 of 6 B8 1k claimed); feeder sends again as b8+ in flight drops under big_cap 4; big_cap 14 and bundle cap still with circuits
CHECKPOINT b9880ac17 (19:21Z) [open] 12:23 PM PDT: 6 packed B8 1k Commits blocked by commit_pack's bundle cap (32.9+120>150), handed to circuits (1920Z); big_cap still open; grid 238 ended
CHECKPOINT b9880ac17 (18:55Z) [open] 11:55 AM PDT: grid 236+ ended, feeder idle on big_cap 4 (all 177 eligible B8+), waiting on circuits' yes for 14 (1802Z handoff); leased Commits 5/5 pass
CHECKPOINT b9880ac17 (18:36Z) [open] 11:36 AM PDT: 11:30 count 434 ended (grid 232, epoch 202), 36 models, 15 families, in lanes/circuits 1820Z report; feeder idle (no CPU Build since 11:23) on big_cap 4, still waiting on circuits' yes for 14
CHECKPOINT b9880ac17 (18:17Z) [open] 11:17 AM PDT: grid 223 ended; feeder idle on big_cap 4 (all 177 eligible items B8+), big_cap 14 asked of circuits in 1802Z handoff, no answer yet; 11:20 counts next
CHECKPOINT b9880ac17 (17:54Z) [open] 17:55Z (10:55 AM PDT): grid ended 218. First leased Commit passed (cov-gm398, held its GPU 2m10s of a 292 s pod; replay queued). Packable B8/1k Builds ended and spooled (gm055, 057, 065, 066). Trim reapplied with measured B8/1k peaks (21 items; measured peaks ~half the estimates). Feeder held by big_cap 8 and build_mem_gb 730 (the 10:02 caps); no answer yet on the 450 lever.
CHECKPOINT b9880ac17 (17:38Z) [open] 17:44Z (10:44 AM PDT): leased submissions flowing (6 since 17:27Z). Node 2 back: the 6 stranded grid Builds run there now; 3 more offloaded 17:31-17:34Z, one leased (gm404), whose Commit n2_build.sh will submit unleased (reply note:20261001T1743Z-reply-from-circuits-grid-models-lease-on-n2-built-items). Labeller reads gpu_lease.json (lease minutes or why not leased); restarted.
CHECKPOINT b9880ac17 (17:30Z) [open] 17:32Z (10:32 AM PDT): 10:30 counts posted (note:20261001T1731Z-report-from-circuits-grid-models-counts-1030): 404 ended (grid 213, epoch 191), 36 models, 15 families; projection ~435 at 11:30 (6 grid Builds held by node 2's cutover; caps lowered 10:02 by someone else). lease: self switched on in gm_feed.py at 17:11Z (175 non-packing items via submit_leased.py on the two lease trees, 14 pack); labeller knows the lease trees.
CHECKPOINT b9880ac17 (17:07Z) [open] 17:08Z (10:08 AM PDT): all 3 new models' first rows ended succeeded (Build, Commit, replay; pleias + danube labelled pass, salamandra next pass): grid 22 models / 12 families, both 36 / 15. Trim applied for the new models (19 items). Node 2 is drained for the 17:00Z quota cutover (note:20261001T1612Z-handoff-from-node2-ops-node2-cutover-fill-drained): n2_build.sh offloaded 6 grid Builds there at 16:27-16:34Z (gm053, gm054, gm064, gm214, gm221, gm222), which wait until the hand-back; into the 10:30 report.
CHECKPOINT b9880ac17 (16:45Z) [open] 16:48Z (9:48 AM PDT): counts_all.py (grid + the rest of vllm-epoch-run, node 1's records): 387 ended (grid 197: 188 pass, 9 fail, named; epoch 190: 125 ok, 65 failed), 33 models (32 with a pass), 12 families (11 with a pass; pythia none). -pk3 twins labelled (gather/base_of took -pk3; gm-label restarted). Pleias-350m's first Build passed 16:43:56Z; danube/salamandra pending CPU quota. Trim reapplied (38 items, 15772 -> 15023 GB). The feeder is bound by build_mem_gb (963/1000) and deployments-cpu; the packable 48 GB Builds wait; pack spool empty.
CHECKPOINT b9880ac17 (16:31Z) [open] 16:31Z (9:31 AM PDT): -pk3 twins gm005/gm008 packed (ada3883d77) and match their bases (run root, map, verdict). 3 models added as wave 5 (cov-gm373..444, 72 items, tree cursor-grid-models-more-be5a @ 704714544); gm-label restarted with their families. 9:30 reorder written (reorder.py --pack: new models' first rows, 18 packable, 160 B8/1k, rest). Grid ended 192 (183 pass, 9 fail, all named), 19 models, 9 families.
CHECKPOINT b9880ac17 (16:08Z) [open] 9:08 AM PDT: acting on circuits' 1555Z handoff. -pk3 twins of gm005/gm008 submitted 15:59:12Z on node 1 with 16 GB Builds (trim rule from their measured 5.9/9.1 GB peaks) so they admit before n2-offload's 2-min hold; held for quota so far, not moved. Registering 3 small ungated BF16 llama-arch models from new families, smallest first: PleIAs/Pleias-350m-Preview, h2oai/h2o-danube3-500m-base, BSC-LT/salamandra-2b (TP1).
CHECKPOINT b9880ac17 (15:49Z) [open] 8:49 AM PDT: trim holds (7 trimmed Builds since 15:16Z peaked 4-8 GB, at most 0.32 of the new request; no Build failed since). deployments-cpu is now bound by replays (flat 64 GB template default; 4 pending), not Builds (12 at builds_cap, 451 GB). Replay peaks run 4-87 GB, 4 classes over 64, no unsubmitted item in a measured class: replay requests left as they are (note:20261001T1516Z-finding-build-mem-trim, Afterwards).
CHECKPOINT b9880ac17 (15:44Z) [open] 8:46 AM PDT: all 9 -pk2 twins ended; the 7 packed match their bases (run root, binding map, verdict); gm005/gm008-pk2 unpacked (node-2 Builds, n2_build.sh bypasses route()); gm001-pk2 fails on the base's SiluMul_v1 edge and pack-stopped qwen3-06b. note:20261001T1540Z-finding-pk2-twins-packed-match; handoff to circuits 20261001T1545Z (pack-lift, n2_build, -pk3?). Feeder: 170 ended, 12 Builds (451 GB), cpu-pending 1. Labeller passes ok on node 1.
CHECKPOINT b9880ac17 (15:35Z) [open] 8:37 AM PDT: -pk2 twins: 7 of 9 ran packed (commit-pack MPS pods); gm002/003/004/006/007/009-pk2 PASS 460/460, same run root, binding map and verdict as their bases; gm001-pk2 (qwen3-06b, base fails on the SiluMul_v1 edge) replaying. gm005-pk2 and gm008-pk2 ran unpacked: their Builds were offloaded to node 2, and n2_build.sh submits the Commit with dispatch.py submit (no route/packable). gm005-pk2 matches; gm008-pk2 replaying. 167 ended; labeller on node 1, passes ok.
CHECKPOINT b9880ac17 (15:18Z) [open] 8:17 AM PDT, re circuits' 7:55 follow-up: (1) labeller moved to node-1 tmux gm-label (research, /workspace/jobs/gm-label, store creds from the research-r2 Secret); first pass 15:08:33Z wrote 40 labels to the remote; the VM copy died with the VM restart at 14:53Z. (2) 91 of 215 unsubmitted Build requests trimmed, 16340 -> 12574 GB, backup items.bak-1516Z.json, note:20261001T1516Z-finding-build-mem-trim, art:4c0352b9. (3) PACK_MODELS lists the 9 models; 9 -pk2 twins submitted 15:11:55Z. Incident: key lines printed to my tool output, note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines.
CHECKPOINT b9880ac17 (14:42Z) [final] 7:44 AM PDT: 20 models / 10 families registered; 134 deployments ended (127 pass, 7 fail: 6 SiluMul_v1 edge, 1 item config gm127); 19 models / 9 families ended, 18 with a pass; 9 golden twins match, all unpacked (PACK_MODELS lacks them); feeder keeps node 1 fed; art:c8c825f9f8aa2831d33b6b21039c5a90be8d6bcc6f990c16b8c6c35653ce7be3
CHECKPOINT b9880ac17 (14:42Z) [final] 7:43 AM PDT: 20 models / 10 families registered; 134 deployments ended (127 pass, 7 fail: 6 SiluMul_v1 edge, 1 item config gm127); 19 models / 9 families ended, 18 with a pass; 9 golden twins match, all unpacked (PACK_MODELS lacks them); feeder keeps node 1 fed; art:c8c825f9f8aa2831d33b6b21039c5a90be8d6bcc6f990c16b8c6c35653ce7be3
CHECKPOINT b9880ac17 (14:40Z) [final] 7:41 AM PDT: 20 models / 10 families registered; 134 deployments ended (127 pass, 7 fail: 6 SiluMul_v1 edge, 1 item config gm127), 19 models / 9 families ended, 18 with a pass; 9 golden twins match unpacked (PACK_MODELS lacks them); feeder keeps node 1 fed
CHECKPOINT 70e926d (14:15Z) [open] 7:16 AM PDT: acted on circuits' 1412Z: deadline gate dropped 14:12Z, burst caps kept (per_tick 12, cpu_pending_max 12, commit_cap 14). Build concurrency now bound by deployments-cpu's 608 Gi memory quota (Build requests 86-128 GB). Counts 14:15Z: 124 ended (117 pass, 7 fail: 6 SiluMul_v1 edge, 1 config gm127), 19 models (18 with a pass), 9 families. 7:40 counts next.
CHECKPOINT de79a63 (14:03Z) [open] 7:05 AM PDT: golden twins done (all 9 same root/map/verdict, all unpacked: PACK_MODELS lacks them; note:20261001T1355Z-finding-golden-twins-unpacked-all-match, handoff 1357Z). Acted on kueue-fold's 1315Z reply (Hold ended 13:30Z as it said). New failure named: cov-gm127 (qwen3-30b) Commit died at vLLM KV-cache init, gpu_memory_utilization 0.5 < 56.9 GiB weights; set GPU_UTIL=0.9 on the 11 unsubmitted qwen3-30b items. cov-gm149 failed on the SiluMul_v1 edge (auto-checked). Feeder: burst commit_cap 14 to 14:20Z; deadline hold extended so no 7:50-crossing row goes before 14:50Z. Counts at 14:00Z: 117 ended, 110 pass, 7 fail (6 SiluMul edge, 1 config).
CHECKPOINT e8cff57 (13:32Z) [open] 6:34 AM PDT: Hold lifted 13:30Z (kueue-fold's 1315Z reply: the quiet hour released it); no-release removed 13:2xZ. My 7 waiting Commits (gm135/051/149/127/204/133/132) admitted 13:30Z; 8 Builds admitted incl. twin gm005-pk, twin gm003-pk and gm096 moved to node 2. Feeder burst extended to 13:50Z (per_tick 12, cpu_pending_max 12) for the refill's first 15 min. Twins still not on PACK_MODELS (dispatch.py unchanged since 08:18Z).
CHECKPOINT c83c233 (13:13Z) [open] 6:16 AM PDT: node 1 still on Hold (both queues), commit-release's no-release file still present; flagged to circuits (1307Z note + addendum). 9 twins + 7 rows queued since 12:55Z; 7 of my Commits wait deactivated; none admitted since 12:46Z. Feeder, labeller, twins submitted; twin compare waits on their Commits.
CHECKPOINT db8a2b2 (12:27Z) [open] 5:27 AM PDT: in node 1's hold; 92 ended (88 pass, 4 SiluMul_v1 edge). Feeder resumes at 12:55Z (reordered, burst), 9 golden twins at 12:55:20Z. Flagged node 2's max_min=40 can't start before the 7:50 count: note:20261001T1218Z-handoff-from-circuits-grid-models-node2-max-min-40-no-start.
CHECKPOINT 1ea7ca2 (12:04Z) [open] 5:05 AM PDT, re note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens: (1) unsubmitted items reordered quickest deployment first (est from node 1's walls; backup items.bak-1202Z.json), burst per_tick 12 / cpu_pending_max 12 until 13:10Z, deadline gate kept (Commit by 14:35Z); (2) small rows first feed node 2's gaps through the offloads; (3) 9 twins cov-gm00N-pk (gm002-009, and gm001 for qwen3-06b, whose B1 256 rows all failed in the replay on the SiluMul_v1 edge though their Commits passed) submit at 12:55:20Z from node-1 tmux gm-twins on the plan tree; labeller labels -pk keys; comparison script feeder/twin_compare.py; (4) counts at 7:40.
CHECKPOINT ebaf224 (11:48Z) [open] 4:50 AM PDT counts: 103 submitted, 79 ended (75 pass, 4 fail: SiluMul_v1 expf-overflow edge, all Qwen3-0.6B); 17 models / 9 families; note:20261001T1149Z-report-from-circuits-grid-models-counts-0450. Feeder in its 11:30-12:55Z guard.
CHECKPOINT 99b1e04 (11:13Z) [open] 4:13 AM PDT: 67 deployments ended (63 pass, 4 fail, all SiluMul_v1 expf-overflow edge); 17 models, 9 families (falcon3, llama3, mistral, olmoe, phi, qwen25, qwen3, smollm2, yi). 14B TP1 B8 256 Commits took 14 min. Deadline gate now holds 11 rows past 12:10Z; feeder stops at 11:30Z.
CHECKPOINT 2b29cfc (10:49Z) [open] 3:52 AM PDT, re note:20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree: acted. Every row submitted since 10:36Z runs on cursor-grid-plan-gm-827a (05fa9d3ea, 6 so far); the labeller now names that tree in each note (TREES); my branch stays cursor/grid-models-8c79 @ b9880ac17. My inbox watcher missed this note for 10 min (its pull failed on an uncommitted edit; fixed with --autostash).
CHECKPOINT a65c31d (10:47Z) [open] 3:47 AM PDT: 56 deployments ended (52 pass, 4 fail: all SiluMul_v1 expf-overflow edge, gm001/031/081/082, three of them qwen3-0.6B); 11 models, 7 families; Builds at cap 12; deadline gate holds 0 so far.
CHECKPOINT f171190 (10:26Z) [open] 3:27 AM PDT: kept circuits' 3:16 unskip (none held for a non-length reason); added a deadline gate to gm_feed (Commit est must end by 12:10Z, until 12:55Z) so the 5:10 rule is enforced: note:20261001T1027Z-handoff-from-circuits-grid-models-unskip-ack-deadline-gate. 45 ended (43 pass, 2 SiluMul_v1 edge).
CHECKPOINT 67f26bc (10:15Z) [open] 3:15 AM PDT: 42 ended (40 pass, 2 SiluMul_v1 edge); 18 in flight; 4 queued on node 2 (max_min 40). Kept circuits' feeder values, added 18 skip_keys gm310-318/gm340-348 (3B-6B B16/B32 1k Commits likely >30 min): note:20261001T1015Z-handoff-from-circuits-grid-models-feeder-skip-long-commits.
CHECKPOINT dbdfa87 (10:07Z) [open] 3:10 AM PDT, re note:20261001T1006Z-handoff-from-circuits-idle-hold-node2-fill: no Gemma-2 from me (skip_roles). All 20 of my checkpoints are staged on node 2 now; 4 of my Commits (gm027/041/042/044) already wait in node 2's queue for 3:30, and the feeder keeps going smallest-first, so held Commits overflow there. The 24 non-Gemma held rows stay held (their Commits likely pass max_min 40 and would restart). I switch to the planned tree for every new row once it is named.
CHECKPOINT 2be6e6f (10:00Z) [open] 3:00 AM PDT: 48 submitted, 35 ended (33 pass, 2 fail: both SiluMul_v1 expf-overflow edge, labelled by silu_check); 4 Commits stuck on node 2 (no slot before 9:30 AM PDT); feeder now gates Builds on my node-1 Commits so fewer wait into offload
CHECKPOINT 76861d5 (09:35Z) [open] 2:36 AM PDT: 19+ ended (18 pass, 1 fail); gm001 diagnosed: SiluMul_v1 expf-overflow edge (gate -97), quarantined SiluMul_v2 matches, note:20261001T0934Z-handoff-from-circuits-grid-models-gm001-silumul-v1-expf-overflow; labelled
CHECKPOINT a37f097 (09:18Z) [open] 2:20 AM PDT: 29 submitted, 16 ended (15 pass, 1 fail gm001); handoff note:20261001T0920Z-handoff-from-circuits-grid-models-node2-no-commit-slot (node 2 can start no Commit before 9:30 AM PDT: max_min 90 vs its windows)
CHECKPOINT 001b539 (09:01Z) [open] 2:02 AM PDT: 25 submitted, 13 ended (12 pass, 1 fail: gm001 SiluMul_v1 replay mismatch); counts report note:20261001T0901Z-report-from-circuits-grid-models-counts-0205; labeller counts node-2 passes; holds (36 + Gemma + TP2) unchanged, 3/20 checkpoints on node 2
CHECKPOINT 4abfc02 (08:49Z) [open] 1:53 AM PDT: grid flowing: about 20 submitted, Builds 3-6 min, Commits 5-8 min. cov-gm002 (qwen25-05b-instruct) and gm003 (falcon3-1b) PASS 460/460, slim keeps present, labels on R2. FINDING cov-gm001 (qwen3-06b B1 256/32 greedy): replay 459/460, SiluMul_v1 at model.layers.27.mlp.act_fn/out row 15 (prefill) has 1 of 3072 elements unequal (index 107); F_V(committed inputs) != committed output, the first such mismatch on node 1. Slim keep kept. Report at 2:05 AM.
CHECKPOINT dc5493a (08:26Z) [open] 1:27 AM PDT: GO received and acted on. Merged coverage-v1 @ 90ebe43d9 (MoE slim-plan fix, HASH_THREADS, commit-tokens) into cursor/grid-models-8c79 @ b9880ac17; the tree is synced to node 1. The feeder went to go at 08:24:42Z on waves 1-3, with the 14B TP1 rows right after wave 1. Gemma-9B and the 36 long rows stay skipped; TP2 (24 rows) stays held until infra's TP2 answer, so say if 'all non-Gemma' meant TP2 too. First Builds cov-gm001/002 were submitted 08:25:35Z and admitted. Counts follow at 2:05 AM.
CHECKPOINT a54b1a5 (08:11Z) [open] 1:12 AM PDT: holding for circuits' go (expected ~1:30 AM). Feeder gm-feed armed on node 1: wave 1 = gm001-120 less the 3 held Yi B8 1k rows. 36 long-Commit rows held pending node-2 staging (note 20261001T0753Z handoff). Nothing submitted.
CHECKPOINT a3db005 (07:52Z) [open] 12:54 AM PDT: acted on circuits' 0749Z no-Gemma-on-node-1 directive. Holding 36 rows likely over 30 min of Commit (all 12 gemma2-9b rows, 6 qwen3-30b-a3b-2507 B8 rows, 18 B8 1k rows of the 7-8B dense models); asked for node-2 staging of 8 checkpoints (note 20261001T0753Z handoff). Feeder armed on hold; 372 rows pre-flight resolved, 0 bad. Waiting for go.
CHECKPOINT e3f0e02 (07:37Z) [open] 12:38 AM PDT: acted on circuits' 0719Z decisions. Holding for go. Tree cursor/grid-models-8c79 @ eda63fddd is synced to node 1 and already carries replay-keep-leaves (merged coverage-v1 @ 4764da87e). Added 12 TP1 rows for the 14B models (qwen3-14b and phi4-14b, B1/B8 256/32 x 3 samplings; say if you meant 12 each). 372 items in waves: (1) cov-gm001-120, B1/B8 of the 10 models under 7B; (2) gm121-228, B1/B8 of 7B+/MoE/Gemma-9B plus the 14B TP1 rows; (3) gm229-348, small B16/B32; (4) gm349-372, TP2, held for infra. Feeder tmux gm-feed on node 1 is armed: on go, wave 1 starts within 60 s. Families counted as 11.
CHECKPOINT 31b05b7c7 (07:21Z) [open] 12:26 AM PDT: 20 models registered (branch cursor/grid-models-8c79 @ 31b05b7c7, merged coverage-v1 4764da87e), tree synced to node 1 at /workspace/research/trees/cursor-grid-models-8c79, 360 config-run items (cov-gm001..360) ready; nothing submitted; holding for circuits' go / 'builds now' (note 20261001T0707Z handoff)
CHECKPOINT 3843df1 (07:07Z) [open] 20 models staged (configs, TP1 fixtures, 480 workloads, weights.tsv); download r20261001-064838-2a41 running, ETA 12:45 AM PDT; holding every submission until circuits' go (note:20261001T0707Z-handoff-from-circuits-grid-models-builds-chain-commits)

## FINAL

~~~text
tip: cursor/grid-models-8c79 @ b9880ac17 (base cursor/coverage-v1-2622@90ebe43d)        merge-with: none
     cursor/grid-models-more-be5a @ 704714544 (the 3 new models; base cursor/grid-boundary-gm-827a @ 1fff7995)
known-failures: none    pod: none of mine (shared vy-nebius-1 and vy-n2; I created no pod); $0 of my own
artifacts: art:c8c825f9f8aa2831d33b6b21039c5a90be8d6bcc6f990c16b8c6c35653ce7be3 (14:37Z gather), art:4c0352b9 (Build trim);
           per-deployment outcomes are labels on each attempt, by circuits-grid-models
~~~

**Against the 11:30 AM PDT goals of note:20261001T1555Z-handoff-from-circuits-1130-set:**

- **Ended deployments, both nodes: 434 at 11:30, below the 450 floor.** The count was 449 at 12:50 PM PDT.
- **Models: 36, and families: 15.** Both floors are met: 35 models and 14 families have a pass. pythia-160m (the epoch run's) is the
  one without.
- **Every failure has a named cause.** The epoch run's are named by circuits-epoch-audit.
- The counts were reported at 10:30 and 11:20, with the 11:30 line appended to the second report:
  note:20261001T1731Z-report-from-circuits-grid-models-counts-1030 and note:20261001T1820Z-report-from-circuits-grid-models-counts-1120.

**Models: 23 ungated HF models in 13 families.**

- 20 are on `cursor/grid-models-8c79`. The list is in note:20261001T1440Z-report-from-circuits-grid-models-counts-0740.
- 3 are on `cursor/grid-models-more-be5a`: pleias-350m, danube3-500m and salamandra-2b. They make 72 items, cov-gm373 to gm444, in
  wave 5.
- All three new models passed their first row by 10:03 AM PDT. By 12:50 they had 4, 6 and 3 passes and no failures.

**Grid at 12:50 PM PDT: 244 ended, 234 pass, 10 fail.**

- Where they ran, Build / Commit: node 1 / node 1: 187; node 2 / node 1: 52; node 1 / node 2: 4; node 2 / node 2: 1.
- **9 failures are the SiluMul_v1 expf-overflow Definition gap.** Seven are qwen3-06b: gm001, 031, 081, 082, 102, 001-pk and
  001-pk2. Two are qwen3-8b: gm149 and gm214. The quarantined SiluMul_v2 equals every mismatched committed word.
- **1 failure is a configuration error in my item:** gm127 had no GPU_UTIL.

**Packing and leases.**

- **Packed twins match their bases on run root, binding map and verdict:** the 7 packed -pk2 twins
  (note:20261001T1540Z-finding-pk2-twins-packed-match) and both -pk3 twins.
- **Leased Commits pass.** Since 10:11 AM PDT the feeder has sent every non-packing item through `submit_leased.py` on the lease
  trees. Of the 10 lease-tree items that ended, all passed:
  - 6 ran leased. Each waited at most 0.75 min for its GPU and held it for 1.2–2.2 min.
  - 4 ran without the lease, because node 2 built them and `n2_build.sh` submits the Commit plainly
    (note:20261001T1743Z-reply-from-circuits-grid-models-lease-on-n2-built-items).

**Still running, unattended, on node 1:**

- **Feeder:** tmux `gm-feed`, policy in `/workspace/jobs/gm-feed/policy.json`. To stop it, `touch STOP` there.
  - It sends little now. `big_cap` is 4 (set at 10:25 AM PDT, not by me), and every one of the 177 eligible items is B8 or larger.
- **Labeller:** tmux `gm-label`. It labels each ended grid item, its -pk twins and lease details.

**Open for circuits:**

- **`big_cap` 14** (note:20261001T1802Z-handoff-from-circuits-grid-models-big-cap-idle). You can set it directly in `policy.json`;
  back the file up first.
- **The pack pilot's bundle cap** (note:20261001T1920Z-handoff-from-circuits-grid-models-pack-bundle-cap). A flat 120 GB estimate
  per B8 1k Commit held 6 small-model Commits for 70–110 min.
- **Node-2-built items lose packing and the lease.** `n2_build.sh` is infra's.
- **The new models aren't in `PACK_MODELS`,** and none of them has a packed twin yet.

**Incident:** key lines were printed to my tool output
(note:circuits-grid-models/20261001T1517Z-friction-env-names-printed-key-lines). Rotate `NEBIUS_SA_PRIVATE_KEY`.

**Documents this lane wrote:**

- in `lanes/circuits/`: 0753Z, 0920Z, 0934Z, 1015Z, 1027Z, 1218Z, 1357Z, 1407Z, 1545Z, 1636Z and 1802Z handoffs; 0901Z, 1149Z,
  1440Z, 1731Z and 1820Z count reports; the 1517Z one-liner; the 1920Z bundle-cap handoff;
- in `lanes/circuits-grid-models/`: the findings 1355Z golden twins, 1516Z Build trim and 1540Z pk2/pk3 twins; the frictions
  1517Z key lines and 1922Z pack bundle estimate; the feeder and labeller code under `feeder/` and `labeller/`
  (`add_models.py`, `reorder.py --pack` and `counts_all.py` among them);
- in `lanes/circuits-replay-keep-leaves/`: the 1743Z reply.

**Handoffs received, all acted on** (and circuits' 7:55 AM PDT follow-up):

- 20261001T0719Z-handoff-from-circuits-decisions.md
- 20261001T0749Z-handoff-from-circuits-no-gemma-node1.md
- 20261001T0821Z-handoff-from-circuits-go.md
- 20261001T1006Z-handoff-from-circuits-idle-hold-node2-fill.md
- 20261001T1011Z-handoff-from-circuits-feeder-opened-up.md
- 20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree.md
- 20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens.md
- 20261001T1315Z-reply-from-kueue-fold-node1-hold-ends-1330z.md
- 20261001T1412Z-handoff-from-circuits-drop-deadline-gate.md
- 20261001T1417Z-handoff-from-circuits-commit-phases-boundary-gm-tree.md
- 20261001T1555Z-handoff-from-circuits-1130-set.md
- 20261001T1705Z-handoff-from-circuits-replay-keep-leaves-lease-self.md
