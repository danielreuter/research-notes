---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: decided (Daniel, 2026-09-27: batched, serialized sessions) · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# Zero knowledge against a malicious verifier: the options weighed (decision-time analysis)

This is `backends/flock/verifier/lean/soundness/DESIGN.md` §11 as it stood before the decision, moved here verbatim.
`DESIGN.md` §11 now states the decided model: batched, serialized sessions with single-rewind simulation. It keeps
Prabhakaran–Rosen–Sahai and registered verifier keys as reserve notes. Section references are to `DESIGN.md`.

## The analysis

**The target.** Daniel, 2026-09-26: the verifier is malicious (two nations checking each other), so honest-verifier zero
knowledge is not an acceptable fallback anywhere. The target is zero knowledge against a malicious verifier, including
many concurrent sessions.

**The lemma every option uses** is special honest-verifier ZK (SHVZK): a simulator for every fixed coin sequence.

- VEIL proves exactly that for its compiler: a simulator whose output equals the real view "for any value of verifier
  randomness" (perfect; Lemma 4.3). Its footnote names the notion "semi-malicious", and Succinct has machine-checked
  the paper's statements in Lean.
- Masked Flock (M1, VEIL-style) must keep that property on binary fields:
  - every leaked GF(2^128) value needs 128 uniform mask bits whose weights span;
  - ring switching must be covered;
  - adversarial out-of-domain points or repeated query positions must not reveal more than the padding covers.

  So the prover must reject degenerate coins, as VEIL's generators exclude a zero mask coefficient.
- What remains is stopping the verifier from choosing coins adaptively, and simulating without rewinding across
  sessions.

**(a) Serialize all sessions.**

- **Zero knowledge.** Coins are committed per round with HM96 at step 0, and a Goldreich–Kahan simulator makes one
  extraction run, then one rewind. Sequential composition of auxiliary-input zero knowledge (Goldreich–Oren 1994)
  covers session after session. Collision resistance only, no setup.
- **Cost.** One session at a time, each about 220 round trips (live, per the scoping estimate).
  - With the counterparty's coin server co-located with the prover (sub-millisecond round trips, as Phase B plans),
    that is 0.1–0.2 s per session, negligible next to proving.
  - Across a border (50–150 ms round trips) it is 11–33 s per session. Each session must then carry many tables in
    lockstep, up to a whole run's (the batch is bounded by prover memory), or throughput falls by the idle fraction.
- **Identities.** A counterparty can defeat per-identity serialization by running sessions under several identities and
  pooling their views. So serialization must be global: at most one session at a time with anyone who could collude with
  the counterparty, which in a bilateral setting means everyone.

**(b) Coins from a joint public beacon.**

- **Zero knowledge: yes, straight-line.** If every coin comes from a beacon that releases its values on schedule
  whatever the prover sends, the verifier chooses nothing. The simulator waits for the values and runs the SHVZK
  simulator. There is no rewinding, so concurrency costs nothing, and quantum verifiers are covered as well.
