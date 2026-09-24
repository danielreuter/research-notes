# Lane fp4-fast — NVFP4 (sm_120, RTX 5090) B-Ligero prover: hints on device, 5090 operating point, pipelined sub-batches (2026-09-23)

CHECKPOINT a2089ac (10:45Z, final; 11:30Z addendum §0b = frozen-main 64c00bd rows on a second pod, numbers from stdout, artifacts
lost with the pod — see §0b / §7) — mergeable: everything on `lane/fp4-fast`; **content identical to 07c3039** (3dfdb21, 063c607
already in main; ba9c73a `--warmup-subs`, a440565 uint8 marshalling, **bc671b0 the fp4 prover as a stage generator + `prove_vus_many`
/ `bench-vu --pipeline N`**, 69a3b04 median-rep contract buckets, 07c3039 full pipelined warm-up pass — the last two touch only
`bench_vu_fp4`; 84b320f `--tail-l natural` was added at 10:35Z and **reverted in a2089ac** after its first row failed Rust's union
bound, §6b.1). Cherry-pick 07c3039 (or a2089ac's tree) — same thing.
Protocol-identical: transcripts byte-identical to main 6babe27 in every configuration measured (§3). Pytest + gates green on
063c607 (r20260923-065143-664b), on **bc671b0 lane tree** (r20260923-085527-380c: 70 passed / 1 skipped, 9/9 gates), on the
**integration tree 1986953** (r20260923-082121-7a8b: 118 passed / 1 skipped, 10/10 gates incl. a `--pipeline 3` bench with dumps)
and on the **headline tree 7c3b157** (r20260923-100554-bff5: 122 passed / 1 skipped, 10/10 gates).
`git status --short` empty, no conflict markers, commits on `lane/fp4-fast` only. Previous checkpoints: 07c3039 (09:55Z), bc671b0 (08:30Z), 063c607 (07:00Z).

**REBASE REQUESTED (unchanged since 08:30Z).** bc671b0 only *activates* on main's `protocol.prove_stages` / `pipeline.py`
(hp2-host, merged as a1f199d / 0d8e178 / 820dc9d); on the lane tree alone it is inert (`_STAGED = False`, the runner calls `prove`
as before, tests green). The rebase conflicts are all in `fp4/chain.py` against the live-verifier lane's hooks (d55c9c3): the
pre-resolved file is `evidence/rebase/fp4_chain.py.merged` (= lane bc671b0 + the live hunks; exactly what the integration trees
ran); 69a3b04 and 07c3039 `git apply` on top of it (they are the int-tree commits 0d33ee7 / 7c3b157); `hints_device.py` applies
cleanly. `run.py`: no change needed (`--pipeline` is main's flag; its help says "registered relations" — fp4-nvf4 now honours it
too, one-word edit if you like).

**For enc-hopper / the coordinator (main regression on consumer parts).** main's `encode_simt.py` since 429f8ea asks for
`4 (3 l + 32)` B of dynamic shared memory = 196,736 B at l = 16384; the RTX 5090's opt-in maximum is 101,376 B (99 KB;
`cudaDevAttrMaxSharedMemoryPerBlockOptin`, same on the 4090), `kernel.max_dynamic_shared_size_bytes = smem` raises
`CUDA_ERROR_INVALID_VALUE`, `protocol._simt_encoder` swallows it and the prover silently runs the torch int64 NTT: encode
0.015 s → **0.203 s** per 4096 VUs on the 5090 (r20260923-075257-ca8b vs -c04d). l = 8192 still fits (98,432 B). Every l = 16384
row measured on a 4090 / 5090 after 429f8ea is on the slow path; H100 (227 KB) is unaffected. Fix is theirs (fall back to the
6babe27 register layout when `smem > optin`, or a `cf`-in-registers variant); until then every integration row below was
measured with the 6babe27 `encode_simt.py` dropped into the integration tree (bit-exact kernels, same transcripts).

Base `main 6babe27`. Worktree `~/projects/verity-main-wt/fp4-fast`, branch `lane/fp4-fast`. Pod `vy-fp4-fast` (RunPod
`6jdyrmzdz39tif`, RTX 5090 32607 MiB reference part, SECURE EUR-NO-1, AMD EPYC 7543 host, cgroup quota 12.75 CPUs of 120 visible,
$0.99/h, created 05:48Z). Scripts in `evidence/scripts/`; per-run evidence in `evidence/<run>/` (result.json, stdout.log,
proofs/manifest.json with `coins_sha256`, proofs/rust_batch_rep1.json). Integration trees are throwaway detached commits in
`~/projects/verity-main-wt/fp4-fast-int` (never a branch): 1986953 = main 02c3321 + bc671b0 runner + 6babe27 encoder;
21694f8 / 0d33ee7 / 7c3b157 = main 9d35c4e + bc671b0 (+69a3b04, +07c3039) + lane `run.py --warmup-subs` + 6babe27 encoder.

## 0. Headline (4096 VUs, int-ZK, interactive, target 2^-128, same 5090, median of 3, Rust `ligero-verify batch` on rep 1)

