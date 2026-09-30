---
id: 20260930T2300Z-reply-from-coordinator-hillclimb-overhead-formula
campaign: verity
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde), answering @proofs 3:51 PM PDT (Daniel's hillclimb plots)
---

# How to compute overhead for the GemmCoordinate hillclimb plots

Use the campaign's existing definition, `verity_numerical.bench.contract`, which every Table 1 number already follows, so the plots stay comparable with the ledger. Change only the hardware line.

## (a) The formula

Overhead is one prover-second per native-second, per VU (one `GemmCoordinate_v2{K, DOT}` instance, K MACs = 2K FLOP):

~~~text
overhead = (prover seconds per VU) / (native seconds per VU)
         = (t_prove / VUs) / (2K / peak)
         = peak / R_proved,   where R_proved = 2 * K * VUs / t_prove
~~~

That is `contract.overhead()` / `census.native_seconds_per_instance()`. Per-GEMM 2MNK is the same thing: a GEMM is M×N coordinates of 2K FLOP each.

**Numerator (`t.total` in the contract):**
- All prover buckets: witness, encoding and commitment, arithmetic, lookup, ZK additional, serialization. The host witness build counts; the prover owns it.
- Steady state: a warm session (`WARM=1` / `FLOCK_KEEP_SESSIONS`), statements back to back, divided by accepted VUs. Staging and the circuit build are preprocessing (`fixed.setup_seconds`), reported beside the ratio, not in it.
- **The verifier is excluded** (`verifier.seconds` is its own column).
- C-Flock's `prove_total_s` per statement, divided by VUs per statement (`units_per_statement`), is that numerator.

**Plot a second series too, GPU-held seconds per VU (job seconds / VUs).** Tonight's K=2048 row had prove 1.02 s but about 8.3 s of GPU hold per statement, because the loopback verifier runs in series. The two series diverge by about 8×, and a step that fixes the verifier's hold shows up only in the second. Daniel's plot (3), GPU utilization, is roughly their ratio.

**Denominator:** the datasheet dense tensor-core peak of the device for the operand dtype, at **FP32 accumulate**, no sparsity. An FMA counts as 2 FLOP. That is the census hardware line's `flop_per_second`. Peak is the conservative choice, since real kernels run below it.

## (b) M0 v3's 4.80e6×

I couldn't find how that number was computed: nothing in the project store or the notes matches it. If it is prover time over a measured torch bf16 linear on a vCPU basis, its denominator is a measured CPU rate, not a GPU datasheet peak. Convert with:

~~~text
overhead_vs_peak = overhead_measured * (peak / R_native_measured)
~~~

Here `R_native_measured` is the FLOP/s of the torch baseline it divided by (2K × coordinates / baseline seconds), on whatever hardware it ran. Ask the M0 lane for that rate. Without it, the number can't be moved onto the peak basis, and Daniel's plot (1) should not mix the two.

## (c) An RTX PRO 6000 Blackwell Server Edition peak

`census/hardware.json` has no line for it. The only Blackwell entry is `rtx-5090/e2m1`, sourced from the RTX Blackwell architecture whitepaper, Appendix A. I have no sourced figures and am not quoting any.

Before plotting, add `rtx-pro-6000-bse/{bf16,e4m3,e2m1}` lines under `census/README.md`'s sourcing rules, from NVIDIA's RTX PRO 6000 Blackwell Server Edition datasheet or the whitepaper's professional-GPU table. Watch for three things:
- **Accumulate width:** GeForce parts halve FP8/FP16 rates at FP32 accumulate (the census's Ada line notes this). The line must be the FP32-accumulate figure, or say it is assumed, as the L40S line does.
- **Sparsity:** headline "AI TOPS" are usually 2:4-sparse FP4; use the dense figure.
- **Clock:** peaks are at boost clock; say which.

## (d) K values

Take them per datatype, the same set for each:
- **K = 1536:** the frozen campaign target, comparable with every ledger row.
- **K = 2048 and 8192:** Llama-3.2-1B's hidden size and MLP-down width. K=2048 is where tonight's whole-row data is, and K=8192 is @proofs' node-2 item.
- **K = 4096:** the 7-8B hidden size, and the midpoint.
- **Optionally the largest served K, 14336** (Llama-3.1-8B / Mistral-7B MLP down), to show the scaling in K.

Every K is a multiple of 16, as `GemmCoordinate_v2` requires. Hold the tile (`FLOCK_GEMM_TILE`), batch and statement parameters fixed across a step's K values, and record them in each point's fingerprint.
