---
id: 20261006T0229Z-draft-proof-service-pous
campaign: memory-accounting
lane: memory-accounting
kind: draft
status: open
repo: verity
origin: bc-15ada664-f325-5371-a473-65d408be3cf5
---

Restated for Daniel's ruling of 5 Oct, 7:48 PM PDT: PoUS is zero-knowledge; there is no clear mode.

# PoUS as a user of the proof service

This is a read-only review of PoUS on origin/main c305471c5 (after the Lean move, 7b410fbf6), against proofs' design
(Project store `internal/recursive-zk-system-architecture.md`, 5 Oct, 4:55 PM PDT). It is memory-accounting's input to
@proofs' joint note `proof-service-architecture`. Paths are relative to `verity/protocols/accounting/space/pous/` unless
they start with `benchmarks/`. The scheme written up is P2 v3 (`p2-16448/v3`). The band, dense and P3 appear only where the
graded and continuous audits, or the band's 64 KiB block, matter. The window is Daniel's ruling in #1159, Δ + RTT ≤
500 + 354 µs = 854 µs. #1159 is not on main yet, so main still has `ROOT_CALL_NS = 2_900_000` and `reference.py`'s
`MAX_RTT_ALLOWANCE_NS = 1_000_000`.

Under the ruling, the verifier never sees W or C\*. The public-encoder setup (`setup.verifier_key_from_encoding`, which
decodes all of C\* on the verifier) goes. The encoding is proved over committed data, and every answer is proved after
the session against a commitment sent inside its deadline.