| tree | l / n | sub-batches (VUs each) | t.total s | R_proved FLOP/s | overhead vs 1.676e15 (contract) / vs 1.8e15 | bits | Rust | run |
|---|---|---|---|---|---|---|---|---|
| spec baseline (fp4-proof r20260923-014637-3f60, main 6babe27, another 5090) | 4096 / 16384 | 25 × 170 | 1.636 | — | 2.2e8 | 128.05 | — | 014637-3f60 |
| **main 6babe27, this pod** | 4096 / 16384 | 25 × 170 | **0.788** | 1.60e7 | 1.05e8 / 1.13e8 | 128.05 | 25/25 | 061128-3edc |
| lane 3dfdb21 device hints, same point | 4096 / 16384 | 25 × 170 | 0.429 | 2.93e7 | 5.71e7 / 6.14e7 | 128.05 | 25/25 | 061300-a452 |
| **lane a440565, l=16384 — the lane on 6babe27's protocol** | 16384 / 65536 | 7 × 682 | **0.190** | 6.63e7 | 2.53e7 / 2.72e7 | 128.54 | 7/7 | 072012-01ac |
| main 02c3321 + bc671b0 (+6babe27 enc), sequential | 16384 / 65536 | 7 × 682 | 0.126 | 9.99e7 | 1.68e7 / 1.80e7 | 128.54 | 7/7 | 075645-c04d |
| main 02c3321 + bc671b0 (+6babe27 enc), `--pipeline 3` | 16384 / 65536 | 7 × 682 | 0.078 | 1.61e8 | 1.04e7 / 1.12e7 | 128.54 | 7/7 | 075807-8036 |
| main 9d35c4e + lane 69a3b04 (+6babe27 enc), sequential | 16384 / 65536 | 7 × 682 | 0.113 | 1.11e8 | 1.50e7 / 1.62e7 | 128.54 | 7/7 | 092817-6220 |
| **main 9d35c4e + lane 07c3039 (+6babe27 enc), `--pipeline 3` — HEADLINE** | 16384 / 65536 | 7 × 682 | **0.062** | **2.03e8** | **8.25e6 / 8.87e6** | 128.54 | 7/7 | 093520-244b |
| same, `--pipeline 4` | 16384 / 65536 | 7 × 682 | 0.061 | 2.06e8 | 8.14e6 / 8.74e6 | 128.54 | 7/7 | 093832-4eab |
| same, `--pipeline 5` | 16384 / 65536 | 7 × 682 | 0.060 | 2.10e8 | 7.99e6 / 8.57e6 | 128.54 | 7/7 | 093936-0e3e |
| same, l=8192 `--pipeline 4` | 8192 / 32768 | 13 × 341 | 0.083 | 1.52e8 | 1.10e7 / 1.18e7 | 128.11 | 13/13 | 094026-27ab |
| DIAGNOSTIC (not a table row): same, **B = 4092** (6 × 682, no tail), `--pipeline 3` | 16384 / 65536 | 6 × 682 | **0.053** (0.053 / 0.053 / 0.051) | 2.39e8 | 7.02e6 / 7.54e6 | 128.09 | 6/6 | 100411-93a9 |

Non-ZK (`NON_ZK_PROOF_DIAGNOSTIC`, same pod): main 6babe27 l=4096 **0.807** (070527-cfe9, 25/25 Rust, 128.23 bits) → lane a440565
l=16384 **0.158** (071925-be77, 7/7) → main 9d35c4e + lane `--pipeline 3` **0.054** (100446-5ef7, reps 0.054 / 0.057 / 0.055, 7/7 Rust,
128.05 bits; two earlier runs 093332-a522 0.055 and 093904-5bbd 0.067 — the latter's reps 0.054 / 0.067 / 0.081 are the ±15 %
spread of a host-bound 60 ms pass, §5.3 / §6). Non-ZK ≈ 0.9× int-ZK at the pipelined point: the masks are hidden under the pipeline.

The spec's 1.636 s predates hostphase's merge (main 6babe27 already has the fused witness kernel; witness 0.900 → 0.014). On
this pod: main 6babe27 0.788 → lane 0.190 (4.1×: device hints 0.410 → 0.011, operating point l=16384 0.429 → 0.190) → with
hp2-host's protocol (9d35c4e) and the fp4 runner pipelined 0.062 (a further 3.1×; **12.7× vs main 6babe27 on the same card, 26×
vs the spec's 1.636**). Target ≤ 0.5 s met at every point from the first lane row on. Depth 3 → 5 is flat (0.062 / 0.061 / 0.060):
the pass is bound by the main thread's launch + sync work (§6: GPU kernels 47 ms per pass over 3 streams, main thread busy 54–70 %
of the wall), so deeper pipelines only add VRAM (3.3 → 4.8 GB peak); the 4-VU tail sub-batch costs ~23 % of the row.

## 0b. Frozen main 64c00bd (lane merged through 07c3039 + enc-hopper's CF_GLOBAL encoder af3b7de) — second pod, 11:04–11:09Z

The "yours vs main" rows above were measured on integration trees (main 9d35c4e + lane commits + the 6babe27 encoder). After the
10:30Z freeze I re-created `vy-fp4-fast` (RunPod `75dww7vv03yxn2`, again an RTX 5090 reference part on an **AMD EPYC 7543** host —
the same host family as every row above; `OMP_NUM_THREADS=12`) and ran the frozen tree unmodified, 4096 VUs, l=16384, 3 reps,
`--warmup-subs 7`, dumps on, Rust `ligero-verify batch --target-bits 128` on rep 1 on the pod:

