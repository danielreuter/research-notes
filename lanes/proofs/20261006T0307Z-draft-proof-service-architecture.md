---
id: proofs/20261006T0307Z-draft-proof-service-architecture
campaign: proofs
lane: proofs
kind: draft
status: agreed by compute-accounting, memory-accounting and network-accounting (5 Oct, 8:41 PM PDT); for Daniel
repo: danielreuter/verity
origin: bc-bb283e71-f122-57b3-b894-fccb8cd2ada1 (proof-service, for the proofs coordinator bc-8416bc72)
---

# The proof service: architecture (draft for the three leads)

For Daniel and the three leads, written 5 Oct from 8:07 PM PDT. It answers your 7:17 PM PDT directive: PoUW, PoUS and the
network warden each state what is committed, which units need proofs, the check, and what they do with the outcome. The
proof service does everything else. It refines proofs' interface note (`note:proofs/20261006T0255Z-draft-proof-service-interface`,
here "the interface note") under your 7:48 PM PDT ruling: in every protocol the circuit and the data are hidden, there is
no clear mode, and only the minimum is public, each public item with its reason.

Read at `origin/main` `c305471c5`. Inputs, at the notes commits named:
- compute-accounting's `note:20261006T0233Z-draft-pouw-service-user` (PoUW; requirements R1–R13, questions Q1–Q7; its
  public list at `5e71daace`);
- memory-accounting's `note:20261006T0229Z-draft-proof-service-pous`, restated for the ruling at 8:07 PM PDT (`a5825f376`;
  PoUS; R1–R12, Q1–Q7);
- network-accounting's `note:network-accounting/network-accounting/20261006T0230Z-draft-warden-proof-service` (the warden;
  R1–R5; revised for the ruling at `40968ff4b`);
- compute-accounting's ask, relayed by the proofs coordinator at 8:15 PM PDT: make W's row schema one service choice.

## The short version

- **The service is one API over four parties.** A protocol hands it a `Spec` (its committed values, selection rule, check
  and public items) and gets back an `Outcome`. The GPU workers (trusted by neither party) compute. The prover gateway
  (developer-trusted) commits, registers and proves. The verifier gateway (auditor-trusted) issues live coins, draws, runs
  timed sessions and keeps the record. The batch verifier (auditor-trusted, Lean) verifies and writes the outcome.
- **The 7:48 PM ruling becomes one rule the service enforces.** Everything the auditor can observe must be a function of the
  `Spec`'s public items. That covers the registration's fields, which proof mode the service picks, the number and size of
  sessions, and each message's size and timing. Public items are the minimum each protocol needs, each with its reason,
  and come in four kinds (top, 8:15 PM PDT, after compute-accounting): protocol structure (scheme constants, the check's
  Program, the selection law and its parameters); the protocol's outputs (the verdict, PoUW's credited work N, δ in its
  profile); the verifier's own coins and draws (PoUW's drawn indices); and hiding commitments (W's salted root). Never
  public: the developer's data, its circuit, or anything that reveals them, such as shapes, row indices, layouts and
  unsalted digests. Daniel checks each protocol's list. Four changes follow:
  - The registration stops showing per-template populations, per-root leaf counts and per-call roots.
  - A drawn unit's position is read in gates, with `MerkleRead_v1` (on main) and the subtree read (#1063).
  - There is no clear mode.
  - The warden's statements are padded to its public capacity.
- **W is committed once, by weight row** (section 2.1). It is stored as registered `hm96-sha512/row/v2` values in W's
  stored dtype, and the service fixes that schema. PoUW reads its rows aligned. PoUS's setup opens the one or two rows each
  2,054-byte payload touches, which costs about 10–65% more per setup block, by row width. The other layout would cost
  PoUW 20–50% more hashing on 1.38M weight rows every epoch.
- **Each protocol gets a short call sequence** (section 4):
  - PoUW: epoch coins, then serve-time commits, then a two-stage draw per audit window, a recursive proof and the profile.
  - PoUS: a recursive setup proof over committed W and C, then a sequential timed session on the node with nonce-bound
    commits, then one proof of the answers and an exhaustive fact.
  - The warden: streamed commits, every link-window selected, and a ZK proof of the grid check per window.
- **Each protocol deletes its own copies of the infrastructure** (section 5). For PoUW that is about 7k lines in its own
  files. PoUS loses its timed verifier's loops, transport, salt, draw, vk tree and public-encoder setup, and keeps its
  acceptance rules as the oracle the service's timed mode is difftested against. The warden loses its
  digest, record-keeping and publishing.
- **The migration starts tonight with served-zk** (section 6): one served request whose commitment the proof opens, with
  the draw moved from `os.urandom` to one-stage's registration, receipt and Lean draw. The order after that: the warden's
  records, PoUW's draw, registered row/v2, PoUS's timed mode, epoch coins, the two-stage driver, hidden layout, then
  recursion as a mode.
- **Ten questions need Daniel** (section 7), each with proofs' recommendation. The rest are for the leads and proofs.
  Section 8 lists the asks of each lead.

## 1. What changed since the interface note

**The 7:48 PM ruling, read as a service rule.** Hiding the data is what commitments and zero knowledge already do. The
ruling goes further in three places.

1. **Structure is data too.** These are all hidden:
   - the model's matmul graph and its shapes;
   - the batch per step;
   - row indices;
   - the number of calls;
   - the warden's frame counts.

   Today one-stage's registration (`one_stage/registration.py`) shows the auditor the program's digest, the query, each
   template's population, the law's strata with their counts, and every root's leaf count. The auditor checks the record
   against its own copy of the program. Under the ruling the auditor holds only the public check Program and the public
   items. So a registration carries the public items and salted roots, and nothing else.

   This supersedes the 2026-10-01 (3:32 PM PDT) ruling's "shapes such as batch size and sequence length may stay public
   for now" (`.agents/skills/friction/SKILL.md`). #1277 adds the skill's lines for the 7:48, 7:17 and 7:11 PM rulings
   and points the old clause to them, so that nobody reads it as current.

   What the auditor used to check against its own copies moves into a **window statement**: a small Program, proved once
   per window. Its public outputs are the public aggregates, such as PoUW's unit count N and its credited work, and it
   shows that the committed layout is well formed.
2. **What the service does can leak.** If the service picks direct ZK for a quiet warden link and recursion for a busy
   one, the choice reveals the link's traffic, and a session's size reveals its frame count. So `prove` picks its mode and
   sizes from public items only. A statement whose real size is hidden is padded to a public bound.
3. **There is no clear mode,** for secret data or for public data. The interface note's native-check branch is gone (that
   note is updated). All three users had already dropped it. PoUS now proves its setup over committed W and C, and its
   guarantee waits on `commit_fresh`'s possession claim (question D3).

