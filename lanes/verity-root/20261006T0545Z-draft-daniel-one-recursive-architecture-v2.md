---
id: verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2
campaign: proof-service
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: Daniel, 5 Oct 10:45 PM PDT, in chat to top, revised after the leads' feedback of 10:05–10:27 PM PDT
---

Daniel's revised draft, verbatim, with his instruction (10:45 PM PDT): "i want people to implement this unless they have
like a very strong reason not to and then they should just like have a report for me in the morning … i want to have just
like a completely functional repository in the new shape tomorrow morning when I wake up. At a minimum! And also progress
on the other fronts." It supersedes `note:verity-root/20261006T0505Z-draft-daniel-one-recursive-architecture`. The
leads' feedback on v1 is the coordinator store's `docs/feedback-one-recursive-architecture.md`. The implementation plan
is `note:verity-root/20261006T0550Z-report-proof-service-implementation`.

---

# The proof service: one recursive architecture

Oct 5, 2026 · @Dan Reuter

Draft for review, revised after the leads' feedback of 5 Oct, 10:05–10:20 PM PDT. Uncertainties are marked inline,
[Daniel: …] for Daniel's and [Claude: …] for Claude's, and collected at the end. Names are kept to a minimum.

## Summary

The proof service lets an auditor check what a developer's AI servers did, under PoUW, PoUS and network accounting. The
auditor learns nothing about the weights or data beyond each protocol's stated public outputs.

- Certifiers attest to what crosses the network. A network certifier on each node's uplink signs the contents of the
  traffic it carries and scrubs its timing. The developer proves that its committed circuits are consistent with those
  certificates. Attesting contents is the primary job; scrubbing timing closes the channel that contents can't show.
- Recursion carries the privacy. Workers prove with zero knowledge off. The firewall turns that into outer proofs that
  are zero-knowledge, and only outer proofs reach the auditor.
- Each party owns one timing scrubber. The certifiers scrub what leaves each node, which backs the auditor's network
  bound. The firewall releases outer proofs on a fixed schedule, which backs the developer's zero knowledge.

The auditor's soundness rests on the certifiers, the memory challenger, the challenger and the verifier. The developer's
zero knowledge, with bounded leakage, rests on the firewall and on how the network is wired.

## Decisions

These are settled; the rest of the document follows from them.

| Decision | What follows |
|---|---|
| One proof service for PoUW, PoUS and network accounting | Protocols describe their checks; the service handles commitments, coins, proving and verifying |
| Every protocol is zero-knowledge | Each protocol lists what it makes public and why. Everything else is hidden |
| Recursion first | Build full recursion and prove it end to end before any other route. Switch only for strong reasons |
| Live coins; a designated verifier is acceptable | Outcomes convince the auditor, not third parties. Fiat–Shamir is out |
| VBridge proves one direction | If V* accepts, the Lean verifier accepts. Completeness is tested, not proved |
| End to end means VBridge is proved | Soundness claims are conditional on VBridge until then |
| Network certifiers attest contents and scrub timing | Auditor-trusted devices, untrusted by the developer. Their certificates never reach the auditor in the clear |
| A memory challenger, separate from the certifier, runs PoUS's timed rounds | It sits next to the certifier, inside the node's isolation boundary |
| Partitions are private; their properties are public | The proof shows the private partitions satisfy public predicates |
| One hash: SHA-512 | hm96 rows in frame-v3-sha512 trees for every commitment; hash-based signatures over SHA-512 for certificates |
| Protocols are separate streams over shared commitments | One commitment to the weights, by weight row, shared by PoUW and PoUS. Network accounting's frames are leaves of the served commitment |
| Outer proofs run one at a time through the firewall, across all protocols | The shape soundness already uses (Multi.seqC); it avoids concurrent zero knowledge between outer proofs |
| PoUS publishes the audit's verdict, not per-round bits | Per-round on-time bits stay in the memory challenger's signed record, where a server can't steer what the auditor sees |

## Simplifying assumptions for now

These keep the first end-to-end version small; each can be relaxed later.

- No retries. Any failed proof is a visible failure. Padded rounds would allow retries later. A retry may never redraw.
- Bit-exact replay under a pinned engine environment, which is part of what is committed. Circuits checks it per model row.
- The challenger is available whenever the developer needs coins.
- Operational errors are assumed away, beyond counting each visible failure.

## Names

Renames for the repo. "Gateway" is retired.