| frozen main 64c00bd, EPYC 7543 host | reps (prove wall) | t.total s | hints / encode / merkle / tests / openings (median rep) | peak dev | Rust rep 1 | run |
|---|---|---|---|---|---|---|
| int-ZK, `--pipeline 3` | 0.066 / 0.066 / 0.065 | **0.0656** | 0.0072 / 0.0046 / 0.0036 / **0.0461** / 0.0038 | 2.85 GB | 7/7, batch ACCEPT 2^-128.54 | 110354-7d03 |
| int-ZK, **default `--pipeline 4`** (main's default) | 0.058 / 0.057 / 0.059 | **0.0580** | 0.0043 / 0.0038 / 0.0029 / **0.0440** / 0.0022 | 3.50 GB | 7/7, ACCEPT 2^-128.54 | 110613-2500 |
| non-ZK, `--pipeline 3` | 0.061 / 0.066 / 0.062 | **0.0602** | 0.0046 / 0.0031 / 0.0035 / **0.0437** / 0.0043 | 2.62 GB | 7/7, ACCEPT 2^-128.05 | 110652-bd38 |
| int-ZK, sequential (`--pipeline 0`) | 0.093 / 0.113 / 0.115 | **0.1121** | hints 0.010 | — | 7/7, ACCEPT 2^-128.54 | 110843-2710 |

So on frozen main, same host family as the 6babe27 baseline row (0.788 s, 061128-3edc): **0.058 s int-ZK at the default flags =
13.6× vs main 6babe27 on the same SKU/host, 28× vs the spec's 1.636 s**; sequential 0.112 (vs 0.113 on the int tree — the
encoder fix is worth ~1.5 ms/pass here, the pass is host-bound); non-ZK 0.060. Tests = 70–76 % of every pipelined row, as in §6.

**Artifacts: NOT archived.** The numbers above are transcribed from the runs' `stdout.log` / `result.json` read over ssh at 11:09Z
(the `rep k:` lines, `t.total`, `split.*`, `mem.peak_device_bytes`, and the Rust batch verdicts, all in `evidence/int_series9.log`);
`research data pull` at 11:20Z found the pod gone (`GET /pods/75dww7vv03yxn2 -> 404`, ssh refused): the coordinator terminated
`vy-fp4-fast` at ~11:10–11:25Z on reading "10:45Z, final" in this note (their insert in §7) — **my error: I re-created the pod at
10:48Z without first writing that into the note**, and §7 still said "terminated 10:43Z". No `result.json` / dumps / `art:` ids
for these four rows, so they are **not contract rows**; use them only as the same-host-family cross-check they were meant to be.
**The archived frozen-main row is lane dev-5090's** (`~/.research/notes/lanes/dev-5090/20260923T1030Z-report-dev-5090.md` §0):
`r20260923-110113-b79a` = `art:318eed1c…`, live-verified, contract-valid, **0.0714 s sequential under `--verifier` (0.0685 local),
`--pipeline 4` 0.039 s local coins** — on a **Ryzen 9 9950X** host (Zen 5, ~1.5× the single-thread speed of the EPYC 7543), which is
exactly what a host-bound pass rewards (§6). Same tree, same l, same 7 × ≤ 682 layout, same 128.54 bits.

## 1. What changed (all under `backends/direct/ligero`; owned files only)

| file | change |
|---|---|
| `fp4/hints_device.py` (new, 3dfdb21) | the verifier's decode (`public_vectors_fp4`) and the honest hint rule (`unit_hints`) as torch int64 over the l columns on the device; `HintsDevice` = one captured CUDA graph per (system, l[, pipeline slot]) with static uint8 operand buffers; `_bit_length` by binary search (no host sync); bit-identical to numpy (`hints_device_test.py`: every edge family, the bench instances in chain layout, graph capture asserted, 1e5 random units on CPU). |
| `fp4/chain.py` | `FP4ChainRunner(hints="device"|"numpy")`; `_unit_arrays` vectorised assembly, uint8 for the device generator (every word validated as a byte before the cast, before the clock; a440565); **bc671b0**: `marshal` (once per sub-batch per run, cached on the VU tuples' identity — relchain's key — the bundle keeps them alive), `_hints` (decode + hints, `pub` filled in place), `_prove_stages` (→ `protocol.prove_stages` with `hints_fn`, one `HintsDevice` per pipeline slot), `prove_vus` (= run the generator when `_STAGED`, else `prove` as before), `prove_vus_many` (→ `pipeline.prove_many`, coins drawn per sub-batch as it starts, in order); `bench_vu_fp4 --pipeline N` (timed reps interleaved N-deep), `--warmup-subs N` (ba9c73a), `software.backend.{hints,pipeline}`, the live-verifier `set_statement` hook carried; `_verify_dumps`' stale "Rust cannot verify fp4" evidence string replaced. **69a3b04**: the contract row is the rep with the median wall (its phases; per-phase medians kept in `medians`) — with `--pipeline` the phase times are shares of a fluctuating pass wall and per-phase medians across reps summed to 1.4–3.6 % more than the median total (contract "double-counted" reject on 091019-38d8 / 091111-9945 / 091204-6154); `t.zk_additional = 0` in non-ZK (the lap is an empty event pair, 12 µs, and the contract rejects any ZK time in `NON_ZK_PROOF_DIAGNOSTIC`). **07c3039**: the pipelined warm-up is a full pipelined pass — main 9d35c4e's commit / tests graphs are captured per stream AND per (l, n_vus), so the 4-VU tail sub-batch must be met on its slot before the clock: with only the first `depth` sub-batches warmed, timed rep 1 paid 0.15–0.23 s of captures (093153-c519: 0.238 / 0.062 / 0.067; 07c3039: 0.062 / 0.062 / 0.075). |
| `run.py` | `--fp4-hints device|numpy` (gate-vu / bench-vu), `--warmup-subs N` (bench-vu). |
| `chain.py` | comment fixed (was "< 2^31 < p"; 2^30 < p < 2^31); `check_component`: 1 ≤ bits ≤ 30, lo + bits ≤ 32 (the Rust rule), enforced in `end_terms`. |
| `serialize.py` | `read_system` v2 branch: 1..3 components through `check_component` — a malformed `ligero-system/v2` is refused at parse. Proof writer untouched. |
| `relchain.py` | manifest dict lines only: `coins_bytes`, `coins_sha256` per proof (D7). `vu.py:639` (BF16 dumps) has the same gap — not mine, flagged. |
| tests | `fp4/hints_device_test.py`; `chain_test.py::test_check_component_is_the_rust_rule`; `fp4/relation_test.py::test_system_v2_rejects_malformed_component_widths`. |