**PoUS's restated note** costs its setup. P2's 16,448-bit squarings are non-native in C-Flock's GF(2), so a block's setup
statement is about 6.3e7 ANDs, 92% of them in the squarings. memory-accounting's estimates:
- An exhaustive setup is about 1,300 recursive sessions per GB of W: 2.9 GPU-hours of outer proving, 25 GB of proofs and
  about 16 hours of Lean verify.
- A sampled `subset:s` setup is 8 sessions (s = 2,759, ε = 1% at 2^-40) or 24 (s = 8,828, at 2^-128), whatever |W| is.
  It needs a restated certificate (`P2SlackFamilyFreeBlocks`) and a larger k.

**γ (pouw-gamma, 8:18 PM PDT).** It does not hold with E_A from the coins and the matmul's index alone (option (a)): at
8192³, 256 of 256 rows formed exactly onto 16 shared A′ rows, so the prover's work falls to 2–4%. Per-row seeds (`-h3`)
keep γ at 0.36949% with no new assumption and no gateway on decode's path. Section 4.1 has the details and D1 the
recommendation.

## 2. The API, refined

```python
@dataclass(frozen=True)
class Spec:
    values: tuple[Value, ...]          # (1) what is committed
    selection: Selection               # (2) which units need proofs
    check: Check                       # (3) the check each selected unit passes
    public: tuple[Public, ...]         # what the auditor may see beyond the service's own items
    context: bytes                     # the statement context (PoUW's identifier v1), bound into every registration
                                       # (4), what the protocol does with the Outcome, is the protocol's own code

@dataclass(frozen=True)
class Public:
    item: str                          # "N", "credited work", "B", "(T, r, B, tau_b)", "Sigma_sync", "root_W"
    kind: str                          # "structure" | "output" | "coins" (the verifier's coins and draws)
                                       # | "commitment" (hiding: salted); never the data, the circuit, or what reveals them
    reason: str                        # why it must be public
    source: str                        # "parameter" (fixed before the run) | "window" (a public output of Check.window)

@dataclass(frozen=True)
class Value:
    name: str                          # "A", "vk", "rows", "answers"; "W" names the deployment's registered weights
    schema: str | None                 # "hm96-sha512/row/v2" | "hm96-sha512/row-seg/v1"; None for registered values,
                                       # whose schema the service fixes (section 2.1)
    phase: str                         # "epoch" | "serve" | "interior" (after the draw) | "in-deadline"
    registered: bool = False           # committed once per deployment, read by position
    fresh: bool = False                # nonce-bound inside a deadline (PoUS's answers)

Selection = All() | Law(text) | TwoStage(replay: Law, check: "all" | int) | Sequential(law="uniform:k", population)

@dataclass(frozen=True)
class Check:
    program: Program                   # the public per-unit check, by digest
    query: Query                       # its proof units: a fixed public shape per template class
    window: Program | None = None      # once per window, over the committed layout; outputs the "window" public items
    public_outputs: tuple[str, ...] = ()   # read by the auditor; given to RecursiveZK's simulator (PoUW R4)
    deadline: Deadline | None = None   # delta, delta_late, cap, n, miss budget, RTT cap: a property of the record
    proof_deadline: Duration | None = None # a proof that verifies after it is refused, and the outcome is a reject

@dataclass(frozen=True)
class Outcome:
    accepted: bool
    verdict: Verdict                   # one_stage.verdict.Verdict
    profile: IntegrityProfile | None   # sampled selections: wrong units at delta
    exhaustive: Exhaustive | None      # All and Sequential: each unit's verdict, and in time or not
    terms: Terms                       # proof, binding, possession, sampling: named error terms
    public: Mapping[str, object]       # the window statement's public outputs, now proved
    record: bytes                      # SHA-512 of the record
```

The calls are the interface note's (its section 2), with these changes:

- **`commit` keeps per-call roots at the prover gateway.** The window's registration carries one root over a committed list
  of per-call entries, padded to a public bound. Per-call roots in the clear would show the number of calls and each one's
  rows, which is the batch per step. This changes PoUW's R2. Its property C1, that every call's commitment precedes the
  draw's key, still holds, because the window root is registered before the draw.
- **`commit_registered` is the only way W is committed,** with the schema fixed by the service (section 2.1).
- **`register` enforces the public-items rule.** The verifier gateway refuses a registration with a field that is neither
  a salted root nor a declared public item.
