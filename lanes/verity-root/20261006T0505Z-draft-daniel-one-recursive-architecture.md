---
id: verity-root/20261006T0505Z-draft-daniel-one-recursive-architecture
campaign: proofs
lane: verity-root
kind: draft
status: for review (Daniel's draft, written with another Claude; leads' feedback in thread 05:05Z)
repo: danielreuter/verity
origin: Daniel, relayed verbatim by top (bc-d6f8b221) on 5 Oct 2026, 10:05 PM PDT
---

Daniel's draft, verbatim, as he sent it. Note the rename: the network warden is now the **network certifier**.

# The proof service: one recursive architecture

Oct 5, 2026 · @Dan Reuter

Draft for review. Uncertainties are marked inline, [Daniel: …] for Daniel's and [Claude: …] for Claude's, and collected at the end. Names are kept to a minimum and will settle as the design does.

## Summary

The proof service lets an auditor check what a developer's AI servers did, under PoUW, PoUS and network accounting. The auditor learns nothing about the weights or data beyond each protocol's stated public outputs.

Three ideas carry it:
- Network certificates tie proofs to the physical system. A network certifier on each server uplink signs what it sees. The developer proves that its committed circuits are consistent with those certificates.
- Recursion carries the privacy. Workers prove everything with zero knowledge off. The firewall turns that into outer proofs that are zero-knowledge, and only outer proofs reach the auditor.
- What crosses is fixed in advance. Outer proofs leave on a public schedule with a fixed shape. A malicious worker or certifier can then steer only failures and coarse public outputs, and both are bounded.

The auditor gets soundness, resting on the certifiers, the challenger and the verifier. The developer gets zero knowledge with bounded leakage, resting on the firewall and on how the network is wired.

## Decisions so far

These are settled; the rest of the document follows from them.

| Decision | What follows |
|---|---|
| One proof service for PoUW, PoUS and network accounting | Protocols describe their checks; the service handles commitments, coins, proving and verifying |
| Every protocol is zero-knowledge | Each protocol lists what it makes public and why. Everything else is hidden |
| Recursion first | Build full recursion and prove it end to end before any other route. Switch only for strong reasons |
| Live coins; a designated verifier is acceptable | Outcomes convince the auditor, not third parties |
| VBridge proves one direction | If V* accepts, the Lean verifier accepts. Completeness is tested, not proved |
| End to end means VBridge is proved | Soundness claims are conditional on VBridge until then |
| Certifiers are not mutually trusted | The auditor trusts them for soundness. The developer doesn't trust them, and their view never reaches the auditor |
| Protocols are independent | Each runs as its own asynchronous stream, not coupled to the others. [Daniel: how they relate in time is unclear.] |
| Assumed for now | Bit-exact replay of served computation; the challenger is available when needed |

## Who does what

The prover is the workers behind a firewall, P = F ∘ W. The auditor runs a challenger online and a verifier offline. Network certifiers sit on the developer's site but answer to the auditor.

| Component | Does | Trusted by | Soundness holds against it | Zero knowledge holds against it |
|---|---|---|---|---|
| Workers W | The developer's AI servers and GPUs. Run the real computation and nearly all proving work | neither | yes | yes, except failures |
| Firewall F | Developer-trusted CPUs, the only path to the auditor. Makes everything that leaves zero-knowledge | developer | yes | no: it is the developer's trusted base |
| Network certifiers N | Auditor devices on server uplinks. Sign network certificates attesting the traffic they see | auditor | no: they are the auditor's trusted base | yes, except failures |
| Challenger C | Auditor service. Issues live coins for outer proofs, committed in advance | auditor | no | yes |
| Verifier V | The auditor's Lean verifier, run offline. Accepts or rejects outer proofs | auditor | no | yes |

The network has to be wired so that two things hold:
- For the developer: workers and certifiers reach the auditor only through the firewall.
- For the auditor: every uplink that matters passes through a certifier.

Two rules follow:
- Certificates never reach the auditor in the clear. They are witness: the prover proves things about them. [Claude: I think this is required. Certificates hold unsalted hashes of traffic, and bits a malicious certifier chooses, so a log the auditor reads would leak.]
- Coins the auditor sees come only from the challenger, which never sees the witness.