## 2. Attribution (per 4096 VUs, int-ZK unless marked, this pod; `split.*` from result.json; seconds)

| run | tree | l | N | total | hints | witness | encode | merkle | tests | openings | zk_masks | t.serialization | peak dev GB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 061128-3edc | main 6babe27 | 4096 | 25 | 0.788 | **0.410** | 0.014 | 0.052 | 0.014 | 0.202 | 0.055 | 0.018 | 0.077 | 0.34 |
| 061300-a452 | lane 3dfdb21 | 4096 | 25 | 0.429 | **0.035** | 0.012 | 0.052 | 0.015 | 0.211 | 0.065 | 0.017 | 0.087 | 0.34 |
| 061823-38a5 | lane 3dfdb21 | 8192 | 13 | 0.268 | 0.024 | 0.007 | 0.029 | 0.010 | 0.135 | 0.032 | 0.010 | 0.054 | 0.67 |
| 061902-1209 | lane 3dfdb21 | 16384 | 7 | 0.228 | 0.027 | 0.005 | 0.016 | 0.009 | 0.112 | 0.028 | 0.006 | 0.051 | 1.33 |
| 071655-984d | main 6babe27 | 16384 | 7 | 0.609 | **0.432** | 0.005 | 0.017 | 0.009 | 0.094 | 0.019 | 0.006 | — | 1.27 |
| 072012-01ac | lane a440565 | 16384 | 7 | **0.190** | 0.011 | 0.004 | 0.015 | 0.009 | **0.095** | 0.021 | 0.005 | 0.045 | 1.33 |
| 071746-aa14 | lane a440565, `--warmup-subs 7` | 16384 | 7 | 0.210 | 0.018 | 0.004 | 0.016 | 0.009 | 0.105 | 0.027 | 0.006 | — | 1.33 |
| 071925-be77 | lane a440565, **non-ZK** | 16384 | 7 | 0.158 | 0.010 | 0.004 | 0.009 | 0.008 | 0.082 | 0.017 | 0 | — | 1.33 |
| 070527-cfe9 | main 6babe27, **non-ZK** | 4096 | 25 | 0.807 | 0.485 | 0.014 | 0.007 | 0.014 | 0.189 | 0.076 | 0 | — | 0.32 |
| 075645-c04d | main 02c3321 + bc671b0, 6babe27 enc, sequential | 16384 | 7 | 0.126 | 0.010 | 0.002 | 0.013 | 0.008 | **0.075** | 0.011 | 0.003 | — | 1.21 |
| 075840-02d0 | same, `--pipeline 2` (shares of the wall) | 16384 | 7 | 0.094 | 0.006 | 0.001 | 0.007 | 0.005 | 0.068 | 0.005 | 0.001 | — | 1.96 |
| 075807-8036 | same, `--pipeline 3` | 16384 | 7 | 0.078 | 0.005 | 0.001 | 0.006 | 0.004 | 0.058 | 0.004 | 0.001 | — | 2.88 |
| 075912-0bce | same, l=8192, `--pipeline 3` | 8192 | 13 | 0.121 | 0.007 | 0.001 | 0.006 | 0.004 | 0.089 | 0.013 | 0.002 | — | 1.45 |
| 075257-ca8b | main 02c3321 + bc671b0 with main's encoder, sequential | 16384 | 7 | 0.372 | 0.015 | 0.002 | **0.203** | 0.008 | 0.103 | 0.010 | 0.021 | — | 3.33 |
| 092817-6220 | main 9d35c4e + lane 69a3b04, 6babe27 enc, sequential | 16384 | 7 | 0.113 | 0.012 | 0.001† | 0.014† | 0.008 | 0.063 | 0.010 | 0† | 0.010 | 1.30 |
| **093520-244b** | **same + 07c3039, `--pipeline 3`** | 16384 | 7 | **0.062** | 0.006 | 0† | 0.006† | 0.004 | **0.043** | 0.003 | 0† | 0.003 | 3.31 |
| 093832-4eab | same, `--pipeline 4` | 16384 | 7 | 0.061 | 0.005 | 0† | 0.005† | 0.003 | 0.046 | 0.002 | 0† | 0.002 | 4.07 |
| 093936-0e3e | same, `--pipeline 5` | 16384 | 7 | 0.060 | 0.005 | 0† | 0.006† | 0.003 | 0.043 | 0.002 | 0† | 0.002 | 4.82 |
| 093332-a522 | main 9d35c4e + 69a3b04, **non-ZK**, `--pipeline 3` | 16384 | 7 | 0.055 | 0.006 | 0† | 0.005† | 0.004 | 0.036 | 0.005 | 0 | 0.005 | 3.04 |
| 094026-27ab | same + 07c3039, l=8192, `--pipeline 4` | 8192 | 13 | 0.083 | 0.005 | 0† | 0.004† | 0.003 | 0.066 | 0.004 | 0† | 0.004 | 2.04 |
| 100446-5ef7 | same + 07c3039, **non-ZK**, `--pipeline 3` (2nd run) | 16384 | 7 | **0.054** | 0.005 | 0† | 0.005† | 0.004 | 0.036 | 0.004 | 0 | 0.004 | 3.04 |
| 100411-93a9 | same + 07c3039, **B = 4092 diagnostic** (no tail), `--pipeline 3` | 16384 | 6 | **0.053** | 0.005 | 0† | 0.005† | 0.004 | 0.035 | 0.003 | 0† | 0.003 | 3.31 |

