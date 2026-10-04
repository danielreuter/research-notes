---
id: 20261004T2102Z-report-relay-p2-seed-expander
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 20:33Z request from store:pous/internal/efficient-crypto/attacks/p2-seed-expander.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/efficient-crypto/attacks/p2-seed-expander.md`, sha256 `ac2b3d8995a4d992f5b8196ff15a292dda706b512d60e9ddda1c5e878dbe4eef`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P2 seed expansion in the storage game

28 Sep 2026. Scope: the key-expander part of P2–M1-SGI only. This does not
address whether square–mask–square itself behaves like an ideal permutation.

## Result

The generic random-oracle view replacement needed for the desired lemma is
false under the game exactly as stated; no nontrivial acceptance bound follows
from the RO assumption alone.
A 256-bit salt defeats bounded preprocessing only when the attacker has a
finite query budget after the salt, or when the setup oracle exposes only the
selected salt row. Here preprocessing after the salt has unlimited computation
and unlimited H queries. With one bit of H-dependent advice it can query all
other salt rows and recover a bit of the selected row. With s bits it can make
the statistical distance from an independent row at least 1 − 2⁻ˢ.

Consequently:

- for a globally fixed SHAKE random oracle under the stated game, the only
  universal numerical value justified here is the vacuous ε_exp = 1, at both
  B = 2¹⁹ and B = 2²³;
- modeling setup as a fresh independent-output oracle sampled after W closes
  the key-independence issue exactly, with ε_exp = 0;
- a weaker, domain-restricted salted-RO model has a valid conditional lemma.
  Its worst-case losses with a 256-bit salt are about 2⁻¹¹¹·⁷⁸ at B = 2¹⁹ and
  2⁻¹⁰⁹·⁷⁸ at B = 2²³ when H-dependent W is counted. These figures do not
  apply when off-row H queries are unlimited.

Recommendation: use SHAKE256 with the exact framing below, and call the
deployment assumption **P2-EXP-IO**: after W is committed, setup supplies one
fresh independent random XOF stream per segment, block and purpose. This is
clearer than claiming that ordinary PRG security or a plain global-ROM theorem
proves the result. Concrete SHAKE256 in place of P2-EXP-IO remains a named
multi-stage storage-game idealization.

## 1. Candidate expanders and assumptions

### 1.1 Required framing

Use a canonical, injective, length-delimited encoding. For example:

```text
base =
  "verity/pous/p2/expand/v1" ||
  protocol-version ||
  prime-id ||
  model-commitment ||
  setup-salt-256 ||
  u64(segment) ||
  u64(block)

mask-stream  = SHAKE256(base || "K")
tweak-stream = SHAKE256(base || "t")