- **`select` draws indices in [0, N) or [0, B), with N and B public.** A drawn PoUW index names a unit only inside the proof.
- **`prove` reads positions in gates and picks its mode from public items.**
  - Each drawn index resolves to committed positions in gates, read from the committed layout with `MerkleRead_v1`
    (`verity/primitives/commitments/gates/merkle.py`, #1050, merged and circuit-checked), or with the subtree read
    (`MerkleSubtreeRead_v1`, #1063, open) for an aligned run of rows such as a tile's 64 A rows.
  - It proves `Check.window` once per window.
  - It picks direct ZK or recursion, and the session sizes, from public items only.
  - A job may be many sessions with one outcome, such as PoUS's setup or PoUW's window (PoUS R12).
- **`outcome` stays pending until the proof verifies** (PoUS R5). It binds the proof to the session's record digest, and
  refuses a proof after `Check.proof_deadline`. A developer can't wait out a rejection and retry.
- **`timed` releases on a schedule.** The prover gateway sends each answer's commitment at a fixed offset in its round, so
  an arrival time carries no information (warden R1). That uses the honest prover's margin, never soundness, because
  PoUS's certificate already grants the adversary all of Δ + RTT. The exact times stay on the verifier gateway, and the
  record keeps one on-time bit per round. **The schedule is required for zero knowledge**, not only against a malicious
  verifier gateway: `RecursiveZK` quantifies over every behavior of the auditor, and the auditor's own gateway sees
  exact arrival times whatever the record keeps. The deadline bit protects readers of the record; the fixed schedule,
  enforced by the developer-trusted prover gateway (or a warden grid on that link), protects against the auditor. A
  message that misses its slot is an abort symbol, charged under warden R5 (network-accounting).

Who runs what, unchanged from the interface note:

| party | trusted by | runs | today's code |
|---|---|---|---|
| GPU workers | neither | `digest`, `inner`, `outer_heavy` | `backends/flock/live` (Rust prover); served-zk's `hm96_rows.cu` |
| prover gateway | the developer | `commit*`, `register`, `prove`, the send check | `verity_flock.rec_live` (#1245), `FC_GATE=1` (#1270); neither on main |
| verifier gateway | the auditor | `receive`, `coins`, `select`, `timed`, `record` | `one_stage.registration`, `flock-verify draw`; `flock-audit` (#1237); #1227's loop |
| batch verifier | the auditor | `verify`, `outcome` | `flock-verify` (Lean), `one_stage.audit` |

**Guarantees.** The interface note's section 5 table stands, and the ruling adds four rows:

| call | guarantee | status |
|---|---|---|
| `prove`: a position read in gates | `MerkleRead_v1` is a circuit-checked Boolean Definition; in a session it inherits the `zk_session_*` soundness | Definition on main; the subtree read #1063 |
| `prove`: the window statement | an ordinary Program, under the same session theorems | none yet: each protocol writes its own |
| the public-items rule | no theorem. It is what `RecursiveZK`'s simulator needs, and the joint corollary (warden R5) is where it gets stated | none yet |
| `timed`: scheduled release, required for ZK against the auditor; a missed slot is an abort symbol charged under warden R5 | the warden's constant-rate bound (`EncardDecodableLeConstantRate`) on the gateway link | main, for the warden's links; not instantiated |

### 2.1 W's row schema: one service choice

compute-accounting asked for this, so that PoUS's 2,054-byte hiding rows and PoUW's row/v2 can't drift apart. The
service fixes the schema of registered values. A protocol's `Spec` names the deployment's registered W and never
declares a schema for it.

**W is committed by weight row.** Each row of each weight matrix becomes one `hm96-sha512/row/v2` registered value: the
hiding leaf over PoUW's `sha512/row/v2` row digest, whose prefix carries the row's bit length. The rows are in W's stored
dtype (BF16 for the served model), in a committed tensor order. A committed tensor table gives each tensor's row count and
row length. PoUS and PoUW share that table, and it is hidden. W's byte stream, for PoUS, is the concatenation of those rows.

**How PoUW opens it.** Each B_j is one aligned row, read at a hidden position. PoUW widens BF16 to FP32 in gates, as `pc4`
already does for A (`row-bf16/v1`), so W's commitment halves against today's `pouw/row-fp32/v1`. This moves `pc8`'s
weight-side digests, which is compute-accounting's change to make.

**How PoUS opens it.** Payload i is bytes [2,054·i, 2,054·(i + 1)) of the stream. `P2Decode` finds the one or two rows
those bytes fall in from the tensor table, in gates, opens them at hidden positions, and extracts the payload. The cost
uses memory-accounting's rule of about R/128 SHA-512 compressions per R-byte row, and their figure of about 2.5e6 ANDs per
hidden path. Against today's 6.26e7 ANDs a block, a setup block costs:
- about 10–25% more for 8 KiB rows (k = 4,096: `gate_up`, `qkv`, `o`), the high end when a payload straddles two rows;
- about 30–65% more for `down`'s 28 KiB rows (k = 14,336).

A sampled setup's 24 sessions become about 29 to 40 (*estimate*).

**Why not PoUS's layout.** Committing W as 2,054-byte payload rows would let PoUS open row i at public position i, with
no table. PoUW would then read each B_j across 4 to 15 unaligned payload rows, about 20–50% more hashing per weight row,
plus a second hidden path where a row straddles a subtree boundary. PoUW proves about 1.38M weight rows every epoch, so
that is about 4e12 extra ANDs an epoch, and every 15 minutes. PoUS's extra under the weight-row layout is about 2e11 ANDs
once per deployment for a sampled setup. Even an exhaustive setup's extra, about 1e14 for a 16 GB model, is less than a
day of the other layout's PoUW cost (*estimates*). A second, PoUS-only root would need a proof of equality: about 1.6e12
ANDs per GB, by memory-accounting's estimate.

What isn't built: registered row/v2 (the interface note's section 4), the tensor table as a committed value with its
well-formedness in PoUS's setup statement and PoUW's epoch statement, and PoUW's BF16 weight rows.

## 3. What each protocol states

These are the four things, restated from the users' notes under the ruling. A protocol's check can be any Program: under
the 2026-10-04 (8:42 AM PDT) ruling, soundness is one theorem over everything the compiled Lean verifier accepts, so a new
check needs `circuit-check` (AGENTS.md) and no change to the verifier. The verifier refuses a form its proof doesn't
cover, which limits completeness and never soundness.

**PoUW (Pearl-C).**
- What is committed:
  - per deployment, W, as registered values (section 2.1);
  - per epoch, the workload declaration;
  - per call, A's rows, the tile digests and the call's `UnitRecord`;
  - after the draw, the drawn tiles' interiors (A′, ok, `rowk`'s carries and the cap rows).
- Selection: `TwoStage(replay=subset over N tiles, check="all")`. Every unit is one 64 × 64 × `row_k` tile.
- The check: `Pc8CheckHidden` (`pouw/circuit/pc8.py`). Its window statement proves the work sum, the index-to-tile map, and
  the excluded and voluntary rows' rules.
- Public items, from compute-accounting's list:
  - the verdict per window;
  - N and the credited work;
  - the check's scheme id and constants;
  - ε, δ and the drawn indices;
  - the weights' salted root;
  - the profile.
- The outcome feeds `Theorem1` and γ, and then the credit.

**PoUW (`ncp-v2`).**
- What is committed: A's int7 rows; B registered; Y strips and c₀ per weight; each unit's outputs.
- Selection: `Law("work:K")` with its closure.
- The check: `NcpLinear_v1`, `NcpWeight_v1`.
- The outcome: a `Stratified` profile, then γ from `TTNCP_U`.
- One conflict with the ruling: these templates carry the matmul's shape in their names (`{M,K,N,PERM}`). That is question
  L5.

**PoUS (P2).**
- What is committed:
  - W, as registered values (section 2.1);
  - C, by the prover, under hm96-sha512 hiding leaves in a frame-v3 tree;
  - each audit answer, nonce-bound inside its deadline (`A_j`).
- Selection, at setup: `All()` or `Law("subset:s")` over the B blocks (question D10).
- Selection, at audit: `Sequential("uniform:k", B)`. k is 105 after an exhaustive setup, and 120 or 140 after a sampled one.
- The check: `P2Decode` at setup and `AnswerOpens` at audit, both public Programs to write. The deadline is Δ + RTT =
  854 µs (#1159).
- Public items, from memory-accounting's list:
  - the verdict and the `StorageProfile`;
  - the scheme's and the certificate's parameters, and B;
  - W's and C's roots, and the salt;
  - the setup indices and the setup profile;
  - the `A_j`;
  - the audit's indices and nonces, once the session closes;
  - each round's on-time bit, the record's only timing (an output);
  - the k drawn hiding leaves of C, `AnswerOpens`' public inputs (section 4.3 step 8). They are hiding, so they reveal
    nothing about C; the verifier gateway holds all B of them from setup and checks them against C's registered root;
  - a rejection or abort.
- The outcome: `P2SlackFamilyUncond` (or `P2SlackFamilyFreeBlocks` after a sampled setup), then the `StorageProfile`.

**The warden.**
- What is committed: per link-window, the record, its T row digests and the declared clock sync, with the frames' leaves
  taken from the served commitment.
- Selection: `All()`.
- The check: `NetTiming`'s `Accepted (constantRate …)` for egress and `StatusComplete` for ingress, in code form
  `warden_program` (#1268).
- Public items, from network-accounting's list:
  - the verdict per link-window;
  - whether each record arrived by its deadline;
  - the parameters;
  - the charge.
- The outcome: the charge, and the run is rejected on any violation.

## 4. Call sequences

### 4.1 PoUW, Pearl-C on sm_120

Per deployment and per epoch (about 15 minutes):
1. The prover gateway commits W once per deployment, with `commit_registered` and the tensor table (section 2.1). Every
   epoch, it commits the epoch's workload declaration with `commit` and calls `register`.
2. The verifier gateway `receive`s the registration, logs a receipt, and answers `coins("epoch", after=receipt)`.
3. The GPUs expand the coins into the epoch's salt and noise.

> **γ with A chosen after the epoch coins: it does not hold under option (a). Seed each row instead (`-h3`), and γ stays
> 0.36949% at 8192³** (pouw-gamma, `note:pouw-gamma/20261006T0318Z-finding-gamma-adaptive-a`, 8:18 PM PDT).
> - Under (a), E_A comes from the coins and the matmul's index alone, so the prover knows each row's noise before it
>   chooses the row. It can choose each row of A so that the formed row A′ lands exactly on one of a few shared targets,
>   then compute those few rows of C̃ once per weight per epoch and copy them. On the exact reference at 8192³ (sm_120),
>   256 of 256 rows (8 calls × 32) formed bit for bit onto 16 shared A′ rows, 216 onto one. Every row passed the noise
>   floor and `live_row`, the replayed debit stayed under the 1/1000 cap, and every tile was computed correctly, so
>   neither the hidden audit nor the work law's draws sees anything. The prover's work falls to about 2–4% of W_ref: the
>   best γ under (a) is about 96–98%, no bound at all.
> - No new statement rescues (a). The game already lets the prover choose A after the salt; the γ theorems take TT_OUT
>   at the semantics as a hypothesis, and under (a) that hypothesis is false (the attack is a counterexample).
> - **The fix is a per-row form of option (b), already designed and proved:** row i of call u draws E_A from
>   H_"pearl-c/v0/seed-A"(coins ‖ leaf_i ‖ root_B ‖ u·2³² + i), with leaf_i the GPU's own unsalted digest of the row
>   (step 4's `digest`). The coins can stay public before serving, and neither the gateway nor a round trip sits on
>   decode's path. `ttOutRowSeed_of_ttOut` (on main) reduces the row-seeded TT_OUT to the granted per-unit one with no
>   new named assumption; the error becomes (q + R)/2¹²⁸ over the R declared rows.
> - Cost: on the panel `-h3` is cheaper than `-h2` (1.340× against 1.464× at decode, 1.205× against 1.223× at prefill,
>   GPU 1's real call). In the hidden audit, an estimated 0.1–0.2M ANDs per drawn A row, about 1% of that row's hm96
>   read, keyed on the SHA-512 row digest the gadget already computes, with E_A private.
> - Owed, Lean only: the row-seeded `K` twin of `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` (the served line,
>   LoopCast8p72, cap 1/1000), a mechanical port of `RowSeedGamma.lean` that compute-accounting owns, and the statement
>   review of (C1) and (C2), the deployed seed's conditions.
> - Pearl-C4 has the same seed_A shape and was not tested, so it stays off served accounting until the attack has been
>   run on it (compute-accounting).
> - Under the ruling, the anchors' positions move into gates either way, because a unit's coordinates are hidden.

Serving, per call:

4. The GPU computes A's unsalted row digests (`digest`, row-seg/v1) and the call's `UnitRecord`. Under `-h3` each row's
   digest is computed **before forming and seeds that row's E_A**, so there is one digest per A row: if the seed is keyed
   on hm96's inner SHA-512 row digest (pouw-gamma's recommendation), the commitment and the seed read the same digest and
   the GPU hashes each row once. That puts SHA-512 on decode's path ahead of forming, unlike `-h2`'s tree, which is off
   it. The measured 1.340× is `-h3` with BLAKE3; the SHA-512-keyed seed is unmeasured, and compute-accounting times both
   in the 12:00 AM PDT (07:00Z) window. The prover gateway salts the digests into the window's handle, asynchronously and
   off decode's critical path. Nothing leaves the developer's site.

Per audit window (decoupled from the epoch, question D6):

5. At a fixed time after the window closes, the prover gateway calls `register` with the window's root, N and the claimed
   credited work. The verifier gateway logs the receipt.
6. The verifier gateway draws K′ tile indices in [0, N) from its own randomness with
   `select(receipt, TwoStage(subset:K′, all))`. K′ is set from ε, δ and the public ratio N·w_max/W (question L3).
7. The GPUs regenerate the drawn tiles' interiors, and the prover gateway commits and registers them. The verifier gateway
   logs the second receipt.
8. The service proves recursively:
   - Inner sessions run per template class, sized to the block limit. Each drawn tile's rows are read at hidden positions:
     one path into the root over calls, one subtree read for A's rows, and one row read in the registered W.
   - The window statement is proved alongside them.
   - V*'s outer session goes through the gate (#1270).
9. The batch verifier runs `verify` with Lean's `flock-verify`, then `outcome`. That gives the subset law's
   `IntegrityProfile` over N tiles at δ, the terms (`RecursiveSound`'s error and binding), and the proved N and credited
   work.
10. PoUW applies `Theorem1` with δ_s from the profile. It takes γ from the **row-seeded `K` twin of
    `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192`, which is owed**: a port of `RowSeedGamma.lean`, by a
    compute-accounting lane started tonight, plus the statement review of (C1) and (C2). The per-unit theorem as it
    stands does not cover `-h3` and is not cited for it. `TileProofSoundAll` is discharged by `RecursiveSound` once
    `VBridge` is proved. The result is certified work
    (1 − γ)(1 − ε_s)·W, and PoUW credits it.

### 4.2 PoUW, `ncp-v2`

The same as 4.1 with three differences:
- The epoch coins give only the salt, since `ncp-v2`'s noise is Fiat-Shamir in gates. It has no seed_A problem.
- The selection is one-stage (`Law("work:K")` with its closure), so there is no step 7.
- `prove` takes direct ZK or recursion by the drawn statement's public size.

The serving side's change is vLLM's unsalted SHA-256 leaves (`pouw_circuit.py`) becoming `commit`.

### 4.3 PoUS

Setup, once per deployment. Each coin comes after the previous receipt, and the record shows the order (PoUS R11).
1. W is the deployment's registered commitment, shared with PoUW (section 2.1). The verifier gateway issues the 24-byte
   salt as `coins("epoch", after=receipt of W)`.
2. The GPUs encode C = Enc(W, salt). The prover gateway commits C's hm96-sha512 leaves and registers C's root, and the
   verifier gateway logs the receipt.
3. The verifier gateway draws the setup selection, `All()` or `subset:s` over the B blocks, after C's receipt.
4. The service proves `P2Decode` on the drawn blocks recursively: 8 or 24 sessions for a sampled setup, about 1,300 per GB
   for an exhaustive one. The public inputs are W's root, C's root, the salt and the indices, and W's rows are read at
   hidden positions through the tensor table. Direct CPU `--zk` would take memory-accounting's estimated 22 days per GB,
   so recursion is the only option.
5. Once the proof verifies, `outcome` gives the setup profile (s, m, δ_s), and PoUS registers vk = (C's root, B, the
   profile). A proof after the proof deadline is refused.

Each audit:

6. PoUS takes k, Δ = 500 µs and the RTT cap of 354 µs from its certificate, and refuses anything outside it
   (`Certificate.refusals`).
7. The on-node verifier gateway runs `timed(C's root, Sequential("uniform:k", B), deadline, fresh=True)` on #1227's
   Lean-owned loop:
   - It measures the RTT between the gateways first, and refuses an allowance above 354 µs.
   - Each round, it reveals (i_j, nonce_j) as one Goldreich–Kahan opening of its coin tree.
   - The prover gateway checks the opening, reads block i_j, and sends `A_j = commit_fresh(nonce_j, block)` at a fixed
     offset. `commit_fresh` hashes nonce_j ‖ the whole 2,056-byte block; a commitment over nonce_j ‖ H(block) is the
     precomputation attack again.
   - **The offset comes from the honest per-round tail at the audit's rejection target, not from p99.9**
     (memory-accounting). 185 µs is p99.9 per round under load, and an audit is 105 rounds, so a 0.1% honest rejection
     needs about 1e-5 per round. A release after the offset counts as a miss. memory-accounting's preemptible sweep
     (bc-addb6781) measures honest acceptance at the 354 µs cap tonight; the offset is set from it and the on-node round.
     400 µs is a placeholder until then.
   - The record keeps one bit per round, on time or not, and the exact times stay on the verifier gateway.
8. After the session, the service proves `AnswerOpens`: each `A_j` opens, with nonce_j, to the same 2,056 bytes as C's
   leaf i_j, and the statement recomputes the inner digest H(block) from those bytes. The verifier gateway holds all B of
   C's hiding leaves (64 bytes a block) from setup and checks them natively against C's registered root, so the k drawn
   leaves are public inputs and the statement needs no Merkle path. That is about 3.4e8 ANDs at k = 105: one recursive session, or about 21 s of direct `--zk`. The size rule picks.
9. Once the proof verifies, by PoUS's proof deadline (it suggests an hour), `outcome` gives an `Exhaustive` fact (k of k
   on time and opened), the terms (proof, binding, possession) and the setup profile.
10. PoUS maps the fact through its certificate into the `StorageProfile`, adding the service's terms and, after a sampled
    setup, δ_s and the larger k's tail.

### 4.4 The warden

The deployment role has no calls. The developer's site (GPUs and prover gateway) is a spatial unit. The prover gateway's
link to the verifier gateway is an egress link, and the coins arrive on an ingress link. The warden enforces that these
are the only links, and bounds what their timing carries.

The user role, per link-window:
1. The proxy's worker calls `commit_stream("rows", link, window)`, appends each row (10 a second) off the tick, and calls
   `.close()` for the root. The frames' leaves are the served commitment's, so PoUW and the warden open one commitment.
2. At a fixed time after the window, the proxy calls `register`. The record keeps only whether the registration was in by
   the deadline.
3. The verifier gateway runs `select(receipt, All())`, which takes every link-window.
4. The service proves the grid check over the committed frames' digests, anchors and syncs. The statement is padded to the
   public capacity T·r, so its size depends on public items only. At r = 1,024 that probably means recursion for every
   window (question L6).
5. `verify` and `outcome` give an `Exhaustive` fact with each link-window's verdict.
6. The warden charges log₂ #Σ_sync bits per accepted egress window, plus the ingress K share. It rejects the run on any
   violation.

## 5. What each protocol deletes

**PoUW** deletes about 7k lines of its own files, 4k of them benchmarks and kernels. With core's beacon and BLS code that
is compute-accounting's 7.5k. By file:
- `pouw/audit.py`'s commitments, openings, `Sampled`, `Verifier`, `Audit` and the beacon path (~190 of 360);
- `serving.py`'s hash formats and manifest (~75), the commitment side only: PoUW keeps the per-row seed derivation
  (`-h3`'s `b3_seeds`, or its SHA-512 successor). compute-accounting also owes `pearl_c.row_seed` in the reference and
  `-h3` in PoUW's PROTOCOL.md;
- `pearl_c_work.py`'s `Beacon`, draw and replayed audit (~140);
- `circuit/plan.py`'s laws, sampler and profile (~250);
- `anchors.py`'s `Ledger`, `Receipt` and fresh source (~165);
- `leaves.py`'s digest, commit and leaf (~70);
- vLLM's on-device commitment and replay check (~780);
- the served replay (`verify_run.py`, `fast_tile.py`: 598) and Pearl-C4's replay (342);
- the -h0/-h2 hash kernels (935, keeping the TurboSHAKE leaf if the tile digest stays);
- `pouw_hash/` (2,483, already dead);
- `hidden_zk/` (1,043, whose controls become the service's tests).

PoUW keeps the row schemas, the work table and closure map, the `pc8` check, the CPU reference, the identifier, the noise
derivations, `WorkProfile` and its Lean.

**PoUS** deletes these, from memory-accounting's table:
- W's commitment (`setup.commit`, `_commitment_hash`, `COMMIT_TAG`, `w_commitment`, vLLM's `_commit`);
- vk's tree (`verifier.py`'s `MerkleTree`, `leaf_hash`, `node_hash` and `verify_path`, and `reference.py`'s second framing);
- the salt draw (`setup.draw_salt`, `setup_salt`, the bench constant, vLLM's `os.urandom` placeholder);
- the challenge draw (`audit.challenge_key`, `TimedVerifier.challenge`, `audit_key`, the `os.urandom` sources);
- the timed verifiers' loops (`TimedVerifier`, `run_timed`, `protocol.Verifier`, `ContinuousVerifier`, `p2_v1/live.py`'s
  loop), but not their acceptance rules (below);
- transport and RTT calibration (`band_gpu/live.py`'s wire, `calibrate`, `limit_of`, `ControlResponder`, `continuous.Reply`);
- the audit JSON records, with their device and server times;
- the public-encoder setup (`setup.verifier_key_from_encoding`), and the setup verifier as a mechanism.

PoUS keeps the scheme and codec, `Certificate`, `StorageProfile`, `LOCAL_CLAIMS`, `audit.simulate`, the Lean, the kernels and
the benchmark measurements. It also keeps its acceptance rules (strict, the continuous miss budget and graded: the rule
code in `audit.py` and `continuous.py`) with `audit.simulate`, as the oracle the service's timed mode is difftested
against, like the warden's Python audit. `ContinuousVerifier`'s rules are what `test_pous_continuous_difftest` checks
against the Lean model. Only the loops, transport, draws, salt, vk tree, records and public-encoder setup go
(memory-accounting). `layout.Layout` becomes the developer's private data, and the tensor table replaces it in the
statements (section 2.1). The service's sessions take k, Δ and the call time from PoUS's certificate, so P3's defaults
can no longer reach a P2 audit (the consolidation note's first fix).

**The warden** deletes:
- `commitment.py`'s digest, keeping the row format as the committed value's encoding;
- `audit.py`'s record-keeping (deadline, duplicates, settling), keeping `check_link`, `check_ingress_link` and the verdict
  names;
- `Proxy.publish`'s sink, which becomes `commit_stream` and `register`;
- `active_replay.py`'s audit, which calls `verify`.

The Python audit stays as the oracle that the Lean difftest compares against.

**Core** deletes these only if the questions go as recommended:
- `verity/primitives/crypto/beacon.py` and `bls12_381.py` (502 lines), if no protocol keeps drand (D5);
- `merkle.py`'s `frame-b3` and `frame-b3s`, once `experimental/.../multiproof.py` drops them too.

The two-stage law moves from `experimental/verity_experimental/sampled_proofs/law.py` into `sampled_proofs`.

## 6. Migration order

Each step names its owner and what it needs. Step 1 lands with step 0's code, and step 2 can start in parallel.

0. **served-zk, tonight (compute-accounting; proofs advises).**
   - Today, on `cursor/pouw-served-zk-e3fa` (`e55462bdd`, no PR), the job:
     - commits one served `o_proj` call's rows in the statement's format on the CPU, from a retained pass;
     - draws one tile from `os.urandom` after the commitment;
     - proves `Pc8TileHidden{K=4096,1,1,sm120}`;
     - checks the openings in Python and the session in Lean, with foreign-proof and foreign-commitment controls.
   - The service's first call changes three things:
     - The draw becomes one-stage's: `registration.record` (v1, one root per side, `window.kind = "served"`), `check`,
       `receipt`, then `flock-verify draw` from the verifier's own randomness.
     - The opening check goes into the audit record (`verity/one-stage/audit/v0`) beside the Lean verdict.
     - The commit takes GPU digests (`hm96_rows.cu`) salted on the host, as `rec_live` does, once the kernel is measured.
   - Roots and counts are public in this prototype, which is fine on test prompts. That is a development shortcut, which
     the 2026-10-01 (3:32 PM PDT) ruling allows for research velocity and never as the protocol. Hidden layout (step 8)
     comes before any real traffic.
   - Done means: one served request whose commitment the proof opens, with the registration, receipt, draw and Lean
     verdict in one audit record, and the controls rejecting.
1. **The service's first code (proofs).** It is created with step 0's code and not before (AGENTS.md). It holds:
   - the `Spec` and `Outcome` types;
   - the public-items check in `register`;
   - `select` and `outcome` over `one_stage`.

   The Glossary gains "proof service", "prover gateway", "verifier gateway", "batch verifier" and "selection rule" in the
   same change. Where it lives is question L12.
2. **The warden's records into the service's record (network-accounting and proofs).** No proving is involved.
   - `Proxy.publish` calls `register`.
   - The receipt keeps only the order and the deadline bit. Today `registration.receipt` stamps `received` to the second;
     that becomes the bit (warden R1).
3. **PoUW's draw into one-stage (compute-accounting).** `pc8` calls register a v2 record and take the Lean draw.
   `anchors.Ledger` and `plan`'s sampler are deleted, and the work table and closure map stay. R7 is settled here
   (question L3).
4. **Registered row/v2 and the tensor table (proofs, with both leads).** These are W's one schema (section 2.1).
   - Registered row/v2 covers Python, `Flock/Registered.lean`, the Rust `--registered`, `rec_live.top_rows`, and the
     `ZkReg` records with a named statement reviewer (the interface note's section 4).
   - Step 3 needs it for PoUW's weight side, and PoUS's setup reads W through it.
5. **PoUS's timed mode in the service (memory-accounting and proofs).**
   - It is built on #1227's loop with #1159's cap, taking nonce-bound commitments: the verifier gateway stores 64-byte
     `A_j`, not blocks.
   - Development runs on test W. PoUS's loop, transport, salt and challenge draw are deleted.
   - PoUS's guarantee waits on step 11.
6. **Epoch coins (proofs, after the γ answer).** These are PoUW's and PoUS's salts. `Epoch.start`'s drand path is retired,
   subject to D5.
7. **The two-stage driver (proofs).** It covers PoUW's interiors after the draw: the driver and its log, a general stage 1,
   the law's move into core, and the Lean coverage check (the interface note's section 4).
8. **Hidden layout (proofs, with each lead for its window statement).** This covers:
   - the registration's public-items rule;
   - `Check.window`;
   - position reads in gates (`MerkleRead_v1`, #1063).

   It must land before any real traffic.

   The cost is a few hidden paths per drawn PoUW tile, at about 14–26 ms of `--zk` proving per opening (measured at depths
   9 to 22: `hidden-reads-pricing` and #772). At K′ of 28k–55k that is about 0.3–1.2 CPU-hours a window (*estimate*),
   small beside the units themselves. The 2026-10-01 (4:31 PM PDT) ruling accepts the hidden read's cost unless it proves
   a bottleneck.
9. **Recursion as a service mode (proofs).** This takes `rec_live`, the gate (#1270) and V* climbing to the salted tops
   (rec-step3), and adds the size rule. The direct/recursive crossover gets measured here (PoUW R12).
10. **PoUW's profiles only from the service (compute-accounting).** The served replay becomes a labelled diagnostic, then
    goes. This needs R1, filler, the kept width and the cap in `pc8` first.
11. **PoUS's proofs (memory-accounting and proofs).** In order:
    1. one traced 16,448-bit squaring through `circuit-check`, the first measurement memory-accounting names;
    2. `P2Decode` and `AnswerOpens` as Programs;
    3. the possession claim (D3) and PoUS's answer check restated against it;
    4. `P2SlackFamilyFreeBlocks`, for a sampled setup (D10);
    5. `commit_fresh` in the prover gateway.
12. **The warden's ZK check over committed frames (network-accounting and proofs).**
13. **Lean composition (proofs, with compute-accounting).** This covers:
    - `HiddenAudit` instantiated with the service's per-tile game;
    - `TileProofSoundAll` from `RecursiveSound` (after `VBridge`);
    - `Theorem1` over the service's δ_s.

    The joint corollary (warden R5) comes after.
14. **`ncp-v2`'s serving commit (compute-accounting).** It moves to `commit` once question L5 is settled.

## 7. Open questions

These are merged across the three notes, with duplicates dropped. "D" questions need Daniel. "L" questions are for the
leads and proofs.

### Needing Daniel

- **D1. Pearl-C's noise seed and γ (PoUW Q1).** γ does not hold under (a): a prover forms every row onto a few shared
  targets and does 2–4% of the work (section 4.1). Recommendation: per-row seeds, the `-h3` format (option (b) per row),
  which keeps γ at 0.36949% with no new assumption and keeps the gateway out of decode's path. compute-accounting agrees.
  Owed: the row-seeded `K` twin of `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` (compute-accounting's port) and the
  statement review of (C1) and (C2). Pearl-C4 stays off served accounting until the attack has been run on it.
- **D2. Is W's size public (PoUS Q5)?** PoUS's B shows |W| to within a 2,054-byte block, hence the model's size. PoUW's
  weight-side proving, about one unit per weight row every epoch, shows it too. Recommendation: public for now, with that
  reason. Pad W to a bucket when a deployment needs its size hidden. Inside PoUS's certified family that needs no Lean
  change, but the profile then certifies the padded store.
- **D3. The possession claim (PoUS Q3).** It is a new named assumption, for example `possession/sha-512` under the
  `random-oracle` model: a nonce-bound commitment received by time t determines a hash query on the whole block, made
  after the nonce. That holds only if `commit_fresh` hashes nonce_j ‖ the whole 2,056-byte block and `AnswerOpens`
  recomputes H(block) from those bytes; over nonce_j ‖ H(block) it is the precomputation attack again (memory-accounting).
  With it, the general rule is written down: a guarantee about *when* a value was held needs a nonce-bound
  commitment, and one about *what* was committed needs only binding. Recommendation: yes, entering PoUS's profile beside
  `P2_CLAIMS`. Without it, PoUS is broken by a prover holding 3% of C, and PoUS's guarantee waits on it.
- **D4. Where PoUS's timed verifier runs, what makes it auditor-trusted, and isolation as soundness (PoUS Q1, R3, R8).**
  Recommendation, in four parts:
  - first deployment on an auditor-owned host on the same switch, and a confidential VM once one is qualified;
  - RTT p99.9 measured at or below 354 µs before each audit;
  - a named claim in the profile until then, beside `live-verifier` and `designated-verifier`;
  - isolation enforced by the warden on auditor-trusted terms, never credited to the prover gateway.
- **D5. The salt's source (PoUW Q3).** Recommendation: live coins (epoch coins bound to the registration). Delete the
  beacon and BLS code unless a mining mode that third parties can check is wanted.
- **D6. The audit window and ε (PoUW Q5).** Recommendation: decouple the window from the 15-minute epoch (for example,
  daily), and set ε per deployment from the proving budget. At ε = 0.1% and δ = 2⁻⁴⁰, K = 27,713 full tiles, and L3's law
  multiplies that by N·w_max/W, up to about 2 when decode's half-filled tiles dominate.
- **D7. The live coins as ingress (warden R4).** Recommendation: charge their timing, and exempt their content, which the
  auditor chose independently of the secret. This changes what the K charge counts.
- **D8. The prover gateway as a Lean program (`note:proofs/20261006T0213Z-finding-zk-gateway`).** The options are (a) the
  shadow as a third channel, `pcs`, answered by today's Rust, its honesty a named assumption; or (b) a Lean prover.
  Recommendation: (a) now. A Lean prover over V*'s 2^28 to 2^32 words would be larger than everything else and would sit
  on the session's critical path. Revisit (b) when the assumption is the weakest link.
- **D9. The lottery on served work (PoUW Q2).** The ruling hides tile digests, which seems to settle this.
  Recommendation: confirm that served accounting uses the sampled audit only, and that the lottery stays for a mining mode
  on synthetic inputs, outside `RecursiveZK`'s claim.
- **D10. PoUS's setup: exhaustive or sampled (PoUS Q7)?**
  - Exhaustive keeps ρ = 18/19 and k = 105, and is certified today. It costs about 2.9 GPU-hours of outer proving, 25 GB of
    proofs and 16 hours of Lean verify per GB of W.
  - Sampled at ε = 1% and δ_s = 2^-128 is s = 8,828 blocks, about 24 sessions, 470 MB of proofs and 18 minutes of Lean
    verify, whatever |W| is. It lowers ρ to about 0.938 and raises k to 140.

  Recommendation, with memory-accounting: sampled, once `P2SlackFamilyFreeBlocks` is pinned, and exhaustive until then.

### For the leads and proofs

- **L1. The public-items lists.** All three now exist: PoUW's (`5e71daace`), the warden's (`40968ff4b`) and PoUS's
  (`a5825f376`). Each item is one of the four kinds (section 1) with its reason: structure, an output, the verifier's coins
  and draws, or a hiding commitment. PoUW's list has values of the last three kinds (N, δ, the drawn indices, W's salted
  root), which the corrected rule allows. The service enforces the lists, and Daniel checks each in the morning. Owners:
  each lead, to keep them current.
- **L2. Per-call roots stay private (PoUW R2, restated).** The window root, registered before the draw, keeps C1.
  **Agreed** by compute-accounting.
- **L3. PoUW's per-unit work (R7) under the ruling.** Strata by credit class would show each class's count. Proofs'
  recommendation is a uniform `subset:K′` over the N equal tiles, with K′ = ⌈ln(1/δ) / −ln(1 − ε·W/(N·w_max))⌉:
  - A wrong set holding a share ε of credited work has at least ε·W/w_max tiles, so `subset_miss` and a one-line counting
    step give the bound.
  - The credited work W is claimed at registration and proved by the window statement, and N is public.
  - The cost is the factor N·w_max/W in proving.

  **Agreed** by compute-accounting. If the factor of up to 2 ever matters, a work-weighted draw located in gates through a
  committed prefix-sum tree removes it; not now. The Lean step is proofs'.
- **L4. Protocol-chosen units (PoUW R8) show their count.** **Decided** (compute-accounting): the excluded and voluntary
  rows' rules fold into the window statement, so their count stays hidden.
- **L5. `ncp-v2`'s shapes are in its template names (`NcpLinear_v1{M,K,N,PERM}`).** **Decided** (compute-accounting):
  `ncp-v2` is re-tiled into fixed-shape units like `pc8`'s. Its shapes don't become public items, and it stays off real
  traffic until then.
- **L6. The size rule reads public items only.** **Agreed** (network-accounting): the warden pads to T·r by default, with
  no extra charge; size classes only as a named log₂(#classes) charge per window. PoUW sizes sessions by the drawn
  count. A cheaper statement shape for step 12 to measure against: commit only the T counts per window. A left-packed
  FIFO row t is frames [S_{t−1}, S_t) of the canonical sequence, so the rows' frames are ranges of the served
  commitment's leaves, not a second copy, and the check is expectedRow's counts from per-session closed forms (eligible
  = anchor + δ + ⌊λ/ρ⌋ is arithmetic in λ). That is O(T + sessions), padded to a public session cap, instead of O(T·r)
  leaves. Owner: network-accounting, in step 12.
- **L7. The gateway link's timing and egress (warden R1, PoUS's timed loop, PoUW R13).** **Agreed** (network-accounting),
  with the weight changed: scheduled release is **required for zero knowledge**, not only against a malicious verifier
  gateway, because `RecursiveZK` quantifies over every behavior of the auditor and the auditor's own gateway sees exact
  arrival times whatever the record keeps. The deadline bit protects readers of the record; the fixed schedule, enforced
  by the developer-trusted prover gateway (or a warden grid on that link), protects against the auditor. A message that
  misses its slot is an abort symbol, charged under R5. C-Flock's message sizes already follow from the circuit, and
  PoUS's answers go at a fixed offset. Owners: proofs and network-accounting.
- **L8. PoUW's two-stage default (Q6) and registered row/v2 (Q7, R3).** Proofs takes both (steps 4 and 7).
- **L9. A sequential timed mode, and who reads the outcome (PoUS Q2, Q4; warden R2).** The service grows a sequential timed
  mode on #1227, since the warden's timing work wants the same loop and clock. `StorageProfile` stays PoUS's reading of the
  service's `Exhaustive` fact, and the warden computes its own charge from it. All three are agreed.
- **L10. W's row schema (PoUS Q6, R9; compute-accounting's ask).** Recommendation: section 2.1. W is committed by weight
  row as registered `hm96-sha512/row/v2` values in the stored dtype, with one shared tensor table. PoUW reads aligned rows
  and widens BF16 in gates. PoUS opens the one or two rows a payload touches. memory-accounting put this to Daniel as its
  Q6. Proofs thinks the two leads can settle it on these numbers, and goes to Daniel only if they disagree. Owners:
  compute-accounting and memory-accounting.
- **L11. Proofs' remaining theorems:**
  - public outputs in `RecursiveZK`'s simulator (PoUW R4);
  - malicious-auditor zero knowledge at C-Flock's `--zk` (`gk_simulate_hm96` instantiated);
  - the sequential draw: indices and nonces uniform, independent and hidden until revealed, which `P2SlackFamilyUncond`
    assumes;
  - epoch coins independent of the registered commitment;
  - the joint corollary with network-accounting (warden R5), not tonight.
- **L12. Where the service lives.** Recommendation: inside `verity/protocols/verification/sampled_proofs`, which already
  owns registration, the draw, the audit and the verdict, with the gateways in `backends/flock`. No new package. Owner:
  proofs.
- **L13. Measurements:**
  - the Lean verify time per window, the largest unknown (PoUW R11: today 4,777–5,841 s for one 16-instance `hidden_zk`
    session);
  - the direct/recursive crossover (R12);
  - the commit rate on sm_120 (R1, from served-zk's `rows_bench.py`);
  - one traced 16,448-bit squaring (PoUS);
  - the hidden-read cost per drawn tile;
  - the PoUS round on the node with a Lean prover gateway in it.

## 8. Asks of each lead

**Agreement (8:41 PM PDT):** compute-accounting agrees, with four changes (thread 1791253199.410869,
1791257722.929929): the owed row-seeded theorem (section 4.1 step 10, D1), one row digest before forming (step 4), the
seed derivation kept (section 5), and Pearl-C4 off served accounting. network-accounting agrees, with two changes
(1791257756.221339): L7's weight and L6's cheaper statement shape. memory-accounting agrees, with four changes
(1791257816.713839): keep PoUS's acceptance rules as the difftest oracle (section 5), the on-time bits and drawn hiding
leaves as public items (section 3), the offset from the rejection target (section 4.3 step 7), and `commit_fresh` over
the whole block (step 8, D3; the interface's signature). All ten are applied. **All three leads agree.**

**compute-accounting (PoUW):** answered. Asks 1–3: agree, with the changes applied. Ask 4: L4 and L5 decided (section 7).
Ask 5: served-zk moves onto one-stage's registration, receipt and Lean draw after its 11:00 PM PDT (06:00Z) verdict, and
`hm96_rows.cu`'s rate comes from the 12:00 AM PDT (07:00Z) window as R1's number.
1. Agree to sections 3, 4.1, 4.2 and PoUW's part of section 5, or mark what's wrong.
2. Agree L2 (private per-call roots) and L3 (uniform `subset:K′` scaled by N·w_max/W), or say why not.
3. Agree section 2.1 (W by weight row, BF16 widened in gates), which moves `pc8`'s weight-side digests.
4. Decide L4 (protocol-chosen units) and L5 (`ncp-v2`'s shapes).
5. Run served-zk's step 0 through one-stage's registration, receipt and Lean draw in place of `os.urandom`. Report
   `hm96_rows.cu`'s rate as R1's number.

**memory-accounting (PoUS):** answered. Ask 1: agree, with the changes applied. Ask 2: agreed, W by weight row with P2's
byte stream as the rows in committed tensor order, and the tensor table's well-formedness in `P2Decode`. Ask 3: the
fixed-offset release and an hour's proof deadline agreed. Ask 4: takes step 5 and step 11 (starting with one traced
16,448-bit squaring through `circuit-check`).
1. Agree to sections 3, 4.3 and PoUS's part of section 5, or mark what's wrong.
2. Agree section 2.1: PoUS opens weight rows through the shared tensor table, at an estimated 10–65% more per setup block.
3. Agree the fixed-offset release in the timed loop, and the proof deadline in `outcome`.
4. Take step 5 (the timed mode on #1227) and step 11 (PoUS's proofs, starting with one traced squaring).

**network-accounting (the warden):** answered. Asks 1–2: agree, with the changes applied (L6, L7). Asks 3–4: takes step
2 once `register` exists, and co-owns L11.
1. Agree L7 (deadline bits plus scheduled release) as R1's answer.
2. Agree L6 (padding to T·r, or a named size-class charge).
3. Take step 2, the records into the service's record, as the warden's first step.
4. Co-own the joint corollary (L11) when it is scheduled.

## Checkpoint

- 5 Oct, 8:22 PM PDT (03:22Z): drafted, with the coordinator's 8:15 PM PDT instructions applied: no clear mode, PoUS's
  restated note, public items as structure, and W's row schema as one service choice (section 2.1).
- 5 Oct, 8:26 PM PDT (03:26Z): ready to send. Cited the rulings it rests on: 7:48 PM superseding 2026-10-01's "shapes may
  stay public" (section 1), the one-theorem ruling (section 3), the development shortcut (step 0) and the hidden read's
  accepted cost (step 8).
- 5 Oct, 8:32 PM PDT (03:32Z), proofs coordinator: public items restated in top's four kinds (section 1, `Public.kind`,
  L1), and γ filled in from pouw-gamma's finding (sections 1 and 4.1, D1; the interface's section 8).
- 5 Oct, 8:37 PM PDT (03:37Z), proofs coordinator: compute-accounting's four changes and network-accounting's two
  applied (sections 2, 4.1, 5, 7 and 8); memory-accounting's answer pending.
- 5 Oct, 8:41 PM PDT (03:41Z), proofs coordinator: memory-accounting's four changes applied (sections 1, 3, 4.3, 5,
  7 and 8; the interface's `commit_fresh` signature). Agreed by all three leads.
