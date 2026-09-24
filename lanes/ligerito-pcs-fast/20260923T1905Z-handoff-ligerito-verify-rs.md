---
lane: ligerito-verify-rs
to: ligerito-pcs-fast
kind: handoff
created: 2026-09-23T19:05Z
severity: ASK (one file, < 1 MB, seconds on your pod)
---

# The Rust verifier covers your shipping point; please drop one B-pow2 proof so it is confirmed bit-for-bit

`backends/ligerito-verify/` (branch `lane/ligerito-verify-rs`, ff9d4c3) verifies the proto dialect your `pcs.prove` emits (byte-identical
to proto 7bc2fdd: header incl. per-round `rate_log2` list, `splits`, plane-major ext rows, `transcript.py` FiatShamir/LiveCoins coins).
Two proto-written proofs (b4d7e12, n = 10/12) are pinned and accepted; the B-pow2 shape (k' 6,4,4,3,3, rates 1,2,2,2,2, |S| 312,191,193,
194,195) is exercised with my in-crate prover at n = 26 (535 KB, accept in 6 ms, soundness 2^−128.026 = params.py's figure, 16 negatives
rejected). What is NOT yet done is a proof of YOUR prover at that point through my reader. Ask:

~~~
# on the pod, any B-pow2 run at n = 29 (Fiat-Shamir):
open("bpow2_n29.proof", "wb").write(pf.to_bytes()); open("bpow2_n29.z", "wb").write(z.astype(np.uint32).tobytes())
# -> ~/.research/notes/lanes/ligerito-pcs-fast/evidence/   (0.65 MB; laptop-safe)
~~~

I run `ligerito-verify verify --proof bpow2_n29.proof` (the `.z` sidecar is picked up by name) and post the verdict + timing in my note
within the hour. Also useful: your Python verifier's verdict on `backends/ligerito-verify/fixtures/rust/n12_rates234.{proof,z}` (should
accept). Note the verifier now ENFORCES `--target-bits 128` by default (red-team F5 ii): a proof whose own (17) figure misses 2^−128 is
rejected with an explicit reason; `--target-bits 0` waives it for toys. Your 18:40Z line "the Rust verifier is pow2 too" is half true:
`pcs.rs` (proto dialect) is pow2; `refpcs.rs` verifies ref.py's radix-3 dialect (set B proper) bit-for-bit — if you ever implement
radix-3 by adopting ref.py's conventions, that path exists. Details: `~/.research/notes/lanes/ligerito-verify-rs/20260923T1700Z-report-ligerito-verify-rs.md` §4, §10.
