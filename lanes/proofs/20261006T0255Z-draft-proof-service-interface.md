---
id: proofs/20261006T0255Z-draft-proof-service-interface
campaign: proofs
lane: proofs
kind: draft
status: draft
repo: danielreuter/verity
origin: bc-bb283e71-f122-57b3-b894-fccb8cd2ada1 (proof-service, for the proofs coordinator bc-8416bc72)
---

# The proof service: its interface (draft)

For Daniel, written 5 Oct from 7:55 PM PDT, in answer to your 7:17 PM PDT directive: the proof layer is the one
service that PoUW, PoUS and the network warden call, and none of them keeps commitment, randomness, draw, transport,
verifier, gateway or audit-record code of its own.

Read at `origin/main` `c305471c5` (after the Lean move), with the branches cited by name. It starts from proofs' design
(Project store `internal/recursive-zk-system-architecture.md`, 5 Oct, 4:55 PM PDT) and answers the three users' notes:
compute-accounting's `note:20261006T0233Z-draft-pouw-service-user` (PoUW, R1–R13), memory-accounting's
`note:20261006T0229Z-draft-proof-service-pous` (PoUS, R1–R10) and network-accounting's
`note:network-accounting/network-accounting/20261006T0230Z-draft-warden-proof-service` (the warden, R1–R5). Nothing here
is built under these names; section 6 says what is.

## The short version

- **A protocol hands the service one `Spec` and gets back one `Outcome`.** The `Spec` is the protocol's four things as
  data: what is committed, the selection rule, the check, and the reading of the outcome. Everything else is the service.
- **Your 7:48 PM PDT ruling arrived while this was being written.** The ruling: the circuit and the data are hidden in
  every protocol, and only the minimum is public, each item with its reason. There is no clear mode, for secret or
  public data, and this note now has none. The architecture note
  (`note:proofs/20261006T0307Z-draft-proof-service-architecture`, sections 1 and 2) applies the rest of the ruling, and
  on four points supersedes this note:
  - a registration carries only salted roots and declared public items, and what `receive` used to check against the
    auditor's own copy of the program moves into a window statement proved once per window;
  - per-call roots stay private behind one registered window root;
  - PoUW's per-unit work is a uniform draw over equal tiles, not strata by credit class;
  - `prove` picks its mode and sizes from public items only.
- **The service is a few calls and a record, across four parties.** The prover gateway (developer-trusted) commits,
  registers and proves. The GPU workers (trusted by neither) only answer the gateway. The verifier gateway
  (auditor-trusted) receives registrations, issues live coins, draws, runs timed sessions and keeps the record. The batch
  verifier (auditor-trusted, Lean) verifies and writes the outcome.
- **The service picks how each check is proved.** It uses direct ZK when the statement is small and recursion when it is
  large.
- **A correction to proofs' design.** Binding does not show possession. "Hash each PoUS answer inside the deadline and
  prove it later" is unsound, because the prover can precompute every block's commitment. `commit` gets a nonce-bound form,
  and possession becomes a new named claim (section 3).
- **Proofs takes both of compute-accounting's asks as service calls.** The two-stage driver goes on `select`, and
  registered row/v2 goes on `commit_registered` (section 4).