K_j = first 16,448 bits of mask-stream
t_j = first consecutive 16,448-bit tweak candidate strictly below p
```

The exact byte order and field lengths must be frozen and covered by vectors.
One setup salt may cover all eight MVP segments because `segment` and `block`
make every input distinct. Reusing the same input, omitting the segment, or
resetting local block numbers without a segment tag destroys that conclusion.
The salt must be drawn without prover grinding after the W commitment.

The two purpose strings make K and t separate RO coordinates. An equally sound
ideal specification can use one stream with a frozen, prefix-free parse, but it
must not ambiguously overlap K and t.

### 1.2 Candidate A: SHAKE256 as a random oracle

There are two materially different formulations.

**Global-ROM formulation.** Sample one public random oracle H once. The
expander above evaluates H on inputs containing a random 256-bit setup salt.
For any fixed salt, all distinct framed inputs have independent random XOF
streams. This is the usual “SHAKE256 is a random oracle” idealization.

It gives literal independent keys if everything fixed before the salt is
independent of H. It does not give literal independence if pre-salt W or advice
may depend on H and the post-salt preprocessor can make unlimited H queries.
Section 2 gives the separation.

**P2-EXP-IO formulation, recommended.** After W is committed, sample the
family of XOF streams indexed by `(segment, block, purpose)` independently of
the complete pre-setup transcript. Publish the salt and oracle outputs. This
is equivalently a fresh setup-specific random oracle whose handle is created
after W. Then every K is uniform in `{0,1}¹⁶⁴⁴⁸`, every accepted t is uniform
in Z_p, and all pairs are mutually independent. Thus ε_exp = 0 by definition.

P2-EXP-IO is stronger than a theorem about one globally fixed RO. A concrete
SHAKE implementation is deterministic and globally fixed, so replacing it by
P2-EXP-IO is an assumption, not an information-theoretic fact.

### 1.3 Candidate B: ChaCha20 or ChaCha8 with feed-forward

A precise ideal-permutation version is:

1. Sample a public ideal permutation P on 512-bit strings after the pre-setup
   transcript, or require the analogous independent-row property.
2. Injectively encode the 256-bit setup seed, segment, block and 64-byte chunk
   counter into distinct ChaCha input states X_i.
3. Return `P(X_i) + X_i`, with addition independently modulo 2³² in each word.
4. Concatenate 65 blocks to obtain the nominal 4,112 bytes for one P2 block.

For q distinct inputs, replacing ideal-permutation outputs by independent
512-bit strings costs at most q(q − 1)/2⁵¹³ by the PRP/PRF switching argument.
Input-dependent feed-forward is a bijection on each output and does not enlarge
that distance. At 65 blocks per P2 block:

| P2 blocks | ChaCha blocks q | switching loss at most |
|---:|---:|---:|
| 2¹⁹ | 34,078,720 | 2⁻⁴⁶²·⁹⁶ |
| 2²³ | 545,259,520 | 2⁻⁴⁵⁴·⁹⁶ |

This is useful only in the fresh-permutation or independent-row model. If P is
a globally fixed ideal permutation, H-dependent advice and unlimited post-salt
P queries recreate the same auxiliary-input problem as candidate A.

No theorem says the concrete ChaCha round permutation is ideal. ChaCha8 also
adds a reduced-round cryptanalytic assumption. Candidate B therefore has no
soundness advantage over SHAKE256 here; it only has a CPU-speed advantage.

### 1.4 Candidate C: a standard-model PRG

A conventional PRG G maps a short uniformly random, hidden seed to a longer
string computationally indistinguishable from uniform for efficient
distinguishers. That definition is inapplicable twice:

1. The setup seed is public. Given `(s, y)`, an efficient distinguisher tests
   whether `y = G(s)`. Ordinary PRG security never promises pseudorandomness
   jointly with the seed.
2. The P2 preprocessor is computationally unbounded. Even if the seed were
   hidden, it can enumerate the PRG support, whose size is at most 2 to the seed
   length, inside a key-vector space vastly larger than that.

The following separation is specific to P2, not merely a support-size
observation.

**Proposition 1 (a standard PRG can make every P2 ciphertext compressible).**
Assume any ordinary locally seekable secure PRG G₀ whose decoded output is a
sequence `(c̃_j, K_j)`, with c̃_j pseudorandom in Z_p and K_j pseudorandom
16,448-bit strings. Define another efficient expander G₁ for the fixed weight
vector W = 0 by

```text
t_j = d(σ_Kj(d(c̃_j))) mod p
G₁(s) = ((K_j, t_j))_j .
```

Then G₁ is an ordinary secure PRG for the target key distribution, but P2's
encoded ciphertext is exactly `C = (c̃_j)_j`. A storage adversary retains only
the public seed and evaluates the locally seekable G₀ block online.

**Proof.** For fixed K, the map
`c ↦ d(σ_K(d(c)))` is a permutation of Z_p. Therefore the displayed map sends
a uniform `(c̃, K)` to a uniform `(t, K)`. It is efficiently computable, so a
distinguisher for G₁ gives a distinguisher for G₀ by applying this map to its
challenge. Finally, by construction,
`D_j(c̃_j) = d(σ_Kj(d(c̃_j))) − t_j = 0`, so correctness and bijectivity of P2
give `E_j(0) = c̃_j`. The seed is a short description of all ciphertext
blocks. ∎

This shows that “the keys are the output of a secure PRG” cannot replace an
expander assumption tailored to this storage game.

## 2. The requested random-oracle transfer

### 2.1 Impossibility under unlimited post-salt queries

Let the salt space have N = 2²⁵⁶ rows. It is enough to replace each complete
row by one bit X_a; larger key rows only strengthen the example.

**Proposition 2 (salt does not freshen a row against unlimited later
queries).** Let X₁, …, X_N be independent uniform bits and let the one-bit
pre-salt advice be

```text
Z = X₁ xor X₂ xor ... xor X_N .
```

After a uniform salt A is revealed, a preprocessor that can query all rows
other than A recovers

```text
X_A = Z xor (xor of all queried rows).
```

If the setup key is instead an independent uniform bit U while the same oracle
and advice remain available, the equality test succeeds with probability
one-half. With s coordinate-wise parity bits, the real and independent views
have statistical distance at least 1 − 2⁻ˢ.

**Proof.** The first equality is the definition of Z. In the independent
experiment U is independent of Z and all queried rows, so all s recovered
coordinates agree with U with probability 2⁻ˢ. The equality test distinguishes
the views with advantage 1 − 2⁻ˢ. The advice and recovered coordinates occupy
s bits, so taking s no larger than the state cap respects the storage bound. ∎

The recovery occurs during the unbounded preprocessing stage after the salt.
The online bound Q = 2²⁰ on complete P2 forward decodes is irrelevant: it is
not a post-salt H-query bound. This counterexample is a distinguisher, not a
demonstrated compression attack against concrete P2. Its consequence is exact
but narrower: no generic RO-to-independent-keys acceptance lemma follows in
this game. The actual P2 acceptance inequality might still hold, but
establishing it would be a new P2-specific storage-game assumption or proof.

If W may depend on H, W itself is auxiliary information. Calling only the
retained private string “advice” does not remove the information carried by a
public H-dependent W. A valid bound must count up to B log₂p additional bits,
or require W to be independent of H.

### 2.2 What the cited salted-ROM results actually prove

I checked the theorem statements in the full papers.

- **Unruh 2007**, *Random Oracles and Auxiliary Input*, CRYPTO 2007, ePrint
  2007/168, Theorem 2: for auxiliary input with range size 2ᵖ, an adversary
  making at most q RO queries can replace the oracle by one with at most f
  pre-sampled points at statistical cost at most `sqrt(pq/(2f))`. Finite q is
  essential.
- **Dodis–Guo–Katz 2017**, *Fixing Cracks in the Concrete: Random Oracles with
  Auxiliary Input, Revisited*, EUROCRYPT 2017 II, pages 473–495, Theorem 1
  restates Unruh as `sqrt(ST/(2P))`; Theorem 2 gives a general lower bound of
  order ST/P against that approach. Their salting theorems are
  application-specific: inversion, collision resistance, PRGs/PRFs and MACs.
  They do not state a generic unbounded-query storage-game compiler.
- **Coretti–Dodis–Guo–Steinberger 2018**, *Random Oracles and Non-Uniformity*,
  EUROCRYPT 2018 I, pages 227–258:
  - Theorem 5 gives the AI-ROM to P-bit-fixing-ROM loss
    `2(S + log₂(1/γ)) T_comb/P + 2γ`.
  - Theorem 17 gives generic standard salting in the bit-fixing ROM with loss
    P/K for a salt space of size K.
  - Corollary 18 combines them:

```text
ε_exp ≤ P/K
      + 2(S_aux + log₂(1/γ)) T_comb/P
      + 2γ .
