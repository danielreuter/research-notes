---
cursor:
  subagentId: "bc-43b97b54-095b-53ee-adcb-9385cff11854"
id: 20260930T2240Z-report-proofs-progress-plots
campaign: overnight-sep30
lane: console
kind: report
status: final
repo: danielreuter/verity
---

# What Console Proofs → Progress plots measure

## Where the UI vs the numbers live

- **Console UI** (Progress, All/Prefill/Decode tabs): website repo `apps/docs/` (branch `cursor/console-v2-a491`, e.g. be381be); not in `danielreuter/verity` (`lanes/console/20260930T1910Z-report-console.md`).
- **Panel ids Daniel reads:** `verity/prover-overhead-prefill` and `verity/prover-overhead-decode` (`lanes/proofs/20260930T2209Z-handoff-from-console-progress-questions.md`). Published with `PUT /api/panels/{id}` + `panels:write` (not a research-store kind; `tools/research/.../kinds.py` has no `panel/*`).
- **Metric computation (verity):** draft PR [#554](https://github.com/danielreuter/verity/pull/554), branch `cursor/ov-gemm-slowdown-4d6a` — **not on origin/main**. Files: `backends/flock/pod/gemm_slowdown.py`, `71-gemm-slowdown.sh` (class sweep via `70-class-sweep.sh`).

## What each plot is

| Plot / series | Config id (`ov.config`) | How computed |
|---|---|---|
| Per-matmul overhead | `256x16384x2048`, `256x2048x8192` (prefill); `1x16384x2048`, `1x2048x8192` (decode) | One Llama-3.2-1B fused linear shape: gate_up (N×K = 16384×2048) or down (2048×8192); M = 256 or 1 (`gemm_slowdown.py` CONFIGS / docstring L7–19) |
| Whole model | `llama32-1b.prefill.M256`, `llama32-1b.decode.M1-8` | Sum prover and native over all GEMMs in `phases()`: 16×{qkv,o,gate_up,down} + lm_head (prefill lm_head at M=1); decode sums M∈{1,2,4,8} (`phases()` L45–49; morning note L18–19) |
| Prefill vs decode tabs | panel suffix / phase | Same ratio, split by phase (`CONFIGS` phase field) |
| v1 / v2 / v3 | lines `flock-m0-v1`, `flock-m0-v2`, `flock-m0-v3` | **Campaign prover lines**, not C-Flock protocol versions: v1 = untiled M0; v2 = 4×4 tiles @ K=2048; v3 = tiles + host-witness levers (merged onward) (`lanes/flock-netlist/20260930T1235Z-report-prover-morning-inputs.md` L22–35) |

Overnight table mirrors the same six configs × three lines (`docs/overnight-results.md` §3 L226–249).

## Overhead definition

**overhead = prover_s / native_s** (unit `x-native`), same RTX PRO 6000 (sm_120).

- **Numerator:** from a `GemmCoordinate_v1{K}` class-sweep statement at largest packing: per output coordinate `s_per_coord = (witness_s + prove_total_s) / n`, with pipelined steady-state `full = max(full, witness_prebuilt_s / pipeline_depth)` (`per_coordinate` L85–107). A full GEMM costs `M * N * s_per_coord` (L140–144). Coordinates packed into statements (e.g. 4×4 tiles, m≈35) — **inferred:** one statement time is divided by its coordinate count, then scaled by M×N (not “one statement × statement count” without that division).
- **Denominator:** torch bf16 `F.linear` (cuBLAS), weights rotated past L2 so each call reloads from memory (`native()` L52–82; morning note L18).
- **Not** the frozen ledger’s A100 BF16-peak VU overhead (`bench/plots.py` / Overview) — Progress questions note that mismatch explicitly.

## Feeds

- Campaign `overnight-sep30`; Kueue prover benches on vy-nebius-1.
- Attempt produces `out/slowdown.json` + `result.json`; `point` emits one run per config with measurement `overhead` (L173–186).
- Example runs: v1#8 `r20260930-124807-a26a`; v3 best around `r20260930-181717-b71e` / `r20260930-184956-61fe` (4.8e6 / 1.04e5 whole-model) (`lanes/proofs/20260930T2055Z-handoff-from-flock-netlist-m0-state.md`).
- Dashboard aggregates labeled attempts into series `overhead/<config>/<phase>` (`lanes/overnight-dashboard/20260930T1336Z-report-overnight-dashboard.md`). **Inferred:** that feed (or a sibling publisher) is what fills `verity/prover-overhead-{prefill,decode}` for console Progress; exact PUT mapper not in this checkout.

## Why prefill vs decode

Prefill uses M=256 tokens on layer GEMMs (lm_head M=1, last-token logits). Decode measures M=1,2,4,8 and sums them. That changes GEMM shapes, native cuBLAS time, and how full 4×4 tiles are (decode M=1 underfills a 4-row tile) — hence separate ratios and panels (`gemm_slowdown.py` L9–10; morning note L18–19; flock-v2-design note on tile fill).
