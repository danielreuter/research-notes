---
lane: agkr-fp8
kind: report
created: 2026-09-24T20:47Z
status: open
---

CHECKPOINT 07a8edd6 (21:07Z) [open] 07a8edd6: fp8-ada 4096 VUs on 4090 passes (t.total ~1.11s, Rust 2/2, 2^-130.19, negatives 4/4 both verifiers); next: recorded 3-rep run + data put --preserve + coordinator handoff, then H100
CHECKPOINT 4e26d864 (20:47Z) [open] 66841d43: A-GKR FP8 circuits (checker v2 adder-side view, packed-word epilogue), BF16 statements byte-identical, 600 random VUs match silicon; 4090 pod vy-agkr-fp8 bootstrapped; dev run fp8-ada 256 VUs running. next: 4096 + negatives

## Design (commit 66841d43, 07a8edd6)

A-GKR at the E4M3 relations reuses lane agkr-table's GPU path (gpu.v2 export / witness / bench_result, prover,
Rust verifier) with checker v2 on the pipeline's **adder-side view**:
`Params(sig=4, exp=4, acc_sig=14, width=14, floor=-139, groups=model.groups, acc_exp=8, op_nan_rule="e4m3")`
(`backends/gkr/gpu/v2/fp8.py::adder_params`). The chained state (s, e_hat, M, z) is the 14-bit adder magnitude; the
FP32 word is `M << 10`. Silicon's lossy rescale of the incoming FP32 word (`M24 >> 10`, zero flag on all 24 bits) is
the identity on every chained state (low 10 bits zero), so no rescale gadget is needed; `check_widths` still refuses a
lossy view. Units are `sum(groups) = 32` products: 48 per VU (ada: 2 groups of 16; hopper: 1 group of 32).

Checker v2 edits (BF16 byte-identical: REAL and hopper-bf16 circuit/epilogue/chain/manifest sha256 unchanged vs
ab9573fd): accumulator-named bounds where the accumulator is meant (LEADNORM clamp/overflow `acc_e_min/acc_e_max`,
Pack `acc_bias/acc_e_min/acc_t_finite`, T_HDR `acc_exp`), T_OP honours the e4m3 NaN rule (only 0x7f/0xff lack rows),
`vb = max(ceil(s_bits/2), -k_lo)` (FP8: s_bits 20, k_lo -13 from the floor clamp -> vb 13; REAL unchanged at 15).

Epilogue (FP8): one row per VU `one, s, e, M, z, ovf[g], sgn[g], y16` with `y16 == Pack.check(state, flags)` at the
adder-side params = the 22-bit packed word `s 2^21 + t 2^13 + (f >> 10)` = `fp8/relation.pack_public(y)` (public
word, < 2^22 < p, every linked component table-determined in the last unit). Column keeps the name `y16` because the
chain binds the public word by that name in `gpu/run.read_chain` and `verifier/src/main.rs`.

Unit sizes: ada 472 columns / 150 queries per unit, epilogue 10 columns; hopper 448 / 139, epilogue 8. Tables tiny
(T_OP 254, SHIFT 8192, TNORM 229376 the largest) vs BF16's 5.1M implicit rows.

Cross-checks: laptop, 612 random VUs x 2 models (zeros, subnormals, max exponents, cancellation) through
`vu_rows_fp8`: every unit's packed state == silicon `tc_dot` accumulator >> 10, every row satisfies its circuit mod p.
Pod: `gpu.v2.witness recipe --relation fp8-ada --vus 64` byte-exact (device generator vs export rows). 256-VU
bench_result (4090): Python 2/2, Rust 2/2 accept, 2^-130.19, contract clean, t.total 0.73 s.

4096 VUs on the 4090 first OOMed in the Ligero opening (a 6.7 GB cupy buffer); 07a8edd6 runs `open_w_qc_eval` in
row blocks of 4096 on < 40 GB parts (block sums mod p: q unchanged; 80 GB parts keep the one-shot path).