- **Guarantees.** On main: direct ZK's soundness, its honest-verifier zero knowledge, hm96's hiding and the one-stage
  law. In flight: recursion's `RecursiveSound` and `RecursiveZK` (#1261) and C-Flock's `EndToEnd` (#1257). Recursion counts
  as end to end only once `VBridge` (#1258 and its plan) is proved. No theorem yet: zero knowledge against a malicious
  auditor at C-Flock's `--zk`, the nonce-bound commitment, the epoch coins, the sequential draw and the gateway's send
  check (section 5).

## 1. What a protocol states: the `Spec`

A word first: the Glossary already uses **Policy** for a condition on declarations (NCI's). So this note calls "which units
need proofs" the **selection rule**.

```python
@dataclass(frozen=True)
class Value:                          # (1) what is committed
    name: str                         # "A", "W", "vk", "record"; one tree per (name, call or window)
    schema: str                       # "hm96-sha512/row/v2" | "hm96-sha512/row-seg/v1"
    bits: int                         # bits per row: public shape
    phase: Phase                      # "epoch" | "serve" | "interior" (after the draw) | "in-deadline"
    registered: bool = False          # committed once per program, read by position (weights)
    fresh: bool = False               # nonce-bound, inside a deadline (section 3)

Selection = (                         # (2) which units: the selection rule
    All()                                             # warden; PoUS's exhaustive setup
  | Law(text, work=None, closure=None)                # "work:K" | "stratified:K" | "subset:K" | "bernoulli:N/D"
  | TwoStage(replay=Law(...), check=None | k)         # replay units by a law, interiors committed, then k (or all) of
                                                      # each drawn one's proof units
  | Sequential(law="uniform:k", population=B)         # PoUS: index j revealed only after answer j - 1
)                                                     # + extra(registration) -> units: protocol-chosen, proved and
                                                      #   recorded, outside the escape bound (PoUW R8)

@dataclass(frozen=True)
class Check:                          # (3) the check each selected unit passes
    program: Program                  # a public Program or Definition, by digest
    query: Query                      # its partition into proof units
    regions: Callable[[Record], PublicInputs]   # computed on the auditor's side only (PoUW R9)
    public_outputs: tuple[str, ...] = ()        # ports the auditor reads, given to RecursiveZK's simulator (PoUW R4)
    deadline: Deadline | None = None            # delta, delta_late, cap, n, miss budget: a property of the record
@dataclass(frozen=True)
class Outcome:                        # (4) what the protocol reads
    accepted: bool
    verdict: Verdict                  # one_stage.verdict.Verdict: failure codes in the order found
    profile: IntegrityProfile | None  # sampled selections: wrong-unit bounds at delta
    exhaustive: Exhaustive | None     # All and Sequential: each unit's verdict, and "by the deadline or not"
    terms: Terms                      # named error terms: proof, binding, possession, sampling delta
    record: bytes                     # SHA-512 of the record of record
```

`Spec = (values, selection, check, context)`, where `context` is the protocol's statement context, such as PoUW's
identifier v1 (scheme, salt, workload), bound into the registration (PoUW R10). The fourth thing, what the protocol does
with the outcome, is the protocol's own code: PoUW's credit rule and γ, PoUS's `StorageProfile`, the warden's charge.

## 2. The calls, by party

```python
# GPU workers: trusted by neither party. They answer the prover gateway, and reach nothing else (egress, deployment).
digest(schema, rows) -> list[Digest]              # unsalted inner digests x (sha512/row/v2 or row-seg/v1), streamed
inner(statement, witness, coins) -> messages      # a C-Flock session with zero knowledge off
outer_heavy(vstar_statement, transcript) -> work  # the outer proof's arithmetic, gated

# Prover gateway: developer-trusted. A Lean program on #1237's framework; Python and Rust prototypes today.
commit(value, digests) -> Handle                  # salts each x; Handle.root() per call, asynchronous, batched per pass
commit_stream(value) -> Appender                  # .append(row) off a real-time tick; .close() -> Root (warden R3)
commit_registered(program, value, rows) -> Registered   # hm96-sha512/row/v2 (section 4)
commit_fresh(nonce, block) -> CommitString        # x = SHA-512(prefix(nonce) || block) over the whole block, never over
                                                  # H(block); inside the deadline (section 3)
register(spec, roots) -> Registration             # sent to the verifier gateway; the receipt comes back
prove(draw, check) -> Sessions                    # zk | recursive, chosen by size; gates every message

# Verifier gateway: auditor-trusted. Live coins and the record. flock-audit (#1237), on the node for PoUS.
receive(registration) -> Receipt                  # salted roots and public items only (one_stage R1-R7 as restated), logged
coins(kind, after: Receipt) -> Coins              # kind: "epoch" | "session" (coin tree) | "nonce"
select(receipt, selection) -> Draw                # from its own randomness, after the receipt
timed(root, selection: Sequential, deadline, fresh) -> TimedRecord   # PoUS's loop, Lean-owned (#1227)
record() -> Record                                # append-only; times only as "by the deadline or not"

# Batch verifier: auditor-trusted Lean, offline.
verify(record, sessions, check) -> Verdict        # flock-verify
outcome(record, verdicts) -> Outcome              # the audit record, and the profile or the exhaustive fact
```

One audit window, in order: the gateway commits (serve phase), registers, and gets a receipt. The verifier gateway issues
the draw. For a two-stage rule, the gateway then commits the drawn units' interiors and registers again. The gateway proves,
and the batch verifier verifies and writes the outcome. Epoch coins, when a protocol needs them, come before serving and are
bound to an epoch registration.

**`commit`.** The GPU computes each leaf's unsalted inner digest `x` and sends only that to the gateway. The gateway draws the
salt `y`, computes `b = x ⊕ M·y` and `c = H(y)`, builds the frame-v3-sha512 tree, and returns each call's root when it is
ready. Salts never reach a GPU. A GPU that sends a wrong `x` gains nothing: hm96's hiding holds for every `x`, and a wrong
`x` opens to no row, so its proof fails. This is compute-accounting's split (R1). The gateway's share is about 1 µs a leaf,
1.5–5 cores per GPU at decode (their estimate); `M·y` and `c` depend on the salt alone, so they are precomputed. Roots come
per call (R2). A window's registration carries one root over the calls' entries (each call's root, its shape and counts,
and its committed record), since 15 minutes of decode is millions of calls. Under the 7:48 PM ruling the entries are
committed, not public. `commit_stream` is the same over rows that arrive 10 times a second (warden R3).

**`register` and `receive`.** This is one-stage's registration (`registration.record`, `check`, `receipt`), plus the
protocol's context (R10) and the root over per-call roots. One change for the warden's R1: today's receipt stamps the
verifier's clock to the second (`registration.receipt`'s `received`). The record should keep only the order (receipt before
draw) and whether the registration was in by its deadline.

**`coins`.** Three kinds, each in its own domain, so an epoch's coins, a window's draw and a session's coins never mix
(PoUW R5, R11):
- `epoch`: coins bound to an epoch registration's digest, for PoUW's salt and noise (the precommitted circuit), about every
  15 minutes.
- `session`: today's coin tree (`coin-tree/hm96-sha512/v2`), with Goldreich–Kahan's commitment so a malicious auditor
  learns nothing.
- `nonce`: a fresh value revealed with each timed challenge (section 3).

The audit window, the span one registration covers, is the protocol's choice and is independent of the epoch. Proving has
to keep pace with windows, not finish inside an epoch.

**`select`.** The verifier gateway draws from its own randomness after the receipt, under the rule in the `Spec`:
- `Law`: the one-stage laws as today (`draw.derive`, `check_draw`; Lean `Flock.Draw`). PoUW's per-unit work (R7) is met by
  strata keyed by template and credit class, the class read from the per-call records registered before the draw. The
  README's rule already says a template whose units are credited differently is split. Lean's `work_escape_le` takes any
  strata, and `prob_auditReg` covers strata that depend on the registration. What's new is code: `draw.derive` and
  `Flock.Draw` derive strata from the program and query alone today. Under the 7:48 PM ruling, strata would reveal each
  class's count. The architecture note (its L3) replaces them with a uniform draw over N equal tiles, scaled by the public
  ratio N·w_max/W.
- `TwoStage`: section 4.
- `All`: no draw, and so no escape term.
- `Sequential`: inside `timed`, below.
- `extra`: protocol-chosen units such as PoUW's exclusion tiles (R8), proved and recorded like drawn ones but outside the
  escape bound.

**`prove`.** The service picks the mode:
- **Direct ZK**: one C-Flock `--zk` session over the committed values (`--registered`, `--public-inputs`), with the gate of
  #1270 between the GPU and the auditor.
- **Recursive**: an inner session with zero knowledge off on the GPUs, through the gateway's salted-hash proxy (`rec_live`),
  then V*'s outer `--zk` session through the gate.

The rule is by size. The gate's trusted work grows with the committed witness: for direct ZK that is the statement's
witness, and for recursion it is V*'s, which grows only with the inner proof's openings and algebra. So the service proves directly
when the drawn units' witness is below V*'s, and recursively above it. Drawn units of one template class go into sessions
sized to the prover's block limit (PoUW R11, R12). Today V*'s eight statements are 2^28 to 2^32 words each, and the gated
outer prove costs 46.8 s and about 176 CPU-seconds of gateway work a session (#1270). The crossover itself is unmeasured.
PoUS's openings go direct, and PoUW's windows go recursive.

**`timed`.** This is PoUS's audit as a verifier-gateway mode, on the node, built on #1227's Lean-owned loop with no Python
hop in the round (PoUS R2, R4, R7). The verifier gateway draws k indices uniform with replacement from its own
randomness, keeps them secret until each reveal (in hidden mode, from its coin tree, one Goldreich–Kahan opening a round),
and reveals index j only once answer j − 1 is in or its hard deadline has passed. It checks each answer after stamping its
receipt, or after the last round when the check doesn't fit the gap (the band's graded audit). The record keeps, per index,
whether the answer was correct and in time, not when it arrived (warden R1). With `fresh=True` (hidden mode), each reveal
carries a nonce and the gateway answers with `commit_fresh` inside the deadline. A direct-ZK proof after the session then
shows that every committed answer opens vk's root at its index.

**`verify` and `outcome`.** `flock-verify` is the verifier of record. It takes the protocol's regions, computed from the
record by the auditor's side, and refuses prover-supplied ones (R9). `outcome` writes one-stage's audit record
(`verity/one-stage/audit/v0`) with `verity/integrity-profile/v1` for sampled rules. For `All` and `Sequential`, it writes an
`Exhaustive` fact instead: each unit's verdict, whether every unit was correct and on time, and the record's digest.
`IntegrityProfile` keeps its one meaning, a bound on wrong units at δ. PoUS maps the exhaustive fact through its certificate
into its `StorageProfile` (PoUS R6), and the warden computes its charge from the per-unit verdicts (warden R2).

**The record.** The verifier gateway keeps it. It holds, in order:
- registrations and receipts;
- the coins issued, or their commitments;
- the commit strings and roots received;
- the draws;
- the session records;
- the verdicts;
- for each deadline, one bit: in time or not.

Its custody is the `live-verifier` assumption (`RecordCustodyZKJ`) until #1237's fourth PR makes the record a theorem about
the Lean program.

## 3. A correction: binding is not possession

Proofs' design said that inside PoUS's deadline the gateway sends a salted hash of each answer, and that "binding fixes the
answer at that moment, so for the timing argument the hash is as good as the block". **That is wrong.** Binding fixes which
value a commitment opens to. It says nothing about when the committer held that value.

The salt is the prover's. So a prover can compute, in advance, every block's commitment (with hm96, only its unsalted digest
`x = H(block)`), keep those 64 bytes per 2,056-byte block (3.1% of C), and send each one in microseconds when asked. It then
rebuilds the blocks from W at leisure for the proof that follows. The certificate needs about 18/19 of C held, so a prover
holding 3% passes every audit. memory-accounting found this.

The fix is `commit_fresh(nonce_j, block)`. The verifier gateway reveals a fresh `nonce_j` with index j, and the commitment
puts it in hm96's inner prefix: `x = SHA-512(prefix(nonce_j) ‖ block)`. The nonce goes in front because SHA-512 is a
Merkle–Damgård hash: with the nonce at the end, a prover could store each block's 64-byte midstate and finish the hash in a
microsecond. Hiding still comes from the gateway's salt, and binding from collision resistance.

What this shows about possession needs a **new named claim**. No standard-model property of SHA-512 says a digest was
computed from bytes held at the time. In the random-oracle model, a commitment received by time t determines a hash query
on the whole block, made after `nonce_j` was revealed. PoUS's Lean then restates its answer check against that query. PoUS's
guarantee waits on this claim and that restatement.

The rule, in general: a guarantee that rests on *when* a value was held needs a nonce-bound commitment. A guarantee about
*what* was committed before a challenge needs only binding. PoUW's draw and the warden's records are of the second kind.

## 4. The two asks proofs takes

**The two-stage driver, on `select`.** It runs sampled proofs' two-stage law in four steps:
1. serve-time commitment of the replay units' boundaries;
2. the draw of replay units, after the receipt;
3. the drawn units' interiors committed and registered;
4. proving.

For PoUW, a replay unit is a drawn tile's closure. Its boundary is A's rows, the tile digests and the per-call records.
Its interiors are A′, the ok rows, `rowk`'s carries and the cap rows. Stage 1 is `work:K` over tiles, and stage 2 is all of
a drawn unit's proof units. With stage 2 at "all" there is no second draw, so Lean's `late_interior_insecure` (a fine draw
before the interiors are committed) can't arise, and the profile is the work law's over replay units.

What isn't built:
- **The driver itself**, with its log of two registrations and their receipts (the README says "not built yet"), and an
  audit record that holds both.
- **A general stage 1.** `TwoStageLaw` (`experimental/verity_experimental/sampled_proofs/law.py`) draws replay units only
  `Bernoulli(p)` per class. Stage 1 must take any one-stage law and its closure, and the law moves out of `experimental`
  into `sampled_proofs`.
- **The Lean check.** `twoStage_count` and `two_stage_b_tight` hold for every first-stage law. Whether they cover
  `TwoStageLaw.profile` exactly, its largest-replay-unit rule included, is unchecked (the README's "Not yet in Lean").
- **Decision 41's security function and red-team review**, and the check that PoUW's tiles per proof unit match the
  partition (`validate_refinement` exists).

**Registered row/v2, on `commit_registered`.** Registered values move from `hm96-sha512/row/v1` to `hm96-sha512/row/v2`
(PoUW R3, by your ruling that no row is `sha512/row/v1`). #1270 already commits each tree top as a registered row
(`TOPS = "hm96-sha512/v1/node-row"`), in row/v1 today. What isn't built:
- **Python**: `one_stage/registered.py` (`SCHEMA`, `row_words`, `row_digest`, the domain's format) and its vectors.
- **The Lean verifier**: `Flock/Registered.lean` reads row/v1 only. `Flock/HmRow.lean` already computes row/v2 leaves.
- **The prover**: the Rust prover's `--registered` rows, and the in-circuit row digest, whose prefix carries the bit length.
- **Recursion**: `rec_live.top_rows` and `RecOpen`'s reads (rec-step3), changed together.
- **The lock**: the `ZkReg` theorems read the verifier's registered path (`Flock/Registered.lean`, `HmRow.lean`). If their
  records change, they need a named statement reviewer.

## 5. What each call is guaranteed by

| call | party | guarantee | status |
|---|---|---|---|
| `commit`: hiding | prover gateway | `hm96Hiding_gap`; `gatewayLeaf` under `hash-derived-key` in `RecursiveZK` | main; #1261 |
| `commit`: binding | prover gateway | `cr/sha-512`; `stage_bind` inside `RecursiveSound` | assumption; #1261 |
| `commit_fresh`: possession | prover gateway | a new random-oracle claim, plus PoUS's restated answer check | none yet |
| `commit_registered` at row/v2 | prover gateway | the `ZkReg` family, restated at row/v2 | none yet |
| `receive` | verifier gateway | one-stage's R1–R7 (Python, normative); `prob_auditReg` (`Audit/RegDraw.lean`) | main |
| `coins`: session | verifier gateway | the coin tree, checked by `Flock/CoinTree.lean`; `gk_simulate_hm96`; A6 today, A3 after #1237's third PR | main; #1237 |
| `coins`: epoch, nonce | verifier gateway | — | none yet |
| `select`: one-stage law | verifier gateway | sampled proofs' law: `subset_miss`, `stratified_escape`, `work_escape_le`, and `drawOS_*_escape_le` for the running draw under A3 | main |
| `select`: two-stage | verifier gateway | `twoStage_count`, `two_stage_b_tight`, `effEscape_bernoulli_prod` | main, coverage unchecked |
| `select`: sequential | verifier gateway | — (PoUS's `P2SlackFamilyUncond` assumes uniform indices) | none yet |
| `timed`: the deadline | verifier gateway | its clock and the audit's isolation, as named claims (PoUS R3, R8); #1227 measures the loop | none yet |
| `prove` + `verify`: direct ZK, soundness | prover gateway, batch verifier | the `zk_session_*` family (`zk_session_soundJ_custody`, `zk_session_soundR`, `zk_session_soundHJR_custody`) | main |
| `prove`: direct ZK, zero knowledge | prover gateway | honest-verifier at each coin vector: `zk_session_view`, `zk_session_view_all`, `session_shvzk_le`; against a malicious auditor, `gk_simulate_hm96` instantiated at C-Flock's `--zk` | main; the instance none yet |
| the gateway's send check | prover gateway | the rule in #1270's PROTOCOL §10; `gateway_no_free_choice` proposed | none yet |
| `prove` + `verify`: recursive | prover gateway, batch verifier | `RecursiveSound`, `RecursiveZK` over `VBridge` | #1261; `VBridge` #1258 and plan |
| `outcome` | batch verifier | one-stage's audit (`audit_le`, `audit_count`, `audit_drawn`, `audits_seq`); C-Flock's `EndToEnd` | main; #1257 |
| the record's custody | verifier gateway | `live-verifier` (`RecordCustodyZKJ`) | assumption; #1237 |

What the table means for a protocol:

- **Recursion's soundness.** `RecursiveSound` bounds acceptance of a false hidden statement by the outer session's error,
  plus each round's binding term, plus the inner error. That last error is `2^-205` for C-Flock's interactive table at
  22 ≤ m ≤ 33 (`flock_inner_sound_fast100`). It counts as end to end only once `VBridge` is proved. That proof is
  3,450–6,080 Lean lines in the vbridge plan (`note:proofs/20261005T2345Z-draft-vbridge-plan`). Pieces A (#1258), B1 and
  B2 are proved on branches, and E is under way.
- **Zero knowledge.** `RecursiveZK` is within `εo + nh·2^-193` of a simulator. It holds against a malicious auditor only
  given the outer session's malicious-auditor zero knowledge (`hOuter`), the same gap as direct ZK's: `gk_simulate_hm96`
  is not yet instantiated at C-Flock's `--zk`.
- **C-Flock's `EndToEnd`.** It is the count curve:
  `Pr[accept ∧ ≥ K₀ wrong] ≤ C(n − K₀, kd)/C(n, kd) + ksAvgStrictZ + δ_link`, for the subset law and public outputs. The
  drawn-unit form, hidden outputs and registered reads are its steps B to D.
- **What none of these covers.** Aborts and timing are outside every one of them by name. A refusal costs at most
  `log₂(R + 1)` bits a session (#1270). That is the warden's subject (warden R5).

## 6. What core has, and what's new

| piece | on main `c305471c5` | in flight | new for the service |
|---|---|---|---|
| registration, receipt, draw checks, audit record | `verity/protocols/verification/sampled_proofs/one_stage/` (`registration`, `draw`, `partition`, `audit`, `verdict`) | — | context binding; one root over per-call roots; public items only (the architecture note's section 2); times as deadline bits |
| registered values | `one_stage/registered.py` (`Registered.commit`, row/v1) | #1270: tops as registered rows | row/v2 (section 4) |
| two-stage law | `experimental/verity_experimental/sampled_proofs/law.py` (`TwoStageLaw`, `OwnRandomness`) | — | the driver, a general stage 1, the move into core |
| commitment schemes | `verity/primitives/commitments/hm96/`, `merkle.py` (frame-v3-sha512), `rowleaf.py` (row/v2, row-seg/v1) | — | the split commit (digests in, salted leaves out); streams; the nonce prefix |
| randomness | `verity/primitives/randomness` (`derive`, `Key.uniform`, `bernoulli`, `subset`) | — | the epoch, session and nonce domains |
| integrity profile | `verity/protocols/profile.py` (`IntegrityProfile`, `Stratified`) | — | `Exhaustive` beside it |
| C-Flock prover | `backends/flock/live` (`flock-circuit prove --zk`, `serve`, `src/coin_tree.rs`) | #1270: `FC_GATE=1` (`src/gate.rs`) | sessions per template class at the block limit |
| verifier of record | `backends/flock/verifier/lean/Flock/` (`Verify`, `Zk`, `Draw`, `CoinTree`, `Registered`, `HmRow`) | #1237: `flock-audit`, the auditor as a Lean program | the timed mode; the sequential draw |
| prover gateway | — | `verity_flock.rec_live` (#1245; the inner gateway on #1270), the outer gate (#1270) | the gateway as one Lean program: your choice (a) or (b) in #1270's note |
| recursion | — | `rec_vstar`, `rec_outer` (#1245, #1246); `RecursiveSound` and `RecursiveZK` (#1261); `VBridge` (#1258) | V* climbing to the salted tops (rec-step3) |
| PoUS's timed loop | — | #1227 | the service's `timed` on it |

The service's protocol-facing types would sit beside sampled proofs in `verity.protocols.verification`, created with the
first user's code and not before. The gateways are C-Flock's (`backends/flock`), and the verifier gateway is `flock-audit`.

## 7. The users' requirements

PoUS's numbers here are from its first version (7:29 PM PDT). memory-accounting restated it for the ruling at
8:07 PM PDT and renumbered it, and the architecture note uses the new numbers.

| requirement | met by | status |
|---|---|---|
| PoUW R1: commit fast enough for ~109 MB of A rows per decode step | `commit` taking GPU digests, salted by the gateway, batched per pass | open: the GPU digest kernel and the gateway's rate, which served-zk measures |
| PoUW R2: per-call roots | `Handle.root()` per call; one root over them in the registration | new |
| PoUW R3: registered row/v2 | `commit_registered` | proofs takes it (section 4) |
| PoUW R4: public outputs | `Check.public_outputs`, in the outer statement's public file | open: `RecursiveZK`'s simulator must read them |
| PoUW R5: epoch coins before work | `coins("epoch", after=receipt)` | new |
| PoUW R6: interiors after the draw | `TwoStage` | proofs takes it (section 4) |
| PoUW R7: per-unit work | under the ruling, a uniform `subset:K′` over N equal tiles, K′ scaled by N·w_max/W (architecture note L3) | proofs' recommendation; compute-accounting to agree |
| PoUW R8: protocol-chosen units | `Selection.extra` | new |
| PoUW R9: verifier-derived regions | `Check.regions`; prover-supplied refused | new in the service; C-Flock reads the file today |
| PoUW R10: context binding | `Spec.context`, in the registration | new |
| PoUW R11: verify latency; windows apart from the epoch | windows independent of epochs; sessions per template class | open: Lean verify time is the largest unknown |
| PoUW R12: recursion or direct ZK | `prove` picks by size | open: the crossover is unmeasured |
| PoUW R13: egress | a deployment premise | the warden's |
| PoUS R1: possession inside the deadline | `commit_fresh` and a new claim | open (section 3); PoUS waits on it |
| PoUS R2: sequential draw | `Sequential` in `timed` | new |
| PoUS R3: the verifier gateway on the node | `timed` runs there | open: what makes it auditor-trusted there (question for Daniel) |
| PoUS R4: loop latency | `timed` on #1227's Lean-owned loop | new |
| PoUS R6: storage is not wrong units | `Exhaustive`; `StorageProfile` stays PoUS's | agreed |
| PoUS R7: timed parameters | `Deadline`; the strict audit first | new |
| PoUS R8: isolation as soundness | not the developer's gateway; the warden on auditor-trusted terms | open (question for Daniel) |
| PoUS R9: one commitment to W | `commit_registered` once per deployment, read through PoUS's layout map | new; the mode is the deployment's |
| PoUS R10: vk's leaf format | frame-v3 at P2's next revision; hm96-sha512 in hidden mode | PoUS's change |
| warden R1: arrival times are a channel | the record keeps deadline bits only; the gateway's egress to the verifier gateway on a warden grid | open: the bit-only record protects only against an honest verifier gateway, and the grid against a malicious one |
| warden R2: "all" and a charge | `All`; `Exhaustive` per unit; the warden charges | agreed |
| warden R3: commit off the tick | `commit_stream` | new |
| warden R4: coins as ingress | — | needs Daniel |
| warden R5: aborts and timing composed with `RecursiveZK` | a joint corollary | open; proofs and network-accounting, not tonight |

## 8. PoUW's noise seed and γ

compute-accounting's question 1: does Pearl-C's γ hold if E_A comes from the epoch coins and the matmul's index alone
(option (a)), so that A is chosen after the coins? **No** (`note:pouw-gamma/20261006T0318Z-finding-gamma-adaptive-a`).
Knowing each row's noise first, the prover forms every row onto a few shared targets: at 8192³, 256 of 256 rows landed
bit for bit on 16 shared A′ rows, every rule Pearl-C v1 applies passed, and its work fell to 2–4% of W_ref (γ ≈ 96–98%).
PoUW takes option (b) per row, the `-h3` format: row i of call u seeds E_A from (coins, the GPU's own unsalted digest of
row i, root_B, u·2³² + i). `coins("epoch")` still suffices, no call waits on a root, and γ stays 0.36949% with no new
assumption (`ttOutRowSeed_of_ttOut`, on main). Owed: the served line's row-seeded twin theorem and the deployed seed's
statement review. Option (c), the gateway inside decode's per-call path, is out. The architecture note's section 4.1
has the details.

## Checkpoint

- 5 Oct, 8:00 PM PDT (03:00Z): deliverable 1 written, ahead of the 10:45 PM PDT deadline. Next: deliverable 2,
  `proof-service-architecture`.
- 5 Oct, 8:17 PM PDT (03:17Z): clear mode removed, per the coordinator's relay of the 7:48 PM ruling. The rest of the
  ruling is applied in `note:proofs/20261006T0307Z-draft-proof-service-architecture`. A steward sync at 8:07 PM PDT had
  put back an older copy of this note; this version restores the 8:00 PM text.
- 5 Oct, 8:27 PM PDT (03:27Z): `receive` restated (salted roots and public items only, the auditor's copies moved into
  the window statement), the fourth point on which the architecture note supersedes this one.
