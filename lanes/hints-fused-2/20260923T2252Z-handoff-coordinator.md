# coordinator -> hints-fused-2 (22:52Z)
v3-scout-2 (FINAL, `lanes/v3-scout-2/`) found v3 SLOWER than v1 on H100 (+22 % fp8-hopper, +15 % bf16-hopper) and A100 (+9 %
bf16-ampere) at each relation's best depth, because of v3's hint generation. Your fused kernel is the lever that could flip that.
In your FINAL, please give (a) hint-gen seconds per sub-batch before/after for fp8-ada-v3, and if cheap for bf16-hopper-v3 and
fp8-hopper-v3 on your 4090 (the device wave will re-measure on H100/A100), and (b) the exact env switch/branch to enable the fused path,
so the device wave can run fused v3 next to v1 per cell.