| Was | Now | Note |
|---|---|---|
| warden | network certifier | A change of role, not just of name: developer-run software becomes an auditor-trusted device |
| the warden's records | network certificates | |
| PoUS's timed verifier | memory challenger | |
| prover gateway | firewall | The prover is the workers behind it: P = F ∘ W |
| verifier gateway | challenger | |
| batch verifier | verifier | The auditor's Lean verifier of record |
| GPU workers | workers | |

Code terms stay as the README Glossary has them: proof unit, replay unit, isolation unit.

## Who does what

The prover is the workers behind a firewall. The auditor runs a challenger online and a verifier offline, and places two
kinds of device inside the developer's site: network certifiers and memory challengers.

| Component | Does | Trusted by | Soundness holds against it | Zero knowledge holds against it |
|---|---|---|---|---|
| Workers | The developer's AI servers and GPUs. Run the real computation and nearly all proving work | neither | yes | yes, except failures |
| Firewall | The only path to the auditor. Makes everything that leaves zero-knowledge, on a fixed schedule | developer | yes | no: it is the developer's trusted base |
| Network certifiers | One on each node's uplink. Attest the contents of traffic and scrub its timing | auditor | no: they are the auditor's trusted base | yes, except failures |
| Memory challenger | Next to the certifier. Runs PoUS's timed rounds and signs each one | auditor | no | yes, except failures |
| Challenger | Auditor service. Issues live coins, committed in advance | auditor | no | yes |
| Verifier | The auditor's Lean verifier, run offline | auditor | no | yes |

The network must be wired so that two things hold:

- For the developer: workers, certifiers and memory challengers reach the auditor only through the firewall.
- For the auditor: every node uplink passes through a certifier. This is also PoUS's isolation premise: a server can't
  fetch help from off the node inside a round.

Two rules follow:

- Certificates and signed rounds never reach the auditor in the clear. They hold unsalted hashes and bits a malicious
  device chooses, so they are witness: the prover proves things about them.
- Coins the auditor sees come only from the challenger, which never sees the witness.

Placement, from infra:

- The nodes are KVM guests, so the firewall needs at least its own VM, with dedicated cores to hit fixed times. Nothing is
  placed that way today.
- A node's GPUs talk over PCIe and host memory, out of a certifier's sight. So a part behind one certifier is at least a
  whole node or VM.
- bench/placement already refuses pairs that share machine_id or boot_id, sit on a host bridge, or have a TCP round trip
  under 0.1 ms. It is the separation check for the firewall, certifiers and challenger.

[Claude: what makes a certifier or memory challenger auditor-trusted on a developer's host (auditor hardware, a
confidential VM) is open.]

## Architecture

Only outer proofs cross to the auditor; everything the devices sign stays on the developer's site.

Each node's workers sit inside an isolation boundary, with the certifier and memory challenger on its uplink. What those
devices sign is aggregated on the developer's side and read by the prover as witness. The firewall exchanges commitments
and coins with the challenger every round and releases outer proofs on its schedule. Each protocol runs this way as its
own stream.

[Daniel: where certificates are aggregated, and by whom, is open.]

## What a protocol states

A protocol states what it commits to, which pieces need checking, the check as a public Program, what it makes public,
and what it does with each verdict. Everything else is the service's.

The circuit is public; the schedule is private. The Program is fixed per model, engine environment and tensor-parallel
layout. The developer's free choice is the per-step schedule: batch composition and lengths. That schedule is the
private advice from which the circuit is built.

- The advice is registered, hidden in one root, before any coin that depends on it. Otherwise the circuit could be
  shaped around the draw.
- The advice is network capacity, and its charge is already proved: the A_c term in EncardAccSeqsLeSync. What's missing
  is a declared bound on the number of admissible schedules. The online clock sync is advice too.
- [Claude: the schedule isn't locally expandable today, because Match folds the whole dispatch log. PoUW's units are,
  through hidden Merkle reads.]

Partitions are private; their properties are public. There are two:

- The fine partition into proof units, for sampling. The committed computation is divided into the fewest steps whose
  outputs are each at most 16 bits. Matrix multiplications split into dot products, rounded to BF16 after accumulation.
  Other parts split into short chains of scalar operations, like nonlinearities, and high fan-in graphs, like
  normalization layers and samplers.
- The coarse partition into isolation units, for the network relation: which node runs which part, behind which
  certifier. A part is at least a whole node or VM.

