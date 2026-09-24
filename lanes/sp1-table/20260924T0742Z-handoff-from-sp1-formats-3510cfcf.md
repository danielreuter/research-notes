---
lane: sp1-table
kind: handoff
from: sp1-formats
created: 2026-09-24T07:42Z
---

# New tip lane/sp1-formats @ 3510cfcf (faster fp8 and nvfp4 kernels; four cells re-proved from it)

`3510cfcf` = `2581406f` (my 07:16Z tip) + one commit touching `common/src/{groupsum,tc_fp8,nvfp4,bare}.rs` only. Its
relation-bare guest has ELF `48bb5913…` and vk `0x00a42aa3…a599`. Your A100 BF16 arm is untouched, but the vk is shared,
so an A100 cell proved at 3510cfcf would carry this vk.

- `bare.rs::check_one`: the fp4-nvf4 arm now passes both views (`nvfp4::vu_views(x, w, xw, ww)`). The other arms are as
  at 07:16Z.
- The fp8 kernel reads one 64K-entry pair table per product. The nvfp4 kernel works on the word view with a 64K-entry
  scale-pair table. Both tables are `static`, built at compile time. There is no `unsafe` (`forbid(unsafe_code)` holds).
- Checks: `cargo test --release -p veritor-zk-common --features relation-bare` passes (18 module tests, 6 bare tests).
  The native oracle gives 4096/4096 on all four sets, with negatives rejected.

Cells at 3510cfcf: fp8-ada `art:8d9df3a2` (23.53 s), fp8-hopper `art:70e5bd29` (20.74 s), bf16-hopper `art:76d13bb0`
(24.09 s), fp4-nvf4 `art:a8886e22` (7.43 s). They are handed to verify-night at `20260924T0742Z`.
