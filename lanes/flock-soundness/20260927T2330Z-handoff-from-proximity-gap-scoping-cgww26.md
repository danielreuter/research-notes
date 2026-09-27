---
cursor:
  subagentId: "bc-a2881cda-5857-5d2a-82bd-458f6b99d672"
---

lane: flock-soundness · kind: handoff · from: proximity-gap scoping (bc-a2881cda) · created: 2026-09-27T23:30Z · repo: danielreuter/verity · about: DESIGN §3, A2 (#127, #163)

# proximity-gap scoping → flock-soundness: CGWW26 (ePrint 2026/2209) backs A2 and δ_link, but doesn't beat our compiled bound

Chiesa–Guan–Wang–Wu, "The Cost of Rewinding for Succinct Arguments" ([ePrint 2026/2209](https://eprint.iacr.org/2026/2209)).
William Wang is a Flock co-author. Daniel asked whether it helps. It does, mostly as citations for decisions you already
made. No change to any theorem.

- **Adopting A2 was necessary, not a convenience.** Their Theorem 1: no strict polynomial-time reduction through a
  black-box, VC-oblivious extractor reaches negligible knowledge error in Kilian's protocol. The bounds are
  $\kappa > 1/(8p^2)$ with $p$ rewinds (low-query PCPs), or $\kappa > 1/p$ (zero-knowledge PCPs). That is DESIGN §3's
  strict-time square root, proved inherent. The only ways out are expected time (A2) or the random oracle, DESIGN §3's
  option (ii). Worth citing in §3.
- **A2's constant.** Their §1.2 uses Jaeger–Tessaro (TCC 2020): an expected-time $t^\star$ adversary finds an
  ideal-hash collision with probability at most $t^\star/2^{\lambda/2}$, which is $T/2^{256}$ for SHA-512. That is the
  clean fix I proposed, and it is consistent with the sharp $E[Q]/E[\tau_N] \approx T/2^{256.33}$. It is independent
  support for moving off $2^{256.5}$ (my 17:35Z handoff).
- **δ_link's $N_0$ factor is essentially optimal in the standard model.** Their rETH lower bound says every
  expected-time VC-oblivious extractor for Kilian's protocol makes $\Omega(\ell/\mathrm{polylog}\,\ell)$ rewinds in
  expectation, for quasilinear PCPs with few queries. So the $cN_0/e$ reruns in #163's extractor can't be cut much
  without leaving the standard model. `ASSUMPTIONS.md` §7's "the number to sharpen" is about as sharp as it gets.
- **No gain for the compiled table theorem.** Their IBCS theorem is exactly our compiled shape (a commitment per round,
  openings after the last round), and gives $\epsilon_{\rm IOP} + \epsilon^\star_{\rm VC}(O(\ell t))$. With SHA-512 that
  is about $(\ell+1)t/2^{256}$, where $\ell$ is the total committed length.

  | m | CGWW26 (expected time) | ours (`table_sound_compiled`, strict time) |
  |---|---|---|
  | 33 | $t\cdot 2^{-234.3}$ | $t\cdot 2^{-239.7}$ |
  | 35 | $t\cdot 2^{-232.3}$ | $t\cdot 2^{-238.7}$ |

  Ours is 5–6 bits better, and under the weaker assumption. Their full-extraction knowledge theorem pays $k\cdot\ell$
  (every round's string), so for the audit our level-0-only extraction is better too.
- **Their open problem is one we have a data point on.** They ask whether commit-and-open soundness can be shown without
  extracting a full proof string. Our plurality-table argument (`Rewinding.bad_sq_le`, $\#\mathrm{bad}^2 \le
  N\cdot Q\cdot\#\mathrm{conflict}$ per cap) does exactly that, in strict time with a square root, at cost
  $\sqrt{N\cdot Q}$ rather than $\ell$, and it is machine-checked. Telling the authors is Daniel's call, since it is
  outside contact.

**Suggested edits,** in the same change as the A2 fix:
- DESIGN §3: cite CGWW26 Theorem 1 for why expected time; cite JT20, via CGWW26 §1.2, for A2's constant; cite the
  lower bound for δ_link's optimality.
- ASSUMPTIONS A2 "Why it is plausible": the same JT20 bound.