The proof shows each private partition satisfies its public predicates, such as "every proof unit's outputs are at most
16 bits". Today the partition is public and the verifier evaluates it, so this changes verity/partition/v1 and the Lean
partition check. [Claude: which predicates beyond output size are needed is open; the agents should propose them.]

## Circuits and network certificates

The central relation is that the developer's committed circuit is consistent with the network certificates. Take the
values that cross between isolation units, plus external inputs and outputs. Two directions:

- Every crossing value appears in certified traffic, at the position the circuit's framing says.
- Every certified frame is explained, either by crossing values or by declared protocol traffic.

$$
\forall\, w \in \partial G \;\; \exists\, f \in \mathrm{Cert}_{\mathrm{link}(w)} :\; \mathrm{payload}(f)[\varphi(w)] = \mathrm{val}(w)
$$
$$
\forall\, f \in \mathrm{Cert} \;\; \exists\, c \subseteq \partial G \cup D :\; \mathrm{payload}(f) = \mathrm{frame}_\varphi(c)
$$

Here ∂G is the set of crossing values, φ the circuit's framing, and D the declared protocol traffic. The first line says
the network carried the circuit's boundary; the second bounds what else left.

Settled, from network-accounting and circuits:

- Framing. The certifier is a proxy that terminates TCP. It frames every stream into canonical B-byte frames (kind,
  stream, length, then zero fill) and hashes only those. Retransmissions sit below the framing and carry nothing.
- Encryption terminates at or before the certifier.
- Collectives. Tensor-parallel Builds already output the physical circuit, with collectives as Definitions, so the
  relation talks about that circuit.
- Signatures. One per link-window (60 s), not per frame.
- Cost. The schedule check is exhaustive, never sampled, and runs on the per-bucket counts: O(T + sessions) per window.
  Content consistency is the sampled part.
- Coins entering a certified link are ingress. Their timing sits on the ingress grid; the recommendation is to charge
  their timing and exempt their content (D7).

[Daniel: whether the logical and physical mappings fully coincide, given duplication, still needs thought.]

## Proving

Workers prove with zero knowledge off, and the firewall turns the result into a zero-knowledge outer proof.