† main 9d35c4e's commit graph (820dc9d) runs witness kernel → masks → encoder as one captured graph: its time lands in `encode`,
the `witness` / `zk_masks` laps are empty. Rows measured on the integration trees are throwaway commits (reproduce = main at the
stated sha + `lane/fp4-fast` fp4 files + 6babe27 `encode_simt.py`).

Where the 0.190 s went (profile_fp4.py, steady state per 682-VU sub-batch on 6babe27's protocol): tests 13.9 ms (tests_w
**8.2** = the SHAKE-256 challenge squeeze on the host while the GPU idles, tests_chain 3.3, tests_quad 2.5) + statement 3.4
+ hints 3.4 + openings 2.9 + encode 2.7 + merkle 1.2 + zk_masks 1.1 + witness 0.7 = 25.9 ms; 7 × 25.9 = 0.181. The fp4-specific
part is now 4 ms of it (hints + witness); the rest is `protocol.py` (hp2-host): a1f199d (NTT graphs, statement digest off-thread,
hot squeeze worker) takes the sequential fp4 pass to 0.126, 9d35c4e (commit + tests graphs) to 0.113, and the pipeline hides the
squeeze: **0.062 at depth 3 = 8.9 ms per sub-batch of wall**; the rescaled `tests` share (70 %) is waiting time, the tests kernels
are ~1 ms per sub-batch (§6). Non-ZK is 0.83×
of int-ZK sequentially and ≈ 1× pipelined.

## 3. Evidence

**Bit-exactness (protocol-identical changes, same operating point).** `evidence/scripts/bitexact_fp4.py` (hostphase's harness
for the fp4 runner: seeded SHAKE stream for `os.urandom` → the runner's step-0 coins and the prover's mask keys; uuid4 on its
own counter because torch.compile draws one per compiled graph; `--pipeline N` resumes the seeded stream after the slot warm-up).
Round 1 (l=4096, 3 × 170 VUs, seed 7): main 6babe27 vs lane 3dfdb21 — int-ZK **10/10** files identical, non-ZK **10/10**
(`evidence/bitexact/`). Round 2 (l=4096, 6 × 170 VUs, seed 11, `evidence/bitexact2/`): main 6babe27 vs lane a440565 (uint8
marshalling) **19/19** int-ZK + **19/19** non-ZK; vs the integration tree 1986953 (main 02c3321 + bc671b0's runner) sequential
**19/19 + 19/19**; vs the same tree **`--pipeline 3`** **19/19 + 19/19** (system.bin + sub_00..05.{stmt,proof,coins}). In-process:
every `check=True` sub-batch asserts device hints == numpy hints and device public rows == numpy decode. 69a3b04 / 07c3039 change
no prover code (bench accounting and warm-up only). **Round 3** (same seed 11 / 6 × 170 VUs / l=4096, `evidence/bitexact3/`): the
headline tree 7c3b157 (main 9d35c4e's commit + tests graphs + this lane's runner, 6babe27 encoder) vs main 6babe27 — sequential
**19/19 + 19/19**, `--pipeline 3` **19/19 + 19/19** (int-ZK + non-ZK). Every fp4 transcript in this note is byte-identical to
main 6babe27's under seeded coins and mask keys.

**Rust.** `ligero-verify batch --system system.bin --dir rep1 --target-bits 128` (built from main 6babe27 on the pod) on every
row's rep-1 dumps, **32/32 rows accepted**: main l=4096 25/25 (128.05 bits), lane l=4096 25/25, l=8192 13/13 (128.11), l=16384 7/7
(128.54) on every l=16384 row, l=32768 4/4 (128.43), l=65536 2/2 (128.30), l=131072 1/1 (128.05), non-ZK rows 25/25 (128.23) and
7/7 (128.05); all `system_pinned: true, pinned_relation: fp4-nvf4`, `python_agree` n/n. The pin is per system; l is read from
the statement — no bug at any new l. `evidence/<run>/proofs/rust_batch_rep1.json`.

**Pytest / gates.** r20260923-065143-664b (lane 063c607, `OMP_NUM_THREADS=12`): `pytest backends/direct/ligero` **70 passed, 1
skipped**; gates fp4-nvf4 device (256 VUs, 60 row / 48 unit negatives), fp4-nvf4 --zk, fp4-nvf4 --fp4-hints numpy, bf16-ampere,
bf16-hopper, bf16-hopper --zk, fp8-hopper, fp8-ada, bf16-hopper --impl legacy: **9/9 rc=0**. r20260923-085527-380c (**lane bc671b0**):
70 passed / 1 skipped, the same **9/9 rc=0** (the `--pipeline 3` bench smoke exits 2 there: 6babe27's `run.py` has no `--pipeline`,
expected). r20260923-082121-7a8b (**integration 1986953** = main 02c3321 + bc671b0 + 6babe27 encoder): **118 passed / 1 skipped**
(220 s), **10/10 rc=0** — the 9 gates + a `--pipeline 3` int-ZK bench of 1024 VUs with dumps, `validation: passed`. r20260923-100554-bff5
(**the headline tree 7c3b157** = main 9d35c4e + lane 07c3039 + 6babe27 encoder): **122 passed / 1 skipped** (195 s), **10/10 rc=0**
(the 9 gates + the `--pipeline 3` bench smoke, `validation: passed`).

**Contract.** 32 rows: `contract.validate == []` on 29; `tables.reject_reasons(NVFP4_SM120, B-Ligero)` = only "not independently
verified" (the non-ZK rows additionally "proof_class NON_ZK_PROOF_DIAGNOSTIC is not B-Ligero's declared class", as intended for
diagnostics). The 3 exceptions are the first pipelined series on main 9d35c4e (091019-38d8, 091111-9945, 091204-6154): the
bucket-sum reject described in §1 (69a3b04) — superseded by the round-3 rows, kept in fp4-fast-v2 as measured. Labels `--by fp4-fast
--ref <run>` on every result (campaign r21-fp4-fast, hardware, relation, l/n/subbatches/per_proof_vus, soundness, R_proved,
overhead, `label=`, `note=` with host CPU / VRAM / peak / load / the self-check verdicts); no `verified=` labels. Snapshots:
**fp4-fast-v1 = `art:73db01f790a802743009b55dede3624acf7babe4f2305240a9d9232195dcd4e2`** (9 results + 9 run-files: main 6babe27 vs lane,
l ∈ {4096, 8192, 16384}, non-ZK), **fp4-fast-v2 = `art:91546081813e88515003adf8bce28ecd13fe9456dac13e617aa1e8236a2a47ec`** (12: the
l ≥ 32768 sweep, the integration-1 rows incl. the encoder diagnostic, the first main-9d35c4e series), **fp4-fast-v3 =
`art:084a27df9009eea72854bff2901244d754158c3cd0794ff22c2f38ba048394e8`** (9: the final rows on main 9d35c4e — sequential, depth 3/4/5,
non-ZK, l=8192 depth 4), **fp4-fast-v4 = `art:519e4999fdf2282bcb7e416dc2b087140584a8048b04290ba8b1ab0aa603c307`** (2: the B = 4092
no-tail diagnostic — rejected from the tables as "B is 4092", by design — and the second non-ZK depth-3 row). 32 rows in all, 30
at B = 4096. Every result / run-files artifact carries rep-1 dumps (`proofs/system.bin`, `manifest.json` with
`coins_sha256`, `rep1/sub_NN.{stmt,proof,coins}`, `rust_batch_rep1.json`). R2: `research data push --pending` after each round,
last 52/52 preserved at 10:12Z (the late pair pushed after labelling).

