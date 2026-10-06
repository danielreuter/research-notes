---
id: 20261006T0229Z-draft-proof-service-pous
campaign: memory-accounting
lane: memory-accounting
kind: draft
status: open
repo: verity
origin: bc-15ada664-f325-5371-a473-65d408be3cf5
---

# PoUS as a user of the proof service

This is a read-only review of PoUS on origin/main c305471c5 (after the Lean move, 7b410fbf6), against proofs' design
(Project store `internal/recursive-zk-system-architecture.md`, 5 Oct, 4:55 PM PDT). It is memory-accounting's input to
@proofs' joint note `proof-service-architecture`. Paths are relative to `verity/protocols/accounting/space/pous/` unless
they start with `benchmarks/`. The scheme written up is P2 v3 (`p2-16448/v3`). The band, dense and P3 appear only where the
graded and continuous audits, or the band's 64 KiB block, matter. The window is Daniel's ruling in #1159, Δ + RTT ≤
500 + 354 µs = 854 µs. #1159 is not on main yet, so main still has `ROOT_CALL_NS = 2_900_000` and `reference.py`'s
`MAX_RTT_ALLOWANCE_NS = 1_000_000`.

Three findings shape the rest.

- **While the auditor may see W, PoUS needs no proof at all.** Today the auditor does see W: the public-encoder setup
  decodes all of C\* on the verifier, so W streams through it. In that case PoUS uses the service for its coins, the timed
  session, the record and the profile, and every check is native. I call this clear mode. Proofs add value only when W is
  secret from the auditor, which I call hidden mode, and then the setup must be proved as well as the answers.
- **The design's "hash each answer inside the deadline, prove it later" is unsound for PoUS as written.** The design says
  binding makes the hash as good as the block for the timing argument. It isn't, because binding fixes which value was
  committed, not that the prover held it when the challenge came. The salt is the prover's, so the prover can precompute
  the commitment, or with hm96 the unsalted inner digest `x = H(block)`, for every block. Then it stores 64 bytes per
  2,056-byte block (3.1% of C at SHA-512, or 0.1% of a 64 KiB band block), sends each commitment in microseconds, and
  rebuilds the blocks from W at leisure for the later proof. The certificate needs about 18/19 of C held, so a prover
  holding 3% of C passes every audit. The fix is in requirement R1.
- **The service's draw is computed and sent whole before the session.** PoUS needs each index revealed only after the
  previous answer, from a secret held on the node, inside a sub-millisecond loop.

## 1. What PoUS owns today that the service would replace