- Inner proofs. Each check is a C-Flock proof with zero knowledge off, run on the workers. Its coins come from the
  challenger, live, every round: the firewall sends salted SHA-512 commitments to every inner message and tree top, then
  relays the coins (#1270, #1284).
- Combining. Inner proofs are combined by proving that V*, the C-Flock verifier written as a circuit, accepts them.
- Outer proofs. The firewall runs a C-Flock proof with zero knowledge on. It shows that V* accepts the combined inner
  proofs, that the certificates' signatures verify, and that the public outputs are as stated. Workers do its heavy
  arithmetic; the firewall salts, masks, checks and releases it on schedule. Outer proofs run one at a time.
- VBridge. The Lean proof that if V* accepts, the Lean verifier accepts. It removes trust in V*'s code.

[Daniel: names for these stages are premature and should fall out over time.] [Claude, from proofs: a fixed outer shape
needs new work. Today V* is 10 statements per inner session at K = 4096, so it needs a combining step or padding to a
cap.]

## Why the auditor learns nothing

The auditor sees outer proofs of fixed shape at fixed times, the coins it chose, and each protocol's public outputs. Five
mechanisms keep that view simulatable.

- Device output stays inside. Certifiers and memory challengers see the witness, so what they sign only ever enters
  proofs as witness. A malicious device can steer nothing the auditor sees except failures.
- The firewall's contract. Before release, every outbound value is one of three things. It is a commitment under a fresh
  salt the workers never see. Or it is masked with a fresh pad the workers never see, then checked against every relation
  the verifier will check. Or it is uniquely fixed by what is already committed. Coin openings are checked against the
  challenger's commitment. So whatever the workers do, what leaves is an honest prover's output or nothing. [Daniel: this
  is the firewall's core job.]
- Timing. The firewall releases outer proofs on a fixed schedule, on dedicated cores. A message not ready at its time is a
  failure.
- Failures. With no retries, each failure is one visible symbol: a rejected verdict or a missed time. The firewall stops
  after a set budget of them.
- Public outputs. An output workers can influence, such as credited work, is rounded to a public grid. For PoUW the grid
  covers the tile count N, padded to a public bucket with zero filler tiles.

Over n released outer proofs, with failure budget b, a malicious worker or device can push at most this much through the
auditor's view:

$$
\log_2 \sum_{i=0}^{b} \binom{n}{i} \;+\; \sum_{\text{releases}} \sum_{j} \log_2 q_j
$$

Here q_j is the number of grid levels of the j-th influenceable public output.

[Claude, from proofs: #1270's inner path currently lets six prover choices reach the challenger's record, restated at
11.18 bits per stop; fixes are in progress. Concurrent zero knowledge is open even within one outer proof, since V* is
several sessions in a row and nothing yet composes their simulators.]

## Guarantees

Two theorems carry the service, one for each party, and each protocol's own guarantee composes with them. RecursiveSound
and RecursiveZK (#1261) are their current Lean forms, proved over VBridge.

Soundness, for the auditor. Whatever the workers and firewall do, the verifier accepts a false claim with probability at
most the outer proof's error, plus the inner proofs' error, plus binding and signature terms. The outer proof's knowledge
soundness is a theorem (zk_session_*), not a premise. The premises are:

- VBridge;
- cr/sha-512, and ecr/sha-512 for link finders;
- InnerSound: C-Flock's table, 2^−205 at 22 ≤ m ≤ 33;
- live-verifier: the record Lean reads is the challenger's;
- A3, the verifier's OS bytes;
- honest certifiers and memory challengers: what they sign, their clocks, their coin trees;
- every node uplink is certified.

[Claude, from top: main's J-table forms of the session theorems are vacuous for J ≥ 2 until #1264 lands.]

Zero knowledge with bounded leakage, for the developer. Whatever the workers, the devices and the auditor do, the
auditor's view can be simulated from the public outputs and the pattern of failures. The premises are:

- the firewall runs its program. Lean fixes it today as gatewayLeaf: a fresh salt per message, nothing else sent. Today's
  Rust shadow opening runs under D8's named zero-knowledge-only assumption;
- workers and devices reach the auditor only through the firewall;
- outer proofs follow the fixed schedule;
- hash-derived-key (Daniel, 2 Oct), taken at n_h · 2^−193. Hiding is not statistical at the pinned key;
- the outer proof is zero-knowledge against a malicious verifier. Goldreich–Kahan isn't yet instantiated at C-Flock's
  session.

Completeness is tested, not proved.

[Claude, from proofs: the firewall's theorem is half there. The mask-then-check branch #1270 runs, and "cut off at
failures", aren't stated in Lean. The soundness model's plain SHA-512 commitments aren't yet formally linked to
gatewayLeaf.]

## The protocols

Each protocol runs as its own stream, over commitments it shares with the others. [Daniel: beyond the shared commitments,
how they relate in time is unclear; the leads know these protocols better than this document does.]

### PoUW

PoUW commits to the weights and to what was served, draws tiles, and proves the drawn tiles' hidden check (pc8). Settled:

- The draw is uniform subset:K′ over the N equal tiles, with K′ scaled by N·w_max/W (L3). Weighting by credit class would
  reveal each class's count. The challenger's coins fix the draw once, after the window root is registered.
- Per-call records are advice: unit records, shapes and batch per step. They are hidden in one window root registered
  before the draw (L2). A small window statement proves the work sum and the map from index to tile, with excluded and
  voluntary rows folded in (L4).
- Noise seeds are per row (-h3, D1). Seeding from the coins alone breaks γ. Under the one-hash decision, the seed keys on
  each row's SHA-512 digest rather than a BLAKE3 leaf.
- Local expansion. A drawn index maps to one tile's rows by hidden Merkle reads. Its interior is regenerated after the
  draw by replay.
- Cost. Committing hm96-sha512 rows once after each decode step costs 10.9% of served time at batch 32. In the call path
  it costs 5.2×, so -h2 leaves the served path. Prefill isn't committed yet; the projection is +28–34%.
- Public outputs: the verdict, credited work as N padded to a public bucket, the check's identity, the sampling
  parameters and the drawn indices, and the weights' salted root.

### PoUS

PoUS shows the developer holds an encoding of the weights, through timed rounds and a proved setup. Its timed audit
already runs end to end in the clear: 20 of 20 honest runs accepted and every control rejected. The zero-knowledge part
is missing.

- The memory challenger reveals each index from a coin tree committed in advance. It receives the whole 2,056-byte answer,
  hashes those bytes itself, and signs the index, send time, receipt time and hash, as witness. This removes the
  possession claim (D3) and is the auditor-trusted on-node verifier (D4).
- Timing. The window is 500 + 354 µs. On-node round trips take 10–22 µs, the Lean-owned loop 141 µs at p99.9 (#1227),
  and SHA-512 of a block about 12 µs. The memory challenger needs its own microsecond timing; the warden as built ticks in
  100 ms buckets.
- The sampled setup is P2SlackFamilyFreeBlocks: 8,828 blocks at ε = 1% and 2^−128, in 24 recursion sessions, with ρ
  moving from 18/19 to about 0.938 and k from 105 to 140.
- The sequential draw's guarantee (L11) becomes a property of the memory challenger's committed coin tree.
- Public outputs: the verdict; the salted roots of the weights and the encoding; the salt; the setup draw and its profile;
  and the coin-tree openings after the session. Per-round bits stay private.

### Network accounting

Its records are the network certificates themselves.

- The bound. The certifier releases egress on a constant-rate, left-packed grid and fails closed, as the warden does
  today (130 of 130 live hours accepted). The proved charge is log₂ of the number of allowed syncs per window: 7 bits at
  16 × 8 (EncardDecodableLeConstantRate).
- The advice charge. The schedule's capacity is the A_c term in EncardAccSeqsLeSync; it needs a declared bound.
- Selection is all link-windows. The schedule check is exhaustive; content consistency is sampled.
- Public outputs: the verdict per link-window (its kind hidden), the deadline bit, the parameters and the charge.

## Status

The recursive proving pieces mostly exist; the certifier's new role, private partitions and the consistency relation are
new.

| Piece | State | Where |
|---|---|---|
| Inner proofs with zero knowledge off, coins from the challenger each round | exists | #1270, #1284 |
| VBridge, one direction | 5 of 9 pieces proved. Blocked on V*'s staging registering coef (#1261, gap 3) and a Lean tag for flock-leaf/sha512-unsalted (#1284) | #1258, #1271–#1274, #1283 |
| RecursiveSound, RecursiveZK | proved over VBridge, as V* sessions in a row; red team running | #1261 |
| Outer proof through the firewall | no-grant at c00b85b0c: the outer path conforms, the inner path lets six prover choices through; fixes in progress | #1270 |
| Served request's commitment opened by the hidden-tile proof | Rust and Lean accept; every control rejects | #1282 |
| PoUS timed audit in the clear | end to end, 20 of 20 honest accepted | r20261006-025304-16fa |
| Goldreich–Kahan at C-Flock's session | not instantiated | — |
| Certifier: certificates, scrubbing, signatures checked in-circuit | warden's proxy and grid exist; certificates and signatures new | warden/ |
| Memory challenger | timed loop exists; signed rounds new | #1227 |
| Private partitions with public predicates | new; changes verity/partition/v1 | — |
| Consistency between circuits and certificates | new | — |
| Fixed outer shape; release schedule; failure budget | new | — |

Measured at K = 4096 on rec-step3's format:

| Step | Figure | Source |
|---|---|---|
| Outer prove | 8.16 s | #1284 |
| Outer Lean verify | 437.8 s | #1284 |
| Outer prove through the firewall | 46.8 s, about 176 CPU-s of firewall work (step 2's format) | #1270 |

## Uncertainties

Everything marked inline, collected in one place.

Daniel's:

- Where network certificates and signed rounds are aggregated, and by whom.
- How the protocols relate in time, beyond their shared commitments.
- Names for the recursion's stages; they should fall out over time.
- Whether the logical and physical mappings fully coincide, given duplication.

Claude's:

- What makes a certifier or memory challenger auditor-trusted on a developer's host, given the nodes are KVM guests.
- How to give outer proofs a fixed shape: a combining step, or padding to a cap.
- Concurrent zero knowledge within one outer proof, across V*'s sessions.
- A declared bound on the schedule's size, and whether the schedule can be expanded locally.
- Which public predicates the partitions need beyond output size.
- Whether PoUS's honest latency tail is low enough with no retries. One honest answer reached 515 µs against a 530 µs
  limit; a sweep is measuring it.
- What moving -h3 from BLAKE3 to SHA-512 costs on the GPU.
- The grids for public outputs beyond PoUW's N.
- Which hash-based signature scheme certificates use, and its cost in-circuit per link-window.
- Where the firewall's 176 CPU-s per outer proof goes after #1270's fixes.
