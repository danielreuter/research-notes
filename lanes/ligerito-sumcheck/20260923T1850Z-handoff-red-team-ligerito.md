---
lane: red-team-ligerito
to: ligerito-sumcheck
kind: handoff
created: 2026-09-23T18:50Z
severity: BREAK (zero knowledge, once your bivariate opening round meets ligerito-zk's Libra mask); soundness of your rounds: OK
---

# Your zero-check under ZK: the bivariate opening round leaks; the Gruen `q` wire form cannot carry the Libra mask

* Soundness (independent check): opening round 6/|F| (q has degree ≤ 2 per variable, i.e. total degree 4, plus the two zeros of
  the eq factors); univariate rounds 3/|F|; zero-check total ≈ 93/|F| = 2^-178.9 at 30 variables; the relation union is 2^-173.4.
  Nothing to fix for soundness. The coins come from the verifier's coin alone under `LiveCoins` / `zk.CommittedCoins` (8c OK).
* **ZK BREAK on integration:** `zk.SumcheckMask`'s `g = a_0 + sum_i g_i(x_i)` gives the (X1, X2) message no X1^a X2^b terms.
  Your `round0[3][3]` cross coefficients are therefore witness functionals, sent in the clear. Demo:
  `backends/direct/ligerito/redteam_libra_bivariate.py` @ 9182132 (lane/red-team-ligerito): the cross coefficients are identical
  across mask draws and different across witnesses. Under ZK, either run the opening round univariate, or have ligerito-zk add a
  `3 x 3` cross block for the pair.
* Under ZK every zero-check round has to send the full degree-3 `s(X) = eq(tau_t, X) q(X) + rho G_t(X)` (4 values). The Gruen
  form `(q(0), q(1), q(inf))` can't express the `rho G_t` part. `LGSC0002` needs a ZK variant, and the verifier's
  `E_t((1 - tau_t) q(0) + tau_t q(1))` check becomes `s(0) + s(1) = claim`.
* Also for the record: your pow2 layout (N = 2^30) means set B's radix-3 |S| do not apply to the PCS you feed. ligerito-relation and
  ligerito-pcs-fast have the corrected numbers.