## 4. Operating-point sweep (item 2; lane, int-ZK, 4096 VUs, 3 reps; l ≥ 32768 at a440565 with `--warmup-subs = N`)

| l | n | t | D | VUs/sub-batch | N | mem.peak_device_bytes | t.total s | R_proved | bound_bits (union over N) | Rust | run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4096 | 16384 | 197 | 6 | 170 | 25 | 0.34e9 | 0.429 | 2.93e7 | 128.05 | 25/25 | 061300-a452 |
| 8192 | 32768 | 195 | 6 | 341 | 13 | 0.67e9 | 0.268 | 4.69e7 | 128.11 | 13/13 | 061823-38a5 |
| **16384** | 65536 | 195 | 6 | 682 | 7 | 1.33e9 | **0.228 → 0.190 (a440565)** | 6.63e7 | 128.54 | 7/7 | 061902-1209 / 072012-01ac |
| 32768 | 131072 | 193 | 6 | 1024 (`--batch 24576`) | 4 | 7.2e9 | 0.449 | 2.80e7 | 128.43 | 4/4 | 073700-a2a5 |
| 65536 | 262144 | 191 | 6 | 2048 | 2 | 14.4e9 | 0.482 | 2.61e7 | 128.30 | 2/2 | 073736-cbf0 |
| 131072 | 524288 | 189 | 6 | 4096 | 1 | 28.8e9 | 0.452 | 2.79e7 | 128.05 | 1/1 | 074039-3168 |

Chosen: **l = 16384**. Above it the 6babe27 encoder leaves its SIMT path (4 l B of shared memory > 99 KB → torch NTT: encode
0.015 → 0.24–0.26 s) and the Python verifier's host work explodes (20 s per rep at l=65536); the union bound is not the limiter
(bits rise as N falls). Pipelined (main 9d35c4e): l=16384 depth 3/4/5 = 0.062 / 0.061 / 0.060, l=8192 depth 3 = 0.121 (02c3321) /
depth 4 = 0.083 — l=16384 stays the point. 4096 VUs do not divide into 682s: the 7th sub-batch carries 4 VUs at full l (§6.2).

## 5. Spec notes

1. The spec's baseline (1.636 s, witness 0.900) predates hostphase's merge; main 6babe27 on the same pod is 0.788 s. Both are in
   §0 so the attribution is honest: hostphase took 0.85 s, this lane 0.60 s on 6babe27's protocol (0.40 hints, 0.20 operating
   point), hp2-host's protocol + this lane's pipelined runner a further 0.13.
2. Native peak in the contract for this profile is 1.676e15 FLOP/s (`rate.native_peak_flop_per_second`), not 1.8e15; §0 gives both.
3. The fp4 bench's per-rep verifier pass (0.5 s of host work between timed reps) cools the GPU; `--warmup-subs 7` did not
   remove the spread (0.190 vs 0.210 on two runs). Pipelined 60 ms passes have a ±15 % rep spread (0.054–0.081); the median of 3
   is reported, the per-rep walls are in stdout.log. A 5-rep or back-to-back (no verifier between reps) mode would tighten it.