```

Here T_comb is the finite total oracle-query count of the challenger and the
post-advice attacker. The reduction also incurs soft-O(P) time and state
overhead, so it does not automatically compare two storage games at exactly
the same cap S.

With unlimited post-salt preprocessing queries, T_comb is unbounded and this
corollary is vacuous. Substituting P2's Q is invalid because Q counts complete
two-squaring decodes, not H queries.

For scale only, if all post-salt H queries were additionally capped by
T_comb = 2²⁰, γ = 2⁻¹²⁸, and H-dependent W were counted, optimizing P would
give approximately 2⁻⁹⁹·⁵² at B = 2¹⁹ and 2⁻⁹⁷·⁵² at B = 2²³, before
accounting for the simulator's state overhead. Even one post-salt query gives
only about 2⁻¹⁰⁹·⁵² and 2⁻¹⁰⁷·⁵² from this generic compiler. These are not
bounds for the deployed game.

### 2.3 A valid conditional lemma

The strongest simple same-storage statement applies if, after the salt, the
adversary receives only the selected row of the setup oracle, not arbitrary
other salt rows. Unlimited computation on that row is allowed.

**Lemma 3 (salted row with bounded pre-salt information).** Let
`R₁, …, R_N` be independent complete setup rows, where one row contains every
raw XOF stream needed for all segments and blocks. Let Z be all information
fixed before the uniform row index A, with at most s_aux bits of range. Give
the setup and adversary `(A, Z, R_A)` and no access to other rows. Let U be an
independent row with the same distribution. For any subsequent unbounded
preprocessing, S-bit retained state, online strategy and acceptance predicate,

```text
Pr[accept with R_A]
  ≤ Pr[accept with U] + sqrt((ln 2 / 2) s_aux / N).
