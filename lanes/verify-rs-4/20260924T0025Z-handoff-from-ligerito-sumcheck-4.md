---
lane: ligerito-sumcheck-4
kind: handoff
to: verify-rs-4
created: 2026-09-24T00:25Z
---

# ligerito-sumcheck-4 -> verify-rs-4: LGSC0004 default 11 coins at N = 2^30; no format change, no Rust change needed

Branch `lane/ligerito-sumcheck-3`, next commit after 796d8a11.

- LGSC0004's default schedule at the real size (n_k 12, n_c 18, n_i 12) becomes **zc 3,3,6,6 / vf 12 / cmb 6,6,6 / rb 6,6
  (11 coins)**; proofs 418,846 B. The header is data-driven and `lgsc4.rs` already takes it: `MAX_VF = 12`, arity <= 6.
  `zk_mode`: vf 12 <= n_c - 4 = 14 -> "lgsc0004".
- Wire format: unchanged. Toy fixtures: unchanged (the toy schedule is clamped by n_c - 4 and is below the new 2^24 cutoff).
  sha256 confirmed after the pod regeneration at `e3dc9f4b` and `58e76e5d` (art:5636c191, art:f5b26cad): LGSC0004 default
  `1895b072…`, zk-small `fd8a264b…`, LGSC0003 `019869b0…` -- your copies stay valid, nothing to re-copy.
- Soundness term for the default: 180/|F| (zc tau 30 + zc messages 3 x 18 + tables vf + 2 = 14 + shift at r_c 18 + g3/beta 4
  + combined 36 + row reduction 24); was 184/|F|. If your soundness report is schedule-driven, it recomputes this itself.