## Architecture

Everything runs as streams, and only outer proofs cross to the auditor.

Workers compute and prove continuously, and their traffic passes the certifiers, which sign what they see. Certificates are aggregated on the developer's side and read by the prover as witness. The firewall releases outer proofs on a public schedule and takes the challenger's coins. Each protocol runs this way as its own stream.

[Daniel: where certificates are aggregated, and by whom, is open.] [Claude: the diagram leaves out where inner proofs' coins come from; see Proving.]

## What a protocol states

A protocol states what it commits to, which pieces need checking, the check itself as a public Program, what it makes public, and what it does with each verdict. Everything else is the service's.

Its circuit comes from a pre-committed builder: a public algorithm that expands a small piece of private advice into the full circuit, absorbing nondeterminism such as batching and scheduling. The developer declares how the circuit is partitioned across servers.

[Claude: the codebase has several notions of "unit" (replay units, proof units, spatial units, and possibly others), and I don't know their full scope. Where this document says "piece" or "part", read it loosely.]

What the builder implies, as Claude reads it:
- The advice is fixed before any coin that depends on it. Otherwise the circuit could be shaped around the draw. Sending the advice's hash up a certified uplink timestamps it. [Claude: the coins then have to be certified as arriving later, for example by entering through a certified link.]
- Sampled checks need local expansion. One checked piece and its boundary should be computable from the advice and an index, without building the whole circuit. [Claude: I don't know whether the builder has this property.]
- The advice is network capacity. It is the developer's free choice, so wherever it changes what leaves a server, it can carry up to log2 of the number of admissible advice values. [Claude: "small" should be a stated bound, counted in network accounting's charge.]
- The partition is probably private. It reveals the parallelism layout, so it likely belongs inside the advice. [Claude: open whether any of it can be public.]

## Circuits and network certificates

The key relation is that the developer's committed circuit is consistent with the network certificates the certifiers signed. [Daniel: the exact relation is still to be worked out.]

Claude's first cut: place each part of the declared partition behind one certifier, and take the values that cross between parts, plus external inputs and outputs. The relation has two directions:
- Every crossing value appears in certified traffic, at the position the circuit's framing says.
- Every certified frame is explained, either by crossing values or by declared protocol traffic.

```
∀ w ∈ ∂G  ∃ f ∈ Cert_link(w) :  payload(f)[φ(w)] = val(w)
∀ f ∈ Cert  ∃ c ⊆ ∂G ∪ D :  payload(f) = frame_φ(c)
```

Here ∂G is the set of crossing values, φ the framing the builder outputs, and D the declared protocol traffic. The first line says the network carried the circuit's boundary. The second bounds what else left.

[Daniel: it is unclear whether the logical and physical mappings are identical, given duplication and similar effects.] Claude's guesses at where they differ:
- Collectives. An all-reduce puts partial sums on the wire. If the builder outputs the physical circuit, collectives included, the relation only ever talks about that circuit.
- Retransmissions. The two quantifiers absorb them: a resent chunk appears once and is explained each time. Every copy still counts toward network capacity.
- Traffic inside a node. It never reaches an uplink, so a part must be exactly what sits behind one certifier.
- Framing layer. Certifiers should hash payloads in a canonical framing, not raw packets, so the prover can recompute each hash. [Claude: transport headers are not under the software's control.]
- Encryption. If links are encrypted, certifiers see ciphertext. Either they sit inside the encryption boundary or decryption goes into the relation. [Daniel: encryption through certifiers is defense in depth, not part of the protocol.]

[Claude: on cost, the second direction over frame lengths and timing is cheap and can be checked exhaustively, roughly as network accounting does today. Checking contents means hashing payloads in gates, so it is likely sampled.]

## Proving

Workers prove with zero knowledge off, and the firewall turns the result into a zero-knowledge outer proof.
- Inner proofs. Each check is a C-Flock proof with zero knowledge off, run on the workers. Inner proofs are combined recursively, by proving that V*, the C-Flock verifier written as a circuit, accepts them.
- Outer proofs. The firewall runs a C-Flock proof with zero knowledge on. It shows that V* accepts the combined inner proof, that the certificates' signatures verify, and that the public outputs are as stated. Workers do its heavy arithmetic; the firewall salts, masks, checks and releases.
- VBridge. The Lean proof that if V* accepts, the Lean verifier accepts. It removes trust in V*'s code.

[Daniel: names for these stages, such as aggregation, root proof or wrap, are premature and should fall out over time.] [Claude: how inner proofs are combined (a tree, folding, padding to a fixed shape) is open. The outer proof's shape should not depend on how much work it covers.]

Where inner proofs' coins come from. [Claude: if certifiers only attest, inner proofs need another live coin source that keeps their timing from the auditor. Three options:]
- The challenger, in lockstep. All inner proofs advance round by round together. Each round, the firewall sends one salted root over every proof's message at a fixed time, and the challenger answers with one seed. Coins stay live and certifiers stay pure attestors; the cost is latency. [Claude: my lean.]
- A separate confined coin device on the developer's site, from the auditor, that issues coins and nothing else.
- Fiat–Shamir inside the recursion. No coins needed, but it brings back the hash-inside-recursion heuristic that live coins avoid.

PoUS's timed challenges are the exception: they need a challenger on the path to the server. [Daniel: a certifier could play that role.]

## Why the auditor learns nothing

The auditor sees outer proofs of fixed shape at fixed times, the coins it chose, and each protocol's public outputs. Five mechanisms keep that view simulatable.
- The firewall's contract. Before release, every outbound value is either a commitment under a fresh salt the workers never see; or masked with a fresh pad the workers never see, then checked against every relation the verifier will check; or uniquely fixed by what is already committed. Coin openings are checked against the challenger's commitment. So whatever the workers do, what leaves is an honest prover's output or nothing. [Daniel: this is the firewall's core job: anything sent to the verifier is made zero-knowledge.]
- Certificates stay inside. Certifiers see the witness, so their output only ever enters proofs as witness. A malicious certifier can steer nothing the auditor sees except failures.
- Timing. Outer proofs leave on a public schedule. A message not ready at its time is a failure. [Claude: with streams, what each released proof covers must itself stay hidden or fixed. I haven't worked out how.]
- Failures. A failed inner proof is retried with fresh coins, unseen. Visible failures are rejected verdicts and missed times, and the firewall stops after a set budget of them. [Claude: retries suit inner proofs, whose soundness error is tiny. PoUS's timed audits can't be retried without weakening its certificate.]
- Public outputs. A public output workers can influence, such as credited work, is a channel. It is rounded to a public grid.

Over n released outer proofs, with failure budget b, a malicious worker or certifier can push at most this much through the auditor's view:

```
log2 Σ_{i=0}^{b} C(n, i)  +  Σ_releases Σ_j log2 q_j
```

Here q_j is the number of grid levels of the j-th influenceable public output.

[Claude: if protocols run concurrently against one auditor, the outer proofs' zero knowledge must compose concurrently. Goldreich–Kahan's simulator rewinds, which doesn't compose concurrently in general. The options are to run outer proofs one at a time through the firewall, to have one coin commitment cover a period, or to extract straight-line in the random-oracle model.]

## Guarantees

Two theorems carry the service, one for each party, and each protocol's own guarantee composes with them.

Soundness, for the auditor. Whatever the workers and firewall do, with honest certifiers and challenger, the verifier accepts a false claim with probability at most the outer proof's error, plus the inner proofs' errors times the retry bound, plus binding and signature terms. Its premises:
- VBridge;
- collision resistance of SHA-512;
- unforgeable certificates, and honest certifiers (what they sign, their clocks);
- every uplink that matters is certified;
- knowledge soundness of the outer proof.

Zero knowledge with bounded leakage, for the developer. Whatever the workers, certifiers and auditor do, the auditor's view can be simulated from the public outputs and the pattern of failures. Its premises:
- the firewall runs its verified program;
- workers and certifiers reach the auditor only through the firewall;
- outer proofs follow the public schedule;
- the outer proof is zero-knowledge against a malicious verifier;
- the firewall's salted SHA-512 commitments hide. Salts are fresh random values, so hm96's statistical bound applies.

Completeness is tested, not proved.

The firewall needs its own theorem: whatever the workers do, what leaves is an honest prover's output, cut off at the failures. [Claude: this is new and not yet stated.]

## The protocols

Each protocol runs as its own stream, with its own selection, checks and public outputs. [Daniel: how they relate in time is unclear, and the other agents know these protocols better than this document does.]

**PoUW.** It commits to the weights and to what was served, draws pieces of work in proportion to credited work, and proves the drawn tiles' hidden check (pc8). It publishes the verdict, credited work rounded to a grid, the check's identity and the sampling parameters. Drawn positions stay hidden: each draw maps to its tile in gates. Drawn tiles' interiors come from bit-exact replay.
- [Claude: where Pearl-C's noise seed comes from is still open.]
- [Claude: the per-call records PoUW commits look like part of the builder's advice.]

**PoUS.** It shows the developer holds an encoding of the weights, through timed challenges, and proves its setup. The challenger for the timed part must be on the path to the server. If that challenger receives the answer bytes before the deadline and certifies them, precomputed hashes don't help a cheater, so no separate possession claim is needed. It publishes the verdict, the claimed size and the timing parameters.
- [Daniel: fine that PoUS has no runnable mode yet.]
- [Claude: it needs a lemma for a sampled setup and a guarantee for the sequential draw.]

**Network accounting.** Its records are the network certificates themselves. It proves that certified traffic fits the declared schedule and is explained by the circuits' crossing values, and publishes the verdict, its parameters and the charge.
- [Claude: the charge should include the builder's advice capacity.]

## Status

The recursive proving pieces mostly exist; network certificates and their link to circuits are new.

| Piece | State | Where |
|---|---|---|
| Inner proofs with zero knowledge off, on live coins | exists | backends/flock/live |
| V* over one inner proof | rejects each forgery tested | #1246 |
| Outer proof through a send-checking firewall | works end to end at K = 4096: 8 of 8 accepted, 8 of 8 controls refused | #1270 |
| Outer proof's soundness and honest-verifier zero knowledge | proved | main, zk_session_* |
| Goldreich–Kahan at C-Flock's --zk | not instantiated | — |
| VBridge, one direction | in progress | #1258 and its plan |
| RecursiveSound, RecursiveZK | in progress; to be restated for this design | #1261 |
| Frame recording | exists in network accounting | warden/ |
| Network certificates: signing, aggregation, verification in gates | new | — |
| Consistency between circuits and certificates | new | — |
| Combining inner proofs into a fixed-shape result | new | — |
| Release schedule, failure budget, the firewall's theorem | new | — |

Measured at K = 4096, m = 35:

| Step | Figure | Source |
|---|---|---|
| Inner prove | 0.875 s | #1246 |
| Outer prove, no firewall | 7.90 s | #1246 |
| Outer prove through the firewall | 46.8 s, about 176 CPU-s of firewall work | #1270 |
| Outer proof size | 19.6 MB | #1246 |
| Outer Lean verify | 449 s for ten proofs, not like for like | #1246 |

## Uncertainties

Everything marked inline, collected in one place.

Daniel's:
- How circuits relate to network certificates. Probably a declared spatial partition whose crossing values appear in certified traffic; whether the logical and physical mappings coincide, given duplication, is unclear.
- Where network certificates are aggregated, and by whom.
- How the protocols relate to each other in time. They probably run separately; the other agents may know better.
- Names for the recursion's stages. They should fall out over time.
- Bit-exact replay is assumed for now and may be relaxed later.
- The challenger's availability is assumed for now.
- Whether a certifier serves as PoUS's timed challenger.

Claude's:
- The full scope of the codebase's unit notions (replay, proof, spatial units and others).
- Whether certificates can ever reach the auditor. I think they must not.
- Where inner proofs' coins come from. I lean toward the challenger, in lockstep.
- How the advice gets timestamped before the coins that depend on it.
- Whether the circuit builder expands locally, and how small the advice is.
- Whether any of the partition can be public.
- How streamed outer proofs keep their coverage hidden and their shape fixed.
- Zero knowledge when several protocols run against one auditor at once.
- The layer at which certifiers hash frames, and how encryption interacts with it.
- Which signature scheme certificates use, and its cost in gates.
- Where the firewall's 176 CPU-s per outer proof goes.
- The grids for public outputs such as credited work.
