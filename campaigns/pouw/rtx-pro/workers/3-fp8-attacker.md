---
cursor:
  subagentId: "bc-0f3f8a2f-3024-5bae-bda9-8e3836b9cb92"
---

# GPU 3: FP8 cheaper-computation search and realism (Pearl-C on sm_120)

Worker bc-0f3f8a2f. On node 2 my GPU jobs take whatever `gpu-lease 1` gives and record its UUID; CPU jobs take no lease.
- **Branches:** `cursor/pearl-c-sm120-attacks-cb92` ([draft #507](https://github.com/danielreuter/verity/pull/507); the assessment tools, #451's head merged at `ead771a5`, and from `30e5d473` the 70B capture and replay), and `cursor/pearlc-activations-layers-cb92` ([#505](https://github.com/danielreuter/verity/pull/505), closed 7:18 PM PDT as contained in #507; #451's head plus `pearlc_activations --layers`, one commit, `548363f4`).
- **Atom:** `BLACKWELL_SM120_E4M3_M16N8K32` = `Pipeline ⟨[32], 26, −133⟩` (r20260930-031244-ecbc).
- **Write-up:** [`../fp8-cheaper-computation-search.md`](../fp8-cheaper-computation-search.md) (the list, the census on both atoms, realism, Needs).

## Checkpoints

- 04:50Z: started; store mounted; server pending. Phase A (CPU) under way.
- 05:10Z: census parametric in the atom (`--atom`; selftest against `verity.ml.tc`, 0 mismatches for H100, Ada and sm_120). nvcc 12.9 compiles the probe kernels to QMMA/OMMA/IMMA/QMMA.SP for sm_120a.
- 05:15Z: read `server.md` 05:05Z (the sm_120 step is measured); census re-running on it.
- 05:40Z–06:05Z: the promotion's share of the debit (`debit_parts`), `pearlc_activations --atom`, the routes script's Strassen-E4M3 route, `sm120_chain --reps 0` and `--expect-uuid record` (commits `668522ae`…`d72d2a8d`).
- 06:16Z: the write-up is in the store. Runs: census `r20260930-060720-da05` (sm_120) / `-7e7f` (H100), routes `-060946-418c`, Qwen2.5-0.5B `-060323-5069`.
- 06:30Z: reached node 2 (CPU). Qwen2.5-7B and WikiText-2 are prefetched into `/workspace/hf` (`r20260930-062926-83ef`). v2's debit on 7B (the 06:15Z ask) launched as 10 CPU shards.
- 06:40Z: merged #451's head (`ead771a5`). **My step didn't count the FP32 word's truncation at width 26 as inexact.** Fixed with #451's accounting and re-measured (`r20260930-064135-8d8b`, `-5127`): the residual is 0, not 57%. The write-up is revised.
- 06:45Z: `sm120_chain --gpu lease --expect-uuid lease --clock-label` (`5f1cb93e`). The gates-only run is queued in `gpu-lease 1 --wait` (`r20260930-064531-15cb`), behind a whole-node request.
- 07:05Z: v2's 7B debit is aggregated and in the store (Results 1). The gates run passed on the card (Results 8).
- 07:17Z: the timed run is queued in a whole-node window (`r20260930-071059-5389`, at the head of the lease queue). Two fill jobs are queued on node 2: v1's 7B debit (CPU) and the gates at 7B's shapes (GPU).
- 07:35Z: the timed run passed (Results 8), and so did the 7B-shapes gates. The routes are re-priced at GPU 0's measured prices (`r20260930-072255-bd17`): every saving is 0, and the conditional gap is closed. v1's 7B debit is running as a fill job.
- 07:38Z: v1's attention chunk is done (Results 9). The `down_proj` chunks are split into 4 layers each, so every chunk fits the runner's cap. `r20260930-073729-cf62` preserves the chunks from the node.
- 08:30Z: v1's 7B debit is complete and preserved (Results 9). Llama-3.1-70B: the mirror is prefetched at revision `1b7306651142d0cc65d993076a250a6a82cf046c` (`r20260930-075201-f13b`), captured (every 8th layer, 532 s on 16 cores), and 20 replay fill jobs are running (Results 11). `r20260930-081439-a4d2` aggregates and preserves them.
- 08:50Z: v1's 70B replays are done (10 jobs); v2's are running. The 70B quality job is queued (`pearlc_quality_llama.py`, `de7596a8`; self-test passed on node 2). Both fresh gate seeds pass (Results 8).
- 09:31Z: v1's 70B replay is complete: 70 of 70 linears admissible with the split, 44 without; |S| ≤ 12 of 81; worst tile debit 3.1% of ρ (preliminary, Results 11). v2's `down_proj` chunks overran the 25-minute cap at 4 cross-group words per tile, so they now take 2 (Lessons).
- 10:15Z: **blocked on CPU slots.** Since 09:44Z bc-8412d697's four `aw-` CPU jobs hold all 4 slots: they run 5-minute chunks and re-queue with exit 99, and the runner starts queued CPU jobs in name order and ignores `prio`, so `aw-` always goes before `gpu3-`. My 11 jobs (quality at layer 44 of 80; v2 at 8 of 40 chunks) have not started since. Nothing is lost: each job keeps its checkpoints on node 2, and the waiting runs collect the results when the jobs finish. CPU jobs run again since about 11:08Z.
- 11:05Z: the coordinator's 10:18Z order (1): `benchmarks/pouw/sm120_exact` (`56b6a9c2`, `99fd7e04`) passed its smoke run (`r20260930-105956-3c2d`) and ran as a prio-10 GPU fill job, 11:05–11:14Z in 3 chunks. `r20260930-110516-92d9` preserves it (Results 12–14).
- 11:35Z: queued, all at prio 10 in chunks of 8 minutes or less (Fill candidates):
  - the 70 Llama-3.1-70B linears as units (`7f703eda`; smoke `r20260930-111300-b61b`);
  - 7 census draws per family for the merge rate's power (`9b5db77e`; smoke `r20260930-112933-f898`);
  - the per-row debit re-runs as 6 CPU jobs (`136dd8fb`, Results 16).

  Four runs preserve them. Qwen2.5-0.5B's merge rates run as 4 shards on this VM (`9c2e8708`).
- 11:50Z: 70B quality is done (Results 11: +1.15% with the split). Results 12–14 are written, including 66 of the 70 Llama linears. The early per-row numbers are in Results 16. At v2, 8 words per row can't resolve ρ on k = 3,584 (one flag is 1.12ρ), so the next step is to measure rows at full width, starting with the rows with the largest outlier ratio.
- 12:05Z: all 70 Llama linears and Qwen2.5-0.5B's 168 linears are done: no lemma block anywhere, and no fragment with all 5 pre-adds exact (Results 12–15). The full-width per-row jobs are queued (`1b489399`, Results 16).
- 13:50Z: the greedy pairing covers every census family and every Qwen2.5-0.5B linear. No unit has a joint fragment under any of 3 side orders. One side alone does reach a fragment on 4 structured census families (A on rank1, duplicated, coherent-gaussian, outliers-first; B on rank1), so ε₈'s scope is a question for the coordinator (Needs 8). The 70B pairing runs on node 2 (10 of 70 linears done, 0 fragments so far), preserved by `e47a`.
- 15:40Z: **v2-hot's full-unit rerun (13:56Z order):** the GPU half is done on physical GPU 2: 64 units (16 families × 4, 8,192³), H_i by `pearlc_hot_start`'s `const` rule (c₀ = 64), 0 mismatches in every gate. The window search is queued (`gpus=0`, prio 0), and `r20260930-153135-2062` preserves both (Results 17). v1-hot's run is cancelled (15:02Z) and was never queued. **ε₈'s one-sided check (14:07Z) fails as worded:** no fragment row pair is a near-duplicate, and only coherent-gaussian's are chain-inexact (v2 from +0). By the 14:07Z rule that sends ε₈ back to per side, unless the assessor bounds the one-sided route by what it could skip: at most 14% of a fragment's products, 44% on outliers-first (Results 13, Needs 8). The 70B pairing is at 65 of 70 linears, 0 fragments.
- 16:00Z: **v2-hot's pass condition fails** (Results 17, Needs 10). From H_i, 17 of 64 units have a free-family shape: all 4 units of rank1, saturated, grid-aligned and in-span-FA, and 1 of sparse10's. Every hit lies in atoms 0–12. The free family's t₀ is at most 5 from H_i, against up to 9 from +0. **No unit has a priced-family shape from H_i at any start** (priced t₀ = 0 on every family, against up to 2 from +0). An independent CPU replay confirms 4 of the hits. The widest block found is 2,400 columns from H_i and 3,840 from +0. The 70B pairing is complete: all 70 linears, 0 fragments in every mode (Results 13).
- 17:25Z: **the width check against W*(L) (the 17:00Z order) fails at 16 rows** (Results 18, Needs 11). `hot_width.py` (`5ce64802`, `5ee74659`) measured every start 0–5 and every length of 9 atoms or more on all 64 units. Every gate matched, and each run took 30 s on node 2's CPUs.
  - With 16 rows, saturated keeps 6,519 columns exact over atoms 0–9, against a floor of 1,716. 154 of 1,473 windows fail, up to 36 atoms long.
  - Every window passes from 240 rows (tightest margin 58 columns), and from 40 columns on the other side.
  - The floors for every length come from `widthfloor.py`'s own loop and match its table.
- 18:05Z: **clause (c) fails at 6 atoms and on the 8-atom block** (the 17:31Z order, which supersedes 17:00Z; Results 19, Needs 11). The 17:00Z check had already finished at 17:23Z, so nothing needed stopping.
  - Code: `hot_blocks.py` (`1e595704`), over all 64 units in 19 minutes on CPUs only. Every gate matched.
  - At start 0, 288 rows share 4,458 columns over 6 atoms (N = 3,982), and 448 rows share 2,695 over 7 atoms (8's block, N = 2,487), in all 4 saturated units.
  - 11 of 1,296 cases are found, all at starts 0–2 and lengths up to 12 atoms. The tightest pass is 1,958 columns against 2,047 (start 3, 9 atoms).
  - The VM reset again at about 17:33Z. Recovered: the worktree, `uv` and the notes clone.
- 18:17Z: Verity's GitHub token broker is adopted (the 18:15Z order, item 1): the script's SHA-256 matched the pin, `git ls-remote origin HEAD` and `gh repo view` succeed, and `token.json`'s source is `broker`.
- 19:05Z: **clause (b) holds on the cancelling family's full units** (the 18:15Z order, item 2; Results 20). No block of §8's table is found at any start 6–16 (0 of 2,376 cases). The tightest is 144 rows on 1,505 columns over 9 atoms at start 6, against 2,047.
  - Code: `hot.py` gains `cancel-pair@t4` and per-side liveness (`e3a42dcc`, `0f7c4b45`). `hot_blocks.py` gains one task per (unit, start), saved every minute and resumed (`835a3ac3`, `bdef5bbc`).
  - Both ran as prio-1 fill: the replay on one GPU at 18:32–18:35Z, the search on CPUs at 18:44–19:04Z. Every gate matched.
- 21:37Z: **the corrected-table rerun is queued** (the coordinator's 21:12Z order; server.md PINNED 18:42Z; Results 21 when done). `hot_blocks.py` now records width curves (`3b4784c9`, `860918d7`) and judges `v2hot-blocks-corrected.json` on them. Two prio-5 CPU fill jobs: cancel-pair@t4 at starts 4–16, then the 64 census units at starts 0–16. The VM reset again at about 21:05Z; the worktree, broker and notes clone are recovered.
- 22:45Z: **Results 21 is done** (the 21:12Z order; Needs 11–12). On the corrected table:
  - the census fails at starts 0–2 (15 of 2,730 cases, over 6–13 atoms, on saturated and rank1) and passes at every start 3–16 (tightest: 89 columns, 4.3%, at start 3);
  - `cancel-pair@t4` fails at start 4 (144 × 2,091 against 2,047 over 9 atoms, certified) and passes at 5–16 (tightest: 287 columns, 14.0%, at start 5);
  - Results 19 changes at 4 (start, length) pairs, all to found; Results 20 doesn't change.
  - `hot_blocks.py` at `fd3eab84` ran as two prio-10 CPU fill jobs, 21:39–22:35Z, with 0 gate mismatches. `r20260930-223548-448d` preserved it.
- 23:30Z: **clause (c) passes on `catalogue-audit/floors/row-floors-staircase.json`** (the 3:55 PM PDT order; Results 22, which supersedes Results 21's (c) verdict; Needs 11).
  - No window is found at any start, on the census or `cancel-pair@t4`; the closest is 0.766 of its floor (start 0, 9 atoms). The staircase allows every contraction factor, which meets the 21:47Z condition.
  - The check reads no free-family shape.
  - The padded list moves one of `v2-hot-16384`'s block tests: 13 atoms, 144 × 1,152 → 144 × 1,107. 640 × 10,726 and the rest are unchanged.
  - The stray bc-f5693db2 touched nothing of mine.
  - Judge `r20260930-230905-6d30`; `hot_blocks.py` `0d59d4ab`, `80d17d29`; padded recomputation `art:374b8901…`.
- 5:25 PM PDT (00:25Z, 1 Oct): **the padded re-search, part 1** (the 4:41 PM PDT order; Results 23).
  - The threshold max(N_min, W*) is built: FP16 and TF32 padded, every multiple of 8 rows (`padded_floor.py`, `8a57c3e9`; `art:a6974ffd…`). The staircase binds wherever both pay.
  - Every saved curve re-judged on it finds nothing: 0 of 4,165 windows at starts 0–16, and 0 of 3,159 on `cancel-pair@t4` at 4–16.
  - Zero-slices' 0.89 re-read: it is 1.97× the padded free width at start 0 over 6 atoms, but 0.307 of the threshold.
  - Part 2 (starts 10–252 from +0, 17–252 from H_i; Estimated 103 CPU-h) is staged in three `gpus=0` jobs, **not queued**, waiting on compute-accounting.
  - **0.371% is struck** as v2-hot's figure in Needs 11 (server.md PINNED 4:26 PM PDT). No other line here, in the write-up or in PR text cites it.
- 6:00 PM PDT (01:00Z): **part 2 is split for compute-accounting** (the coordinator's 5:38 PM PDT message). Nothing is queued.
  - (a) is v2-hot's clause (b): `gpu3-fp8-padded-hot.sh` + `gpu3-fp8-padded-hot-cancel.sh`, 48 CPU-h. (b) is v2's region row: `gpu3-fp8-padded-zero.sh`, 55 CPU-h. Both Estimated.
  - Peak memory was measured on one task per job under `numactl --membind=1`, `nice 19` and `taskset 96-127`, outside a timed window (`art:0cd025e3fccd612b274a7d66b3c43fe416fa1a8d4becf9115deffc9a0b6921f0`):
    - each worker peaks at 312–329 MiB anonymous; the whole tree at 396 MiB; the scope's `memory.peak` at 0.39–0.40 GiB;
    - each worker also maps 3.9 GiB of the unit's bitsets, as shared page cache;
    - a 16-process chunk is then at most about 5.3 GiB anonymous, plus up to about 8 GiB of reclaimable page cache.
  - The staged scripts now set `mem_gb=16` (it was 48), 48 GB for all three. VM reset at about 00:35Z; notes clone and ssh recovered.
- 6:40 PM PDT (01:40Z): **custody is done; fix (2) is running; `v2-hot-16384` is on hold** (server.md PINNED 5:52 and 6:28 PM PDT; compute-accounting's 0104Z and 0111Z orders).
  - **Custody: 8 of 8 PRESERVED.** The VM resets since their launch (about 23:40Z, 00:35Z and 01:10Z) wiped the local run records. I rebuilt each `~/.research/runs/<id>/remote.json` from node 2's run directories, then ran `research fetch --all`, `research data custody --publish`, `research data push` and `research data preserved` on each. Every check reported "PRESERVED", with 4/4 or 5/5 objects pushed:
    - `r20260930-213310-5825`: done rc=0 SUCCESS, PRESERVED (run record `art:3fd7976f…`)
    - `r20260930-213529-bb00`: SUCCESS, PRESERVED (`art:81611a8d…`)
    - `r20260930-214453-aa44`: SUCCESS, PRESERVED (`art:763d2f0f…`)
    - `r20260930-220609-e83f`: SUCCESS, result valid, PRESERVED (`art:9ef408e0…`)
    - `r20260930-222313-d437`: SUCCESS, PRESERVED (`art:3d47e586…`)
    - `r20260930-222317-b5b4`: SUCCESS, PRESERVED (`art:3606fe93…`)
    - `r20260930-222322-7ed1`: SUCCESS, PRESERVED (`art:b81a27be…`)
    - `r20260930-222327-4627`: SUCCESS, PRESERVED (`art:817af2d3…`)
  - From now on every node-2 run launches with `--custody-r2 --custody-ttl 8h`. The first is `r20261001-013255-7ab0` (preserved).
  - **Fix (2), the no-charge route's test** (the assessor's spec, `note:20261001T0116Z-reply-from-d7d4b0d1-v2hot-fix2-spec`):
    - `hot.py` now draws the assessor's seven late-start families exactly as `hot_late_start.py`'s `family()` does (`85474991`). Both draws were checked on all seven families. `cancel-pair@t4` is also identical to `8a57c3e9`'s draw, so Results 20's four units of it are reused.
    - The GPU job `gpu3-fp8-fix2-gpu.sh` (`gpus=1 prio=10 max_min=8`) started at 6:35 PM PDT on GPU 0. It writes 6 families × 4 units at 8,192², with bitsets for all 256 atoms, a superset of the spec's atoms 0–16 (Estimated 25 GPU-min).
    - It then queues `gpu3-fp8-fix2-blocks.sh` (`gpus=0 cpus=16 prio=10 max_min=8`). That job judges all seven families at starts 0–5, then 6–16, at every row count against `row-floors-staircase.json` (`6f197bc6…`), as Results 22 did (Estimated 2 CPU-h for starts 0–5).
    - `cancel-pair@t4`'s starts 0–3 are judged inside fix (2), because the spec lists the family. The separate job (approval (2)) stays dropped.
  - **(a) keeps running,** and I stop it at once if fix (2) finds a block. At 6:36 PM PDT: `padded-hot` is on starts 17–63; `padded-hot-cancel` finished 17–63 at 6:19 PM PDT and is on 64–127.
  - **`v2-hot-16384` is on hold** until fix (2) is decided and a new order comes. Nothing is written or queued for it.
  - **MKL race: not exposed.** There is no torch in `benchmarks/pouw/sm120_exact/`, `pearlc_census.py`, my job scripts or `hot-ref/`, and every job runs `uv run --no-project --with numpy`.
- 7:50 PM PDT (02:50Z): **fix (2) fails on the staircase; (a) is stopped; v2-hot is parked** (Results 24; `note:20261001T0250Z-reply-from-0f3f8a2f-v2hot-fix2-fails`).
  - The find: `cancel-pair@flat` unit 1, start 0, 9 atoms, 361 rows × 2,669 columns against W*(9, 368) = 2,216.6. It is certified, with a caveat for the assessor: the block pays only below its composition's own rows.
  - (a) stopped at 7:42 PM PDT, and its cancel half had already finished with 0 found. The judge finishes starts 0–5; starts 6–16 wait for an order.
  - The judge's cost estimate is corrected: about 16 CPU-h for starts 0–5, not 2 (Estimated).
  - My notes-repo replies go out with `RESEARCH_NOTES_TOKEN`. The VM's global git `url.…insteadOf` rewrite would otherwise push them as `cursor[bot]`, which has no write access.
- 8:45 PM PDT (03:45Z): **fix (2)'s final verdict: it fails, on 1 window in all 4 `cancel-pair@flat` units and nothing else** (Results 24). The judge finished starts 0–5 at 7:56 PM PDT: 1,503 windows, 0 gate mismatches, 11.3 CPU-h. `r20261001-031736-ecaa` preserves it and both halves of (a). This is my last checkpoint: by compute-accounting's migration order (`note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff`), FP8 security (bc-4323a347) takes over, and my handoff is `note:20261001T0345Z-handoff-from-0f3f8a2f-migration`. #505 is closed as contained in #507.
- 13:08Z: the greedy pairing on all 168 Qwen2.5-0.5B linears is done, with 0 fragments (at most 8 of 16 A row pairs, 5 of 8 B column pairs; Results 13). The census families run on this VM and merge into node 2's job directory between chunks (identical output, checked on gaussian). The 70B jobs now take 5.5-minute chunks (up to 2 linears each). 7B v1 at full width is done: no row over ρ (Results 16).
- 12:50Z: the 7 census draws are done: the merge rate's bound is under 2^−20 on both sides (Results 13). The greedy adversarial pairing (`pairing.py`, `99899c7c`, `fa74b9e3`; `pearlc_activations --pairing`, `22dc75bc`) passed its self-test here and on node 2. On smokes it reaches 4–8 of a fragment's 16 A row pairs, and it is queued on the census and the 70B linears, with the 0.5B linears on this VM. At full width no row's debit is over ρ (Results 16).

## Results

Details and run ids for everything below are in the write-up. Operand statistics are Measured on CPU, bit-exact against `verity.ml.tc`'s step. W1 prices are Measured (GPU 0's `r20260930-063213-c94a`; int8 IMMA from my chain), except FP8 `mma.sp`, which keeps its public price.

1. **v2's debit on Qwen2.5-7B, the 06:15Z ask** (no promotion, sm_120 atom, #451's `debit_pure`; Measured, CPU on node 2).
   - Coverage: all 197 linears, 394 tiles of 64×8, 2,048 WikiText-2 tokens. 10 runs `r20260930-0631…`/`-0632…`; aggregate `art:65e2ff53d4700e0f65d858094e5ba6463afec992d17fc34e028f73f6b25f7007`.
   - **Per tile:** at most 5.2·10⁻⁵ of atoms (5.2% of ρ = 1/1,000); mean 7.1·10⁻⁶; 0 tiles over ρ. `down_proj` (k = 18,944): at most 2.0·10⁻⁵.
   - **Per word:** at most one flagged atom (0.89% of 112; 2 of 592 on `down_proj`).
   - No tile identities, and no exact-run residual.
   - Joint skips (TT_OUT's): at most 1.8% of one sampled word's atoms.
   - Shortcuts: one greedy word per tile; tiles drawn from rows admissible without the split; the forward pass runs on CPU.
2. **`no-exact-rewrite/sm120-e4m3`.** No route on the list reproduces v1's checked words more cheaply than the native atom at the measured prices (Measured prices × Measured operands, `r20260930-072255-bd17`).
   - Per MAC: int8 IMMA limbs 4.12–4.85, NVFP4/OMMA limbs ≥ 3.14, FP16-accumulate FP8 1.26, Strassen 1.88 with FP16 or BF16 pre-adds and 1.006 with E4M3 pre-adds. 2:4-sparse `mma.sp` and the one-limb routes apply to 0% of in-domain operands.
   - There are no long exact runs to rewrite: no tile-exact run reaches 14 atoms in any of 50 in-domain cells, on any real 0.5B layer or on the 7B hard rows (the longest is 7). The residual is 0.
   - The one conditional gap is closed: FP8 with FP32 accumulate runs at the F16-accumulate rate on this card (GPU 0: 1.000; my chain: 0.988×), so the half-rate case behind the 3.6% bound doesn't arise.
3. **The W1 price gap (Derived).** Lean's `Costs.adopted` and `pearl_c.py` price an FADD at 32 (H100). On this card it is 8.38 (GPU 0, Measured); my chain's promotion time implies 7.0–7.7. At 32 the credit is 14.3–14.8% above the honest cost at every Qwen2.5-7B and Llama-3.1-70B linear and at 8,192³.
4. **The census on sm_120 (Measured).**
   - No tile identity atoms; per-word identities ≤ 0.087% (H100: up to 75%).
   - The debit is ≤ 0.11% on families that pass the cap. On aligned spikes it is 0.42–29.3%, and 97.3–99.4% of that is the FP32 promotion's rounding, not the atom's adder. The cap rejects those tiles.
   - Transfer test: 0 of 51 sets survive (H100: 12 of 82).
   - Group sums equal across two salts ≤ 0.047% (H100: 90%).
5. **2:4 sparse (GPU 7's question).** `mma.sp` for FP8 exists on sm_120a: ptxas emits `QMMA.SP.16864.F32/F16.E4M3.E4M3`, with or without `kind::f8f6f4` (SASS). Its words aren't captured. Pearl-C's noise floor at δ = 1 keeps A′ and B̃ out of 2:4: 0% of 16×64 fragments, ≤ 0.052% zero codes (Measured). A two-half split ties at cost 1.0.
6. **Unpromoted v1** (drop the FADDs): the word equals the ticket word for ≤ 11.1% of words and for no whole tile (Measured, CPU), and on the card for 8.53% of words at 8,192³, 29.6–29.7% at 7B's k = 3,584 shapes and 2.3% at k = 18,944, never a whole 64×64 tile. It would save 5.2–5.6% of the chain's time (Measured) and 6.1% of chain W1.
7. **Realism.** Every Qwen2.5-7B and Llama-3.1-70B linear is in the domain. Admission is atom-independent, so the H100 lane's results carry over (the 7B `down_proj` needs the pinned split, |S| = 38 ≤ 186). The emulated perplexity has no atom, so it carries over as Estimated: 0.5B U +4.87% vs BF16; 7B adopted path +1.45–1.47%.
8. **On the card** (`r20260930-064531-15cb`, GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f, PCI index 0, locked-2100; Measured).
   - The SASS gate passes on nvcc 13.0's sm_120a build: 64 `QMMA.16832.F32.E4M3.E4M3` per 128-deep step, plus 64 FADD in the honest chain only.
   - The honest, unpromoted and int8 chains match the twin bit for bit on the formed families (3 × 16,384 words) and at 8,192³ and 128×8,192² (256 words each).
   - The unpromoted word equals the honest one for 8.53% of words and no 64×64 tile.
   - **Timed** (`r20260930-071059-5389`, the same die, locked-2100: 2,092/12,481 MHz on every item). At 8,192³, the honest chain takes 1.909 ms (575.9 TFLOPS), unpromoted 1.801, int8 IMMA 1.814 and F16 accumulate 1.780. **The promotion is 5.65% of the chain's time** (5.17% at 128×8,192²), against its W1 share of 5.88% at FADD 8. int8 and F16 accumulate run at the FP8 atom's rate.
   - **At 7B's four linear shapes** (m = 2,048, fill job on GPU-fb680060-f371-db1a-73ba-8f2eef43674c, PCI index 1; `art:6c0c59d3af5bbf00ccf5eb31513025662d3c137886b0e81f751d7482e5c25e56`): every gate passes.
   - **At 16,384³ and Llama-3.1-70B's four linear shapes** (m = 2,048, seed 20261002; fill job on GPU-9f1f172d-195e-17de-0679-c0952b0e2fd5, PCI index 3, 4.9 min): every gate passes, 0 mismatches. The unpromoted word equals the honest one for 2.8% of words at 16,384³, 8.5% at k = 8,192 and 1.2% at k = 28,672, and for no 64×64 tile. **Two more seeds reproduce both results** (0 mismatches; `r20260930-082526-102a` preserves all three outputs): seed 20261003 at 8,192³ and 7B's shapes on GPU-2b59d5fe-4acb-287b-5e52-06608509c519 (PCI index 6; equal words 8.5%, 29.1–29.6% and 2.3%), and seed 20261004 at these shapes on GPU-4352a609-f69f-8929-3a1b-c85bdfea9753 (PCI index 4; 2.8%, 8.5% and 1.2%). No 64×64 tile is equal at any shape or seed.
   - Shortcut: a chain microbenchmark without forming or hashing, at 76% of cuBLASLt FP8's 760.5 TFLOPS (GPU 6); one die.
9. **v1's debit (G = 4) on Qwen2.5-7B, for the theory lane** (Measured, CPU fill job on node 2; the same sm_120 atom, tokens and tile sampling as Results 1).
   - Coverage: all 197 linears, 394 tiles of 64×8, 2,048 WikiText-2 tokens. Attempt `r20260930-073729-cf62`; run record `art:c2fd36fe7c100a0ac18feeea72a9e829735ccffeedfb0babafbbc890a2dd9dc2` (`out/v1-7b-agg.json` and the 9 chunks).
   - **Per tile:** at most 3.14·10⁻⁴ of atoms (`layers.1.mlp.gate_proj`), 12.6% of ρ = 1/400; mean 2.25·10⁻⁵; 0 tiles over ρ. By role: q/k/v/o and `up_proj` ≤ 1.05·10⁻⁴, `down_proj` (k = 18,944) ≤ 5.9·10⁻⁵, `lm_head` 1.7·10⁻⁵.
   - **Per word:** at most 4 of 112 atoms (3.6%).
   - No tile identities, and no exact-run residual.
   - Joint skips across groups (`cross_group`, 4 words per tile): at most 2 of 112 atoms (1.8%), 0.89% beyond the debit.
   - Against v2: v1's worst tile uses 12.6% of its cap, v2's 5.2% of its cap; v1's absolute debit is about 6× v2's.
   - Shortcuts: tiles drawn from rows admissible without the split (up to 6.5% of activation rows fail unsplit on `layers.2.mlp.down_proj`); the forward pass runs on CPU in BF16.
10. **Tickets** were dropped from `pearl-c-sm120` at 06:35Z, so the list's "bit for bit" is over C̃ and U. The ticket word in the census is the honest G4 chain word that C̃ checks.
11. **Llama-3.1-70B** (the 07:47Z go; v1 and quality done, v2 running).
   - Weights: `unsloth/Meta-Llama-3.1-70B` at revision `1b7306651142d0cc65d993076a250a6a82cf046c`, all 30 shards in `/workspace/hf` (`r20260930-075201-f13b` for layers ≤ 72, `r20260930-083603-799d` for the rest).
   - Capture: `pearlc_capture.py` (`30e5d473`) streams a BF16 CPU forward one decoder layer at a time. Its self-test matches the full model's forward bit for bit on a tiny random Llama (22 tensors; `r20260930-080835-69a3`, and again in the job). It saved every linear's input X in layers 0, 8, …, 72 on 2,048 WikiText-2 test tokens (window 0, BOS at row 0) in 532 s, into `/workspace/pouw/gpu3-fp8/llama70b-w0/` (4.3 GB, manifest with sha256s).
   - Replay: 20 CPU fill jobs (`gpu3-fp8-llama70b-{v1,v2}-L*.sh`), each running `pearlc_activations.py --replay --split` on one layer's 7 linears. Each reports admission unsplit and with the split (|S| ≤ ⌊k/100⌋: 81 at k = 8,192, 286 at k = 28,672), and the debit on 2 tiles of the split unit per linear, for v1 (G = 4) and v2 (G = 0). v1's 10 jobs are done; v2's are running (its `down_proj` chunks with 2 cross-group words per tile, not 4, since 09:30Z). `r20260930-081439-a4d2` aggregates them.
   - **v1, preliminary** (all 10 jobs; Measured, CPU): 70 linears, 140 tiles. Admissible with the split: 70 of 70; without: 44. |S| ≤ 12 (layer 0's `q_proj`; budget 81), and no split reaches its budget. Row 0 (BOS) is what fails `gate_proj`/`up_proj` in layers 8–72 (|S| = 3 each) and layer 0's `down_proj`; otherwise at most 2 rows fail unsplit, and none with the split. Debit per tile at most 7.6·10⁻⁵ (layer 40's `q_proj`), 3.1% of ρ = 1/400; mean 2.1·10⁻⁵; 0 tiles over ρ; per word ≤ 1.6%; no identities; residual 0; cross-group ≤ 1.6%, 0.59% beyond the debit.
   - v2: layers 0, 8, 16 and 24 are done; layers 32–72 are queued behind the per-row jobs (Results 16).
   - **Quality** (Measured, CPU; `pearlc_quality_llama.py` at `de7596a8`, fill job `gpu3-fp8-llama70b-quality.sh`, 4,463 s on 16 cores; `r20260930-084523-765b` preserved `quality.json` at 10:55Z, run record `art:4a248e9898478f596b21357e21f3e92de660b6facfa7c4c572aa1d6346df240e`).
     - Setup: all 80 layers on 4 × 512 WikiText-2 test tokens (2,044 predictions); the split calibrated on 512 train tokens, |S| ≤ ⌊k/100⌋; `lm_head` in BF16 in every variant; the self-test matches the full forward exactly.
     - Perplexity: BF16 3.4920; FP8 3.5205 (+0.82%, upper 95% bound +1.89%); FP8 + α 3.5270 (+1.00%, +1.74%); FP8 + α + split 3.5322 (**+1.15%**, +1.47%).
     - Paired: α adds +0.18% (SE 0.43%) to plain FP8, and the split +0.15% (SE 0.39%) to that: neither is resolved at 2,044 tokens.
     - The split: 195 of 560 linears use one, at most 12 channels (budget 81 or 286), none at its budget. On the calibration tokens at most 2 of 512 rows fail unsplit (186 linears have one or two, 158 of them `gate_proj`/`up_proj`).
     - Shortcut: FP8 emulation without Pearl-C's U or the sm_120 accumulator; 2,044 tokens.
12. **`no-aligned-exact-region/sm120-unpromoted` on the card** (the 10:18Z order (1), ttout-restatements §7; Measured).
   - **Job:** `benchmarks/pouw/sm120_exact` (`56b6a9c2`, `99fd7e04`) as a prio-10 GPU fill job, 11:05–11:14Z in 3 chunks. It ran on GPU-9f1f172d-195e-17de-0679-c0952b0e2fd5 (PCI 3) and GPU-af0bf9e0-2a17-98be-19b6-f184292c3842 (PCI 7), both at 2,092 MHz under locked-2100. `r20260930-110516-92d9` preserves it.
   - **Unit:** one 8,192² unit per census family (k = 8,192, 256 atoms per word, 225 windows of 32 atoms). Forming is §5 (`census.form_s5`, δ = 1, line norm 16), on v2's unpromoted sm_120 chain.
   - **Gates:** the card's per-(word, atom) truncation flags match the CPU twin exactly (0 mismatches). That covers 4,096 formed elements, 512 chain words, and the window flags of 512 words × 225 windows in both orientations.
   - **Against §7 (in law):** #449's `form_v1` draws other operands than this census, so the comparison is in law. Gaussian at k = 8,192 gives steps exact 96.15% (§7: 96.21%), window density 27.7–55.2% (27.8–55.7%), and a largest 64-tile block of 3×30 (3×27). Gaussian, zero-slices and aligned-spikes-pm1-r64 at k = 1,024 agree as closely.
   - **Census:** 26 families; Π admits 25.
     - No admitted family has an all-exact 1,024 × 512 block in any window, or a single all-exact 16×8 fragment.
     - At 512 or 1,024 rows, the count-order greedy keeps 0 columns.
     - The largest all-exact blocks found are 13 × 2,258 (saturated) and 11 × 2,354 (duplicated). Every other block has ≤ 9 rows, or ≤ 2 columns (e.g. 2,104 × 2 on spikes-groupstart).
     - Only zero-row has the lemma's block (8,192 × 8,192), and Π rejects it (noise floor and liveness on A).
     - **7 draws per family** (`9b5db77e`, GPU fill 11:36–12:40Z, preserved by `r20260930-113545-920d`, result `art:7dc835de4fb904d31f3e064f354cd59addcb03eba25fd98e0f18f8427c28dfe1`): 175 admitted units, 0 lemma blocks, 0 all-exact 16×8 fragments. The largest blocks stay on the same families: saturated 11–14 × 2,030–2,586 (at most 29,354 words), rank1 and duplicated up to about 26,000 words. The 7 zero-row draws have the lemma's block and are rejected.
   - **Llama-3.1-70B linears** (the 10:18Z order's real activations; `7f703eda`; all 70, fill job 11:32–12:02Z on GPU-4352a609-f69f-8929-3a1b-c85bdfea9753 (PCI 4) and others, preserved by `r20260930-113542-0168`, result `art:4f9c9121957f9ee5df8ba0a35fc5c7b786f3b64e4b77a6e0d63f74e4de73710e`). A is the capture's 2,048 token rows and B the weight rows. The rules are unsplit, and the search counts only words whose rows Π admits (26 linears lose row 0 or a few weight rows).
     - 0 lemma blocks, and 0 all-exact 16×8 fragments.
     - Largest blocks: 9 × 11,266 (layer 0 `up_proj`, n = 28,672), and 1,627 × 1 on a `k_proj` (n = 1,024).
   - **Shortcuts:**
     - The searches are greedy, not exhaustive: count-order plain and grown, and `intersect_greedy` with 4 seeds × 64 steps.
     - 7 draws per family.
     - The 70B X is unsplit.
13. **The merge rate `fp8-merge-rate/sm120`** (ε₈, at fragment granularity: 16×32 on A, 8×32 on B; Measured on the same units).
   - **Per pre-add** (32,768 A fragments and 65,536 B fragments per pre-add per unit): 3 families have exact fragments, all on the one difference A21 − A11:
     - spikes-first 768 of 32,768 (2.3%);
     - outliers-first 768 (2.3%);
     - outliers-groupstart 512 (1.6%).

     That is far above 2^−20 (9.5·10⁻⁷) for that one pre-add. The mechanism is Sterbenz: identical outlier rows make the differences exact, while the sums overflow 448. The other 9 pre-adds have 0 exact fragments in every admitted family, and every sum pre-add has 0 on its own.
   - **Full Strassen condition** (all 5 A pre-adds exact on an A fragment, and all 5 B pre-adds on a B fragment, at the same k block): 0 in every admitted family. For one draw that follows from the sum pre-adds' zeros (Derived). On two spikes-first draws it is Measured: 0 A and 0 B fragments with all 5 exact, and 0 of 33,554,432 fragment pairs (`r20260930-112933-f898`).
   - **Diagonal-pair elements** are 28–30%, as for random pairs. The largest block whose diagonal pre-adds are all E4M3 is about 1 × 1,270.
   - **Llama-3.1-70B linears** (all 70): 0 of 45,670,400 pre-add fragments exact, so 0 of 778,240 A fragments and 0 of 8,355,840 B fragments have all 5 exact (0 of 534,773,760 pairs).
   - **Qwen2.5-0.5B linears** (all 168 of layers 0–23, admitted rows, window 0; 4 CPU shards on this VM at `9c2e8708`: `r20260930-114012-8d89`, `-114213-970c`, `-114216-a3d9`, `-114219-7945`). Every one of the 10 pre-adds has 0 exact fragments (0 of 2,972,200), so 0 of 245,042 A fragments and 0 of 349,398 B fragments have all 5 exact (0 of 22,312,752 pairs). Diagonal-pair elements are 25.5–28.7%, and the largest all-E4M3 diagonal block is 1 × 801.
   - **Power:** 0 of N bounds a rate below 3/N at 95%. A pair can't be exact unless both of its fragments are, so the bound is taken per side:
     - one census draw (25 families): A 0 of 819,200 (< 3.7·10⁻⁶), B 0 of 1,638,400 (< 1.8·10⁻⁶), not yet under 2^−20;
     - **7 draws (done, `r20260930-113545-920d`): A 0 of 5,734,400 (< 5.2·10⁻⁷), B 0 of 11,468,800 (< 2.6·10⁻⁷), both under 2^−20; 0 of 2,936,012,800 fragment pairs;**
     - 70B: A < 3.9·10⁻⁶, B < 3.6·10⁻⁷; 0.5B: A < 1.2·10⁻⁵, B < 8.6·10⁻⁶.
   - **Pass condition** (fragment rate ≤ 2^−20), with the fixed quadrants:
     - the full Strassen condition: 0 hits everywhere; the bound is under 2^−20 on both sides over the census's 7 draws, and on B for 70B;
     - the single pre-add A21 − A11 fails it on the three spike/outlier families (over 7 draws: 5,376, 5,376 and 3,584 of 229,376 fragments, the same 2.3%, 2.3% and 1.6%). That opens no route: Strassen needs all 10 pre-adds, and even with all 10 in E4M3 it costs 1.006 per MAC at the measured prices (Results 2).
   - **Under the greedy adversarial pairing** (server.md 09:08Z: any row permutation of A, column permutation of B and k permutation; `benchmarks/pouw/sm120_exact/pairing.py`, `99899c7c`, `fa74b9e3`; Measured, CPU). Per unit, the greedy adds row pairs (A: rows i, i′ to the top and bottom halves; B: columns j, j′), keeping the k pairs (c to the first half, c′ to the second) on which all 5 of that side's pre-adds are E4M3. After each step, a greedy matching gives the k pairs usable at once. A fragment needs 16 A row pairs, or 8 B column pairs, on 32 matched k pairs.
     - **Self-test** (on this VM and on node 2, `r20260930-124136-4a6e`): the conditions equal `merge_stats`' quadrant masks element for element on the identity pairing (0 mismatches). A planted 40 × 80 all-exact block in A (24 × 80 in B) is found as a joint fragment, 16 + 8 pairs on 40 k pairs, and random codes give none.
     - **So far** (smokes, 512 sampled rows per side, all 8,192 or 896–4,864 k indices; the full runs are queued):

| Unit | A row pairs reached (k pairs) | B column pairs (k pairs) | Joint | Fragment |
|---|---|---|---|---|
| census gaussian | 5 (105) | 5 (84) | 4 + 1 (99) | no |
| census spikes-first | 7 (45) | 6 (52) | 7 + 0 (40) | no |
| 70B layer 0 `q_proj` | 7 (48) | 6 (40) | 7 + 0 (36) | no |
| 70B layer 0 `down_proj` (8,192 of 28,672 k) | 6 (68) | 5 (88) | 6 + 0 (68) | no |
| 0.5B layer 0 `q_proj` | 4 (55) | 4 (33) | 5 + 0 (37) | no |
| 0.5B layer 0 `down_proj` | 8 (51) | 5 (49) | 7 + 0 (41) | no |

     - **Reading it:** each added row pair keeps about 1/10 of the k pairs (gaussian: 5.7M, 528k, 50k, 5.2k, 585, 81), so the greedy stalls at 4–8 of 16 A pairs and at 4–6 of 8 B pairs. The slowest decay is 0.5B's `down_proj` input: about 1/2 per pair from the fourth pair on, and 8 A pairs. B alone comes closest (6 of 8 on spikes-first and 70B `q_proj`), but a Strassen step needs both sides on the same k pairs, and the joint search stops at 4–7 A pairs plus at most 1 B pair.
     - **Qwen2.5-0.5B, all 168 linears (done; `pearlc_activations.py --pairing 512`, `22dc75bc`; 4 shards on this VM, `r20260930-123803-fad0`, `-dc56`, `-60b4`, `-10c3`, results `art:442c9d96ccbeaa8f2914258ab1ec93a57b4468539b1ae346cceda4e2080e7b23`, `art:e88f0f6bb87ec43a422227dae46fee7b2e9ed03e50d2d44ad917256c29957d83`, `art:39b0c8b28d84f280b3b692f4277f85ede02c478224772c309ed9fc1ff4626c9d`, `art:976c2e09b0d46e9f48e55885d027b45e5dd75e209aa832e51d392e03b56d3be2`): **0 fragments** in every mode (A-only, B-only, joint).
       - A-only reaches 4 of 16 row pairs on 141 linears, 5 on 17, 6 on 8, 7 on 1 and 8 on 1 (layer 0 `down_proj`, 43 k pairs).
       - B-only reaches 3 of 8 column pairs on 141, 4 on 3 and 5 on 24 (at most 56 k pairs, a `down_proj`).
       - Joint reaches 3–8 A pairs plus at most 1 B pair (3 + 1 on 8 linears); the most is 8 + 0 on layer 0 `down_proj`.
       - By role, the most A pairs are 4–7 on the attention and MLP-in linears and 8 on `down_proj`, whose input decays slowest.
       - Layer 0 `down_proj` differs slightly from the smoke above (8 on 43 against 8 on 51): the CPU forward pass isn't bit-reproducible (Results 16), so its codes differ.
     - **The census, 26 families (done; `fa74b9e3`; 4 shards on this VM, `r20260930-130117-9cad`, `-962c`, `-eef2`, `-829b`).** I merged their items into node 2's `out/pairing_census` between chunks: the gaussian unit, computed on both, was identical apart from timings. The node job then only writes the summary, and `e47a` preserves it.
       - **0 joint fragments.** But **one side alone reaches a fragment on 4 structured families**: A reaches 16 row pairs on rank1 (96 k pairs), duplicated (99), coherent-gaussian (88) and outliers-first (54), and B reaches 8 column pairs on rank1 (197). On all four the joint search stops at 16 + 1 or 16 + 0.
       - Next are constant (A 14) and outliers-groupstart (A 12). The other 19 admitted families reach 5–7 A pairs and 5–6 B pairs, and joint 4–7 + at most 2.
       - Why: these four families' A rows are copies of one vector before forming (duplicated, coherent-gaussian), scaled copies (rank1), or share one set of outlier channels (outliers-first). Only rank1's weight rows are structured enough for B.
       - **Side order:** the joint search takes whichever side's pair keeps the most k pairs, so on these families it fills A first and leaves B few k pairs. `b1ba546c` adds `--joint-policies` (`B-first`, `balanced`; the default searches and their rng stream are unchanged, checked on gaussian and rank1). **All 26 families with all 3 policies (done; `r20260930-132658-2c66`, `-132658-40b3`, `-132659-1e69`, `-132659-ef0e`, results `art:b2e8f643c4ecad5cb3327fbe45604d6eaaf808826b208905f5722f5f9378f731`, `art:5efb9ac7db30c2b623dc0aa304fb20d8f2a06d23b12d364061335cde4c8f72a0`, `art:48e15d3c593b03e539c54aa8ce8e0ffa1f6bf1091aa62ff8d4fa6abe3dc27ca3`, `art:b765220360c12e1c00716c8aa99cdf58a3e22885550219e7e37b0671fbffe7c6`): 0 joint fragments under every policy.** The closest are 16 + 1 by default (coherent-gaussian, duplicated, rank1), 3 + 8 B-first and 7 + 4 balanced (both rank1). On the other admitted families B-first stops at 0 + 4–6 and balanced at 3–5 + 2–3. These runs' default searches equal `fa74b9e3`'s on all 26 families.
       - **For the ε₈ statement:** at fragment granularity with fixed quadrants the rate is 0 everywhere. Under the adversarial pairing, a per-side statement (A fragments or B fragments) fails on these 4 synthetic families; the joint condition that a Strassen step needs holds on every unit searched. Real activations reach neither.
     - **Llama-3.1-70B, all 70 linears (done 15:40Z, node 2 fill; `r20260930-124539-e47a` preserves both jobs, validation passed): 0 fragments in every mode.**
       - A-only reaches 6 of 16 row pairs on 61 linears, 7 on 5, 8 on 2, 9 on 1 and 12 on 1 (layer 0 `o_proj`, 36 k pairs).
       - B-only reaches 5 of 8 column pairs on 65 and 6 on 5 (the most k pairs at 6 is 41, layer 0 `k_proj`).
       - Joint reaches 6 + 0 on 57, 7 + 0 on 6, 5 + 1 on 3, and 8, 9, 10 and 12 + 0 on one each (12 + 0 on layer 0 `o_proj`).
     - **ε₈'s one-sided check (server.md 14:07Z; the assessor's 14:08Z line in `red-team/ratings.md`): does any per-side fragment open a one-sided route?** The check: is every fragment's row pair either uncredited as a near-duplicate or chain-inexact on its window? (`benchmarks/pouw/sm120_exact/eps8_fragments.py`, `151b4062`, on `pairing.py` at `fd0c7d16`; this VM, `r20260930-152413-5198`, result `art:3728e936e3b121af4e282e1c1a0f4c8e9c46149903464214e0b43c3421e357d8`; Measured, CPU.)
       - **Method:**
         - It replays the census pairing's A-only and B-only searches with node 2's seeds and arguments. Every search's steps equal the stored JSON's (4 of 4 families, both sides), and each search now also returns its fragment's row pairs and matched k pairs.
         - A fragment's window is the atoms holding its first 32 matched k pairs (51–58 atoms; 7 on outliers-first).
         - **Near-duplicate:** codes compared up to sign (approved-weights' registration rule (a)), over the whole row (the assessor's ≥ 15/16) and over each window atom and group (d* = 29 of 32 and 112 of 128).
         - **Chain-inexact:** the census chain from +0 on the sm_120 atom, for each pair's two words against all 512 sampled rows of the other side, on v2 (one chain) and v1 (G = 4). A pair counts as chain-inexact when no column has 32 of the fragment's matched k pairs in atoms exact for both words, the prover's best choice.

| Fragment (side) | Row pairs | Near-duplicates | Chain-inexact v2 / v1 | Neither v2 / v1 | Codes equal: whole row / fragment's k | (word, atom) steps exact, v2 / v1 |
|---|---|---|---|---|---|---|
| rank1 (A) | 16 | 0 | 0 / 0 | **16 / 16** | 2.0–4.7% / 0–14% | 92.5–94.2% / 98.4–99.1% |
| rank1 (B) | 8 | 0 | 0 / 0 | **8 / 8** | 2.1–3.7% / 1.6–10.9% | 93.2–94.7% / 98.8–99.0% |
| duplicated (A) | 16 | 0 | 0 / 0 | **16 / 16** | 2.5–4.2% / 1.6–10.9% | 92.4–94.6% / 98.5–99.0% |
| coherent-gaussian (A) | 16 | 0 | 16 / 0 | 0 / **16** | 2.6–5.1% / 1.6–14.1% | 28.3–31.4% / 89.5–92.9% |
| outliers-first (A) | 16 | 0 | 0 / 0 | **16 / 16** | 1.6–3.8% / 14.1–43.8% | 4.3–4.9% / 98.7–99.1% |

       - **Reading it:**
         - The check's two outs don't hold on these rows.
           - They are distinct rows: at most 5.1% of a row's codes are equal, at most 18 of 32 in any window atom, and no block is past d*.
           - The chain is exact on most of their steps, so on every column but coherent-gaussian's v2 columns the prover finds 32 of the fragment's k pairs in atoms exact for both words.
           - Even the fixed first 32 k pairs are exact for both words on 1–39 of 512 columns per pair at v2 (rank1, duplicated) and on 226–506 at v1 (0–5 on coherent-gaussian).
         - Outliers-first at v2 is exact on only 4–5% of its steps. Its fragment lies in atoms 0–6, where the outlier channels are and where the chain from +0 starts exact. That start is what v2-hot's H_i removes (Results 17).
         - **What a one-sided route could use on such a pair** is a delta, C′ = C + (v − u)·B, whose zeros are the equal codes. That is 0–14% of a fragment's k indices (14–44% on outliers-first, whose outlier channels share one sign vector), unstructured, so the tensor core still runs every product.
         - The assessor's rank argument (a bilinear scheme with single-entry B factors saves no products) excludes the rest whatever the exactness (Derived).
         - **By the 14:07Z rule ("any fragment that is neither sends ε₈ back to per side"), this sends ε₈ back to per side.** The alternative is for the assessor to replace "chain-inexact on its window" with a bound on the delta's density (Needs 8).
       - **Shortcuts:**
         - The chains start from +0, the census's start. The pairing forms by `census.form_s5`, not `form_v1`, so v2-hot's H_i isn't replayed here. On node 2's full units H_i moves the exact share by under 0.8 points on every family (Results 17), so it wouldn't change rank1's or duplicated's verdict (Conjectured).
         - 512 sampled columns.
         - The near-duplicate rule is the approved-weights registration rule applied to A's rows, as the assessor's line does. Pearl-C states no A-side rule.
   - **Shortcuts:**
     - the fixed-quadrant counts above use no permutation; the pairing search is greedy, a lower bound on what an adversary can pair;
     - the pairing samples 512 rows per side and, on k = 28,672, 8,192 of the k indices;
     - candidates are ranked on samples (512 × 512 index pairs at the first step, 65,536 k pairs later) and applied exactly;
     - the three side orders run on the census only; the activations use the default order. A joint fragment contains a fragment of each side, and neither side's search finds one on real activations.
14. **SaltDead on the corrected support** (the 10:18Z order (2); bc-3006c44a's F2 ruling: F flat ±11/4, E ±44).
   - **What changes:** nothing earlier. My census and replays never read salt-dead. The debit is the chain's truncation only (`debit`, `debit_pure`), and `not_needed_share` has no SaltDead term. So Results 1, 4, 9 and 11 stand, with no old share to revise.
   - **#449's support:** its `pearl_c_debit.forming_elements` is a stub that returns 0, and nothing of mine calls it. There is nothing to pass to bc-9914c188 from my side.
   - **Old beside new** (Measured on the card with the CPU twin, 0 gate mismatches; share of formed elements dead, A and B alike):

| Where | Old (F ±44) | New (F ±11/4) |
|---|---|---|
| aligned-spikes-r300, -pm1-r300, -pm1-r444 | 0 | 1/64 exactly (every row; 0 rows over 1/64) |
| the other 22 admitted families | 0 | 0 |
| Llama-3.1-70B linears (all 70), A (tokens) | 0 (admitted) | ≤ 4.4·10⁻⁷; worst admitted row 2.4·10⁻⁴ |
| Llama-3.1-70B linears, B (weights) | 0 (admitted) | ≤ 2.65·10⁻⁵; worst admitted row 4.9·10⁻⁴ |

   - **Within 1/64** everywhere: the aligned spikes reach exactly 1/64, their spike share (2 per 128). No admitted row is over 1/64.
   - **The 7B/70B replay debits:** they don't read salt-dead, so there's nothing to re-run. The 70B linears above are the new shares on real activations.
   - **7 draws per family** (`r20260930-113545-920d`, 175 admitted units): the same, with the new share at most 1/64 and 0 admitted rows over it; the old share is 0 everywhere.
   - **Shortcuts:** 70B layers every 8th only.
15. **The Llama-3.1-70B linears as units** (for 12–14): all 70 are done and in 12, 13 and 14 above. Unsplit, 44 of 70 are admissible whole. 21 lose token rows to the noise floor: row 0 on `gate_proj`/`up_proj` in layers 8–72, and 1–2 rows on 3 `down_proj`s. The other 5 lose weight rows: layer 0's `q`, `k`, `v`, `gate` and `up`, up to 11% of `gate`/`up`'s 28,672. With the pinned split, all 70 are admissible (Results 11).
16. **Per-row debit** (server.md 10:21Z, for P2's per-row seeds; Measured, CPU fill jobs on node 2, running).
   - **Why a re-run:** my earlier outputs kept each tile's debit, not its rows'. So `136dd8fb` adds `row_debit_A` and `row_debit_B` per tile, and I re-ran the same replays with `--cross-words 0`. That skips only the cross-group search and keeps the rng stream, so the tiles reproduce wherever the inputs do (Reproduction, below).
   - **What a row means here:** an A row's debit over its 8 words of a 64×8 tile, and a B row's over its 64. One flagged atom in an A row is:

| ρ | k = 3,584 | k = 8,192 | k = 18,944 | k = 28,672 |
|---|---|---|---|---|
| v1 (1/400) | 0.45ρ | 0.20ρ | 0.08ρ | 0.06ρ |
| v2 (1/1,000) | 1.12ρ | 0.49ρ | 0.21ρ | 0.14ρ |

     So at v2 on Qwen2.5-7B's k = 3,584 linears, **any A row with one flagged atom is over ρ**. "Rows over ρ" there counts rows with one or more flags in 8 words, not rows whose full-width debit exceeds ρ.
   - **64 × 8 tiles** (13:50Z; 7B v1 and 70B v1 done, v2 partial). A row is seen through 8 words:

| Set | Tiles | Worst tile / ρ | A rows | Worst A row / ρ | A rows over ρ | Worst B row / ρ | Dispersion (A) |
|---|---|---|---|---|---|---|---|
| Qwen2.5-7B v1 (done, 9 chunks) | 394 | 0.126 | 25,216 | 1.79 (4 flags) | 31 (0.12%) | 0.61 | 2.06 |
| Qwen2.5-7B v2 (26 of 34 chunks) | 378 | 0.070 | 24,192 | 1.12 (1 flag) | 158 (0.65%) | 0.28 | 1.00 |
| Llama-3.1-70B v1 (done, 20 chunks) | 140 | 0.031 | 8,960 | 0.98 | 0 | 0.12 | 1.93 |
| Llama-3.1-70B v2 (29 of 40) | 109 | 0.023 | 6,976 | 0.98 (2 flags) | 0 | 0.12 | 1.02 |

   - **At full width** (`1b489399`, `--tile-cols 64 --rows-by ratio`; Qwen2.5-7B's `q_proj`, `o_proj` and `gate_proj`, k = 3,584; a token row is seen through 64 words, so one flag is 0.056ρ at v1 and 0.14ρ at v2). Per linear, one 64 × 64 tile of the 64 admissible token rows with the largest max|x|/σ (the outlier-channel rows) and one of random rows:

| Set | Tiles | Worst tile / ρ | Random token rows: worst / ρ, over ρ | Outlier-channel rows (max\|x\|/σ 9–415): worst / ρ, over ρ | Weight rows: worst / ρ | Dispersion (A) |
|---|---|---|---|---|---|---|
| Qwen2.5-7B v1 (done, 7 chunks) | 168 | 0.067 | 0.28, 0 of 5,376 | 0.39, 0 of 5,376 | 0.56, 0 of 10,752 | 1.83 (outlier rows 1.98) |
| Qwen2.5-7B v2 (18 of 28 chunks) | 108 | 0.024 | 0.28, 0 of 3,456 | 0.28, 0 of 3,456 | 0.42, 0 of 6,912 | 0.99 |

   - **Reading it:**
     - At full width **no row is over ρ**, not even the outlier-channel rows: the worst token row is 0.28–0.39ρ, and the worst weight row 0.42–0.56ρ. The narrow tiles' rows over ρ (7B, k = 3,584) are 1–4 flags in 8 words, the resolution, and they don't persist over 64 words.
     - The outlier-channel rows are a little worse at v1 (0.39ρ against 0.28ρ) and no worse at v2.
     - Dispersion is the variance over the mean of a row's flag count: 1 is Poisson. v2 is at 1.0, so its flags look independent of the row. v1 is at 1.8–2.1 in both tile shapes, so its flags cluster, within a word (the promotion's rounding) or within a row; even so, its rows stay under 0.4ρ at full width.
     - For P2's per-row seeds (Needs 7): a per-row cap at ρ over the row's full width in the tile holds with margin on every row measured (≥ 1.8× on weight rows, ≥ 2.5× on token rows); over 8 words it can't be applied at v2.
   - **Reproduction:** 7B v1 reproduces 387 of 394 of the earlier run's tile debits, 70B v1 112 of 112 and 70B v2 65 of 65. The 7 other 7B tiles are all in one chunk (`down-8-11`), and its activations differ (the median max|x|/σ is 32.81 in the earlier run and 32.82 now). So the CPU forward pass is not bit-reproducible between runs; the replay is deterministic given its inputs. The 70B replays read a fixed capture, so they reproduce.
   - **Jobs:** the 64 × 8 re-runs are `r20260930-113549-aff2` (v1) and `-113609-8795` (v2); the full-width ones, `gpu3-fp8-rows-7b-wide-v1.sh` and `-v2-{a,b}.sh`, are `r20260930-120430-f1cc`.
   - **Shortcuts:**
     - the 64 × 8 re-runs sample 2 random tiles per linear;
     - the full-width runs cover 3 of 7's linear roles (the three distinct inputs besides `down_proj`'s), 1 random and 1 outlier tile per linear;
     - partial; the 7B v2 runs use fresh seeds (no earlier run to compare).

17. **v2-hot's full-unit rerun** (the coordinator's 13:56Z order; `fill-candidate-aligned-exact-regions.md`, "Update, 12:30Z"; for bc-b58c6093 and bc-3006c44a).
   - **The replay (the GPU half; done 15:31Z on physical GPU 2, `GPU-1cd543c7`; `gpu3-fp8-v2hot-gpu`, 4 chunks):**
     - 16 families (the census's activation and freeze families, and near-cap), 4 units each (salts `<family>/8192/hot-full/<u>`), 8,192³.
     - Formed on the card by `pearl_c.form_v1` on `SM120_UNPROMOTED` (scheme `04734fb5`).
     - Two chains per unit: from H_i by `pearlc_hot_start.py`'s `const` rule (c₀ = 64, not the column RMS), and from +0 beside it.
     - Each atom's exactness per word is written as row and column bitsets.
     - Code `hot.py` at `e07c34eb`.
   - **Gates, all 0 mismatches:**
     - the self-test (near-cap, rank1 and aligned-spikes-r64 at k = 1,024) against `pearlc_hot_start.units` and `chain`, H against `hot_words` and the closed form, and forming against `form_v1`;
     - per unit, 4 rows' forming, H's closed form, and 64 words per chain against the CPU chain.
   - **Share of (word, atom) steps exact, from H_i and from +0** (Measured, 4 units per family; zero-row admits no A row, so none of its words count):

| Families | From H_i | From +0 | H_i's exponents |
|---|---|---|---|
| zero-slices, sparse10, rank1, saturated, grid-aligned, in-span-FA | 0.948–0.959 | 0.952–0.963 | 14–16 |
| near-cap | 0.925 | 0.932 | 15 |
| aligned-spikes-r64, -pm1-r64 | 0.020, 0.025 | 0.021, 0.027 | 13 |
| aligned-spikes-r160 … r300, -pm1-r220 … r444 | 0.0004–0.0026 | 0.0004–0.0028 | 10–12 |

   - **Reading it:**
     - Most steps are exact on both chains; the hot start takes off 0.3–0.7 points.
     - What the lemma needs is whether whole blocks of the fill candidate's shapes are exact over a window. That is the search's question, now queued.
   - **The window search (done 15:49Z, 2 chunks; `gpu3-fp8-v2hot-search`, `gpus=0`, prio 0, 24 processes; `hot_search.py` at `e07c34eb`; Measured, CPU):**
     - every width of the table at every start from atom 0, both families, per unit and chain;
     - it reports t₀ (1 + the last start with a shape), coverage before t₀ and the closest approach, from H_i beside +0;
     - pass condition: no free-family shape at any start from H_i.
   - **The pass condition fails: 17 of 64 units have a free-family shape from H_i. No unit has a priced-family shape from H_i at any start.**

| Family (4 units) | Free t₀, H_i / +0 | Units with a free shape, H_i / +0 | Priced t₀, H_i / +0 | Coverage before t₀ at w = 4 / 6, H_i | The same, +0 | Widest block found, H_i / +0 (columns) |
|---|---|---|---|---|---|---|
| saturated | **5** / 9 | **4** / 4 | 0 / 1 | 2.7% / 1.7% | 30.2% / 21.9% | 2,400 / 3,840 |
| rank1 | **3** / 8 | **4** / 4 | 0 / 1 | 2.7% / 1.7% | 27.5% / 18.5% | 2,400 / 3,840 |
| in-span-FA | **1** / 6 | **4** / 4 | 0 / 0 | 0 / 0.6% | 19.2% / 12.1% | 1,344 / 3,840 |
| grid-aligned | **1** / 5 | **4** / 4 | 0 / 0 | 0 / 0.6% | 19.2% / 11.5% | 1,344 / 3,840 |
| sparse10 | **1** / 5 | **1** / 4 | 0 / 0 | 0 / 0.6% | 16.5% / 8.7% | 1,344 / 3,840 |
| zero-slices | 0 / 5 | 0 / 4 | 0 / 0 | — | 19.2% / 11.5% | — / 3,840 |
| near-cap | 0 / 8 | 0 / 4 | 0 / 2 | — | 38.5% / 23.1% | — / 3,840 |
| zero-row and the 8 aligned-spikes families | 0 / 0 | 0 / 0 | 0 / 0 | — | — | — |

   - **Reading it:**
     - **Where the hits are:** every hit from H_i is in atoms 0–12, at starts 0–4 and widths 4–12. Saturated has hits at starts 0–4 (widths 6 and 9), rank1 at 0–2, and the other three at start 0 only (width 6, and 9 on in-span-FA).
     - **What they cover:** one or a few blocks of the smallest free shapes. Coverage before t₀ is at most 2.7% of a unit's words (one 1,920 × 960-sized block at width 4), against 16–38% from +0.
     - **What H_i does:** it takes the free family's t₀ from 5–9 atoms down to 0–5, removes every shape on near-cap and zero-slices, and takes the priced family's t₀ from up to 2 down to 0 on every family.
       - The closest approaches on the families without a hit: zero-slices at 0.89 of a free width-6 shape, near-cap at 0.03.
       - Per step, the hot start is still mostly exact (0.90–0.94 at atom 0 on these families; 75% of saturated@1's words are exact over atoms 0–3 from H_i).
     - **Against the CPU sample:** the sample (128–256 rows at k = 1,024, atoms 0, 1, 2, 4, 8 and 16) found no shape from H_i, while the full units have them at starts 0–4. I haven't compared the two methods, so why they differ is open. The fill candidate had expected full units to show what the sample couldn't.
   - **An independent check of 4 hits** (`hot_check.py`, `be5f6c62`; `r20260930-155417-bc74`, `art:0e24e7c092622ff5f116a14b9a260a9c4967f83eb33627604d7ac2f26a4a752e`; Measured, CPU on node 2):
     - Hits checked: saturated@1 at atoms 0–3 and 4–9, rank1@1 at 1–6, grid-aligned@1 at 0–5.
     - Each block is rebuilt from the row bitsets as plain bools: 960 × 1,920, 288 × 1,344, 576 × 672 and 336 × 1,152 (rows × columns).
     - 128 sampled words of each are formed on the CPU by `form_v1` and replayed by `pearlc_hot_start.chain` from H_i. Every word is exact on the whole window, with 0 flag mismatches against the bitsets on every atom replayed.
   - **Preserved by** `r20260930-153135-2062`: both halves' JSONs, logs and npz files, `art:a28af2aeea037001e2650ce733116c9ec8b78e1dabb9a2cb0186653a8573a1ea`. The 513 GiB of bitsets stay on node 2 (4.0 TiB free).
   - **The widest exact region, in columns (14:48Z):**
     - v1's is no longer needed (15:02Z).
     - For v2-hot, the widest block found (`r20260930-155745-0e2c`, `art:e029ee1eac2e1cc0adb78ba9d8b7fb44d049bb567417f952da82d6bcdba13dc3`; Derived from the search's arrays) is:
       - from H_i: 2,400 columns (768 rows over atoms 0–3) on rank1 (2 of 4 units; 1,344 on the other 2) and saturated (4 of 4), and 1,344 on the other three families with hits;
       - from +0: 3,840 on every unit with a shape.
     - All are under the roughly 5,400 columns up to which bc-3006c44a's pre-add closure holds (14:48Z).
     - **Shortcut:** the search tests only the table's side lengths, so these are the widest shapes found, not the widest exact regions. +0's 3,840 is the table's widest side, so it is a floor. A per-word width can still be read from the kept bitsets.
   - **Shortcuts:** 4 units per family at 8,192²; the census's synthetic families and near-cap, no real activations; the search is greedy (the top-N lines in stable order), so its t₀ and coverage are lower bounds on what an adversary finds.
   - **v1-hot's run is cancelled (15:02Z):** never queued, and its scripts on node 2 are renamed `cancelled-*`.
18. **v2-hot's widths against the pre-add closure's floors W*(L)** (the coordinator's 17:00Z order; for bc-3006c44a and bc-b58c6093; the floors are `min-merge-search/widthfloor.py`'s, theory §14, addendum 16:55Z). **Superseded at 17:31Z** (server.md, pinned): clause (c) now counts rows and starts at 6 atoms, and the grant doesn't rely on this check. See Results 19. Kept as a record.
   - **What was measured** (`hot_width.py`, `5ce64802` and `5ee74659`; Measured, CPU on node 2, 30 s per run):
     - Input: Results 17's bitsets from H_i, all 64 units, masked to Π's admitted rows and columns.
     - Windows: every start t = 0–5 and every length L from 9 to 256 − t atoms (1,473 windows).
     - Per window and line count R:
       - Wc is the number of columns exact on every atom of the window with each of the R rows that have the most exact words. This is the search's R_r, the width the order asks for.
       - Wr is the same with the sides swapped: rows exact with the top R columns.
     - R = 16 is an m16n8 atom's height, the smallest a region can have, and is the primary line count. The runs also cover 8–2,048 rows, and the finer 128–256 and 32–64.
     - **Gates:** in every unit, both widths at (t, L) = (0, 9) and (5, 12) were recounted from the bitsets unpacked to bools, at every line count: 0 mismatches. Results 17 checked the bitsets themselves against the CPU chain.
   - **The floors for every L** (Derived): `widthfloor.py`'s own loop over every L from 4 to 256. The wrapper (`floors_all.py`) execs its code unchanged up to the loop and reproduces `widthfloor_p8.0.json` at its nine lengths. The floor is non-increasing in L:

     | L (atoms) | 9 | 10 | 12 | 16 | 24 | 32 | 37 | 64 | 128 | 256 |
     |---|---|---|---|---|---|---|---|---|---|---|
     | W*(L), columns | 2,046.0 | 1,716.1 | 1,260.9 | 840.5 | 633.4 | 518.8 | 468.3 | 313.7 | 216.8 | 175.1 |
   - **Verdict at 16 rows: fail.**
     - 154 of the 1,473 windows are at or over their floor: at every start 0–5, at every length from 9 atoms up to 31–36.
     - **Worst:** saturated, start 0, 10 atoms: 6,519 columns against 1,716, 3.8× the floor.
     - **Longest failing window:** 36 atoms (saturated, starts 0 and 1: 578 and 493 columns against 477.5).
     - Every window of 37 atoms or more passes. The tightest pass is saturated at start 2 over 35 atoms: 484 columns against 487.1, a margin of 3.1.
     - Saturated is the closest family in every failing window. It is also closest in all but 3 of the 447 windows with any width; in those 3 the widest width is 1 column, beyond 70 atoms.
   - **Wc with 16 rows, per length and start.** Each cell gives the widest width and the closest family (sat = saturated). F marks a window at or over its floor. All 1,473 windows at every line count are in `compare.json`.

| L | W*(L) | t=0 | t=1 | t=2 | t=3 | t=4 | t=5 |
|---|---|---|---|---|---|---|---|
| 9 | 2,046.0 | 6,759 (sat) F | 6,584 (sat) F | 6,385 (sat) F | 6,159 (sat) F | 5,849 (sat) F | 5,589 (sat) F |
| 10 | 1,716.1 | 6,519 (sat) F | 6,286 (sat) F | 6,091 (sat) F | 5,772 (sat) F | 5,457 (sat) F | 5,181 (sat) F |
| 11 | 1,461.7 | 6,251 (sat) F | 5,996 (sat) F | 5,730 (sat) F | 5,406 (sat) F | 5,057 (sat) F | 4,721 (sat) F |
| 12 | 1,260.9 | 5,964 (sat) F | 5,647 (sat) F | 5,357 (sat) F | 4,977 (sat) F | 4,674 (sat) F | 4,358 (sat) F |
| 13 | 1,098.8 | 5,610 (sat) F | 5,304 (sat) F | 4,919 (sat) F | 4,611 (sat) F | 4,270 (sat) F | 4,053 (sat) F |
| 14 | 976.7 | 5,278 (sat) F | 4,901 (sat) F | 4,559 (sat) F | 4,218 (sat) F | 3,977 (sat) F | 3,766 (sat) F |
| 15 | 894.5 | 4,906 (sat) F | 4,506 (sat) F | 4,162 (sat) F | 3,919 (sat) F | 3,692 (sat) F | 3,447 (sat) F |
| 16 | 840.5 | 4,531 (sat) F | 4,106 (sat) F | 3,914 (sat) F | 3,664 (sat) F | 3,351 (sat) F | 3,128 (sat) F |
| 18 | 770.6 | 3,810 (sat) F | 3,584 (sat) F | 3,217 (sat) F | 2,982 (sat) F | 2,768 (sat) F | 2,619 (sat) F |
| 20 | 717.5 | 3,207 (sat) F | 2,900 (sat) F | 2,709 (sat) F | 2,505 (sat) F | 2,360 (sat) F | 2,195 (sat) F |
| 22 | 672.4 | 2,665 (sat) F | 2,405 (sat) F | 2,271 (sat) F | 2,119 (sat) F | 1,916 (sat) F | 1,830 (sat) F |
| 24 | 633.4 | 2,232 (sat) F | 2,039 (sat) F | 1,880 (sat) F | 1,764 (sat) F | 1,616 (sat) F | 1,480 (sat) F |
| 26 | 599.5 | 1,885 (sat) F | 1,712 (sat) F | 1,579 (sat) F | 1,421 (sat) F | 1,327 (sat) F | 1,112 (sat) F |
| 28 | 569.5 | 1,557 (sat) F | 1,354 (sat) F | 1,240 (sat) F | 1,055 (sat) F | 959 (sat) F | 850 (sat) F |
| 30 | 542.8 | 1,191 (sat) F | 1,048 (sat) F | 929 (sat) F | 832 (sat) F | 747 (sat) F | 690 (sat) F |
| 32 | 518.8 | 905 (sat) F | 827 (sat) F | 731 (sat) F | 666 (sat) F | 576 (sat) F | 511 (sat) |
| 33 | 507.7 | 821 (sat) F | 719 (sat) F | 655 (sat) F | 564 (sat) F | 504 (sat) | 462 (sat) |
| 34 | 497.2 | 711 (sat) F | 648 (sat) F | 578 (sat) F | 493 (sat) | 449 (sat) | 430 (sat) |
| 35 | 487.1 | 645 (sat) F | 581 (sat) F | 484 (sat) | 440 (sat) | 391 (sat) | 358 (sat) |
| 36 | 477.5 | 578 (sat) F | 493 (sat) F | 430 (sat) | 385 (sat) | 353 (sat) | 329 (sat) |
| 37 | 468.3 | 465 (sat) | 414 (sat) | 393 (sat) | 361 (sat) | 322 (sat) | 294 (sat) |
| 40 | 443.0 | 340 (sat) | 318 (sat) | 291 (sat) | 245 (sat) | 224 (sat) | 217 (sat) |
| 48 | 388.4 | 113 (sat) | 85 (sat) | 79 (sat) | 72 (sat) | 59 (sat) | 57 (sat) |
| 64 | 313.7 | 7 (sat) | 6 (sat) | 9 (sat) | 6 (sat) | 7 (sat) | 8 (sat) |
| 128 to 256 − t | 216.8 to 175.1 | 0 | 0 | 0 | 0 | 0 | 0 |

   - **Per family (Wc, 16 rows):** 7 families fail somewhere. Beside each: its failing windows and its longest failing length.
     - saturated: 154 windows, up to 36 atoms;
     - rank1: 111, up to 29;
     - in-span-FA: 90, up to 25;
     - grid-aligned: 87, up to 25;
     - zero-slices: 83, up to 24;
     - near-cap: 75, up to 24;
     - sparse10: 69, up to 22.

     Zero-row and the 8 aligned-spikes families have width 0 with 16 rows on every window of 9 atoms or more.
   - **By row count (Wc, all 1,473 windows):**

     | Rows | 16 | 32 | 64 | 128 | 160 | 192 | 224 | 240 | 256 |
     |---|---|---|---|---|---|---|---|---|---|
     | Windows at or over W*(L) | 154 | 93 | 48 | 11 | 6 | 2 | 1 | **0** | 0 |

     - The last window to fail is saturated at start 0 over 9 atoms: 2,130 columns with 224 rows.
     - From 240 rows every window passes. The tightest is that same window: 1,988 columns against 2,046, a margin of 58; with 256 rows, 1,880 (margin 166).
   - **The other side (Wr: rows exact with the top 16 columns):**
     - 60 windows fail, up to 19 atoms, mostly on rank1. The worst is rank1 at start 3 over 9 atoms: 3,022 rows against 2,046.
     - With 32 columns one window fails (rank1, start 0, 11 atoms: 1,471 against 1,461.7). From 40 columns none does.
   - **Reading it:**
     - **The floors don't close the windows that start at atoms 0–5 by themselves.** The hot start's first atoms leave regions that are short and very wide: 16 rows exact across 6,759 columns over atoms 0–8 (saturated). W*(L) bounds the width alone, whatever the height.
     - So whether v2-hot's γ stays at 0.362% turns on the smallest region a pre-add composition can use, which is for bc-3006c44a:
       - if it needs at least 240 rows, and at least 40 columns on the B side, every window here passes;
       - if 16 rows suffice, windows of up to 36 atoms fail.
     - Results 17's priced search found no priced-family shape from H_i at any start. W*(L) ignores merges, conversion and fit, so a window over its floor is one that this check can't close, not a composition that pays.
   - **Shortcuts:**
     - **Greedy lines.** The rows are the top R by exact count (stable order), so each width is a lower bound on the widest exact region with R lines. A fail is established: the region exists, and the gates recount it. A pass isn't certified. The 240-row threshold is therefore a lower bound too; a better choice of rows could need more.
     - Rows and columns are any lines, not contiguous or tile-aligned, as the search measures them.
     - 4 units per family at 8,192²; synthetic census families and near-cap only; p_add 8.0 only.
   - **Runs and evidence:**
     - `r20260930-171318-738e` (8–2,048 rows): run directory `art:cd6e29ef3716edbdf31cf0d53ca784f8ea7980e60a6ddaae9de29fa0d8b9c32e`; comparison with the floors (`compare.json`, `table.md`, `floors_all.py`, `floors_all_p8.0.json`, `hw_cmp.py`) `art:74c5e8e87409ab403419b5e7057e2f36d8faf0c60e5918eaf9f3c78667ae0ec2`.
     - `r20260930-172147-a789` (32–64 by 8 and 128–256 by 16): run directory `art:95a9108e70b3368b3a024633692671598abe54c7ebf8c2ca176385799344c1fb`; comparison `art:e8d3d00074fc7eed4461757173f45de33ae8dfef2387ac79fb3ef755a688c315`.
     - `r20260930-172028-76cd` failed at the summary step (it looked for 16 rows in a list without 16; fixed in `5ee74659`). Its 64 units' arrays are identical to `a789`'s: `art:ef54d5beb0db44199ddad0662e98e21ede049b81ef2301c79cc92eea766b7f23`.
19. **Clause (c)'s exact blocks at v2-hot's first atoms** (the coordinator's 17:31Z order, pinned in server.md; for bc-3006c44a, bc-b58c6093 and the assessor bc-d7d4b0d1). The spec is `ttout-restatements.md` §8, "v2-hot's first atoms: the full-unit rerun and the restated row (17:30Z)", table "Exact blocks to rule out (rows × columns)". This supersedes Results 18. **Its verdict is superseded by Results 21**, on the corrected table (4 (start, length) pairs change to found). Kept as a record.
   - **The basis is a greedy search, not a certificate.**
     - A block reported found exists: the gates recount its rows' common columns from bools, and Results 17 checked the bitsets against the CPU chain.
     - A block not found may still exist, since a better choice of rows could find it. The likeliest places are the near misses: start 3 over 9 atoms (0.96 of N) and start 1 over 6 atoms (0.93 of N).
   - **What was measured** (`hot_blocks.py`, `1e595704`; `r20260930-173925-45b9`, 19 minutes on 32 of node 2's CPUs, no GPU; Measured):
     - **Input:** Results 17's bitsets from H_i (`r20260930-153135-2062`), all 64 units, masked to Π's admitted rows and columns.
     - **Windows:** every start t = 0–5 and every length L from 6 to 120 atoms, 1,296 (start, length, block) cases in all.
       - A length with no listed row takes the next listed length's blocks. So 8's block 448 × 2,487 also governs 7 atoms, and 12's governs 10 and 11.
       - The table lists no block past 120 atoms.
     - **The question per block M × N:** do some M rows share N columns, all exact over the window? Three greedy searches answer it:
       - *count* (hot_search's R_r, (b)'s basis): the columns exact with the M rows that have the most exact columns;
       - *isect*, run where count misses: start from the row with the most exact columns, then add M − 1 times the row that keeps the most common columns;
       - *columns first*: the rows exact with the N columns that have the most exact rows. It finds the block if it reaches M rows. It never does here: at most 5 rows, against 448 needed (start 0, 7 atoms).
     - "Widest columns found" below is the better of count and isect with M rows.
     - **Gates:** in every unit, every value at (start, length) = (0, 6) and (5, 9) was recounted from the bitsets unpacked to bools, including the columns shared by the rows isect chose: 0 mismatches. (0, 6) is the failing 6-atom window, so its widths are recounted in all 64 units.
   - **Verdict: fail at 6 atoms and on the 8-atom block.** 11 of the 1,296 cases are found. All are at starts 0–2 and lengths 6–12, on saturated (and rank1 as well at start 0 over 9 and 10 atoms).
     - **6 atoms (288 × 3,982):** found at start 0 in all 4 saturated units, at 4,391–4,458 columns. The widest is saturated@1's 4,458, a margin of −476. Starts 1–5 pass; the closest is start 1 at 3,692, a margin of 290.
     - **8 atoms (448 × 2,487):** the 8-atom window itself passes at every start. The widest there is 1,888 columns (start 0, saturated@1), a margin of 599.
     - The same block also governs 7 atoms, which have no row of their own. At start 0 it is found there in all 4 saturated units: 2,581–2,695 columns, the widest saturated@1's 2,695 (a margin of −208).
     - **9 atoms (144 × 2,047):** found at starts 0, 1 and 2 (3,049, 2,427 and 2,374 columns).
     - **10–12 atoms (192 × 1,261):** found at start 0 over 10, 11 and 12 atoms (1,879, 1,374 and 1,344), at start 1 over 10 and 11 (1,426 and 1,361), and at start 2 over 10 (1,412).
     - **From 13 atoms on,** no block is found at any start.
     - **Tightest block:**
       - among the passes, 144 × 2,047 at start 3 over 9 atoms: 1,958 columns (saturated@1), a margin of 89 (4.3%);
       - among the fails, the closest to passing is 192 × 1,261 at start 0 over 12 atoms: 1,344 columns, a margin of −83.
   - **Count order alone misses the 6- and 7-atom blocks.** At start 0 it reaches 3,573–3,731 columns with 288 rows over 6 atoms, and 1,665–1,976 with 448 rows over 7. Both are under N. Isect reaches 4,391–4,458 and 2,581–2,695. So a check on (b)'s count-order basis would have passed both. The finds at 9–12 atoms come from count order at starts 0 and 1, and from isect at start 2.
   - **Per block and start, up to 16 atoms.** "Worst length" is the governed length where the widest is closest to N. Margin is N minus the widest columns found.

| Block (listed L) | M × N | Start | Worst length | Widest columns found with M rows | Required | Result | Margin (columns) | Closest unit |
|---|---|---|---|---|---|---|---|---|
| 6 | 288 × 3,982 | 0 | 6 | 4,458 (isect) | 3,982 | **fail** | −476 | saturated@1 |
| 6 | 288 × 3,982 | 1 | 6 | 3,692 (isect) | 3,982 | pass | 290 | saturated@1 |
| 6 | 288 × 3,982 | 2 | 6 | 2,972 (isect) | 3,982 | pass | 1,010 | saturated@1 |
| 6 | 288 × 3,982 | 3 | 6 | 2,323 (isect) | 3,982 | pass | 1,659 | saturated@1 |
| 6 | 288 × 3,982 | 4 | 6 | 1,851 (isect) | 3,982 | pass | 2,131 | saturated@1 |
| 6 | 288 × 3,982 | 5 | 6 | 1,397 (isect) | 3,982 | pass | 2,585 | saturated@1 |
| 8 | 448 × 2,487 | 0 | 7 | 2,695 (isect) | 2,487 | **fail** | −208 | saturated@1 |
| 8 | 448 × 2,487 | 1 | 7 | 1,910 (isect) | 2,487 | pass | 577 | saturated@1 |
| 8 | 448 × 2,487 | 2 | 7 | 1,360 (isect) | 2,487 | pass | 1,127 | saturated@1 |
| 8 | 448 × 2,487 | 3 | 7 | 978 (isect) | 2,487 | pass | 1,509 | saturated@1 |
| 8 | 448 × 2,487 | 4 | 7 | 651 (isect) | 2,487 | pass | 1,836 | saturated@2 |
| 8 | 448 × 2,487 | 5 | 7 | 524 (isect) | 2,487 | pass | 1,963 | rank1@4 |
| 9 | 144 × 2,047 | 0 | 9 | 3,049 (count) | 2,047 | **fail** | −1,002 | saturated@1 |
| 9 | 144 × 2,047 | 1 | 9 | 2,427 (count) | 2,047 | **fail** | −380 | saturated@1 |
| 9 | 144 × 2,047 | 2 | 9 | 2,374 (isect) | 2,047 | **fail** | −327 | saturated@3 |
| 9 | 144 × 2,047 | 3 | 9 | 1,958 (isect) | 2,047 | pass | 89 | saturated@1 |
| 9 | 144 × 2,047 | 4 | 9 | 1,588 (isect) | 2,047 | pass | 459 | saturated@1 |
| 9 | 144 × 2,047 | 5 | 9 | 1,313 (isect) | 2,047 | pass | 734 | saturated@2 |
| 12 | 192 × 1,261 | 0 | 10 | 1,879 (count) | 1,261 | **fail** (L = 10, 11, 12) | −618 | saturated@1 |
| 12 | 192 × 1,261 | 1 | 10 | 1,426 (count) | 1,261 | **fail** (L = 10, 11) | −165 | saturated@1 |
| 12 | 192 × 1,261 | 2 | 10 | 1,412 (isect) | 1,261 | **fail** | −151 | saturated@1 |
| 12 | 192 × 1,261 | 3 | 10 | 1,075 (isect) | 1,261 | pass | 186 | saturated@1 |
| 12 | 192 × 1,261 | 4 | 10 | 831 (isect) | 1,261 | pass | 430 | saturated@2 |
| 12 | 192 × 1,261 | 5 | 10 | 651 (isect) | 1,261 | pass | 610 | saturated@2 |
| 14 | 256 × 841 | 0 | 13 | 663 (isect) | 841 | pass | 178 | saturated@2 |
| 14 | 256 × 841 | 1 | 13 | 486 (isect) | 841 | pass | 355 | saturated@2 |
| 14 | 256 × 841 | 2 | 13 | 352 (isect) | 841 | pass | 489 | saturated@2 |
| 14 | 256 × 841 | 3 | 13 | 243 (isect) | 841 | pass | 598 | saturated@2 |
| 14 | 256 × 841 | 4 | 13 | 187 (isect) | 841 | pass | 654 | rank1@4 |
| 14 | 256 × 841 | 5 | 13 | 144 (isect) | 841 | pass | 697 | rank1@4 |
| 16 | 216 × 841 | 0 | 15 | 457 (isect) | 841 | pass | 384 | saturated@2 |
| 16 | 216 × 841 | 1 | 15 | 320 (isect) | 841 | pass | 521 | saturated@1 |
| 16 | 216 × 841 | 2 | 15 | 231 (isect) | 841 | pass | 610 | saturated@2 |
| 16 | 216 × 841 | 3 | 15 | 168 (isect) | 841 | pass | 673 | saturated@2 |
| 16 | 216 × 841 | 4 | 15 | 144 (isect) | 841 | pass | 697 | rank1@4 |
| 16 | 216 × 841 | 5 | 15 | 112 (isect) | 841 | pass | 729 | rank1@4 |

   - **From 17 atoms on,** every block passes at every start. Each row gives the block's closest start and length. Every start and length is in `summary.json`.

| Block (listed L) | M × N | Lengths | Closest start and length | Widest columns found with M rows | Required | Result | Margin (columns) | Closest unit |
|---|---|---|---|---|---|---|---|---|
| 17 | 144 × 1,056 | 17 | t = 0, L = 17 | 465 | 1,056 | pass | 591 | saturated@1 |
| 17 | 1,056 × 634 | 17 | t = 2, L = 17 | 20 | 634 | pass | 614 | rank1@4 |
| 18 | 96 × 1,344 | 18 | t = 0, L = 18 | 694 | 1,344 | pass | 650 | saturated@1 |
| 18 | 144 × 634 | 18 | t = 0, L = 18 | 350 | 634 | pass | 284 | saturated@1 |
| 21 | 96 × 1,152 | 19–21 | t = 0, L = 19 | 543 | 1,152 | pass | 609 | saturated@1 |
| 21 | 1,152 × 634 | 19–21 | t = 1, L = 19 | 13 | 634 | pass | 621 | rank1@4 |
| 24 | 192 × 634 | 22–24 | t = 0, L = 22 | 67 | 634 | pass | 567 | saturated@2 |
| 28 | 128 × 960 | 25–28 | t = 0, L = 25 | 68 | 960 | pass | 892 | saturated@2 |
| 28 | 960 × 519 | 25–28 | t = 0, L = 25 | 9 | 519 | pass | 510 | rank1@4 |
| 30 | 128 × 896 | 29–30 | t = 0, L = 29 | 36 | 896 | pass | 860 | saturated@2 |
| 30 | 896 × 519 | 29–30 | t = 0, L = 30 | 7 | 519 | pass | 512 | rank1@4 |
| 33 | 144 × 528 | 31–33 | t = 0, L = 31 | 25 | 528 | pass | 503 | saturated@1 |
| 33 | 264 × 314 | 31–33 | t = 0, L = 31 | 15 | 314 | pass | 299 | saturated@1 |
| 36 | 96 × 672 | 34–36 | t = 1, L = 34 | 25 | 672 | pass | 647 | saturated@2 |
| 36 | 144 × 314 | 34–36 | t = 1, L = 34 | 17 | 314 | pass | 297 | saturated@2 |
| 40 | 64 × 3,840 | 37–40 | t = 0, L = 37 | 28 | 3,840 | pass | 3,812 | saturated@2 |
| 40 | 3,840 × 314 | 37–40 | t = 2, L = 37 | 1 | 314 | pass | 313 | rank1@2 |
| 42 | 96 × 576 | 41–42 | t = 0, L = 41 | 14 | 576 | pass | 562 | saturated@2 |
| 42 | 576 × 314 | 41–42 | t = 0, L = 41 | 4 | 314 | pass | 310 | saturated@1 |
| 48 | 64 × 2,400 | 43–48 | t = 0, L = 43 | 16 | 2,400 | pass | 2,384 | saturated@1 |
| 48 | 2,400 × 314 | 43–48 | t = 0, L = 43 | 1 | 314 | pass | 313 | zero-slices@1 |
| 50 | 64 × 2,304 | 49–50 | t = 0, L = 49 | 11 | 2,304 | pass | 2,293 | saturated@2 |
| 50 | 2,304 × 314 | 49–50 | t = 0, L = 49 | 1 | 314 | pass | 313 | sparse10@1 |
| 60 | 64 × 1,920 | 51–60 | t = 0, L = 51 | 11 | 1,920 | pass | 1,909 | saturated@4 |
| 60 | 1,920 × 314 | 51–60 | t = 0, L = 51 | 1 | 314 | pass | 313 | zero-slices@1 |
| 72 | 64 × 1,600 | 61–72 | t = 0, L = 61 | 6 | 1,600 | pass | 1,594 | saturated@1 |
| 72 | 1,600 × 64 | 61–72 | t = 0, L = 61 | 1 | 64 | pass | 63 | sparse10@1 |
| 75 | 64 × 1,536 | 73–75 | t = 0, L = 74 | 5 | 1,536 | pass | 1,531 | rank1@3 |
| 75 | 1,536 × 64 | 73–75 | t = 1, L = 73 | 1 | 64 | pass | 63 | saturated@1 |
| 120 | 64 × 1,280 | 76–120 | t = 0, L = 76 | 4 | 1,280 | pass | 1,276 | saturated@1 |
| 120 | 1,280 × 64 | 76–120 | t = 0, L = 76 | 1 | 64 | pass | 63 | in-span-FA@1 |

   - **Reading it:**
     - Clause (c), as measured, fails at starts 0–2 over 6–12 atoms on saturated (and rank1 at start 0). From start 3 on, and from 13 atoms on, nothing is found.
     - The finds are §8's rectangles: rows whose H_i ends in zeros stay exact on the same columns while the accumulator is still in H_i's binade.
     - Under §8, a failure invokes §3's fallback (γ ≤ 0.41%, Estimated). That call belongs to bc-3006c44a and the assessor.
   - **Shortcuts:**
     - 4 units per family at 8,192²; the census's synthetic families and near-cap only.
     - Only the blocks the table lists, placed as rows × columns (no transposed placement).
     - The found 7- and 9–12-atom blocks are counted by code gated at (0, 6) and (5, 9), but not recounted at their own windows.
     - Nothing is replayed on the CPU chain here; `hot_check.py` did that for 4 of Results 17's hits.
   - **Evidence:**
     - the run directory (unit records, summary, log): `art:c93eb0e2b2b7d8a2884ceac48239d1b2274166b81f7545e58b24f48335b274f6`;
     - the per-block tables and their scripts: `art:798224c772afb299a45f7d78c0710771f86328db792716f47ff8fb048dced3d4`, which supersedes `art:cfd0e0f2…`, the grid alone;
     - the persistent output on node 2: `/workspace/pouw/gpu3-fp8/out/v2hot-blocks/`.

20. **Clause (b) on the assessor's most persistent cancelling family, on full units** (the coordinator's 18:15Z order; server.md 17:45Z; the assessor's rating at t₀ = 6 in `internal/pouw/red-team/ratings.md` 17:45Z; for the assessor bc-d7d4b0d1 and bc-b58c6093). **Results 21 re-judges it on the corrected table:** nothing changes at starts 6–16, and it adds starts 4–5, where start 4 fails.
   - **Clause (b)** of `no-aligned-exact-region/sm120-unpromoted-hot` says no wide exact block starts at atom 6 or later. The assessor's CPU search sampled 64 rows × 512 columns at k = 2,048. This checks its most persistent family, `cancel-pair@t4`, on full units.
   - **Verdict: pass.** No block of §8's table is found at any start from 6 to 16, at any length: 0 of 2,376 (start, length, block) cases.
     - **Tightest:** 144 × 2,047 at start 6 over 9 atoms. The widest set found is 1,505 columns (unit 2), a margin of 542 (26% of N).
     - **Next closest:** 192 × 1,261 at start 6 over 10 atoms, with 801 columns (a margin of 460, 36%).
     - **The 6-atom block (288 × 3,982):** 1,518 columns at start 6 (38% of N).
     - **8's block (448 × 2,487):** 545 columns over 7 atoms at start 6.
   - **The basis is a greedy search, not a certificate.** It is the same three searches as Results 19: count order, intersection, and columns first. A block found would exist; a miss doesn't rule one out. Here no search comes within a quarter of N, and the columns-first search never finds a single row.
   - **The family is in the domain.** In every unit all 8,192 rows of A and all 8,192 columns of B are live (`pearl_c.live_row`) and admitted by Π (noise floor and liveness) (Measured).
   - **The replay** (`hot.py` at `0f7c4b45`; Measured on one RTX PRO 6000, sm_120):
     - **Draws:** `cancel-pair@t4` as `hot_late_start.py` draws it: B's columns Student-t(4) with B[2l+1] = B[2l]; A[2l] = v and A[2l+1] = −v, where v's first half is random signs and the rest N(0, 0.1²).
       - The generator is seeded by the SHA-256 of the unit salt `cancel-pair@t4/8192/hot-full/<u>`. The law is the assessor's but the draws are not, since its seed is Python's per-process string hash.
     - **Units:** 4 units of 8,192 × 8,192 at k = 8,192, formed on the card by `pearl_c.form_v1` on `SM120_UNPROMOTED`.
     - **Chains:** the unpromoted chain from H_i (rule `const`, c₀ = 64) and from +0. Only the chain from H_i is searched.
     - **Gates, all 0 mismatches:**
       - the self-test on near-cap, rank1 and aligned-spikes-r64 at k = 1,024;
       - per unit, 4 rows and 8,192 elements of forming;
       - 64 words over all 256 atoms of both chains, in both layouts, against `pearlc_hot_start.chain`;
       - H_i against the closed form.
     - **Run:** fill job `gpu3-fp8-v2hot-cancel-replay` (prio 1, `gpus=1`), 18:32–18:35Z in one chunk, about 12 s per unit on the card.
     - **The first attempt failed:** at 18:28Z the item `cancel-pair@t4@1` was split at its first `@`. `0f7c4b45` fixes it. That attempt's log is in the evidence.
   - **Exact steps from H_i** (Measured, unit 1; the other units agree to within 0.3 points):
     - by atom: 90.7% at atom 0, 96.9% at atom 5, 97.2% at atom 6 and 97.6% at atom 16;
     - over all 256 atoms: 95.9%, against 96.3% from +0.
     - So the per-step rate does rise after the start, as the assessor's sample showed. Blocks still don't form, because the inexact steps fall on different words.
   - **The search** (`hot_blocks.py` at `bdef5bbc`, `--per-start`; Measured, CPU only):
     - **Coverage:** every start t = 6–16 and every length L from 6 to 256 − t, masked to Π's admitted rows and columns.
       - A length with no listed row takes the next listed length's blocks. Past 120 atoms no block governs, and the count at 64 rows is 0 columns at every such length.
     - **Gates:** in each of the 44 (unit, start) tasks, every value at L = 6 and L = 9 was recounted from the bitsets unpacked to bools, including the rows the intersection search chose: 88 windows, 0 mismatches.
     - **Run:** fill job `gpu3-fp8-v2hot-cancel-blocks` (prio 1, `gpus=0`), 18:44–19:04Z in 4 chunks.
       - The first two chunks ran all 44 tasks at once on the fill's 32 shared cores. Under that contention a task took about 6.5 minutes, so most were cut off at the budget.
       - `bdef5bbc` makes each task save its progress every minute and resume after the saved plane, and the next two chunks finished them.
   - **Widths fall with the start**, although the per-step rate rises. The best width over each block's lengths, by start:
     - the 6-atom block (288 × 3,982): 1,518 at start 6, then 1,255, 994, 839, 712, 564, 463, 387, 334, 314, and 268 at start 16;
     - the 9-atom block (144 × 2,047): 1,505 at start 6, then 1,317, 1,074, 880, 767, 655, 583, 499, 442, 386, and 341 at start 16;
     - 8's block over 7 atoms (448 × 2,487): from 545 at start 6 to 80 at start 16;
     - 12's block over 10 atoms (192 × 1,261): from 801 at start 6 to 132 at start 16.
   - **Against the census families a start earlier** (Results 19, start 5): saturated reached 1,397 (6 atoms) and 1,313 (9 atoms). `cancel-pair@t4` at start 6 is a little wider than that, at 1,518 and 1,505, but at most 74% of any block's N.
   - **Against the assessor's sample** (count order, 64 rows × 512 columns, k = 2,048; `/workspace/pouw/fill-out/assessor-late-start/late-start-64x512.json`): at start 6 over 6 atoms, 16 rows share 53% of the columns, 32 rows 12% and 64 rows none. On full units, 288 rows share 18.5% of 8,192 columns by the intersection search. The sizes and searches differ, so this is context, not a comparison.
   - **Per block over starts 6–16.** Each row gives the block's closest start and length; every start and length is in `summary.json`. Units are `cancel-pair@t4@1`–`@4`, written u1–u4.

| Block (listed L) | M × N | Lengths | Closest start and length | Widest columns found with M rows | Required | Result | Margin (columns) | Closest unit |
|---|---|---|---|---|---|---|---|---|
| 6 | 288 × 3,982 | 6 | t = 6, L = 6 | 1,518 (isect) | 3,982 | pass | 2,464 | u2 |
| 8 | 448 × 2,487 | 7–8 | t = 6, L = 7 | 545 (isect) | 2,487 | pass | 1,942 | u2 |
| 9 | 144 × 2,047 | 9 | t = 6, L = 9 | 1,505 (isect) | 2,047 | pass | 542 | u2 |
| 12 | 192 × 1,261 | 10–12 | t = 6, L = 10 | 801 (isect) | 1,261 | pass | 460 | u2 |
| 14 | 256 × 841 | 13–14 | t = 6, L = 13 | 187 (isect) | 841 | pass | 654 | u1 |
| 16 | 216 × 841 | 15–16 | t = 6, L = 15 | 138 (isect) | 841 | pass | 703 | u2 |
| 17 | 144 × 1,056 | 17 | t = 6, L = 17 | 191 (isect) | 1,056 | pass | 865 | u1 |
| 17 | 1,056 × 634 | 17 | t = 6, L = 17 | 13 (isect) | 634 | pass | 621 | u2 |
| 18 | 96 × 1,344 | 18 | t = 6, L = 18 | 311 (isect) | 1,344 | pass | 1,033 | u1 |
| 18 | 144 × 634 | 18 | t = 6, L = 18 | 153 (isect) | 634 | pass | 481 | u1 |
| 21 | 96 × 1,152 | 19–21 | t = 6, L = 19 | 265 (isect) | 1,152 | pass | 887 | u1 |
| 21 | 1,152 × 634 | 19–21 | t = 6, L = 19 | 10 (isect) | 634 | pass | 624 | u2 |
| 24 | 192 × 634 | 22–24 | t = 6, L = 22 | 40 (isect) | 634 | pass | 594 | u2 |
| 28 | 128 × 960 | 25–28 | t = 6, L = 25 | 45 (isect) | 960 | pass | 915 | u2 |
| 28 | 960 × 519 | 25–28 | t = 6, L = 25 | 7 (isect) | 519 | pass | 512 | u3 |
| 30 | 128 × 896 | 29–30 | t = 6, L = 29 | 27 (isect) | 896 | pass | 869 | u4 |
| 30 | 896 × 519 | 29–30 | t = 6, L = 29 | 6 (isect) | 519 | pass | 513 | u2 |
| 33 | 144 × 528 | 31–33 | t = 7, L = 31 | 21 (isect) | 528 | pass | 507 | u4 |
| 33 | 264 × 314 | 31–33 | t = 7, L = 31 | 13 (isect) | 314 | pass | 301 | u2 |
| 36 | 96 × 672 | 34–36 | t = 6, L = 34 | 21 (isect) | 672 | pass | 651 | u2 |
| 36 | 144 × 314 | 34–36 | t = 6, L = 34 | 15 (isect) | 314 | pass | 299 | u2 |
| 40 | 64 × 3,840 | 37–40 | t = 6, L = 37 | 25 (isect) | 3,840 | pass | 3,815 | u1 |
| 40 | 3,840 × 314 | 37–40 | t = 6, L = 37 | 1 (isect) | 314 | pass | 313 | u1 |
| 42 | 96 × 576 | 41–42 | t = 6, L = 41 | 13 (isect) | 576 | pass | 563 | u1 |
| 42 | 576 × 314 | 41–42 | t = 8, L = 41 | 5 (isect) | 314 | pass | 309 | u3 |
| 48 | 64 × 2,400 | 43–48 | t = 6, L = 43 | 17 (isect) | 2,400 | pass | 2,383 | u3 |
| 48 | 2,400 × 314 | 43–48 | t = 6, L = 43 | 1 (isect) | 314 | pass | 313 | u1 |
| 50 | 64 × 2,304 | 49–50 | t = 6, L = 49 | 12 (isect) | 2,304 | pass | 2,292 | u3 |
| 50 | 2,304 × 314 | 49–50 | t = 6, L = 49 | 1 (isect) | 314 | pass | 313 | u1 |
| 60 | 64 × 1,920 | 51–60 | t = 6, L = 51 | 11 (isect) | 1,920 | pass | 1,909 | u2 |
| 60 | 1,920 × 314 | 51–60 | t = 11, L = 52 | 2 (isect) | 314 | pass | 312 | u2 |
| 72 | 64 × 1,600 | 61–72 | t = 6, L = 61 | 7 (isect) | 1,600 | pass | 1,593 | u1 |
| 72 | 1,600 × 64 | 61–72 | t = 6, L = 61 | 1 (isect) | 64 | pass | 63 | u1 |
| 75 | 64 × 1,536 | 73–75 | t = 6, L = 73 | 5 (isect) | 1,536 | pass | 1,531 | u1 |
| 75 | 1,536 × 64 | 73–75 | t = 6, L = 73 | 1 (isect) | 64 | pass | 63 | u1 |
| 120 | 64 × 1,280 | 76–120 | t = 6, L = 76 | 5 (isect) | 1,280 | pass | 1,275 | u4 |
| 120 | 1,280 × 64 | 76–120 | t = 6, L = 76 | 1 (isect) | 64 | pass | 63 | u1 |

   - **Shortcuts:**
     - a greedy search, not a certificate;
     - one family, 4 units;
     - the draws are not the assessor's own (the same law);
     - only the chain from H_i is searched (the +0 bitsets are written);
     - only the blocks the table lists, placed as rows × columns;
     - the 16 census families were searched at starts 0–5 only (Results 19), not 6–16.
   - **Evidence:**
     - the replay's records (unit records, masks, H_i, self-test, logs, code hashes, but not the bitsets), the search's per-task files and summary, and the job scripts: `art:d5792585c0462d549e612c1b561b9007f57570def15fccebf3b1948f46ca0a01`, preserved by `r20260930-190625-348e`;
     - the trees shipped by `r20260930-182541-cc16`, `-183127-1bb0` and `-185538-212f`;
     - the bitsets (32 GiB) on node 2 in `/workspace/pouw/gpu3-fp8/out/v2hot-cancel/`, and the search output in `/workspace/pouw/gpu3-fp8/out/v2hot-cancel-blocks/`.

21. **v2-hot's blocks against the corrected table, on the census and on `cancel-pair@t4`** (the coordinator's 21:12Z order; server.md PINNED 18:42Z; for bc-b58c6093, bc-3006c44a and the assessor bc-d7d4b0d1). **Its clause (c) verdict is superseded by Results 22:** clause (c) now reads the row-dependent staircase, on which nothing is found at any start. The curves and widths below still stand. Kept as a record.
   - **Inputs:**
     - the table is bc-b58c6093's `internal/pouw/cheap-binding/v2hot-blocks-corrected.json` (sha256 `76436412…ed37`): 914 blocks, 64–640 rows × 176–5,462 columns, at every length 5–256;
     - the floors are `widthfloor-all-p8.0.json` (sha256 `b99516e4…43d7`). Each W* is ⌈width_floor⌉, checked on load. Length 4 has no block, since its W* (10,726) exceeds a unit's 8,192 columns.
   - **This supersedes Results 19's verdict and extends Results 20 to starts 4–5.** Changes are marked **[changed]**.
   - **Verdict by start** (Measured; greedy: a block found exists, but a miss is not a certificate):

| Starts | 16 census families (64 units) | `cancel-pair@t4` (4 units) |
|---|---|---|
| 0–2 | **fail:** 15 of 2,730 (start, length, block) cases found, on saturated (plus rank1 at start 0 over 9 and 10 atoms). Tightest pass: 1,110 of 1,152 columns with 144 rows (start 1, 13 atoms, saturated@2), a margin of 42 (3.6%) | not run |
| 3 | pass: 0 of 902. Tightest: 1,958 of 2,047 (144 rows, 9 atoms, saturated@1), 89 (4.3%) | not run |
| 4–5 | pass: 0 of 1,792. Tightest: 1,588 of 2,047 (start 4, 9 atoms, saturated@1), 459 (22.4%) | **fail at start 4 [new]:** 144 rows share 2,091 columns over atoms 4–12 (unit 2), against N = 2,047; certified. Start 5 passes; its tightest is 1,760 of 2,047 (9 atoms, unit 2), 287 (14.0%). The group's tightest pass is 1,664 of 1,717 (start 4, 10 atoms, unit 2), 53 (3.1%) |
| 6–16 | pass: 0 of 9,570. Tightest: 1,054 of 2,047 (start 6, 9 atoms, saturated@2), 993 (48.5%) | pass: 0 of 9,570. Tightest: 1,505 of 2,047 (start 6, 9 atoms, unit 2), 542 (26.5%) |

   - The order asked for `cancel-pair@t4` at starts 6–16. I ran it from start 4, so that the 4–5 group covers both sets (one extra chunk). It wasn't run at starts 0–3.
   - **Where Results 19 changes** (census, starts 0–5, the same 64 units' bitsets):
     - **8 atoms is now found [changed].** The corrected block is 288 × 2,487 (Results 19's was 448 × 2,487). At start 0, 288 rows share 2,848 columns (saturated@1, certified). Results 19's 448 rows reached 1,888.
     - **13 atoms is now found at start 0 [changed]:** 144 rows share 1,437 columns against 1,152 (saturated@1, certified). Results 19's "from 13 atoms on, nothing is found" now holds from 14 atoms. The closest from 14 is start 0 over 14 atoms: 1,108 of 1,152, a margin of 44 (3.8%).
     - **12 atoms at start 1 and 11 atoms at start 2 are now found [changed].** The table now has 144 × 1,717 (10 atoms), 144 × 1,462 (11) and 144 × 1,261 (12), where Results 19 took 192 × 1,261 for all three. Start 1 over 12 atoms reaches 1,441 of 1,261, and start 2 over 11 reaches 1,476 of 1,462 (saturated@1 only; both certified).
     - **7 atoms has its own block [changed], with the same verdict:** 288 × 3,097, found at start 0 at 3,669 columns. Results 19 used 8's block there (2,695 with 448 rows).
     - **5 atoms is new:** 640 × 5,462 passes at every start (widest 3,744 at start 0, a margin of 1,718).
     - **Unchanged:** 6 atoms (4,458 of 3,982 at start 0, in all 4 saturated units), 9 atoms at starts 0–2, and a pass at every case of starts 3–5. Starts 3–5 are now measured on the corrected table; the tightest is still 1,958 of 2,047 at start 3.
     - **Wider at 9 atoms:** start 0 reaches 3,494 columns by the intersection path, where Results 19 reported 3,049 by count order (its intersection search ran only where count order missed).
     - In all, 4 of the 690 (start, length) pairs both tables cover change, each from pass to found: start 0 at 8 and 13 atoms, start 1 at 12, start 2 at 11.
   - **Where Results 20 changes** (`cancel-pair@t4`, starts 6–16): **nothing.** 0 of 9,570 cases are found (Results 20: 0 of 2,376 on the old table), and the tightest is the same 1,505 columns at start 6 over 9 atoms. **Start 4 is new** (Results 20 began at 6), and it fails.
   - **Census, 5–13 atoms, starts 0–5.** A cell is the widest columns found with M rows, and (+x) the margin N − widest. **found** names the widest unit. Every (start, length, block), with its closest family and unit, is in `summary.json`.

| L | M × N | t = 0 | t = 1 | t = 2 | t = 3 | t = 4 | t = 5 |
|---|---|---|---|---|---|---|---|
| 5 | 640 × 5,462 | 3,744 (+1,718) | 2,739 (+2,723) | 1,906 (+3,556) | 1,322 (+4,140) | 908 (+4,554) | 706 (+4,756) |
| 6 | 288 × 3,982 | **4,458 found** (saturated@1) | 3,692 (+290) | 2,972 (+1,010) | 2,323 (+1,659) | 1,851 (+2,131) | 1,397 (+2,585) |
| 7 | 288 × 3,097 | **3,669 found** (saturated@1) | 2,880 (+217) | 2,230 (+867) | 1,722 (+1,375) | 1,282 (+1,815) | 991 (+2,106) |
| 8 | 288 × 2,487 | **2,848 found** (saturated@1) | 2,155 (+332) | 1,679 (+808) | 1,201 (+1,286) | 907 (+1,580) | 684 (+1,803) |
| 9 | 144 × 2,047 | **3,494 found** (saturated@1) | **2,896 found** (saturated@3) | **2,374 found** (saturated@3) | 1,958 (+89) | 1,588 (+459) | 1,313 (+734) |
| 10 | 144 × 1,717 | **2,851 found** (saturated@1) | **2,314 found** (saturated@3) | **1,902 found** (saturated@1) | 1,517 (+200) | 1,227 (+490) | 999 (+718) |
| 11 | 144 × 1,462 | **2,282 found** (saturated@3) | **1,850 found** (saturated@1) | **1,476 found** (saturated@1) | 1,186 (+276) | 925 (+537) | 737 (+725) |
| 12 | 144 × 1,261 | **1,831 found** (saturated@1) | **1,441 found** (saturated@1) | 1,134 (+127) | 889 (+372) | 697 (+564) | 529 (+732) |
| 13 | 144 × 1,152 | **1,437 found** (saturated@1) | 1,110 (+42) | 870 (+282) | 660 (+492) | 506 (+646) | 396 (+756) |
| 13 | 192 × 1,099 | 1,011 (+88) | 750 (+349) | 567 (+532) | 416 (+683) | 310 (+789) | 236 (+863) |

   - **Census, 5–13 atoms, starts 6–16:**

| L | M × N | t = 6 | t = 7 | t = 8 | t = 9 | t = 10 | t = 11 | t = 12 | t = 13 | t = 14 | t = 15 | t = 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 640 × 5,462 | 642 (+4,820) | 712 (+4,750) | 542 (+4,920) | 549 (+4,913) | 431 (+5,031) | 400 (+5,062) | 319 (+5,143) | 295 (+5,167) | 318 (+5,144) | 514 (+4,948) | 442 (+5,020) |
| 6 | 288 × 3,982 | 1,126 (+2,856) | 901 (+3,081) | 883 (+3,099) | 823 (+3,159) | 695 (+3,287) | 663 (+3,319) | 605 (+3,377) | 567 (+3,415) | 503 (+3,479) | 680 (+3,302) | 612 (+3,370) |
| 7 | 288 × 3,097 | 753 (+2,344) | 735 (+2,362) | 643 (+2,454) | 588 (+2,509) | 525 (+2,572) | 450 (+2,647) | 417 (+2,680) | 421 (+2,676) | 375 (+2,722) | 473 (+2,624) | 355 (+2,742) |
| 8 | 288 × 2,487 | 550 (+1,937) | 505 (+1,982) | 484 (+2,003) | 446 (+2,041) | 405 (+2,082) | 351 (+2,136) | 282 (+2,205) | 260 (+2,227) | 273 (+2,214) | 324 (+2,163) | 231 (+2,256) |
| 9 | 144 × 2,047 | 1,054 (+993) | 855 (+1,192) | 692 (+1,355) | 731 (+1,316) | 677 (+1,370) | 550 (+1,497) | 502 (+1,545) | 481 (+1,566) | 413 (+1,634) | 496 (+1,551) | 430 (+1,617) |
| 10 | 144 × 1,717 | 791 (+926) | 646 (+1,071) | 590 (+1,127) | 632 (+1,085) | 526 (+1,191) | 463 (+1,254) | 381 (+1,336) | 337 (+1,380) | 322 (+1,395) | 383 (+1,334) | 288 (+1,429) |
| 11 | 144 × 1,462 | 590 (+872) | 513 (+949) | 484 (+978) | 475 (+987) | 378 (+1,084) | 325 (+1,137) | 286 (+1,176) | 235 (+1,227) | 240 (+1,222) | 276 (+1,186) | 206 (+1,256) |
| 12 | 144 × 1,261 | 422 (+839) | 414 (+847) | 385 (+876) | 344 (+917) | 298 (+963) | 244 (+1,017) | 229 (+1,032) | 200 (+1,061) | 167 (+1,094) | 200 (+1,061) | 154 (+1,107) |
| 13 | 144 × 1,152 | 331 (+821) | 317 (+835) | 272 (+880) | 272 (+880) | 231 (+921) | 180 (+972) | 165 (+987) | 145 (+1,007) | 121 (+1,031) | 155 (+997) | 119 (+1,033) |
| 13 | 192 × 1,099 | 221 (+878) | 209 (+890) | 182 (+917) | 190 (+909) | 154 (+945) | 122 (+977) | 113 (+986) | 98 (+1,001) | 84 (+1,015) | 99 (+1,000) | 86 (+1,013) |

   - **Census, the closest passing block at each start, over all lengths.** From 14 atoms the closest at every start is 144 × 1,152 over 14 atoms: 1,108 columns at start 0 (a margin of 44), 841 at start 1 and 647 at start 2, falling to 95 at start 16.

| Start | Cases found | Closest passing block | Length | Widest columns found with M rows | Required | Margin | Closest unit |
|---|---|---|---|---|---|---|---|
| 0 | 8 | 144 × 1,152 | 14 | 1,108 | 1,152 | 44 (3.8%) | saturated@2 |
| 1 | 4 | 144 × 1,152 | 13 | 1,110 | 1,152 | 42 (3.6%) | saturated@2 |
| 2 | 3 | 144 × 1,261 | 12 | 1,134 | 1,261 | 127 (10.1%) | saturated@2 |
| 3 | 0 | 144 × 2,047 | 9 | 1,958 | 2,047 | 89 (4.3%) | saturated@1 |
| 4 | 0 | 144 × 2,047 | 9 | 1,588 | 2,047 | 459 (22.4%) | saturated@1 |
| 5 | 0 | 144 × 2,047 | 9 | 1,313 | 2,047 | 734 (35.9%) | saturated@2 |
| 6 | 0 | 144 × 2,047 | 9 | 1,054 | 2,047 | 993 (48.5%) | saturated@2 |
| 7 | 0 | 144 × 2,047 | 9 | 855 | 2,047 | 1,192 (58.2%) | saturated@2 |
| 8 | 0 | 144 × 1,717 | 10 | 590 | 1,717 | 1,127 (65.6%) | rank1@4 |
| 9 | 0 | 144 × 1,717 | 10 | 632 | 1,717 | 1,085 (63.2%) | rank1@4 |
| 10 | 0 | 144 × 2,047 | 9 | 677 | 2,047 | 1,370 (66.9%) | rank1@4 |
| 11 | 0 | 144 × 1,717 | 10 | 463 | 1,717 | 1,254 (73.0%) | rank1@1 |
| 12 | 0 | 144 × 2,047 | 9 | 502 | 2,047 | 1,545 (75.5%) | rank1@3 |
| 13 | 0 | 144 × 2,047 | 9 | 481 | 2,047 | 1,566 (76.5%) | rank1@3 |
| 14 | 0 | 144 × 2,047 | 9 | 413 | 2,047 | 1,634 (79.8%) | rank1@4 |
| 15 | 0 | 144 × 2,047 | 9 | 496 | 2,047 | 1,551 (75.8%) | rank1@4 |
| 16 | 0 | 144 × 2,047 | 9 | 430 | 2,047 | 1,617 (79.0%) | rank1@4 |

   - **`cancel-pair@t4`, 5–13 atoms, starts 4–8** (units written cp@1–cp@4):

| L | M × N | t = 4 | t = 5 | t = 6 | t = 7 | t = 8 |
|---|---|---|---|---|---|---|
| 5 | 640 × 5,462 | 1,274 (+4,188) | 923 (+4,539) | 672 (+4,790) | 491 (+4,971) | 379 (+5,083) |
| 6 | 288 × 3,982 | 2,312 (+1,670) | 1,892 (+2,090) | 1,518 (+2,464) | 1,255 (+2,727) | 994 (+2,988) |
| 7 | 288 × 3,097 | 1,749 (+1,348) | 1,368 (+1,729) | 1,129 (+1,968) | 870 (+2,227) | 709 (+2,388) |
| 8 | 288 × 2,487 | 1,265 (+1,222) | 1,018 (+1,469) | 778 (+1,709) | 637 (+1,850) | 498 (+1,989) |
| 9 | 144 × 2,047 | **2,091 found** (cp@2) | 1,760 (+287) | 1,505 (+542) | 1,317 (+730) | 1,074 (+973) |
| 10 | 144 × 1,717 | 1,664 (+53) | 1,397 (+320) | 1,202 (+515) | 990 (+727) | 795 (+922) |
| 11 | 144 × 1,462 | 1,318 (+144) | 1,112 (+350) | 913 (+549) | 736 (+726) | 612 (+850) |
| 12 | 144 × 1,261 | 1,057 (+204) | 846 (+415) | 671 (+590) | 565 (+696) | 452 (+809) |
| 13 | 144 × 1,152 | 807 (+345) | 621 (+531) | 519 (+633) | 419 (+733) | 350 (+802) |
| 13 | 192 × 1,099 | 516 (+583) | 381 (+718) | 313 (+786) | 241 (+858) | 205 (+894) |

   - **`cancel-pair@t4`, the closest block at each start, over all lengths.** It is 144 × 2,047 over 9 atoms at every start:

| Start | Widest columns found with 144 rows | Required | Margin | Closest unit |
|---|---|---|---|---|
| 4 | 2,091 | 2,047 | **found** (the only case) | cp@2 |
| 5 | 1,760 | 2,047 | 287 (14.0%) | cp@2 |
| 6 | 1,505 | 2,047 | 542 (26.5%) | cp@2 |
| 7 | 1,317 | 2,047 | 730 (35.7%) | cp@2 |
| 8 | 1,074 | 2,047 | 973 (47.5%) | cp@2 |
| 9 | 880 | 2,047 | 1,167 (57.0%) | cp@1 |
| 10 | 767 | 2,047 | 1,280 (62.5%) | cp@1 |
| 11 | 655 | 2,047 | 1,392 (68.0%) | cp@1 |
| 12 | 583 | 2,047 | 1,464 (71.5%) | cp@1 |
| 13 | 499 | 2,047 | 1,548 (75.6%) | cp@1 |
| 14 | 442 | 2,047 | 1,605 (78.4%) | cp@1 |
| 15 | 386 | 2,047 | 1,661 (81.1%) | cp@1 |
| 16 | 341 | 2,047 | 1,706 (83.3%) | cp@1 |

   - **Every block found** (16 cases; each one's widest came from the intersection path). "Checked" says how the width was confirmed beyond the search itself: a certificate (below), or the per-task gate at 7 atoms.

| Set | Start | Length | M × N | Widest columns | Widest unit | Found in | Checked |
|---|---|---|---|---|---|---|---|
| census | 0 | 6 | 288 × 3,982 | 4,458 | saturated@1 | 4 saturated | |
| census | 0 | 7 | 288 × 3,097 | 3,669 | saturated@1 | 4 saturated | gate |
| census | 0 | 8 | 288 × 2,487 | 2,848 | saturated@1 | 4 saturated | certificate |
| census | 0 | 9 | 144 × 2,047 | 3,494 | saturated@1 | 4 saturated, 3 rank1 | |
| census | 0 | 10 | 144 × 1,717 | 2,851 | saturated@1 | 4 saturated, 3 rank1 | |
| census | 0 | 11 | 144 × 1,462 | 2,282 | saturated@3 | 4 saturated | |
| census | 0 | 12 | 144 × 1,261 | 1,831 | saturated@1 | 4 saturated | |
| census | 0 | 13 | 144 × 1,152 | 1,437 | saturated@1 | 4 saturated | certificate |
| census | 1 | 9 | 144 × 2,047 | 2,896 | saturated@3 | 4 saturated | |
| census | 1 | 10 | 144 × 1,717 | 2,314 | saturated@3 | 4 saturated | |
| census | 1 | 11 | 144 × 1,462 | 1,850 | saturated@1 | 4 saturated | |
| census | 1 | 12 | 144 × 1,261 | 1,441 | saturated@1 | 4 saturated | certificate |
| census | 2 | 9 | 144 × 2,047 | 2,374 | saturated@3 | 4 saturated | |
| census | 2 | 10 | 144 × 1,717 | 1,902 | saturated@1 | 4 saturated | |
| census | 2 | 11 | 144 × 1,462 | 1,476 | saturated@1 | saturated@1 | certificate |
| cancel | 4 | 9 | 144 × 2,047 | 2,091 | cp@2 | cp@2 | certificate |

   - **Which search finds them:**
     - count order alone finds none of the 16; every find needs the intersection path;
     - the mirrored side (N columns first, then their shared rows) reaches M rows in 6 of the 16: start 0 over 9–12 atoms and start 1 over 9–10, up to 235 rows against 144 (start 0, 9 atoms). It finds nothing the row side misses;
     - over all 26,356 cases, the widest came from count order in 25,335 and from the intersection path in 1,021.
   - **Method** (`hot_blocks.py` at `fd3eab84`, from `3b4784c9` and `860918d7`; Measured on node 2's CPUs, no GPU):
     - **Curves, not verdicts.** Per (unit, start, length) the search saves, on each side, the widest set found at every size: M rows to their shared columns, and N columns to their shared rows.
     - **Two greedy lower bounds per side:**
       - count order: lines by exact count, then a prefix AND;
       - the intersection path: add the line that keeps the most partners, ties to the lowest index. It is evaluated lazily against upper bounds, and matches the plain greedy on the self-test.
     - **A block M × N is found** if a row curve reaches N columns at M rows, or a column curve reaches M rows at N columns.
     - **The table is applied at summary time.**
       - `hot_blocks.py --summary-only --table T --floors F` re-judges a later table from the saved per-task files, with no rerun, and `envelope.json` holds each (start, length)'s maximum over every unit's curves.
       - `load_table` refuses a table whose W* isn't ⌈width_floor⌉ or with a block narrower than W*. A fit-aware table without one W* per length would need that check relaxed.
     - **Coverage:**
       - every start 0–16 (census) and 4–16 (`cancel-pair@t4`), and every length 5 to 256 − t, masked to Π's admitted rows and columns;
       - every length has its own blocks now, so nothing is borrowed from the next listed length as in Results 19.
     - **Bitsets:** Results 17's 64 census units from H_i (`r20260930-153135-2062`) and Results 20's 4 `cancel-pair@t4` units, both on node 2.
   - **Gates:** in each of the 1,140 (unit, start) tasks, every value at lengths 4 and 7 was recounted from bools, including the lines the intersection path chose: 2,280 windows, 0 mismatches.
   - **Certificates:** `verify_block.py`, one `research run` each on node 2's CPUs, took the five blocks new to this table and checked them again from the bitsets: the chosen rows, their common columns, exactness over the window, and Π's admission. All five hold at exactly the reported widths (the rows marked "certificate" above). Each run keeps its `rows.npy` and `cols.npy`.
   - **Run:** two CPU fill jobs (`gpus=0`), raised from prio 5 to prio 10 at 21:50Z:
     - `cancel-pair@t4` at starts 4–16: 21:39–21:56Z, 2 chunks;
     - the census at starts 0–16, in phases 3–5, 0–2 and 6–16: 21:56–22:35Z, 8 chunks;
     - CPU time: 26,011 s in the intersection paths, 1,229 s in count order and 1,773 s in the ANDs.
   - **Shortcuts:**
     - the search is greedy, so a miss is not a proof;
     - the intersection path stops once fewer than 32 partners remain. Every block in the table is at least 176 columns wide and 64 rows tall, so no verdict depends on it, but the saved curves are cut below 32;
     - 4 units per family at 8,192², on the census's synthetic families and near-cap, with no real activations;
     - `cancel-pair@t4` uses our seeds, not the assessor's (the same law);
     - only the chain from H_i is searched;
     - only rows × columns placement is judged, as the table lists it;
     - the table is provisional (bc-d9842080's catalogue audit; fit-aware floors are pending). The saved curves let a later table be judged with `--summary-only` or from `envelope.json`.
   - **Evidence:**
     - `art:7cb5d6fa02990b096665b39723e63be30982044aff23a45aacd660f9ac40f1a2`, preserved by `r20260930-223548-448d`. It holds both searches' per-task files, summaries, envelopes and logs, the table and floors as read, the five certificates, and the job scripts;
     - the ships `r20260930-213529-bb00` (`cancel-pair@t4`) and `r20260930-214453-aa44` (census), and the certificate runs `r20260930-220609-e83f`, `-222313-d437`, `-222317-b5b4`, `-222322-7ed1` and `-222327-4627`;
     - on node 2: `/workspace/pouw/gpu3-fp8/out/v2hot-blocks-corrected/{s0-2,s3-5,s6-16}/` and `/workspace/pouw/gpu3-fp8/out/v2hot-blocks-corrected-cancel/`.
   - **For v2-hot's route** (the theory lane's call):
     - clause (c) still fails at starts 0–2, now over 6–13 atoms;
     - on the census, start 3 passes with the tightest margin at 89 columns (4.3%);
     - a t₀ of 4 fails on `cancel-pair@t4` at start 4;
     - from start 5 on, nothing measured is found; the tightest is `cancel-pair@t4` at start 5, 287 columns (14.0%).
22. **Clause (c) on the row-dependent staircase: it passes** (the coordinator's 3:55 PM PDT order; server.md "PINNED 3:52 PM PDT", which amends 3:17 PM PDT; for bc-3006c44a, bc-b58c6093 and the assessor bc-d7d4b0d1). **This supersedes Results 21's clause (c) verdict.**
   - **The floor table** is `internal/pouw/rtx-pro/catalogue-audit/floors/row-floors-staircase.json` (bc-d9842080; sha256 `6f197bc6…2cfe2`).
     - It holds W*(L, M) over 4,180 schemes at `ac13ca88`, for L = 4–256 and M = 8–8,192, with every contraction factor 2–16 and zero padding on rows, columns and K.
     - It is a lower bound, at most 19% loose in rows. It allows every contraction factor, so this is a pass in the 21:47Z sense, not a "pass under the restricted set".
     - (8, 768) is no longer unknown: its floor is 3,283.0, and the widest 768-row set over 8 atoms is 842 columns (start 0).
   - **Rule:** every step of every saved curve (both sides, count order and intersection path) is a block M × N. It is found if N ≥ W*(L, M), where M is read at the step at or below ⌈M⌉₈, as the file says. A null step (nothing pays below 8,192 columns) is never found.
   - **Verdict** (Measured on node 2's CPUs, on Results 21's saved curves; greedy, so a find is certain and a miss is not a certificate; a pass on a lower-bound floor stands):

| Set | Starts | Windows judged | Found | Tightest: start, length, M × N against W*(L, M) | N / W* |
|---|---|---|---|---|---|
| census, 64 units | 0–2 | 756 | 0 | 0, 9 atoms, 361 × 1,697 against 2,216.6 (step at 368 rows; its composition needs 432), saturated@1 | 0.766 |
| | 3–5 | 747 | 0 | 3, 9 atoms, 177 × 1,585 against 4,526.8, saturated@1 | 0.350 |
| | 6–16 | 2,662 | 0 | 6, 9 atoms, 121 × 1,317 against 6,750.6, saturated@4 | 0.195 |
| `cancel-pair@t4`, 4 units | 4–16 | 3,159 | 0 | 4, 9 atoms, 177 × 1,704 against 4,526.8, cp@2 | 0.376 |

   - **By start**, the tightest N / W*:
     - census: 0.766, 0.581, 0.440, 0.350, 0.280 and 0.237 at starts 0–5, and at most 0.195 from 6;
     - `cancel-pair@t4`: 0.376 and 0.310 at starts 4–5, and at most 0.268 from 6.

     Every tightest point is at 9 atoms. No window comes within 19% of its floor (the closest is 23.4% under, at start 0), so the held-back finer table can't change the verdict.
   - **Results 21's 16 found blocks all pass here**, at 0.16–0.52 of their floors. Examples:
     - 288 × 4,458 over 6 atoms at start 0, against W*(6, 288) = 18,020.6;
     - 144 × 3,494 over 9 atoms at start 0, against W*(9, 144) = 6,750.6;
     - `cancel-pair@t4`'s 144 × 2,091 over 9 atoms at start 4, against 6,750.6.
   - **Order item 3: this check reads no free-family shape.** It reads the staircase and the saved curves only.
     - The staircase is at or above the padded free family's `padded_min_cols` at every (window, rows) point listed in `catalogue-audit/free-family/free_family_compare_all.json`, with 0 exceptions. It is also finite wherever the free family pays.
     - Results 21's check did read free-family shapes, through the corrected table: its row counts (64–640) and some of its widths, such as 144 × 1,152 from 13 atoms. This check replaces that one.
   - **The interim probe** (3:17 PM PDT): the widest set of 640 rows over 4–7 atoms at starts 4 and 5, per family, in columns (Measured, 8,192² arrays). Families with no 640-row set are left out.

| Family | t4, 4 atoms | t4, 5 | t4, 6 | t4, 7 | t5, 4 | t5, 5 | t5, 6 | t5, 7 |
|---|---|---|---|---|---|---|---|---|
| saturated | 1,458 | 908 | 544 | 316 | 1,047 | 612 | 366 | 222 |
| rank1 | 1,138 | 792 | 594 | 405 | 911 | 706 | 478 | 337 |
| in-span-FA | 577 | | | | 375 | | | |
| grid-aligned | 509 | | | | 330 | | | |
| zero-slices | 463 | | | | 303 | | | |
| sparse10 | 343 | | | | 220 | | | |
| `cancel-pair@t4` | 1,930 | 1,274 | 804 | 503 | 1,449 | 923 | 567 | 361 |

     So 640 rows share at most 1,930 columns (`cancel-pair@t4`, atoms 4–7), well under about 2,700; the census's widest is 1,458. This is at 8,192 columns wide; at 16,384 it would be an extrapolation.
   - **The padded list's effect on `v2-hot-16384`'s block tests** (Derived, CPU):
     - **Method:** I recomputed bc-d9842080's padded rule (`free_family_padded.py`) at units 8,192 and 16,384 for 4–13 atoms. The script is `ff16k.py`, over `pearlc_region_family.search("all", (16, 8, 16), 2.0, unit, 8192)`, with 718,323 and 1,349,172 states.
     - It gives the padded minimum columns at every multiple of 8 rows, and the tests M × max(N_padded(L, M), W*(L)) at the undominated M, with W* from `widthfloor-all-p8.0.json`.
     - It agrees with `free_family_compare_all.json` at all 130 shared (window, rows) points, at both units.
     - **Tests by length:**

| L | Corrected table (8,192 wide) | Padded, 16,384 wide |
|---|---|---|
| 4 | none (W* 10,726 > 8,192) | 640 × 10,726: new at 16,384 wide; padding takes the free family's 3,840 to 3,835.2, and W* sets the width |
| 5 | 640 × 5,462 | the same |
| 6, 7, 8 | 288 × 3,982, 3,097, 2,487 | the same |
| 9, 10, 11, 12 | 144 × 2,047, 1,717, 1,462, 1,261 | the same |
| 13 | 144 × 1,152 and 192 × 1,099 | **144 × 1,107** (padded 1,106.2, −3.9%) and 192 × 1,099 |

     - **So:** at the lengths the run covers (atoms 0–12, so at most 13 atoms), padding moves one test, 13 atoms at start 0. 640 × 10,726 is unchanged. The 16,384-wide search adds no composition that lowers a test: the tests are the same at both units.
     - **Where padding binds:** it cuts widths by 0.4–8.5% at the listed rows, but binds over W*(L) only from 13 atoms: at 144 rows over 13–16 atoms, 1,152 → 1,106.2, and at 64–288 rows from 18 atoms. Between listed row counts it cuts more (to 0.53× at 9 atoms, by bc-d9842080's file), but at 4–12 atoms W* sets the width at every row count from the fewest up.
     - **For a clause (b) replay:** Results 21's (b) cases at starts 6–16 miss by at least 26.5% of the required width (48.5% on the census), more than padding's cut at the listed rows. I didn't re-judge the in-between row counts, because (b) replays run only if (c) fails.
     - **The table for the run:** `/workspace/pouw/gpu3-fp8/catalogue-audit/v2hot-blocks-padded-16384.json` on node 2 (`hot_blocks.py --table` format, sha256 `ffaecbea…`).
   - **The pinned sample points:** the widest columns with M rows over all units, at starts 0–5 (Measured; `cancel-pair@t4` at starts 4–5 in brackets).

| (L, M) | W*(L, M) | t = 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|---|
| (6, 288) | 18,020.6 | 4,458 | 3,692 | 2,972 | 2,323 | 1,851 [2,312] | 1,397 [1,892] |
| (8, 768) | 3,283.0 | 842 | 493 | 307 | 272 | 207 [202] | 176 [146] |
| (12, 192) | 4,526.8 | 1,344 | 1,010 | 755 | 581 | 438 [696] | 329 [543] |
| (24, 192) | 2,131.7 | 47 | 42 | 34 | 1 | 0 [41] | 1 [34] |

   - **The stray agent bc-f5693db2 touched none of my files** (checked 23:25Z):
     - in the store, this file and the write-up were last written by me;
     - on node 2, every file under `gpu3-fp8/` changed since 23:09Z is one of this job's outputs, and no fill entry names it;
     - the branch is at `80d17d29`, the same locally and on origin.
   - **Evidence:**
     - the judge run `r20260930-230905-6d30` (SUCCESS, 6.9 s, preserved; every `staircase.json`, `inputs.sha256`, `code.sha`);
     - `hot_blocks.py --staircase` at `0d59d4ab` and `80d17d29` (self-test passes);
     - the padded recomputation, with the table and input hashes: `art:374b890183398e3e073b4987854dc1bd04df1b51309a9d17e5d0247130d8a779`;
     - on node 2: `/workspace/pouw/gpu3-fp8/jobs/gpu3-fp8-v2hot-staircase.sh`, `/workspace/pouw/gpu3-fp8/catalogue-audit/`, and `staircase.json` in each of Results 21's output directories.
   - **Shortcuts:**
     - the search is greedy;
     - 4 units per family at 8,192², synthetic families, `cancel-pair@t4` on our seeds, and the chain from H_i only;
     - the staircase is at unit 8,192, which matches these arrays;
     - the padded recomputation is my own run of bc-d9842080's rule, on this VM, not a `research run`;
     - W*(L) at unit 8,192 is used unchanged at n = 16,384, as the order does. For comparison, the staircase at (4, 640) is 62,381.4.
   - **Next** (the 3:17 PM PDT order, unchanged):
     - `deltacharge.py` is optional and not run.
     - Then the `v2-hot-16384` GPU run. `hot.py` needs an atom cap: the chain over atoms 0–12 only, with forming and H_i on the full k = 16,384. Without it, a unit writes all 512 atoms, about 64 GiB.
     - Jobs: `gpu3-fp8-v2hot16k-gpu.sh` (`gpus=1 prio=10`, about 25-minute leases, exit 99) and `gpu3-fp8-v2hot16k-blocks.sh` (`gpus=0`).
     - Estimated 1–1.5 GPU-h: the 8,192 run held 50 lease-minutes for 64 units at a median 12 s of GPU time each, with host drawing dominating. Here there are 24 units at 4× the area over 13 atoms instead of 256.

23. **The padded re-search, part 1: the threshold, and every saved curve re-judged on it** (the coordinator's 4:41 PM PDT order; server.md pinned 4:35 PM PDT; for bc-3006c44a, bc-b58c6093 and the assessor bc-d7d4b0d1). Part 2, the windows not yet measured, is staged and waits on compute-accounting.
   - **The threshold** at (L, M) is max(N_min(L, M), W*(L, M)), for L = 4–256 and every M = 8, 16, …, 8,192 (Derived; `padded_floor.py`, `8a57c3e9`):
     - the padded free family is FP16 (16, 8, 16) at 2.0 and TF32 (16, 8, 8) at 4.0, all ranks, by bc-d9842080's rule;
     - its gate reproduces every `padded_min_cols` point of `free_family_compare_all.json`, with 0 mismatches;
     - `art:a6974ffdfdd3902ff642e844db89a4cf9e94a7bd389af8ab4b6029af4d417720` (sha256 `677fc85e…`), on node 2 at `/workspace/pouw/gpu3-fp8/catalogue-audit/padded-threshold.json`.
   - **The staircase binds at every point where both bounds pay** (256,903 points). Neither padded family is ever wider than W*, and the TF32 shapes pay only from L = 144.
     - At 51 points the threshold is null (nothing pays) where the staircase is not: the staircase rounds rows down, so its first step comes up to 19% early. These are L = 4–35, at M = 88–632 rows. Of them, only L = 9–17 at M = 120–136 have W* under 8,192.
     - So the threshold equals the staircase except at those 51 points, where it is stricter.
   - **Every saved curve is re-judged on it, and nothing is found** (Measured; greedy, lower bounds):
     - v2-hot from H_i at starts 0–16 on the 64 census units: 0 of 4,165 windows;
     - `cancel-pair@t4` at starts 4–16: 0 of 3,159.
     - The tightest pass is 0.766 (start 0, 9 atoms: saturated@1, 361 rows on 1,697 columns against 2,216.6). By start 3 it is 0.350, by start 6 0.175 (0.262 on `cancel-pair@t4`), and by start 16 0.073.
     - On node 2: `/workspace/pouw/gpu3-fp8/out/v2hot-blocks-padded/{s0-2,s3-5,s6-16}/` and `out/v2hot-blocks-padded-cancel/`. Their `units` are symlinks to Results 21's curves.
   - **Results 17's zero-slices close approach, re-read** (the hot chain, start 0, 6 atoms; Measured):
     - Results 17 had 1,194 rows on 288 columns, 0.888 of the free shape 1,344 × 288. That was count order only.
     - The greedy curves go further: 569 rows share 1,318 columns, **1.97× the padded free width** N_min(6, 569) = 669.6. So against the free family alone (pre-adds free), zero-slices meets it at start 0.
     - On the threshold the staircase binds: 361 rows on 2,060 columns against W*(6, 368) = 6,701.0, a ratio of **0.307**.
     - Start 0 is clause (c)'s, which passed on the staircase (Results 22).
   - **Part 2 is staged, not queued:** three `gpus=0` jobs in `/workspace/pouw/gpu3-fp8/jobs/`, judged on the threshold and then on the staircase alone (`stair-only/`). Each chunk ends its tasks by 16 minutes, with a hard stop at 20 plus the phase judges, under `max_min=28`, and exits 99 while work remains.

| Job | Question | Units | Starts | Estimated CPU-h |
|---|---|---|---|---|
| `gpu3-fp8-padded-zero.sh` | v2's region row, from +0 | 64 census | 10–252 | 55 |
| `gpu3-fp8-padded-hot.sh` | v2-hot's clause (b), from H_i | 64 census | 17–252 | 41 |
| `gpu3-fp8-padded-hot-cancel.sh` | v2-hot's clause (b), from H_i | 4 `cancel-pair@t4` | 17–252 | 7 |

   - **The estimate (Estimated, ±25%)** is 103 CPU-h in all. It interpolates the measured CPU-s per (unit, start) task:
     - from +0: 38 at start 10, 24 at 24, 19 at 48, 15 at 80, 11 at 128 and 5 at 240;
     - from H_i: 13.6 at start 16, 11 at 128 and 5 at 240;
     - on `cancel-pair@t4`: 60, 21 and 9 at the same starts.
     - These are 4 units at each probed start, under node 2's load. Probe logs: `art:ff434ce6ed34b92c70a89e571ccac9de38400b2da861587754c990be92ad4f97`. Ignore `art:55f2128c…`, a corrupt upload of the same logs.
     - Skipping L = 4–5, where nothing can be found (W* ≥ 10,701 > 8,192), saves under 5%, so the jobs keep every length from 4.
   - **Shortcuts:**
     - the search is greedy;
     - 4 units per family at 8,192²; synthetic families; `cancel-pair@t4` on our seeds only, from H_i only (its +0 chain is not in v2's row);
     - a block of M rows is judged at the next multiple of 8 up, which can only lower the threshold;
     - the threshold was built on this VM, not by a `research run`; its builder is committed and its output preserved.
24. **Fix (2) fails on the staircase, so (a) is stopped and v2-hot is parked** (compute-accounting, `note:20261001T0111Z-order-from-compute-accounting-v2hot-route`; the assessor's spec, `note:20261001T0116Z-reply-from-d7d4b0d1-v2hot-fix2-spec`; reported in `note:20261001T0250Z-reply-from-0f3f8a2f-v2hot-fix2-fails`).
   - **The units (Measured):**
     - the seven late-start families of `hot_late_start.py`'s `family()`, 4 units each at 8,192², from H_i (`const`), with bitsets for all 256 atoms;
     - six are new (`gpu3-fp8-fix2-gpu.sh`, `out/fix2`; `hot.py` at `85474991`, shipped by `r20261001-013255-7ab0` with custody);
     - `cancel-pair@t4` is Results 20's units, the same draw and salt;
     - every gate is clean;
     - the cost was 20.0 GPU-min in 4 chunks, 6:35–7:02 PM PDT; one chunk was preempted by the runner and resumed.
   - **The judge** (`gpu3-fp8-fix2-blocks.sh`, `out/fix2-blocks/s0-5`):
     - as Results 22: every unit, start 0–5 and window length from 4 atoms; both sides' width curves (count order, intersection path); every step against `row-floors-staircase.json` (`6f197bc6…`), read at the next multiple of 8 rows.
     - **Final (7:56 PM PDT, all 168 tasks; Measured):** 1,503 windows judged at starts 0–5, 0 gate mismatches, **1 window found**: start 0, atoms 0–8 (L = 9), in all 4 `cancel-pair@flat` units and in no other family. Each block has 361 rows, every word exact and admitted by Π, against W*(9, 368) = 2,216.6, read at the next multiple of 8 rows:

       | Unit | Columns | Ratio to the floor |
       |---|---|---|
       | `cancel-pair@flat@1` | 2,669 | 1.204 |
       | `cancel-pair@flat@2` | 2,666 | 1.203 |
       | `cancel-pair@flat@3` | 2,780 | 1.254 |
       | `cancel-pair@flat@4` | 2,580 | 1.164 |

     - Unit 1's block is certified from the bitsets by `r20261001-024328-ae9b` (preserved). The other three are the judge's intersection path, not separately certified.
     - **Nothing else is found.** The tightest pass at each start is `cancel-pair@flat`: start 0 at L = 10, 249 × 3,096 against 3,274.8 (0.945); start 1 at L = 9 (0.948); start 2 (0.753); start 3 (0.611); start 4 (0.499); start 5 (0.411).
     - **The caveat:** the block pays only where the staircase applies a composition's floor below that composition's own row count (the documented ≤ 19% looseness in rows). The 360–368-row steps come from a composition needing 432 rows; the 512-row step's needs 576. On all four units, the rows side gives:

       | Rows | Floor | Units 1, 2, 3, 4 (ratio) |
       |---|---|---|
       | 360 (padded threshold, nothing rounded up) | 2,359.5 | 1.135, 1.133, 1.182, 1.097 |
       | 432 (the composition's own rows) | 2,216.6 | 0.946, 0.960, 0.980, 0.933 |
       | 576 | 1,536.8 | 0.754, 0.788, 0.765, 0.783 |

       So it is a fail on the agreed floor, which errs toward failing, and not on a row-exact floor. Whether that verdict stands is the assessor's call (now bc-f9af3acc).
     - **Cost (Measured):** 7 chunks, 2:12–2:56Z (7:12–7:56 PM PDT), 42.2 active min at 16 CPUs, about 11.3 CPU-h of slot time; about 4 CPU-min per task against Results 21's 40 s. Starts 6–16 (308 tasks, about 20 CPU-h at that rate, Estimated) are not run without an order. The job file's comment says 14 CPU-h; that figure was from the first chunk and is superseded.
     - **Preserved** by `r20261001-031736-ecaa` (custody, validation passed; run record `art:d999de25abc6f2b429001a040bc969e494f1f6461c318fda925bf410295d87fa`): the GPU half's records without bitsets, the judge's 168 task files and `staircase.json`, both halves of (a), and the job scripts (`jobs/preserve-fix2.sh`).
   - **(a) stopped at 7:42 PM PDT** (the order's item 2):
     - `gpu3-fp8-padded-hot.sh` was at starts 17–63, 1,828 of 3,008 tasks. Its running file was replaced by a stub that exits 0, and its process group got SIGTERM; the runner requeued the stub, which finished as done. The original is in `jobs/`, with its progress, and resumes if requeued.
     - `gpu3-fp8-padded-hot-cancel.sh` had finished at 7:19 PM PDT: 0 found in 27,966 windows at starts 17–252, on both the padded threshold and the staircase alone. The tightest was 0.062 (start 17).
   - **Shortcuts:**
     - the search is greedy;
     - 4 units per family, on our seeds;
     - synthetic families only;
     - the verdict reads the staircase at the next multiple of 8 rows, as the table says.

## Needs

Through the coordinator (the write-up's §6 has the detail):
1. **The statement's W1 prices on sm_120:** FADD 8.38 (GPU 0's measurement), not 32 (Lean's `Costs.adopted`, `pearl_c.py` `FADD_UNITS`). At 32 the credit is 14.3–14.8% above the honest cost.
2. **The cap on this atom:** v1's cap margin grows (≤ 0.11% debit on admitted families, H100 0.21%). The aligned-spike debit is the FP32 total's rounding, so v1 can't narrow it. v2 at ρ = 1/1,000: see Results 1.
3. **Rates:** done, except FP8 `mma.sp`'s rate and words (GPU 4) and m16n8k16 E4M3. No route needs them.
4. **GPU 1's device record** should use `BLACKWELL_SM120_E4M3_M16N8K32` (the census's `sm120-e4m3-k32`, alias `sm120`).
5. **Llama-3.1-70B's activations:** go at 07:47Z; captured, replays running (Results 11).
6. **CPU slots on node 2 (for the infra lane):** the fill runner's CPU path starts queued jobs in name order, ignoring `prio` (its docs say "prio: higher starts first"), and a chunk that exits 99 goes straight back in at its old place. A lane with ≥ 4 short-chunk CPU jobs whose names sort early holds every slot until it finishes (since 09:44Z: `aw-*` before my `gpu3-*`). Fix: order CPU jobs by (−prio, time queued), touching a job's file when it re-queues, or round-robin by owner.
7. **P2's per-row cap needs an extent** (Results 16). A row seen through a 64×8 tile has 8·T atoms. At v2 on k = 3,584 one flagged atom is then 1.12ρ, so a per-row cap at ρ over so few words fails honest rows by resolution alone. Over 64 words (a 64 × 64 tile) every row measured is at most 0.39ρ (token rows, including the outlier-channel rows) or 0.56ρ (weight rows), so a per-row cap at ρ over the row's full width in the tile holds with margin; over 8 words it doesn't.
8. **ε₈ (`fp8-merge-rate/sm120`), stated on the joint condition** (the coordinator's 13:57Z ruling; the assessor's 14:08Z B; Results 13).
   - **The joint rate is 0 on every unit searched** under the greedy adversarial pairing: the census's 26 families under 3 side orders, all 168 Qwen2.5-0.5B linears, and all 70 of Llama-3.1-70B's. With fixed quadrants the bound is under 2^−20 on both sides over the census's 7 draws.
   - **Per side, beside it:** A reaches a fragment on 4 census families (rank1, duplicated, coherent-gaussian, outliers-first) and B on 1 (rank1). Real activations reach none.
   - **The 14:07Z check fails as worded.** Of those 5 fragments' 72 row pairs, 0 are near-duplicates. Only coherent-gaussian's 16 are chain-inexact, and only at v2. So 4 fragments at v2 and 5 at v1 have row pairs that are neither, and by the 14:07Z rule ε₈ goes back to per side.
   - **What such a pair could still use** is a delta's zeros: 0–14% of a fragment's products (14–44% on outliers-first), unstructured.
   - **For the assessor, one choice:** keep the check as worded, so ε₈ goes back to per side; or replace its "chain-inexact on its window" with a bound on the delta's density.
9. **Merging:** `cursor/pearl-c-sm120-attacks-cb92` now contains #451's head. If #451 lands first, mine rebases cleanly. If mine goes first, it carries #451.
10. **v2-hot's lemma (for bc-b58c6093 and bc-3006c44a; Results 17):** the full-unit pass condition fails, so the lemma needs t₀ or `post-add-bound/sm120` for the first atoms.
    - **Free family from H_i:** t₀ is at most 5 atoms (saturated; rank1 3, in-span-FA, grid-aligned and sparse10 1, the rest 0). Every hit is in atoms 0–12, and coverage before t₀ is at most 2.7% of a unit's words.
    - **Priced family from H_i:** no shape at any start on any unit (t₀ = 0), against t₀ up to 2 from +0.
    - **The widest block found** is 2,400 columns from H_i and 3,840 from +0. Both are under the roughly 5,400 columns of the pre-add closure (14:48Z).
    - Which of t₀ or the post-add bound the lemma takes is the theory lane's choice. For t₀, 5 atoms of 256 is what these families need, and real activations weren't run.
11. **Clause (c) of v2-hot's first-atoms row passes on the row-dependent staircase** (for bc-3006c44a, bc-b58c6093 and the assessor bc-d7d4b0d1; Results 22, which supersedes the verdict below).
    - On `catalogue-audit/floors/row-floors-staircase.json` (W*(L, M), every contraction factor), no window is found at any start 0–16 on the census or 4–16 on `cancel-pair@t4`. The closest is 0.766 of its floor, at start 0 over 9 atoms.
    - ~~By the 3:17 PM PDT order, v2-hot then holds at 0.371% packed with no charge.~~ Struck (server.md PINNED 4:26 PM PDT): no uncharged figure stands for v2 or v2-hot. ~~The figure that stands for v2-hot is 0.689% packed with the derived charge, pending the assessor's rating of clause (c).~~ Struck (compute-accounting, `note:20261001T0104Z-order-from-compute-accounting-2aa33ad8-0f3f8a2f-v2hot-fails`): the derived-charge route is dead, at γ ≥ 0.951% packed and ≥ 1.226% as written on the full catalogue (t_c = 4), a rising floor. v2-hot's only route under 1% is the no-charge route, which needs the assessor's fix (2) and (a) to pass (`note:20261001T0111Z-order-from-compute-accounting-v2hot-route`); fix (2) is running.
    - Clause (b) from H_i at starts 4–16 also finds nothing on the padded threshold (Results 23). Starts 17–252 are part 2.
    - **Fix (2) fails on the staircase (Results 24), so v2-hot is parked.** All 4 `cancel-pair@flat` units at start 0 have 361 rows sharing 2,580–2,780 columns over 9 atoms against 2,216.6 (1.16–1.25×), and nothing else is found at starts 0–5. It pays only below its composition's own rows (0.933–0.980 at 432 rows), which is for the assessor to rate. Part 2 (a) is stopped; its cancel half found nothing at starts 17–252.
    - The rest of this item is Results 21's verdict on the corrected table, kept as a record.
    - **Superseded: it failed on the corrected table.**
    - **Where it fails:** 15 of 2,730 cases at starts 0–2, over 6–13 atoms, on saturated (and rank1 at start 0 over 9 and 10 atoms). At start 0, 288 rows share 4,458 columns over 6 atoms (N = 3,982) in all 4 saturated units.
    - **Changed from Results 19:** the 8-atom block (now 288 × 2,487) and 13 atoms (144 × 1,152) are found at start 0, 12 atoms at start 1 and 11 atoms at start 2. All four are certified.
    - From start 3 on, and from 14 atoms on, nothing is found. The tightest pass is still 1,958 columns against 2,047 (start 3, 9 atoms).
    - The basis is a greedy search. Count order alone finds none of the 16 blocks found.
    - **The next step is the theory lane's:** §3's fallback (γ ≤ 0.41%, Estimated) as §8 says, or a changed H_i (§8's per-word bits).
12. **Clause (b) from t₀ = 4 fails on `cancel-pair@t4`** (for the assessor bc-d7d4b0d1, bc-b58c6093 and bc-3006c44a; Results 21).
    - At start 4, 144 rows of unit 2 share 2,091 columns over atoms 4–12, against 2,047. It is certified from the bitsets.
    - From start 5 on, nothing measured is found, on the census or on `cancel-pair@t4`. The tightest is `cancel-pair@t4` at start 5 over 9 atoms: 1,760 columns, a margin of 287 (14.0%). At start 6 it is 1,505 (542, 26.5%), as in Results 20.
    - So on what was measured, (b) holds from t₀ = 5 or 6 and not from 4. The measurement is 4 units of one family, with our seeds; t₀ is the theory lane's choice.
    - **Since Results 22:** clause (c) covers starts 0–5 and passes there on the staircase, including this start-4 block (0.31 of W*(9, 144) = 6,750.6). The start-4 block matters only if (b) is applied from t₀ = 4. At starts 6–16 nothing is found under (b), and the padded shapes can't change that at the listed rows.

## Lessons

- `research run --on vy-nebius-2` returns once the run is launched, and the workload runs on without this VM. Watch it with `research pods ssh vy-nebius-2 -- cat <run dir>/…`, and bring it home with `research fetch --all <id>`: plain `fetch` copies only the metadata.
- `gpu-lease 1` without `--wait` exits at once when any request is waiting (`a request is waiting first`), so the run fails. Fix: always `gpu-lease 1 --wait`, and give `research run` a `--timeout` long enough for the queue.
- The lease queue is first come, first served. A waiting `gpu-lease 8` holds back every 1-GPU request behind it until the longest held lease ends. Mine did at 07:11Z: it waited about 4½ minutes, until a lease capped at 28 minutes ended early, while 7 GPUs sat idle. The 07:05Z rule (holds ≤ 30 minutes, longer work to the fill runner) bounds the wait but doesn't remove it. For the infra lane: let a 1-GPU request that ends before the longest held lease go first (backfill; `gpu-lease` knows each hold's `timeout`).
- Seven of my CPU shards of v2's 7B debit (`research run`, no lease) were still running in the first ~3 minutes of another lane's timed window (`r20260930-064339-7ccf`, from 07:01Z), on at most 7 of 192 cores. Fix: CPU work longer than a few minutes goes to the fill runner, which pauses CPU jobs during a timed window. My later CPU work does.
- Sharding by `--layers` regex turns a 2.8-hour 7B replay into about 35 minutes on 10 cores, or into chunks that fit the fill runner's 25-minute cap.
- For identity gates, pass the job's `$GPU_LEASE_UUID` (the first entry under `gpu-lease 8`) to `sm120_chain --expect-uuid`. `nvidia-smi` sees all 8 GPUs whatever `CUDA_VISIBLE_DEVICES` says.
- This VM was reset at about 07:48Z, which wiped `/tmp`, `~/.research` and uv. Recovery: install uv, clone the notes repository to `~/.research/notes` (its `machines.d/` registers node 2; the SSH key comes from `RUNPOD_SSH_KEY_B64`), and run the research tool from a `main` checkout: older branches' tools refuse an `ssh` machine ("runpod only"). A run launched before the reset has no local record, so `research fetch` can't find it. `research data show <run id>` reads it from the store instead.
- **For the infra lane (the fill runner):** a CPU job paused for a timed window keeps its `max_min` clock running (`fill_runner.py` measures `time.monotonic() - t0` and never moves `t0`), so a chunk sized near the cap is killed soon after the window ends. At 09:30Z this cost two 25-minute v2 `down_proj` chunks of the 70B replay: one ran past the cap on its own, the other was paused through a window. Better: don't count paused time (or, for CPU jobs that hold no GPU, requeue at the cap without counting it as a start). Mine now: `down_proj` chunks take 2 cross-group words per tile, not 4, and a chunk may start 5 times.
- `research run --on` ships a tree only with `--source <clean checkout>`. Without it the run has no source directory, so a `/workspace/research/src/<sha>/…` path fails unless an earlier run shipped that commit (`r20260930-154844-9f93`).
- Node 2's Python is 3.14, whose multiprocessing doesn't fork by default. So module state set after import (the scheme `hot.load_ref` loads) must be set again in each worker, with a Pool `initializer`.
- The node's HF cache (`/workspace/hf`) was empty at 06:28Z. One prefetch run filled Qwen2.5-7B and WikiText-2 (15 GB, about 40 s), so ten shards didn't race to download it.

## Fill candidates

Queued in node 2's fill runner at 07:16Z (scripts in `/workspace/pouw/fill/queue/`, copies in `/workspace/pouw/gpu3-fp8/`; code from `research run`'s shipped tree at `5f1cb93e`):

| Candidate | Script | GPU-hours | Restarts cleanly | Yields |
|---|---|---|---|---|
| v1's debit (G = 4, sm_120 atom) on Qwen2.5-7B, every linear, 2 tiles each, window 0 | `gpu3-fp8-v1-debit-7b.sh` (`gpus=0`, 9 chunks by layer regex; attention took 13 minutes of CPU, `down_proj` goes 4 layers per chunk) | 0 (8 cores) | yes: a chunk's JSON is its checkpoint; exit 99 while chunks remain | v1's per-tile debit on real activations against ρ = 1/400, beside v2's (Results 1) |
| `sm120_chain` gates at Qwen2.5-7B's four linear shapes (m = 2,048) | `gpu3-fp8-chain-7b-shapes.sh` (`gpus=1`, one chunk, about 2 minutes) | ≈ 0.05 | yes: stateless; the output directory is its checkpoint | the chain's bit-exact gates, and the unpromoted chain's failure, at the model's shapes |

Outputs land in `/workspace/pouw/gpu3-fp8/{v1-debit-7b,chain-7b-shapes}/`. Both are done and preserved: the 7B-shapes gates in `art:6c0c59d3af5bbf00ccf5eb31513025662d3c137886b0e81f751d7482e5c25e56`, v1's 9 chunks and their aggregate by `r20260930-073729-cf62`.

Queued from 08:14Z (code at `30e5d473`, shipped by `r20260930-080835-69a3`; copies and `llama70b-scripts.sha256` in `/workspace/pouw/gpu3-fp8/`):

| Candidate | Script | GPU-hours | Restarts cleanly | Yields |
|---|---|---|---|---|
| Llama-3.1-70B capture, every 8th layer (done, 532 s) | `gpu3-fp8-llama70b-capture.sh` (`gpus=0`, 16 cores) | 0 | yes: a hidden-state checkpoint per layer, exit 99 past 20 minutes; on success it moves the 20 replay jobs from `queue-after-capture/` into the queue | X for every linear of 10 layers, with a manifest |
| Llama-3.1-70B replays, one job per layer and version | `gpu3-fp8-llama70b-{v1,v2}-L{00..72}.sh` (`gpus=0`, 8 cores; v1: 2 chunks, v2: 4, one tile per `down_proj` chunk) | 0 | yes: a chunk's JSON is its checkpoint | admission with and without the split, and v1's and v2's debit (Results 11) |
| `sm120_chain` gates at 16,384³ and 70B's shapes, then fresh seeds | `gpu3-fp8-chain-16k-70b-shapes.sh` (done), `gpu3-fp8-chain-seeds-{a,b}.sh` (`gpus=1`, about 5 minutes each) | ≈ 0.25 | yes: stateless | bit-exact gates on new stand-ins (Results 8) |

More candidates, not queued: v1 and v2 replays on further WikiText-2 windows (the 7B script with `--window 1`, `2`, …, or a second 70B capture with `--window 1`).

Queued 11:32–11:36Z, all `prio=10` in chunks of 8 minutes or less. Each chunk exits 99 while items remain. Copies of the scripts and their sha256s (`llama70b-scripts.sha256`) are in `/workspace/pouw/gpu3-fp8/`, and `gpu3-fp8-preserve.sh` collects each set once all its jobs are in `done/` or `failed/`.

| Candidate | Script | GPU-hours | Restarts cleanly | Yields | Preserved by |
|---|---|---|---|---|---|
| The 70 Llama-3.1-70B linears as units: exact region, merge rate, salt-dead | `gpu3-fp8-exact-acts70b.sh` (`gpus=1`, 4 cores, 32 GB, 5.5-minute budget; `136dd8fb`) | ≈ 0.5 | yes: one JSON per unit plus `state.json` | Results 12–14 on real activations | `r20260930-113542-0168` |
| 7 draws of every census family | `gpu3-fp8-exact-runs.sh` (`gpus=1`, 4 cores, 24 GB, `--runs 1,…,7`) | ≈ 0.8 | yes: the same | the merge rate's power (Results 13) and the blocks' spread over draws (Results 12) | `r20260930-113545-920d` |
| Per-row debit, v1 (G = 4) | `gpu3-fp8-rows-70b-v1.sh` (replay with split, 20 chunks), `gpu3-fp8-rows-7b-v1.sh` (live forward, 9 chunks); `gpus=0`, 8 cores, `--cross-words 0` | 0 | yes: a chunk's JSON is its checkpoint | Results 16 (`agg_rows.py`) | `r20260930-113549-aff2` |
| Per-row debit, v2 (G = 0) | `gpu3-fp8-rows-70b-v2-{a,b}.sh` (20 chunks each), `gpu3-fp8-rows-7b-v2-{a,b}.sh` (17 each, fresh seeds) | 0 | yes: the same | Results 16 | `r20260930-113609-8795` |
| Per-row debit at full width (queued 12:04Z) | `gpu3-fp8-rows-7b-wide-v1.sh` (7 chunks of 4 layers), `gpu3-fp8-rows-7b-wide-v2-{a,b}.sh` (14 chunks of 1 layer each); `gpus=0`, 8 cores, 64 GB, `1b489399`, seeds 20264001 + i and 20264101 + L | 0 | yes: the same | whether outlier-channel rows' debit persists across 64 columns (Results 16) | `r20260930-120430-f1cc` |
| The greedy adversarial pairing on the 26 census families (queued 12:45Z; done 13:17Z: 2 items on node 2, 24 computed on this VM and merged between chunks) | `gpu3-fp8-pairing-census.sh` (`gpus=0`, 2 cores, 8 GB, 5.5-minute budget, about 2 units per chunk; `fa74b9e3`, shipped by `r20260930-124136-4a6e`) | 0 | yes: one JSON per unit plus `state.json` | Results 13's pairing on every family | `r20260930-124539-e47a` |
| The greedy adversarial pairing on the 70 Llama-3.1-70B linears (queued 12:45Z) | `gpu3-fp8-pairing-acts70b-{a,b}.sh` (layers 0–32 and 40–72; `gpus=0`, 2 cores, 16 GB; a linear takes 2.6–4.1 minutes, so a 5.5-minute budget from 13:07Z (4 before) runs 1–2 per chunk, at most about 7 minutes) | 0 | yes: the same | Results 13's pairing on real activations | `r20260930-124539-e47a` |

Outputs land in `/workspace/pouw/gpu3-fp8/out/{exact_acts70b,exact_runs,pairing_census,pairing_acts70b_a,pairing_acts70b_b}/`, `/workspace/pouw/gpu3-fp8/rows-{70b,7b}-{v1,v2}/` and `/workspace/pouw/gpu3-fp8/rows-7b-wide-{v1,v2}/`. The 70B linears and the 7 draws are done and preserved (`r20260930-113542-0168`, `r20260930-113545-920d`).

Queued 14:40–14:58Z for v2-hot's full-unit rerun (13:56Z). Code is at `e07c34eb`, shipped by `r20260930-145634-28e5`, and the reference scripts are under `/workspace/pouw/gpu3-fp8/hot-ref` (SHA256SUMS). Copies of the scripts are in `/workspace/pouw/gpu3-fp8/jobs/`:

| Candidate | Script | GPU-hours | Restarts cleanly | Yields | Preserved by |
|---|---|---|---|---|---|
| v2-hot's replay, 64 units, from H_i (`const`, c₀ = 64) and from +0 (done 15:31Z, 4 chunks) | `gpu3-fp8-v2hot-gpu.sh` (`gpus=1`, `on=2`, prio 10, `max_min=8`, 8 cores, 24 GB, 5.5-minute budget) | ≈ 0.25 | yes: one directory per unit, `state.json` | the per-atom bitsets and gates (Results 17) | `r20260930-153135-2062` |
| v2-hot's window search (done 15:49Z, 2 chunks) | `gpu3-fp8-v2hot-search.sh` (`gpus=0`, prio 0, `max_min=8`, 24 processes, 48 GB, 5.5-minute budget; exits 99 while no written unit waits) | 0 | yes: one JSON and npz per (unit, chain) | t₀, coverage and the pass condition (Results 17) | `r20260930-153135-2062` |

- **Queue changes:**
  - **prio 0:** my queued `gpus=0` jobs are set to prio 0 (server.md 12:44Z), by rename to a dot-file and back, never editing a running job.
  - **Held (`.hold-*` in the queue):** from 15:08Z, the 70B v2 replays and the per-row v2 jobs. They waited until the v2-hot search's summary existed, so the search started first, and were released at 15:49:43Z.
  - **v1-hot cancelled (15:02Z):** v2-hot's GPU job had been written to queue v1-hot's run once it finished. At 15:14Z the queued copy was replaced, between chunks, by one without that step. v1-hot's scripts are renamed `cancelled-*`.

## GPU-ready run lines

From a checkout of `main`'s research tool (`uv run --project tools/research research run`), with `--source` a clean checkout of `cursor/pearl-c-sm120-attacks-cb92` at `5f1cb93e` (`S=/workspace/research/src/5f1cb93eba16e9117b238650cf2c0d71c2757501`):

- **(a) Gates only, one GPU** (about 70 s once it holds the lease; done once: `r20260930-064531-15cb`):
  `research run --on vy-nebius-2 --project verity --campaign pouw --source <checkout> --timeout 3600 --env GPU_LEASE_WHO=bc-0f3f8a2f-3024-5bae-bda9-8e3836b9cb92 -- gpu-lease 1 --wait -- bash -c 'exec uv run --no-project --with numpy python3 $S/benchmarks/pouw/sm120_chain/run.py --gpu lease --expect-uuid "$GPU_LEASE_UUID" --clock-label locked-2100 --shapes 8192x8192x8192,128x8192x8192 --reps 0'`
- **(b) Timed, whole node** (gates, then 20 reps per shape on the first leased GPU; capped at 19 minutes; queued as `r20260930-071059-5389`):
  `research run --on vy-nebius-2 --project verity --campaign pouw --source <checkout> --timeout 7200 --env GPU_LEASE_WHO=bc-0f3f8a2f-3024-5bae-bda9-8e3836b9cb92 -- gpu-lease 8 --wait -- timeout 1140 bash -c 'export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*} && exec uv run --no-project --with numpy python3 $S/benchmarks/pouw/sm120_chain/run.py --gpu lease --expect-uuid ${GPU_LEASE_UUID%%,*} --clock-label locked-2100 --shapes 8192x8192x8192,128x8192x8192 --reps 20'`
- **(c) CPU replays** go to the fill runner (the scripts above), not to `research run`, so that they pause during timed windows.

## Panel rows

- **v2's saving over v1, measured on the card** (an estimated re-pricing of v2 from v1's attempt 5; the coordinator appended it as attempt 16):
  `panel.py append --line pearl-c-sm120 --version v2 --precision fp8 --phase prefill --shape m8192-n8192-k8192 --kind estimated --slowdown 1.27 --lo 1.265 --hi 1.275 --gamma 0.00362 --change kernel --description "v1's attempt 5 (1.34) less the promotion measured on the card: 5.65% of the honest chain's time at 8,192³, 0.108 ms, or 0.075× of cuBLASLt FP8's 1.4457 ms (W1 model at FADD 8.376: 0.065×); a chain microbenchmark without forming or hashing, locked-2100" --source "r20260930-071059-5389; internal/pouw/rtx-pro/fp8-cheaper-computation-search.md §5 (bc-0f3f8a2f)"`
- The cheaper-computation routes aren't rows: each is a check on γ, and none saves anything at measured prices (Results 2).
