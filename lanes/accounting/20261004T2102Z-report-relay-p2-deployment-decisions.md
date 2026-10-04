---
id: 20261004T2102Z-report-relay-p2-deployment-decisions
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 20:33Z request (F2 holds the 1.9 ms derivation) from store:pous/docs/efficient-crypto/p2-deployment-decisions.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/efficient-crypto/p2-deployment-decisions.md`, sha256 `f493f8c030dfc2ed05c4f739090376d4fa3515ce1e875c8f2e70225f257e01c1`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P2: freeze decisions (frozen 29 Sep 2026)

29 Sep 2026. Workstream 2 (efficient cryptography). **P2 is frozen as spec v1** (`docs/efficient-crypto/p2-spec-draft.md`).
Daniel deferred every freeze decision to our recommendations, so each item below is recorded as **"default, Daniel
deferred, 2026-09-29"**. Background and evidence follow the list.

Freezing the spec does not decide the deployment question (Decision 1 below). P2 stays an experimental option next to
the band until its instantiation assumption is accepted; that default is still "not yet".

| Item | Decision | Record |
|---|---|---|
| F1. Payload profile | `p2-2054B`: 2,054 bytes per block | default, Daniel deferred, 2026-09-29 |
| F2. Operating point | B = 2^19, Q = 2^20, Δ = 0.5 ms with an RTT allowance of at most 1 ms, one CPU or GPU core with cooperation allowed within one chiplet, w = 16,448, k from F6 | default, Daniel deferred, 2026-09-29 |
| F3. Published error total | 1% + 2^-128, split as below | default, Daniel deferred, 2026-09-29 |
| F4. Expander assumption | Accept P2-EXP-IO, realized with SHAKE256 | default, Daniel deferred, 2026-09-29 |
| F5. The three margin pins | Pinned in `lean/pous`, 29 Sep, 17:55Z | default, Daniel deferred, 2026-09-29 |
| F6. The buffer | k = 105 | default, Daniel deferred, 2026-09-29 |
| The prime | Keep 2^16448 − 21065, ECPP-certified, without a Lean-checked primality proof | default, Daniel deferred, 2026-09-29 |
| Decision 1: the instantiation assumption (P2–M1-SGI) | **Not accepted yet**; P2 stays experimental | default, Daniel deferred, 2026-09-29 |

## F1. Payload profile

**The choice.** How many payload bits each 16,448-bit block carries:
- `p2-16447b`: 16,447 bits, packed continuously across bytes;
- `p2-2054B`: 2,054 whole bytes (16,432 bits), which the MVP already uses.

**What each costs.**
- `p2-16447b` carries 0.09% more payload per block, but needs bit packing across byte boundaries, and the MVP must
  migrate to it.
- `p2-2054B` leaves 15 bits per block unused (0.09%) and changes nothing.
- Both are equally covered by the pinned exact-domain rows (every payload width from 15,665 to 16,447 bits), and by
  the wire format and its vectors.

**Default: `p2-2054B`.** *Decided: default, Daniel deferred, 2026-09-29.*

## F2. Operating point: B, k, Q, Δ and the hardware

**The choice.** Fix together:
- the block count B and the per-answer query budget Q;
- the deadline Δ plus the round-trip (RTT) allowance;
- the hardware the adversary is allowed. This is Decision 2 below: whether several cores may cooperate on one squaring.

The challenge count k is F6.

**What each costs.** The width w = 16,448 is safe exactly when Δ + RTT is small enough for the hardware reading:

| Hardware reading | Δ + RTT = 0.5 ms (on-node verifier) | Δ + RTT = 2.9 ms (the largest round trip the band is designed for) |
|---|---|---|
| One core per squaring | safe: 8,000 bits needed | safe: 16,448 bits needed |
| Up to 8 cooperating cores on one chiplet | safe: at most 10,368 bits needed | **not safe**: about 28,200 bits needed |

- **At 0.5 ms (the default):** w = 16,448 covers both readings with room to spare. It stays safe with cooperation up
  to roughly 1.5 ms of Δ + RTT (*est.*). Nothing changes, and the MVP already runs a 500 µs limit with an on-node
  verifier.
- **Remote verifier with cooperation allowed:** a remote verifier (RTT up to 2.4 ms) together with cooperating cores
  needs w ≈ 28,200. That means a new prime, new pins and about 1.7× the decode cost.
- **Remote verifier with the literal one-core reading:** 16,448 bits stands, but the timing assumption must then
  exclude splitting one squaring across cores.

**Default** (*decided: default, Daniel deferred, 2026-09-29*)**:**
- B = 2^19; the pins also cover 2^8 to 2^23.
- Q = 2^20.
- Δ = 0.5 ms with an on-node verifier and a measured RTT allowance of at most 1 ms.
- Adversary hardware: a CPU or GPU core, with cooperation within one chiplet allowed; ASICs and FPGAs excluded.
- w = 16,448.
- k per F6.

**Measured (29 Sep, one CPU pod, `art:b92b6d56fa12cc8e04b3f6843991c2e76f49366adc89140a96c33842f70b41ed`, run
`r20260929-060834-0ec4`).** The pod was an AMD EPYC 4564P (Zen 4), with an effective clock of 5.48 GHz, and
cooperation ran on one 8-core chiplet:

| Cores cooperating on one squaring | 1 | 2 | 4 | 8 |
|---|---|---|---|---|
| ns per squaring | 2,717 | 1,516 | 921 | 778 |
| one 16,448-bit root | 44.7 ms | 24.9 ms | 15.2 ms | 12.8 ms |

- **Cooperation helps the adversary more than modelled:** 3.5× at 8 cores, against the 1.1–2.6× assumed. A core-to-core
  round trip inside the chiplet is only 33 ns.
- **The on-node audit round trip** (116-byte challenge, 2,754-byte response) is small:
  - within a chiplet: 6.8 µs median and 10.4 µs at p99.9;
  - across chiplets: 10.5–16 µs median and 22 µs at p99.9, with one 2.1 ms outlier in 50,000 rounds.
- **So w = 16,448 holds at the default:**
  - Δ + RTT ≈ 0.52 ms, and the fastest measured adversary root is 12.8 ms, about 25× the budget.
  - Against the conservative architectural floor (one core about 13.2 ms at 5.7 GHz, divided by the measured 3.5×), it
    is still about 3.8 ms (*est.*). The 2× margin therefore holds up to Δ + RTT ≈ 1.9 ms (*est.*), which covers the
    1 ms RTT allowance.
- **What changes:** at larger budgets the chiplet reading needs more width than the table above says.
- **Honest-prover note:** pin the verifier and the responder on the same chiplet, so round-trip tails stay in
  microseconds.

## F3. Published error total

**The choice.** What total failure probability the spec publishes, and how that total splits across the proved and
assumed parts.

**Draft wording for the spec:**

> A prover that retains at most ⌊(18/19)·|C|⌋ bits beyond W and the public setup between challenges passes an audit
> with probability at most 1% + 2^-128. The 1% is the audit's sampling term, exact in the model. The 2^-128 is a sum of
> four terms:
>
> - (a) **the ideal-model term** ε_ideal ≤ 2^-129, proved in Lean for P2's exact-domain model
>   (`P2ErrorSplitB19Uncond`; the proved bound is far smaller than 2^-129);
> - (b) **the instantiation term** ε_inst ≤ 2^-130, assumed: that square–mask–square behaves like independent ideal
>   permutations in this storage game (P2–M1-SGI);
> - (c) **the challenge-derivation term** ε_chal ≤ 2^-131, assumed: that `verity.randomness` outputs are
>   indistinguishable from uniform;
> - (d) **the expander term** ε_exp = 0 under the setup assumption P2-EXP-IO (F4).
>
> The terms combine additively by a reduction outside Lean, so the total is at most 2^-129 + 2^-130 + 2^-131 < 2^-128.

**What each costs.**
- **This wording** keeps the "1% + 2^-128" headline accurate, and needs `P2ErrorSplitB19Uncond` pinned (F5).
- **Publishing the abstract-model bound alone** is simpler, but it states nothing about the concrete scheme.
- **Adding an instantiation term on top of the old 2^-128** would silently change the headline to 1% + 2^-127.

**Default: adopt the wording above.** *Decided: default, Daniel deferred, 2026-09-29.*

## F4. The expander assumption, P2-EXP-IO

**The choice.** Whether to accept as a named assumption that setup gives every block a fresh, independent mask and
tweak, drawn after the weights are committed. It would be realized by SHAKE256 with the spec's v1 framing, as a
storage-game idealization in the same primitive class as the band's Feistel-SHAKE256.

**What each costs.**
- **Accepting with SHAKE256** costs about 12% of device throughput: about 23.7 → 21 GB/s on an L40S (*est.*; not yet
  measured on the device).
- **Keeping the MVP's ChaCha8** is measured at 23.66 GB/s, but it adds a reduced-round assumption, and it still needs
  P2-EXP-IO.
- **Rejecting P2-EXP-IO** leaves no known alternative: an ordinary secure PRG is provably insufficient in this game.

**Default: accept P2-EXP-IO with SHAKE256.** *Decided: default, Daniel deferred, 2026-09-29.* The MVP migrates from ChaCha8 and measures the cost.

## F5. The three margin pins

**The choice.** Whether to add `P2SlackB19Uncond`, `P2SlackFamilyUncond` and `P2ErrorSplitB19Uncond` to the Lean
trusted layer (`lean/pous`). They state that the exact-domain rows also hold:
- against an adversary with 64 or 128 extra bits per block, at k = 95 / 104 for 2^19 blocks and 96 / 105 over
  2^8–2^23 blocks;
- with the ideal-model error at most 2^-129, both for the k = 88 row and for the slack rows.

**What each costs.**
- **Pinning** adds three statements and one definition (`MeetsWithSlack`) to the trusted layer, and no new model
  file. The statement review is GO after its docstring fixes, and all three grade PASS.
- **Not pinning** leaves F3's split and F6's buffer without a trusted-layer statement; they would stay proofs in a
  submission folder.

**Default: pin them.** *Decided: default, Daniel deferred, 2026-09-29.*

## F6. The buffer: k = 88, 96 or 105

**The choice.** How many sequential challenges an audit uses:
- **k = 88:** the least that the proof supports. It has no margin for structural leakage: a systematic saving above
  about 6 bits per block voids the proved bound.
- **k = 96:** absorbs 64 bits per block.
- **k = 105:** absorbs 128 bits per block.

The "bits per block" here cover only leakage that reduces to bounded, reusable per-block advice.

**What each costs.** Audit length grows in proportion to k: +9% challenges for 96, +19% for 105.
- **With an on-node verifier:** each challenge costs the honest prover a few microseconds (7.4 µs worst case in the
  MVP's run), so even 105 challenges add well under a millisecond per audit.
- **With a remote verifier:** each challenge costs one round trip, so a 128-bit buffer adds 17 round trips per audit.

**Default: k = 105.** *Decided: default, Daniel deferred, 2026-09-29.* It is cheap insurance while the XOR question (Decision 1) is open.

---

# Background and evidence

**What P2 is.**
- **Construction:** each weight block is encoded as c = ρ(σ_j(ρ(m + t_j))) over the prime p = 2^16448 − 21065. ρ is a
  modular square root, and σ_j XORs a fresh per-block mask.
- **Costs:** decode is two squarings. Re-encoding a dropped block costs at least one 16,448-bit square root, which must
  take longer than the audit deadline plus the round trip on the fastest allowed hardware (the timing assumption
  "SeqRoot").

**What is proved.** In Lean, unconditionally, in the abstract model M1, where each block is an independent ideal
permutation that anyone can evaluate forward and no one can invert:
- `P2MeetsM1B19Uncond`: the MVP's own instance, 2^19 blocks at 16,448 bits, with 88 challenges.
- `P2MeetsM1FamilyUncond`: every block count from 2^8 to 2^23 at 16,448 bits (about 0.5 MB to 17.2 GB), with 88
  challenges.
- `P2MeetsM1Uncond` (2^23 blocks), `P2MeetsM1W8192Uncond` and `M1MeetsUncond`.
- `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond` and `P2MeetsM1pW8192Uncond`: the same rows on P2's exact domain
  [0, p) rather than 2^w bit strings, for every payload width in range, including the MVP's 2,054 bytes. They were
  added on 28 Sep after the repo snapshot and are pending your review.

A named reviewer on a GPT model reviewed every statement and the A2 proof they rest on. Its verdicts were GO, or GO
once its wording fixes were applied.

**What it buys.** With fresh per-block keys derived on the device (the version the proof covers, inside the space
bound), P2 v2 decodes at **23.66 GB/s** on an L40S on Qwen2.5-0.5B, with every gate passing. That is **15.4× the band
scheme's 1,532 MB/s** on the same workload.
- **Source.** Measured by the POUS MVP owner; Attempt `r20260928-142137-28ac`. The run uses 2^19 blocks, the instance
  `P2MeetsM1B19Uncond` covers.
- **The shared key.** The shared-key build did 25.23 GB/s in the same run.
- **The expander.** The run uses ChaCha8. With SHAKE256, which the crypto review prefers, it would be about 21 GB/s,
  about 13.7× the band (*est.*, if the 12% device estimate holds).
- **Superseded.** The earlier 25.0 GB/s (Attempt `r20260928-081028-0c5f`) read CPU-derived keys from device memory,
  which is outside the space bound.
- **On an H100.** 14.75 GB/s, with the kernel not re-tuned; deriving the keys on the device cost nothing measurable
  there.

Both decisions below concern what sits outside Lean.

## Decision 1: accept "square–mask–square with fresh per-block keys behaves like M1's ideal permutation"?

**What the assumption says,** in the reviewer's formulation (P2–M1 storage-game indifferentiability):
- **Scope:** for weights fixed before setup, and fresh independent per-block mask and tweak pairs drawn after W, the
  following adversary is covered:
  - unbounded preprocessing that keeps at most S bits of state;
  - at most Q = 2^20 complete forward evaluations per answer;
  - answers within the deadline on the allowed hardware.
- **The claim:** that adversary succeeds no more often than in M1, up to a negligible ε_inst.
- **What it is not:** a claim that P2 looks like a random permutation. It is a claim about this storage game only.

**Evidence** (crypto review on a GPT model, plus the campaign's red teams):

| For | Against |
|---|---|
| It is a genuine permutation, and a fresh random tweak makes every target uniform after W | After naming the two roots as unknowns, P2 is **two quadratic equations joined only by a public XOR** over a mismatched domain. Whether a combined bit-level and field-level attack (SAT or MQ linearization with carries) can compress a block with **no root** is **open**; this is the main risk. *28 Sep: still open. Bit-level SAT turned out too weak to test it (it fails even the zero-mask control), and no integer or lattice route past a dense mask is known* |
| A dense uniform mask blocks every known route: the fourth-root collapse (with a zero mask, a small lattice recovers 10–16% of a block rootlessly), sparse and clustered masks, the multiplicative shift attack that refuted "RSA is an ideal permutation", and split hints on both roots (these needed at least 1.055w of advice in lattice runs at w = 128–256) | No reduction is possible: the sms5 reductions review shows no black-box reduction to a single-stage assumption exists for this construction class |
| The one known partial-knowledge attack (a stored hint skips one root) is understood and already priced into the 16,448-bit width | The same project has an exact precedent: "RSA is an ideal permutation" was **false** in this storage game, because algebraic structure let the adversary compress offline |
| Discrete-log and smoothness shortcuts are far outside budget: SNFS precomputation about 2^220, individual descent about 2^207, smoothness root-finding probability below 2^−2700 | **Key-expander gap:** per-block keys expanded from one short public seed are not independent against an unbounded preprocessor, as M1 requires. The expander needs its own named assumption, or must be idealized as an independent-output oracle. *28 Sep: now stated as P2-EXP-IO; see the evidence round below* |
| Distinguishers exist (root parity reveals the quadratic character; the key family is succinct), but none yields more than about one bit per block | Only about a day of internal review, with no external cryptanalysis. The algebraic-cipher literature (MiMC, Jarvis, Rescue, Poseidon, Anemoi) repeatedly shows that high inverse degree is not a security argument. *28 Sep: a literature pass and two small-width studies have been added; there is still no external review* |

**The prime.** 2^16448 − 21065 is ≡ 7 mod 8. Trial division leaves 16,417-bit and 16,402-bit cofactors of p − 1 and
p + 1. The special form makes discrete logs easier than for a random prime, but still far outside budget at this size.
A random prime removes that concern, but not the XOR question, and it roughly doubles the reduction cost.

*Certification (28–29 Sep).* **p is proved prime.** p ± 1 have too little factored structure for a cheap N±1 proof,
so the proof is an ECPP certificate.
- **The run.** Enge's CM, 339 steps, 2 h 39 min on 4 cores.
- **The checks.** PARI's `primecertisvalid`, CM's `ecpp-check` and the campaign's independent verifier all accept it.
- **The file.** SHA-256 `6a3f6f11…d3c5`, in `internal/efficient-crypto/p2-prime/`.
- **The alternative prime is no longer needed.** p′ = 2^16448 − 1213·2^8232 − 1, proved prime in Lean, matters only
  if a Lean-checked primality proof becomes a requirement.
- See `docs/efficient-crypto/p2-prime-certificate.md`.

**Confidence compared with the band.**
- **Band (Feistel-SHAKE):** moderate. It is heuristic, but it rests on a standardized, heavily analysed primitive and
  published 8-, 10- and 14-round Feistel indifferentiability results. It still carries the storage-game composition
  caveat.
- **P2 (square–mask–square):** low. The map is bespoke, minimally analysed, and has no reduction.

**Recommended default: do not accept yet.**
- **For now:** keep the band as the deployed secure scheme, and keep P2 as a flagged experimental option (the MVP
  already labels it "abstract-M1 result; instantiation assumption pending Daniel").
- **What would move this to "accept with conditions"**:
  1. a frozen public spec, including the key expander and the allowed hardware;
  2. external cryptanalysis aimed at compression, not ordinary distinguishing;
  3. a public bounty with reduced-width challenges that reward advice below (18/19)w answering without a root;
  4. a direct generic-model bound for "dense random XOR between two signed squarings";
  5. the key-expander question resolved;
  6. the Lean certificate rerun on the exact domain [0, p).

Source: `internal/efficient-crypto/attacks/p2-instantiation-review.md` (reviewer `crypto-review-p2-instantiation`,
gpt-5.6-sol-xhigh).

### Evidence round, 28 Sep (CPU only, under the GPU freeze): what moved

The campaign worked through the CPU-doable parts of the six items above. The same GPT reviewer then checked every
result. **The recommended default is unchanged: do not accept yet.** The reviewer's confidence also remains low. The
deployment-critical questions are still the unproved dense-XOR instantiation and the timing re-gate on the fastest
allowed hardware, which is frozen with the pods.

| Item | What was done | Moved? |
|---|---|---|
| 1. Frozen spec | Draft v0 with test vectors: exact maps, a one-exponentiation root, canonical encodings, key derivation, two payload profiles, and a "Before freeze" checklist | **Partly.** Not freezable until the prime has an ECPP certificate, Decision 2 is made, and the challenge, authentication and wire formats are specified |
| 2. Cryptanalysis aimed at compression | Internal only: a literature pass, a character and differential study, and a small-width SAT study | **Partly, internally; nothing external.** No attack on dense-mask P2 found. See the details below |
| 3. Bounty | A private kit: challenge ladder at w = 64–1,024, a verifier, and a zero-mask control that the verifier accepts as a real break | **Partly.** Ready to publish on your go. The rule is exploratory triage: a pass shows an attack, a fail proves no bound. Rewards and judging are yours to set |
| 4. Generic-model bound | The pure field-algebraic model is vacuous: it "proves" the broken zero mask secure. With the XOR replaced by an ideal permutation, a conditional bound holds under a new composable square-root assumption | **Partly.** It isolates the XOR question but gives no bound for the real dense XOR |
| 5. Key expander | Stated as the setup assumption **P2-EXP-IO**: keys come from fresh independent streams drawn after W is committed, which is how M1 already treats its permutations | **Moved, on paper.** Concrete SHAKE256 in its place stays a named storage-game assumption, in the band's primitive class |
| 6. Lean on the exact domain [0, p) | Proved: the 2^19 row, the 2^8–2^23 family and the 8,192-bit row, for every payload width from 15,665 to 16,447 bits (8,192-bit row: 7,802–8,191), including the MVP's 16,432. k is unchanged | **Partly.** The [0, p) part is reviewed (GO) and pinned as `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond` and `P2MeetsM1pW8192Uncond` (28 Sep, 12:38Z). They were added after the snapshot in PRs #162/#183 and are pending your review. The timing re-gate on the fastest hardware is not done |

**Cryptanalysis details (item 2).**
- **Literature.** The closest prior construction is Sloth's round of a root followed by a simple permutation. P2 is a
  two-root Sloth whose middle permutation is a public XOR.
- **Why the literature lowers confidence modestly.** A replica-encoding proof failed on exactly the argument "a
  missing block forces an inversion" (the Damgård–Ganesh–Orlandi proof, broken by Garg–Lu–Waters). There is also a
  black-box separation for incompressible encodings (Moran–Wichs).
- **Parallel-root attacks.** The 2024 attacks on Sloth++, VeeDo and MinRoot belong in the timing assumption's threat
  model. They don't weaken the 16,448-bit gate.
- **Character and differential study.** Dense-mask biases decay like a random function's, about 2^-8217 at
  deployment (*est.*), while the controls detect known structure.
- **SAT study.** An exact CNF solved with an off-the-shelf SAT solver fails the zero-mask control: it stalls at about
  8 dropped bits of c on every mask, while lattices recover hundreds of bits when the mask is zero. It therefore shows
  neither an attack nor resistance. Integer and lattice methods remain the only demonstrated rootless route, and none
  gets past a dense mask. Hybrid solvers that combine SAT or Gröbner with integer carries remain untested.

**New findings.**
- **The certificate margin is thin.** k = 88 absorbs only 6 bits per block of any structural saving. A larger k buys
  more:

  | Per-block saving absorbed | 6 bits | 32 bits | 64 bits | 128 bits | 256 bits |
  |---|---|---|---|---|---|
  | Least k | 88 | 91 | 95 | 103 | 125 |

  No k survives a saving above about 842 bits per block. **Option, not a change to any default:** raise k for a
  buffer, at the cost of proportionally more audit challenges.

  *Certified in Lean (29 Sep).* On the exact-domain model, against an adversary holding λ extra bits per block
  beyond ⌊(18/19)·|C|⌋:

  | λ bits per block | 0 | 64 | 128 | 256 |
  |---|---|---|---|---|
  | lower proved k, 2^19 blocks | 88 | 95 | 104 | 127 |
  | whole 2^8–2^23 family | 88 | 96 | 105 | 128 |
  | raw storage breaks it up to | k = 85 | k = 92 | k = 100 | k = 121 |

  - **The error split.** The ideal-model term also fits in 2^-129 for every row, leaving half of the 2^-128 budget
    for the instantiation and expander, given an additive reduction outside Lean.
  - **Status.** Proposed pins `P2SlackB19Uncond`, `P2SlackFamilyUncond` and `P2ErrorSplitB19Uncond`, in
    `lean/submissions/efficient-crypto/p2-margin/`. The statement review is GO after its docstring fixes, and all
    three grade PASS against a scratch layer. They are **not pinned**.
  - **What λ covers.** Only leakage that reduces to bounded, reusable per-block advice.
  - **Cost.** For a 64- or 128-bit buffer, k = 96 or 105 over the family: 9–19% more challenges than k = 88.
- **Mask reuse must stay forbidden.** Under a shared mask, the outer-root parity has a strong negation relation. With
  independent masks the relation disappears.
- **Key-expansion cost.**
  - Measured on this CPU: SHAKE256 expansion takes 9.1 µs per block, about 2.2× a two-squaring decode.
  - On the device, measured with ChaCha8: 23.66 GB/s, against 25.23 GB/s for the shared key in the same run
    (Attempt `r20260928-142137-28ac`). SHAKE256 is not measured on the device; the 12% estimate gives about 21 GB/s.
  - Switching to ChaCha8 for speed would add a weaker, reduced-round assumption.
- **The MVP deviates from the spec draft.** These are for the MVP owner:
  - the expander is ChaCha8;
  - the tweak is reduced by one subtraction of p, a negligible bias but nonconforming;
  - integers are little-endian on the wire;
  - the code cites a stale 2^23 pin.
  Its 2,054-byte payload is a conforming profile (`p2-2054B`).

Sources, all in `internal/efficient-crypto/` unless noted:
- `attacks/p2-seed-expander.md`, `attacks/p2-generic-bound.md`, `attacks/p2-literature.md`,
  `attacks/p2-character-bias.md` and `attacks/p2-sat-recovery.md`;
- the reviewer's section "Evidence round, 28 Sep 2026" in `attacks/p2-instantiation-review.md`;
- `p2-bounty-kit/`;
- `docs/efficient-crypto/p2-spec-draft.md`;
- `lean/submissions/efficient-crypto/p2-domain/`.

## Decision 2: may the adversary use several cooperating cores on one squaring?

The time model says "a CPU core or a GPU core". A 16,448-bit squaring is one big multiplication, and a multi-core CPU
can split it. The question is whether that split is in scope.

**Evidence.**
- **Literature:** no library threads a single multiplication at this size.
  - GMP never creates threads. FLINT's threaded FFT pays off only around a million digits, and 16,448 bits is about
    4,950 digits.
  - The sequential-squaring (VDF) literature treats each squaring's internal parallelism as the only speedup available.
  - The adversary that really threatens P2's width is a **custom squarer**, not a cluster of cores: about 25 ns per
    1024-bit squaring on an FPGA, projected at single-digit ns on an ASIC at 2048 bits. The time model's exclusion of
    ASICs (and, implicitly, FPGAs) carries as much weight for P2 as for the band.
- **Measured on this VM** (4-core Xeon, 4.0 GHz): a hand-built split of one dependent chain at p = 2^16448 − 21065, with
  every run verified against GMP.

| Cores | ns per squaring | Speedup |
|---|---|---|
| 1 (best single-core IFMA kernel) | 2,099 | 1 |
| 2 | 1,484 | 1.41× |
| 3 | 1,210 | 1.73× |
| 4 | 983 | 2.13× |

- **The limit is the exchange, not the flag.** Every squaring pays about 483 ns (4.6 core-to-core round trips) to
  exchange the 2.5 KB result, however many cores take part. The earlier estimate of 2.3–4.1× at 4–8 cores assumed a
  20–40 ns single hop; no known split achieves it.
- **Modelled for the fastest core** (Zen 5 at 5.7 GHz, 8 cores on one chiplet): **1.1× / 1.55× / 2.6×**, for an
  exchange costing 4.6 / 2.3 / 1 round trips. Crossing chiplets costs at least 150 ns and caps 8–16 cores at
  1.25–1.6×, so the useful adversary is one chiplet. One GPU warp is about 5× slower than the CPU floor, and a whole SM
  about 1.3× slower.

**Width forced for a 2× margin.** The deadline plus round-trip budget is 0.5 ms with an on-node verifier and zero round
trip, or 2.9 ms, the largest round trip the band is designed for.

| Adversary | 0.5 ms budget | 2.9 ms budget |
|---|---|---|
| 1 core | 8,000 bits | 16,448 bits |
| 2 cores | 8,000 | 16,448–17,328 |
| 4 cores | ≤ 8,544 | 18,064–22,592 |
| 8 cores, one chiplet | ≤ 10,368 | 21,568–28,176 |

Ranges run from a well-engineered exchange to the one-round-trip floor.

**Cost at those widths.** Decode per byte grows roughly linearly with w. From the covered 23.66 GB/s at 16,448 bits:
about 17 GB/s at 22.6 kbit and about 14 GB/s at 28.2 kbit (*est.*), still roughly 9–11× the band. At 22–28 kbit P2 costs
more per byte than P3 on heuristic ARX primitives, so at those sizes its only advantage is over the SHAKE-based band.

*Settled by F2 at the top:* F2 takes the 0.5 ms branch, where the existing 16,448-bit width already covers
cooperation within one chiplet.

**Recommended default: allow cooperation within one chiplet (8 cores), and size for the adversary-favourable end.**
- **Why:** every real server has many cores, and "a CPU core" was chosen to set the speed of a sequential step. Splitting
  one big multiplication is parallelism inside that step that ordinary hardware allows. The conservative reading costs
  about 1.7× in width and throughput, not a change of design.
- **Widths:** about 28,200 bits at the 2.9 ms budget, and about 10,400 bits if the verifier round trip is confirmed to be
  near zero.
- **Measure the verifier's real round trip first:** it moves the width by up to about 2.7×, far more than the cooperation
  question does.
- **If you choose the literal one-core reading instead:** 16,448 bits stands, and the timing assumption must then say
  explicitly that one squaring is not split across cores.

Source: `internal/efficient-crypto/candidates/p2-coop-cores.md` (worker `cpu-p2-coop`; code in `p2-coop-cores/`). The
Zen 5 figures are modelled, since pods are frozen.

## Corrections and gaps folded in

- **Which throughput the proof covers.** The Lean pin covers only fresh per-block keys (M1). The campaign's GPU
  benchmarks used a shared mask with linear tweaks (M2), which the proof does not cover. Those figures include the 24.2
  GB/s tuned kernel at 16,448 bits. The covered figure is the MVP's **23.66 GB/s** for P2 v2, with per-block keys
  derived on the device (Attempt `r20260928-142137-28ac`). That is 6.2% below the shared-key build's 25.23 GB/s in the
  same run. The earlier 25.0 GB/s (Attempt `r20260928-081028-0c5f`) read CPU-derived keys from device memory, outside
  the space bound. The scout's early cost estimate and its k = 101–102 bound were also M2.
- **Block count: closed.** The MVP runs 2^19 blocks (8 segments of 65,536), but the first pin was at 2^23. Two new
  unconditional pins now cover it, both proved in Lean with only Lean's standard axioms:
  - `P2MeetsM1B19Uncond`: exactly 2^19 blocks at 16,448 bits, with k = 88 challenges.
  - `P2MeetsM1FamilyUncond`: any block count from 2^8 to 2^23 at 16,448 bits, with k = 88.
- **How low k can go.**
  - 88 is the least challenge count this proof route gives. At k = 87 no certificate exists, because each block costs
    at least 20 bits of advice in Lemma A.
  - k = 85 is refuted in Lean at 2^19: storing as many blocks raw as fit in the space budget already passes the audit.
    This also shows the family statement is not vacuous.
  - k = 86 and 87 are neither proved nor refuted. Closing that gap would need a sharper Lemma A, not a better
    certificate.
- **The review of the block-count pins.** The reviewer was `statement-review-p2` (gpt-5.6-sol-xhigh). It gave GO for
  the 2^19 pin. It gave GO WITH CONDITIONS for the family, which became GO once two docstring fixes were applied. It
  independently rechecked the 88-versus-87 arithmetic and the k = 85 counterexample.
- **The scope is unchanged.** These are still abstract-M1 results. The timing assumption, the instantiation assumption
  (Decision 1) and the domain [0, p) versus 2^16448 all sit outside Lean, as before.
- **Device-side key derivation: measured** (by the POUS MVP owner).
  - **The gap it closes:** the earlier run derived the per-block keys on the host and read them from device memory.
    That is about 2 GB of keys for a 0.99 GB model, which breaks the 1.05× space bound.
  - **P2 v2** derives the keys on the device with ChaCha8. It reaches 23.66 GB/s on an L40S with every gate passing,
    against 25.23 GB/s for the shared key (Attempt `r20260928-142137-28ac`).
  - **On an H100** (14.75 GB/s, kernel not re-tuned), device derivation cost nothing measurable.
  - **SHAKE256**, which the crypto review prefers, is not measured on the device: about 21 GB/s (*est.*, 12%).

## Summary

| Decision | Recommended default | Main reason | What would change it |
|---|---|---|---|
| 1. Accept the square–mask–square instantiation | **Not yet**; keep the band deployed, P2 experimental | Low confidence: a bespoke algebraic map with no reduction, an open rootless-compression question, and the RSA precedent | External compression-focused cryptanalysis, a published bounty, a bound for the real dense XOR. As of 28 Sep, the key expander is resolved on paper (P2-EXP-IO) and the exact domain is proved in Lean |
| 2. Cooperating cores on one squaring | **Allowed within one chiplet**; w ≈ 28,200 at 2.9 ms (≈ 10,400 at 0.5 ms) | Real servers have many cores; the measured and modelled speedup is 1.1–2.6× at 8 cores | A measured verifier round trip; a decision that the time model means one physical core per squaring |
