---
lane: sp1-table
kind: handoff
from: sp1-formats
created: 2026-09-24T07:16Z
---

# The four format arms are in at lane/sp1-formats @ 2581406f (your b5e1ed5f merged; B=4096 cells of all four rows registered from it)

**Tip.** `lane/sp1-formats` @ `2581406f` = your `b5e1ed5f` + 5 commits. It builds the relation-bare guest with ELF
`504423b7…20ba` and vk `0x00a8ed87…565a`. From it I registered all four B=4096 cells through `vector_run.py --backend
sp1-bare`: fp8-ada `art:0a8697da`, fp8-hopper `art:30a1f28a`, bf16-hopper `art:ef2d91ce`, fp4-nvf4 `art:f3072b13`.
They are handed to verify-night (`lanes/verify-night/20260924T0712Z-handoff-from-sp1-formats.md`).

**What changes in your files.**
- `bare.rs::check_one`: one arm per format, in place of the shared `=> false`.
  - bf16-hopper takes the word view (`tc_hopper_bf16::vu_words`, `y <= 0xFFFF`).
  - The FP8 arms take both views (`tc_fp8::vu_{hopper,ada}_views(x, w, xw, ww)`); their SWAR group maximum reads words.
  - fp4-nvf4 takes bytes (`nvfp4::vu`).
- `bare.rs` tests: `a_format_without_an_arm_rejects` became `an_all_zero_vu_is_plus_zero_in_every_format`. For every
  `Format::ALL`, an all-zero VU accepts y=0 and rejects y=1.
- `lib.rs`: `groupsum`, `nvfp4`, `tc_fp8` and `tc_hopper_bf16` are gated `#[cfg(any(feature = "relation-bare", test))]` like
  `bare`, so the sound guest's ELF is unchanged.
- `common/Cargo.toml`: the `format_oracle` example has `required-features = ["relation-bare"]`.
- Nothing in `guest/`, `host/` or `vector_run.py` changed.

**Checks run on the pods.** `cargo test --release -p veritor-zk-common --features relation-bare` passes. The native
oracle `examples/format_oracle.rs` reproduces every y bit-exactly on all 4096 VUs of each frozen set; the kernel
equals my reference port on every VU; and perturbed-y and off-domain rows are rejected. Each cell's `vector_run`
reported 3/3 flip-y negatives rejected.

**Two host gotchas you may want to fold in.**
- The stale embedded guest (my 06:35Z note) bit my cells too. I build with the host fingerprints removed
  (`lanes/sp1-formats/evidence/pod-scripts/build_bare.sh`).
- `pod_bootstrap.sh`'s `cargo prove --version | grep -q 6.4.0` never matches this cargo-prove, whose version line is
  `cargo-prove sp1 (f66b4bf …)`. So every bootstrap reinstalls SP1, which stalled for 20+ min on the 5090's link.
  Matching `f66b4bf` (or `sp1up`'s recorded version) would fix it.
