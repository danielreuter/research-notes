---
cursor:
  subagentId: "bc-e6a46970-b6ef-5738-af64-182b143075d4"
---

# GPU 0: FP8 tensor-core capture (sm_120, RTX PRO 6000)

Worker bc-e6a46970. Branch `cursor/sm120-fp8-capture-75d4`, head `7aa3abf6`, draft [#492](https://github.com/danielreuter/verity/pull/492). It stacks on the vLLM lane's draft [#487](https://github.com/danielreuter/verity/pull/487) (`cursor/vllm-sm120-fp8-probe-422d`, 07caae24 merged in) and registers no second copy of their models or `tc_probe` entries. On node 2 I hold at most one GPU, through `gpu-lease 1`, for ≤ 30 minutes per lease.

## Checkpoints

- 04:58Z: Phase A started (the store mounted, nvcc 12.9.86 from NVIDIA's apt repo).
- 05:40Z: took the 04:50Z scope cut: no E4M3/E5M2 recapture; the gap rows only, stacked on the vLLM branch.
- 06:08Z: Phase A done CPU-side: W1 microbenchmarks, the store tools, the workspace suite, the identity row and bootstrap checks.
- 06:21Z: Phase B on node 2. `w1.py --compile-only` under CUDA 13.0 (V13.0.88): the gated SASS is identical to 12.8/12.9's (`r20260930-062059-dc4d`).
- 06:24Z: **the first W1 run failed its numeric gate, before any timing** (`r20260930-062247-e371`): FADD and FFMA wrote 8 check words per thread where the host reads 16, and the cast's XOR check fold was vacuous (both operand orders XOR to `hi ^ lo`, so f and g cancelled). Fixed in 2cbcfcd4 and ab14291d; a vacuous gate now fails by name. No measurement came from that run.
- 06:33Z: **W1 prices measured** (`r20260930-063213-c94a`, below).
- 06:39Z: **a second cast loop** separates F2FP's own cost from its support instructions (`r20260930-063827-e4c6`, the same die; every other rate reproduces to five significant figures). Next: the eight `fp8.py` rows, then the two replays.
- 07:24Z: **all seven `fp8.py` rows passed** on dies 0, 2 and 7 (below). With W1 they are the eight run lines. No discrepancy against `BLACKWELL_SM120_E4M3_M16N8K32`.
- 07:29Z: the first two replays (`r20260930-072548-34f7`, `r20260930-072829-948b`) failed before any kernel ran: `tc_probe.py` took `--out '$RESEARCH_RUN_DIR'` literally. No measurement came from them. Relaunched with a shell that expands only `--out` (lesson below).
- 07:31Z: the relaunch (`r20260930-073046-6792`, `r20260930-073115-4da4`) ran only the layout check, because my run line lacked `--sweep`. These are not replays.
- 07:37Z: **both replays passed** with `--sweep --n-random 25000`, the lane's shape (`r20260930-073559-5abe` e4m3, `r20260930-073650-c9c5` e5m2; GPU 4). **Phase B's list is done; I hold no GPU.**
- 08:02Z: **`add.rn.f32x2` priced** (`r20260930-080124-a89c`, below). It builds for sm_120a as two `FADD`s; there is no `FADD2` here, so no add costs half of FADD's price. Panel revision row on `pearl-c-sm120` v1 attempt 5. The E2M1 cast was not re-measured (the reason is below the table).
- 08:40Z: **the E2M1 cast, split** (`r20260930-083408-d164`, below). The honest packing loop is 9.27 per code: ptxas packs four codes a word through F2FP's MERGE_C, at no cost. F2FP alone is 7.9–8.2 (Derived from three loops), so the credited 8.0 stands and there is no panel row. The coordinator withdrew the `fp8-recheck` jobs (Needs 4). I hold no GPU.
- 09:28Z: **2:4-sparse E4M3 `mma.sp` captured** (`r20260930-092239-f0d0`, below). The sparse word is one align-add over the 64-deep span, which is the dense step on the 32 stored products, not two chained k32 steps. It costs 0.5 W1 per logical MAC and 1.0 per nonzero product. I hold no GPU.
- 09:52Z: **GPU 1's E4M3 cast-and-store loop timed, with the packed form beside it** (`r20260930-094910-ddbc`, below). The port's loop costs 32.06 W1 per code and the packed form 16.00. Both are bound by their stores, at 2.00 SM-clocks per warp `STS`, not by the casts. I hold no GPU.
- 10:20Z: **wide stores meet GPU 1's ≤ 11.7** (`r20260930-101643-6b20`, below). The packed cast-and-store costs 8.72 W1 per code with `STS.64` (160-byte rows) and 8.75 with `STS.128` (192-byte rows). Both are bound by the casts, not the stores. At form_s5's 144-byte rows, bank conflicts put both back at 16.00. nvidia-smi is now sampled every 5 rep rounds, so the lease held the GPU 14.1 s, down from 58.0. I hold no GPU.
- 10:33Z: **W1 on all eight dies** (the coordinator's fill outputs at e41832fb, not recorded runs; Results). No price differs across dies by more than 0.033%. The packed E4M3 cast's rep rates sit on 786, 787 or 788 SM-clocks per loop iteration, so read it as 12.28–12.31 per code. Next: the capture fill as split GPU and CPU jobs.
- 11:07Z: **the capture fill is queued as split jobs** (Fill jobs below). 9d5abb09 adds `fp8.py --phase gpu|verify` for the step row. One GPU job is pinned to each die, and each captures four units in 20–30 s of lease. When they're all captured, it queues its own `gpus=0` verify job. By 11:05Z five dies had captured all their units. Dies 3, 5 and 6 are waiting on other lanes' jobs, and the verify jobs on CPU slots. **Push pending:** GitHub rejects this VM's token, so 9d5abb09 is local and on node 2 only (shipped by `r20260930-105644-7738`). I hold no GPU.
- 11:33Z: **the capture fill is done: 0 mismatches on 45.1 M fresh-seed elements, on all eight dies** (Results). All 32 units passed: E4M3 and E5M2 every-family steps and the floor-aimed E4M3 families, against the registered models. There's no discrepancy, so nothing needs confirming. The captures held each die for 20–30 s and were host-bound (flagged in Results). The 11:07Z push went through at 11:10Z, so 9d5abb09 is on origin. I hold no GPU.
- 12:35Z: **`cvt.rn.f16x2.e4m3x2` (E4M3 to FP16) costs 8.00 W1 per code, 16.00 per instruction** (`r20260930-122749-94e1`, Results; server.md 11:10Z's row). It's bit-exact against `verity.ml.tc.term.decode_e4m3` on all 65,536 inputs. The buffers were poisoned with 0xA5, and each op's no-write negative control was rejected. The GPU part ran as one prio-10 fill job (`--lease-via-fill`, 295bc0af) and held die 7 for 10 s. The packed E4M3 cast in the same run landed on 788 clocks again (12.31). I hold no GPU.
- 15:16Z: **the FP16 leaf costs 2.000 W1 per MAC** (`r20260930-151254-404a`, Results; server.md 14:48Z's first row). `mma.sync m16n8k16` with FP32 accumulation runs at 511.99 MACs per SM per clock against E4M3 k32's 1,023.98. That's at or above 1.93, so the leaf condition holds. The `HADD2` row was cancelled at 15:02Z (the assessor's `assessor-hadd2` had measured it), so I didn't run it. Its loops are built and tested at 73599997. The GPU part was one prio-10 fill job, which held die 7 for 10 s. I hold no GPU.
- 15:34Z: **FP16 MMA / `HADD2` co-issue measured** (`r20260930-152940-ae57`, Results and Needs 8; the coordinator's 15:19Z row). The loop is the leaf's 16 `HMMA.16816.F32` with n `HADD2` per iteration. The MMA rate stays within 2% of its alone rate through n = 48, drops 5.2% at n = 64 and 9.0% at n = 112, and falls off at n = 128 (−16.7%), where `HADD2` starts to bind. `HADD2` alone is exactly half rate (64.00 per SM per clock). All 18 ops passed the gates. The row was one prio-10 fill job, which held die 7 for 41 s. I hold no GPU.
- 17:19Z: **the rewrite-mix probe says no route saves anything** (`r20260930-171330-eece`, Results and Needs 9; server.md 16:12Z). At the deciding point (48 `HADD2`, 17 FADD, 7 `ldmatrix` and one STS/LDS pair per 16 HMMA, 2 warps per SMSP, 236 registers), the MMAs run at 448.28 MACs per SM per clock against 511.99 alone. So t_mix/t_solo = **1.142**, past the spec's 1.063. R2's 88-add point is 1.401. All 21 ops passed the gates, bit-exact against `mix_model`. The row was one prio-10 fill job, which held die 1 for 40 s. I hold no GPU.
- 18:25Z: **the copy-free deciding point runs at t_mix/t_solo = 1.115, above 1.055** (`r20260930-181838-7460`, Results and Needs 9; the coordinator's 17:53Z row). With fresh forms, ptxas builds the deciding point with 0 MOVs in the loop, against 101, and the MMAs run at 459.08 MACs per SM per clock against 511.99 alone. The 7 `ldmatrix` per 16 HMMA alone cost nothing (1.000). All 8 ops passed the gates, bit-exact against `mix_model`. The row was one prio-10 fill job with no sampler, which held die 6 for 10 s. I hold no GPU.
- 18:45Z: **the second capture fill is queued** (Fill jobs below; server.md 18:28Z, the coordinator's 18:30Z row). There are 16 GPU jobs, 2 per die, pinned with `on=`: the step captures (`fp8cap2-die<d>.sh`), which were all done by 18:40:50Z, and the chains at K = 2^16 and 2^18 (`fp8chain-die<d>.sh`). The CPU halves are `gpus=0` jobs that the GPU jobs queue. bf77c948 splits the chain row like the step row, and `r20260930-184046-4dfa` shipped it. **The whole fill holds about 0.5 GPU-h, not the 5 asked for.** The device's own work is about 20 s of that (Measured), and the rest is host work inside the lease. I hold no GPU.
- 22:15Z: the first gate run of the GPU check (`r20260930-221312-3234`, cc33f769) failed before any lease: `fp8_gpucheck.py` took `--out '$RESEARCH_RUN_DIR'` literally. No measurement came from it. 7aa3abf6 expands it.
- 22:55Z: **the GPU check passed its gate with 0 mismatches, and its fill is queued** (`r20260930-221543-8564`, Results; Fill jobs; the coordinator's 21:12Z row). `fp8_check.cu` runs the step model beside the tensor core in the same warp. The gate compared the GPU model with the CPU model bit for bit on every existing capture (`fp8cap2`, `fp8chain`). Eight `fp8gc-die<d>.sh` jobs (`gpus=1 on=<d> prio=10 max_min=8`) hold about 5.0 GPU-h (Estimated). Their first chunks kept the dies 99–100% busy, and the first production launch (1.07e9 tiles) passed its CPU re-check. The CPU re-check (about 17 core-hours) waits on pous's 4 CPU slots, so it will trail the GPU half by hours. The fill runner holds the dies for these jobs, in chunks of at most 6 minutes.
- 02:15Z: **migration handoff written** (research-notes `lanes/accounting/20261001T0215Z-handoff-from-e6a46970-migration.md`; Daniel's 6:55 PM PDT ruling). The GPU check's GPU half is done: all 8 jobs exited 0 between 23:39Z and 00:26Z, after 60 chunks and 5.11 GPU-h (Measured), leaving 98 GB of launch files. Its 40 CPU verify jobs and the second fill's 14 are queued, and none has started. I start no new work. The handoff supersedes this file's Needs.

## Results

### The FP8 step check on the GPU: the gate and the first fill launch: Measured, locked-2100

Run `r20260930-221543-8564` (head 7aa3abf6; `result.json` validation passed, and the harness's class is SUCCESS) ran on node 2. The GPU half ran as two fill leases (`--lease-via-fill`, `gpus=1 prio=10 max_min=8`). The first, `fp8gc-r20260930-221543-8564-0.sh` on GPU 6 (GPU-2b59d5fe), spent its 330 s budget with units left and exited 99. The second, `-1.sh` on **GPU 5 (GPU-0c776bca-b587-ee46-2218-f72d8f5f435a)**, UUID checked, finished the units, the smoke launches and the timing. Driver 580.173.02, CUDA 13.0.88; the library's sha256 is `d70ec7fb…`. The spec is the coordinator's 21:12Z row.
- **The kernel** (`fp8_check.cu`, `fp8_gpucheck.py`). Each lane generates its own fragment of the tile from a counter hash, through per-(kind, family) code tables. The warp runs one QMMA, then the integer-only step model of each spec on the same operands, and counts every word's mismatches per spec. It keeps a hash-drawn sample of tiles (all 128 words of a kept tile, with the device's words) and every tile where the primary flags a word, and it dumps the operands of the first 8 kept tiles. The chain kernel feeds each step's device word to the next step, as the chain row does, and records every word of one chain per launch.
  - SASS gate (Measured): each fused kernel holds exactly one QMMA of its kind (`QMMA.16832.F32.E4M3.E4M3`, `.E5M2.E5M2`, `.E4M3.E5M2`) and no floating-point instruction, and the model kernel holds none. 111–127 registers, 0 spills.
- **The gate, before any fill word counts:**

| check | compared | mismatches |
|---|---|---|
| Host port. The numpy generator against `gc_host_gen`; the host model against `cpu_words` and `fp8.step_model`; `mxf8` with random scales against `fp8.evaluate` | every kind and family | 0 |
| Step captures (`fp8-capture2`, 128 units). The GPU model's words of every ported candidate against `fp8.evaluate`, and its primary against the core kernel | 188,720,128 elements × every candidate | **0** and **0** |
| The GPU's verdict on each step capture against the CPU verify's `probe_results.json` | 107 of 107 CPU-verified units | all agree |
| Chain captures (`fp8-chain`, 31 units). The GPU's step replay from the device's previous words, on both 64-step end windows, against the core kernel, for the SM120, Ada and Hopper models | 25,165,824 window words | **0** for each model |
| Every chain step word of the device against the GPU's primary | 1,006,632,960 words | **0** (Ada 864,727,149, Hopper 864,721,875) |
| The GPU's chain verdicts against the CPU verify's | 6 of 6 | all agree |
| Fused smoke launches: every tile kept and dumped, one word corrupted, 4 specs. The operands against the generator, each tile's counts against the CPU models, and the flags | 39 launches, 933,888 words | 0 failures; 39 of 39 controls flagged; 0 primary flags beyond them |

The gate compared the GPU model with the CPU model directly on all 159 units. So it didn't wait for the second fill's CPU verify, of which 21 step and 25 chain units are still queued (Fill jobs).
- **Timing** (Measured, cudaEvent, one die, 376 blocks of 8 warps):
  - Step launches: 7.88e7 tiles/s with 1 spec (1.0e10 words/s), 4.36e7 with 2, and 2.28e7 with 4.
  - Chains: 8.10e7 steps/s with 1 spec and 4.49e7 with 2.
  - The model sets the rate, not the tensor core: each spec costs about as much as the first.
- **The first production launch** (die 2, GPU-1cd543c7; `e4m3-s20264200`, `g_randn_zero_acc` launch 0; re-checked on this agent VM with the same code):
  - 1,069,337,984 tiles (136.9e9 words) in 24.3 s on the device.
  - The primary mismatches on 1 word (the planted control), and `(32,) w25 f-133` on 1. This family doesn't separate the two widths; `g_randn_random_acc`'s launch 0 has w25 at 2.2e10 of 1.4e11 words.
  - 261,193 tiles were kept: 261,192 sampled at 1 in 4,096 and 1 flagged.
  - The CPU agrees with the GPU's counts on every kept tile, for both specs (0 disagreements). The dumped operands are the generator's (0 on A, Bt and C). The control is flagged, and no other word is.
  - The re-check took 93 CPU-seconds and peaked at 6.1 GB.
- The GPU was 99–100% busy in the fill's first four chunks, by gpu-lease's sampler.

**Flagged shortcuts:**
- **The gate's leases held their GPUs 5m44s at 17% busy and 4m26s at 30%.** They read 8.2 GB of old captures from scratch. This is one-time; the fill generates its operands on the device.
- **"Fresh seeds" are fresh draws, not fresh tables.** The operand tables are fixed per (kind, family) at `TABLE_SEED` 20261001, and a unit's seed chooses which of the 4,096 codes each element draws. So each FP32 accumulator family has 4,096 values across every seed.
- **The sample is 1 in 4,096 tiles (steps) and 1 in 8,192 (chains), not the 1 in 1,000 asked for.** Each kept tile stores its 128 device words, so 1 in 1,024 would write about 0.4 TB and need about 60 CPU core-hours (Estimated). The chosen rates re-check 2.1e10 words, about 105 GB and 17 core-hours. Every flagged word is kept at any rate.
- **Two specs per launch (the primary and `(32,) w25 f-133`), not four.** Each spec costs as much as the primary, so four would halve the words checked. Ada and Hopper are refuted by the gate and by every earlier row.
- The first launch was re-checked on this agent VM, not in a node-2 fill job. The unit's verify job checks it again.
- The fill's outputs are fill outputs, not recorded runs. Only the gate is a recorded run.

### For bc-3006c44a: the rewrite mix's `ldmatrix` share and its copy-free floor: Measured, locked-2100

Run `r20260930-181838-7460` (head 90843af6; `result.json` validation passed, and the harness's class is SUCCESS) ran on node 2, **GPU-2b59d5fe-4acb-287b-5e52-06608509c519 (index 6)**, UUID checked. Driver 580.173.02, CUDA 13.0.88. The spec is the coordinator's 17:53Z row, from `theory-pearl-c-sm120.md` §14's 17:50Z addendum.
- **How it ran:** one fill job, `w1-r20260930-181838-7460.sh` (`gpus=1 max_min=8 prio=10`), 18:20:58–18:21:08Z on its first start. It preempted nobody and wasn't preempted; a preempted chunk exits 99 and is requeued (90843af6, tested). The run had no sampler (`--no-sampler`), so nothing of the harness's ran beside the timed loops. The operands are on the device.
- **The loops** are the previous row's frame (one block of 8 warps per SM, 2 per SMSP, 64 `HMMA.16816.F32` per warp and iteration, 236 registers), with three new ops (69–71):
  - `mix_h0_f0_l7` is item (1) as the coordinator wrote it: the MMAs and the deciding point's 7 `ldmatrix` per 16 HMMA (14 `LDSM.16.M88.4` and 14 `.2` per 64 HMMA), nothing else. Each load writes resident sub-block words that the next MMAs read, so none is dead. Each reads its own 128-byte window of a 17-matrix tile, so ptxas can't merge repeated loads.
  - `mix_h0_f17_l7` is item (1) as the addendum wrote it: the same loads with h0_f17's 17 FADD and one STS/LDS pair per 16 HMMA.
  - `mix_h48_f17_cf` is item (2): the deciding point (48 `HADD2`, 17 FADD, 7 `ldmatrix`, one STS/LDS pair per 16 HMMA) with fresh forms. Each form is one add of two distinct resident sub-blocks, X = S + S′, which ptxas builds straight into the HMMA's operand registers.
- **SASS gate (Measured, the pod's cubin):** each loop is exactly its counts. For the three new ops MOV is a watched instruction, so a single MOV in the loop fails the gate. There are **0 MOVs in all three loops**, against 101 (25.25 per 16 HMMA) in `mix_h48_f17`'s. Counting whole kernels, prologue and epilogue included, they have 2, 4 and 6 MOVs, against 109. There's no FTZ, LDL or STL, and STACK and LOCAL are 0.
- **Gates, all before timing, on all 188 blocks:** identity, SASS, one block per SM, and the numeric gate. That gate runs 8 iterations and checks them bit-exact against `mix_model`, which now models the fresh forms and the loads' direct feed. There were **0 mismatches on all 8 ops**. The buffers were poisoned with 0xA5, and every no-write control was rejected (1,540,096 mismatching words and a single SM id).
- nvidia-smi read 2,092 MHz, with no clock-event reasons, before round 0 and after rounds 4 and 9. Cycles over event time gave 2,049–2,096 MHz. There were 10 reps of about 64 ms per op. Rep spreads are ≤ 8 ppm on the new ops and 470 ppm on h0_f17.

| Point | Per 16 HMMA: `HADD2` / FADD / `ldmatrix` / STS-LDS pairs | Forms | MMA MACs/SM/clk | t_mix/t_solo | Loop MOVs per 16 HMMA |
|---|---|---|---|---|---|
| The leaf's loop (`hmma_f16_f32`), solo | 0 / 0 / 0 / 0 | – | 511.991 | 1.000 | 0 |
| MMAs alone (h0_f0) | 0 / 0 / 0 / 0 | – | 511.999 | 1.000 | 0 |
| **(1) h0_f0_l7** | 0 / 0 / 7 / 0 | – | 511.984 | **1.000** | 0 |
| MMAs and FADDs (h0_f17) | 0 / 17 / 0 / 1 | – | 495.07 | 1.034 | 0 |
| **(1′) h0_f17_l7** | 0 / 17 / 7 / 1 | – | 496.00 | **1.032** | 0 |
| h48, the deciding point as before | 48 / 17 / 7 / 1 | chained | 447.14 | 1.145 | 25.25 |
| **(2) h48, copy-free** | 48 / 17 / 7 / 1 | fresh | **459.08** | **1.115** | **0** |

The rates are Measured, and t_mix/t_solo is Derived from them (the solo rate over the point's). The MOVs are Measured, from the SASS.

**What it settles:**
- **The copy-free deciding point runs at t_mix/t_solo = 1.115** (Derived). That's above 1.055 and 1.063, so by the addendum's thresholds the MOV caveat is closed at any cast, and v1 fits 1% as written.
- **The copies and the form chain together cost 2.7%** (1.145 against 1.115, Derived, same die and run). That's 0.030 of the loss of 0.145; the other 0.115 remains with no copy at all.
- **The `ldmatrix` share is zero.** Alone, the 7 loads per 16 HMMA leave the MMAs at 1.000 (511.984 against 511.991). Beside h0_f17's FADDs and round trip they give 1.032 against h0_f17's 1.034, a −0.19% difference, inside ptxas's schedule grain.
- **The components don't add up to the mix.** 1.034 (h0_f17) × 1.000 (the loads) × 1.008 (48 independent `HADD2`, co-issue row `r20260930-152940-ae57`) is 1.042, and the copy-free mix is 7.0% above that. What's left comes from the adds feeding the operands: each HMMA waits on its forms' `HADD2`s, and 2 warps per SMSP hide less of that latency than the co-issue row's 4, whose adds fed nothing (Conjectured, from the counts).
- The chained deciding point runs at 1.145 on die 6, against 1.142 on die 1 in `r20260930-171330-eece` (the same loop, instruction for instruction): 0.26% between dies and runs. h0_f0 and h0_f17 reproduce, at 1.000 and 1.034.

**Flagged shortcuts:**
- **Fresh forms give an optimistic floor.** Besides the MOVs, they drop the chained forms' `HADD2`-to-`HADD2` dependency (X + S″ on the previous add). So 1.115 is at or below a copy-free schedule of the chained forms, and 2.7% is an upper bound on the copies' own cost. The verdict doesn't need the two separated, since even this floor is above 1.063. The spec (`rewrite-mix.md` §Dependencies) allows fresh or chained forms. Every add's operand pair is distinct (ptxas merges equal adds); the schedule test checks it, and the SASS's 192 `HADD2` confirm it.
- In the l7 ops the loads feed the MMAs directly, where a route's loads feed the adds. Each load reads its own tile window, and a real layout's bank pattern isn't modelled.
- As before, the STS/LDS pair is a same-thread round trip on one word, and one register structure (236, with ballast) serves every point. One die and one run.

### The FP8 v1 rewrite's per-MMA mix: Measured, locked-2100

Run `r20260930-171330-eece` (head cf26da18; `result.json` validation passed, and the harness's class is SUCCESS) ran on node 2, **GPU-fb680060-f371-db1a-73ba-8f2eef43674c (index 1)**, UUID checked. Driver 580.173.02, CUDA 13.0.88. The spec is bc-3006c44a's `min-merge-search/rewrite-mix.md` with its 16:20Z amendment (server.md 16:12Z).
- **How it ran:** one fill job, `w1-r20260930-171330-eece.sh` (`gpus=1 max_min=8 prio=10`), 17:14:13–17:14:53Z on its first start; it preempted nobody. The library was built and SASS-gated on the pod before the job was queued. The gate rows and model words take about 0.5 s of CPU inside the job (server.md 15:31Z's trivial CPU work).
- **The loop** (`w1_prices.cu`'s `mix_*`, ops 50–68). One block of 8 warps per SM, 2 per SMSP. Per warp and iteration: 64 `HMMA.16816.F32` in four groups of 16, as 4 interleaved chains of 4, among the point's adds, FADDs, `ldmatrix`, converts and 4 STS/LDS pairs. Per 16 HMMA these are the spec's counts. At the deciding point: 48 `HADD2`, 17 FADD, 7 `ldmatrix` (3.5 x4 and 3.5 x2) and one STS/LDS pair.
  - The adds build the HMMA operands. They are block-adds of resident sub-blocks (an A form is 4 `HADD2`, a B form 2): X = S + S′, then X + S″. There is one form buffer per chain, and a form is rewritten 4 slots after the HMMA that reads it.
  - Each chain's first HMMA in a group starts from zero. The merges (acc[c] += acc[c+2], 4 FADD each) seed later HMMAs. The promotions (4 FADD) add each chain's group result into 64 resident totals, chain 0's word through the STS/LDS round trip.
  - The converts (3 per 64 HMMA at the route points) rewrite a freshly loaded sub-block word, which the adds then read.
- **SASS gate (Measured):** every loop is exactly its counts, besides `UIADD3`, `UISETP`, `BRA`, NOPs and MOVs (recorded): 64 `HMMA.16816.F32`, n_H `HADD2` (no `HFMA2`), n_F FADD, the `F2FP.F16.E4M3.UNPACK_B` converts, `LDSM.16.M88.4` and `.2`, 4 STS and 4 LDS.
  - There's no FTZ, LDL or STL anywhere in these kernels, and STACK and LOCAL are 0.
  - Registers are 232–240, from `__maxnreg__(240)` plus a ballast of loaded words held across the loop. h256 and R2-con-flat are the exceptions, at 226.
- **Gates, all before timing, on all 188 blocks:** identity, SASS, and one block per SM.
  - The numeric gate runs 8 iterations on per-lane rows whose FP16 halves are ±0.25, 0.5, 0.75 or 1. It checks all 32 words of every thread bit-exact against `mix_model`.
  - `mix_model` is an exact-integer model of the same schedule: the forms, the m16n8k16 fragment layout, the merges, the promotions and the final sums. It raises if any step leaves the range where every rounding order is exact.
  - There were **0 mismatches on all 21 ops**. Every no-write control was rejected (1,540,096 mismatching words and a single SM id). The buffers were poisoned with 0xA5.
- nvidia-smi read 2,092 MHz, with no clock-event reasons, before round 0 and after rounds 4 and 9. Cycles over event time gave 2,051–2,099 MHz. There were 10 reps of about 63 ms per op. Rep spreads are ≤ 807 ppm (h40), and 14 ppm at the deciding point.
- **The MMA-alone references agree:** the leaf's loop (`hmma_f16_f32`, 16 warps) runs at 511.992 MACs per SM per clock, and the mix kernel's MMAs alone (`mix_h0_f0`, 8 warps, 64 HMMA, 4 chains) at 511.999. So the frame costs nothing, and t_mix/t_solo is the same against either.

| Point | Per 16 HMMA: `HADD2` / FADD / `ldmatrix` / cvt | MMA MACs/SM/clk | t_mix/t_solo | MOVs per 16 HMMA | Registers |
|---|---|---|---|---|---|
| MMAs alone (h0_f0) | 0 / 0 / 0 / 0 | 511.999 | 1.000 | 0 | 236 |
| MMAs and FADDs (h0_f17) | 0 / 17 / 0 / 0 | 495.07 | 1.034 | 0 | 236 |
| h32 | 32 / 17 / 7 / 0 | 456.11 | 1.123 | 15.75 | 234 |
| h40 | 40 / 17 / 7 / 0 | 442.93 | 1.156 | 21.75 | 236 |
| **h48, the deciding point** | **48 / 17 / 7 / 0** | **448.28** | **1.142** | 25.25 | 236 |
| h56 | 56 / 17 / 7 / 0 | 436.17 | 1.174 | 39.5 | 236 |
| h64 | 64 / 17 / 7 / 0 | 418.09 | 1.225 | 43.75 | 234 |
| h80 | 80 / 17 / 7 / 0 | 382.27 | 1.339 | 64.25 | 235 |
| h96 | 96 / 17 / 7 / 0 | 360.75 | 1.419 | 82.75 | 235 |
| h112 | 112 / 17 / 7 / 0 | 338.79 | 1.511 | 80.5 | 236 |
| h128 | 128 / 17 / 7 / 0 | 324.43 | 1.578 | 77.75 | 238 |
| h160 | 160 / 17 / 7 / 0 | 283.09 | 1.809 | 78.25 | 232 |
| h192 | 192 / 17 / 7 / 0 | 257.28 | 1.990 | 68.25 | 240 |
| h256 | 256 / 17 / 7 / 0 | 210.38 | 2.434 | 80.25 | 226 |
| R1-LB-flat | 30 / 19 / 7.5 / 0.75 | 459.73 | 1.114 | 13 | 235 |
| R1-LB-BR | 30 / 62 / 7.5 / 0.75 | 423.87 | 1.208 | 8.75 | 232 |
| **R2-LB-flat** | **88 / 21 / 7 / 0.75** | **365.51** | **1.401** | 72.5 | 234 |
| R2-LB-BR | 88 / 36 / 7 / 0.75 | 350.69 | 1.460 | 73 | 236 |
| R2-con-flat | 248 / 21 / 7 / 0.75 | 212.24 | 2.412 | 76 | 226 |

The rates are Measured, and t_mix/t_solo is Derived from them (511.99 over the point's rate). The MOVs and registers are Measured, from the SASS.

**What it settles:**
- **The deciding point runs at t_mix/t_solo = 1.142** (Derived), past both of the spec's thresholds (1.042 and 1.063). By the spec's reading, no route saves anything. At Πρλ 0.941–0.956, 1 − Πρλ·1.142 is −7.5% to −9.2% of the block (Derived); breaking even would need s ≤ 1.046–1.063.
- **R2's 88-add point runs at 1.401.** 1 − 0.4691·λ·1.401 is −31.4% of its block at λ = 2.000 and −30.5% at 1.986 (Derived). R1-LB-flat runs at 1.114: −10.6% and −9.8% (break-even 1.007–1.014).
- **The FADDs and the shared-memory trip alone cost 3.4%** (h0_f17, Measured). The first 32 adds with their 7 `ldmatrix` take the loss to 12.3%. The curve then climbs about 1.5% per 8 adds to n = 64, and steeply after that.
- **In the co-issue row** (`r20260930-152940-ae57`), 48 independent `HADD2` cost the MMAs 0.78%. Here the adds feed the operands, the merges feed seeds, and 2 warps per SMSP hide less latency than 4. At the deciding point neither the FMA pipe (about 44% of the MMAs' time, at 2 clocks per `HADD2` and 1 per FADD; 54% if the MOVs run there too) nor issue (about 46% of slots, MOVs included) is full. So the loss is dependency latency and scheduling, not throughput (Conjectured, from the counts).

**Flagged shortcuts:**
- **The MOVs.** ptxas copies registers in every loop: 25 per 16 HMMA at the deciding point, 72.5 at R2-LB-flat. They come from the probe's forms, which are built in place in loop-carried registers while the HMMA needs an aligned quad. A hand-scheduled rewrite may need fewer, and this run can't separate their cost. To bring s from 1.142 down to 1.063, they would have to account for more than half the loss.
- h40 is slower than h48 (1.156 against 1.142). Neighbouring points differ in ptxas's schedule by about 1–2%, so read the curve at that grain.
- One register structure serves every point: about 200 live values, the rest ballast loaded before the loop and folded into the check words after it (live, but untouched in the loop). It isn't each route's own layout (R2's two-warp split, for example).
- The STS/LDS pair is a same-thread round trip on one word, not a cross-warp exchange: there's no barrier and no bank conflict.
- The forms restart every iteration from resident sub-blocks, with every coefficient +1 (`HADD2`, no `HFMA2` with ½).
- The converts are 3 per 64 HMMA at the route points (0.75 per 16, against the spec's 0.65 and 0.81), and there are none in the sweep. The sweep is at n_F = 17 (the amendment's), not the original spec's 21 and 36.
- R1-con-flat wasn't run, because it spills at 240 registers. h256 and R2-con-flat run at 226: a ballast of 2 words gives 226, and 4 spill.
- In the gate, the converted low bytes are 0x00 (zero). The timing rows are other data: random halves in [0.5, 2) with fraction bit 6 clear, so no convert reads a NaN code.
- `ldmatrix` reads a warp tile laid out so that each lane gets its own words. A real layout's bank pattern isn't modelled.
- One die and one run.

### FP16 MMA and `HADD2` co-issue: Measured, locked-2100

Run `r20260930-152940-ae57` (head 7dcce2c1; `result.json` validation passed, and the harness's class is SUCCESS) ran on node 2, **GPU-af0bf9e0-2a17-98be-19b6-f184292c3842 (index 7)**. The UUID was checked, as for the leaf row. Driver 580.173.02, CUDA 13.0.88.
- **How it ran:** the leaf row's way. One fill job, `w1-r20260930-152940-ae57.sh` (`gpus=1 max_min=8 prio=10`), queued while all eight GPUs were busy. It started at 15:30:54Z, was done at 15:31:35Z on its first start, and preempted nobody. There was no `--timed` lease: the coordinator confirmed at 15:19Z that a per-SM-per-clock rate doesn't need one.
- **The loops** (the SASS gate, Measured). Each `coissue_h<n>` loop is exactly the leaf's 16 `HMMA.16816.F32` and n `HADD2`, besides `UIADD3`, `UISETP.NE.AND`, `BRA.U` and ptxas's NOPs. The `HADD2`s use the pure `{y.hi, y.hi}` form, with no PRMT in the loop and no FTZ. The k-th MMA is followed by `HADD2` number ⌊kn/16⌋ up to ⌊(k+1)n/16⌋, on 8 chains in turn. ptxas spaces the MMAs with 15 NOPs at n = 0, and the `HADD2`s take their place: 15 at n = 4, 10 at n = 48, 2 at n = 112, none from n = 128.
- **Gates, all before timing, on all 188 blocks:** identity, SASS, and one block per SM.
  - Every warp runs both the MMAs and the chains. Even warps store the accumulators, with all-ones operands, so every word must be 512. Odd warps store the 8 `HADD2` chains. Those are drawn per lane from the timing rows and checked against `h16_steps`, one FP16 rounding per step of an exact float64 sum. Their other 8 words must keep the 0xA5 poison. So each output is checked at every lane position, on half the warps.
  - There were **0 mismatches** on all 18 ops, which also include the leaf alone (n = 0), `HADD2` alone and the unit.
  - Every no-write negative control was rejected: 770,048 to 1,540,096 mismatching words and a single SM id.
- nvidia-smi read 2,092 MHz, with no clock-event reasons, before round 0 and after rounds 4 and 9. Cycles over event time gave 2,083.7–2,098.7 MHz. There were 10 reps of about 64 ms per op. Rep spreads are ≤ 6 ppm, except 985 ppm at n = 256.
- **`HADD2` alone** runs at 63.999 registers per SM per clock, 0.500 SM-clocks per warp instruction. That's 16.00 W1 per register, 8.00 per FP16 element. The assessor's `assessor-hadd2` measured about 61.
- The table, per n, is in Needs 8.

**What it settles:**
- **Up to n = 48 `HADD2` per 16 MMAs, the pre-adds hide beside the FP16 MMAs** (Measured). n = 48 is one register per 21 MACs. The MMA rate loses 0.4–1.9%. Each co-issued `HADD2` register adds 0.33–3.0 W1 of time, against 16.0 alone (Derived: the added SM-clocks per warp iteration × 1,023.98 / 32n).
- **From n = 64 to 112, the MMA loses 5.2–9.0%.** Each register still adds only 1.6–1.8 W1, 10–11% of its cost alone (Derived).
- **The knee is n = 128.** There, both pipes would need 64 SM-clocks per warp iteration. The loop takes 76.8, with both pipes at 83%. From n = 128 on, `HADD2` binds (0.83–0.93 of its alone rate), and the MMA rate falls as about 1/n. The utilization sum (MMA fraction + `HADD2` fraction) peaks at **1.71, at n = 112**. The assessor's 14:58Z line cites a measured co-issue of at most 1.45. That may be a different loop or quantity; I haven't reconciled the two.
- **Below 2%, the losses don't grow with n:** n = 48 loses less than n = 24 or 32. The loop period is quantized to 0.25 SM-clocks per warp iteration (one SMSP clock per iteration of its four warps), and ptxas places the `HADD2`s among its NOPs differently at each n. So these small losses are scheduling, not a pipe limit (Conjectured).
- **Flagged shortcuts:**
  - One die and one run.
  - The operands are in registers, in a steady loop. A real pre-add also loads its operands (shared memory or `ldmatrix`), and that isn't measured here.
  - Each output is checked on half the warps, as above.
  - The negative control skips the launch.

### The FP16 leaf, `mma.sync m16n8k16 f32.f16.f16.f32`: Measured, locked-2100

Run `r20260930-151254-404a` (head 73599997; `result.json` validation passed, and the harness's class is SUCCESS) ran on node 2, **GPU-af0bf9e0-2a17-98be-19b6-f184292c3842 (index 7)**, the same die as the 12:35Z row. The UUID was checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88.
- **How it ran:** the same way as the 12:35Z row. The run built the library and SASS-gated it on node 2 with no GPU, then queued one fill job, `w1-r20260930-151254-404a.sh` (`owner=bc-e6a46970 gpus=1 max_min=8 cpus=8 project=pous prio=10`, no `on=`). That job waited about 47 s in the queue, then ran from 15:14:00Z to 15:14:10Z on its first start and preempted nobody.
- **The loops** (the SASS gate, Measured): each is 16 MMAs, 15 `NOP`, `UIADD3`, `UISETP.NE.AND` and `BRA.U`, the same shape as the unit's loop. The new loop is 16 `HMMA.16816.F32`, and there's no FTZ.
- **Gates, all before timing, on all 188 blocks:** identity, SASS, and one block per SM.
  - The numeric gate uses all-ones operands, so every accumulator word must be exactly 512. There were **0 mismatches** on every op.
  - Buffers were poisoned with 0xA5 before every gated launch.
  - **Each op's no-write negative control was rejected:** it left 1,540,096 mismatching words and a single SM id.
- nvidia-smi read 2,092 MHz, with no clock-event reasons, before round 0 and after rounds 4 and 9. Cycles over event time gave 2,083.1–2,094.2 MHz. There were 10 reps of 63.8 ms per op.

| loop | MACs per SM per clock | rep spread | W1 price per MAC |
|---|---|---|---|
| dense E4M3 `m16n8k32`, FP32 accumulate (the unit) | 1,023.983 | 0.3 ppm | 1 |
| **FP16 `m16n8k16`, FP32 accumulate** | **511.992** | 0.2 ppm | **2.000** |
| FP16 `m16n8k16`, FP16 accumulate | 511.992 | 0.2 ppm | 2.000 |
| BF16 `m16n8k16`, FP32 accumulate | 511.992 | 0.2 ppm | 2.000 |

**What it settles:**
- **The leaf is 2.000 W1 per MAC** (Measured: 2.0000001, and 2.0000007 with FP16 accumulation). That is at or above bc-3006c44a's 1.93, so the leaf condition of v1's pre-add closure holds. It agrees with the assessor's 2.0 (`r20260930-060338-26b9`, 507 against 1,011–1,016).
- **The accumulation type doesn't change the leaf's cost:** FP32 and FP16 accumulation, and BF16 inputs, issue at the same rate to under 1 ppm.
- **Flagged shortcuts:**
  - One die and one run.
  - This is the issue rate of a steady loop with operands in registers. It is not whole-GEMM wall time, the convention the assessor's caveat (iii) names (15:02Z line of `ratings.md`).
  - No `--timed` lease. A fill row can't carry one: the runner wraps fill jobs in `--preemptible` leases, and a `--timed` lease would have requeued every GPU fill job on the node, GPU 3's running v2-hot chunk included. The rate is per SM per clock, and neighbours can only move the clock, which is recorded above.
  - The gate is all-ones, as for the other atoms. It is not a random-data comparison against a registered FP16 model.
  - The negative control skips the launch; it doesn't run a kernel that writes nothing.
  - The co-issue of pre-adds with FP16 MMAs (the time-only item in `concurrent-budgets/sm120`) is not measured here. See Needs 8.

### E4M3 to FP16, `cvt.rn.f16x2.e4m3x2`: Measured, locked-2100

Run `r20260930-122749-94e1` (head 295bc0af; `result.json` validation passed) ran on node 2, **GPU-af0bf9e0-2a17-98be-19b6-f184292c3842 (index 7, bus FE:00.0)**, with the UUID checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88.
- **How it ran:** the run built the library and SASS-gated it on node 2 with no GPU. It then queued its GPU part as one fill job, `w1-r20260930-122749-94e1.sh`, with `owner=bc-e6a46970 gpus=1 max_min=8 cpus=8 project=pous prio=10` and no `on=`, and waited. The job waited 3.5 min in the queue, started at 12:31:46Z and was done at 12:31:56Z on its first start. It preempted nobody, and its results are this run's. The child's own wall was 6.1 s.
- **The loops** (the SASS gate, Measured: each loop is exactly this, besides `UIADD3`, `UISETP.NE.AND` and `BRA.U`; there is no PRMT and no FTZ):
  - `f2fp_f16_e4m3`: 8 chains, each feeding a convert's low half back into the next. It's 64 `F2FP.F16.E4M3.UNPACK_B` and nothing else.
  - `f2fp_f16_e4m3_half`: the same, XORing the lane's constant in before every other convert. It adds 32 `LOP3.LUT`.
  - `f2fp_f16_e4m3_xor`: XORs it in before every convert, adding 64 `LOP3.LUT`.
- **Gates, all before timing, on all 188 blocks:** identity, the SASS gate and one block per SM.
  - The numeric gate compares against `verity.ml.tc.term.decode_e4m3`, the registered decode. It covers the chains, and every thread's first 8 words, which convert every 16-bit input once (all 65,536). There were **0 mismatches** on every op.
  - Both NaN codes, 0x7F and 0xFF, come out as FP16 **0x7FFF**, so the device drops the NaN's sign (Measured). The gate requires a NaN half to be an FP16 NaN. The decode names no NaN bits, so these bits are only recorded.
  - Every gated launch started from chk, cycles and sm poisoned with 0xA5. A word an op doesn't write must still read 0xA5A5A5A5 (8 per thread for the E4M3 cast).
  - **Each op's no-write negative control was rejected:** a launch that runs no kernel leaves the poison. That gave 1,540,096 mismatching words (770,048 for the E4M3 cast) and a single SM id, so the gate fails it. This is server.md 11:50Z's rule, so these rows can go on the panel as measured (`--negative-control`).
- nvidia-smi read 2,092 MHz, with no clock-event reasons, before round 0 and after rounds 4 and 9. Cycles over event time gave 2,086.8–2,094.7 MHz. There were 10 reps of about 63 ms per op.

| loop | rate per SM per clock | rep spread | W1 price per code | per instruction (2 codes) |
|---|---|---|---|---|
| dense E4M3 MMA (the unit) | 1,023.983 MAC | 0.3 ppm | 1 per MAC | |
| **`cvt.rn.f16x2.e4m3x2` alone** | 127.998 codes | 0.3 ppm | **8.000** | **16.000** |
| the same + 1 LOP3 per 2 converts | 85.290 codes | 3.7 ppm | 12.006 | |
| the same + 1 LOP3 per convert | 63.955 codes | 4.5 ppm | 16.011 | |
| E4M3 cast, packed (`cvt.rn.satfinite.e4m3x2.f32`) | 83.166 codes | 1,274 ppm | 12.312 | 24.625 |

**What it settles:**
- **The FP16 convert is 8 W1 per code, not 4** (Measured). bc-3006c44a's "4, probably 8" is 8. It issues at half rate: 0.500 SM-clocks per warp instruction, 64 lanes per SM per clock.
- **The costs add, so the bare loop is priced right** (Derived from the three loop periods). The bare loop's chains reach 0 within about 3 converts: an FP16 image of an E4M3 value has a low byte of 0x00 or 0x80. The XOR-fed loops keep live data. Adding the first 32 LOP3 costs 16.024 SM-clocks per warp iteration, and adding the second 32 costs 16.021. The two steps agree to 0.02%, so a zero-data fast path would have shown. The rate also doesn't depend on the data.
- **LOP3 contends with the convert** (Derived): each LOP3 warp instruction adds 0.5007 SM-clocks, the same as a convert. So a post-add path pays 8 per code for the convert, plus 16 per lane-instruction (8 per code at one per convert) for each integer support instruction that shares its pipe. That matches the E4M3 cast's finding (W1 section): F2FP contends with every integer instruction in its loop at about half an SM-clock. I measured LOP3 only. PRMT and IADD3 sharing that pipe is Conjectured from the E4M3 cast's fit.
- **The 786/787/788 spread moves the published 12.31 by −0.016 to −0.031 per code** (Derived: 65,536 codes per SM per iteration over L clocks, in W1 units). 12.31 is L = 788, the top of the range. L = 787, the eight-die fill majority, gives 12.297, which is −0.016 or −0.13%. L = 786 gives 12.281, which is −0.031 or −0.25%. This run's reps sat 7 on 788 and 3 on 787, with the median on 788. So that's six recorded runs of six on 788, while the fill runs sat on 787. As a cost, 12.31 is the conservative reading.
- **Flagged shortcuts:** one die and one run. The bare loop's chains carry zero data after about 3 converts, but it's priced by the additivity check above, not by live data. The negative control skips the launch; it doesn't run a kernel that writes nothing.

### FP8 steps with fresh seeds on all eight dies, split capture and verification: fill outputs, not recorded runs, locked-2100

**These are fill outputs, not recorded runs.** The 16 jobs under Fill jobs ran 9d5abb09's `fp8.py --row step`. Each die's `gpus=1` job ran `--phase gpu` on its four units, loading the library that `r20260930-105644-7738` built and gated (the sha256 checked before each chunk). A `gpus=0` job then ran `--phase verify` on those units. The outputs are node 2's `/workspace/pouw/fill-out/fp8-capture/die<d>/<unit>/`: `step_gpu.json`, `tiles_<instruction>.npz`, `probe_results.json` and `capture_sample.json`, 336 MB in all. They have no run id, so nothing is in the evidence store and no label can point at them.
- **Gates, all before capture, on every unit:**
  - Identity: the name, SM count, driver and UUID, with the UUID checked against `GPU_LEASE_UUID`. Every unit's UUID is its job's pinned die (the UUIDs and buses are in the W1 eight-die table below).
  - The SASS gate, on the prebuilt library's own dump.
  - The layout check.
- **All 32 units passed, with 0 mismatches against the registered models on 45,106,176 elements and 0 record-only mismatches** (Measured). The seed is 20261100 + 10d + j on die d: E4M3 at j = 0 and 1, E5M2 at j = 2, and the floor units at j = 5.

| units | model | passed | elements (gated) | mismatches | nearest alternatives: mismatches per unit, the range over units |
|---|---|---|---|---|---|
| `f8_e4m3`, every family, `--n-random 4096`: 2 seeds per die | `BLACKWELL_SM120_E4M3_M16N8K32` | 16/16 | 21,682,176 (21,616,128) | **0** | `(32,) w26 f-123` 6,507–7,189; `(32,) w27 f-133` 43,184–43,564; `(16,16) w26 f-133` 75,135–75,876 |
| `f8_e5m2`, every family, `--n-random 4096`: 1 seed per die | `blackwell_sm120_e5m2_m16n8k32` | 8/8 | 10,841,088 (10,802,496) | **0** | `(32,) w26 f-123` 6,476–7,144; `(32,) w27 f-133` 49,001–49,861; `(16,16) w26 f-133` 83,079–83,869 |
| `f8_e4m3`, `acc_floor,subnormal_isolated,wide_spread`, `--n-random 65536`: 1 seed per die | `BLACKWELL_SM120_E4M3_M16N8K32` | 8/8 | 12,582,912 (all) | **0** | `(16,16) w26 f-133` 32,334–33,045; `(32,) w26 f-123` 44,792–45,429; `(32,) w27 f-133` 56,815–57,496 |

Hopper's `(32,) w14 f-139` and Ada's `(16,16) w14 f-139` are refuted by 652,657–1,015,363 per unit, on every unit.

**What it settles:**
- **The registered E4M3 and E5M2 steps hold on each of node 2's eight dies, with 24 fresh seeds.** Before this, each step model had been checked on one or two dies. There's no discrepancy, so no fresh-seed confirmation is needed.
- **The floor-aimed families now agree at 16× the Phase B row's sample, on every die.** The nearest alternative, `(16,16) w26 f-133`, is refuted by at least 32,334 per unit. Phase B's 98,304 elements refuted it by 1,978, and 16 × 1,978 = 31,648, so the margin grows with the sample (Derived).
- **The split reproduces the one-process row's verdict.** A test pins the split word for word to the one-process run. So these units are the same check as Phase B's rows, with the GPU freed before the CPU verification.
- **Timings (Measured):**
  - The captures ran 11:02:32–11:07:23Z, and each die's job held its lease 20–30 s for four units.
  - The verifications ran 11:07:43–11:28:48Z, 27.7–34.4 s per unit on the fill runner's nice-19 CPUs and 2.0–2.2 min per job. All 16 jobs exited 0 on their first start.
  - nvidia-smi was read once per unit, by the identity gate.
- **Flagged: the capture is host-bound.** Device time was 0.01–0.17 s of each unit's GPU phase, which lasted 2.3–3.4 s for every-family units and 9.6–11.6 s for floor units. So most of a die's 20–30 s lease went to host work under the lease: operand generation, the gates and interpreter startup. At this scale that's under half a minute per die. Before scaling up, generate the operands in a `gpus=0` job and capture several seeds per process, so the lease covers only the gates and the device.
- **Other flagged shortcuts:**
  - These are fill jobs, not `research run`, so there is no evidence-store record.
  - The library was prebuilt once, and its SASS was gated on its own dump, not rebuilt per die.
  - The E5M2 units are my addition to the coordinator's E4M3 and floor example (default taken: same cost, and a second registered model).
  - `mxf8_e4m3` and `f8_e4m3e5m2`, the two hypotheses, weren't run. They're a Fill candidates line.

### E4M3 cast-and-store with 64- and 128-bit shared stores: Measured, locked-2100

Run `r20260930-101643-6b20` (preserved; head 84b953ad; `result.json` validation passed). It ran on node 2, **GPU-0c776bca-b587-ee46-2218-f72d8f5f435a (index 5, bus F4:00.0)**, with the UUID checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88.
- The parent built the library and ran the SASS gate without a GPU. `gpu-lease 1 --wait --max-min 10` then held the GPU **14.1 s** of a 16.8 s run, for identity, the numeric gate and timing. The timed launches were 9 ops × 10 reps × 63 ms = 5.7 s of that.
- **Gates, all before timing:**
  - Identity: name, SM count (188), driver and UUID.
  - The SASS gate pins every loop body exactly (the table below). There are no MOVs and no spills, and no `.FTZ` anywhere in the library.
  - The numeric gate compares each loop's staged words with `fp8.cvt_ref` through `w1.cs_model`. The wide loops stage the 32-bit packed form's words, so they share its models. Every op had 0 mismatches on 188 of 188 SMs, and none was vacuous.
  - One block per SM.
- **Clocks:** every rep's clock, as cycles over event time, was 2,093.9–2,099.2 MHz. The three nvidia-smi samples (before round 0, after rounds 4 and 9) read 2,092 MHz with no clock-event reasons.
- **Spread over the 10 reps:** 0.61% for the FADD-fed 128-bit loop, 0.36% for the input-free one, and under 0.015% for the rest.
- **The 32-bit packed loops reproduce `r20260930-094910-ddbc` on this second die:** 16.0000 and 17.5686, against 15.99998 and 17.56864.

Every loop carries the 3 uniform loop instructions, a warp iteration makes 2,048 codes, and the price per code is half the SM-clocks per warp iteration.

| loop (row stride) | SASS per iteration | codes per SM per clock | SM-clocks per warp iteration | W1 price per code |
|---|---|---|---|---|
| **`STS.64`, 160 B**, no per-code input | `F2FP` ×32, `STS.64` ×8, `IADD3` ×2 | 117.45 | 17.44 | **8.72** |
| `STS.64`, 160 B, one FADD per code | `F2FP` ×32, `STS.64` ×8, `FADD` ×64 | 62.26 | 32.90 | 16.45 |
| **`STS.128`, 192 B**, no per-code input | `F2FP` ×32, `STS.128` ×4, `IADD3` ×2 | 116.97 | 17.51 | **8.75** |
| `STS.128`, 192 B, one FADD per code | `F2FP` ×32, `STS.128` ×4, `FADD` ×64 | 66.94 | 30.59 | 15.30 |
| `STS.64`, **144 B** (form_s5's), no per-code input | as above | 64.00 | 32.00 | 16.00 |
| `STS.128`, **144 B**, no per-code input | as above | 64.00 | 32.00 | 16.00 |
| `STS` (32-bit), 144 B, no per-code input (reproduced) | `F2FP` ×32, `STS` ×16, `IADD3` ×2 | 64.00 | 32.00 | 16.00 |
| `STS` (32-bit), 144 B, one FADD per code (reproduced) | `F2FP` ×32, `STS` ×16, `FADD` ×64 | 58.28 | 35.14 | 17.57 |

**What it settles:**
- **Wide stores reach GPU 1's target: 8.72 per code with `STS.64`, and 8.75 with `STS.128`** (Measured). Both are under 11.7, and both need the row stride below.
  - Plugged into the coordinator's linearization (v1 chain-only 0.959% + 0.0111 points per unit above 8), both give **about 0.967%**, under 1%. That figure is Derived from the linearization; the real γ is the theory lane's to compute.
- **The loops are bound by the casts now, not the stores** (Derived).
  - 32 F2FP and 2 IADD3 at 0.5 SM-clocks each come to 17 SM-clocks. The loops measure 17.44 and 17.51.
  - What's left above 8.0 per code is the loop's 2 IADD3s and 2.6% model error. F2FP alone is 8.0 per code (the 08:40Z split).
- **The store rule, Derived from the six input-free store loops so far (the port's, the 32-bit packed one and the four above):** a warp store costs the larger of 2.00 SM-clocks per instruction and 1.00 SM-clock per 128-byte wavefront. So shared memory takes 128 B per SM clock, and at most one warp store issues every 2 SM-clocks.
  - `STS.U16` and `STS.32` are one wavefront each: 2.00.
  - Conflict-free, `STS.64` is two wavefronts (2.00), and `STS.128` four (4.00). Here each loop's 16 SM-clocks of stores hide under its 17 of ALU work.
  - With the 2-way conflicts of 144-byte rows, `STS.64` is four wavefronts and `STS.128` eight: 4.00 and 8.00 SM-clocks. That is exactly the 32.00 measured for both.
- **The row stride matters as much as the width** (Measured at 144; the bank analysis is Derived).
  - A 64-bit store is served per half-warp: rows g = 0..3 of 16 lanes. So a row stride ≡ 32 (mod 128) bytes, such as 160, puts the four rows' 32-byte chunks on disjoint banks.
  - A 128-bit store is served per quarter-warp: rows g, g + 1. So a stride ≡ 64 (mod 128), such as 192, keeps it conflict-free.
  - At 144 (≡ 16), both widths conflict 2-way, and the price falls back to the 32-bit form's 16.00.
  - An XOR swizzle of the 16-byte chunks would work instead of padding, but I haven't measured one.
  - form_s5's epilogue reads a row's 128 bytes per 8 threads with `LDS.128`, which is conflict-free at any stride that is a multiple of 16.
- **The FADD feed now adds about its own cost** (Measured). Fed by one FADD per code, the wide loops cost 16.45 and 15.30. That is 7.73 and 6.54 above the input-free loops, against FADD's own 8.00 per register.
  - Once the stores stop binding, the casts and the feed share the loop's time. 64 FADD + 32 F2FP take 30.6–32.9 SM-clocks per iteration, near 16 + 16 = 32. So FADD and F2FP overlap little (Derived; hypothesis: they share a datapath).
  - The fed loops still cost no more than the input-free price plus FADD's own 8.00: 16.45 against 16.72, and 15.30 against 16.75. So pricing the cast-and-store at 8.72 and the per-code FP32 op separately at 8.00 or 8.38, as the γ calculation does, doesn't undercount.

**The layout each width needs** (Derived from form_s5's fragment layout at 952e3ecc. Lane (g, q) holds columns 8nb + 2q + j, for j = 0, 1, of rows g and g + 8 in atom nb. I didn't run form_s5 with these stores):

| store | codes per store | a store holds | physical byte → logical column | row stride |
|---|---|---|---|---|
| `STS.U16` (form_s5 now) | 2 | one atom's pair | byte c = column c (row-major) | any; 144 is conflict-free |
| `STS.32` | 4 | a row's pairs from 2 atoms | within each 16: 4q + 2i + j → 8i + 2q + j (i < 2) | 144 is conflict-free |
| **`STS.64`** | 8 | a row's pairs from 4 atoms | **within each aligned 32: 8q + 2i + j → 8i + 2q + j (i < 4)**, a 4 × 4 transpose of column pairs, its own inverse | **≡ 32 mod 128, e.g. 160** |
| `STS.128` | 16 | a row's pairs from 8 atoms | within each aligned 64: 16q + 2i + j → 8i + 2q + j (i < 8) | ≡ 64 mod 128, e.g. 192 |

- **The consumer is the main GEMM,** which reads Ã (`at`) and B̃ (`bt`) along K. form_s5 writes both through `form_side`, so both carry the same order, and so does every 128-column tile, which starts on a multiple of 128.
- **`STS.64` keeps each k32 group's 32 columns inside the same aligned 32 bytes.**
  - The GEMM reads the bytes contiguously as now, and each k32 atom sums the same 32 products.
  - The registered step (`GroupSum`: every product aligned to the group maximum, then summed exactly) doesn't depend on the order within a group. So C̃ is bit-identical to the row-major layout's (Derived from the model).
  - The condition is the one at 10:16Z: F_B's lines, and anything else that reads Ã or B̃ by logical column, apply the same order. That includes the twin's sampled tiles.
- **`STS.128` crosses k32 groups.** Physical bytes 0–31 of each 64 hold the logical columns ≡ 0–3 (mod 8) from both 32-column halves.
  - Either the GEMM's two atoms read their 32 logical columns as 8-byte chunks at a 16-byte stride (atom 0 the first 8 bytes of each 16, atom 1 the second), or the statement's K order becomes this permutation.
  - The second option changes which products each atom groups, and hence C̃'s bits.
- **My recommendation (reversible, and GPU 1's call): `STS.64` at a 160-byte row.** It costs the same as `STS.128` (8.72 against 8.75), needs no change to the GEMM's loads, and keeps every k32 group intact. sO grows from 9,216 to 10,240 bytes.
- **In form_s5 itself** (Derived, from the store rule): 64-bit stores take its stores from 8 `STS.U16` (16 SM-clocks) to 2 `STS.64` (4) per iteration of 4 QMMAs (16). Its 8 `LDS.64` (2 wavefronts each, so 16 by the same rule) and 8 `LDG.E` stay. So the loads, not the stores, would then be what bounds it against the QMMAs. That is Conjectured for the `LDG.E`, whose cost I didn't measure. The fused cast of 10:16Z removes the stores altogether.

**Flagged shortcuts:**
- The wide loops' words are the 32-bit packed form's. Their store widths, addresses and row strides are form_s5's with the new strides, but the codes in them come from my loop's values, not from form_s5's atoms. The layout table is Derived, not run.
- The FADD feed stands in for form_s5's FMUL.
- The stores are `asm volatile` `st.shared.v2/v4.b32` with a memory clobber.
- The bank-conflict counts follow the half-warp and quarter-warp service rule. The 144-byte loops' exact 2× (32.00 against 16 of stores) agrees with it, but no profiler counted wavefronts.
- One die and one seed. No model is registered for a rate, so there is no discrepancy to confirm.

### E4M3 cast-and-store: `pearl_c_sm120.cu`'s loop and the packed form: Measured, locked-2100

Run `r20260930-094910-ddbc` (preserved; head e41832fb; `result.json` validation passed). It ran on node 2, **GPU-1cd543c7-ad34-75a8-ebfe-863061d1954a (index 2)**, with the UUID checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88.
- The parent built the library and ran the SASS gate without a GPU. It then took `gpu-lease 1 --wait --max-min 10` for identity, the numeric gate and timing only. The lease held the GPU for 58.0 s of a 60.7 s run (why so long: Lessons).
- **Gates, all before timing:**
  - Identity: name, SM count (188), driver and UUID.
  - The SASS gate pins every watched opcode of each loop body to an exact count (the table below).
  - The numeric gate checks every op's words exactly. For the cast-and-store loops, these are the words each loop staged in shared memory, against `fp8.cvt_ref` applied to the model's FP32 values (`w1.cs_model`). Every op had 0 mismatches on 188 of 188 SMs, and none was vacuous.
  - One block per SM.
- nvidia-smi read 2,092 MHz on every rep, with no clock-event reasons. Cycles over event time gave 2,091–2,094 MHz. There were 10 interleaved reps per op. The new loops' spread was under 0.01%, and the packing cast's 0.13% (it was 0.25% at 06:33Z).
- The reference ops reproduce the 06:33Z runs to five significant figures on this die: the unit at 1,023.98, FADD at 122.257 (8.376) and the E4M3 packing cast at 83.167 (12.312).

**What was timed:**
- **The port** is GPU 1's `form_s5` at 952e3ecc (built with `-O3 -fmad=false`). Each code is one scalar `__nv_cvt_float_to_fp8(…, __NV_SATFINITE, __NV_E4M3)`, which is one `F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C` with RZ as its partner. A `LOP3` and an `IMAD` join two codes into a 16-bit word, and one `STS.U16` stores it.
- **The packed form** converts two live floats per `cvt.rn.satfinite.e4m3x2.f32` and stores four codes per 32-bit `STS`.
- **Each form runs twice:** once fed by one FADD per code (a live FP32 chain, standing in for the port's FMUL), and once with no per-code input (the casts read loop constants, and two `IADD3`s change a live register per iteration).

Each loop also carries the 3 uniform loop instructions (`UIADD3`, `UISETP`, `BRA.U`). A warp iteration makes 2,048 codes, so the price per code is half the SM-clocks per warp iteration.

| loop | SASS per iteration | codes per SM per clock | SM-clocks per warp iteration | W1 price per code |
|---|---|---|---|---|
| **the port**, no per-code input | `F2FP` ×64, `LOP3` ×32, `IMAD` ×32, `STS.U16` ×32, `IADD3` ×2 | 31.94 | 64.12 | **32.06** |
| the port, one FADD per code | the same with `FADD` ×64 in place of the `IADD3`s | 29.13 | 70.29 | 35.15 |
| **the packed form**, no per-code input | `F2FP` ×32, `STS` ×16, `IADD3` ×2 | 64.00 | 32.00 | **16.00** |
| the packed form, one FADD per code | `F2FP` ×32, `STS` ×16, `FADD` ×64 | 58.28 | 35.14 | 17.57 |

**What it settles:**
- **The port's loop costs 32.06 W1 per code** (Measured), at the top of bc-3006c44a's Derived 28–32. Fed by a live FP32 value per code, it costs 35.15. The port feeds its casts with FMULs, so the FADD-fed arm is its closer stand-in.
- **The stores bind, not the casts** (Derived).
  - Both input-free loops run at exactly 2.00 SM-clocks per warp store: 64.12 / 32 = 2.004 for `STS.U16`, and 32.000 / 16 = 2.000 for the 32-bit `STS`.
  - A warp store costs the same whether it writes 64 B or 128 B. So the limit is per instruction, at 0.5 warp stores per SM per clock. The addresses are free of bank conflicts: rows are 144 B apart, and lane (g, q) writes bank 4g + q, or the halves of 4g + q/2.
  - The port's half-rate ALU work (64 F2FP, 32 LOP3 and 2 IADD3, at 0.5 SM-clocks each) comes to 49 SM-clocks, or 24.5 per code. It hides under the stores' 64.
- **The packed form costs 16.00 per code, not 12.31** (Measured). 12.31 is the cast packed into registers with no store (the `f2fp_e4m3x2` row). With its stores, the packed form is store-bound too: 16 stores at 2.00 is 32 SM-clocks, against 17 of ALU work.
- **So GPU 1's switch to the packed form halves the price:** 32.06 → 16.00 per code, or 35.15 → 17.57 with the feed.
- **The feed isn't additive.** It adds 3.09 per code to the port and 1.57 to the packed form, well under FADD's own 8.00 per register, because it issues in the store-bound loop's slack. A price that adds the feed's full cost to the cast-and-store's overcounts.
- **Conjectured, not measured: wider stores might take the packed form to about 8.5.**
  - `STS.U16` and `STS.32` cost the same per instruction. If `STS.64` or `STS.128` do too, the packed form's 16 stores become 8 or 4.
  - The loop would then be ALU-bound at 34 half-rate instructions, 17 SM-clocks, which is about 8.5 per code.
  - That needs each thread to hold 8 or 16 codes of one row in consecutive bytes, a layout change beyond the packed form's.
  - One W1 run would price it (Fill candidates).
- **form_s5 itself (Derived from its SASS and this run; I didn't time it).**
  - Its inner loop holds 4 `QMMA.16832`, 16 `FMUL`, 16 `F2FP`, 8 `LOP3`, 8 `IMAD`, 8 `STS.U16`, 8 `LDS.64` and 8 `LDG.E` per iteration.
  - At 2.00 each, the 8 stores alone take 16 SM-clocks, the same as the 4 QMMAs (4.0 each at the unit rate).
  - If the `LDS.64` and `LDG.E` share the stores' path at a similar cost, the loop is bound by memory instructions, not by the tensor pipe. That is Conjectured; I didn't measure either instruction's rate.
  - The packed form halves the stores to 4 `STS` (8 SM-clocks). Timing form_s5 itself would settle both points.
- **FTZ (server.md 09:34Z):**
  - No kernel here uses FTZ. The SASS gate pins `FADD` exactly, and a `FADD.FTZ` body fails it (`test_sass_gate_pins_the_cast_store_loop`).
  - The library is built with `-O2`, with no `-ftz=true` and no fast-math.
  - form_s5's SASS at 952e3ecc also has no `.FTZ`: its FP32 arithmetic is 16 `FMUL`.

**Flagged shortcuts:**
- **The input-free port arm feeds each convert a live register as its other half and keeps the low byte, where the port has RZ.**
  - With RZ, the convert of a loop constant would be loop-invariant.
  - The SASS gate pins the port's counts (64 `F2FP`, 32 `LOP3`, 32 `IMAD`, 32 `STS.U16`), so only the partner register differs.
  - The FADD-fed arm uses the port's own scalar call, with RZ.
- **The packed form's layout.**
  - Four codes per 32-bit word from one thread means a word holds a column pair from each of two adjacent n8 atoms: columns 2q, 2q+1, 8+2q and 9+2q of each 16.
  - That is a fixed permutation of the port's row layout within each 16 columns.
  - My kernel only picks the registers. In form_s5, the consumer must read the permuted order, or the permutation goes into the statement. That is GPU 1's and theory's call.
- **The FADD feed stands in for the port's FMUL.** FADD and FFMA issue at the same rate here; FMUL's rate I didn't measure.
- **The stores are `volatile`,** so ptxas keeps every one. The port's stores aren't volatile, but they are its staged output, so they stay too. The SASS is plain `STS` / `STS.U16` either way.
- One die and one seed. No model is registered for a rate, so there is no discrepancy to confirm.

### 2:4-sparse E4M3 `mma.sp::ordered_metadata` m16n8k64 against dense k32 atoms: Measured, locked-2100

Run `r20260930-092239-f0d0` (preserved; head 12017ae3; `result.json` validation passed). It ran on node 2, **GPU-0c776bca-b587-ee46-2218-f72d8f5f435a (index 5)**, with the UUID checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88.

**The run's shape** (one recorded run):
- The parent builds both libraries and runs both SASS gates without a GPU.
- It then takes `gpu-lease 1 --wait --max-min 15` for the GPU phase only: identity, three layout gates, the captures, then W1 timing.
- The lease held the GPU for 27.6 s: 10.4 s capture, about 15 s W1.
- The CPU verification (20.1 s, 32 workers) ran after the lease was released. The wall time was 51.1 s.

**Gates, all before timing:**
- **SASS** (Measured, static): `mma.sp::ordered_metadata…m16n8k64.row.col.kind::f8f6f4.f32.e4m3.e4m3.f32` lowers to **`QMMA.SP.16864.F32.E4M3.E4M3`**, and the dense atom to `QMMA.16832.F32.E4M3.E4M3`. The W1 loop holds 16 `QMMA.SP`, 15 NOPs and the 3 uniform loop instructions.
- **Identity:** name, SM count (188), driver and UUID.
- **Operand layout gate:**
  - It tries 12 candidate layouts: 2 B-register maps × 3 metadata maps × 2 index orders. Exactly one must reproduce the device's words.
  - The one that did is the PTX ISA's layout: B register r, byte j is k = 4q + j + 16r, at column lane/4. Lane 4g + q holds row g + 8(q&1)'s metadata for groups 8(q>>1) + c, at bits 4c. A nibble is (i1 << 2) | i0, and stored column 2c is i0's element. The selector is 0.
  - Each of the other 11 missed at least 8,135 words.
  - The dense atom's and the chain twin's own layout gates passed too, so both twins read their operands correctly.
- **W1's numeric gate:** exact words on 188 of 188 SMs, 0 mismatches.

**Q1: what does the sparse instruction write?**
- **Workload:** 66 variants (each family shared, per row, and from +0), seed 20260930. That is 4,371,968 elements, 4,359,488 of them gated: 1,657,472 from +0 accumulators and 2,702,016 from the families' nonzero accumulators. The families are the usual E4M3 step families plus the specials.
- **The only fit is `(64,) w26 f-133`:** 0 mismatches on every gated word, from +0 and from nonzero accumulators. Zero products carry no bits, so this is exactly the registered dense `BLACKWELL_SM120_E4M3_M16N8K32` step, `(32,) w26 f-133`, applied to the 32 stored products.
- **A hardware twin agrees:** the dense `QMMA.16832` atom, on the stored A and the metadata-gathered B, matches the sparse word on every gated element, bit for bit.
- **Two chained dense k32 atoms on the logical halves (hardware twin `chain2`) differ on 269,444 gated words.** 112,205 of them are from +0 accumulators and 157,239 from nonzero ones; 130,038 are shared-operand variants and 139,406 per-row. The chained model `(32,32) w26 f-133` gives the same 269,444, and both twin checks pass: the chain twin equals the chained model, and the dense twin equals the registered model.
- **The other candidates, refuted** (mismatches in gated words):

| candidate | mismatches |
|---|---|
| `(64,) w26 f-133` (one align-add over the 64-deep span) | **0** |
| `(64,) w26 f-123` | 21,150 |
| `(64,) w27 f-133` | 133,450 |
| `(64,) w28 f-133` | 180,119 |
| `(64,) w25 f-133` | 252,420 |
| `(32,32) w26 f-133` (two chained k32 steps) | 269,444 |
| `(32,32) w27 f-133` | 341,714 |
| `(32,32) w25 f-133` | 343,074 |
| `(16,16,16,16) w26 f-133` | 472,544 |
| `(8,)x8 w26 f-133` | 590,412 |

- **Hypothesis, no registry entry:** `tc-model/sm120-e4m3-sp-k64` is the registered dense sm_120 E4M3 step applied to the 32 stored products: one align-add, 26 bits, floor −133.
- **Unselected B entries don't reach the word** (Measured on 496 elements). 496 record-only elements differ between the device and every model: 196 in `specials.per_row` and 300 in `specials.per_row.zero_acc`. In every one of them, a NaN in B sits only at logical columns the metadata doesn't select. The device writes a finite word, the one the dense twin gives on the gathered B. Every model and the chain twin propagate that NaN (0x7fffffff), because they multiply the logical zeros. That the sparse word depends only on the stored A, the selected B and C is Derived from this and the 0-mismatch fit.

**Q2: the rate (W1 at locked-2100).**
- nvidia-smi read the SM clock at 2,092 MHz (2,100 on one rep per op), with no clock-event reasons. Cycles over event time gave 2,095.3–2,098.4 MHz. There were 10 reps per op, with a spread < 0.00003%.
- **The unit:** `qmma_e4m3_f32` ran at 1,023.98 MAC per SM per clock. This reproduces the 06:33Z runs on a third die.
- **The sparse op:** `qmma_sp_e4m3` ran at **2,047.96 logical MAC per SM per clock**.
  - That is **0.5000006 W1 per logical MAC**, or **1.0000012 W1 per nonzero product**.
  - Per instruction, sparse runs at 0.9999988 of the dense rate. A k64 sparse instruction issues as fast as a k32 dense one.
- **What that means for Pearl-C** (Derived): 2:4-sparse registered weights run the FP8 chain at 2× the logical MAC rate. Each sparse step replays bit for bit as one dense step on the compressed operands, so a verifier can check it against the registered dense model. Whether and how the credit counts sparse MACs is a statement parameter, so that goes through the coordinator.

**Flagged shortcuts:**
- Only the shared variants keep a family's designed products. There, one metadata word serves every row, and the family's k32 B sits at the selected columns of random finite filler.
- In a per-row variant, each row draws its own metadata over a logical B that is the family's k32 B followed by the previous tile's. The rows then select different products, so a family's structure (cancellation, spread) is only partly kept. The second half of B is reused rather than drawn fresh.
- The operand layout was selected by the gate rather than assumed. Only the PTX ISA's layout passed.
- The chained reference is a hardware twin, the dense k32 kernel run twice on the logical halves, not only the model. It agreed with the model on every element.
- This is one die and one seed, with no fresh-seed confirmation. None was needed: there is no discrepancy against a registered model.

### W1 prices on sm_120: Measured, locked-2100

Runs `r20260930-063213-c94a` and `r20260930-063827-e4c6` (both preserved; the second adds the zero-extended cast loop, and every rate the two share agrees to five significant figures): node 2, **GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f** (index 0, bus DB:00.0), driver 580.173.02, built with CUDA 13.0. Every gate passed before timing: identity, the SASS loop gate, the numeric gate (exact words on all 188 blocks for every op, none vacuous) and one block per SM. On every rep, nvidia-smi read the SM clock at 2,092 MHz and memory at 12,481 MHz, with no clock-event reasons; cycles over event time gave 2,095–2,098 MHz. All 188 of 188 SMs ran, with one 512-thread block each. There were 10 reps of about 63 ms per op. The rep-to-rep spread is < 0.03%, except the cast at 0.25%.

**The unit** is one dense E4M3 `mma.sync` MAC with f32 accumulation: 1 / (1,023.98 MAC per SM per clock). A price is the unit's rate over the op's rate, in the op's own unit.

| op (PTX) | SASS in the loop | rate per SM per clock | W1 price |
|---|---|---|---|
| **dense FP8 E4M3, f32 acc.** (`mma…m16n8k32…kind::f8f6f4.f32.e4m3.e4m3.f32`) | `QMMA.16832.F32.E4M3.E4M3` ×16 | 1,023.98 MAC | **1** per MAC (the unit) |
| dense FP8 E4M3, f16 acc. | `QMMA.16832.F16.E4M3.E4M3` ×16 | 1,023.98 MAC | 1.000 per MAC |
| mxf8f6f4 E4M3, 1X ue8m0 scales | `QMMA.SF.16832.F32.E4M3.E4M3.E8` ×16 | 1,023.43 MAC | 1.0005 per MAC |
| dense NVFP4 (`mxf4nvf4` 4X ue4m3) | `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X` ×16 | 2,046.85 MAC | 0.500 per MAC |
| **BF16 MMA**, f32 acc. (m16n8k16) | `HMMA.16816.F32.BF16` ×16 | 511.99 MAC | **2.000** per MAC |
| FP16 MMA, f16 acc. | `HMMA.16816.F16` ×16 | 511.99 MAC | 2.000 per MAC |
| **FP32 FADD** (`add.rn.f32`) | `FADD` ×64 | 122.26 lanes | **8.376** per register |
| **FP32 FFMA** (`fma.rn.f32`) | `FFMA` ×64 | 122.24 lanes | **8.377** per register |
| **E4M3 cast** (`cvt.rn.satfinite.e4m3x2.f32`), four codes packed per word | `F2FP.SATFINITE.E4M3.F32.PACK_AB_MERGE_C` ×64, `PRMT` ×16, `IADD3` ×18 | 83.17 codes | **12.31** per code (24.62 per instruction) |
| E4M3 cast, each result zero-extended | `F2FP…PACK_AB_MERGE_C` ×64, `LOP3` ×64, `IADD3` ×34 | 48.87 codes | 20.95 per code |

(Each MMA loop also holds 15 NOPs, and every loop 3 uniform-datapath loop instructions: `UIADD3`, `UISETP`, `BRA.U`.)

The E2M1 cast's three loops (`r20260930-083408-d164`) have their own section below: 9.27 per code packed, 20.95 zero-extended, 7.9–8.2 for F2FP alone.

**What the table settles:**
- **FP8 with f32 accumulation runs at full rate on this SKU** (f16/f32 = 1.000). GeForce Blackwell halves it. My earlier "Conjectured yes" is now Measured.
- **The MMA ratios** are exact: BF16 2, NVFP4 0.5, mxf8 1.

**Derived from the table and the loop compositions** (for the theory lane; flagged, not measured directly):
- **FADD alone is 8.00 per register, FFMA 8.00.** The loop is 64 FADD plus 3 loop instructions. At one warp instruction per SM sub-partition per clock, the issue limit is 128 × 64/67 = 122.27 lanes per SM per clock; the measurement is 122.26. So FADD is issue-bound at 128 lanes per SM per clock, and the 8.376 includes the 4.5% loop overhead.
- **The cast alone is 7.7–8.0 per code.**
  - The two cast loops differ only in their integer support: 34 or 98 instructions (PRMT/IADD3/LOP3) per 64 F2FP.
  - A linear fit of the loop time to the counts gives 0.483 SM-clocks per F2FP warp instruction and 0.540 per support instruction.
  - Hence F2FP alone runs at 132.5 codes per SM per clock, 7.7 per code. The simpler model, all of them sharing one half-rate pipe of 64 lanes per SM per clock, gives 8.0 (16 per instruction). That model predicts the two loops within 0.5% and 3.4%.
  - A model where F2FP overlaps its integer neighbours predicts 128 and 83.6 codes per SM per clock, against 83.2 and 48.9 measured, so it is refuted.
  - **So the cast contends with every integer instruction in its loop,** at about half an SM-clock per warp instruction. A quantizer that spends one PRMT per four-code word costs 12.0 per code on the shared-pipe model. ptxas packed half the words here with MERGE_C and no PRMT.
- **Against the Estimated planning numbers** (06:08Z, Public rates): FADD was about 8, and is 8.38 Measured or 8.00 alone. The cast was 8–16, and is 12.31 Measured in the packing loop or 7.7–8.0 alone. H100's W1 is 32 for FADD and 32 for the cast.

### W1 prices on all eight dies: fill outputs, not recorded runs, locked-2100

**These are fill outputs, not recorded runs.** The coordinator ran `w1.py` at e41832fb on each of node 2's eight dies as fill jobs: a prebuilt `libw1_prices_sm_120a.so`, `--reps 10`, seed 20260930, and e41832fb's 20 ops (everything in the W1 table, the E2M1 and `f32x2` loops, the sparse step, and the four cast-and-store loops before the wide stores). The outputs are node 2's `/workspace/pouw/fill-out/w1-dies/die0..die7/w1_results.json`. They have no run id, so nothing is in the evidence store and no label can point at them.
- **Every die passed every gate before timing:** identity (the UUID checked against `GPU_LEASE_UUID`), the SASS loop gate on the prebuilt library's SASS, and the numeric gate (exact words on all 188 blocks, none vacuous). Every die's `validation` reads `passed`.
- e41832fb samples nvidia-smi after every rep: 200 samples per die.

| die (index) | UUID | bus | clock from cycles, per rep (MHz) | nvidia-smi | wall (s) |
|---|---|---|---|---|---|
| 0 | GPU-5f1149a4 | DB:00.0 | 2,095.3–2,099.2 | 2,092; no event reasons | 61.7 |
| 1 | GPU-fb680060 | E0:00.0 | 2,096.8–2,099.0 | 2,092; none | 39.0 |
| 2 | GPU-1cd543c7 | E5:00.0 | 2,090.7–2,099.0 | 2,092; **one sample of 200 reads `0x4`** (SW power cap) | 61.0 |
| 3 | GPU-9f1f172d | EA:00.0 | 2,092.7–2,099.1 | 2,092; none | 60.9 |
| 4 | GPU-4352a609 | EF:00.0 | 2,096.2–2,099.3 | **2,100 on 8 samples of 200**, else 2,092; none | 61.0 |
| 5 | GPU-0c776bca | F4:00.0 | 2,082.8–2,099.3 | 2,092; none | 47.9 |
| 6 | GPU-2b59d5fe | F9:00.0 | 2,089.9–2,099.3 | 2,092; none | 39.8 |
| 7 | GPU-af0bf9e0 | FE:00.0 | 2,089.2–2,099.2 | 2,092; none | 36.7 |

**The die-to-die spread of every W1 price.** Each die's price is Measured. The spread is Derived: (max − min) / min of the eight per-die median rates, per SM per clock. The price spreads are the same, because the unit's rate is 1,023.9831 on every die, to 0.1 ppm. The last column is the widest max-over-min rep range on any single die. The per-instruction prices have the same spreads as the per-code ones, so they're left out.

| op | price per | min | max | die spread | widest one-die rep range |
|---|---|---|---|---|---|
| dense E4M3, f32 acc. (the unit) | MAC | 1.0000 | 1.0000 | 0.1 ppm | 0.3 ppm |
| dense E4M3, f16 acc. | MAC | 1.0000 | 1.0000 | 0.1 ppm | 0.4 ppm |
| mxf8f6f4 E4M3, ue8m0 scales | MAC | 1.0005 | 1.0005 | 0.4 ppm | 0.8 ppm |
| dense NVFP4 | MAC | 0.5003 | 0.5003 | 0.4 ppm | 0.2 ppm |
| BF16 MMA, f32 acc. | MAC | 2.0000 | 2.0000 | 0.1 ppm | 0.4 ppm |
| FP16 MMA, f16 acc. | MAC | 2.0000 | 2.0000 | 0.1 ppm | 0.3 ppm |
| FP32 FADD | register | 8.3757 | 8.3757 | 0.2 ppm | 0.6 ppm |
| FP32 FFMA | register | 8.3765 | 8.3765 | 0.4 ppm | 1.9 ppm |
| **E4M3 cast, packed** | code | 12.297 | 12.301 | **323 ppm** | 2,532 ppm |
| E4M3 cast, zero-extended | code | 20.953 | 20.953 | 8.2 ppm | 4.3 ppm |
| `add.rn.f32x2` | word | 8.6256 | 8.6256 | 0.1 ppm | 0.4 ppm |
| the same adds as plain C pairs | word | 8.1876 | 8.1876 | 0.2 ppm | 0.3 ppm |
| E2M1 cast, packed | code | 9.2719 | 9.2724 | 57.8 ppm | 15.9 ppm |
| E2M1 cast, zero-extended | code | 20.953 | 20.953 | 7.4 ppm | 3.8 ppm |
| E2M1 cast, packed, with 32 constants | code | 9.2656 | 9.2656 | 0.3 ppm | 1.4 ppm |
| 2:4-sparse E4M3 | logical MAC | 0.5000 | 0.5000 | 0.1 ppm | 1.4 ppm |
| cast-and-store, the port, FADD-fed | code | 35.147 | 35.148 | 14.6 ppm | 39.0 ppm |
| cast-and-store, the port, no per-code input | code | 32.061 | 32.062 | 11.2 ppm | 21.0 ppm |
| cast-and-store, packed, FADD-fed | code | 17.568 | 17.568 | 6.8 ppm | 15.2 ppm |
| cast-and-store, packed, no per-code input | code | 16.000 | 16.000 | 0.1 ppm | 0.5 ppm |

**What it settles:**
- **No W1 price differs across the eight dies by more than 0.033%.** Every die spread but the E4M3 cast's is under 60 ppm (0.006%). So one die's prices stand for all eight, and every price in the sections above, each measured on one die, holds on node 2 as a whole.
- **The E4M3 cast's 323 ppm is one SM-clock of loop period, not a die difference** (Derived).
  - Its rep rates fall on three levels: 83.17, 83.27 and 83.38 codes per SM per clock.
  - These are 65,536 codes per SM per iteration (16 warps × 64 F2FP × 2 codes × 32 lanes) over 788, 787 and 786 SM-clocks.
  - Seven dies' medians sit on 787. Die 5's (83.246) falls between 787 and 788, with 5 reps at 787 and 4 at 788.
  - All five of my recorded runs that timed it had their medians on 788, which gives the 12.31 in the W1 table (six of six with `r20260930-122749-94e1` on die 7 at 12:31Z, 7 reps on 788 and 3 on 787): die 0 at 06:33Z, 06:38Z and 08:34Z, die 1 at 08:01Z, and die 2 at 09:49Z. The fill runs on those three dies have their medians on 787 (12.297). So the level moves between runs on one die. Why the recorded runs all landed on 788 isn't known (flagged; each timed fewer ops than the fill's 20).
  - Read the packed E4M3 cast as **12.28–12.31 per code** (786–788 clocks), not 12.31 to four figures. It's the only op here whose rep spread is wider than 0.004%.
- **Four ops spread across dies by more than any one die's reps:** the NVFP4 MMA (0.4 against 0.2 ppm), both zero-extended casts (8.2 and 7.4 against 4.3 and 3.8 ppm) and the packed E2M1 cast (57.8 against 15.9 ppm). With one run per die, this can't tell a die difference from a run difference (flagged). All four are ≤ 58 ppm, which moves no price at the precision any γ uses.
- **The E2M1 three-loop split reproduces on every die:** F2FP alone fits 8.1969–8.1974 per code (59 ppm), and the uniform term fits −0.336 to −0.337 on all eight. So the 7.9–8.2 bracket is the model's error (the fits disagree), not measurement noise.
- **The clock doesn't enter any price.** Rates are per SM per clock, from in-kernel cycle counts. Die 2's one `0x4` sample came at 178.7 W, on rep 0 of the packed FADD-fed cast-and-store, and that rep read 2,096.0 MHz from cycles with a rate at the die's median. Die 4's 2,100 MHz readings came with 2,097–2,099 MHz from cycles. Neither moved a rate.
- **Flagged shortcuts:** one run per die; fill jobs, not `research run`, so there is no evidence-store record; the prebuilt library, checked by the SASS gate on its own dump and not rebuilt per die. The wall times (36.7–61.7 s) include e41832fb's nvidia-smi sample after every rep and bear on nothing here.

### The packed FP32 add `add.rn.f32x2`: Measured, locked-2100

Run `r20260930-080124-a89c` (preserved): GPU-fb680060-f371-db1a-73ba-8f2eef43674c (index 1), with the UUID checked against `GPU_LEASE_UUID`. Driver 580.173.02, CUDA 13.0.88, head 43d2ae0d. Every gate passed before timing: identity, the SASS loop gate, the numeric gate and one block per SM. For the packed add, the numeric gate adds 1 to the low word and 2 to the high, so a swapped half would show. All 188 SMs ran; nvidia-smi read 2,092 MHz with no clock-event reasons, and cycles over event time gave 2,095–2,099 MHz. There were 10 reps, with a spread < 0.001%. Every rate from the 06:33Z run reproduces to five significant figures (FADD 122.257, the cast 83.17), so the die makes no difference.

**Does it build, and what does it lower to?** Measured statically with CUDA 13.0.88, the same build as node 2's.
- `add.rn.f32x2` builds for sm_120a with no warning. **Each instruction lowers to two scalar `FADD`s.** The `__fadd2_rn` intrinsic does the same.
- **sm_120a has no packed FP32 unit.** `add.rn.ftz.f32x2`, `mul.rn.f32x2` and `fma.rn.f32x2` also lower to scalar pairs (`FADD.FTZ`, `FMUL`, `FFMA`). The same sources for sm_100a give `FADD2`, `FADD2.FTZ`, `FMUL2` and `FFMA2`, one per instruction.
- **ptxas pairs no scalar adds on its own,** on either architecture. Independent FP32 adds written as plain C, as `float2` members or as inline-PTX scalars stay one `FADD` each, even on sm_100a, which has `FADD2`. So an adversary gets no fused add for free.

| op | SASS in the loop | words per SM per clock | W1 price per result word |
|---|---|---|---|
| `add.rn.f32x2` (inline PTX, 8 packed chains) | `FADD` ×128 + 3 loop | 118.71 | **8.63** (17.25 per instruction, two words) |
| the same adds as plain C pairs (16 scalar chains) | `FADD` ×128 + 3 loop | 125.07 | **8.19** |
| `add.rn.f32` (the FADD row above, 8 chains) | `FADD` ×64 + 3 loop | 122.26 | 8.38 |
| **FADD alone** (Derived, from the two loops above it) | | 128.0 | **8.00** |

- **FADD is issue-bound at one warp instruction per SM sub-partition per clock.** The issue model predicts 128 × 128/131 = 125.07 and 128 × 64/67 = 122.27, and the measurements are 125.065 and 122.257. A two-point fit gives 0.24998 SM-clocks per `FADD` warp instruction: 128.0 words per SM per clock, 8.00 per word (Derived).
- **The packed form is 5.1% slower than the same adds as scalar pairs,** with the identical opcode mix (Measured). Its SASS pins each pair to an aligned 64-bit register pair, and ptxas marks no operand reuse on the addends, where the scalar pairs get `.reuse` on every addend. That this causes the 5.1% is Conjectured.
- **For the promotion add** (bc-b58c6093's open-price line): nothing on sm_120 adds FP32 at half of FADD's price. The cheapest FP32 add is scalar `FADD`: 8.00 per word alone, 8.19 in the 128-FADD loop, 8.38 in the 64-FADD loop. A rev1 credit at 8.38 is at most 4.5% above 8.00, not 2×. Which reading the proof charges is the theory lane's call.

### The E2M1 cast `cvt.rn.satfinite.e2m1x2.f32`, in the loop and alone: Measured, locked-2100

Run `r20260930-083408-d164` (preserved): GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f (index 0), with the UUID checked against `GPU_LEASE_UUID`. Head d71142be, CUDA 13.0.88, driver 580.173.02.
- Every gate passed before timing: identity, the SASS loop gate, and one block per SM (188 of 188).
- The numeric gate checks each loop's words against `w1.e2m1_ref`, on random per-lane operands that cover every E2M1 code, both signs and saturation: 0 mismatches. `e2m1_ref` is GPU 4's rule, bit-exact on 1,041,112 elements in `r20260930-072940-33b5`.
- Cycles over event time gave 2,096.5–2,097.1 MHz. There were 10 reps, with a spread of 0.24% on the packed loop and < 0.001% on the rest.
- Every other W1 rate reproduces the 08:01Z run to five significant figures (the unit 1,023.98, FADD 122.257, the E4M3 cast 83.17).

The three loops each carry 3 uniform-datapath or branch instructions per iteration, besides what the table lists:

| loop | SASS per iteration | codes per SM per clock | W1 price per code |
|---|---|---|---|
| packed: four converts per word, as a quantizer feeds the MMA operand | `F2FP.SATFINITE.E2M1` ×64, `IADD3` ×10 | 110.44 | **9.27** (18.54 per instruction, two codes) |
| packed, with 32 constants | `F2FP` ×128, `IADD3` ×18 | 110.51 | 9.27 |
| zero-extended (`cvt.u32.u8`) | `F2FP` ×64, `LOP3` ×64, `IADD3` ×34 | 48.87 | 20.95 |
| **F2FP alone** (Derived, below) | | 125–129 | **7.9–8.2** (8.0 on the shared pipe) |

- **Packing four E2M1 codes into a word costs nothing on sm_120a** (Measured, from the SASS). ptxas chains each word's four converts through F2FP's MERGE_C operand, so the packed loop is F2FP plus the fold's `IADD3`s. The E4M3 packing loop needs one `PRMT` per two words (16 per 64 F2FP) and costs 12.31.
- **F2FP costs the same for E2M1 as for E4M3** (Measured). The zero-extended E2M1 loop and the E4M3 u16 loop have the same opcode mix, and both run at 48.8711 codes per SM per clock, to six significant figures.
- **F2FP alone.** Each fit solves the loops' SM-clocks per warp per iteration for per-instruction costs:
  - Packed against zero-extended, leaving the uniform instructions out (the method of the E4M3 fit): 0.497 SM-clocks per F2FP and 0.531 per support instruction, so **7.94** per code.
  - 32 constants against zero-extended: 0.505 and 0.525, so **8.08**.
  - All three loops solved exactly, with a term per uniform instruction (`w1.split`; `split.e2m1.*` in `result.json`): 0.512, 0.531 and **−0.34**, so **8.20**. A negative cost is unphysical: the loops aren't exactly additive. So the spread of the fits, 7.94–8.20, is the model error.
  - The two packed loops alone give nothing: their support ratios (10/64 and 18/128) nearly coincide, so the pair is ill-conditioned.
  - **The shared half-rate pipe** puts F2FP and every integer support instruction at 0.5 SM-clocks (64 lanes per SM per clock), with uniform instructions free. It predicts the packed loop within 0.24%: its 74 pipe instructions run at 0.5012 each, which gives 8.02 per code. It predicts the 32-constant loop within 1.5%, the zero-extended loop within 3.4%, and the E4M3 packing loop within 0.5%.
- **Against GPU 4's 15.99 in the loop:** their loop chains each convert through a `LOP3`, a flagged shortcut, and the pipe charges that at F2FP's own price. The honest packed loop costs 9.27 per code. F2FP alone is 7.9–8.2, so their Derived "≈ 8.0 alone" stands, now bracketed by measurements.
- **Does it move a price?** No panel row.
  - The credit already charges the cast's F2FP alone at 8.0 FP8 MACs per element (`theory-pearl-c4-domain.md`'s credit table: 32.8 NVF4 MACs with the FMUL). That is inside 7.9–8.2, and the bracket moves f_s ≈ 98 NVF4 MACs by −0.1 to +0.4.
  - An older document would move: `theory-pearl-c-sm120.md` prices Pearl-C4's E2M1 cvt at the E4M3 cast's 8.0–12.31 ("which isn't measured"). The E2M1 packing loop is 9.27, so the top of that range drops from 12.31 to 9.27. Whether to re-run the γ calculator is the theory lane's call, through the coordinator.

### FP8 rows on silicon: Measured (node 2, gates first; each row its own run)

| row | run | GPU | primary model | mismatches (gated elements) | nearest alternative refuted |
|---|---|---|---|---|---|
| **mixed FP8 → BF16 chain** (one accumulator: `QMMA` e4m3 then `HMMA` bf16; families qb, qb_zero_acc, bq, g4 (40 steps), random (64 steps)) | `r20260930-064802-9eba` | GPU-5f1149a4 (0) | `sm120_e4m3+hopper_bf16` | **0** (225,280), free run never diverges | `sm120_e4m3+ampere_bf16` 32,139; `ada_e4m3+hopper_bf16` 135,599 |
| **floor-aimed E4M3 accumulators** (`step f8_e4m3`, families acc_floor, subnormal_isolated, wide_spread) | `r20260930-071136-c37b` | GPU-5f1149a4 (0) | `BLACKWELL_SM120_E4M3_M16N8K32` | **0** (98,304) | 7/7; nearest `(16,16) w26 f-133` 1,978, `(32,) w26 f-123` 2,888 |
| **mxf8f6f4 E4M3, 1X ue8m0** (`step mxf8_e4m3`, 20 families incl. scale_sweep, scale_floor, scale_nan) | `r20260930-071735-c9c8` | GPU-1cd543c7 (2) | HYPOTHESIS `(32,) w26 f-133`, products pre-scaled by 2^(sfa+sfb−254) | **0** (1,521,208 gated of 1,551,744; the rest record-only non-finite) | 12/12; floor −129 186, −128 622, −126 2,133, −124 5,774; post-scaled 71,286; w27 55,808 |
| **E4M3 × E5M2** (`step f8_e4m3e5m2`, 7 families) | `r20260930-071826-892a` | GPU-1cd543c7 (2) | HYPOTHESIS `(32,) w26 f-133`, e4m3 × e5m2 products | **0** (2,195,456) | 7/7; nearest `(32,) w26 f-123` 2,848 |
| **dependent E4M3 chains** (`chain --steps 2048 --chain-tiles 16`: K = 65,536; families gauss, gauss_acc, pos, unit, absorb, spikes) | `r20260930-071917-0e98` | GPU-1cd543c7 (2) | `BLACKWELL_SM120_E4M3_M16N8K32`, every step replayed from the device's previous word | **0** (25,165,824), free run never diverges | 2/2; `hopper_e4m3_k32` 21,035,250, `ada_e4m3_m16n8k32` 21,035,470 |
| **E4M3 / E5M2 cast** (`cvt`: `cvt.rn.satfinite.e4m3x2.f32`, `.e5m2x2.f32`; grid + random words) | `r20260930-072304-5f06` | GPU-af0bf9e0 (7) | `cvt_ref` (the H100-measured cast `verity.ml.tc.cast`, and its E5M2 analogue) | **0** (16,711,838 gated of 16,777,216; NaN inputs record-only, also 0) | none registered; NaN output byte is 0x7f for both formats |
| **FP32 add** (`fadd`: `add.rn.f32`, `add.rn.ftz.f32`; random, near-cancellation, subnormal, ties, overflow, specials) | `r20260930-072333-7084` | GPU-af0bf9e0 (7) | `rn` on `FADD`, `rn_ftz` on `FADD.FTZ` | **0** each (7,848,344 gated of 7,864,712) | each kernel refutes the other's model by 551,243 (subnormal 483,711, near 63,600, ties 3,166); canonical NaN 0x7fffffff |

**The vLLM lane's families, replayed with seed 20261001** (`tools/tc_probe/tc_probe.py --sweep --n-random 25000 --sass-check`, their capture's shape: 13 asserted families plus the non-finite specials, which are recorded and never asserted). Both ran on **GPU-4352a609-f69f-8929-3a1b-c85bdfea9753 (index 4)** per `gpu-lease`'s line, with validation passed:

| instruction | run | model | mismatches (asserted elements) | hypotheses refuted |
|---|---|---|---|---|
| `sm120.mma.m16n8k32.e4m3` | `r20260930-073559-5abe` | `BLACKWELL_SM120_E4M3_M16N8K32` | **0** (6,434,816) | Ada (16,16)/14: 4,907,478; 2×HMMA BF16 + FADD: 762,865 |
| `sm120.mma.m16n8k32.e5m2` | `r20260930-073650-c9c5` | `blackwell_sm120_e5m2_m16n8k32` | **0** (6,434,816) | Ada + e5m2 products: 4,086,500; 2×HMMA BF16 + FADD: 765,099 |

Both runs' `result.json` records GPU-5f1149a4 (index 0) as the device; that is `tc_probe`'s identity bug (Needs 2), not where they ran. The fp8_floor_probe family agrees in both.

**What the step rows settle (Measured, one die each, seed 20260930):**
- **No discrepancy against `BLACKWELL_SM120_E4M3_M16N8K32`.** The floor-aimed families agree on die 0, as the vLLM lane's families did on theirs.
- **mxf8 block scaling applies to the products before the 26-bit sum.** The post-scaled datapath is refuted (71,286 mismatches).
- **The mxf8 floor is ≤ −130.** Floors −129 to −124 are refuted, and floor −133 agrees. The fake-silicon grid had predicted 54, 122, 423 and 1,179 mismatches for these floors at n = 256; the device gives 186, 622, 2,133 and 5,774 at 16× the sample. As derived at 06:08Z, no finite test separates floors ≤ −130 here.
- **E4M3 × E5M2 is the same datapath as E4M3 × E4M3:** one group of 32, 26 bits, floor −133.
- These two are hypotheses with no registered model. Registering them is the vLLM lane's call, not mine.
- **The registered step composes over 2,048 dependent steps (K = 2^16) with no drift**, in all six chain families, on a second die. The mixed FP8 → BF16 chain composes the same way. So a proof may replay a long FP8 chain step by step against the one-step model.
- **The cast and FP32 add are exactly the references the proofs use**, on die 7: the E4M3 cast is the H100-measured one, and `FADD` / `FADD.FTZ` are RN binary32 with and without flush-to-zero.
- Dies: the rows ran on indices 0, 2 and 7, and the replays on 4. Each row's UUID is read from the CUDA device itself and matches `gpu-lease`'s stderr line. No row or replay disagrees with its model on any die.

### SASS (Measured, static)

nvcc 12.9.86 offline and CUDA 13.0 on node 2 give identical gated loops. Store runs: `r20260930-060217-6c89` and `r20260930-060227-9825` (12.9), and `r20260930-062059-dc4d` and `r20260930-063114-195d` (13.0, the current cast loop).
- The `kind::f8f6f4` e4m3 and the legacy `mma…f32.e4m3.e4m3.f32` lower to the same `QMMA.16832.F32.E4M3.E4M3`, with the same encoding. So the vLLM lane's capture covers the `kind::f8f6f4` form.
- e4m3×e5m2 lowers to `QMMA.16832.F32.E4M3.E5M2`, and mxf8f6f4 1X ue8m0 to `QMMA.SF.16832.F32.E4M3.E4M3.E8`.
- The mixed chain holds one `QMMA` and one `HMMA.16816.F32.BF16`, on one accumulator.
- **Flagged shortcut:** with warp-uniform operands, ptxas moves the cast onto the uniform datapath (`UF2FP`). The benchmarks feed each lane its own operands, and the SASS gate rejects any U-form.

### Derived facts about the floor (from the model and the grid)

- With unscaled FP8, the floor is unobservable at any value ≤ −124: the grid's least significant bit is 2^(floor−25), and no product is below 2^−32. This agrees with the vLLM lane.
- With mxf8 block scales, scaled products reach the floor. The fake-silicon grid then separates floors −129, −128, −126 and −124 from −133 (54, 122, 423 and 1,179 mismatches at n = 256), and separates the post-scaled datapath (9,919). Floors ≤ −130 cannot be told apart: 32 terms sum to at most 2^(f−20).

### Chain predictions, Derived

Fake silicon: the registered model stands in for the device; 512 chains per family, seed 20260930; `art:b75c090b7aea8659ec392a7594583eaf5e6eea2c75af91729c15301d1a3f8228`. Each cell is the fraction of exact steps in the doubling window ending at K, then the fraction of frozen steps.

| family | K=32 | K=1024 | K=8192 | K=65536 | rel. error vs exact at 2^16 (median / max) |
|---|---|---|---|---|---|
| chain_gauss | 0.998 / 0 | 0.982 / 0 | 0.964 / 0 | 0.913 / 0 | 1.9e-8 / 2.2e-7 |
| chain_gauss_acc | 0.242 / 0.002 | 0.740 / 0.002 | 0.732 / 0.002 | 0.701 / 0.002 | 3.8e-8 / 8.4e-5 |
| chain_pos | 0.025 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1.8e-4 / 1.9e-4 |
| chain_unit | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 0 |
| chain_absorb | 0.506 / 0.494 | 0.506 / 0.494 | 0.256 / 0.744 | 0.256 / 0.744 | 9.1e-4 / 9.8e-4 |
| chain_spikes | 0.980 / 0 | 0.804 / 0 | 0.637 / 0 | 0.438 / 0 | 3.1e-7 / 1.8e-6 |

**Measured on silicon** (`r20260930-071917-0e98`, GPU-1cd543c7, 16 tiles × 128 = 2,048 chains per family, seed 20260930), the same cells from the device's own words:

| family | K=32 | K=1024 | K=8192 | K=65536 | rel. error vs exact at 2^16 (median / max) |
|---|---|---|---|---|---|
| chain_gauss | 0.999 / 0 | 0.980 / 0 | 0.964 / 0 | 0.915 / 0 | 1.8e-8 / 3.1e-7 |
| chain_gauss_acc | 0.258 / 0.001 | 0.694 / 0.002 | 0.688 / 0.002 | 0.658 / 0.002 | 4.9e-8 / 9.2e-5 |
| chain_pos | 0.026 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1.8e-4 / 1.9e-4 |
| chain_unit | 1 / 0 | 1 / 0 | 1 / 0 | 1 / 0 | 0 |
| chain_absorb | 0.498 / 0.502 | 0.498 / 0.502 | 0.251 / 0.749 | 0.251 / 0.749 | 9.8e-4 / 9.8e-4 |
| chain_spikes | 0.974 / 0 | 0.795 / 0 | 0.637 / 0 | 0.408 / 0 | 3.9e-7 / 2.6e-6 |

The prediction holds within sampling (4× the chains here). Only chain_absorb freezes: from K = 8,192 on, 75% of its steps leave the accumulator unchanged, and the accumulator is unchanged since K/2 on the same 75%. A positive-drift chain (chain_pos) is never exact after K = 32 and ends 1.8e-4 from the exact sum.

## Node 2 run lines

On this VM I run `main`'s research CLI (the ssh provider, #478) from a local worktree of `origin/main` merged over my branch, and load my tools by their spec from the shipped tree. `R` is:

~~~sh
PYTHONPATH=<main worktree>/tools/research/src python -m research run --on vy-nebius-2 --project verity --campaign pouw --source . --cwd source --env GPU_LEASE_WHO=bc-e6a46970
~~~

With `U = uv run --frozen --no-dev --package verity-tc-probe-fp4 --`, the lines are:

~~~sh
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U gpu-lease 1 --wait --max-min 15 -- python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row step --instruction mxf8_e4m3   --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row step --instruction f8_e4m3e5m2 --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row step --instruction f8_e4m3 --families acc_floor,subnormal_isolated,wide_spread --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row chain --steps 2048 --chain-tiles 16 --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row mixed --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row cvt   --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U gpu-lease 1 --wait -- python tools/tc_probe_fp4/fp8.py --row fadd  --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U python tools/tc_probe_fp4/fp8.py --row sparse --lease-max-min 15 --out '$RESEARCH_RUN_DIR' --clocks locked-2100
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 10 --ops fadd,f2fp_e4m3x2,cs_port_fadd,cs_port_nogen,cs_packed_fadd,cs_packed_nogen
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 10 --smi-every 5 --ops cs_packed_fadd,cs_packed_nogen,cs_w64_fadd,cs_w64_nogen,cs_w128_fadd,cs_w128_nogen,cs_w64_nogen_r144,cs_w128_nogen_r144
$R --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8 -- $U python tools/tc_probe_fp4/fp8.py --row compile --out '$RESEARCH_RUN_DIR'
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 8 --lease-via-fill bc-e6a46970 --smi-every 5 --ops f2fp_f16_e4m3,f2fp_f16_e4m3_half,f2fp_f16_e4m3_xor,f2fp_e4m3x2
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 8 --lease-via-fill bc-e6a46970 --smi-every 5 --ops hmma_f16_f32,hmma_f16_f16,hmma_bf16_f32
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 8 --lease-via-fill bc-e6a46970 --smi-every 5 --ops hmma_f16_f32,hadd2,coissue_h4,coissue_h8,coissue_h12,coissue_h16,coissue_h24,coissue_h32,coissue_h48,coissue_h64,coissue_h80,coissue_h96,coissue_h112,coissue_h128,coissue_h160,coissue_h192,coissue_h256
$R --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 8 --lease-via-fill bc-e6a46970 --smi-every 5 --ops hmma_f16_f32,mix_r1_lb_flat,mix_r1_lb_br,mix_r2_lb_flat,mix_r2_lb_br,mix_r2_con_flat,mix_h0_f0,mix_h0_f17,mix_h32_f17,mix_h40_f17,mix_h48_f17,mix_h56_f17,mix_h64_f17,mix_h80_f17,mix_h96_f17,mix_h112_f17,mix_h128_f17,mix_h160_f17,mix_h192_f17,mix_h256_f17
$R --no-sampler --tool tools.tc_probe_fp4.tool_fp8:W1_PRICES  -- $U python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100 --lease-max-min 8 --lease-via-fill bc-e6a46970 --smi-every 5 --ops hmma_f16_f32,mix_h0_f0,mix_h0_f17,mix_h48_f17,mix_h0_f0_l7,mix_h0_f17_l7,mix_h48_f17_cf
~~~

The last five lines are `r20260930-122749-94e1`, `r20260930-151254-404a`, `r20260930-152940-ae57`, `r20260930-171330-eece` and `r20260930-181838-7460`. The last ran `R` from a worktree of `origin/cursor/nebius-server-da07`, whose CLI resolves `vy-nebius-2` from the notes clone's `machines.d/` after a VM reset. With `--lease-via-fill OWNER` (295bc0af), `w1.py` doesn't take `gpu-lease` itself: its GPU part becomes one fill job (`gpus=1 prio=10`, with `max_min` from `--lease-max-min`), and the run waits for it. It withdraws the job if it's still queued after 90 min.

The GPU check's gate (`r20260930-221543-8564`) is:

~~~sh
$R --no-sampler --tool tools.tc_probe_fp4.tool_fp8:TC_PROBE_FP8_GPUCHECK -- $U python tools/tc_probe_fp4/fp8_gpucheck.py --phase gate --out '$RESEARCH_RUN_DIR' --lease-via-fill bc-e6a46970-b6ef-5738-af64-182b143075d4 --workers 16
~~~

It builds, runs the SASS gate and the host-port check, and prepares the old captures on the CPU. It then leases through fill jobs (`fp8gc-<run>-<n>.sh`, re-leasing while the child exits 99) and compares on the CPU after the last lease.

The last line (`r20260930-105644-7738`, no GPU) shipped 9d5abb09 to `/workspace/research/src/9d5abb09…` and built the library the split fill jobs load with `--prebuilt`.

The sparse row takes its own lease (`gpu-lease 1 --wait --max-min 15`) around the GPU phase only, so it isn't wrapped in one. It builds and runs the SASS gates before the lease, and verifies on the CPU after releasing it. Since e41832fb, `w1.py --lease-max-min M` works the same way: it builds and runs the SASS gate, then takes `gpu-lease 1 --wait --max-min M` for identity, the numeric gate and timing. The unit op always runs, whatever `--ops` lists.

The replays use `U' = uv run --frozen --no-dev --package verity-tc-probe --` and a shell that appends the expanded `--out` (see Lessons):

~~~sh
$R --tool tc_probe -- $U' gpu-lease 1 --wait -- sh -c 'exec "$0" "$@" --out "$RESEARCH_RUN_DIR"' python tools/tc_probe/tc_probe.py --instruction sm120.mma.m16n8k32.e4m3 --seed 20261001 --sweep --n-random 25000 --sass-check
$R --tool tc_probe -- $U' gpu-lease 1 --wait -- sh -c 'exec "$0" "$@" --out "$RESEARCH_RUN_DIR"' python tools/tc_probe/tc_probe.py --instruction sm120.mma.m16n8k32.e5m2 --seed 20261001 --sweep --n-random 25000 --sass-check
~~~

`--sweep --n-random 25000` is the vLLM lane's capture shape: 13 finite families, 6,434,816 elements, plus the specials.

Since 43d2ae0d, the identity gate of `fp8.py` and `w1.py` checks the device's UUID against `gpu-lease`'s `GPU_LEASE_UUID` by default, as well as the name, the SM count and the driver. Runs before that recorded the UUID unchecked, and I matched each to `gpu-lease`'s stderr line. W1 is a one-GPU job, not a timed window: its rates are per SM per clock, and neighbours can only move the clock, which is recorded per rep.

## Lessons

- **A fresh agent VM has no `~/.research`.** For `research run --on vy-nebius-2`, write `~/.research/machines.toml` with `[machines.vy-nebius-2]`: `provider = "ssh"`, `host = "81.85.2.121"`, `user = "research"`, `project = "verity"`, `root = "/workspace/research"`. The CLI takes `RUNPOD_SSH_KEY_B64` and the `R2_*`/`AWS_*` secrets from the environment.
- **A branch stacked on an older base lacks the ssh provider.** Run `main`'s research from a worktree (on `PYTHONPATH`), and load the branch's tool by its spec (`--tool tools.tc_probe_fp4.tool_fp8:W1_PRICES`). The registry loads it by file from the shipped tree, so `main` needs no copy of the registration.
- **Node 2's system `python3` has no numpy.** Wrap the workload as `uv run --frozen --no-dev --package <member> -- gpu-lease 1 -- python …`: the venv syncs before the lease is taken, and the `python` inside the lease is the venv's.
- **`research run --timeout` would extend the machine's lease.** The CLI says so when it's absent ("lease was not extended: the run has no --timeout"). Node 2's terms say touch no lease, so I pass no `--timeout`. The infra lane may want the ssh provider to never extend a lease it doesn't own.
- **`nvidia-smi --query-gpu` fails as a whole on one unknown field.** An identity gate that reads the driver from the same query then sees no driver. `fp8.smi_query` retries field by field. `clocks_event_reasons.active` works on 580 (`clocks_throttle_reasons` is the deprecated name).
- **`gpu-lease 1` exits 75 without running anything while an 8-GPU request waits** (a timed window). Queue with `gpu-lease 1 --wait` instead: the one-GPU request then waits its turn behind the window.
- **`research run --on` over ssh reads stdin.** In a `while read` loop fed by a heredoc, give it `< /dev/null`, or it swallows the rest of the list.
- **A fake device that returns the expected words can't catch a layout bug.** Only the first silicon run can. The numeric gate caught a check-word stride error before any timing. A gate whose expected words are all zero now fails as vacuous: my cast gate had passed on zeros both ways.
- **CUDA 13.0's ptxas gives the same gated SASS** as 12.8/12.9 for these kernels. The default RunPod image's CUDA 12.4 can't build sm_120a (moot now).
- **With the same operands in every lane, ptxas moves the E4M3 cast onto the uniform datapath (`UF2FP`).** Each lane needs its own operands.
- **`research run --on` passes argv without a shell, so `'$RESEARCH_RUN_DIR'` arrives literally.** `fp8.py`, `w1.py` and `probe.py` expand it themselves; `tools/tc_probe/tc_probe.py` doesn't, and it built into a directory named `$RESEARCH_RUN_DIR`. Wrapping the whole command in one `sh -c '…'` string hides the flags from the tool's parser (the store would record the default seed). What works: `sh -c 'exec "$0" "$@" --out "$RESEARCH_RUN_DIR"' python tools/tc_probe/tc_probe.py --instruction … --seed …`. The parser still sees every flag, and only `--out` is expanded. An `expandvars` in `tc_probe.py` would remove the trap; it's the vLLM lane's file.
- **`tc_probe.py` without `--sweep` runs only its 8,192-element layout check,** prints "ALL HARDWARE WORDS REPRODUCED", and exits 0, with `validation: not_run` in `result.json`. My Phase A run lines left `--sweep` out, so `r20260930-073046-6792` (e4m3, GPU-af0bf9e0, index 7) and `r20260930-073115-4da4` (e5m2, GPU-5f1149a4, index 0) are layout checks, not replays. Read `validation` and the element count, not the banner.
- **A PTX instruction that builds for sm_120a need not have a unit there.** `add/mul/fma.rn.f32x2` build without a warning and lower to scalar pairs; only sm_100a has `FADD2`/`FMUL2`/`FFMA2`. Read the SASS before pricing a packed op. A local `cuda-nvcc-13-0` plus `cuda-cuobjdump-13-0` and `cuda-nvdisasm-13-0` from NVIDIA's apt repo answer this in seconds, with node 2's exact ptxas.
- **A two-loop split depends on how it counts the per-iteration overhead.** For E2M1, counting the 3 uniform instructions as support or not moves F2FP's alone price by about 6%. A third loop with a different cast count pins that term. When the term comes out negative (−0.34 here), the loops aren't additive: report the spread of the fits, not one solve.
- **`panel.py append` under the system `python3` has no matplotlib, so the plots aren't regenerated.** Re-run `panel.py render` with a Python that has it (the workspace venv does).
- **Split capture from verification so no lease holds a GPU idle.** The sparse row runs `gpu-lease` as a subprocess around the GPU phase only. It writes the raw words to the run directory and verifies them after the lease ends. The lease held the GPU 27.6 s of a 51.1 s run, and the 20.1 s CPU verification held none. Any queue wait falls before the GPU phase and holds no GPU; here it was under 2.4 s (the lease subprocess took 27.6 s, the GPU phase 25.2 s).
- **A 2:4-sparse layout has many plausible readings of the metadata,** so let the device pick one, not the docs. A layout gate with exact small integers, and B nonzero at the unselected columns, rules out every wrong candidate by thousands of words.
- **An agent VM can come back reset to `main`, with nothing installed.** Before the 09:49Z run I rebuilt everything: `cuda-nvcc-13-0` (with cuobjdump and nvdisasm), the venv (`uv sync --package verity-tc-probe-fp4` plus pytest), `~/.research/machines.toml` (the first lesson), and the `origin/main` worktree for the CLI. Nothing on the VM survives a reset, so keep this recipe here, not in a shell history.
- **W1 holds its lease about 8 s per op for 0.63 s of timed kernels.** The 09:49Z run held the GPU for 58.0 s, of which 7 ops × 10 reps × 63 ms = 4.4 s were timed. Most of the rest is probably the nvidia-smi sample after every rep (Conjectured; not profiled). Sampling once per op, or on a thread during the rep, would shorten the lease several-fold.
- **Never probe a `gpu-lease` lock to see whether a GPU is free.** At 11:01Z I ran `flock -n /run/gpu-lease/<i>.lock true` on node 2's eight locks. On each free GPU, that took the lock for an instant: I touched the leases, which node 2's terms forbid, though nothing waited or changed. The free count is in `/workspace/pouw/fill/status.txt`, and the holders in `/run/gpu-lease/<i>.owner`: read those.
- **A recursive search of the store mount is slow:** `rg` over it took 400 s. Search the repo, or read the one store file by path.
- **Fill jobs can chain without a watcher.** A CPU job that exits 99 while its input is missing would be requeued at once and spin. Instead, the GPU job queues its own CPU job once its outputs exist: it stages the script as a dotfile in `queue/`, which the runner skips, then renames it into place. Nothing on the agent's VM has to survive for the chain to finish.
- **A recorded run can use a fill slot and still get a run id.** `research run` does the build and the gates, `w1.py --lease-via-fill` queues the GPU part as a fill job, and the results come back into the run directory. Two traps in the runner:
  - It retries any exit but 0, 99, 75, 124 and 143 once, so a failed gate followed by a passing retry would read as a pass. The job script records the child's exit status in the run directory and exits 0; preemption still kills it and requeues it.
  - It moves a finished job into `done/` before it appends the event, so wait for the event.
- **Poison every buffer the transcript reads, and run a no-write negative control** (server.md 11:50Z, adopted at 295bc0af's parent 34774d0d). `w1_run` memsets chk, cycles and sm to 0xA5 before every launch, and its flag 1 launches nothing. The gate requires unwritten words to keep the poison and fails any op whose negative control it accepts. A stale buffer from an earlier launch would otherwise pass a kernel that never ran.
- **`add.rn.f16x2` is not a pure `HADD2` loop on sm_120a:** ptxas lowers half of the adds to `HFMA2` (x · 1 + y), as the assessor found. An addend of `{y.hi, y.hi}` (`mov.b32 {l, h}, y; mov.b32 t, {h, h}`) gives 64 pure `HADD2` with an `.H0_H0` operand, because `HFMA2`'s addend has no such swizzle. `cvt.f32.f16` is `HADD2.F32`, and `add.rn.f32.f16` is `FHADD`. `w1.py`'s `hadd2`, `add_f16x2`, `hfma2`, `hadd2_f32` and `fhadd` loops (73599997) pin all five.
- **Queue wait dominates a row's wall, not the GPU.** The mixed row's wall was 1,386 s for 4 s of GPU, and step_floor's 335 s for 4 s: both waited behind `gpu-lease 8` windows, and any GPU freed ahead of a window stays idle until the last one is free. A one-GPU job queued behind a window can't start early (the queue is FIFO). The chain row is the opposite: 212 s under the lease, almost all of it the host replaying 2,048 steps through four models while the GPU idles.

- **Pous's CPU fill is 4 slots on 32 cores (96–127), at nice 19.** The runner orders CPU jobs by `prio`, then by how many jobs their owner has running, then by the file's age, so an owner's newest CPU job runs after all of its older ones. Size a verification in CPU slot-hours, not only core-hours. A canary is quicker on the agent VM: a 141 MB launch file streamed over `research pods ssh` in 10 s.
- **A per-worker memory peak sets `mem_gb`.** The runner caps each CPU job with `MemoryMax`. The fill-verify worker peaked at 6.1 GB on a 261,193-tile launch, so 8 workers under 24 GB would have been killed.

## Fill jobs (third fill, the GPU check, queued 22:43Z on node 2)

The coordinator's 21:12Z row. The tree is 7aa3abf6, shipped by the gate run to `/workspace/research/src/7aa3abf6…`. The library is the one the gate built and passed (`fp8-gpucheck/build/`, with its sha256 checked before every chunk). The plans and jobs come from `fp8-gpucheck/jobs/mkjobs.py`, sized by the gate's timing.
- **`fp8gc-die<d>.sh`, d = 0–7** (`gpus=1 on=<d> max_min=8 cpus=4 prio=10 mem_gb=16`): five units per die, seed 20264000 + 100d + k, specs `primary` and `(32,) w25 f-133`, launches sized from the gate's timing (Estimated):
  - `e4m3` (k = 0): every family (11), 2 launches each of 1.07e9 tiles (24.5 s). 9 GPU-min.
  - `floor` (k = 1): E4M3 `g_acc_floor`, `g_acc_floor_cancel`, `g_subnormal_isolated` and `g_wide_spread`, 4 launches each of 1.14e9 (26.2 s). 7 GPU-min.
  - `e5m2` (k = 2): every family, 1 launch each of 1.66e9 (38.2 s). 7 GPU-min.
  - `mixed` (k = 3): E4M3 × E5M2 (`f8_e4m3e5m2`, a hypothesis with no registered model), every family, 1 launch each of 1.19e9 (27.3 s). 5 GPU-min. This is the `mixed` row, moved onto the GPU check.
  - `chain` (k = 4): the six chain families, 3 launches each of 42,112 chains × 32,768 steps (K = 2^20 per chain; 1.38e9 steps, 30.8 s), with every word of each launch's first chain recorded. 9.2 GPU-min.
  - Each launch writes `L_<family>_<i>.npz` whole, which is its checkpoint. Launch 0 of each family corrupts one word, the negative control. A chunk starts no launch after 330 s and exits 99, as it does on SIGTERM; a failed identity or SASS gate exits 1. Each finished unit queues its own CPU half.
- **`fp8gcver-die<d>-<unit>.sh`** (40 jobs, `gpus=0 max_min=30 cpus=4 mem_gb=48`): `fill-verify --workers 4` writes `V_<launch>.json` per launch, then `unit_verify.json`. It exits 99 with launches left, 0 on a pass and 1 on a failure. They had 8 workers and 24 GB until the first launch's re-check peaked at 6.1 GB; I changed them before any was queued.
- **Totals (Estimated from the gate's timing):** 4.96 GPU-h, 37.5 GPU-min per die. 7.8e11 tiles, or 1.0e14 words, with 1.67e8 tiles kept (2.1e10 words re-checked on the CPU). About 17 CPU core-hours (93 CPU-s per 1.07e9-tile launch, Measured on this VM), and about 105 GB.
- **The CPU half is the bottleneck.** Pous's CPU jobs share 4 slots on cores 96–127, and 28 were queued at 22:47Z, including the second fill's 14 verify jobs. With all 8 dies, the GPU half should take about 40 min of wall; the re-check will take hours more.
- Outputs are under node 2's `/workspace/pouw/fill-out/fp8-gpucheck/`: `die<d>/<unit>/`, `build/` and `jobs/`. They are fill outputs, not recorded runs.
- **Not moved:** the `cvt` and `fadd` rows. They are other instructions, and this kernel models only the QMMA step.

## Fill jobs (second fill, queued 18:35–18:45Z on node 2)

**Status at 22:47Z:** 107 of 128 step units and 6 of 31 chain units have passed their CPU verify (`fp8chainver-die0.sh` and `-die1.sh` exited 0, in 28.7 and 28.0 min). The other 14 verify jobs (`fp8ver2-die0`–`7`, which requeue with 99 after about 7 min each, and `fp8chainver-die2`–`7`) are queued behind other lanes' CPU jobs. The GPU check's gate already compared all 159 units' words with the CPU model (Results).


The coordinator's 18:30Z row (server.md 18:28Z) asked for about 5 GPU-h. Every job is `gpus=1 on=<d> max_min=8 prio=10` with the matching `gpus=0` verify job, in the 11:07Z design below.
- Each unit is one (row, die, seed), and its GPU-phase JSON is its checkpoint (written whole, then renamed).
- A job exits 99 after about 5 minutes with units left, and on SIGTERM, which it passes to its child first. It exits 1 on a failed gate.
- The GPU job queues its verify job once every unit is captured, so no verification runs in a lease.
- Outputs are on node 2 under `/workspace/pouw/fill-out/fp8-capture2/` and `fp8-chain/`, one directory per die and unit, with the job files in `jobs/`. They are fill outputs, not recorded runs.

**`fp8cap2-die<d>.sh`, d = 0–7** (tree 9d5abb09, the library of `r20260930-105644-7738`, `fp8.py` and `mma_fp8.cu` unchanged at bf77c948). There are 16 step units per die, with seed 20262000 + 100d + j:
- E4M3 every family at `--n-random 4096`, j = 0–7: 10.8 M elements per die, at or above 10^7 on every die.
- Floor-aimed (`acc_floor,subnormal_isolated,wide_spread`) at `--n-random 65536`, j = 8–11: 6.3 M per die, 4× the 11:07Z per-die sample.
- E5M2, j = 12 and 13; `mxf8_e4m3`, j = 14; and `f8_e4m3e5m2`, j = 15. These are the step rows of "every `fp8.py` row on each other die".
- **Done:** all 128 units passed their gates and were captured by 18:40:50Z. Each die held its GPU for 1.3–1.5 min (Measured, 11.8 GPU-min in all), and the device ran for 11.2 s of that. That's 180.5 M elements and 1.4 GB. The verify jobs `fp8ver2-die<d>.sh` (`max_min=20 cpus=4`) are queued, at about 8 min each (Estimated, 16 units × about 30 s).

**`fp8chain-die<d>.sh`, d = 0–7** (tree bf77c948, where the chain row splits, shipped by `r20260930-184046-4dfa`: compile and SASS gate passed). The chains have 16 tiles of every chain family:
- K = 2^16 (`--steps 2048`) at seed 20263000 + 100d.
- K = 2^18 (`--steps 8192`) at seed 20263001 + 100d.
- Dies 3, 4 and 5 started the first version, which splits K = 2^18 into one unit per family. Each such unit held the GPU for 45 s against 0.13 s on the device, because `chain_families` generates every family's operands before the filter applies. So I swapped the other five dies' queued files, each claimed atomically first, for one K = 2^18 unit.
- The K = 2^16 unit held 11.9 s (Measured). The lease is about 4.7 min per die on dies 3–5 and about 1.1 min on the others (Estimated), which is about 20 GPU-min.
- The verify jobs `fp8chainver-die<d>.sh` (`max_min=30 cpus=4`) replay every step through the three models and the free-running fold. They take about 17 min per die (Estimated from the 11:07Z chain row's 212 s at K = 2^16).

**Total: about 0.5 GPU-h of lease**, 11.8 GPU-min Measured plus about 20 Estimated. Of that, about 20 s is device work, and the rest is operand generation and file I/O on the host.
- These captures can't fill 5 GPU-h honestly: verifying a word on the CPU costs about 10^3 times what capturing it costs on the device.
- To fill 5 GPU-h, the check would itself have to run on the GPU: a CUDA port of the step model, with the CPU cross-checking a sample.
- Generating the operands in a `gpus=0` job first would cut these leases to the gates and the device.
- The `mixed`, `cvt` and `fadd` rows aren't queued, because they still verify inside the process that holds the GPU.

## Fill jobs (queued 11:02–11:03Z on node 2; all done by 11:28:48Z)

All 16 jobs started once and exited 0 (the runner's `events.jsonl`). Their results are in Results.

**The FP8 step, split into capture and verification** (server.md 09:56Z, 10:26Z). Code 9d5abb09: `fp8.py --row step --phase gpu` runs the identity gate (the lease's UUID), the SASS gate, the layout check and the capture, and writes `step_gpu.json` beside `tiles_<instruction>.npz`. `--phase verify`, with the same workload flags and no device, checks that capture on the CPU and writes `probe_results.json`. One seed gives the same operands, words and samples split or not: the split reproduced the one-process run word for word on three instructions, and a test pins it. `--prebuilt` loads the library that `r20260930-105644-7738` built and SASS-gated (`--row compile`: passed, CUDA 13.0.88). The job copies it with its sha256 and checks that before every chunk.
- **`fp8cap-die<d>.sh`**, d = 0–7: `gpus=1 on=<d> max_min=8 prio=10`. Four units per die, with seed 20261100 + 10d + j:
  - E4M3 at j = 0 and j = 1, every family, `--n-random 4096`: 1,355,136 elements each.
  - E5M2 at j = 2, the same shape.
  - The floor-aimed families `acc_floor,subnormal_isolated,wide_spread` at j = 5, `--n-random 65536`: 1,572,864 elements, 16× the Phase B row's sample.
  - A unit's `step_gpu.json` is its checkpoint. The job exits 99 after about 5 minutes with units left, exits 1 on a failed gate, and fails a unit that started 3 times.
  - Once every unit has passed its gates, it queues `fp8ver-die<d>.sh` into the queue itself: staged as a dotfile, which the runner ignores, then renamed.
  - Measured lease per die: 20–30 s, with nvidia-smi read once per unit by the identity gate.
- **`fp8ver-die<d>.sh`**: `gpus=0 max_min=20 cpus=4`. It verifies each unit, with `probe_results.json` as the checkpoint, and exits 99 after about 7 minutes. At the end it exits 1 if any unit failed. The runner then retries it once and moves it to `failed/`, which alerts: read that unit's `probe_results.json` first.
- **Outputs:** node 2's `/workspace/pouw/fill-out/fp8-capture/die<d>/<unit>/`, with the library in `build/` and the staged verify jobs in `jobs/`. Fill outputs, not recorded runs.
- **Total:** 8 dies × (3 × 1,355,136 + 1,572,864) = 45.1 M elements (Derived). This is 32.5 M from E4M3 and E5M2 every-family units and 12.6 M floor-aimed.

## Fill candidates

Every line is a one-GPU `gpu-lease 1 --wait` job on node 2 through `$R … -- $U gpu-lease 1 --wait -- …` (the run lines above). None holds state between runs, so each restarts cleanly from scratch; a preempted run is just rerun. GPU-hours are Measured leased time from this session's runs (the probe's own seconds; queue wait holds no GPU), scaled linearly where the size differs, which is Estimated.

| job | command (after `$U gpu-lease 1 --wait --`) | GPU-h | restarts cleanly | yields |
|---|---|---|---|---|
| ~~W1 on each other die~~ **done**: the coordinator ran it on all eight dies as fill at e41832fb (Results) | `python tools/tc_probe_fp4/w1.py --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100` | Measured 36.7–61.7 s wall per die with 20 ops | yes | die-to-die spread of every W1 price: ≤ 0.033% |
| every `fp8.py` row on each other die | the seven row lines above | 0.08 per die (Measured: 306 s for all seven) | yes (per row) | die-to-die agreement of every row |
| ~~E4M3 step, fresh seeds at scale~~ **queued** as split fill (Fill jobs above). This line said `--n-random 1000000`, which is wrong: `--n-random` counts tiles of the largest family, so 1e6 elements is `--n-random 4096` (1,355,136), and 1000000 would be about 331 M | | | | |
| ~~floor-aimed accumulators at larger samples~~ **queued** at `--n-random 65536` (Fill jobs above) | | | | |
| E4M3 and E5M2 steps, many more seeds (the split jobs above, more units per die) | `fp8cap-die<d>.sh` with more seeds in `units`/`flags` | 20–30 s leased per 4 units (Measured), almost all of it host work; generating operands in a `gpus=0` job first would cut the lease to the gates and the device | yes | tens of millions more elements per GPU-minute; verification 28–34 s per unit on node 2's fill CPUs (Measured), ≈ 10 s per 1.36 M elements on this VM |
| `mxf8_e4m3` and `f8_e4m3e5m2` steps (hypotheses, no registered model) through the same split | `--instruction mxf8_e4m3` / `f8_e4m3e5m2` | as above | yes | fresh-seed, multi-die support for the two hypotheses |
| longer FP8 chains (K = 2^18) | `python tools/tc_probe_fp4/fp8.py --row chain --steps 8192 --chain-tiles 16 --out '$RESEARCH_RUN_DIR'` | 0.24 (Estimated: 4 × the Measured 212 s at 2,048 steps; fits one 30-min lease) | yes | whether chain_spikes and chain_gauss_acc keep losing exact steps past 2^16, and 4× more steps checked |
| 2:4-sparse E4M3, fresh seeds and dies | `$U python tools/tc_probe_fp4/fp8.py --row sparse --lease-max-min 15 --seed <new> --n-random 16384 --out '$RESEARCH_RUN_DIR'` (takes its own lease; no outer `gpu-lease`) | 0.008 at the default 4,096 (Measured 27.6 s leased); ≈ 0.02 at 16,384 (Estimated) | yes | multi-seed, multi-die support for the `tc-model/sm120-e4m3-sp-k64` hypothesis; the GPU is free while the CPU verifies |
| E4M3 packed cast-and-store with `STS.64` / `STS.128` on the other seven dies (measured on die 5 at 10:16Z, Results) | `python tools/tc_probe_fp4/w1.py --lease-max-min 10 --smi-every 5 --ops cs_w64_fadd,cs_w64_nogen,cs_w128_fadd,cs_w128_nogen,cs_w64_nogen_r144,cs_w128_nogen_r144 --out '$RESEARCH_RUN_DIR' --reps 10 --clocks locked-2100` (takes its own lease; no outer `gpu-lease`) | 0.004 each (Measured 14.1 s leased at 9 ops) | yes | die-to-die spread of the wide-store prices |
| `LDS.64` and `LDG.E` rates beside `STS` (the same, two more ops) | as the line above | ≈ 0.01 (Estimated) | yes | whether form_s5 is bound by its memory instructions rather than its QMMAs |
| `tc_probe` replays, more seeds and dies | the replay line above with `--seed <new>` (and `.e5m2`); `--n-random 200000` for 8× the elements | 0.007 each (Measured 21–26 s at 25,000); ≈ 0.05 at 200,000 (Estimated) | yes | multi-seed, multi-die agreement with the vLLM lane's models |

(K = 32 × `--steps`: the 2,048-step row already reached K = 2^16, so the earlier `--steps 65536` line was wrong, at ≈ 1.9 GPU-h and too long for one lease.)

## Needs

1. **Theory (bc-3006c44a), via the coordinator:** the W1 table above, runs `r20260930-063213-c94a` and `r20260930-063827-e4c6`. For the chain-only γ:
   - FADD: 8.38 Measured, or 8.00 for FADD alone.
   - The cast: 12.31 per code Measured in a packing loop, or 7.7–8.0 per code for F2FP alone (Derived from the two cast loops).
   - The E2M1 cast: 9.27 per code Measured in its packing loop, or 7.9–8.2 for F2FP alone (Derived from three loops, `r20260930-083408-d164`). F2FP costs the same for both formats.

   Which reading the proof charges is the theory lane's call. I change no statement parameter.
2. **Coordinator → vLLM lane (bc-049fc756): `tc_probe`'s identity on a shared node.** `tools/tc_probe/tc_probe.py` `host_identity()` runs `nvidia-smi … -i 0`. NVML indices ignore `CUDA_VISIBLE_DEVICES`, so on node 2 every `tc_probe` result records physical GPU 0's UUID, whichever GPU `gpu-lease` gave the run. `fp8.identity_gate` avoids this by querying `--id=<the CUDA device's own UUID>`. It's their file, so I don't touch it. For my replays, the run's `stderr.log` keeps `gpu-lease`'s line naming the GPU it got, and I check the recorded UUID against it.
   - **Confirmed on node 2:** `r20260930-073559-5abe` and `r20260930-073650-c9c5` ran on GPU-4352a609 (index 4) and record GPU-5f1149a4 (index 0) in `result.json` and `tc_evidence`. The labels `tc_probe` prints for the store include `device GPU-5f1149a4…`, which would be false for both. I applied no labels.
   - Two small fixes in their file would help: `nvidia-smi --id=<the CUDA device's UUID>` (as `fp8.smi_query` does), and `os.path.expandvars` on `--out` (Lessons).
3. Nothing blocking. Phase B's list is done (07:37Z), `add.rn.f32x2` is priced (08:02Z), the E2M1 cast is split (08:40Z), the 2:4-sparse E4M3 step is captured and priced (09:28Z), and the E4M3 cast-and-store loops are priced (09:52Z), including with wide stores (10:20Z). W1 is priced on all eight dies (10:33Z), the FP8 steps are verified with fresh seeds on all eight (11:33Z), the FP16 convert is priced (12:35Z), and so is the FP16 leaf (15:16Z), the MMA / `HADD2` co-issue is measured (15:34Z), and so are the rewrite mix (17:19Z) and its copy-free follow-up (18:25Z). The second capture fill is queued (18:45Z, Fill jobs). The GPU check passed its gate, and its fill is queued (22:55Z). Next, if the coordinator wants more: any line under Fill candidates, or `cvt` and `fadd` ported onto the GPU check.
4. **The coordinator withdrew the `fp8-recheck` fill jobs** (e4m3 and e5m2 at seeds 20261005–6) at 08:30Z, because they held GPUs idle while verifying on the CPU. I didn't rerun them (default taken):
   - No discrepancy needs a fresh-seed confirmation, and the seed-20261001 replays passed on a second die.
   - `tc_probe` verifies inside the lease. Splitting capture from verification would be a change to the vLLM lane's file.
   - The seeds stay available as the replay line under Fill candidates.
5. **Coordinator → approved-weights lane (bc-8412d697):** the sparse result above, run `r20260930-092239-f0d0`. The `tc-model/sm120-e4m3-sp-k64` hypothesis is the dense step on the 32 stored products. It costs 0.5 W1 per logical MAC and 1.0 per nonzero product, so the rate is 2× per logical MAC. Registering a model is not my call; it has no registry entry.
6. **Coordinator → theory (bc-3006c44a) and GPU 1 (bc-18346d9c):** the cast-and-store prices above, run `r20260930-094910-ddbc`.
   - The port's loop is 32.06 W1 per code (35.15 fed by a live FP32 value per code). This replaces the Derived 28–32.
   - The packed form is 16.00 (17.57 fed). A packed-form γ computed at 12.31 per code should be recomputed at 16.00.
   - Both loops are store-bound, so wider stores (Conjectured about 8.5, unmeasured) or fewer store instructions would lower the price further. A cheaper cast would not.
   - Which reading the credit charges is the theory lane's call. I change no statement parameter.
7. **Coordinator → theory (bc-3006c44a): the FP16 convert on v1's post-add path,** run `r20260930-122749-94e1` (server.md 11:10Z).
   - `cvt.rn.f16x2.e4m3x2` costs **8.00 W1 per code** (16.00 per instruction), Measured and bit-exact against `decode_e4m3`.
   - Each LOP3 sharing its pipe adds 8 per code at one per convert (Derived).
   - The packed E4M3 cast's 786/787/788 spread moves 12.31 by −0.016 to −0.031 (−0.13% to −0.25%). 12.31 is the top.
   - I change no statement parameter.
8. **Coordinator → theory (bc-3006c44a): the leaf and `HADD2` for v1's pre-add term** (server.md 14:48Z, 15:02Z).
   - **The leaf:** FP16 `mma.sync m16n8k16` with FP32 accumulation costs **2.000 W1 per MAC** (Measured, run `r20260930-151254-404a`, 511.99 against E4M3 k32's 1,023.98 MACs per SM per clock). That is at or above 1.93. FP16 accumulation and BF16 cost the same. This is the issue rate of a steady loop, not whole-GEMM wall time.
   - **`HADD2`:** the coordinator cancelled my `HADD2` row at 15:02Z; the number to use is the assessor's (`assessor-hadd2`, 14:53Z): half rate, about 61 per SM per clock, `HFMA2` the same, and 7.9 W1 per written element. ptxas's `HADD2` + `HFMA2` split of `add.rn.f16x2` doesn't lift it to full rate. The co-issue run below also measured `HADD2` alone, as the table's reference, and it agrees: 63.999 per SM per clock, 16.00 W1 per register, 8.00 per element.
   - **For the time-only item in `concurrent-budgets/sm120`: the co-issue table** (Measured, run `r20260930-152940-ae57`, locked-2100, die 7; server.md 15:19Z).
     - The loop is the leaf's 16 `HMMA.16816.F32` (32,768 MACs per warp) with n `HADD2` per iteration.
     - "Alone" is the leaf's loop for the MMA (511.99 MACs per SM per clock) and `HADD2`'s own loop (64.00 registers per SM per clock).
     - The added W1 per `HADD2` register is Derived: (the loop's SM-clocks per warp iteration − 64.001) × 1,023.98 / (32n). `HADD2` costs 16.0 alone.

     | n | MMA MACs/SM/clk | MMA change | `HADD2` registers/SM/clk | `HADD2` fraction of alone | sum | SM-clocks per warp iteration | added W1 per `HADD2` register |
     |---|---|---|---|---|---|---|---|
     | 0 | 511.99 | 0 | 0 | 0 | 1.000 | 64.001 | – |
     | 4 | 510.00 | −0.39% | 1.99 | 0.031 | 1.027 | 64.251 | 2.00 |
     | 8 | 506.06 | −1.16% | 3.95 | 0.062 | 1.050 | 64.751 | 3.00 |
     | 12 | 508.02 | −0.78% | 5.95 | 0.093 | 1.085 | 64.501 | 1.33 |
     | 16 | 506.06 | −1.16% | 7.91 | 0.124 | 1.112 | 64.751 | 1.50 |
     | 24 | 502.18 | −1.92% | 11.77 | 0.184 | 1.165 | 65.251 | 1.67 |
     | 32 | 502.18 | −1.92% | 15.69 | 0.245 | 1.226 | 65.251 | 1.25 |
     | 48 | 508.02 | −0.78% | 23.81 | 0.372 | 1.364 | 64.501 | 0.33 |
     | 64 | 485.44 | **−5.19%** | 30.34 | 0.474 | 1.422 | 67.501 | 1.75 |
     | 80 | 481.87 | −5.88% | 37.65 | 0.588 | 1.529 | 68.001 | 1.60 |
     | 96 | 474.89 | −7.25% | 44.52 | 0.696 | 1.623 | 69.001 | 1.67 |
     | 112 | 466.16 | −8.95% | 50.99 | 0.797 | **1.707** | 70.293 | 1.80 |
     | 128 | 426.60 | **−16.68%** | 53.33 | 0.833 | 1.666 | 76.811 | 3.20 |
     | 160 | 364.60 | −28.79% | 56.97 | 0.890 | 1.602 | 89.875 | 5.17 |
     | 192 | 312.09 | −39.04% | 58.52 | 0.914 | 1.524 | 104.995 | 6.83 |
     | 256 | 239.08 | −53.30% | 59.77 | 0.934 | 1.401 | 137.061 | 9.13 |

   - **The reading:**
     - Up to n = 48 (one `HADD2` register per 21 MACs), the pre-adds hide beside the FP16 MMAs: the MMA rate loses under 2%.
     - From n = 64 to 112, the MMA loses 5–9%, and each register adds 1.6–1.8 W1, about a tenth of its alone cost.
     - The knee is n = 128, where both pipes' work is equal. Past it, `HADD2` binds.
     - The utilization sum peaks at 1.71. The assessor's 14:58Z line cites at most 1.45, which I haven't reconciled.
     - The operands are in registers, so a real pre-add's loads aren't counted. Results has the flagged shortcuts.
   - I change no statement parameter.
9. **Coordinator → theory (bc-3006c44a): the rewrite-mix probe** (`min-merge-search/rewrite-mix.md` with its 16:20Z amendment; server.md 16:12Z), run `r20260930-171330-eece`, Results above.
   - **The deciding point** (16 HMMA with 48 `HADD2`, 17 FADD, 7 `ldmatrix` and one STS/LDS pair, 2 warps per SMSP, 236 registers): **t_mix/t_solo = 1.142** (Derived from Measured rates, locked-2100). That's past 1.063, so by your reading no route saves anything: −7.5% to −9.2% of the block at Πρλ 0.941–0.956 (Derived).
   - **R2's 88-add point: 1.401** (LB-flat; 1.460 with 36 FADD). That's −31.4% and −30.5% of its block at λ = 2.000 and 1.986 (Derived).
   - The whole curve and the other routes are in the Results table. The MOV flag is the one that could move the deciding number; the other shortcuts are listed there too.
   - **The follow-up (the coordinator's 17:53Z row), run `r20260930-181838-7460`:** the deciding point with a copy-free form schedule (0 MOVs in the loop, against 101) runs at **t_mix/t_solo = 1.115** (Derived), above 1.055 and 1.063, so the MOV caveat is closed. The 7 `ldmatrix` per 16 HMMA alone cost nothing (1.000); beside h0_f17's FADDs they give 1.032, against its 1.034. The copies and the form chain were 2.7% (1.145 on this die). Results has the table and the flags; fresh forms are an optimistic floor.
   - I change no statement parameter.
