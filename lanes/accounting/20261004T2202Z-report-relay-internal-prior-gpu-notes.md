---
id: 20261004T2202Z-report-relay-internal-prior-gpu-notes
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/prior-gpu-notes.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/prior-gpu-notes.md`, sha256 `47990d8f7d19a001dabf98bb37620bec2858b707e46a24443a24eec355f7e529`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Prior GPU measurements and lessons (from Daniel's previous porep-inference agent)

Pasted by Daniel on 27 Sep 2026, 14:50 UTC. The paste started partway through §1. Paths refer to `~/projects/porep-inference` on Daniel's laptop; the `research/trusted4/` subset is copied under `internal/sources/porep-inference/`, and the rest is being exported.

## 1. Cost model (partial)

Slopes, independent of b up to 64:
- +0.158 R_seq per IMAD-pipe op per byte;
- +0.110 per instruction for balanced ARX code (see the pricing rule below);
- +0.0059 per int8 MAC per byte;
- +1.06–1.34 per extra HBM byte per byte.

Only the first ≈ 2 ops/byte hide behind the weight stream.

**Pricing rule (important).** ARX and keystream code co-issues on both integer pipes (LOP3/SHF on the ALU, IMAD-as-add on the FMA pipe). Price it by the busier pipe's instruction count: the effective cost is about 0.68 of the SASS count (a measured factor of 1.46). Big-integer modular arithmetic is IMAD.WIDE-bound, so price it on IMAD alone. NTT butterflies run at a measured 0.9 T/s (≈ 2 T/s ideal).

Source: `research/trusted4/decoder.md` §3.7–3.10, `research/trusted4/region.md` §9.

## 2. Primitive throughputs (H100)

| Primitive | Measured | Per byte |
|---|---|---|
| IMAD / IADD3 / LOP3 issue | 16.65 / 16.21 / 16.21 T instr/s | — |
| device-to-device copy | 1.51–1.52 TB/s (read and write counted once) | reference |
| cuBLASLt int8 GEMM | 805 T MAC/s (`torch._int_mm` is 16× slower; don't use it) | — |
| bf16 GEMM | 878 TFLOP/s | — |
| ChaCha8 / 12 / 20 keystream, compute only | 4,131 / 2,674 / 1,627 GB/s | ChaCha8 = 6.8 SASS/B (244 ALU + 120 FMA per 64 B) |
| Philox4x32-10 | 5,795 GB/s | 2.75 SASS/B |
| keystream stored to HBM at a 64-byte stride | all limited to ≈ 320 GB/s (half-sector writes) | consume in registers instead |
| sparse gather-XOR, block on-chip, w = 4 / 8 / 16 taps | 865 / 485 / 260 GB/s | taps over HBM: 117 / 60 / 30 GB/s |
| 30-bit Montgomery modMAC (lazy-4 reduction, exact) | 5.69 T/s | — |
| one 2048 / 3072 / 4096-bit Montgomery multiplication (CGBN, whole GPU) | 1.24 / 2.55 / 4.52 ns | 68 / 93 / 124 int32/B |
| injection-ARX DRG decode, (4,6,4), 64 KB blocks | 440 GB/s = 3.42× memcpy time (B200: 483 GB/s, 6.57×) | ≈ 25–30 int32/B |

**Real decoders fused into the GEMM** (R_seq, bit-exact):

| Decoder | b = 1 | b = 8 | b = 32 | b = 2,048 | b = 8,192 |
|---|---|---|---|---|---|
| fmix2 (2-round mixer; not a random oracle) | 1.09 | 1.11 | 1.31 | 1.34 | ≈ 1.2 |
| Philox4x32-10 | 1.17 | 1.17 | 1.40 | 1.34 | ≈ 1.2 |
| ChaCha8 | 1.28 | 1.29 | 1.75 | 1.36 | ≈ 1.2 |
| RSA-2048 e = 3 forward (synthetic vector, 64 int32/B) | 11.6 | 11.7 | 11.6 | 4.3 | 1.45 |

Nothing cryptographically adequate measures below 1.10× at decode batch.

**Not measured; measure these first if P3 uses them:**
- **SHA-256 on the GPU:** ≈ 20–25 SASS/B, ≈ 1–1.5 TB/s compute only (estimate).
- **Keccak-f[1600] / SHAKE:** ≈ 40–55 SASS/B of rate (estimate).
- **BLAKE3:** ≈ 11–12 int ops/B, ≤ 1.4 TB/s (estimate, from Pearl's kernel).
- **A Feistel permutation built from a standard hash** costs roughly (rounds) × (hash cost per byte of round-function input plus output). An 8-round Feistel from SHA-256 or Keccak is on the order of 130–400 int32/B (estimate). That fits only the prefill regime (144 int32/B at 2×), not decode batch. A 2-round heuristic variant is about 4× cheaper. Measure the round function inside the fused kernel, not standalone.

## 3. End-to-end reference numbers (public DRG encoding, shipping point (4,6,4), 64 KB)

| Setting | Result |
|---|---|
| Weights, harness, fused decode→WGMMA, B = 8 / 16 / 32 | 4.52× / 4.38× / ≈ 4.4× (unfused 4.96× / 4.78×) |
| Weights, vLLM 0.28 + FA3 + CUDA graphs, B = 1 at 30K / 118K context | 6.04× / 4.99× (155 → 25.8 tok/s) |
| Weights, vLLM, B = 8, shared prefix / unique | 5.11× / 4.24× at 30K; 2.60× / 2.43× at 118K |
| Weight-decode delta | a flat 32–34 ms per step (14.1 GB at ≈ 0.42 TB/s), independent of engine; the ratio depends only on how lean the plaintext step is |
| KV-only Mooncake session, B = 8 (30 turns, 30K → 118K) | 2.71× (TPOT turn 1: 2.43×, turn 30: 4.74×) |
| Weights and KV both encoded, B = 8 | 3.67× per session (TPOT 5.03× → 6.30×) |
| Prefill, 8K tokens | 1.09–1.11× (phase-1 point); ≈ 1.1–1.2× at 8K+ for the shipping point (derived) |
| Plaintext step anatomy, b = 1 | 28 layers + lm_head ≈ 6.6 ms (lm_head alone 0.36 ms; gate_up 107 µs; down 68 µs) |

## 4. Audit and timing measurements

**Bulk bandwidth audit** (Shacham–Waters linear MAC over random 32 KB sectors of a 70 GB region):
- Reads at 3.09–3.12 TB/s, 97–98% of the sequential ceiling and above D2D memcpy.
- 8–16 KB sectors come within 2–4% of that; 4 KB sectors lose 15%.
- Honest time T = 0.547 / 1.314 / 2.590 ms at X = 1.6 / 4 / 8 GB.
- Idle tail: p99.9 − p50 = 0.09–0.13 ms.

Tail under a serving load (X = 4 GB, p99.9 excess over idle p50):

| Challenge placement | Tail excess | Verdict |
|---|---|---|
| challenge kernel in a separate process | 2.45 ms | fails: it waits out the load's time slice |
| in-process, own stream, plaintext model | 0.37 ms | passes |
| in-process, persistent-grid decode kernels | 1.8–2.4 ms | fails |
| in-process, bounded-CTA kernels (`BPC=2` / fused `auto4` / `auto2`) | 0.34 / 0.17 / 0.11 ms | passes; costs +1.0–1.2% step time |

Off-HBM tiers:
- PCIe Gen5 pinned host memory: 55.5 GB/s by copy engine, 51.3 GB/s for a kernel reading mapped host memory.
- NVLink peer: 450 GB/s, i.e. 15% of HBM bandwidth.
- Enforceable off-HBM fraction: 2.5% at X = 4 GB, 2.2% at 8 GB (derived).

**Raw-block audit** (k = 207 blocks of 32 KB, written into the challenger's buffer over PCIe):
- The honest response is a PCIe transfer: about 15 µs plus kB/52 GB/s, i.e. 6.8 MB in about 0.15 ms.
- p50 / p99.9 / max = 0.164 / 0.216 / 0.579 ms under an HBM-saturating load (30,000 rounds, device clock).
- False-reject runs: 0 late out of 30,000 rounds at Δ = 1.0 ms (k = 207) and at Δ = 1.5 ms (k = 640).
- Under long-lived GEMM kernels the response waits one CTA lifetime (+0.7 ms p50, +1.5 ms p99.9), so it needs Δ = 2–2.5 ms.
- Cost to serving: 0.02% at 1 round/s. By comparison, a MAC over the whole 70 GB takes 22 ms, which is 2.2% of the GPU at 1 round/s.
- **Timing does not separate placements inside the server.** A host-DRAM attacker adds only +5 µs at a 2–5% deficit, and +75 µs with all data in host DRAM. The location claim must come from accounting or the bandwidth audit, not from this deadline.

**Tiny probes** (a single 4–32 KB sector read to pinned host memory, a proxy for RDMA):
- p50 ≈ 10 µs.
- Tail under a memory-bound load: p99.9 = 73 µs, max 266 µs. A strict all-probes-on-time policy needs Δ ≳ 300 µs.

**Adversary sequential speed t_min** (one dependent chain of the 4-round injection-ARX hash):

| Implementation | Per hash |
|---|---|
| H100 thread, latency-tuned | 288 ns (ALU floor ≈ 200 ns) |
| one CPU core, Xeon 8470 | 58 ns |
| ASIC/FPGA | 5–10 ns (estimate) |

Latency doesn't improve with more chains in flight; only throughput does. **Any timed security argument must use the CPU or ASIC figure, not the GPU figure.** Our 32 KB blocks failed the regeneration-versus-deadline check for this reason (a 1.61 ms chain against a 1.81 ms deadline). 64 KB gives 1.75× margin against the decode-kernel chain speed, but only 1.30× against the latency-tuned GPU chain.

Sources: `research/challenger2.md`, `research/protocol2.md`, `research/trusted4/audit.md`, `research/spotcheck3.md` §3.

## 5. Settled negative results (don't re-run)

1. **Tensor-core (int8 `mma.sync`) nonlinear mixer:** 2.3× slower than injection-ARX at equal parameters on H100, and slowest on B200 too. The MMA → transpose → finalizer phases serialize, and it spills at 128 registers. The cost is in the phases around the MMA, not the MMA itself.
2. **Fusing decode into the GEMM** is worth only 9–10% once decode is 92–94% of the kernel. It's worth 1.4–1.5× only with a cheap mixer.
3. **Blackwell doesn't help integer decoders.** B200 HBM is 2.13× faster, but per-SM INT/SMEM throughput is at Hopper rate. Every integer decoder is about 1.9× worse relative to memcpy on B200. The fused WGMMA kernel is sm_90a-only; Blackwell needs a tcgen05 port.
4. **Tile-shared parent patterns (matrix-structured graphs) are unsound** (15–30% leak). Adding degree instead of layers costs more ((3,12,4) > (4,6,4)).
5. **Levers that don't pay:** a plaintext KV working window saves < 1%; TMA bulk copies in the decode kernel are neutral to negative; nibble-FP8 absorb is exact but 1.16× more expensive; speculative decoding improves the ratio only against a non-speculating baseline.
6. **No sound point of the DRG construction reaches ≤ 2.2×** for weights at B ≥ 8, or for weights and KV together.

## 6. Methodology traps

**Baselines and reporting:**
- Measure the plaintext baseline in the same run, and report both shared-prefix and unique-prompt numbers. vLLM's prefix cache changes plaintext decode by 20–40% at B = 8.
- Say which convention you use: additive (decode time plus GEMM time) or fused (inside one kernel). They differ by up to 1.5× at low batch.
- Use the device clock (cudaEvent) for tails; a Python host-clock stand-in doubled the tail.
- Warm up. The GPU clocks down between sparse rounds, which produced a spurious 0.46 ms max.
- vLLM's fused path is near-identical, not bit-identical, to plaintext (fp32 split-K accumulation order differs from cuBLAS). Check bit-exactness on the decoded weights, not on the logits.

**Kernel pitfalls:**
- Check the SASS after every kernel refactor. nvcc 12.4 silently left an unrolled loop rolled (a local-memory frame, −10 to −25%).
- The decode kernel was ALU-latency bound: the pipe was 37% utilized at 1 CTA/SM. Occupancy was the only lever that moved it (1 → 2 → 4 CTAs/SM: 860 → 1,050 → 1,112 GB/s). The 64-register cap binds at 2 CTAs/SM. Bank conflicts cost 5–15% once the mixer is fast.
- Persistent-grid kernels are incompatible with a sub-millisecond challenger; bounded CTAs cost 0–4%.
- A torch strided copy of 15 GB cost 50 ms in prefill. Write the CUDA kernel.

**Measurement setup:**
- Performance counters (`ncu`) have no permission on RunPod. Use SASS instruction counts times the measured issue rates; this matched hand counts and predicted within 20%.
- CGBN needs one binary per (bit width, threads-per-instance) pair, and `flock` on the GPU between sweeps.
- Put the priority parameter first in every sweep. A watchdog once killed a pod mid-sweep and the tail of the run was lost.

## 7. Operations notes for a $100 budget

- **Budget arithmetic.** H100 SXM on RunPod ran $3.29–3.49/h (≈ 28 GPU-hours for $100); B200 $6.79/h; A40 CPU pods $0.49/h. The phase-4 GPU pod did the whole budget-box plus decoder campaign in 4.5 h for $15.9. Run CPU-only work (pebbling solvers, cryptanalysis, GMP) on a CPU pod, not on the GPU pod or a laptop.
- **Pod control:** `terminate` takes the pod id, not the name; by name it returns an error and the pod keeps running. Detach the budget watchdog with a double fork or a new session, or it dies with the tool shell. Run pod setup under `nohup`.
- **Pod environment:** fresh images lack `rsync`. CPU pods are cgroup-capped below the advertised vCPU count (13.6 of 16; 7.65 of 96), so report per-core numbers.
- **File sync hazards:** use a separate pod directory per agent (`rsync --delete` in a shared checkout reverted another agent's files). Pushing local logs overwrote live pod logs. `zsh` aborts an `&&` chain on an unmatched glob, which once silently skipped a launch; check the log before waiting.
- **Reproducibility:** every CSV gets a `.cmd` sidecar with the exact command line.

## 8. Reusable code (porep-inference repo)

| Path | What |
|---|---|
| `research/trusted4/decoder/fused/synth_fused.cu`, `run_region.sh`, `region.py` | synthetic fused decode→GEMM kernel that sweeps int32/int8/extra-byte cost per weight byte across b; produces the budget box |
| `research/trusted4/decoder/budget/imad.cu`, `sass_count.py` | issue-rate microbenchmarks and SASS counting |
| `research/trusted4/decoder/ring/prims.cu` | ChaCha/Philox XOF, NTT, gather-XOR microbenchmarks |
| `research/trusted4/tdpcost/cgbn_powm_bench.cu` | big-integer modexp on the GPU (CGBN) |
| `research/trusted4/audit/` | raw-block audit harness, honest tails, attacker placements, false-reject runs |
| `porep/challenge/`, `porep/bench/challenge_*.py` | Shacham–Waters bulk-MAC challenger kernel; jitter, tier and regeneration benchmarks |
| `porep/kernels/porep_fused.cu`, `porep/model.py`, `vllm_porep/` | fused decode→WGMMA kernel, Qwen2 harness, vLLM quantization-plugin integration |
| `research/spotcheck3/chain_{cpu.c,gpu.cu}` | adversary chain-latency (t_min) benchmarks |
| `infra/runpod_ctl.py`, `infra/pod.sh`, `infra/detach.py` | pod control, budget kill-switch, detached jobs |