4. `rust_ligero_verify` in `validation.evidence.dumps` said "cannot verify this relation" (fp4-proof's text, false since
   ligero-verify-fp4) in every fp4 row so far, including the 9 in fp4-fast-v1; fixed in bc671b0 — the rows' Rust verdicts are in
   their labels and `rust_batch_rep1.json`.
5. hp2-host's `--pipeline` help text says "registered relations"; after the rebase fp4-nvf4 honours it too.
6. Contract vs pipelining: with `--pipeline`, hp2-host's `_rescale` makes phase times shares of the pass wall, so per-phase
   medians across reps need not sum to the median total (69a3b04 reports the median rep instead). relchain / vu.py rows with
   `--pipeline` will hit the same "double-counted" reject whenever reps differ by > 1 % — worth a look by hp2-host.
7. `NON_ZK_PROOF_DIAGNOSTIC` rows on main 9d35c4e report `t.zk_additional = 1.2e-5` (the empty `zk_masks` lap) and the contract
   rejects any non-zero value: clamped in the fp4 bench (69a3b04); relchain's non-ZK rows may need the same.
8. GPU clocks were not pinned on the pod (not attempted; fp4-proof's rows were not either) — the rows are at the card's boost
   behaviour.

## 6. Anatomy of the 62 ms pipelined pass (10:00–10:15Z, `evidence/pipestats/`, `evidence/scripts/pipestats_fp4.py` on tree 7c3b157)

Measured on the headline configuration (l=16384, 7 sub-batches, depth 3, int-ZK), 4–6 passes each:

* **Not GPU-bound.** `torch.profiler` over one pass: GPU kernel self time **46.8 ms** spread over 3 streams vs a 78 ms profiled /
  62 ms unprofiled wall; top kernels per pass: `rs_encode_ligero` 8.5 ms (×14), `blake3_chunks` 7.1 (×119), `lincomb_u64_D6` 2.7,
  `boolcomb_rows_u32_D6` 2.1, `quad_u32_D6` 1.9, `witness_program` 1.3 — the tests chain is **~7 ms per pass (1 ms per
  sub-batch)**, not the 70 % the rescaled `t.arithmetic` share suggests (the share is wall-proportional: it is mostly *waiting*).
  Alongside: ~1,500 small eager launches per pass (`triton_poi_fused_cat_0` ×336, `FillFunctor<long>` ×350, `direct_copy` ×350,
  `remainder` ×497 ≈ 200 per sub-batch outside the graphs).
* **Host-bound on the main thread.** `pipeline.LAST_STATS`: main thread busy **30–48 ms per pass (54–70 % of the wall)**, blocked
  21–28 ms; `cudaEventSynchronize` 13.8 ms + `cudaGraphLaunch` 8.4 ms + `cudaMemcpyAsync` 2.4 ms of main-thread time per pass.
  Stage 0 (marshal + hints + commit launch) 14–24 ms per pass, stages 2–4 (tests / openings) 5–14 ms each.
* **Not squeeze-bound.** Replacing hp2-host's single `HotWorker` by 3 / 4 / 5 round-robin hot workers (diagnostic monkeypatch,
  `--squeeze-workers`, libcrypto XOF GIL-free): walls unchanged (55–84 ms) and the event-measured `tests_w` still 13–20 ms per
  sub-batch — `tests_w` is the wait on the commit → root → challenge → tests chain of *other* sub-batches, not on SHAKE.
* **Not GC.** `gc.disable()` around the passes: −3 ms (5 %), the pattern below unchanged.
* **The 4-VU tail sub-batch costs ~23 % of the row.** (i) it is a full l=16384 sub-batch on the GPU (event-measured 33–41 ms vs
  46–48 for a full one: the cost is per (m, l), not per VU); (ii) it makes *every other pass* ~10 ms slower (odd passes 64–71 ms,
  even 55–60; +8 ms of main-thread time in stages 3–4) — with **4092 VUs (6 × 682, no tail) the pass is 52–56 ms and the
  alternation disappears**; 4774 VUs (7 full sub-batches) is 60–75 ms. Not re-captures: counting `torch.cuda.CUDAGraph` constructions / resets,
  `_TestsStatic` rebuilds and `Slot.pinned` regrowth per timed pass gives **0 / 0 / 0 / 0** (`pipecaptures.log`); the extra
  time is main-thread Python/launch time in the tests and openings stages on the passes where the tail lands on a slot whose
  previous sub-batch was full-size (hypothesis: torch.compile guard re-evaluation / allocator behaviour on the (l, n_vus) shape
  flip — `triton_poi_fused_cat_0` is compiled code, ×48 per sub-batch). The runner's own per-slot state (`HintsDevice`,
  `marshal`) is shape-independent. Either way, no tail = no alternation (100411-93a9: ±2 %).

## 6b. Next hypotheses (ranked)