Labels: **[M]** is measured, with its run or artifact id. **[C]** is computed from measured figures, with the arithmetic.
**[E]** is estimated, with the arithmetic or the model. The circuit counts come from a model (`/tmp/zkcost.py` on this
agent's VM, not committed). Its inputs are C-Flock's measured gadgets: SHA-512 compression at 81,402 ANDs and the hm96 row
tail at 241,490, both [M] from `sha512_circuit.compression(1).counts` and `hm96_row().counts`
(`internal/private-circuit/arch-designs.md`). It also uses Keccak-f[1600] at 24 × 1,600 = 38,400 ANDs (one AND per χ bit),
and a full adder at one AND. C-Flock has no 16,448-bit multiplier, so the squaring counts are not a traced circuit.

Three findings shape the rest.

- **The setup proof is the expensive piece, and non-native arithmetic dominates it.** C-Flock proves over GF(2). XOR is
  free, but every carry of P2's 16,448-bit squarings is an AND. A block's setup statement is about 6.3e7 ANDs [E], 92% of
  them in its two squarings.
  - Exhaustive: about 3.0e13 ANDs per GB of W [E]. That is about 1,300 recursion sessions, 2.9 GPU-hours of outer proving,
    25 GB of proofs and about 16 hours of Lean verify per GB [C].
  - Sampled `subset:s`: s = 2,759 blocks (ε = 1% at 2^-40) or 8,828 (ε = 1% at 2^-128), whatever |W| is. That is 8 or 24
    sessions [C]. It costs a Lean restatement, an effective ρ of 18/19 · (1 − ε), and k raised from 105 to 120 or 140.
- **Hashing an answer inside the deadline and proving it later is sound only if the hash absorbs a fresh verifier nonce
  before the block.** A prover-salted commitment, hm96's inner `x = H(block)` included, can be precomputed. A prover then
  stores 64 bytes per 2,056-byte block, 3.1% of C, and passes every audit, while the certificate needs about 18/19 of C.
  @proofs accepted this. Their interface gives `commit` a nonce-bound form and names the possession claim (R1).
- **The service's draw is computed and sent whole before the session.** PoUS needs each index revealed only after the
  previous answer, from a secret held on the node, inside a sub-millisecond loop (R2).

## 1. What PoUS owns today that the service would replace

| Piece | Path on origin/main | What replaces it | What PoUS keeps |
|---|---|---|---|
| Commitment to W | `setup.commit`, `_commitment_hash` and `COMMIT_TAG` (a hand-rolled streaming copy of `identity.tagged_sha256`); `protocol.commit`; `benchmarks/pous/p2_v1/reference.py` `w_commitment` and `W_COMMITMENT_LABEL`; vLLM `protocol_options/pous.py` `_commit` | The service's hiding commit of W as 2,054-byte payload rows under hm96-sha512, registered once and shared with PoUW (R9) | The manifest and `layout.Layout`, which say which bytes are W. Both become the developer's private data |
| The vk tree over C's leaves | `verifier.py` (`leaf_hash`, `node_hash`, `MerkleTree`, `verify_path`, `VerifierKey.check` and `check_path`), with `labels.tag`, `labels.salt_value` and `params.SALT_BITS`; a second leaf framing in `p2_v1/reference.py` (`leaf`, `root`, `epoch_id`); `leaves.bin` written by `benchmarks/pous/band_gpu/harness.py` | The prover's commitment of C under hm96-sha512 hiding leaves and the service's frame-v3 tree over them. Openings are checked inside proofs, never natively on a value | What a leaf commits: block i of C |
| The salt | `setup.draw_salt` and `SALT_DOMAIN`; `p2_v1/reference.py` `setup_salt`; `p2_v1/harness.py` `SETUP_SOURCE`, a fixed bench constant; vLLM's `salt_source`, with an `os.urandom` placeholder | A live coin drawn after W's registration, kept on the record, and a public input of the setup proof | The rule that the salt comes after the commitment, and its 24-byte width |
| The challenge draw | `audit.challenge_key`, `CHALLENGE_DOMAIN` and `TimedVerifier.challenge` (`key.uniform(B, j)`); `protocol.challenge_key`; `p2_v1/reference.py` `audit_key` (`audit-id/v1`, `audit-challenge/v2`); the `os.urandom(32)` sources in `band_gpu/live.py` and `p2_v1/live.py` | The service's draw in a sequential mode, revealing index j with its nonce under the Goldreich–Kahan coin commitment (R2) | `k` and the law, which come from the certificate |
| The continuous arrival schedule | `continuous.run_continuous`, whose `wait` the caller supplies | The service's coins | `n` and the miss budget |
| The timed verifier | `audit.TimedVerifier` and `run_timed`; `protocol.Verifier`; `continuous.ContinuousVerifier`; the hand-rolled loop in `p2_v1/live.py`; #1227's Lean loop (`benchmarks/pous/timing_loop/`, not on main) | The service's verifier gateway in a timed mode. It receives commitments, not answers | The acceptance rules (strict, the continuous miss budget, graded) and `audit.simulate`, the oracle-model audit that tests replay |
| Transport and RTT calibration | `band_gpu/live.py` (`LiveResponder`, the `<QQ` request and `<QQQ` header wire, `OP_CHALLENGE`, `OP_PING`, `OP_CLOSE`, `calibrate`, `limit_of`, `LogicalClock`); on the server side `band_gpu/harness.py` `ControlResponder` and the socket loop in `band_gpu/pous_native.cu`; `continuous.Reply` with `send` and `receive`; vLLM's in-process responder | The service's transport between the two gateways, and its RTT measurement before each audit | The device read that serves block i to the prover gateway, which is prover-worker code, and the value, late and recompute controls as test responders |
| Records | `live.py`'s audit JSON (the source, each answer's time, device and server ns, verdicts); `audit.Answer` and `AuditResult`; the harness's result JSON | The service's record: the coin commitment and its openings, each answer's commitment, the on-time bit per round (exact times stay on the verifier gateway), the after-session proof and the verdict | Nothing on the record. Device and server time are benchmark measurements only and leave the record |
| The setup verifier | `setup.verifier_key_from_encoding` (public encoder, which goes), `setup.verifier_key` (private encoder), `verifier_setup`, `protocol.verifier_key`, `check_server_root` | The service's setup proof: `P2Decode` proved over committed W and committed C, over every block or a `subset:s` draw, with its setup profile | `decode_segment`, and the decode relation stated as a Program |
| Gateways | None: answers leave the responder in the clear | The prover gateway (it salts, adds the nonce and commits each answer inside the deadline) and the verifier gateway, both in every round | Nothing |
| Randomness primitives | Already core's (`verity.primitives.randomness`); PoUS owns only its domain strings | Nothing new | The scheme's key expansion (`schemes/p2.py` `shake_keys`), which is part of the encoding, not a challenge |

PoUS also keeps everything that is the scheme or its guarantee: `schemes/`, `codec.py`, `layout.py`, `primitives.py`,
`oracle.py`, `adversary.py`, `Certificate`, `StorageProfile` and `LOCAL_CLAIMS` in `protocol.py`, the Lean under
`verity/Security/.../Pous/`, the GPU kernels, and the benchmark's measurements (kernel gates, the synthetic loop, SeqRoot,
NVMe). The Lean grader (`lean/Grader`, `grade.sh`, `TRUSTED.sha256`) judges Lean submissions, not audits, so it stays.