| Piece | Path on origin/main | What replaces it | What PoUS keeps |
|---|---|---|---|
| Commitment to W | `setup.commit`, `_commitment_hash` and `COMMIT_TAG` (a hand-rolled streaming copy of `identity.tagged_sha256`); `protocol.commit`; `benchmarks/pous/p2_v1/reference.py` `w_commitment` and `W_COMMITMENT_LABEL`; vLLM `protocol_options/pous.py` `_commit` | The service's commit of W, registered once and shared with PoUW | The manifest and `layout.Layout`, which say which bytes are W |
| The vk tree over C's leaves | `verifier.py` (`leaf_hash`, `node_hash`, `MerkleTree`, `verify_path`, `VerifierKey.check` and `check_path`), with `labels.tag`, `labels.salt_value` and `params.SALT_BITS`; a second leaf framing in `p2_v1/reference.py` (`leaf`, `root`, `epoch_id`); `leaves.bin` written by `benchmarks/pous/band_gpu/harness.py` | The service's commitment scheme (a frame-v3 SHA-256 tree, or hm96-sha512 leaves in hidden mode) and its native path check | What a leaf commits: block i of C |
| The salt | `setup.draw_salt` and `SALT_DOMAIN`; `p2_v1/reference.py` `setup_salt`; `p2_v1/harness.py` `SETUP_SOURCE`, a fixed bench constant; vLLM's `salt_source`, with an `os.urandom` placeholder | A live coin drawn after W's registration, kept on the record | The rule that the salt comes after the commitment, and its 24-byte width |
| The challenge draw | `audit.challenge_key`, `CHALLENGE_DOMAIN` and `TimedVerifier.challenge` (`key.uniform(B, j)`); `protocol.challenge_key`; `p2_v1/reference.py` `audit_key` (`audit-id/v1`, `audit-challenge/v2`); the `os.urandom(32)` sources in `band_gpu/live.py` and `p2_v1/live.py` | The service's draw, in a sequential mode (R2) | `k` and the law, which come from the certificate |
| The continuous arrival schedule | `continuous.run_continuous`, whose `wait` the caller supplies | The service's coins | `n` and the miss budget |
| The timed verifier | `audit.TimedVerifier` and `run_timed`; `protocol.Verifier`; `continuous.ContinuousVerifier`; the hand-rolled loop in `p2_v1/live.py`; #1227's Lean loop (`benchmarks/pous/timing_loop/`, not on main) | The service's verifier gateway in a timed mode | The acceptance rules (strict, the continuous miss budget, graded) and `audit.simulate`, the oracle-model audit that tests replay |
| Transport and RTT calibration | `band_gpu/live.py` (`LiveResponder`, the `<QQ` request and `<QQQ` header wire, `OP_CHALLENGE`, `OP_PING`, `OP_CLOSE`, `calibrate`, `limit_of`, `LogicalClock`); on the server side `band_gpu/harness.py` `ControlResponder` and the socket loop in `band_gpu/pous_native.cu`; `continuous.Reply` with `send` and `receive`; vLLM's in-process responder | The service's transport, and its RTT measurement before each audit | The device read that serves block i, which is prover-worker code, and the value, late and recompute controls as test responders |
| Records | `live.py`'s audit JSON (the source, each answer's time, device and server ns, verdicts); `audit.Answer` and `AuditResult`; the harness's result JSON | The service's record: coins, send and receipt times on the gateway's clock, the answers or their commitments, and the verdicts | Device and server time, as benchmark measurements |
| The setup verifier | `setup.verifier_key_from_encoding` (public encoder), `setup.verifier_key` (private encoder), `verifier_setup`, `protocol.verifier_key`, `check_server_root` | The service runs PoUS's setup check, natively over every block in clear mode or as a sampled ZK proof in hidden mode | `decode_segment`, and the decode relation stated as a Program |
| Gateways | None: answers leave the responder in the clear | The verifier gateway in both modes, and the prover gateway in hidden mode only | Nothing |
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
   - W is committed once and shared with PoUW, as the bytes that `layout.Layout` places into P2's 2,054-byte payloads.
   - C's leaves are committed as vk's root. In clear mode the verifier computes them from C\* itself and registers the
     root, so they are its own state, not a prover commitment. In hidden mode the prover commits them under hiding leaves.
   - In hidden mode only, each answer is committed inside its deadline, under the nonce-bound commitment of R1.
2. **Which units are checked.**
   - At setup, every block in clear mode, or a `subset:s` draw of blocks in hidden mode.
   - In the audit, k = 105 indices uniform with replacement over the B blocks. Index j is revealed only after answer j − 1
     is in, or after its hard deadline passes. Every answer is checked and none is sampled, because the certificate needs
     all k correct and on time. In clear mode no unit needs a proof.
3. **The check each unit passes, as a public Program.**
   - Setup, `P2Decode`: `sq(σ_K(sq(c))) − t mod p` equals W's payload at block i, with `(K, t)` from `shake_keys` at the
     salt, segment and block, and leaf i is the hash of `c` under the leaf framing.
   - Audit, `LeafCheck`: `leaf_hash(i, answer) == vk.leaves[i]`, or the RFC 9162 path to the root.
   - The deadline is not a Program. It is a property of the record: receipt time minus send time is at most Δ + RTT on the
     verifier gateway's clock. The service therefore takes it as a session parameter.
