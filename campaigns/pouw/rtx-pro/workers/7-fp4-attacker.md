---
cursor:
  subagentId: "bc-dbc19788-573d-5ba4-b3b2-d6551c1c60ef"
---

# GPU 7 → GPU 4: FP4 attacker and quality (sm_120, RTX PRO 6000)

Worker bc-dbc19788. FP4 stream attacker + quality. **Rebalance (server.md 05:05Z): GPUs 6–7 → the red team; I work
CPU-side and take GPU index 4 after GPU 4's FP4 recheck.** No pod row tonight. Stand-in atoms until GPU 4's recheck:
`BLACKWELL_SM120_NVF4` / `_MXF4` (RTX 5090 pins), named in each result. Branch `cursor/fp4-attack-quality-60ef`
(https://github.com/danielreuter/verity/pull/new/cursor/fp4-attack-quality-60ef).

## Checkpoints

- 04:55Z started Phase A; store mounted; `server.md`: pending. VM: 4 cores, ~4 GB free RAM, no GPU.
- 05:05Z read the rebalance: I take GPU 4 after the recheck (not GPU 7); no pod. Continuing Phase A on CPU.
- 05:10Z census tool + quality harness written; synthetic census sweep and the 7B CPU quality run launched.
- 05:15Z committed the census/quality tools (`benchmarks/pouw/fp4_census.py`, `fp4_quality.py`, `fp4_redteam_tool.py`,
  tests); suite `benchmarks/pouw` green (15 tests).
- 05:18Z GPU 5's `fp4-design.md` (Pearl-C4 v0) is up. Applied the cheaper-computation route list to it.
- 05:20Z **cheaper-computation kernels built + SASS-gated offline** (nvcc/cuobjdump 12.9, sm_120a): dense/2:4-sparse/int8
  all pass.
  **2:4 sparse `mma.sp` kind::mxf4nvf4 is real SASS** (`OMMA.SF.SP.168128...`) — resolves GPU 4 recheck item 6.
- 05:22Z route list `fp4-cheaper-computation.md` written (this dir). Census sweep done (k up to 32,768 + narrow adder).
  7B quality run mid-flight (layer 13/28, CPU).
- 05:30Z real-operand census on real Qwen2.5-7B activations+weights (layers 0/1/3/7/13): **MXFP4 exact everywhere;
  NVFP4 freezes on early-layer massive-activation operands.** Attack list + status updated. Quality run at layer 22/28.
- 05:37Z 7B quality done: FP8 +1.26%, NVFP4 W4A4 +11.56%, MXFP4 W4A4 +36.97%, PoUW-NVFP4 +2.39% over plain NVFP4
  (Measured, CPU). Phase A complete pending GPU access; `server.md` still pending (no "node 2 is ours").
- 05:43Z read 05:25/05:35Z updates. Built the **base-split falsifier** (`fp4_census.py basesplit`, coordinator's ask):
  row-relative δ≥1/8 → cheater ties honest (1.000×); block-relative → cheater beats (0.75–0.99×). Renamed the report to
  `fp4-cheaper-computation.md` and reworded "attack"→"cheaper-computation search" per the 05:35Z wording rule. Working
  defaults from 05:25Z (Q1 forming credited; Q5 keeps B's noise) noted. Server still CPU-only.
- 05:57Z read 05:50Z relay (my findings routed to GPUs 3/4/5 + theory). **Finer δ sweep pins the floor:** at row-relative
  **δ=1/8 the base-split cheater is exactly 1.000× on all 11 families** (NVFP4 and MXFP4); δ=1/10 still leaks 1.9% on the
  outlier family, δ=1/16 leaks up to 43%. So 1/8 is the tight floor (the coordinator's relayed "≈1/6" is conservative,
  consistent). **Added the row-relative PoUW quality variants** `pouwrow_nvf4`/`pouwrow_mxf4` (the γ-secure deployable
  config, δ=1/4) to `fp4_quality.py` — the earlier PoUW-* quality below is the *insecure block-relative* stand-in; the
  deployable number is running on CPU (7B, ~2 h) and lands here when done. Committed `b4b9729f`, pushed. Server CPU-only.
- 07:00Z read 06:00–06:50Z: **node 2 is ours.** The coordinator ran my `peak` (prices Measured: 1.000/0.500/1.997) and
  GPU 4 confirmed the atoms and that 2:4-sparse words equal the dense ones, so every CPU census here is the real sm_120
  atom. **Answered theory §5's ask** (the salt-dead 4-group share, `774e321f`): median 0.44/0.49 on real Qwen, not the
  ~35% §5 assumed; hardware-exploitable share 0 (Results, Needs 1). Merged `main` for the node-2 ssh provider
  (`024ac7d6`, no overlap); SSH to node 2 works. Node contended (timed windows + 7 waiters), so the GPU quality run goes
  in as a **fill job** (below), not a lease that would wait behind the timed windows.
- 07:50Z read 07:05–07:15Z. **The GPU quality run was CPU-bound, as the 07:05Z note suspected:** every noise tensor was
  drawn with a CPU generator and copied over, and each layer built with a CPU random init (the coordinator's run:
  6% GPU utilisation, 410 s/layer; my first fill chunk: 86 s/layer at 32 windows, i.e. ~40 min, past the 25-min cap,
  then preempted by a timed window after 6.4 min). Fixed in `e3762dea`: noise drawn on the device, variants run one at
  a time with per-variant parts and a time budget (exit 99 = more chunks), CPU results bit-identical to before. The fill
  job is re-queued with it and now also dumps all 28 layers' operands. `fp4_census.py basesplit --acts` (`31c20126`)
  computes the real-operand salt-dead shares from the tool (reproduces 0.435/0.490 exactly). `fp4-cheaper-computation.md`
  now carries the Measured prices, the confirmed atoms and the salt-dead finding (§0.6, §3.1).
- 08:40Z **GPU quality run done** (fill job, 6.5 GPU-min over two chunks, GPU-1cd543c7, `art:59a6f733…`): Qwen2.5-7B on
  32×2048 windows (65,504 tokens). **The γ-secure PoUW output (row δ=1/4) costs +0.84% ± 0.27 perplexity over clean
  NVFP4**; clean NVFP4 W4A4 is +7.15% over BF16, MXFP4 +29.5% (Quality below). The local CPU run's two OOM kills were a
  leak, not the lm_head: each patched `forward` closure held its module, so finished layers lived until a full gc
  (fixed `d9412334`). ε_R census: the partner search took ~45 min per layer, so I bounded it to 64 k-blocks (87 s per
  layer, `d9412334`), withdrew my queued node-2 census job (a timed window plus 14 CPU jobs ahead of it) and run it on
  this VM's 4 cores against the 28 GPU-dumped layers (copied, hashes checked). Push works again.
- 09:55Z read 08:55–09:34Z. **Send early: v1's D-NF no longer makes the one-sided base split tie on stride rows**
  (09:22Z ask; Results, first item). The census now screens at 10ρ with the reference's whole row rule (D-NF + D-SS,
  `pearl_c4` at `5f0a1529`), has the spiky and stride families, and a second tool forms operands exactly as Pearl-C4
  does (`fp4_formed_census.py`, GPU 5's twin). ε_R and the zero fractions are in Results (09:30Z first ask). The
  10ρ debit census (both predicates, v1 and v2 words, 28 layers + families) and the exact-forming ε_R on real layers are
  running on this VM. Commits `2da2cd05`, `464722c0`, `78d7f041`, pushed.
- 10:50Z **The GPU ε_R job is done** (3 chunks, 10:29–10:43Z, 14 GPU-min, exit 0; `art:a4268def…`): it reproduces the
  CPU census over all 28 layers (NVFP4 activations 0.0091 median, MXFP4 0.070), with the partner search over 1,024
  k-blocks (Results). MXFP4's families at 10ρ: honest admitted tiles already sit at ρ (item 2), in §3.2 of
  `fp4-cheaper-computation.md`. acc-freeze replicated on a second seed in both formats (v2 7.2–7.8ρ). The row rule's
  debit census is preserved (`art:5e6a3bc2e31582cb605419b6276c0e73bc4ebdab9c84f0f743bb71472688a0cc`); the word rule is
  still running on this VM.
- 10:30Z read 09:38–10:07Z. **First GPU chunk queued (09:56Z ask):** `gpu7-fp4-merge-gpu.sh` (prio=10, ≤ 8-min chunks,
  exit 99), ε_R and the zero fraction per family (256 × 16,384, both operands) and on every linear of all 28 layers,
  with the stand-in forming in torch on the GPU and the partner search over up to 1,024 k-blocks (the CPU run: 64).
  Each chunk first gates the port bit for bit against the numpy census (`fp4_merge_gpu.py`, `ce5f8f18`; passed on node
  2's venv). Queued at 10:23Z behind a timed window. **The 10ρ debit census is written up** in
  `fp4-cheaper-computation.md` §3.2 (all 28 layers, row rule): admitted real tiles ≤ 25% of ρ, sub-grid 0, no formed 2:4
  span under either predicate. **The census's pair rule is the hardware's** (09:38Z: 67 / 121 / 57 of 256, as GPU 4
  counted). **New:** acc-freeze is admitted and costs 7–8ρ under v2 (Needs 0c); MXFP4 v2 at h = 14 floors nothing
  (Needs 0b). Exact-forming ε_R on real layers is in Results (`art:142daa4b…`). Word rule and MXFP4 families still
  running on this VM.
- 11:01Z read 10:40–11:02Z. **Applied bc-a8466279's two corrections to the stride-row finding** (Results, first
  item; Needs 0). An FP32 op now costs 16.92 FP4 MACs (the FFMA's 8.46 FP8 MACs × 2; `abfd19d7`), and NVFP4 is priced
  at the value level. NVFP4's tie holds: 1.84–2.00 two-sided, 0.92 one-sided at worst. MXFP4's stride-grid rows still
  cost 0.76 two-sided through the CUDA-core route, because UE8M0 scales don't move with the salt; Needs 0 asks whether
  their check covers MXFP4. Re-run: `art:92f3567a…`. The word rule's debit census finished at 11:09Z (`art:bc0bfa62…`, both rules): per-word H
  lets merged k128 reproduce 0.16 of whole chains against 0.002 per row, so v2-hot's per-row H is the better form
  (`fp4-cheaper-computation.md` §3.2; Needs 0c).

- 12:06Z read 10:32–11:22Z. **Re-censused at the √90 screen under the 10:35Z rule** (the 10:32Z ask, which I had
  missed; `d80dadc8`, `art:1abee109…`, `fp4-cheaper-computation.md` §3.3). Every real row passes D-NF, and 0.986 of
  real tiles stay within ρ with q/k/v as one GEMM, against 0.18 admitted under the old cap. At their own n = 512, K/V
  lose 60% of tiles to item 4 (Needs, GPU 5). acc-freeze and the 10ρ-edge stride rows are now rejected. **But
  stride-grid rows with ρ at amax/9.44 escape the screen, and on MXFP4 they still cost 0.94 two-sided** (`3c0b1b82`,
  `art:4767f842…`; Needs 0).
  *(12:40Z: that run's 0.815 / 60% used the retired item-4 rule; corrected numbers in the next line.)*
- 12:40Z read 12:13Z. **Re-censused the √90 screen with item 4 on the witness only (11:32Z rule;** `9afa0b99`,
  `art:8d6aff0f…`, `fp4-cheaper-computation.md` §3.3). 196 real cells, every row passes D-NF. Within ρ = 1/400: 0.987 of
  tiles at each linear's own n and 0.987 with q/k/v fused, K/V 1.000 either way. Within 1/1,000: 0.974 own n, 0.982
  fused, K/V 0.971 / 1.000. Honest debit on admitted tiles, median / mean: 0.059 / 0.134 of 1/400 at own n, 0.038 /
  0.100 fused. The misses are gate_proj L0–L2, mostly through item 3. Posted the stride-row and base-split-tie results under
  **For bc-a8466279** (below). No new construction on the current noise design until the fix lands.
- 13:40Z read 13:25Z. **Ran F1′ (`dnc2.py` unchanged) on the stride rows:** every stride family's tile is rejected
  (debit 0.8–2.9 per MAC), the controls carry none, and no family nets a gain (next section; `5b8b9989`,
  `art:fb8f7aac…`). `fp4_formed_census.py` now reads the current reference's admission (`490b1126`).
- 18:31Z read 18:26Z (the keyed-rotated NVFP4 census as ~5 GPU-h fill). **#580's enforced rule has no GPU evaluation:** it is
  `PearlC4.tile_cap` (exact, CPU; #580's `real.py` spends ~150 s a 64 × 64 tile at k = 8,192). A `gpus=1` job would hold
  the card idle, so this census goes in as `gpus=0` fill (CPU stages), with **0 GPU-h**; the GPU queue needs another
  candidate. A GPU job here needs a torch port of `tile_cap` gated bit-for-bit against it first (not started).
- 18:38Z **queued `fp4-kt-census-c138ca9d.sh`** on node 2 (`gpus=0 max_min=25 cpus=8 prio=10`): `benchmarks/pouw/fp4_kt_census.py`
  (`c138ca9d`) with #580's `real.py` unchanged (at `3f700c52`) on Qwen2.5-7B layers 0 / 14 / 27, all 7 linears, `none|pc`,
  `rotb8s|pc`, `rotb8s|al` × 15 activation families: admission per row and 2 seeded 64 × 64 tiles per linear through
  `tile_cap`. Checkpoints: one npz per (variant, family), then real.py's task JSONs. Estimated 25–40 CPU-h, 3–5 h wall,
  0 GPU-h (from local tile times: 3.9 s at k = 256, 5.9 s at k = 512, scaled). Shortcuts: W is 4 keyed 64-row blocks per
  linear, real.py's split stand-in, label-keyed noise. Cross-group sets and the transfer test aren't in it: they belong to
  the FP8 chain's accounting (`aw_advdebit.py`); Pearl-C4's tile items stand in for them here.
- 11:46 AM PDT ask (the torch port of #580's tile check), done. **`fp4_tile_gpu.py` matches #580's `tile_cap` bit for bit:
  0 mismatches over 18,072 tiles and 360 words** (15 census families plus planted screened, dead and reject tiles; CPU gate
  plus a GPU check on node 2; Measured; `art:2c8c2064…`). The Qwen2.5-7B census on it (`fp4_gpu_census.py`, `388eeb55`)
  already covers all 28 layers × 7 linears × 3 variants at 16 tiles per linear. Its GPU stage took 4.5 GPU-min (Measured,
  node 2). Its judge, which re-judges every tile with the reference on the CPU, was at 63 of 588 tasks at 4:40 PM PDT, about
  29 per 30-min chunk (Measured), so roughly 9 more hours of wall time (Estimated).
- 4:40 PM PDT read 3:02 PM PDT (bc-f5bf55c8's 70B version 4 coverage census on the GPU). **Premise corrected:** that census
  runs `fp4_f1_pricing.linear` (bc-f5bf55c8's numpy float64 emulation, certified law, NVFP4), not #580's `tile_cap`, so the
  bit-for-bit port above doesn't apply. I wrote a new torch port, `benchmarks/pouw/fp4_cov70b_gpu.py` (`de8c3df9`,
  `4f406662`). The draws, ρ², `volunteer_rows` and `summarize` stay the census's own code; the witness, the per-row law,
  byte CDFs, block excess and the F1/F2 windows run in float64 on the GPU. **It is not bit for bit:** FFT, `pow` and
  reduction orders differ at about 1e-15. So its gate requires every count to be equal and every figure to agree within 1e-9
  relative. The local gate over synthetic linears exercises rejects, R1, `volunteer`, several draw chunks and partial
  batches: 0 mismatches, worst difference 5.2e-13 (Measured, CPU torch). On node 2, queued at 4:39 PM PDT under
  `/workspace/pouw/gpu7-fp4/cov70b/4f406662/`, with its own `out/`:
  - `ref`: `F.linear` itself, run on the CPU.
  - `gate`: the port on the GPU against `ref` on the same draws, on layers 0 and 79, all 7 linear kinds at the census's 8
    bands plus k/v at every band. Any mismatch exits 1 and queues nothing further.
  - 8 `run` jobs, L00-09 through L70-79 (`gpus=1 prio=10`, 6.5-min chunks, exit 99): every weight band (the CPU census
    samples 8), over salts 0–7. Salt s appends s to the census's seed, so the salts give the spread of coverage over the
    verifier's draws, which the CPU census doesn't measure.
  - `summary`: queued only when every layer is done at every salt.
- 5:15 PM PDT **70B GPU census running, gated with 0 mismatches** (`art:d146ee99…`: the gate outputs, the CPU reference
  and the job scripts). All Measured on node 2's RTX PRO 6000s:
  - against `F.linear` itself: 18 cases (layers 0 and 79, all 7 kinds), 0 mismatches over 954 counts and 1,188 figures,
    worst figure 1.2e-14 relative. The port takes 0.12–1.7 s a case, against the CPU census's 12–79 s.
  - at the run's batch size (2^26 elements) and code: 25 cases, the 18 above plus layer 12's 7 linears at every band
    against the 2^24 outputs (the draw chunks grouped differently): 0 mismatches over 1,332 counts and 1,650 figures, worst
    1.2e-14. Each code version gates itself once, before its first linear (`out/gate-b26-<code>`).
  - **The first chunks were starved of CPU, not GPU.** The fill runner pins GPU jobs to the same 32 cores (96–127, nice 19)
    as the 4 pous CPU slots. At load ~100 my processes got 13–29% of a core, held GPUs at 1–12% utilization, and did 25
    linears per chunk against 219 for a luckier job, while cores 128–191 sat idle. The bound was the port's kernel
    launches (thousands of small ones per row batch). 2^26 batches (`141b552e`) cut them about 4×: each job now gets about
    1.1 cores and 2.6 s of GPU-held wall time per linear at every band (L00–09: 106 linears in 4.6 min, from 25 in 6.5).
    The pinning is the runner's policy, not mine: for the infra steward, GPU fill jobs whose host side is Python-bound
    lose 4–9× on those cores.
  - **Size:** salts 0–15 at every band over the 560 linears = 8,960 linears ≈ 6.5 GPU-h (Estimated from the measured
    2.6 s). At 5:12 PM PDT, 1,748 were done in about 82 GPU-min (Measured, from the runner's events). Jobs:
    `fp4-cov70b-run-L{00-09,…,70-79}-4f406662.sh` (salts 0–7), `fp4-cov70b-run-s08-15-L{00-09,…,70-79}-f0822520.sh`
    (salts 8–15), then `fp4-cov70b-summary-s00-15-f0822520.sh`. All are `gpus=1 prio=10`, 6.5-min chunks, exit 99.
    Every output records its code hash and batch size.
  - **Interim, salt 0 complete** (560 linears, 419,840 tiles at every band; `art:daba1118…`; Measured with the census's
    own `summarize`): uncredited 4.28%, 0 tiles rejected, worst credited tile 0.919 of the cap (L66 o_proj), tiles over
    0.5/0.8/0.9/1.0 of the cap 15,250/1,040/177/0, `volunteer` gave up 0 rows, uncertified blocks 23 of 99.6 M (A) and 37
    of 4.28 G (W). The CPU census (`out4/`, 8 bands) hasn't started. When it lands, its layers 0 and 79 should equal the
    gate's 8-band cases, which use its seeds; I'll check them then. Its other layers draw different bands, so they compare
    only in distribution.
  - Shortcuts: the port isn't bit for bit (above). Salts 1–15 extend the census, they aren't part of it: they give the
    spread of coverage over the verifier's seed. The capture is node 2's 256 tokens.

## For bc-a8466279 and the assessor: the stride rows under F1′ (13:25Z ask)

F1′ was run unchanged: `dnc2.py` and its modules, copied from `internal/pouw/cheap-binding/pearlc4-fix` (sha256 in the
output). Here it reproduces its own table (91.7% / 28.9% / 0.0%). It ran on the stride families of #545, with the
spiky-row and Gaussian families as controls: NVFP4, 64 rows × k 8,192 per side, two draws. Beside it is the split's
measured cost on the same rows, from GPU 5's twin at #548's tip (`e1e4c561`). FP32 op = 2 × 1047/125 = 16.752 FP4 MACs,
both in F1′'s C and in the CUDA-core route. With the rule's C = 16.92/128 instead, no tile debit moves by more than
0.007. `lut256` at 8.55 W1 changes none of these figures: forming, the block scale included, is the same work for the
honest prover and the split. (`fp4_f1prime.py` at `5b8b9989`; `art:fb8f7aac94a906a831debe55610a69f29243c1da388f63e2e1d3f5308d62330b`;
Measured, CPU.)

| Family (A and B alike) | F1′ S_w per side | Modal-byte share | F1′ debit per side | Tile debit (A + B) vs cap 1/400 | Split, exact (value level), one-sided / two-sided cost | Rule's model (codes + scale term, A0's products free), two-sided cost | Net gain |
|---|---|---|---|---|---|---|---|
| stride-row-grid (ρ = amax/10) | 1.50 | 0.95 | 1.45–1.46 | **2.91: rejected** | 0.87–0.89 / 1.76 | 0.78–0.80 | **none** |
| stride-row-grid-edge (ρ = amax/9.45) | 1.04 | 0.95–0.96 | 1.00 | **2.01: rejected** | 0.95 / 1.90–1.91 | 1.06–1.08 | none |
| stride-row-tight | 0.51–0.52 | 0.70 | 0.39–0.40 | 0.78–0.79: rejected | 1.000 / 2.00 | 2.22 | none |
| stride-row (the proposer's) | 1.06–1.17 | 0.73–0.74 | 0.95–1.05 | 1.92–2.09: rejected | 1.000 / 2.00 | 2.19–2.20 | none |
| spiky-row (control) | 0 | 0.48–0.49 | 0 | 0: admitted | 1.000 / 2.00 | 2.25 | none |
| Gaussian (control) | 0 | 0.29–0.30 | 0 | 0: admitted | 1.000 / 2.00 | 2.25 | none |

- **No family nets a gain.** Every stride family's tile is rejected with a debit of 0.8–2.9 per MAC, 300–1,200 times
  the cap, so it costs coverage, not γ. The controls carry no debit and have nothing to save.
- **The exact split never paid two-sided on these rows.** Its A0 is full rank and B̃ is salt-keyed, so the prover pays both
  sides' corrections: 1.76 on stride-row-grid, against the honest 1.000. Re-drawn at the ruled price, one-sided is
  0.87–0.95 with the CUDA-core route and 0.98–0.99 with the 2:4 route alone. At #545's own seeds this twin gives 1.831
  and 1.937 two-sided, so the lower 1.76 is the draw.
- **Only the rule's own model saves anything, and F1′ charges it 13–15 times over.** Treat A0's per-block products as free
  and correct only the blocks whose scale moved (5–6% of blocks). stride-row-grid then costs 0.78–0.80 two-sided, a
  saving of 0.20–0.22, against a tile debit of 2.91.
- **F1′ reads these rows as the narrow-cell family, as §6.5 expected, but harder.** Codes at cell centres give P(≠ mode)
  ≈ 0, so S_w reaches the rule's ceiling of 1.5 (0.5 for the 2:4 pass and 0.5 for each k64 half). The modal-byte share
  is 0.95, so the scale term is only 0.04–0.05. F1′ also rejects stride-row-tight and the proposer's rows, which the exact
  split can't use (cost 1.000). That costs coverage on crafted rows only; the honest controls stay at 0.

## For bc-a8466279 (Pearl-C4 design fix; the root relays)

What this lane measured on the salt-free base split and stride rows. All Measured on CPU with the confirmed sm_120
atoms unless labelled. Nothing here is new work on the current noise design.

- **Stride rows, NVFP4, value level, FP32 op at 16.92 FP4 MACs, two-sided since B̃ is salt-keyed** (`fp4_formed_census.py`
  on GPU 5's twin at `5f0a1529`, 64 rows × k 8,192; `art:92f3567a…`, edge row `art:4767f842…`):

  | Family (A side) | One-sided, 2:4 route | One-sided, + CUDA-core correction | Two-sided |
  |---|---|---|---|
  | stride-row-grid (top two codes of amax 1, ρ = amax/10) | 0.988 | **0.923** | **1.84** |
  | stride-row-grid-edge (ρ = amax/9.44, inside the √90 screen) | 0.995 | 0.975 | 1.94 |
  | stride-row-tight, the proposer's stride-row, spiky-row, Gaussian | 1.000 | 1.000 | 2.00 |

  This agrees with your 0.924 / 1.846 at the 10ρ edge and 1.953 at the √90 edge. At the code level (counting changed
  codes only) the same rows read 0.51–0.54, so a code-level debit misprices NVFP4: a salt-moved UE4M3 scale changes
  every product in its block. The CUDA-core route's word-exactness isn't replayed (Estimated).
- **Mechanism:** ρ is taken at every 8th position, so a row can hold ρ at amax/10 and put its other entries at grid
  centres. Noise σ = ρ/4 against a half-step of amax/6 then moves 2% of codes. The witness `salt_dead` is 0 on these
  rows, so item 1 debits nothing; the saving is TT_OUT's carried share, and this family shows it is not small.
- **MXFP4 (contrast only, the same flat-scale property as its int8 closure):** UE8M0 scales never move with the salt,
  so the same rows cost 0.76 two-sided at the 10ρ edge and 0.94 at the √90 edge.
- **The base split ties at 1.000 on every real cell:** Qwen2.5-7B, 7 linears × layers 0/1/3/13/27, both sides, both
  formats, at the code, value and CUDA-core levels (twin at `524d0c2b`, 12ρ). Exact forming at `5f0a1529` (10ρ) gives
  a minimum of 0.999 (MXFP4; `art:142daa4b…`). Real change density is 0.49–0.64 of codes per salt.
- **The noise floor decides the tie** (`fp4_census.py basesplit`, 11 families): row-relative δ = 1/8 ties at exactly
  1.000 on every family; δ = 1/10 leaks 1.9% on outlier-in-block rows; δ = 1/16 costs 0.588 there; block-relative
  noise costs 0.75–0.99 at any δ. The design's δ = 1/4 has margin on these families.
- **Chains:** v1's chains are exact on every step of the stride families (both formats), so the split reproduces v1's
  words. Under v2 (T1, the census's own model at h = 14; GPU 5's twin has no T1), NVFP4 floors every stride-row word
  (0.000 exact), so the split no longer reproduces them. **Spiky rows stay 1.000 exact under v2**: T1 doesn't close a
  split on spiky rows, as the T1-closures note found. On MXFP4, h = 14 floors nothing on any family.
- **Fixes, as measured or proposed here** (Needs 0 below):
  - (a) Take ρ over every position, or ρ = max(ρ₈, amax_row / c), so no row can hold its noise below amax/(4c). A proxy
    supports it: the census's stand-in noise scales with the whole row's RMS and changes 50–90% of codes on the same
    rows, so the split costs 1.000 on all three stride families (a proxy, not the reference's own forming: Estimated).
  - (b) A noise floor of max(row, block).
  - (c) Debit the realised per-salt split saving on each drawn tile, at fragment granularity with the CUDA-core route.
- **What a fix must keep: honest coverage under the 10:35Z screen** (§3.3 of `fp4-cheaper-computation.md`,
  `art:8d6aff0f…`). Every real row passes D-NF. 0.987 of tiles are within ρ = 1/400 and 0.974–0.982 within 1/1,000.
  The honest debit's median is 0.04–0.06 of 1/400. gate_proj L0–L2 miss, mostly through item 3.
- **Re-running a proposed rule:** `fp4_formed_census.py --families` (exact forming on GPU 5's twin) and `fp4_census.py
  debit|basesplit` (all 28 real layers) take minutes on CPU. Hand me the rule and I re-run the stride, spiky and real
  cells.

## Results

All CPU (stand-in atoms / float64 emulation) unless noted; nothing timed on the card yet. **MXFP4 is broken as a
candidate (server.md 11:19Z: flat block scales, int8 closure D), so every MXFP4 figure here is contrast.**

**Base split on stride rows, on Pearl-C4's exact forming (09:22Z ask, re-priced after bc-a8466279's 10:40Z check;
Measured, CPU, `fp4_formed_census.py` at `abfd19d7`, GPU 5's twin and reference at `5f0a1529` (10ρ), 64 rows × k 8,192,
one salt; `art:92f3567a2c58814a5934ebb98eee8bebdb9b4114390741ec9269e17bc23f4a69`).**
Cost per MAC of the salt-free base split's correction over aligned 16 × 64 fragments, against the honest 1.000.
"2:4" = skip / one `mma.sp` pass / dense (GPU 4 measured those words equal to dense, so this route is exact). "+ CUDA
core" adds a per-fragment FP32 correction of the changed codes at 16.92 FP4 MACs each, the measured FFMA's 8.46 FP8
MACs × 2 (its word-exactness is not replayed: Estimated). "Code" counts changed codes; "value" also counts every code of
a block whose scale moved. The MMA sees values, so the value level is the one that prices a route. Two-sided is A's
cost plus B's, since Pearl-C4's B̃ is salt-keyed.

| Family (A = activations side) | Rows admitted | Codes one salt changes | Blocks whose scale moves | Code, 2:4 | Value, 2:4 | Value + CUDA core | Two-sided, value + CUDA core |
|---|---|---|---|---|---|---|---|
| NVFP4 stride-row-grid (top two codes of amax 1; every 8th at ±0.1, ρ = amax/10) | 1.00 | 0.023 | 0.062 | 0.514 | 0.988 | **0.923** | **1.84** |
| NVFP4 stride-row-grid-edge (ρ = amax/9.44, inside the √90 screen; `art:4767f842…`) | 1.00 | 0.036 | 0.069 | 0.541 | 0.995 | 0.975 | 1.94 |
| NVFP4 stride-row-tight (±U(0.5, 1); every 8th N(0,1)/9) | 1.00 | 0.149 | 0.32 | 0.990 | 1.000 | 1.000 | 2.00 |
| NVFP4 stride-row (the proposer's, /10) | 0.53 | 0.135 | 0.29 | 0.978 | 1.000 | 1.000 | 2.00 |
| NVFP4 spiky-row / Gaussian | 1.00 | 0.53 / 0.59 | 0.50 / 0.70 | 1.000 | 1.000 | 1.000 | 2.00 |
| MXFP4 stride-row-grid | 1.00 | 0.024 | 0.000 | 0.507 | 0.507 | **0.395** | **0.76** |
| MXFP4 stride-row-grid-edge (the same) | 1.00 | 0.032 | 0.000 | 0.521 | 0.521 | **0.478** | **0.94** |
| MXFP4 stride-row-tight | 1.00 | 0.100 | 0.000 | 0.816 | 0.816 | 0.816 | 1.67 |
| MXFP4 stride-row | 0.53 | 0.090 | 0.000 | 0.761 | 0.761 | 0.761 | 1.55 |
| MXFP4 spiky-row / Gaussian | 1.00 | 0.37 / 0.56 | 0.002 / 0.07 | 1.000 | 1.000 | 1.000 | 2.00 |
| **Real Qwen2.5-7B**, 7 linears × layers 0/1/3/13/27, both sides, both formats (twin at `524d0c2b`, 12ρ) | — | ≥ 0.49 (median 0.55–0.64) | — | 1.000 every cell | 1.000 every cell | 1.000 every cell (priced at 8.46; a higher price can only raise it: Derived) | 2.00 |

- **What changed at 10:40Z** (bc-a8466279's two corrections, both right):
  - The first table (`78d7f041`, `art:85bb6341…`) priced an FP32 op at 8.46 FP4 MACs. The measured 8.38–8.46 are FP8
    MACs, so an FP32 op costs 16.76–16.92 FP4 MACs. At 16.76, every CUDA-core figure here drops by at most 1%, since
    min(c, 0.99x) ≥ 0.99·min(c, x) (Derived).
  - Its NVFP4 headline (0.51 one-sided) read the code level. A salt-moved UE4M3 scale changes every product in its
    block, so on NVFP4 the 2:4 route costs 0.99–1.00, and the one-sided threat is the CUDA-core route: 0.92 on
    stride-grid rows. The 0.65 I reported was the same route at the FP8-unit price.
- **NVFP4: v1's tie holds.** Two-sided, stride-grid rows cost 1.84 and every other family 2.00, inside bc-a8466279's
  1.23–1.95× (`cheap-binding/pearlc4-stride-rows.py`). One-sided, the CUDA-core route would save 8% on stride-grid
  rows, and the salt-keyed B̃ rules that model out.
- **MXFP4's stride-grid rows still beat honest two-sided, through the CUDA-core route: 0.395 + 0.369 = 0.76.** 86–95% of
  their fragments take that route; the exact 2:4 route alone ties at 1.01. UE8M0 scales move in no block of any stride
  family, so the value level is the code level, and each salt changes 2% of codes on each side. Plain stride rows cost
  1.55–1.67. Unless bc-a8466279's check covered MXFP4 and found ≥ 1.23, this is open for MXFP4 (Needs 0). The route's
  word-exactness isn't replayed (Estimated).
  - **The √90 screen (10:40Z) doesn't close it.** It screens these rows (amax = 10ρ), and the 10:35Z rule charges
    them. But moving ρ to amax/9.44 escapes the screen, and MXFP4 still wins two-sided: 0.478 + 0.463 = **0.94**
    through the CUDA-core route (the 2:4 route 1.04; `art:4767f842…`). NVFP4 at the same edge costs 1.94, theory's
    1.953. bc-a8466279's check (`theory-pearl-c4-domain.md`, stride rows) is NVFP4 only, and matches mine there: 0.924
    one-sided and 1.846 two-sided at the 10ρ edge, against my 0.923 and 1.84.
- Rows admitted is 0.53–0.55 on this draw of the plain stride family, and was 0.41 on the first (64 rows each).
- v1's chains are exact on every step of all three families (from +0, both formats; `fp4_census.py synth`), so the
  split reproduces v1's words.
- **Mechanism:** ρ is sampled at every 8th position, so a row can hold ρ at amax/10 (the 10ρ screen's edge) and put
  its other entries at grid centres: noise σ = ρ/4 = amax/40 against a half-step of amax/6 moves 2% of codes. The
  reference's witness `salt_dead` is 0 on these rows (the support's extremes, about 6ρ, move every code), so item 1
  debits nothing; the per-salt coincidences are TT_OUT's carried share, and this family falsifies it.
- **v2 (T1) on the same rows, in the census's own v2 model** (GPU 5's twin has no T1 yet; `fp4_census.py debit` at
  `2e84abe5`, k 8,192, 64 pairs, row noise). The split reproduces a word only when its chain loses no bits:

  | Words whose chain loses no bits | Gaussian | stride-grid | stride-tight | spiky |
  |---|---|---|---|---|
  | v1, both formats | 1.000 | 1.000 | 1.000 | 1.000 |
  | v2 NVFP4, h = 14 (row or word rule for H) | 0.000 | **0.000** | 0.000 | **1.000** |
  | v2 MXFP4, h = 14 | **1.000** | **1.000** | **1.000** | 1.000 |

  - **On NVFP4, T1 closes the split on stride rows:** its floors bite on every word. They don't on spiky rows, as the
    T1-closures note found.
  - **On MXFP4, T1 at h = 14 floors nothing on any family:** MXFP4's product unit sits far fewer bits below the atom
    sum than NVFP4's. In a sweep at k 2,048 (Estimated, small), Gaussian words stay 94% exact at h = 8 and first
    all floor at h = 6.
  - **MXFP4's identity atoms alone already charge every admitted spiky tile 0.0088 (3.5ρ)** and Gaussian tiles 0.0025
    (ρ), on v1 and v2 alike (item 2; 0.79% and 0.19% of steps). At h = 6 they rise to 0.0057 on Gaussians. So on MXFP4,
    v2 can't both floor the chains and keep the debit under ρ = 1/400: Needs 0.
- The stand-in noise (RMS over the whole row) misses the family: it changes 50–65% of codes on the same rows.
  On real rows the two agree within a few points (0.636 vs 0.653 NVFP4 A), and the reference's `salt_dead` agrees with
  `fp4_census.witness_salt_dead` on every witness row (4 per cell, 1.000).

**ε_R and the zero fractions (09:30Z first ask, `fp4-merge-rate/sm120`; Measured, CPU on the confirmed atom).** ε_R
(strict) = the share of Strassen-pattern pairs of two live blocks (adjacent and half-split in k and in rows, and the
diagonal) whose sum or difference is one FP4 value under one scale of the format; the partner shares are the adaptive
side (a block with any mergeable partner in the same k-block or row, over 64 k-blocks).

| Operands (row noise δ = 1/4, stand-in; `art:28235eab…`) | NVFP4 ε_R median / max | MXFP4 ε_R median / max | Zero codes NVFP4 / MXFP4 | Zero blocks |
|---|---|---|---|---|
| Real activations, 28 layers × 7 linears | 0.0092 / 0.039 (L14 o_proj, adjacent-row) | 0.069 / 0.23 | 0.11 / 0.16 | 0 |
| Real weights | 0.0001 / 0.0027 | 0.0001 / 0.022 | 0.072 / 0.091 | 0 |
| Synthetic families (11) | ≤ 0.0012 | ≤ 0.0012 | 0.06–0.07 (Gaussian) | 0 (zero-blocks family: 0.5 A) |
| rank-1 A | 0.020 | 0.135 | | |
| outlier-in-block A | ε₋ 0.37, ε₊ 0 | ε₋ 0.95–1.0, ε₊ 0 | 0.45 / 0.55 | |
| **Forming on the GPU** (09:56Z ask; stand-in, device noise; `fp4_merge_gpu.py` at `ce5f8f18`, gated bit for bit against the census; `art:a4268def…`): real activations, all 28 layers × 7 linears | **0.0091 / 0.037** (L1 o_proj) | **0.070 / 0.23** (L19 o_proj) | 0.11 / 0.16 median (max 0.19 / 0.29) | 0 |
| Same run: real weights | 0.0001 / 0.0032 | 0.0001 / 0.022 | 0.072 / 0.091 | 0 |
| Same run: families, 256 × 16,384, A (Gaussian / t₄ / outlier-in-block / rank-1 / spiky / stride-grid) | 0.0001 / 0.0002 / 0.38 / 0.019 / 0.027 / 0.0005 | 0.0000 / 0.0007 / 0.96 / 0.11 / 0.006 / 0.0000 | Gaussian 0.068 / 0.088; stride 0.02–0.03 | 0 |
| **Exact forming** (GPU 5's reference at `5f0a1529`, 10ρ), real layers 0/1/3/13/27 × 7 linears, 64 rows × k 4,096: activations | **0.0092 / 0.042** (L1 o_proj) | **0.096 / 0.29** (L1 o_proj) | 0.12 / 0.22 median (max 0.19 / 0.36) | |
| Exact forming, same cells: weights | 0.0003 / 0.0059 (L0 gate_proj) | 0.0017 / 0.047 (L0 gate_proj) | 0.073 / 0.12 median | |
| Exact forming, families A, 64 rows × k 8,192: Gaussian / outlier-in-block / rank-1 | 0.0001 / 0.056 / 0.107 | 0.0006 / 0.52 / 0.40 | 0.068 / 0.18 / 0.069 (NVFP4); 0.107 / 0.26 / 0.111 (MXFP4) | |
| Exact forming: spiky-row A / stride-row-grid A / stride-row-tight A (k 8,192) | 0.028 / 0.010 / 0.0013 | 0.083 / 0.0006 / 0.0004 | 0.27 / 0.0015 / 0.035 (NVFP4); 0.44 / 0.007 / 0.052 (MXFP4) | 0 |

- NVFP4 partner shares on real activations: 0.19 of live blocks have a mergeable partner in the same k-block (another
  row), 0.012 in the same row; weights 0.021 / 0.006.
- **The GPU run reproduces the CPU census with independent noise draws** (ε_R 0.0091 against 0.0092 median on NVFP4
  activations, 0.070 against 0.069 on MXFP4), over all 28 layers. It took 14 GPU-minutes in 3 fill chunks (GPU
  `GPU-0c776bca…`). **Searching 1,024 k-blocks instead of 64 raises the same-row partner share** to a median of 0.061
  (NVFP4) and 0.18 (MXFP4) of live activation blocks, up to 0.43 / 0.61 (L5 down_proj). The same-k-block share is about
  unchanged (0.18 / 0.34 median). This is a bound on the pairs a prover can choose, and it grows with the candidates
  searched (at a per-pair rate near 3e-4, 1,000 candidates give about 0.26). A Strassen pre-add also needs the matching
  pre-add on the other operand, where the fixed-pattern ε_R is the number that counts.
- Only differences merge on the outlier family (ε₊ = 0): its blocks share one dominant code, which cancels.
- **Exact forming against the stand-in** (`fp4_formed_census.py` at `464722c0`, twin `5f0a1529`;
  `art:142daa4b2ff67647ac5f5140342c7c73fedce7fe3cb80451c16c9497af7c16ba`): NVFP4's real-activation ε_R is the same (0.0092
  median); MXFP4's is higher (0.096 / 0.29 against 0.069 / 0.23), and so are its zero codes (0.22 against 0.16). On the
  families, exact forming raises rank-1 (0.107 / 0.40 against 0.020 / 0.135) and lowers outlier-in-block (0.056 / 0.52
  against 0.37 / 0.95), since ρ at every 8th position sets a different step on those rows. The base split still costs
  1.000 on every real cell at 10ρ, with and without the CUDA-core route (min 0.999, MXFP4).
- **What it does to Strassen** (Derived): a level with FP4 pieces costs 3(2−ε_X)(2−ε_Y) + 2(2−ε_X) + 2(2−ε_Y) slots
  against 8; at the worst real rates that is ≥ 17 against 8 (exact forming's worst, MXFP4 activations 0.29 with weights
  0.047: 17.3), and at MXFP4 outlier-in-block's ε₋ ≈ 1 with the best sign
  choice about 10.1 against 8 (each operand's sign freedom is rank one, so not every piece can be a difference). The
  Winograd cross-operand inner-product route is not measured.
- The zero fraction the tile model estimated at 6–7% for Gaussian rows is 6.8–7.0% (NVFP4) Measured; real activations
  carry 11% (NVFP4) and 16% (MXFP4), spiky rows 27–44%.

**Cheaper-computation surface (Measured on CPU stand-in atoms; full table in `fp4-cheaper-computation.md`):**
- **Exact chains do not erode with depth:** exact_steps = exact_chains = 1.000 at k ∈ {2,048…32,768} for Gaussian, t₄,
  rank-1, 2:4; MXFP4 also exact on coherent/outlier/zero-blocks/scale-spread. Order-binding is gone at every depth
  (matches the FP8 lane's 98–99%). γ must rest on the price argument, not rounding.
- **Row-relative noise (design's β_row, δ=1/4) defeats the structural routes:** tile-2:4, zero-block and duplicate-block
  fractions → 0 on every family. **Block-relative noise does not** — outlier "dead" blocks keep 44% of quads 2:4 vs 8%
  under row-relative. Row-relative floor + dead-block debit is the key domain constant.
- **2:4-sparse route (SASS `OMMA.SF.SP.168128.F32.E2M1.E2M1.UE4M3.4X`, Measured offline):** 0.5×/MAC at the placeholder
  price; crafted 2:4 activations reproduce every word (exact). Domain must exclude 2:4 fragments (Need, sent early).
- **MXFP4 identity atoms ~0.21% on Gaussian** (NVFP4 0.00%), stable across k — above the design's "≪0.1%" (Need to GPU 5).
- **Fastest cheaper computation = salt-free base split + 2:4 Δ (A2+A3): ties honest at 1.0×, does not beat it,** given
  the Measured 68–77% code and 74–80% scale change between salts. So γ is set by the credited fraction, not a shortcut.
- **Base-split empirical γ check (`fp4_census.py basesplit`, Measured, CPU):** per-call A-side cheater cost / dense MAC:
  **row-relative δ=1/4 → 1.000 on every family** (density 0.49–0.60, no 2:4 coverage); row δ=1/8 → 1.000 (the floor);
  row δ=1/16 → 0.588 on outlier rows (beats); **block-relative any δ → 0.75–0.99 (beats, `sparse-2of4` 0.747).** The
  noise floor decides γ: **row-relative, δ ≥ 1/8**; the design's δ=1/4 is safe with margin, block-relative is not.
- **Salt-dead 4-group share — theory §5 Q2/Q3's debit statistic (06:15Z ask; `fp4_census.py basesplit`, `774e321f`;
  Measured, CPU on the confirmed atom).** Per (row, 4-group of k), a code is *salt-dead* when the base already holds it
  (Δ=0); a group with ≥2 salt-dead codes has Δ in one 2:4 half, so Q3 debits it at 0.5/MAC. At the design's
  **row-relative δ=1/4:**

  | Operands | Clean-vs-salt change density | Share of 4-groups with ≥2 salt-dead | Q3 debit (0.5×share) /MAC |
  |---|---|---|---|
  | **Real Qwen2.5-7B, NVFP4** (7 linears × layers 0/1/3/7/13/20/27; `basesplit --acts`, `31c20126`) | 0.61–0.80 | **median 0.44**, range 0.17–0.50 | median 0.22 |
  | **Real Qwen2.5-7B, MXFP4** | 0.57–0.77 | **median 0.49**, range 0.22–0.55 | median 0.25 |
  | Synthetic typical (gaussian, t4, rank-1, coherent, 2:4) | 0.55–0.61 | 0.51–0.59 | 0.26–0.30 |
  | Synthetic worst: outlier-in-block | 0.40–0.49 | **0.70 (NVFP4) / 0.79 (MXFP4)** | 0.35 / 0.39 |

  - **The theory lane's ~35% is low.** Its iid-Binomial *model* is right (measured tracks P(Bin(4,p)≤2) within
    0.01–0.04), but it used p ≈ 0.72 (the 68–77% salt-vs-salt rate). The base-split cheater's base is the *clean* codes,
    and the clean-vs-salt density is lower (real median ≈ 0.63), so the share is ~0.44–0.49 on real operands, up to
    0.79 adversarially. **If γ's debit term scales with this share, re-derive Pearl-C4's 0.73% with it.**
  - **But the hardware can't realize it:** the whole-fragment 2:4 share is **0.000 and the cheater's cost 1.000× on
    every real linear and every synthetic family.** `mma.sp` needs all 16 rows × 32 groups of a fragment 2:4 at once, so
    a per-4-group debit charges for a saving that 16-row fragments never deliver. Debiting at fragment granularity would
    make it ~0, pending a soundness argument that no sub-fragment 2:4 route exists (theory lane's call).
  - **δ trades the debit:** gaussian share 0.82 / 0.71 / 0.53 / 0.26 / 0.12 at δ = 1/8, 1/6, 1/4, 1/2, 1 (NVFP4; MXFP4
    within 0.02). A larger δ shrinks it, at a quality cost.
- **Prices (Measured, node 2, locked-2100; my `fp4_attack.py peak` run by the coordinator, `r20260930-062619-81e2`):**
  **dense 1.000, 2:4-sparse 0.500, int8 1.997 per FP4 MAC** — the public placeholders (1.0/0.5/2.0) hold. No dense
  algebraic rewrite pays (Strassen ≥1.34×, int8 ≥2× + per-block rescales); the only sub-1.0× route is 2:4-sparse, gated
  by the domain (salt-dead share above).
- **Atoms confirmed on the RTX PRO (Measured, node 2):** NVFP4 0 mismatches / 2,269,184 vs `BLACKWELL_SM120_NVF4`
  (`r20260930-062419-a63c`), MXFP4 0 / 2,056,192 vs `_MXF4` (`r20260930-062426-8be5`). So every CPU census here, run on
  these pins, is the real sm_120 atom. **2:4-sparse NVF4 writes exactly the dense words** (GPU 4, `r20260930-062452-464f`:
  0 different of 131,072 + 2,514,944), so the 2:4 route is exact and real, as the census assumed.
- **Real Qwen2.5-7B operands (`fp4_census.py real`, layers 0/1/3/7/13, 7 linears, k 3,584–18,944):** MXFP4 bit-exact
  everywhere; **NVFP4 freezes on early-layer massive-activation operands** (min chain-exact 0.34 none / 0.77 row;
  gate_proj L0/L1 0.76/0.59, down_proj L1 0.46). No structural cheaper-computation surface on real operands (zero-blocks
  ~0, no 2:4). The design's §3 "chains exact" premise holds for MXFP4 but fails for NVFP4 near massive activations (§9 open).

**Quality (streamed layer-by-layer, `fp4_quality.py`; Measured, FP32 matmul of the dequantized operands; clean-path RNE
quantizers, not the frozen atom's accumulation; lm_head BF16 in every variant):**
- Harness validated: streamed BF16 ppl 15.913794 vs the HF full model 15.913792 on Qwen2.5-0.5B.
- **Headline: Qwen2.5-7B WikiText-2 test, 65,504 tokens (32×2048), on the RTX PRO (GPU-1cd543c7, fill job, `cc14bb21`;
  `art:59a6f7338f1b40e04cdbefe50afbce3e8538392fc9869e301b90fc814044a638`). BF16 ppl 6.7154. ± is one standard error over
  windows.**

  | Variant | PPL | vs BF16 | vs its clean FP4 path |
  |---|---|---|---|
  | FP8 E4M3 W8A8 (per-row scale) | 6.7647 | +0.73% ± 0.08 | |
  | NVFP4 W4A4 | 7.1957 | **+7.15% ± 0.66** | |
  | MXFP4 W4A4 | 8.6980 | **+29.52% ± 1.16** | |
  | NVFP4 W4A16 | 6.9581 | +3.61% ± 0.37 | |
  | MXFP4 W4A16 | 7.4731 | +11.28% ± 0.66 | |
  | **PoUW-NVFP4, row δ=1/4 (the γ-secure design)** | 7.2559 | +8.05% ± 0.74 | **+0.84% ± 0.27** |
  | **PoUW-MXFP4, row δ=1/4** | 8.5786 | +27.75% ± 1.18 | **−1.37% ± 0.30** |
  | PoUW-NVFP4, block σ_c=0.5 (insecure stand-in) | 7.2905 | +8.56% ± 0.77 | +1.32% ± 0.23 |
  | PoUW-MXFP4, block σ_c=0.5 | 8.6531 | +28.85% ± 1.19 | −0.52% ± 0.34 |

  The CPU run of the secure rows on 4×512 (`art:ee47c645…`) agrees within its error: +0.01% ± 0.73 (NVFP4) and
  −3.8% ± 0.8 (MXFP4) vs clean. The noise draws differ between the two devices (same law), as `noise_device` records.
- **Verdict (b):** the PoUW output is acceptable relative to the clean FP4 path: **+0.84% ± 0.27 for NVFP4**, and no
  worse for MXFP4 (its salt acts as dither on a quantizer that clips (6, 8)·2^e to 6). Whether FP4 itself is acceptable
  is the deployment's call: round-to-nearest NVFP4 W4A4 costs +7.2% on this model, MXFP4 +29.5%, so **NVFP4 is the
  quality choice** and MXFP4 W4A4 needs a better quantizer (rotation, GPTQ) before it is usable; most of the loss is the
  4-bit activations (W4A16 halves it). Not measured: the frozen atom's accumulation (NVFP4 freezes on early-layer
  massive activations, above), which comes on top.
- Earlier CPU run, Qwen2.5-7B WikiText-2, 2,044 tokens (4×512), BF16 ppl 8.277:

  | Variant | PPL | vs BF16 |
  |---|---|---|
  | FP8 E4M3 | 8.381 | **+1.26%** (±0.48) — matches the H100 lane's +1.24–1.31% |
  | NVFP4 W4A4 | 9.234 | **+11.56%** (±2.28) |
  | MXFP4 W4A4 | 11.337 | **+36.97%** (±5.90) |
  | NVFP4 W4A16 | 8.797 | +6.28% |
  | MXFP4 W4A16 | 9.518 | +14.99% |
  | PoUW-NVFP4 output | 9.454 | +14.22% (**+2.39%** over plain NVFP4) |
  | PoUW-MXFP4 output | 11.429 | +38.08% (+0.81% over plain MXFP4) |

  The two PoUW-* rows here use the *block-relative* stand-in noise, which the base-split census shows is γ-insecure;
  the headline table above has the secure row-relative rows.

## Run lines on node 2 (`gpu-lease` picks the GPU; the brief's fixed indices don't apply there)

    W=--env GPU_LEASE_WHO=bc-dbc19788-573d-5ba4-b3b2-d6551c1c60ef

    # 1. FP4 route prices + SASS gate. DONE by the coordinator (r20260930-062619-81e2: 1.000 / 0.500 / 1.997). That run's
    #    identity record reads "8 devices visible" (the gate's nvidia-smi bug, fixed in baa30fff); rerun for provenance:
    research run --on vy-nebius-2 --project verity --campaign pouw --source . $W \
      --tool benchmarks.pouw.fp4_redteam_tool:POUW_FP4_ATTACK -- gpu-lease 1 --wait -- \
      bash -c 'uv run --with numpy python benchmarks/pouw/kernels/fp4_attack.py peak --reps 20 --out "$RESEARCH_RUN_DIR"'

    # 2. FP4 quality on one GPU. DONE 08:24Z as the fill job gpu7-fp4-quality.sh (cc14bb21; 32 windows x 2048, all 10
    #    variants, --parts + --budget-s 1080, bf16 dumped all 28 layers; venv /workspace/pouw/gpu7-fp4/venv = torch
    #    2.14.0+cu130). Output /workspace/pouw/gpu7-fp4/out/quality_w32_s2048.json, art:59a6f733... The whole split
    #    (146 windows) is ~5x this: FILL_EVAL_WINDOWS=0, ~30 GPU-min over chunks (Estimated from variant_seconds).

    # 3. FP4 census (base split, salt-dead share, exact chains): CPU numpy, so no lease; node 2's CPU or any VM.
    #    On the fill job's dumps (all 28 layers), once its bf16 part exists:
    research run --on vy-nebius-2 --project verity --campaign pouw --source . \
      --tool benchmarks.pouw.fp4_redteam_tool:POUW_FP4_CENSUS -- \
      bash -c 'uv run --with numpy python benchmarks/pouw/fp4_census.py basesplit --noise row,block --delta 0.25 \
        --acts /workspace/pouw/gpu7-fp4/out/acts_w32_s2048 --out "$RESEARCH_RUN_DIR/basesplit.json"'

None of these is a timed panel attempt: the prices are instruction rates, and quality and the census are correctness
runs, so each takes one GPU (or none), not a whole-node window. Clocks are locked-2100 node-wide; record them per rep.

## Panel rows

None from this lane so far. The panel plots honest-prover slowdown per attempt; nothing here is an honest attempt on a
line. The route prices feed γ through the theory lane (its 06:55Z γ at the measured prices is already on the panel), and
the cheaper-computation prover is a γ check that ties the honest MMA at 1.000×. If the theory lane's re-derivation with
the measured salt-dead share (Needs 1) moves Pearl-C4's γ, that row is the theory lane's `--change protocol` update.

## Lessons

- **`research run --on vy-nebius-2` needs two things:** main's ssh provider (#478's `ssh_host_target`; a branch cut
  before 05:39Z lacks it: merge `main`) and a `~/.research/machines.toml` entry: `provider = "ssh"`, `host =
  "81.85.2.121"`, `user = "research"`, `projects = ["verity"]`. No credential goes in it: `ssh_key()` decodes
  `RUNPOD_SSH_KEY_B64` itself.
- **An `nvidia-smi` identity gate sees all 8 GPUs** under `gpu-lease`: ask for the visible device with `-i
  "$CUDA_VISIBLE_DEVICES"` and check it against `GPU_LEASE_UUID` (fixed in `fp4_attack.py`, `baa30fff`). Mine had
  failed falsely with `--expect-uuid` and passed unchecked without it.
- **GPU torch for sm_120 on node 2:** PyPI `torch==2.14.0` resolves to `+cu130` with `sm_120` in `get_arch_list()`,
  which you can check on the CPU without a lease. Build it once into a venv on `/workspace` (with `UV_CACHE_DIR` there),
  so fill jobs reuse it rather than download 3 GB each time. Qwen2.5-7B and WikiText-2 are already in `/workspace/hf`.
- **Git push:** the token baked into the remote URL rotates. Push with a fresh one inline:
  `git push "https://x-access-token:$(gh auth token)@github.com/<repo>" <branch>` (nothing written to disk).
- **The agent store:** in a continuation `self` can point at an empty per-agent store; the campaign files are under
  `/cursor/stores/parent`. The mount also returns transient EAGAIN; retry after a few seconds.
- **A torch job with CPU-seeded noise is CPU-bound on the GPU.** `torch.randn(..., generator=cpu_gen).to(dev)` draws
  billions of normals per layer on a few CPU threads (6% GPU utilisation, 410 s/layer). Seed a
  `torch.Generator(device=dev)` and draw on the device; build modules under `with dev:` so the random init isn't CPU
  either. Check GPU utilisation in the run's `resources.jsonl` before assuming a slow job is GPU work.
- **Fill chunks must keep their work:** a timed window can preempt a fill job at any minute (mine after 6.4 of 25), and
  a restart from scratch can starve. Save per-unit results (here one variant's token NLLs) and exit 99 when the budget
  runs out.
- **Patching `mod.forward` with a closure over `mod` makes a reference cycle,** so a streamed layer's weights outlive
  `del layer` until a full gc; on a 15 GB VM that OOM-killed the 7B run twice. `del mod.forward` when the layer is done.
- **A CPU-only fill job waits behind every timed window and the CPU slots (4)**; for a job of an hour or less of CPU,
  the agent VM's own cores can be faster than the node-2 queue.

## Fill candidates

| Job | Run line | GPU-h | Restarts cleanly | Yields |
|---|---|---|---|---|
| FP4 quality, Qwen2.5-7B, the whole test split (32×2048 done 08:24Z) | `gpu7-fp4-quality.sh` (in `/workspace/pouw/fill/done/`) with `FILL_EVAL_WINDOWS=0` | ~0.5 (Estimated: 6.5 GPU-min for 32 of 146 windows) | Yes: per-variant parts; a preempted chunk resumes at the next variant | 4.6× the tokens; only if the ±0.27 on the PoUW-vs-clean gap needs narrowing |
| **Done 10:43Z** (`art:a4268def…`): ε_R and zero fraction with GPU forming (`fp4-merge-rate/sm120`) | `gpu7-fp4-merge-gpu.sh` (`fp4_merge_gpu.py` at `ce5f8f18`, out `/workspace/pouw/gpu7-fp4/out/merge_gpu`) | 0.23 Measured (14 GPU-min over 3 chunks) | Yes: one JSON per unit (family, or layer × linear, per format); exit 99 | ε_R per family and per real linear, with the partner search over 16× the CPU run's k-blocks |
| FP4 census over all 28 layers (CPU, `gpus=0`) | run line 3 on `acts_w32_s2048` (written by the quality job's bf16 part), plus `fp4_census.py real` on the same dumps | 0 (CPU numpy; ~2 s per linear) | Yes (per-layer files) | The salt-dead share and the exact-chain census on every real linear (today: 7 layers) |

## Needs

**To the coordinator → theory lane (bc-a8466279, Pearl-C4's FP4 domain rules / TT_OUT-FP4), highest first:**
0. **(09:55Z; corrected 10:40Z) Stride rows: v1's tie holds on NVFP4, but MXFP4's stride-grid rows still beat it
   two-sided: 0.76 at the 10ρ edge, and 0.94 with ρ moved inside the new √90 screen** (Results, first item). bc-a8466279 settled the threat model: B̃ is salt-keyed, so the cheater
   pays both sides. Re-priced at 16.92 FP4 MACs per FP32 op and at the value level, NVFP4 costs 1.84–2.00 two-sided
   (their 1.23–1.95 agrees) and 0.92 one-sided at worst. On MXFP4, UE8M0 scales never move with the salt. So a row
   that holds ρ (every 8th position) at amax/10 and puts its other entries at grid centres keeps 98% of its codes on
   each side, and the per-fragment CUDA-core correction costs 0.395 + 0.369 (the exact 2:4 route alone ties at 1.01).
   **MXFP4 is out (11:19Z, flat scales), so this is contrast, and the same flat-scale property: nothing to rule for
   the candidate.** bc-a8466279's check is NVFP4 only, and we agree there.
   Mine takes, per fragment, the cheaper of one `mma.sp` pass and an FP32 correction of each changed code (exactness
   not replayed: Estimated). If MXFP4 is in scope, recommended fix first:
   (a) **take ρ over every position, or ρ = max(ρ₈, amax_row / c)**, so no row can hold its noise below amax/(4c). The
       cost is the S5 statistics pass reading every element instead of every 8th (Estimated small beside forming).
       The census re-runs the family under any proposed rule within minutes (`fp4_formed_census.py --families`).
       Evidence that (a) works: the census's stand-in noise scales with the whole row's RMS, and on the same stride
       rows it changes 50–90% of codes, so the base split costs 1.000 on all three families in both formats (a proxy
       for (a), not the reference's own forming: Estimated; `art:142daa4b…`, `stand_in`).
   (b) a noise floor of max(row, block), per my Need 2 below (pure block-relative leaked 1–25%, §3).
   (c) debit the realised per-salt split saving on each drawn tile: the verifier holds the rows and the salt, so it
       can charge item 1 on one salt's changes, at fragment granularity with the CUDA-core route. Exact, but a new
       debit term.
   If MXFP4 is out of scope, headline NVFP4 (0b's default), where v1 needs no fix.
   **Wording:** item 1's statistic is the witness (salt-independent) deadness, which the reference implements and I
   now census; the per-salt coincidences are TT_OUT's carried share, and this family shows that share is not small on
   crafted rows. My earlier per-salt share (old Need 1 below) is the carried share, not item 1's statistic.
   **Under v2 (T1, census model, 10:05Z):** NVFP4 at h = 14 floors every stride-row word, so the split no longer
   reproduces them and v2 closes this family on NVFP4. On MXFP4, h = 14 floors nothing (next item), so v2 doesn't
   close it there either.
0b. **(10:05Z) MXFP4 under v2 needs its own h, and even then its identity atoms put the debit at or over ρ = 1/400**
   (Results, v2 bullets; census model, not GPU 5's twin, which has no T1). On MXFP4, h = 14 leaves every word exact on
   every family, stride rows included, so T1 doesn't close the split there. Gaussian words first all floor at
   h = 6 (k 2,048, Estimated), but by then item 2's identity debit is 0.0057 (2.3ρ). At any h it is already 0.0088
   (3.5ρ) on every admitted spiky tile and 0.0025 (ρ) on Gaussian tiles. So ρ = 1/400 can't hold for MXFP4 as item 2
   stands. *Recommended default:* headline NVFP4 under v2, and for MXFP4 either take GPU 5's within-4-atom zero-sum
   check in place of the identity debit or re-derive ρ per format (Q6, item 4 below). The census re-runs any h or rule
   in minutes (`fp4_census.py debit --hot-bits H --hot-rule row|word`).
   **D-SS coverage at 10ρ is low on real activations:** exact forming admits median 0.69 of NVFP4 activation rows and
   0.39 of MXFP4's (layers 0/1/3/13/27, min 0 on both); weights 0.64–1.00. In the census's tile model (NVFP4, layers
   0–5 so far) 0–14% of activation tiles have every row admitted. What happens to a rejected row (another format, or
   the whole tile falls back) decides how much of the work FP4 certifies at all; the design should say. All 28 layers
   (row rule, 10:25Z): median 0.77 of activation rows (0.96 at 12ρ), none in L1 gate_proj, and 2–39% of tiles per layer
   with every row admitted (`fp4-cheaper-computation.md` §3.2). **Under the 10:35Z rule, with item 4 on the witness
   (11:32Z; §3.3 there, `art:8d6aff0f…`),** every real row passes D-NF. 0.987 of real tiles stay within ρ = 1/400 at
   each linear's own n and fused alike, and 0.974 (own n) / 0.982 (fused) within 1/1,000. On MXFP4 families item 2
   still takes tiles past ρ (§3.3).
0c. **(10:30Z) acc-freeze is admitted and costs 7–8ρ per tile under v2** (§3.2 there; two seeds, both formats): one
   16-block per row 2^18 above the rest has 1 dead block in 256, inside D-SS's 1 in 64, and T1's hot start then turns
   1.3% of steps into identity atoms (v1: 1.7–2.6ρ, item 3). *Recommended default:* set T1's H from the live blocks only
   (D-SS's dead blocks excluded), or charge D-SS on the dead blocks' share of the row's energy. Say which, and the
   census re-runs the family. With H per word instead of per row it costs 3.3–3.6ρ, still over, and a per-word H lets
   merged k128 reproduce 0.16 of whole chains on real layers, against 0.002 per row (`art:bc0bfa62…`). So the default
   stays per row, with H from the live blocks, which is v2-hot's form (11:00Z) plus the exclusion. **Under the 10:35Z
   rule, acc-freeze tiles go past ρ and are rejected** (v1 1.7ρ, v2 8.1ρ; §3.3), so the family now costs coverage,
   not γ.
1. *(Superseded by the reference's witness item 1: on real rows its share is 0.002 at most, `debit` census.)*
   **Q3's per-4-group debit is larger than §5 assumed — re-derive γ with the measured share (NEW, 07:00Z).** At δ=1/4
   the share of 4-groups with ≥2 salt-dead codes is median 0.44 (NVFP4) / 0.49 (MXFP4) on real Qwen2.5-7B, up to 0.79
   adversarially, not ~35%: §5 used the salt-vs-salt rate (p≈0.72), but the base split's base is the *clean* codes
   (clean-vs-salt p≈0.63). If γ's debit term scales with the share, Pearl-C4's 0.73% moves up. **Two ways out:**
   (a) debit at `mma.sp`'s fragment granularity, where the measured share is 0.000 everywhere and the cheater ties at
   1.000× (this needs a soundness argument that no sub-fragment 2:4 route exists); or (b) raise δ (the share is 0.26 at
   δ=1/2), at a quality cost. *Default until you rule:* keep the per-4-group debit (conservative) and cite this share.
2. **Noise floor = row-relative (or max(row, block)), δ ≥ 1/8** (Measured, tight: δ=1/8 ties honest at exactly 1.000×
   on all 11 families; δ=1/10 still leaks 1.9% on outlier blocks; any block-relative noise leaks 1–25%). The design
   already uses row-relative β_row; pin it in the domain.
3. **A domain rule bounding block-scale spread and forbidding zero or underflowed UE4M3 scales** (NVFP4 range
   >~2^17.8 → zero scales, 40% zero blocks on scale-spread). The 2:4 part is now covered by Q3's debit above.
4. **Re-derive the cap ρ on the FP4 atom from this census** (design Q6): the freeze/cancel rates are here to pin it.

*Resolved:* Q2 (a 1.0× tie is compatible with TT_OUT; theory §5). GPU 4 captured the `mma.sp` words (equal to dense,
`r20260930-062452-464f`) and the coordinator ran my `peak` (`r20260930-062619-81e2`).

**To the coordinator → GPU 5 and the vLLM integration (12:06Z; downgraded 12:40Z): forming A once per fused `qkv_proj`
GEMM matters only if the cap drops to 1/1,000.** The 12:06Z figure (58–61% of K/V tiles past ρ) came from the retired
item-4 rule. With item 4 on the witness (`art:8d6aff0f…`), every K/V tile at its own n = 512 is within ρ = 1/400, with
item 4 at most 0.42 of it. At 1/1,000, separate K/V keep 0.971 of their tiles (L4 k_proj / v_proj 0.33 / 0.31, L1
k_proj 0.77). Fused with q (n = 4,608, vLLM's `QKVParallelLinear`), they keep 1.000 (L1 k_proj 0.98). Only item 4
reads n.

**To the coordinator → GPU 5:** MXFP4 identity atoms are ~0.21% on Gaussian (not ≪0.1%); the within-4-atom zero-sum
check / debit weighs more for MXFP4. **Bigger: NVFP4 chains are not exact on real early-layer Qwen operands** (massive
activations); the design's §3 exactness premise holds for MXFP4 only. §9's massive-activation fix (robust ρ / channel
split) is needed for NVFP4 to headline; MXFP4 is the exactness-robust choice pending the quality run.