Moving the verifier loop into the service also settles the consolidation note's first fix
(note:20261005T2318Z-draft-consolidation): the session's `k`, `Δ` and call time come from the certificate that PoUS passes
in, so P3's defaults (`CHALLENGES = 132`, `CALL_NS = 242_000`) can no longer reach a P2 audit.

## 2. PoUS as a service user

### The four things

1. **What is committed.**
   - W, once, as hm96-sha512 hiding rows of 2,054 bytes, one per P2 payload, so that block i of C decodes to row i. This
     is the same commitment PoUW proves inference against (R9).
   - C, by the prover, as hm96-sha512 hiding leaves (one per 2,056-byte block) under a frame-v3 root, registered before
     the setup draw.
   - Each audit answer, inside its deadline, as the nonce-bound commitment `A_j` of R1.
2. **Which units are checked.**
   - At setup, every block, or a `subset:s` draw of blocks from a coin drawn after C's root is registered.
   - In the audit, k indices uniform with replacement over the B blocks: k = 105 with an exhaustive setup, and 120 or 140
     with a sampled one. Index j and its nonce are revealed only after `A_{j−1}` is in, or after its hard deadline
     passes. Every answer is proved and none is sampled, because the certificate needs all k correct and on time.
3. **The check each unit passes, as a public Program.**
   - Setup, `P2Decode`: open C's leaf i to a 2,056-byte `c` with `c < p`, and W's row i to a 2,054-byte payload. Derive
     `(K, t)` from `shake_keys` at the public salt, segment and block. Check `sq(σ_K(sq(c))) − t mod p` equals the
     payload.
   - Audit, `AnswerOpens`: `A_j` opens, with `nonce_j` in its inner prefix, to the same 2,056 bytes as C's leaf `i_j`.
   - The deadline is not a Program. It is a property of the record: `A_j`'s receipt time minus index j's send time is at
     most Δ + RTT on the verifier gateway's clock. The service takes it as a session parameter.
4. **What PoUS does with the outcome.** An audit is accepted only when all k commitments arrived within 854 µs and the
   after-session proof verifies. PoUS then writes its `StorageProfile` from the certificate
   `Pous.SecurityProofs.P2SlackFamilyUncond`. That certificate says a server holding fewer than ⌊18/19 · |C|⌋ + 128 · B
   bits passes with probability at most 1% + 2^-128, under `P2_CLAIMS`. The profile stays marked experimental while
   SMS-as-M1 is not accepted. PoUS adds the service's error terms: proof soundness, binding, the possession claim, and
   for a sampled setup the setup profile's δ_s and the raised-k tail. A sampled setup also takes the restated
   certificate. A rejected audit, or one whose proof fails, yields no profile. PoUS refuses before calling the service
   when the parameters fall outside the certificate (`Certificate.refusals`).

### The setup proof and its cost

Per block, the model gives the following ANDs:

| Part | ANDs | Basis |
|---|---|---|
| Two 16,448-bit squarings, Karatsuba to a 64-bit base | 5.77e7 | [E] T(n) = 3T(n/2) + 6n, T(64) = 64² |
| Two 16,448-bit squarings, schoolbook | 5.41e8 | [E] n(n+1)/2 products + n²/2 full adders, each squaring |
| Two reductions mod 2^16448 − 21065 | 3.3e5 | [E] 21,065 has 6 set bits: 5 shifted adds, a second fold, a conditional subtract |
| σ_K, `− t mod p`, `c < p` | 1.0e5 | [E] compare-and-mux, subtract, range, about 6n |
| SHAKE256 keys, 32 Keccak-f | 1.23e6 | [C] 32 × 38,400 |
| Open C's leaf (17 compressions + tail) | 1.63e6 | [C] 17 × 81,402 + 241,490 |
| Open W's row (17 compressions + tail) | 1.63e6 | [C] same |
| **Total, Karatsuba** | **6.26e7** | squarings 92%, hashes and openings 7% |

Non-native integer arithmetic dominates, at 92% with Karatsuba or 99% schoolbook. No traced 16,448-bit squaring exists in
C-Flock, and the Karatsuba constant could move this by up to 2×. That is the first thing to measure: one squaring
lowered by `bits.compile` and run through `circuit-check`. The squaring count would drop only in a field where 16,448-bit
products are cheap, which no backend we have offers.