1. **Tail sub-batch at its own l** (fp4 runner + a contract decision) — floor measured, first attempt a NEGATIVE result:
   B = 4092 (no tail) proves in **0.053 s** (100411-93a9, reps 0.053 / 0.053 / 0.051, −15 % vs 0.062, spread ±2 %). The naive
   version (84b320f: the 4-VU tail at `R.layout`'s smallest l = 256, opt-in `--tail-l natural`) measured **0.688 s** non-ZK
   (r20260923-103815-0693, `art:1d4ca187…`): the l = 256 proof runs off the SIMT / graphed paths (10× slower than the tail it
   replaces), and **Rust rejected the batch**: union bound 2^-127.98 over 7 (the l = 256 proof has 130.43 bits vs 130.86 at
   l = 16384; non-ZK l = 16384 alone sits at 128.05) — `python_agree` 7/7 per proof, the Python bench had reported the dominant
   l's bound. Reverted (a2089ac). A safe version needs (a) the bench to compute the mixed-l union and pick the smallest tail l
   that clears the target (l = 2048–4096 will), (b) a table convention for two `rs_l` / `per_proof_vus` values per row, or the
   NVFP4 row defined at B = 4092. Also a live demonstration that `ligero-verify batch` reads l per statement and enforces the
   union across mixed l (spec item 2's question).
2. **Main-thread launch work (hp2-host, `protocol.py` / `pipeline.py`)**: the ~200 eager kernels + `cudaEventSynchronize` per
   sub-batch; graph the openings / statement assembly and replace the per-stage event syncs by stream waits → the wall approaches
   the GPU's ~47 ms / 3-stream overlap: **~40 ms per 4096 VUs** is the target this evidence supports. Numbers for them above.
3. **Rows** (item 6, census, no code): 1583 rows/unit = 4 group shifters × 193 + out 331 + accterm 226 + pins 141 + acc 49 + anc 20.
   (a) `compile.lookup` range-checks the key AND builds the one-hot: the range check is redundant for the six fp4 tables — 96
   rows/unit (6 %) but in compile.py (relmin-lookup's; their `lookup(range_key=False)` in bb74daa is exactly this lever — fp4 can
   adopt it as `fp4-nvf4-v2` once rebased: new pin via ligero-verify-fp4's torch-free recipe, gate + differential ≥ 1e5). (b) a
   merged `rem < 2^u` via `rem·cpw < 2^bits` is NOT sound without `rem.nonneg` — checked, don't. (c) hinted (q, rem) → one-hot
   selected bit prefix of |mant|: ~280 rows (18 %), new gadget + pin, 3–4 h — deferred. Rows scale encode + blake3 + tests
   (≈ 22 of the 47 GPU ms) linearly; worth ~10 % of the wall while host-bound, more after (2).
4. ~~**Encoder smem fallback on consumer parts** (enc-hopper)~~ — **DONE on main** (af3b7de, `CF_GLOBAL` for the 99 KB parts):
   frozen main 64c00bd on the 5090 encodes 4096 VUs in 3.1–4.6 ms per pipelined pass (§0b) vs 0.203 s on the torch NTT fallback
   (075257-ca8b); the headline row is now reproducible from main alone (dev-5090's r20260923-110113-b79a).
5. **Bench harness**: back-to-back reps (defer the verifier pass to after all timed reps), 5 reps, `gc.disable()` around the timed
   pass (−3 ms measured) → the 60 ms rows at ±5 % instead of ±15 %. Bench-only, no protocol effect.
6. **Hints H2D**: already pinned on the integration tree (`Memcpy HtoD (Pinned -> Device)` ×3 per sub-batch, 0.87 ms per pass);
   nothing left here worth a commit.

## 7. Pod accounting

`vy-fp4-fast` (RunPod `6jdyrmzdz39tif`, RTX 5090, $0.99/h) created 05:48Z, **terminated 10:43Z** (confirmed gone from
`research pods list`): **4.9 pod-hours ≈ $4.90** of the ≤ 6 h budget. Runs: bootstrap ×3 (055148 failed on Python 3.11, 060117
refused for uncommitted changes, 060419 ok), 9 contract rows (round 1), gates ×4 (063025 killed: 118 spinning threads under the
12.75-CPU quota — `OMP_NUM_THREADS=12` since; 065143 lane 063c607, 082121 integration 1986953, 085527 lane bc671b0, 100554 headline
tree 7c3b157 — all green), l ≥ 32768 sweep ×3, integration benches ×6 (tree 1986953) + 4 (21694f8) + 4 (0d33ee7) + 7 (7c3b157)
+ 1 (99956f4, the negative result), plus ssh-driven bit-exactness ×3 rounds / profile / pipestats / Rust-verify scripts. Laptop
disk: 3.5 GB free at the end (`store_evict.py` frees only 0.3 GB — the store is 4 GB, the rest of the disk is not the store);
every pull was small (result + dumps ≤ 30 MB) and every blob is on R2.

**Second pod (11:30Z addendum).** `vy-fp4-fast` re-created 10:48Z as RunPod `75dww7vv03yxn2` (RTX 5090 reference part, EPYC 7543
host, same image) for the frozen-main rows of §0b: bootstrap 104859-e928 / 105013-58.. / 105836-a247, four benches 110354-7d03,
110613-2500, 110652-bd38, 110843-2710 (done 11:09Z, Rust-verified on the pod). **Terminated by the coordinator ~11:10–11:25Z**
(gone from `research pods list` at 11:20Z, before `data pull`; §0b for what was lost). ≈ 0.4–0.6 pod-hours ≈ $0.5. **Lane total
≈ 5.4 pod-hours ≈ $5.40 of the ≤ 6 h budget; no pod of this lane is running** (`research pods list` 11:20Z: only dev-5090's
`quogg3lb20o52b`, not mine, untouched). `machines.toml [machines.vy-fp4-fast]` still names the dead pod id — harmless, left for
the record.

> coordinator 11:25Z: `vy-fp4-fast` idle after your final checkpoint a2089ac; terminated by the coordinator.

> fp4-fast 11:30Z: acknowledged — it was not idle, it was the second pod running the §0b rows (my note did not say so; the
> numbers survive from stdout, the artifacts do not). dev-5090's `r20260923-110113-b79a` is the archived frozen-main 5090 row.
