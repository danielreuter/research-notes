# sp1-formats arithmetic is ready (lane/sp1-formats eb0a77a4, 4096/4096 y bit-exact on all four sets); the dispatch arm shape I need

No action needed before your dispatch lands; this is so the shape fits the first time.

- New files only, in `backends/sp1/common/src/`: `groupsum.rs` (shared allocation-free GroupSum, i64), `tc_fp8.rs`,
  `tc_hopper_bf16.rs`, `nvfp4.rs`; four `pub mod` lines appended at the END of `lib.rs` (nothing above them touched).
- Entry points, each `(x_row: &[u8], w_row: &[u8]) -> Option<word>` (`None` = outside the model, reject):

~~~text
format        entry point                      row bytes (x, W each)                      y
bf16-hopper   tc_hopper_bf16::vu_bytes         3072  (1536 x BF16 u16 LE)                u16  f32_to_bf16(acc), NaN->0x7FC0
fp8-hopper    tc_fp8::vu_hopper                1536  (E4M3 bytes)                         u32  final FP32 accumulator
fp8-ada       tc_fp8::vu_ada                   1536  (E4M3 bytes)                         u32  final FP32 accumulator
fp4-nvf4      nvfp4::vu                        1632  (24 x [64 E2M1 code bytes, 4 UE4M3]) u32  final FP32 accumulator
~~~

- Oracle (native, pod): every VU of each frozen set reproduces its model-recorded y; perturbed y and off-domain
  operands refused. Instances come from `verity_sp1.format_instances` (calls `relchain._instance` /
  `fp4.chain.instances_fp4`, checks the recipe digest against `FROZEN_INSTANCES`), file `sp1-format-instances/v1`:
  header JSON (frozen ref, target, shape, block sha256s) + x block + W block + y block, VU-major.
- What I need from your dispatch: one enum/format-id arm per format calling the entry point above, y width per format
  (2 or 4 bytes), and a host path to load a batch from such a file (or tell me your A100 batch file layout and I will
  write mine in it). I add the arms myself.
- Identity: if the A100 cell is proved before my arms merge, its guest (vk) differs from the one my cells use; fine as
  long as each envelope records its own vk. Tell me if you would rather prove A100 on the merged guest.
