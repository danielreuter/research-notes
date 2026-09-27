---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: open · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# One weights root reused across many proofs: soundness, binding, hiding, zero knowledge, leakage, linkability

The long form of `backends/flock/verifier/lean/soundness/DESIGN.md` §10, summarized in `ASSUMPTIONS.md` §7 (Daniel's
question, 2026-09-26; older references to ASSUMPTIONS.md §4.3 and §12 are now `DESIGN.md` §2 and §9). The setting
is the architecture's: the weights are committed once as Halevi–Micali leaves under a Merkle root, registered as the
model's anchor. Every later proof publishes the commit strings `b ‖ c` of the rows it reads, and the verifier checks
their paths to that root (`docs/boolean-core-architecture.md` §1.5–1.6). Sources: `hm96-sha256/v1`'s PROTOCOL.md on
`main` (hiding and binding), `docs/circuit-privacy.md` (leakage function L, §8's theorem list), and ASSUMPTIONS.md §4.3.

## 1. Soundness over N tables

- **The union bound.** Each table's bound holds for every prover strategy, and the history of earlier sessions is part
  of that strategy. Each session's coins are fresh. So
  `Pr[some accepted table is false] ≤ Σ_tables (2^-195.5 + t·√2·S_m/2^256 + t²/2^511)`.
  - Add the root's binding once: the straight-line reduction watches all proofs, costing `t²/2^513`.
  - `t` is the adversary's cumulative work, because every collision finder `B` may use all of it.
- **The rewinding term is linear in the number of tables `N`.**
  - By Cauchy–Schwarz, `Σ_s √(NQ·Adv_s) ≤ √(N·NQ·Σ_s Adv_s)`.
  - A finder that forks one random session has `Σ_s Adv_s = N·Adv(B)`, with `Adv(B) ≤ (2t)²/2^513`.
  - So the total is `N·t·√2·S_m/2^256`. Forking all sessions at once isn't possible, since a fork changes later
    sessions.
- **Budgets for 2^-128 in total** (m = 35, `log2(√2·S_m)` = 17.3):
  - the statistical part needs `N ≤ 2^67.4`;
  - the hash part needs `N·t ≤ 2^110.7`.

| Adversary work `t` | Tables `N` within 2^-128 |
|---|---|
| 2^64 | 2^46.7 |
| 2^80 | 2^30.7 |
| 2^94 (a year of Bitcoin-scale hashing) | 2^16.7 |
| 2^100 | 2^10.7 |

- **In the random-oracle model** the hash term is global: straight-line extraction gives `t²/2^511` once, not per table.
  So the lifetime number in that model is `N·2^-195.5 + O(t²/2^512)`.
- **The per-table security level stays high** (`t/ε ≈ 2^238.7`). The budget only bites for a single lifetime number at
  large `t`. This is a statement decision, not a protocol change.
- The sampling layer (which units are proved) has its own law and error, outside this note.

## 2. Binding over the root's lifetime

- **Tree binding is straight-line.** Two proofs that publish different commit strings at one position with valid paths
  are a collision, and both openings are public. So the root needs collision resistance only against the adversary's
  cumulative work: `t²/2^513` for SHA-512 (2^-313 at `t = 2^100`), or `t²/2^257` for SHA-256, which is 2^-128 only up
  to `t ≈ 2^64.5`.
- **So a long-lived root must use the SHA-512 leaf and tree scheme.** `hm96-sha256/v1` over vllm-v1 trees (today's
  scheme) is not enough at Daniel's 2^80–2^100. The re-baseline moves data commitments to SHA-512, and the weights root
  should be committed after that switch, or rotated right after it.
- **How long binding must hold:** as long as anyone relies on the root, including disputes about old proofs. After a
  break of SHA-512, someone could claim the root commits to other weights.
- **Binding needs no time limit.** Collision resistance doesn't decay with age; only the adversary's cumulative budget
  grows, and SHA-512's margin covers it.
- **Rotation triggers:**
  - a cryptanalytic advance on SHA-512 (full SHA-512 has no known collision attack better than generic; published
    attacks reach reduced-step versions only);
  - exposure of the salts or the key;
  - a planned hash upgrade.
- **Rotation mechanics:**
  - fresh key and salts;
  - a one-time proof that the old and new roots open to the same weights ("same as registered" in `circuit-privacy.md`
    I.5: open both, compare). It costs about 453 ANDs per byte, about 6e13 ANDs for 140 GB of weights, roughly half
    of one #101 run.
- **Quantum.** Straight-line tree binding needs only quantum collision resistance (BHT 2^170.7), with no rewinding. The
  witness-level link (section 6) inherits ASSUMPTIONS.md §12's caveat.

## 3. Statistical hiding of Halevi–Micali leaves under reuse

- **Reuse adds nothing.** Every proof republishes the same commit strings, so the joint view over any number of proofs
  holds the same `N_leaves` commit strings. The bound is fixed by the root's leaf count (hm96 PROTOCOL.md §3):
  - `N_leaves·2^-256` with a key drawn at commitment (`fresh_key`);
  - `N_leaves·2^-192` with the pinned key, except for a one-time `2^-64` fraction of keys (the common-reference-string
    step).
- **Draw the root's key at commitment.** It removes the 2^-64 step, and costs nothing: the key is then a constant of
  every circuit that reads this root.
- **Salts:** never reuse one (two leaves with one salt reveal `x ⊕ x'`), and a rotation draws fresh ones. Salts are as
  secret as the weights for the root's lifetime. If they leak, the unsalted digests `x` become computable, which lets
  anyone confirm guesses of rows.

## 4. Zero knowledge under composition

- **Honest-verifier ZK composes sequentially and concurrently.** Sessions are simulated independently from their
  statements, and statistical errors add per session.
- **Malicious-verifier ZK with the step-0 seed composes sequentially.** Auxiliary-input zero knowledge is closed under
  sequential composition (Goldreich–Oren 1994), which is the hybrid `circuit-privacy.md` §8 plans ("Many runs").
- **Many simultaneous sessions against a malicious verifier are not covered.**
  - The simulator learns each session's committed seed by rewinding, and a verifier that nests sessions can make that
    rewinding blow up. This is the classic concurrent-ZK problem.
  - Black-box concurrent zero knowledge needs Ω̃(log n) rounds of a special preamble (Canetti–Kilian–Petrank–Rosen
    2001; Prabhakaran–Rosen–Sahai 2002 achieve it), or setup (a common reference string, timing assumptions, public
    keys).
- **Options, a design decision:**
  - **Serialize sessions.** Per verifier works only if one party can't hold many verifier identities; otherwise
    serialize globally. `circuit-privacy.md` §8 already says "serialize them, or scope them out".
  - **Take the coins from a public beacon**, so no verifier chooses them. Honest-verifier ZK then suffices, concurrently.
    But soundness rests on the beacon being unpredictable when each round's bytes are recorded, which needs trusted
    timestamps, and rounds slow to the beacon period (about 10 minutes per table at 3 s × 200 rounds).
  - **Scope concurrent malicious-verifier ZK out.** That is fine if only the project's own coin server runs sessions,
    since against it honest-verifier ZK is the relevant property.

## 5. Accumulated leakage from the statements

- **Zero knowledge hides the witness beyond the statement, never the statement itself.** Over N sessions, the joint
  view is simulatable from the N statements (`circuit-privacy.md`'s `L(A, x_i)`). It reveals:
  - workload shapes (token counts and positions, request counts, time windows);
  - timing;
  - linkability;
  - every proved predicate, with its parameters and truth.
- **What doesn't leak:** weights never appear in a statement, and outputs stay committed. Clients see their own
  outputs through serving. That is the model-extraction channel of any API, not of the proof.
- **Predicates are the channel the proof adds.** A predicate over committed outputs gives whoever sees it one bit per
  proof. Over many chosen inputs that is an oracle to the model. So decide which predicates are public, and bound their
  number per model or per counterparty.

## 6. Linkability

- **Linkability is intended, and it is also a leak.** The one root ties every proof to the registered model. Everyone
  seeing two proofs knows they come from one model, and with timing, that model's traffic.
- **Unlinkability would cost too much per run.** It needs a fresh commitment per run and an equality proof ("c and c′
  open to the same Enc(C)", `circuit-privacy.md` I.5), re-hashing the weights and proving about 453 ANDs per byte each
  time. That is affordable at rotations only.
- **The link's soundness needs knowledge soundness.**
  - A statistically hiding leaf has openings to essentially every row (information-theoretically). So "some witness
    with these commit strings satisfies the circuit" says nothing about which weights were used, even for one proof.
  - Our theorem's committed witness (the plurality table, decoded) is a specific object. Showing that its rows equal
    the registered weights `W` means computing it, and then applying Halevi–Micali binding against the registrant's
    opening `(W, R)`. That is an extractor: knowledge soundness.
  - For provers that hold their table, extraction is straight-line: decode it. For arbitrary provers it is a rewinding
    extractor that samples the plurality at every position (about `N/Q` runs per position class) and list-decodes.
  - It is standard for Kilian-style arguments, but it is a separate theorem with its own concrete bound. It is not in
    the theorem list yet.
  - `circuit-privacy.md` §8's composition theorem ("the committed outputs equal the registered architecture evaluated
    on the committed weights and inputs") needs it for the same reason.
