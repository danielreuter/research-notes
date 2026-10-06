---
id: network-accounting/20261006T0633Z-draft-circuit-certificate-consistency
campaign: proof-service
lane: network-accounting
kind: draft
status: open
repo: danielreuter/verity
origin: "worker of the @network-accounting lead (bc-ecea50f6), item N3 of note:verity-root/20261006T0550Z-report-proof-service-implementation, with @circuits (note:circuits/20261006T0615Z-draft-private-partitions); branch cursor/network-certifier-schedule-bound-cfc7"
---

# The consistency relation between the committed circuit and the network certificates (N3)

This specifies the relation of note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2 ("Circuits
and network certificates") as a verity Program, in both directions. It ends with a first check on real network
certificates and a list of what the tensor-parallel (TP) check still needs.

- **Direction 1.** Every crossing value appears in certified traffic, at the position the framing φ gives it.
- **Direction 2.** Every certified frame is explained, by crossing values or by declared protocol traffic D.

The schedule half is exhaustive. The content half is sampled; §5 gives its law, and also a layout that makes direction 2
exhaustive too, leaving only the units' integrity to sampling.

New terms: the warden is the *network certifier*, and its records are *network certificates*. Paths stay as they are
until the rename move lands (note:network-accounting/20261006T0625Z-draft-certifier-rename-map).

## 1. The objects

- **C and its placement.** C is the committed circuit: a program digest, the partition object `verity/partition/v1`,
  and the values tree, which is serving's commitment to every committed value. The placement P_iu maps each gate to an
  isolation unit (IU), and each IU is a node behind exactly one certifier (circuits' X2).
- **∂G, per edge.** An element of ∂G is an edge e = (g, a → b): the value g is computed in IU a and read in IU b ≠ a.
  C's external inputs are edges from `outside`, and its outputs are edges to `outside`. A value read by two other IUs is
  two edges. Refinement (proof units refine P_iu) puts every crossing value in the committed set, so val(e) is read
  from the values tree at g's position.
- **link(e).** The certified link between a's and b's certifiers, taken from the registered topology. Ingress and
  egress are the links to and from `outside`.
- **The certificate of (link ℓ, window w).** The signed record over the left-packed grid (W4, W5):
  - the status;
  - (T, r, B, τ_b);
  - the per-bucket counts n_t, which the timing channel is made of;
  - the real frames f_{t,0..n_t−1}.

  One signature per link-window (S1). N1 moves the digest to SHA-512 and keeps it as witness. N1's leaf format isn't on
  origin, so it is the parameter `Leaf` here (§4).

## 2. The framing φ

φ maps each edge to bytes in one stream of its link, and cuts each stream into canonical frames.

- **A canonical frame** is B bytes: `HEADER = >BII` (kind u8, stream u32, length u32), then the payload, then zero fill.
  The kinds are DATA = 1 and LAST = 2; PAD = 0 is padding, and padding is elided from the record.
  - The payload holds at most B − 9 bytes.
  - The fill is all zero.
  - Every real slot is one canonical frame.
  - Retransmissions sit below the framing and carry nothing.
- **Streams.** φ assigns each edge a stream s(e), which is one session on its link, and a byte range [o(e), o(e) +
  |val(e)|) in that stream's byte sequence. The sequence is the concatenation, in canonical gate order, of the edge
  encodings and the D items φ interleaves with them.
- **Cutting a stream into frames.** The rule is per link, part of φ, and registered:
  - *packed*: full DATA frames of B − 9 bytes, then one LAST frame. This is what the active certifier does on ingress
    today (requests: 1,792 full DATA frames and 19,580 LAST frames over the run below).
  - *one frame per event*: each egress event is its own DATA frame. This is today's egress (715,340 frames, each exactly
    one event).

  With either rule, the frame boundaries are a function of the stream's bytes and the event boundaries alone, so a frame
  is frame_φ(c) for a determined set c ⊆ ∂G ∪ D.
- **φ is a bijection.** It maps (link-window, real slot) onto the frames of frame_φ(∂G ∪ D), in the order the schedule
  releases them.
  - It is injective: a duplicate frame is a violation unless it is a distinct edge (§7).
  - It is surjective onto real slots: a frame that no edge or D item accounts for is a violation.
  - The order inside a stream is φ's. The interleaving of streams within a bucket is the certifier's FIFO, which the
    schedule determines.

## 3. What D contains

D is the declared traffic that isn't a crossing value. Every item is a function of public or registered data, so it
adds no content charge.

- **Coins (D7).** These are the challenger's coin frames on the coin link, an ingress link.
  - Each coin frame opens against the coin root, which is committed before the run.
  - Their timing is charged on the ingress grid at (τ_in, r_coin); their content is exempt. The why is in
    `verity/protocols/accounting/communication/certifier/PROTOCOL.md`, "The coins (D7)".
  - A frame on the coin link that doesn't open against the coin root is unexplained.
- **Status.** The status is one untimed symbol per link-window (W5), bound by the record. It isn't a frame. It enters the
  relation only as the acceptance hypothesis `StatusComplete`: every link of ∂X is complete in every audited window.
- **The control protocol.** These are the bytes around the values: the HTTP request line and headers, the response head,
  SSE `data:` framing, JSON keys and punctuation, the `[DONE]` event, and the shim's `id: <position>` line. D fixes them
  with a grammar, and the grammar's id is registered. Each field is classed as one of three things:
  - *declared*: a fixed string, or a function of public data;
  - *advice*: a function of registered advice. The `id:` line is the frame's logical position, already counted by the
    schedule.
  - *crossing*: an encoding of crossing values.

  Anything else is unexplained.
- **The run's control protocol isn't canonical yet.** The first check (§8) finds two unexplained fields in vLLM's
  chunks, and both are developer-choosable bits:
  - a random completion id, `"id":"cmpl-<16 hex>"`, which is 64 bits per request;
  - a wall-clock `"created"`.

  At 944 requests per busy link-window, the ids alone are about 60,000 bits per link-window. That is about 8,600× the
  sync's 7 bits. The chunking is not canonical either: up to 4 tokens per chunk, depending on when the server flushes.
  D therefore needs all of the following:
  - The id derived from the request's position (or dropped).
  - `created` dropped, or set to the anchor's bucket.
  - One event per token, carrying token ids or the detokenizer's per-token text, so that the event boundaries are a
    function of the values.

## 4. Opening a frame against the certificate

`Leaf` is the parameter until N1 lands. The relation needs three things from it:

1. A leaf per real frame, addressed by its slot (t, j). This lets an opening cost log₂ n hashes, not a row.
   - Today's row digest, `u32be(n) ‖ f_0 ‖ … ‖ f_{n−1}`, would make one opening hash a whole row: up to 1,686 × 4 KiB =
     6.9 MB, about 54,000 SHA-512 compressions.
2. The counts n_t bound separately, so the exhaustive schedule check reads them without any frame.
3. A domain separating links, windows and parameters. This is the record header's canonical JSON, as today.

The proposal is a frame-v3-sha512 tree per link-window.
- Its domain is (link, window, T, r, B, τ_b, status).
- Each leaf is the row leaf of one frame's B bytes at position (t, j), with a role of its own.
- A second, small tree holds the counts n_t.
- The record root is H(counts root ‖ frames root), and S1 signs that root.

**The opening of a sampled frame** (ℓ, w, t, j):
- the frame's B bytes and its Merkle path to the frames root;
- the counts path, which shows j < n_t;
- φ⁻¹ of the slot: its stream s, the frame's index in s, and the list of (edge e, byte range) or D items inside it;
- for each edge, the opening of val(e) in the values tree;
- for each coin item, the opening in the coin root.

The check is `frame == frame_φ(c)`, byte for byte, including the header and the zero fill.

The cost per opening:
- about 33 SHA-512 compressions for the frame (4,096 bytes is 32 blocks, plus padding);
- 16 for the path at n ≈ 35,000;
- the values tree's openings for the edges.

## 5. Which half is exhaustive and which is sampled

**The schedule check is exhaustive.** It is never sampled, and runs at O(T + sessions) per link-window.
- For each link-window, recompute the expected row counts from three inputs:
  - the anchors, which are the ingress certificate's release buckets of the requests;
  - the declared schedule profile and sync, from the PROTOCOL.md declaration ("The declaration": registered capacity
    profiles on a step clock, under X3's hidden schedule root);
  - each session's frame count under φ, which is a function of the values' sizes.
- Compare these counts to the certificate's n_t, through the counts root.
- This is Lean's `constantRate` with the declared advice set, so the timing charge is
  `EncardAccSeqsLeConstantRate`'s.

**Content: the baseline is a sampled frame law.**
- The verifier draws a uniform K-subset of each link-window's real frames. The draw uses `verity.primitives.randomness`
  (`derive(source, "verity/network-certifier/content/v0", {link, window, root})`, then `subset(K, n)`).
- The source is the verifier's own randomness, drawn after registration fixes the certificate roots, the values root
  and φ. Like the one-stage audit, it is sent in the clear.
- m unexplained frames escape with probability C(n − m, K)/C(n, K).
- A wrong frame can carry up to 8(B − 9) = 32,696 bits. At δ = 2⁻⁴⁰ and n = 35,000 (a busy egress link-window today),
  the bits that escape detection are:

  | K per link-window | wrong frames that escape with probability > δ | bits |
  |---|---|---|
  | 1,024 | 922 | 30.1 Mbit |
  | 8,192 | 104 | 3.4 Mbit |
  | 32,768 | 11 | 0.36 Mbit |
  | n (exhaustive) | 0 | 0 |

  So sampling frames bounds an exfiltration charge only at the Mbit scale, against the timing charge's 7 to 10 bits per
  window.

**Recommended: make direction 2 exhaustive by layout.** Take `Leaf` to be the values tree's own leaf format for crossing
values, under φ's positions. Then serving's commitment to the framed boundary, frame_φ(∂G ∪ D), and the certificate's
frames root are the same tree, and both directions reduce to the equality

  root_frames(ℓ, w) = Root_φ(values root, D, ℓ, w),

one comparison per link-window.
- The developer knows every slot in advance, because the schedule determines the release given the registered advice.
  So the developer can build the identical tree.
- What remains sampled is whether the committed boundary values are what C computes. That is the integrity profile
  (`verity.proofs.profile`), under the one-stage or two-stage law, with wrong units weighted by their output bits, as
  sampled proofs already do for exfiltration.
- On egress links, the outputs go outside, so register every unit that writes an egress edge as its own class at
  p = 1 (`TwoStageLaw`, `k = None`). These are the sampler and detokenizer rows, small next to the model.
- On interior links, content is an integrity question, sampled at the profile's law.

Under this layout the content charge on egress is 0 bits, and the relation's sampled part is the existing profile.

## 6. As a verity Program

The Program is `verity/network/consistency/v0`, one per audit.

**Public inputs**, all registered before any coin:
- the program digest and the partition object;
- P_iu and the topology (link(e) for each edge), with the placement table row per root Call;
- φ: B, each link's cutting rule, the stream-assignment rule, the encodings, and D's grammar id;
- Σ_sync, the capacity-profile list P_cap (or its root and N), and X3's schedule root;
- the coin roots;
- per link-window: the record root, the signature, (T, r, B, τ_b) and the status;
- the draw, under the baseline law only.

**Advice** (private witness):
- per link-window, the counts n_t and the counts-tree paths;
- the schedule advice: the profile index i < N and the sync per window, opened under the schedule root;
- the anchors, from the ingress certificates;
- under the baseline, per drawn frame: its bytes, its frames path, φ⁻¹ of its slot, and the openings of its edges in the
  values tree and of its coin items in the coin roots. Under the recommended layout, instead: the frames tree's
  internal nodes, which are the values tree's boundary subtree.

**Outputs:**
- the accept bit;
- the declared charge, which is fixed by the public sets (log₂ N once or per window, and log₂ #Σ_sync per window), so it
  reveals nothing about which profile or sync was chosen.

**The Program's parts:**
- the schedule check (exhaustive, §5);
- the content check (sampled frames under the baseline, the root equality under the layout);
- the signature verification per link-window (S1's Boolean Definition on the SHA-512 gadget), or proved outside and
  linked by the record root.

Every SHA-512 comes from the one gadget, and every opening is a frame-v3-sha512 path.

## 7. Do the logical and physical mappings coincide under duplication? (Daniel's open question)

They coincide when ∂G is per edge and φ is a bijection onto real slots. They fail in three cases, each with its own fix.

- **One value, two receivers.** A broadcast or an all-gather to several ranks is several edges, so it is several
  frames, each explained. This is the per-edge ∂G above. It needs P_iu's edges, not values.
- **One value sent twice to one receiver.** This covers an application-level retry, a redundant send, or a value that a
  collective algorithm sends twice. The second copy is a duplicate slot.
  - Its content carries nothing new, but its presence is a real frame, and therefore timing.
  - Under the bijection it is unexplained unless the circuit has it as a second edge. A second edge means a second
    member of the collective Definition, as in ring or tree all-reduce, where a chunk is forwarded hop by hop.
  - The relation does not deduplicate. Deduplicating would let a sender choose how many copies to send.
- **The physical algorithm isn't the logical one.** TP Builds model `AllReduce2_v1{N}` and `AllGather2_v1` as the
  one-shot exchange: each rank sends its whole partial to its peer, with members `<site>/part_rank{r}` and `<site>/0`
  per step. NCCL's ring all-reduce instead sends a reduce-scatter chunk of partials, then the all-gather chunk of sums.
  - At N = 2 this is the same bytes per rank, but different values (half partials and half sums), summed in a
    different order.
  - The mappings coincide only if one of two things holds:
    - The transport is pinned to the algorithm the Definition models: a one-shot custom all-reduce, or NCCL with the
      algorithm, protocol and channel count pinned.
    - The Definition models the transport exactly: ring order, chunking, and the dtype and rounding of each partial sum.
  - The second is also what makes the summation exact under FP semantics, so the circuit side owes it either way. Its
    statement is that the physical collective's outputs equal the logical `AllReduce` at each rank. It is a refinement
    lemma about the Definition, not part of this relation.

So the relation is stated over the physical circuit (the circuit TP Builds output). The logical circuit is related to it
by the collective Definitions' refinement, and duplication is explained only by distinct edges.

## 8. A first check on real network certificates

The check is `benchmarks/network_traces/consistency.py` (branch `cursor/network-certifier-schedule-bound-cfc7`). It
checks what can be checked without a Build of the same requests.

- **φ:** whether every real slot is canonical.
- **Ingress, direction 1:** whether every certified request equals its run input, which is the workload's
  `active_replay.live_body(session, model)`.
- **Egress, direction 2:** each stream's bytes are split into events, classed declared, advice, crossing or unexplained,
  and compared with the server's own event log.

**The data.** All ten configurations (honest and covert) of the live vLLM recording art:cc136bcf (run
r20261006-035423-2cd5, llama8b, active certifier, B = 4,096, T = 600, τ_b = 100 ms, r = 1,686). The recorded check is run
r20261006-062817-bc66, record art:3ab2e518.

**The result:**
- **φ:** 0 non-canonical slots out of 736,712 real frames: ingress 19,580 LAST and 1,792 DATA; egress 715,340 DATA, each
  exactly one event.
- **Ingress:** all 19,580 certified requests equal their run inputs.
  - Bytes: 21.9 MB crossing (prompt and max_tokens), 3.9 MB declared.
  - 1.7 MB is unexplained relative to the run inputs: the workload's `user` session label and trailing-space filler.
    These are client-side and belong in the run inputs.
- **Egress:**
  - 18,223 streams compared with the server log, and 0 differ. One covert configuration has no server log, so its 913
    streams are reported as uncompared, not as passing.
  - All 696,429 JSON events reserialize exactly, plus 18,911 `[DONE]` events.
- **Egress bytes by class** (176 MB): declared 77.7%, unexplained 13.1%, advice 3.6% (the `id:` positions), crossing
  5.7% (the text).
  - Every one of 19,136 requests carries a 16-hex-digit (64-bit) random completion id and one `created` value, spanning
    up to 358 s within a run.
  - Busy egress link-windows hold 34,499 to 35,386 real frames, and the peak bucket is at r = 1,686.

**What it shows.** φ is canonical as built. The ingress direction holds end to end on real traffic. Egress needs §3's
canonical control protocol before direction 2 can hold: the 13.1% unexplained bytes are developer-choosable.

## 9. What the TP check needs

The check against a TP Build's crossing values did not run. It needs three things that don't exist yet:

1. **A recording with inter-node traffic.** Every recording is single-node. TP-2 inside one node crosses no certifier,
   and X2 makes the node the IU.
2. **A Build of the requests that were served through the certifier.** No Build exists of a recorded run's requests, so
   direction 1 on egress outputs, and on any interior edge, can't be checked.
3. **A pinned transport.** The TP Builds' one-shot AllReduce2 is not NCCL's ring traffic (§7).

**The format asked of @circuits**, for a TP-2 run across two certified nodes:
- per step, the members `<site>/part_rank{r}` and `<site>/0` for o_proj, down_proj, embed_tokens and lm_head;
- for each member: the step, the rank pair, the values-tree position, the dtype, and the byte encoding;
- the Build's request-to-step map;
- the Definition's transport (one-shot or ring) and the pinned NCCL settings.

With that, `consistency.py` gains an interior-link mode that checks direction 1 per member and direction 2 per real
slot.

## Correction from @circuits (X4, 6 Oct 10:30Z, main `a7134c413`)

§7 and the "pinned transport" item assumed the TP Builds use a one-shot all-reduce. They don't.

**Transport.**
- The TP Builds run pynccl with custom all-reduce disabled and `NCCL_P2P_DISABLE=1` (recorded as `env_required`), on batch-invariant NCCL (tree / Simple).
- Their Definitions (`AllReduce2_v1` at 2 ranks, `AllReduce_v2` chained above that) model the result's arithmetic, not the messages on the wire.
- What the wire carries is NCCL's tree traffic.
- Nothing records NCCL's actual choice (algorithm, protocol, channels, transport, version), and no TP Build spans nodes.
- So direction 1 at a node boundary needs two things:
  - NCCL's choice, recorded and pinned;
  - a wire model of tree / Simple chunks as a Definition, or a transport the certifier can frame canonically.

**Members.**
- The rank-local input is `<site>/part_rank<r>`; an all-gather's is `shard_rank<r>`.
- The reduced output has one of three names:
  - `<site>/0` for dense row-parallel linears;
  - `<site>/out` for fused MoE and mid-module sites;
  - the bare `<site>` for `embed_tokens` and `logits_processor`.
- Two caveats:
  - on a `reduce_results=False` model, `/0` is the partial;
  - GLM's fused all-reduce + RMSNorm commits no bare sum.
- The bytes are raw bf16, row-major and little-endian, at a 4-byte-aligned offset in the step's packed stream, under 256-byte `chunk-leaf-v1` leaves. Those leaves are still SHA-256, so they need the one-hash move.
- The address comes from `binding_map_rank<r>.json`, not from the name.
- Example: Llama-3.2-1B TP2, step 5, `o_proj/part_rank1` is [1, 2048] bf16, 4,096 bytes.

**Request to step.** Request r's step s is engine step `arrive_step + s`, as the Program declares. The binding map's request blocks carry the collector's `step_rows`. Token positions follow from the schedule.

The two-node recorded check comes after 7:00 AM PDT (14:00Z).