One GB of W is 1e9 / 2,054 ≈ 4.87e5 blocks. Exhaustive setup per GB:

| Item | Figure | Basis |
|---|---|---|
| ANDs | 3.0e13 | [E] 4.87e5 × 6.26e7 |
| Recursion sessions | about 1,300 (1,170–1,450) | [C] at M0 #20's 2.1–2.6e10 ANDs per 2^35-bit inner statement (`layout_model.TODAY`, r20260930-184956-61fe) |
| Inner proving, GPU, zero knowledge off | 15–19 GPU-min | [C] at 2.7–3.5e10 ANDs/s (same source) |
| Outer (V\*) proving | about 2.9 GPU-h | [C] 1,300 × 7.90 s [M #1246, K = 4096, m = 35] |
| Proof size | about 25 GB | [C] 1,300 × 19.6 MB [M #1246] |
| Lean verify | about 16 h | [C] 1,300 × 45 s, from #1246's 449 s for ten sessions, which it calls not like for like |
| Direct CPU `--zk`, for comparison | about 22 days, and 4e4 TB of staging | [C] at the ladder's best 16M ANDs/s and 1.37 GB staged per million ANDs (r20261003-215938-bdf1). Infeasible |
| Gateway CPU | unmeasured | The design lists it as open |

The exhaustive setup needs no Lean change. Decode is a bijection on [0, p), and the circuit checks `c < p`, so a proved
block is a codeword and the certificate applies to C as it stands.

A sampled setup draws `subset:s` after C's root, so s is set by ε and δ_s, whatever |W| is. The ε here is the fraction of
blocks allowed not to decode to W, and s = ⌈log(1/δ_s) / −log(1 − ε)⌉:

| ε, δ_s | s | ANDs | Sessions | Inner | Outer | Proof | Lean verify | k |
|---|---|---|---|---|---|---|---|---|
| 1%, 2^-40 | 2,759 | 1.7e11 | 8 | about 6 s | about 63 s | about 157 MB | about 6 min | 120 |
| 1%, 2^-128 | 8,828 | 5.5e11 | 24 | about 18 s | about 190 s | about 470 MB | about 18 min | 140 |
| 0.1%, 2^-40 | 27,713 | 1.7e12 | 74 | about 58 s | about 9.8 min | about 1.45 GB | about 55 min | 112 |

These are all [C] at s × 6.26e7 ANDs and the per-session figures in the exhaustive table. The prover still hashes every
block's hiding leaf natively, about 2.4 core-seconds per GB [E]. That is 4.87e5 × (3.0 µs for SHA-512 over 2,056 B, [M on
this VM] art:0ce31c5914749928a9507c50119588d4c9191e39f5fbc27fa0c6601a31e684e9, plus about 2 µs for the salt hash and the
leaf).

What sampling costs the guarantee:
- **ρ.** Up to εB blocks need not decode to W. The prover can commit anything there and need not store those blocks.
  That lowers the effective fraction to ρ_eff ≈ 18/19 · (1 − ε): 0.938 at ε = 1% and 0.946 at 0.1%.
- **k.** Challenges that land on those blocks are free passes. k becomes 105 + j, where P[Bin(k, ε) > j] is at most the
  tail. That gives k = 120 at ε = 1% for 2^-43.0, 140 for 2^-129.2, and 112 or 125 at ε = 0.1% for 2^-41.1 or
  2^-131.2 [C, exact binomial].
- **δ.** The profile's failure union gains δ_s plus that tail.
- **Lean.** The certificate must be restated over a store with at most εB blocks that need not decode. The proposed name
  is `P2SlackFamilyFreeBlocks`, with ρ_eff and k as parameters. That lemma is memory-accounting's work, and the
  sampled setup can't be cited before it is pinned in `lean-audit.json`.

### Each timed answer's proof and its cost

**Inside the deadline.** The prover gateway receives index `i_j` with `nonce_j` and checks the coin opening against the
session's coin commitment. It reads block `i_j` from the device and sends `A_j = hm96-sha512(block)`, with `nonce_j` in
the inner prefix: `x = SHA-512(prefix(nonce_j) ‖ block)`, then `b = x ⊕ M_key · y` and `leaf = H(leaf_prefix ‖ b ‖ c)`. The
salt `y`, `M_key · y` and `c = H(salt_prefix ‖ y)` don't depend on the nonce and are computed before the round. The round
budget at p99.9, against 854 µs:

| Step | p99.9 | Basis |
|---|---|---|
| Lean-owned socket and clock loop, under load | 140.7 µs | [M] vy-nebius-2, r20261005-163745-e84f (`internal/memory-accounting/pous-timing-loop-node.md`); it moved 64 KiB blocks, so this is conservative for P2 |
| The prover gateway's hop | 23–30 µs | [M] the same run's Lean-to-Python hop, as a stand-in |
| SHA-512 over 2,056 B | 12.4 µs | [M on this VM] art:0ce31c5914749928a9507c50119588d4c9191e39f5fbc27fa0c6601a31e684e9 |
| The hm96 finish (the XOR and one leaf compression) | about 1 µs | [E] about 0.3 µs per compression on the same VM |
| The coin-opening check | about 0.5 µs | [E] a few SHA-256 compressions |
| **Total** | **about 185 µs** | [C] 140.7 + 30 + 12.4 + 1 + 0.5. It fits within 854 µs, and within Δ = 500 µs alone |

The band's 64 KiB block takes 135.7 µs for SHA-512 [M, same artifact], about 310 µs in all. This time comes out of the
honest prover's margin only: the certificate already grants the adversary all of Δ + RTT.

Still to measure on the node:
- the full round, with a Lean prover gateway in the path;
- SHA-512 on the node's Xeon 6776P;
- the handoff of a block from the GPU to the gateway's CPU;
- the coin tree's per-round reveal and check;
- the RTT p99.9 on the deployment link, between the two gateways.

**After the session.** One statement template, `AnswerOpens`, with k instances. Each instance opens `A_j` (17
compressions + tail, with the nonce public) and C's leaf `i_j` (17 + tail), and checks the 2,056 bytes are equal. The
verifier gateway holds C's hiding leaves, so leaf `i_j` is a public input, and the circuit needs no Merkle path.