```

**Proof.** Independence of the rows gives

```text
sum over a of I(R_a ; Z) ≤ H(Z) ≤ s_aux bits.
```

For uniform A,
`I(R_A ; Z | A) ≤ s_aux/N`. This mutual information is the base-2 relative
entropy between `(A,Z,R_A)` and `(A,Z,U)`. Pinsker's inequality converts it to
statistical distance at most `sqrt((ln 2 / 2) s_aux/N)`. W, C, the retained
state, all later unbounded computation and the online transcript are channels
applied to these views, so data processing cannot increase statistical
distance. The difference of acceptance probabilities is at most that
distance. ∎

If W is independent of H, take s_aux = S. If W may be an arbitrary
H-dependent element of Z_p^B, take at least `s_aux = S + B log₂p`; using Bw is
a conservative integer bound.

| B | Bw bits | S = floor((18/19)Bw) | ε, H-dependent advice only | ε, advice plus H-dependent W |
|---:|---:|---:|---:|---:|
| 2¹⁹ | 8,623,489,024 | 8,169,621,180 | 2⁻¹¹²·³⁰ | 2⁻¹¹¹·⁷⁸ |
| 2²³ | 137,975,824,384 | 130,713,938,890 | 2⁻¹¹⁰·³⁰ | 2⁻¹⁰⁹·⁷⁸ |

These are exact parameter calculations, not asymptotic security claims. They
are conditional on the row restriction and therefore are not the deployed
game's ε_exp.

### 2.4 Rejection, σ's branch, public seeds and error accounting

Let `r = (2¹⁶⁴⁴⁸ − p)/2¹⁶⁴⁴⁸ = 21065/2¹⁶⁴⁴⁸`.

- Parsing independent w-bit candidates until one is below p gives an exactly
  uniform t in Z_p. It terminates with probability one and uses
  `1/(1 − r)` candidates on average. There is no distributional error. A
  bounded implementation that permits L candidates would have failure at
  most B rᴸ.
- For every fixed intermediate value x, `x xor K` is uniform over w-bit
  strings when K is uniform. Thus σ takes its exceptional branch with
  probability exactly r. The concrete P2 map includes that branch, so it is
  not an expander error. A proof that deletes the branch must charge at most
  Br: 2⁻¹⁶⁴¹⁴·⁶⁴ at B = 2¹⁹ and 2⁻¹⁶⁴¹⁰·⁶⁴ at B = 2²³.
- If both “a tweak candidate was rejected” and “σ used its branch” are
  replaced by ideal behavior, a union bound is 2Br, one bit larger in the
  exponent. There is no reason to make either replacement in the exact spec.
- The salt/seed and every derived key are public. Revealing the seed therefore
  gives no secret information beyond a compact way to recompute already
  public keys. That observation does not create independence: compact,
  related public keys are exactly the issue being modeled.

The current M1 headline is already `0.01 + 2⁻¹²⁸`. No positive ε_exp may
simply be added while retaining that exact headline. The ideal certificate and
instantiation error must be reallocated so their sum is at most the existing
cryptographic allowance (or the ideal 1% term must be lowered by the same
amount).

Even the conditional 256-bit-salt figures above are larger than 2⁻¹²⁸. Under
Lemma 3 with H-dependent W at B = 2²³, a salt of at least 293 bits makes that
single expander term at most 2⁻¹²⁸; 295 bits makes it at most 2⁻¹²⁹ for an
equal split. Longer salt does not repair Proposition 2 when post-salt queries
remain unbounded. P2-EXP-IO instead gives ε_exp = 0 by construction.

## 3. Narrow state and “Careful with composition”

Ristenpart–Shacham–Shrimpton, *Careful with Composition: Limitations of the
Indifferentiability Framework*, EUROCRYPT 2011, LNCS 6632, pages 487–506
(full version ePrint 2011/339), give a storage-audit counterexample. An
iterative hash's short chaining state replaces a large file prefix between the
preprocessing and challenge stages even though the hash is indifferentiable
from a random oracle. Their point applies directly to the validity of a
composition argument in this two-stage game.

It does not, by itself, give a P2 compression attack:

- SHAKE's 1600-bit sponge state, or ChaCha's 256-bit seed plus counter, is a
  checkpoint for regenerating the public K and t streams.
- P2 stores c, not those streams. C also depends on W through two inverse
  square-root layers. An expander checkpoint does not contain a prefix of C
  and does not turn forward squarings into the missing roots.
- Since the setup seed already regenerates every key, retaining a 1600-bit
  sponge state is no better for storage than retaining/publicly reading the
  256-bit seed. Neither substitutes for a 16,448-bit c_j.

So there is no narrow-state compression route from state width alone. This is
a reason, not a proof: Proposition 1 shows that an adversarially structured
expander can arrange for its seed to describe C. RSS says ordinary
indifferentiability cannot rule such a route out in a multi-stage game. The
appropriate conclusion is “no direct attack from the SHAKE state is known,
but use a storage-game assumption,” not “sponge indifferentiability proves
composition.”

## 4. Assumption class relative to the band

The primitive idealization is the same class already used by the deployed
band:

- SHAKE256 round functions are treated as random functions/random-oracle
  outputs;
- Keccak-f is treated as an ideal permutation;
- sponge indifferentiability and Feistel indifferentiability connect those
  ideal objects to the construction.

Using SHAKE256 for P2 expansion adds no new primitive family. It does add a
new use-specific claim: a globally fixed, salted SHAKE instance may be
replaced by independent setup outputs in this multi-stage storage game.
The band's own write-up already names the RSS caveat, so this is not a new
class of idealization for the project, but it is a separate assumption
instance and is not inherited automatically from the band's Feistel proof.

P2-EXP-IO states the needed property directly and avoids pretending the
ordinary composition theorem applies. It closes memo item 5 on paper if the
decision is to accept an independent-output idealization. It does not prove
that concrete SHAKE has the property, and it does not close the larger
square–mask–square P2–M1-SGI assumption.

## 5. CPU cost

### 5.1 Method

**Measured.** Four-vCPU Intel Xeon VM, one pinned CPU, best of 11 except the
OpenSSL bulk test (best of five one-second runs). Initial load average was
1.15, 0.46, 0.29; the exact two-domain SHAKE run began at 0.44, 0.45, 0.32.
Software: OpenSSL 3.0.13, Python 3.12.3, cryptography 41.0.7, gmpy2 2.3.1 and
GMP 6.3.0. Key expansion emits two separately domain-separated 2,056-byte
streams, 4,112 useful bytes total per 2,056-byte P2 block. No rejection
occurred or is expected at measurable frequency.

| Implementation | Measured useful-output throughput | Measured or derived cost per P2 block |
|---|---:|---:|
| SHAKE256, hashlib/OpenSSL, two XOF domains | 0.450 GB/s | 9.131 µs measured |
| ChaCha20, OpenSSL bulk stream | 5.872 GB/s | 0.700 µs derived from measured throughput |
| ChaCha20, cryptography/OpenSSL, new Python object per block | 0.391 GB/s | 10.517 µs measured |
| ChaCha20, local portable scalar C, feed-forward | 0.478 GB/s | 8.598 µs measured |
| ChaCha8, local portable scalar C, feed-forward | 1.221 GB/s | 3.368 µs measured |

The OpenSSL bulk figure is the relevant optimized ChaCha20 primitive rate if
segments are expanded as contiguous counter streams. It omits per-stream
initialization. The Python per-block result shows that a naive host wrapper can
erase that advantage. The ChaCha8 number is scalar, not an estimate of a
vectorized device or AVX implementation.

**Measured.** gmpy2 took 78.700 µs per dependent pair of 16,448-bit modular
squarings. Against that baseline, SHAKE adds 11.6%, optimized bulk ChaCha20
0.9%, and scalar ChaCha8 4.3%.

Against the campaign's 2.1 µs single-core IFMA measurement per squaring, a
two-square decode is 4.2 µs:

| Expander | Expansion time / 4.2 µs decode | Combined CPU time per block |
|---|---:|---:|
| SHAKE256 | 2.17× | 13.33 µs |
| optimized bulk ChaCha20 | 0.17× | 4.90 µs |
| scalar ChaCha8 | 0.80× | 7.57 µs |

Thus SHAKE is more expensive than the optimized CPU decode unless expansion is
batched or parallelized across cores. This is a performance fact, not a reason
to substitute ChaCha8's weaker assumption.

### 5.2 Device-side scale

*est.* The band documentation gives 9,650 Keccak-f calls per Π₂ call,
13 Π₂ calls per 65,536-byte deep decode, and 1,532 MB/s on the L40S. That is
about 1.914 Keccak-f calls per band plaintext byte. Two domain-separated P2
SHAKE streams of 2,056 bytes each need about 32 Keccak-f calls, or 0.01556
calls per P2 plaintext byte. Scaling only by this count gives *est.* 188 GB/s
of P2 plaintext-equivalent key expansion. Serially combining that with the
measured 25.0 GB/s P2 arithmetic gives *est.* 22.1 GB/s, an *est.* 11.7%
throughput reduction.

This is marked *est.* It assumes comparable Keccak occupancy and ignores
kernel integration, rejection control and memory scheduling. The POUS MVP
owner must measure device-side derivation.

## 6. Can the key material be reduced?

Not under the present proof and attack review.

- K must be a fresh, independent, full-width dense mask. Truncating its
  entropy, making it sparse, reusing it, or deriving related masks reopens the
  known zero-mask, sparse-mask and related-key routes and leaves M1.
- t must be fresh and uniform in all of Z_p. This makes `W_j + t_j` uniform
  after W is fixed. A 256-bit or otherwise narrow tweak leaves each target in
  a small public translate set and invalidates the fixed-point, subgroup and
  setup-order arguments.
- K and t must be independent coordinates. Deriving one algebraically from
  the other is a different assumption; Proposition 1 shows why apparently
  pseudorandom correlations can be fatal.

The public setup salt already compresses the representation of the key
material. The implementation may store only that salt and derive keys on
demand, but it must generate the full 4,112 useful bytes per block. Reducing
those outputs safely requires a new concrete construction and a new P2–M1
analysis, not a parameter tweak.

## Artifacts

- Benchmark source:
  `internal/efficient-crypto/attacks/p2-seed-expander/bench.c`
- OpenSSL/hashlib and GMP driver:
  `internal/efficient-crypto/attacks/p2-seed-expander/bench_gmp.py`
- Full commands, samples, versions and load:
  `internal/efficient-crypto/attacks/p2-seed-expander/benchmark.log`
