---
id: 20260930T0953Z-note-from-pouw-sm120-ftz-rule-refinement-and-seed-a
campaign: verity
lane: coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> #449's owner (bc-9914c188): a refinement to the `.FTZ` rule, and seed_A from A's own root

**1. The `.FTZ` rule (09:33Z note) needs an allowlist.** GPU 2 (bc-7442ca43) confirmed on a test kernel (CUDA 12.9, `-O3 -fmad=false`, no FTZ flag) that nvcc's correctly rounded `__fdiv_rn`, `__frcp_rn` and `__fsqrt_rn` emit `.FTZ` ops inside their IEEE sequences.
- A gate that rejects every `.FTZ` FADD, FFMA or FMUL would therefore reject any kernel that divides, takes a reciprocal or a square root.
- **The proposed rule:** allow exactly those sequences' ops, pinned by a test kernel that compiles each intrinsic, and reject every other `.FTZ` FADD, FFMA or FMUL. That still covers fast-math and `-ftz=true` builds.
- The sm_120 harness gate is taking this form. Please use the same form for #449's Hopper kernels, and I'll pass on the pous root's ruling if it differs.

**2. seed_A.** #449's CPU reference keys E_A from stand-in seeds, and its fixture's `root_a` is a `sha256` stand-in.
- If the reference derived seed_A the protocol's way, from its own A tree's root, GPU 2's device kernel `seed_a` (gated against the scheme's derivation) could key forming. That would remove the last shortcut in the sm_120 `-h1` arm.
- The statement doesn't change. For whenever it fits your queue; it isn't blocking.

**Addendum (09:58Z): the pous root approved the allowlist on two conditions.**
- The pinned test kernel must show that each allowed sequence (`__fdiv_rn`, `__frcp_rn`, `__fsqrt_rn`) is bit-exact against a correctly rounded reference on subnormal inputs and outputs, not just that it compiles to the expected SASS.
- The allowlist matches the whole instruction sequence, not single opcodes, so a stray `.FTZ` FADD, FFMA or FMUL next to a divide is still rejected.

Please build #449's Hopper gate the same way. The recorded check of `61d0298d` is running on the CI pod: `r20260930-095445-6d59`.

**Addendum (10:14Z): the pous root adds `__frsqrt_rn` to the allowlist, under the same conditions.**
- A whole-sequence match, including any slow path, and a fast-math negative control.
- Keyed to the nvcc version, failing closed otherwise.
- Bit-exact against a correctly rounded reference on all 2³² FP32 inputs.

A kernel that uses `rsqrt_rn` keeps it: switching to sqrt then reciprocal rounds twice and would change the reference and the statement.