- **The beacon must not be the counterparty's.** One that can hold back a value until it has seen the prover's message
  forces rewinding again, and one the prover controls breaks soundness. "Joint" therefore means a third party or a
  threshold of them (drand's League of Entropy), or a VDF beacon.
- **Soundness then assumes:**
  - each round's bytes are recorded before that round's beacon value is released (the verifier's clock);
  - the beacon is unpredictable to the prover and unbiasable by it. For drand, that means fewer than a threshold of its
    members collude with the prover, plus BLS unforgeability over pairings: not collision resistance, and not
    post-quantum.
- **Cost.** Rounds pace to the beacon period: about 11 minutes per table at drand's 3 s.
- **Side effect.** With trusted timestamps, transcripts become transferable evidence rather than deniable ones. The
  weights stay hidden either way.

**(c) A straight-line-extractable coin commitment.**

- **Encryption to a key the simulator holds.** In the common-reference-string model, that key is a trapdoor someone
  generated: trusted setup, excluded.
- **Registered verifier keys** (the bare public-key model, Canetti–Goldreich–Goldwasser–Micali 2000).
  - Each verifier registers a public key once, with a proof of knowledge of its secret key. It then encrypts its
    per-round coins under that key, with perfectly binding encryption opened round by round.
  - The simulator extracts the secret key once, at registration, and afterwards decrypts every session's coins
    straight-line, so concurrency costs nothing.
  - There is no trusted party, but there is a public-key assumption (LWE, for post-quantum) and a registration phase
    before sessions.
- **The observable random-oracle model** (Pass 2003; Canetti–Jain–Scafuro 2014). The verifier commits with HM96 as
  today, and the simulator reads the coins off the verifier's SHA-512 queries. It is hash-only and setup-free, but zero
  knowledge then rests on the random-oracle model (soundness is unchanged), and quantum queries cannot be observed.

**(d) Standard concurrent-ZK techniques.**

- **Commitment first.** Public-coin protocols like Flock's cannot be black-box concurrent ZK as they stand
  (Pass–Tseng–Wikström 2009). Committing the verifier's coins first, as in (a), is the necessary first step.
- **Prabhakaran–Rosen–Sahai (2002).** A preamble of ω(log n) slots after the coin commitments lets a recursive rewinding
  simulator extract every session's coins in polynomial time. It needs collision resistance only and no setup, and
  gives real concurrency. The cost is a few dozen extra round trips, and a simulator whose proof and concrete bounds
  are heavy: a large formalization.
- **The timing model (Dwork–Naor–Sahai 1998).** Bounded delays and prover-imposed time-outs keep sessions from nesting.
  It needs collision resistance plus a timing assumption, and is paid for in latency.
- **Non-black-box simulation (Barak 2001)** is impractical here.

**Recommendation,** under Daniel's constraints (collision resistance only where possible, no trusted setup, a malicious
verifier):

1. **Now: (a), global serialization.** Co-locate the counterparty's coin server with the prover, and batch a run's
   tables into one session in lockstep. It needs only collision resistance (the HM96 coin commitments) and the
   Goldreich–Kahan simulator already planned. The cost is operational.
2. **If concurrency is required: (d), a Prabhakaran–Rosen–Sahai preamble.** It is the only option that keeps collision
   resistance only and no setup while allowing real concurrency. The price is extra rounds and a much harder proof.
3. **Otherwise:** (c) with registered keys is the cleanest concurrent option, if Daniel accepts one public-key
   assumption. (b) fits only if both nations accept a third-party beacon for soundness. Both are straight-line, so they
   also sidestep quantum rewinding (§9), which (a) and (d) would need.

All four rest on the SHVZK lemma for masked Flock, which is the first zero-knowledge theorem to prove.

### 11.1 Batching inside one serialized session (Daniel's route, 2026-09-27)

Daniel's constraints are exactly one verifier and no trusted third parties (so no beacon), and throughput matters. His
route: one session carries every table from a time window, and many GPUs or datacenters prove them in parallel. The
verifier commits once, at step 0, to the whole coin schedule. Sessions are serialized, and each is arbitrarily large.

1. **Zero knowledge needs only the sequential, single-rewind simulator.**
   - A session is one protocol with one commitment, however many tables and machines it spans. What forces repeated
     rewinding is several commitments interleaved in time.
   - The Goldreich–Kahan simulator makes one extraction phase: an honest prover on a dummy witness. That is
     indistinguishable from a real run until the final openings, because every earlier message is masked and those
     openings come after the last coin. It then rewinds once, to just after step 0, and simulates every table from the
     extracted coins by SHVZK. The tables' masks are independent, so their simulations compose. The simulator runs in
     expected polynomial time, handling aborts as Goldreich–Kahan do.
   - Serialized sessions compose sequentially.
   - **Conditions:** every prover machine checks each revealed coin against the same step-0 commitment before answering.
     No other interactive zero-knowledge protocol with the verifier (predicates, openings, recursion's outer proof) runs
     alongside a session, unless it is straight-line.
2. **Sharing coins across tables costs no soundness.** Each table's bound holds for every prover strategy, and the other
   tables are just part of that strategy. Each table's coins are still uniform, so the union bound gives
   `Σ tableError` over the session's tables, exactly as for separate sessions. Three conditions:
   - every table's statement and root is in round 0, before any coin;
   - a round's coins are released only after that round's bytes are recorded for every table that uses them. With
     identical coins that is a barrier across machines. Streams derived per table from the one commitment
     (domain-separated) avoid the barrier and keep the single rewind;
   - the two reps of one table keep independent coins, derived per (rep, round). Squaring 2^-97.8 into 2^-195.5 needs
     it.
3. **Latency.** A session lasts one machine's proving work plus about 220 round trips, paced by the slowest machine. With
   tables spread across GPUs, that work is about one table, 0.5–1 s.
   - That gives about 1–2 s with a co-located coin server, 3–16 s across datacenters in one region, and 11–33 s across a
     border.
   - Sessions run back to back, so the batching window equals the session length, and a table waits at most window plus
     session: twice the session length.
   - Throughput scales with machines, not concurrency, until prover memory limits the tables a machine holds in lockstep.
   - The one verifier can run a coin-server instance beside each datacenter, all opening the one committed schedule.
     That keeps round trips sub-millisecond everywhere.

**If batching failed: Prabhakaran–Rosen–Sahai costs.**

- **Structure.** The verifier commits to its secret σ and to 2k² shares of it (`σ⁰ᵢⱼ ⊕ σ¹ᵢⱼ = σ`). Then come k slots,
  each one round trip: the prover sends k random bits, and the verifier opens one share of each of k pairs.
- **Slots.** A session gets the simulator stuck with probability at most `2^-(k − O(h))`, where h ≈ log₂ of all slots in
  the schedule, union-bounded over the N concurrent sessions. So `k ≈ λ + log₂ N + O(log(N·k))` for simulation error
  2^-λ. Taking the hidden constant as 2, that is about 125 slots at λ = 80, N = 2^10, and 170–210 at λ = 128,
  N = 2^10–2^20: 55–95% more round trips than Flock's 220.
- **Growth.** k grows by about 3 slots per doubling of N, and does not depend on session size.
- **Per-session overhead.** 2k² commitments to σ, plus k² openings.
  - In Prabhakaran–Rosen–Sahai, σ is the verifier's challenge, and ours is a whole coin schedule: about 20 KB per
    table schedule, or 4–5 KB if coins are cut to the bits used. So the shares alone are 0.1–2 GB per session.
  - Protecting a short trapdoor instead means an FLS-style OR-branch in the proved circuit and a
    witness-indistinguishable argument for it: a redesign.
- **Lean.**
  - A malicious-verifier ZK framework for the `Game` model (views, simulators, rewinding access).
  - The Goldreich–Kahan simulator, about 1,000–1,500 lines, which batching needs too.
  - The recursive simulator and its random-tape counting argument, about 3,000–5,000 lines; Pass–Tseng–
    Venkitasubramaniam's simplified analysis is the one to formalize.

  That is several times the knowledge-soundness work.
- **"Exactly one verifier"** does not simplify it, because the concurrent model already has one adversarial verifier
  controlling every session. It does make global serialization enforceable, with no identities to multiply. It also
  makes registered keys trivial: one key, registered once with no concurrency, then straight-line simulation, at the
  price of a public-key assumption (LWE).

**Recommendation: batching.** It meets throughput with serialized sessions, and needs only collision resistance plus the
single-rewind simulator we need anyway. Prabhakaran–Rosen–Sahai's rounds, bandwidth and proof stay off the table. If
real concurrency is ever needed, a single registered verifier key is cheaper than Prabhakaran–Rosen–Sahai, if LWE is
acceptable.