| Item | Figure | Basis |
|---|---|---|
| ANDs per answer | 3.25e6 | [C] 2 × (17 × 81,402 + 241,490) |
| ANDs per audit, k = 105 | 3.41e8 | [C] (k = 140: 4.55e8) |
| By recursion | one session: inner under 0.875 s, outer 7.90 s, 19.6 MB, Lean verify about 45 s | [M #1246] at m = 35, a 2^35-bit statement, so an upper bound for 3.4e8 ANDs |
| Direct CPU `--zk`, for comparison | about 21 s of proving at 16M ANDs/s; about 14 proofs of N = 8 instances, about 22 MB at 1.57 MB per proof | [C] r20261003-215938-bdf1's ladder (its fastest rung, N = 8) and r20261004-032911-9751's per-proof size; staging the 3.25e6-AND template is about 4.5 GB at 1.37 GB per M ANDs |

If the leaves are not public, the circuit carries a 19-level path per answer instead: about 2.5e6 more ANDs per
answer [E] (19 two-compression nodes), so about 1.6× the statement.

### The call sequence

The method names are proposals, like the design's.

Setup:
1. The developer calls `commit(W, rows=2054)` through the prover gateway. The registration fixes W's root, and the
   verifier logs a receipt. PoUW uses the same root.
2. The verifier draws `coin("verity/pous/salt/v1", after=W.receipt)`, the 24-byte salt. The coin goes on the record.
3. The developer encodes C = Enc(W, salt) on the GPU and calls `commit(C, leaves=hm96-sha512)`. C's root is
   registered, with a receipt.
4. The verifier draws the setup law, `exhaustive` or `subset(s)`, from `coin("verity/pous/setup-draw/v1",
   after=C.receipt)`.
5. The developer proves `P2Decode` over the drawn blocks. Public inputs are W's root, C's root, the salt and the indices.
   The service verifies and returns the setup profile (s, m, δ_s), and PoUS registers vk = (C's root, B, the profile).

Audit:
1. PoUS takes the parameters from the certificate, or the restated one: k, Δ = 500 µs, and an RTT cap of 354 µs.
2. The service calls `timed_session(C.root, law=uniform_with_replacement(B, k), reveal=sequential(nonce=True),
   limit=Δ + RTT, commit=nonce_bound_hm96)` on the on-node verifier gateway. Before the session it measures the RTT
   between the gateways and refuses an allowance above 354 µs, as `calibrate` and `limit_of` do today.
3. After the last round, the developer proves `AnswerOpens` over the k commitments. The service verifies it, and returns
   the verdict and the record. PoUS writes the `StorageProfile`.

### What PoUS reveals beyond the verdict

**Public:**

| Item | Reason |
|---|---|
| The verdict and the `StorageProfile` | The output |
| The scheme id and its parameters (w, c0, block and payload bytes, blocks per segment, the expander) | The certificate is stated for them, and the proofs' Programs read them |
| The certificate parameters (k, Δ, RTT cap, call time, ρ or ρ_eff, δ, the theorem, the claims) | The profile cites them. They depend on nothing secret |
| B and the segment count | The law is uniform over B, and the bound is in \|C\| = B × 2,056 × 8 bits. B reveals \|W\| to within a 2,054-byte block, hence the model's size. Hiding it means padding W to a bucket. Padding inside the certified family (2^8–2^23 blocks) needs no Lean change, but the profile then certifies the padded store (Q5) |
| W's root and C's root | The proofs' public inputs. They hide under hm96 |
| The salt, once drawn | `shake_keys` is a public function of it, and the setup proof takes it as a public input. It is independent of W. It must stay unknown to the developer until W's root is registered, which the coin's ordering gives |
| The setup draw's indices, after C's root is registered | Third parties re-verify the setup proof. They name blocks, not their contents |
| The setup profile (s, m, δ_s) | It is in the failure union |
| The answer commitments `A_j` | The after-session proof's public inputs. Hiding under hm96 |
| The audit's indices and nonces, after the session (or the continuous stream) closes, as coin-tree openings | Third parties re-verify the proof. They are independent of W. Never the source key, which would give the indices of later audits |
| Rejection or abort, about one bit | Aborts are outside ZK by name in the design |

**Verifier gateway (auditor side) only:**

| Item | Reason |
|---|---|
| Exact send and receipt times | A timing channel, outside `RecursiveZK` by name. It can show the storage medium and any content-dependent latency. The record publishes only each round's on-time bit, the limit and the measured allowance. The certificate reads only on-time bits, so no Lean change |
| Indices and nonces during the session, to the prover one at a time | Sequential reveal (R2) |
| C's hiding leaves (B × 64 B, 32 MB for 2^19 blocks) | They let the circuit skip Merkle paths. They hide under hm96 and could be public, but third parties need them only to re-verify, and the gateway can serve them |

**Hidden:**

| Item | Reason |
|---|---|
| W, C, every block value, every leaf preimage, the hm96 salts | The ruling |
| `layout.Layout`: tensor names, shapes, dtypes, which tensors | It reveals the architecture. With one flat commitment of 2,054-byte rows, PoUS needs no layout at all, and PoUW reads tensors at hidden positions (`MerkleRead_v1`) |
| Device and server time reports | Today's records carry them. They leave the record: they are a side channel and nothing reads them |

Hiding needs certificate or Lean changes in two places. The sampled setup needs `P2SlackFamilyFreeBlocks`, and hiding B
needs the profile to certify the padded store. The possession claim (R1) needs PoUS's Lean to restate its answer check
against the nonce-bound query. Public on-time bits and public setup indices need nothing.

## 3. Requirements the service doesn't meet yet

**R1. Possession inside the deadline.** A prover-salted commitment of a precomputed block does not show possession. The
in-deadline commitment absorbs a fresh verifier nonce `nonce_j`, revealed with index j, before the block's bytes: with
hm96, `x = H(prefix(nonce_j) ‖ block)`. Hiding still comes from the prover's salt, and binding from collision resistance.
Possession is a new named claim: in the random-oracle model, a commitment received by time t determines a hash query on
the whole block made after `nonce_j` was revealed. @proofs' interface gives `commit` this form and names the claim. What
remains is on our side: PoUS's Lean restates its answer check against that query, and the profile lists the claim beside
`P2_CLAIMS`. The joint note should replace the design's sentence that the hash is as good as the block.

**R2. A sequential draw.** The one-stage draw is computed from the verifier's randomness and sent whole before the
session. PoUS needs these properties:
- the indices and nonces come from a secret that stays secret until each reveal, because a known source makes every index
  computable in advance (`audit.challenge_key`'s docstring);
- index j is revealed only once `A_{j−1}` is in or has expired;
- the law is k indices uniform with replacement (`Key.uniform(B, j)`), which none of the service's laws (`subset`,
  `bernoulli`, `stratified`, `work`) is.

The recommendation is a timed-session mode in the verifier gateway, with a per-index reveal from the coin tree and a
`uniform:k` law. The Goldreich–Kahan coin commitment opens one (index, nonce) per round, and the prover gateway checks
the opening, about a microsecond [E], inside Δ.

**R3. The verifier gateway runs on the node, auditor-trusted for both integrity and confidentiality.** The design says it
doesn't matter where the verifier gateway runs. For PoUS it does. The measured RTT on the node is 10–22 µs against a
354 µs cap. An open TCP connection over RunPod's global network costs about 0.14 ms per round trip (1a1bb6a27), and it
would fit only if its p99.9 stayed under 354 µs, which nobody has measured. So the gateway sits on the developer's node,
or on an auditor-owned host on the same switch.
- Integrity: it must keep its clock honest.
- Confidentiality: it must keep the challenge source secret from the developer. Under ZK it must also keep the exact
  times and, if they aren't published, C's leaves.

The recommendation is a confidential VM (TEE) or an auditor-owned host, with the RTT p99.9 measured before each audit.
Until then, the trust in this gateway is a named claim in the profile, beside `live-verifier` and
`designated-verifier`.

**R4. The round's latency, with both gateways counted.** The service's timed mode should be built on #1227's Lean-owned
loop, with no Python hop on the verifier's side, and with the verifier and libuv's event-loop thread on one pinned CPU.
The prover gateway sits in every round. With it, P2's round is about 185 µs at p99.9 and the band's about 310 µs [C, §2].
- The pure-Lean `Flock.Sha256` takes 1.4 ms per 64 KiB [M, the timing-loop note], so a Lean prover gateway needs a native
  SHA-512 (the design benchmarks a faster Lean SHA-512 at 5–7×).
- The verifier gateway now stores 64-byte commitments rather than checking blocks, so the band's graded audit no longer
  needs the post-round check that 26 µs gaps forced.

**R5. The audit's verdict waits for its proof.** The timed session ends with k on-time bits and k commitments, but the
verdict exists only once `AnswerOpens` verifies. The service should hold the session open as pending, bind the proof to
the session's record digest, and refuse a proof submitted after a deadline that PoUS sets: one hour is ample for a
one-session proof [C, §2]. Otherwise a developer can wait out a rejection and retry. The same applies to the setup: vk is
registered only after the setup proof verifies.

**R6. A storage bound is not a wrong-unit bound.** `IntegrityProfile` bounds the wrong proof units of a partition under a
sampling law. PoUS's k indices are challenges, every answer is proved, and its 1% comes from the storage game, not from a
sampling law. The naive reading, `(1 − m/B)^k ≤ δ`, gives "at most 4.4% of blocks unanswerable" at δ = 1%. That is not the
guarantee, because it ignores an adversary that holds partial information about blocks. The recommendation is that the
service reports the exhaustive fact (k answers, all proved and on time, with the record's digest), and PoUS maps it
through its certificate into the `StorageProfile`. A sampled setup's integrity profile is the one place an
`IntegrityProfile` legitimately enters. Its m and δ_s set ρ_eff and k, and its δ_s joins the application's one failure
union.

**R7. The timed mode needs these parameters.**
- Δ, a hard deadline Δ_late, an audit cap, and `n` fixed in advance.
- An arrival schedule from the verifier's own coins, independent of the setup, the indices and the answers.
- A miss budget.
- The continuous verifier's rules: answers name their challenge, and every challenge closes with an outcome.
- For the graded audit, the next challenge goes out within the RTT of an answer, or the gap is charged to the window
  (9897c17f1).

On P2 only the strict audit is certified today, since the graded and continuous results are band-only and hold in the
ideal-permutation model. So the strict audit is needed now, and the rest when those results are restated for P2.

**R8. Isolation is a soundness premise for PoUS.** The design's egress premise, that the GPUs reach only the prover
gateway, is developer-trusted and serves zero knowledge. PoUS's perfect isolation during the audit is a premise the
auditor's soundness needs, because the adversary is the developer. The prover gateway is the developer's, so the service
never counts it as providing isolation, and the warden enforces the audit window on auditor-trusted terms.

**R9. One commitment to W, shaped for both protocols.** Today W's commitment is a single unsalted streaming SHA-256,
which cannot be opened per block and is not hiding. The setup proof must open W at block i in-circuit. That is cheap only
if W is committed as hiding rows of exactly one P2 payload (2,054 bytes) each, which the table's 1.63e6 ANDs per row
assumes. PoUW then proves inference against the same root, reading tensors at hidden positions (`MerkleRead_v1`, or
`one_stage/registered.py`'s hm96-sha512 rows at this row size). Other row sizes still work, as long as the setup opens
every row a payload touches, at about R / 128 compressions per R-byte row. For example, rows of 64 KiB would cost about
512 × 81,402 ≈ 4.2e7 ANDs per block, which takes the block's statement from 6.26e7 to about 1.03e8 [C]. A second, PoUS-only root
would need its own proof of equality with PoUW's, about 1.6e12 ANDs per GB [E: 4.87e5 blocks × two openings of about
1.63e6]. The row size is a joint decision with PoUW (Q6).

**R10. C's leaf format.** Under ZK, C's leaves are hm96-sha512 hiding leaves under the service's frame-v3 tree. PoUS's
two SHA-256 framings (`verifier.leaf_hash` with a little-endian tag, P2 spec v1's big-endian `reference.leaf`) go at P2's
next spec revision. That changes fixtures and the spec's leaf section, but no Lean, because the Lean idealizes the
per-block tags. Natively, a leaf costs 3.0 µs per P2 block and 77 µs per 64 KiB [M on this VM, same artifact], about
1.6 core-seconds for 2^19 leaves.

**R11. Ordering, on the record.** W's root is registered, then the salt is drawn, then C's root is registered, then the
setup draw is made, then the setup proof verifies, then audits run. Each coin is drawn after the previous receipt, and the
record shows it. A salt known before W's commitment lets the developer pick W against the keys. A setup draw known
before C's root lets it encode only the drawn blocks.

**R12. The setup proof is a large batch job.** Exhaustive is about 1,300 inner sessions per GB, 25 GB of proofs and 16
hours of Lean verify [C]. The service must take a proof job of that size with one aggregate verdict, or a `subset:s` law
whose setup profile reaches PoUS. Both need V\*'s session count, and the Lean verify time, to fall before an exhaustive
setup is practical. The sampled setup fits today's figures.

## 4. Questions for Daniel

1. **Where does the auditor's timed verifier run, and what makes it auditor-trusted on the developer's node?** My
   recommendation is a confidential VM or an auditor-owned host on the same switch, with the RTT p99.9 measured at or below
   354 µs before each audit. Until then, its trust is a named claim in the profile.
2. **Does the service grow a sequential timed mode, or does PoUS keep its own loop and use the service only for coins, the
   record and the proofs?** My recommendation is that the service grows it, built on #1227's Lean loop, since the network
   warden's timing work will want the same loop and clock.
3. **@proofs has accepted the nonce-bound commitment and named the possession claim. Does that claim enter PoUS's profile
   as a random-oracle claim beside `P2_CLAIMS`, with PoUS's Lean restating its answer check against it?** My
   recommendation is yes, and the restatement is memory-accounting's work.
4. **Does `StorageProfile` stay PoUS's own reading of the service's verdict, rather than a kind of `IntegrityProfile`?** My
   recommendation is that it stays PoUS's and cites the service's record by digest, so that `IntegrityProfile` keeps its
   one meaning, a bound on wrong units.
5. **Is |W| public?** B reveals W's size to within 2 KB. My recommendation is yes for now, since PoUW's own proof sizes
   and costs show the model's scale anyway. Hiding it means padding to a bucket and certifying the padded store.
6. **May PoUS and PoUW share one commitment to W, as hiding rows of 2,054 bytes?** My recommendation is yes, and PoUW's
   row reads must work at that size. Larger rows raise the setup's per-block cost (about 1.7× at 64 KiB rows), and a
   second root needs a proof of equality (R9).
7. **Exhaustive or sampled setup?** My recommendation is sampled now, at ε = 1% and δ_s = 2^-128 (s = 8,828, about 24
   sessions, 470 MB and 18 min of Lean verify, k = 140 [C]), once `P2SlackFamilyFreeBlocks` is proved. The exhaustive
   setup keeps ρ = 18/19 and k = 105 but costs about 2.9 GPU-hours, 25 GB and 16 hours of Lean verify per GB [C]. Until
   the lemma lands, only the exhaustive setup is certified.