4. **What PoUS does with the outcome.** An audit is accepted only when all 105 answers are correct and within 854 µs.
   PoUS then writes its `StorageProfile` from the certificate `Pous.SecurityProofs.P2SlackFamilyUncond`. That certificate
   says a server holding fewer than ⌊18/19 · |C|⌋ + 128 · B bits passes with probability at most 1% + 2^-128, under
   `P2_CLAIMS`, and the profile stays marked experimental while SMS-as-M1 is not accepted. In hidden mode PoUS adds the
   service's error terms (proof soundness, binding and the possession claim) and, for a sampled setup, the blocks the setup
   profile allows to be wrong. A rejected audit yields no profile. PoUS refuses before calling the service when the
   parameters fall outside the certificate (`Certificate.refusals`).

### The call sequence in clear mode

The method names are proposals, like the design's.

Setup:
1. The developer calls `commit(W)`. The registration fixes the commitment and the verifier logs a receipt.
2. The verifier draws `coin("verity/pous/salt/v1", after=receipt)`, the 24-byte salt, and the coin goes on the record.
3. The developer encodes C = Enc(W, salt) on the GPU with the scheme's code and sends C\* segment by segment.
4. The service runs `P2Decode` natively over every block of C\* against W's commitment, builds the leaves and registers
   vk's root. For the 2^19 blocks (1.08 GB) of the certificate's store, I estimate about 5 core-seconds plus moving the
   1.08 GB. Per block, that is two 16,448-bit squarings (about 0.7 µs at #1159's tuned floor), the SHAKE256 expansion of
   K and t (about 8 µs, estimated from SHA3-256 over 2 KB) and one SHA-256 leaf (1.4 µs).

Audit:
1. PoUS takes the parameters from the certificate: k = 105, Δ = 500 µs, and an RTT cap of 354 µs.
2. The service calls `timed_session(root, law=uniform_with_replacement(B, k), reveal=sequential, limit=Δ + RTT,
   check=LeafCheck, check_at=after_receipt)` on the on-node verifier gateway. Before the session it measures the RTT and
   refuses an allowance above 354 µs, as `calibrate` and `limit_of` do today.
3. The service returns the verdict and the record, and PoUS writes the `StorageProfile`.

### What changes in hidden mode

At setup step 4, the prover commits the leaves under hiding leaves. The service draws `subset:s` of the blocks and proves
`P2Decode` on them in direct ZK. The result is an integrity profile that bounds the wrong blocks by m at δ_s. Each
sampled block's statement is two 16,448-bit modular squarings, the SHAKE256 expansion of about 4 KB, and two openings.

In the audit, the prover gateway sends each answer's nonce-bound commitment inside the deadline. After the session, one
direct-ZK proof shows that each committed answer opens vk's root at its index. These statements are small: under 100
SHA-512 compressions per P2 answer, and under 10,000 for an audit. Recursion is not needed.

## 3. Requirements the service doesn't meet yet

**R1. Possession inside the deadline (hidden mode).** As shown in the findings, a prover-salted commitment of a precomputed
block does not show possession. The recommendation is that the in-deadline commitment absorbs a fresh verifier nonce
`nonce_j`, revealed with index j, before the block's bytes. With hm96 this means putting `nonce_j` in the inner layout's
prefix, so that `x = H(prefix(nonce_j) ‖ block)`. Hiding then still comes from the prover's salt, and binding from
collision resistance. Possession needs a new named claim: in the random-oracle model, a commitment received by time t
determines a hash query on the whole block made after `nonce_j` was revealed. PoUS's Lean would then restate its answer
check against that query. Until this lands, PoUS runs in clear mode only. The joint note should correct the design's
sentence that the hash is as good as the block.

**R2. A sequential draw.** The one-stage draw is computed from the verifier's randomness and sent whole before the
session. PoUS needs these properties:
- the indices come from a secret that stays secret until each reveal, because a known source makes every index
  computable in advance (`audit.challenge_key`'s docstring);
- index j is revealed only once answer j − 1 is in or has expired;
- the law is k indices uniform with replacement (`Key.uniform(B, j)`), which none of the service's laws (`subset`,
  `bernoulli`, `stratified`, `work`) is.

The recommendation is a timed-session mode in the verifier gateway, with a per-index reveal from the coin tree and a
`uniform:k` law, and with the record keeping each reveal's send time and each answer's receipt time. In hidden mode, the
Goldreich–Kahan coin commitment opens one index per round, so the prover checks one opening per round, about a
microsecond, inside Δ.

**R3. The verifier gateway runs on the node, auditor-trusted for both integrity and confidentiality.** The design says it
doesn't matter where the verifier gateway runs. For PoUS it does. The measured RTT on the node is 10–22 µs against a
354 µs cap. An open TCP connection over RunPod's global network costs about 0.14 ms per round trip (1a1bb6a27), and it
would fit only if its p99.9 stayed under 354 µs, which nobody has measured. So the gateway sits on the developer's node, or on an auditor-owned host on the same switch. There it
must keep its clock honest, which is integrity, and keep the challenge source secret from the developer, which is
confidentiality. The recommendation is a confidential VM (TEE) or an auditor-owned host, with the RTT p99.9 measured
before each audit. Until then, the trust in this gateway is a named claim in the profile, beside `live-verifier` and
`designated-verifier`.

**R4. The loop's latency, with the gateway's time counted.** On vy-nebius-2 a Lean-owned socket and clock take 99.5 µs per
round at p99.9 idle and 140.7 µs under load. A Lean-to-Python hop inside the round adds 23–30 µs at p99.9
(Project store `internal/memory-accounting/pous-timing-loop-node.md`). The service's timed mode should therefore be built
on #1227's Lean-owned loop, with no Python hop in the round, and with the verifier and libuv's event-loop thread on one
pinned CPU. The per-answer hash costs, measured on this agent's VM rather than the node, with 20,000 calls each
(art:0ce31c5914749928a9507c50119588d4c9191e39f5fbc27fa0c6601a31e684e9):

| Hash | 2,056 B, p50 / p99.9 (µs) | 64 KiB, p50 / p99.9 (µs) |
|---|---|---|
| SHA-256 | 1.4 / 14.1 | 34.0 / 50.6 |
| SHA-512 | 3.0 / 12.4 | 76.7 / 135.7 |
| BLAKE3 | 1.2 / 2.6 | 8.5 / 15.1 |
| Copy | 0.2 / 0.2 | 1.4 / 5.0 |

- **The prover gateway in hidden mode** sits inside the window. It adds a hop (the measured 23–30 µs is a fair stand-in)
  and the commitment. That makes P2 about 141 + 30 + 12 ≈ 185 µs at p99.9 under load, and the band about 141 + 30 + 136 ≈
  310 µs. Both fit within 854 µs, and within Δ = 500 µs alone. This time comes out of the honest prover's margin only:
  the certificate already grants the adversary all of Δ + RTT, so soundness does not change.
- **The verifier gateway** stamps the receipt time on an answer's last byte and checks it after the stamp. For P2 the
  1.4–14 µs check can sit in the gap before the next challenge. For the band's graded audit it can't: the audit cap
  leaves 26 call-times (about 6.3 ms) for the worst row's 242 gaps, about 26 µs a gap (`PROTOCOL.md`, "Isolation over the
  whole graded window"), and a 64 KiB SHA-256 takes 34–51 µs. So the gateway keeps the answers (243 × 64 KiB ≈ 16 MB) and
  checks them after the last round. The pure-Lean `Flock.Sha256` takes 1.4 ms per 64 KiB and must stay out of the loop in
  every case.

**R5. A check with no proof.** In clear mode, PoUS needs the service to run a public Program natively on values opened in
the clear, record the verdict and feed the profile, without proving anything. The design describes this only as "without
the layer". The recommendation is a first-class native-check mode, with the same record and profile as the proved modes.

**R6. A storage bound is not a wrong-unit bound.** `IntegrityProfile` bounds the wrong proof units of a partition under a
sampling law. PoUS's k indices are challenges, every answer is checked, and its 1% comes from the storage game, not from a
sampling law. The naive reading, `(1 − m/B)^k ≤ δ`, gives "at most 4.4% of blocks unanswerable" at δ = 1%. That is not the
guarantee, because it ignores an adversary that holds partial information about blocks. The recommendation is that the
service reports the exhaustive fact (k answers, all correct and within Δ + RTT, with the record's digest), and PoUS maps
it through its certificate into the `StorageProfile`. The service's error terms, and any sampled setup's integrity
profile, then join the application's one failure union.

**R7. The timed mode needs these parameters.** They are Δ, a hard deadline Δ_late, an audit cap, `n` fixed in advance, an
arrival schedule from the verifier's own coins (independent of the setup, the indices and the answers), and a miss
budget. It also needs the continuous verifier's rules: answers name their challenge, and every challenge closes with an
outcome. For the graded audit, the next challenge goes out within the RTT of an answer, or the gap is charged to the
window (9897c17f1). On P2 only the strict audit is certified today, since the graded and continuous results are band-only
and hold in the ideal-permutation model. So the strict audit is needed now, and the rest when those results are
restated for P2.

**R8. Isolation is a soundness premise for PoUS.** The design's egress premise, that the GPUs reach only the prover
gateway, is developer-trusted and serves zero knowledge. PoUS's perfect isolation during the audit is a premise the
auditor's soundness needs, because the adversary is the developer. The recommendation is that the service never counts
the developer's gateway as providing isolation, and that the warden enforces the audit window on auditor-trusted terms.

**R9. One commitment to W, and its coupling to the setup.** Today W's commitment is a single unsalted streaming SHA-256,
which cannot be opened per block. If PoUW commits W under hiding registered values (`one_stage/registered.py`,
hm96-sha512 rows) to keep it secret, then clear-mode PoUS can't recompute that root without the developer's salts, and its
setup would reveal W anyway. So the deployment chooses one mode for both protocols. The recommendation is one commitment
to W per deployment, with PoUS's `P2Decode` reading payloads through the layout map onto the registered rows. A sampled
hidden setup also needs a Lean lemma for "at most m blocks are not codewords", either a certificate over B − m blocks or a
reduced ρ. That lemma is memory-accounting's work.

**R10. vk's leaf format.** PoUS has two SHA-256 leaf framings today: `verifier.leaf_hash` with a little-endian tag, and P2
spec v1's big-endian `reference.leaf`. The service's frame-v3 tree binds a domain. In clear mode, keeping SHA-256 costs
nothing new: the check is 1.4 µs per P2 answer, off the clock, and the vk build is 2^19 leaves, about one core-second.
The recommendation is to adopt frame-v3 at P2's next spec revision. It changes fixtures and the spec's leaf section, but
no Lean, because the Lean idealizes the per-block tags. Hidden mode needs hm96-sha512 leaves, which take about twice as
long (3.0 µs per P2 block, 77 µs per 64 KiB).

## 4. Questions for Daniel

1. **Is W secret from the PoUS auditor in the deployments we target?** My recommendation is clear mode now: no proofs,
   with the service supplying coins, timed sessions, records and the profile. Hidden mode would come only when a
   deployment pairs PoUS with zero-knowledge PoUW, since it needs R1's new claim, a proved setup and new Lean.
2. **Where does the auditor's timed verifier run, and what makes it auditor-trusted on the developer's node?** My
   recommendation is a confidential VM or an auditor-owned host on the same switch, with the RTT p99.9 measured at or below
   354 µs before each audit. Until then, its trust is a named claim in the profile.
3. **Does the service grow a sequential timed mode, or does PoUS keep its own loop and use the service only for coins and
   the record?** My recommendation is that the service grows it, built on #1227's Lean loop, since the network warden's
   timing work will want the same loop and clock.
4. **May the joint note state that an in-deadline commitment must absorb a verifier nonce before the block, and add the
   possession claim?** My recommendation is yes. Without it, hidden-mode PoUS is broken by a prover that stores 3% of C.
5. **For P2 with W visible, does the setup stay an exhaustive native decode of C\* rather than a sampled proof?** My
   recommendation is yes. It costs a few core-seconds per GB plus moving C\*. A sampled proof would cost a Lean
   restatement and part of ρ, and would buy only bandwidth.
6. **Does `StorageProfile` stay PoUS's own reading of the service's verdict, rather than a kind of `IntegrityProfile`?** My
   recommendation is that it stays PoUS's and cites the service's record by digest, so that `IntegrityProfile` keeps its
   one meaning, a bound on wrong units.
