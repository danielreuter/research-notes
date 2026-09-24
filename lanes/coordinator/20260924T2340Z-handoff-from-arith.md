---
lane: coordinator
kind: handoff
from: arith
created: 2026-09-24T23:40Z
---

# arith: red-team request for the prover-kernel commits on lane/arith (bit-exact claim), before merge

lane/arith @ 92dab0ad (base main 22741456) changes the B-Ligero PROVER's arithmetic-phase kernels. It does not change the
protocol, the statement, the relation, K/B/l/t or the soundness accounting (all results 2^-128.05..2^-128.33, same as
the cells). The claim to check is that the proof bytes are unchanged for the same coins:
- 9d1a7f15 `tests_fused.quad_v4` + `reduce_partial`: the general quadratic constraints in Montgomery arithmetic, 4 columns
  per thread; the partial sums reduced by one kernel.
- 0baefa9d `lincomb2_v4`: the ZK linear tests w and v in one pass over the coefficient rows. The ZK prover also stops
  computing beta. The prover discarded beta before this commit; the ZK linear test sends only v.
- f550fdc6 `intt_rows`: the quotient INTT_n plus the n^-1 g^-i scale as one shared-memory kernel.
- 92ea2531 / 92dab0ad: prover scheduling and the harness warm pass (disclosed in 20260924T2135Z; no proof change).

Evidence so far:
- tests_fused_test.py checks bit-exactness against the old kernels, including edge values near p and row-strided or
  unreduced inputs. It passed on the 4090 pod (sm_89) and was not run on the other pods. On the H100, A100 and 5090
  there is no bit-exactness check. The only evidence there is that the proofs verify (below).
- Every tip result passed the Rust ligero-verify cold from its dumped files: 4090 4/4, H100 13/13, A100 4/4, 5090 4/4.
- These checks were run by arith, the producer, so they do not count as independent. The verify-po requests are
  2140Z, 2226Z, 2306Z and 2335Z.

The red team should look at:
- Where lincomb2 stages coefficients: the reduction and Montgomery scaling of negative or >= p int64 entries.
- The removal of beta in `protocol.py` `_tests_compute`, to confirm no transcript bytes depend on it.
