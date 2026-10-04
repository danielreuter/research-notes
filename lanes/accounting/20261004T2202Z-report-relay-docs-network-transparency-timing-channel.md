---
id: 20261004T2202Z-report-relay-docs-network-transparency-timing-channel
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/network-transparency/timing-channel.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/network-transparency/timing-channel.md`, sha256 `1e6486a09c46303297a3ab42db39e1bebc037f3c99ecbe779d621b7a39c22f37`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Network transparency: covert capacity of the bucketed timing channel

28–29 Sep 2026. An experimental branch. The Lean is in `lean/submissions/network-timing/` (§5). The reference
implementation is the draft [PR #326](https://github.com/danielreuter/verity/pull/326), `protocols/network_warden`.

**History.**
- **18:50Z and 19:10Z:** the red team's two FIX rounds, both resolved, and its GO on the theorem
  (`internal/network-transparency/redteam-verdict*.md`).
- **19:35Z:** Daniel's first answers.
- **20:10Z:** Daniel's second answers (`docs/project-context.md`, "Network decisions, round 2").
  - Release is constant-rate, with clock-sync advice, and Theorem 3 is rewritten around it.
  - A violation is recorded and rejected, with no halt.
  - Jitter is calibrated against honest provers; that a sender can't shift release times is tested separately.
  - POUS's challenges stay inside the spatial unit.
  - Spatial and temporal units replace "compartment", and "claim" is gone.
- **20:20Z:** the ontology's term mapping is applied, and the K charge follows its decision 7: ingress only, from the
  last wipe before the IU starts.
- **29 Sep, 00:30Z:** calibration evidence for decision D, from honest traces rebuilt from recorded runs (§3.6). The
  reference package is renamed `network_warden` (Daniel's call).
- **29 Sep, 00:45Z:** Daniel decides D: the ingress bucket is 100 ms, and the per-token trace run is deferred.
- **29 Sep, 17:40Z:** deployment decisions A11 and A13, on the agents' recommendations (Daniel deferred).
  - Committed weights sit outside the wipe domain (§3.2).
  - Warden records are committed by hash, with padding elided (PR #326 `commitment`; the capacity bounds on committed
    records also assume `cr/sha-256`).

**Terms.**
- **Verity's terms:** from the README Glossary and `verity.proofs.profile.IntegrityProfile`.
- **Physical terms:** Daniel's *spatial unit*, the machines behind network wardens, and *temporal unit*, a spatial
  unit's computation between two wipes.
- **Terms owned here:** only the network terms, in §4. The resource-ontology owner is revising its document to match,
  and its term mapping is pending.

**Sources:**
- Daniel's September draft (`internal/network-transparency/sept-draft-fixed-slot-bucketing.md`);
- the Notion pages [Network tap security properties](https://app.notion.com/p/208c04501cff4b25a8161d6b8ab32939) and
  [Zero covert capacity from a declared causal rule (v2)](https://app.notion.com/p/eb8f6159e79342e88d94aeca0a7c5891),
  whose causal-uniqueness theorem this generalises;
- [Verity](https://app.notion.com/p/3d2399515d9e805b8d24dd0bad9b8bca);
- `internal/verity-ontology-draft.md`, used only for K.

**Checks** (`internal/network-transparency/`):
- `capacity_numbers.py`;
- `grid_bruteforce.py`;
- the red team's `redteam_checks.py` and `redteam_checks_round2.py`.

**Notation.**
- **X and ∂X:** a spatial unit, and its boundary links.
- **r:** a link's allocation, in frames per bucket. It plays the role the earlier drafts gave the slot count S.
- **Covert capacity** C(ℓ, w): what link ℓ can carry in window w, beyond what the Program and its prescribed inputs
  determine. It is the ontology's network residual `Res_net`, and C_in is its ingress part.

## 0. Result

**Constant-rate release.** The warden releases every link's frames in a fixed grid of T buckets per window, and every
bucket carries exactly r frames:
- the real frames come first, left-packed, in queue order;
- padding fills the rest.

The wire therefore looks the same in every bucket. Colluding receivers can still tell padding from real frames, though,
so what remains observable is the link's **occupancy**: the number of real frames in each bucket, n_0, …, n_{T−1}. Once
the Program fixes the frames' content and their order, occupancy is the only thing the sender still controls: it is the
timing channel.

**Two bounds** hold against any adversary (adaptive, colluding, with feedback and unbounded memory):

~~~text
every run:      what (ℓ, w) emits      ≤  log2 #G_lp + R·log2 D + log2 #Σ   ≈ T·r·B    (the unbound capacity)
accepted runs:  C(ℓ, w)                ≤  log2 #G_acc(ℓ, w) + R·log2 D                  (Theorem 1)
~~~

A rejected window may already have carried up to its unbound capacity before it was rejected. The bound is on accepted
runs. A violation is recorded, and the protocol rejects the run, as a policy signal.

**Without structure, occupancy is a large channel.** If timing advice could choose it freely, every bucket, occupancy
would carry up to `T·log2(r+1)` bits per link-window (Proposition 2; this is the *envelope*). That is about 6,000 bits
per 1-minute window at 100 ms and r = 1,024.

**Clock-sync advice pins it down (Theorem 3).** The Program gives every real frame a *logical release time*:
- its **anchor**: the recorded bucket of the request it answers;
- plus an **offset δ**;
- plus its index within the session divided by a **rate ρ** (frames per bucket).

The warden's FIFO rule at allocation r then fixes each frame's bucket. The only timing advice is (δ, ρ) per window, the
advice that syncs the Program's logical clock to the physical one. So accepted runs carry at most
`A_c + Σ_w log2 #Σ_sync` bits (A_c is the content advice), and never more than the envelope.

**The numbers.** With 16 offsets and 8 rates, the clock-sync advice is **7 bits per window**. That bounds **egress**,
what X can exfiltrate.

**Ingress is different.** For K only ingress counts, and ingress timing is set by the outside sender, who chooses when
requests arrive, so no clock pins it. Its covert capacity is the ingress grid's envelope, `log2(r_in+1)/τ_in` per
ingress link.

| At 100 ms, 1-min windows | Per window | Per day | Per day, as a share of K |
|---|---|---|---|
| Egress, one clock per spatial unit | 7 bits | 10,080 bits | (not charged to K) |
| Egress, one clock per link (4 links) | 28 bits | 40,320 bits | (not charged to K) |
| Ingress, one link at r_in = 64 | 3,613 bits | 5.2e6 bits | 5.7% |
| Ingress, one link at r_in = 1,024 | 6,001 bits | 8.6e6 bits | 9.5% |

**K** = αΓ ≈ 9.1e7 bits (about 11 MB) is the inference-only policy's budget per inference unit (IU). Under the
ontology's decision 7, an IU is charged two things:
- the ingress covert capacity across ∂X, from the last wipe before it starts to its end;
- what survived that wipe.

Egress is exfiltration, reported per spatial unit and window.

**What constant rate costs.**
- **Padding bandwidth.** Every link carries its allocation r·B/τ_b at all times, real or padding: 335 Mbit/s at
  r = 1,024, B = 4 KiB and τ_b = 100 ms. The padding share is 1 − (mean real frames per bucket)/r, which calibration
  measures, and which is large for bursty inference traffic (for example 90% at 10% utilization).
- **Latency.** A session's first frame leaves δ buckets after its anchor, and δ must cover honest compute latency
  across the window's load. Later frames leave at the pace ρ, even when the GPU is faster. Bucketing adds up to one
  bucket, and queueing adds delay when bursts exceed r.

**Grid parameters.** The protocol fixes T, τ_b, r, B and the clock-sync ranges from a security parameter. For example,
it chooses them so that the charge per IU stays under a target share of K. The default is
τ_b = 100 ms, with r and the sync ranges calibrated from honest vLLM runs (`internal/network-transparency/calibration-spec.md`).
On honest traces rebuilt from recorded runs (§3.6), plaintext serving needs r ≈ 1,000 and the request link r_in = 33,
with no honest misses.

**Two conditions weigh as much as the grid:**
- **Left-packing, with a Program-fixed release order** (both decided): free slot choice would cost r/log2(r+1) times
  more, and a free order up to 72×.
- **Senders cannot shift the warden's release times.** That is a warden property, tested (§1.4).

## 1. Threat model and warden assumption

### 1.1 Setting

Every link crossing ∂X has an active warden, which is trusted. The **adversary** is everyone else acting together:
- the devices in X, which hold the secret Z;
- every endpoint beyond the wardens: receivers, senders, the orchestrator and the operator;
- the party that declares the advice.

It is computationally unbounded, adaptive and stateful, and its receivers see everything a warden emits, at any timing
resolution. It does not control the wardens, their clocks, the grid parameters, the verifier or the Program. The
Program is committed without access to Z (the Notion page's condition (I)).

**Egress** exfiltrates Z. **Ingress** is chosen by an upstream colluder and observed inside X.

### 1.2 What the warden controls (assumption W)

For each link ℓ and window w:

- **W1, fixed parameters.** The protocol programs them into the warden, derived from a security parameter. They are
  public before w and independent of Z and of traffic:
  - the window's start, T, τ_b (`|w| = T·τ_b`), the allocation r and the frame size B;
  - the queue capacity Q and its overflow policy;
  - every bucket's cutoff c_t and every slot's emission time τ_{t,s}.

  A frame delivered into X in ingress bucket t is readable by the Program only from egress bucket t + 1 on, a fixed
  lag on recorded buckets. Inter-warden clock skew is bounded inside the guard interval.
- **W2, regeneration and re-timing.** The warden terminates the physical and transport layers on both sides, and the
  two sides are independent:
  - frames are re-emitted from its own clock;
  - no physical-layer feature, ack, credit or backpressure crosses;
  - outer emission is fire-and-forget;
  - ingress delivery doesn't depend on the device accepting it (a refusal only sets σ).

  A frame fully received by c_t is eligible for bucket t, and slot (t, s) leaves at a fixed τ_{t,s} > c_t, with a guard
  interval covering the warden's worst-case processing time. So every emission on ℓ during w is a function of the grid
  g, the jitter j (§1.4), the status σ and warden noise ν that is independent of the adversary.
- **W3, fixed frame size.** Every frame is exactly B bits. A message of λ bits occupies ⌈λ/B⌉ consecutive frames by a
  fixed rule.
- **W4, constant-rate, left-packed (decided).** One FIFO queue per link.
  - Bucket t emits exactly r frames: `n_t = min(eligible queue, r)` real frames in slots 0 … n_t − 1, in queue order,
    and warden padding in slots n_t … r − 1.
  - It is a fixed rule the warden executes, so the sender can't choose positions or the number of frames on the wire.
  - Free slot choice is counted only for comparison.
- **W5, the record is exactly (grid, σ).**
  - The grid gives every slot's content, real or padding, bound to the grid parameters and to (warden, link, window).
  - σ is one untimed symbol per link-window, published at the window's end: complete, or not established with a reason.
  - The record has no arrival times, queue depths, drop counts or fault times.
- **W6, fail-closed.** Every failure leaves emissions a function of (g, j, σ, ν), with g left-packed. Nothing is
  forwarded unwardened; after a fault the rest of the window is padding, and σ records the reason.

**Acceptance.** A link-window is accepted if three things hold:
- σ = complete;
- the grid equals the Program's grid (§2.4);
- both are established by a verdict deadline L windows after the window closes.

Anything else is a **violation**. It is recorded, and the protocol rejects the run, as a policy signal. There is no
halt. A non-complete window is never a gap: honest faults are violations too.

### 1.3 What the adversary controls

The **sender** of a link is whichever adversarial device enqueues its frames: a device in X for egress, or an outside
colluder for ingress. It controls:
- **when each frame enters the queue,** which sets every n_t, the timing channel;
- **the frames' order, content and length;**
- **the advice,** within what the audit accepts;
- **coverage events:** overflow, malformed frames, pulling a link or refusing delivery. A device in X can set an ingress
  link's σ, so every boundary link's status counts as egress.

### 1.4 Jitter

There are two separate things here, handled differently.

- **J, a warden property that is tested.** A sender cannot shift the warden's release times: slot (t, s) leaves at
  τ_{t,s} by the warden's clock, whatever the sender does. This is established by adversarial testing of the warden:
  - adversarial senders: data-dependent timing, contention across links, power or thermal coupling, edge races;
  - adversarial receivers: ack timing;
  - coupling between the two directions of a cable.

  Under J, jitter carries no sender information (D = 1). If testing finds residual influence with D distinguishable
  levels on R emissions, the bounds gain R·log2 D. With uniform warden dither of width u against an offset window of
  width a, that is at most `log2(1 + a/u)` bits per emission.
- **The expected distribution, which is calibrated.** Release-time jitter measured from honest provers on the same
  hardware is the reference the J test compares against, and the baseline for anomaly detection (calibration spec §4).

### 1.5 Out of scope

- Paths that bypass the wardened links.
- State queued across a wipe.
- The correctness of the Program's run, which enters only through §2.4's integrity term.
- The grid's confidentiality.
- POUS: its challenges come from within the spatial unit and stay there, so they never cross a wardened link.

## 2. The covert-capacity theorem

### 2.1 Objects

- **Slots and grids.** A slot holds padding ⊥ or a real frame f ∈ {0,1}^B, and a grid g is a T × r array of slots.
- **Occupancy.** occ(g) marks the real slots. Under left-packing, that is the same as n_t, the number of real frames in
  bucket t.
- **Packings.** `P_free = {0,1}^(T×r)` counts free slot choice, for comparison. `P_lp` counts left-packed grids, and is
  in bijection with {0,…,r}^T.
- **Releasable grids.** G_lp is the set of grids with occupancy in P_lp.
- **The observation of (ℓ, w).** It is O = (g, j, σ).
- **Accepted runs.** E is the event that every link-window of ∂X in the horizon is accepted. G_acc(ℓ, w | h) is the set
  of grids released in some run with history h that is accepted up to and including (ℓ, w). This is acceptance by
  prefix.

**What is conditioned on.** All counts are conditional on the Program's prescribed inputs. The Program reads ingress
content as declared input, which the inference-only policy charges as reads (§2.5). Z is anything else the
adversary holds.

### 2.2 Theorem 1 (counting bounds)

Assume W1–W6 and J, and let the outside parties follow a Z-independent strategy. Write
`N_rel(ℓ, w) = #G_lp · D^R · #Σ` and `N_acc(ℓ, w) = max_h #G_acc(ℓ, w | h) · D^R`. On accepted runs σ is complete, so
N_acc has no status factor.

- **(a) Every run.** A decoder that sees everything the wardens emit distinguishes at most ∏ N_rel values of Z, and
  `I(Z; emissions) ≤ Σ log2 N_rel`. This is the unbound capacity.
- **(b) Accepted runs.** The observation sequences of runs in E number at most ∏ N_acc, so
  `I(Z; O | E) ≤ Σ log2 N_acc`. The bound is of the form accept ⇒ bound, with δ = 0 for the counting.

*Proof.*
- **(a)** Condition on ν and on the outside coins, both independent of Z. By W2 and W6 every emission is a function of
  (O, ν). Order the link-windows by time, then by link. Then `I(Z; O_1 … O_k) ≤ Σ H(O_i | O_<i) ≤ Σ log2 N_rel(i)`, and
  for a deterministic adversary z ↦ (O_1 … O_k) takes at most ∏ N_rel(i) values.
- **(b)** In a run accepted up to step i, the observation at step i lies in G_acc(h) × [D]^R. So the prefix-accepted
  sequences form a tree with at most N_acc(i) children at step i, and E's runs are among its full paths. ∎

**What is assumed of whom.** Nothing restricts the adversary: there is no finite-state, memoryless or stationary
assumption, and feedback doesn't help. Finiteness comes only from the warden (W1–W6) and from J.

**The unbound capacity** is `log2 #G_lp = T·log2(Σ_{n=0..r} 2^(n·B)) ∈ [T·r·B, T·r·B + T·2^(1−B)]`. Timing matters
exactly when content is bound, which is Verity's case, and only on accepted runs.

### 2.3 Proposition 2 (the occupancy envelope)

**The fill.** Under W2–W4, g = fill(f, n): the k-th real frame of the queue-order sequence f goes to the k-th real
slot, in index order t·r + s. For a fixed f, n ↦ fill(f, n) is injective. So once the frames and their order are fixed,
the grid carries exactly the occupancy's information.

**The counts:**
- **free slots:** `#P_free = 2^(T·r)`;
- **left-packed:** `#P_lp = (r+1)^T`;
- **at most M real frames available:** at most `binom(M+T, T)` grids. The warden never releases more than was enqueued
  (Lean: `sum_released_le`, `encard_fifoGrids_le_of_available`);
- **all M released:** at most `binom(M+T−1, T−1)`;
- **a deadline of d buckets from a reference the sender doesn't choose:** at most `(d+1)^M`. With sender-picked
  references there is no such bound.

**Tightness.** With at least T·r frames available, the sender enqueues n_t ≤ r frames in bucket t before c_t, and
realises every n ∈ {0,…,r}^T. That carries `T·log2(r+1)` bits, with zero error at D = 1. This is the envelope: what
occupancy carries when nothing pins it.

**Order.** The queue order decides which frames fall in which bucket. With distinct frames available early, a free
order carries up to log2 M! bits: 72× the occupancy term at 1 ms × 16 slots over a 1-minute window. Within-bucket
sorting still leaves 61×. A Program-fixed order (decided: the canonical gate order) removes it.

### 2.4 Theorem 3 (constant rate and clock-sync advice)

**The logical schedule.** The Program assigns every real frame k two things:
- an **anchor** a(k): the recorded ingress bucket of the request it answers (for a frame with no request, the window's
  first bucket);
- a **logical index** λ(k): its position within its session, from the canonical gate order.

The window's **clock-sync advice** is σ_w = (δ_w, ρ_w), from a fixed set Σ_sync, for example δ ∈ {0,…,15} buckets and
ρ ∈ {1,…,8} frames per bucket. Frame k is eligible at the logical bucket

~~~text
e(k) = a(k) + δ_w + ⌊λ(k) / ρ_w⌋
~~~

The Program's grid is the warden's own rule (W4) applied to these logical times: FIFO in canonical order, r frames per
bucket, real frames first, padding after.

**How a run passes.** The sender's shaper (§6) hands frame k to the warden exactly at e(k). On an accepted run, then,
the physical grid equals the logical one:
- a frame that isn't ready by e(k) makes the window a violation;
- so does a frame handed over early.

**The statement.** Assume W1–W6 and J, and the exact binding: (ℓ, w) is accepted only if its grid equals the
Program's. The Program is deterministic, committed Z-blind, and reads the recorded ingress, its content advice a_c and
the clock-sync advice. Then, for every Z-independent operator strategy, over the horizon:

~~~text
log2 #(accepted grid sequences)  ≤  A_c + Σ_w log2 #Σ_sync(w)                       (the advice cap)
log2 #(accepted grid sequences)  ≤  A_c + Σ_β min( A_t(β) , Σ_{(ℓ,w)∈β} T·log2(r+1) )  (the block cap: the envelope)
~~~

Here the timing advice is `A_t = Σ_w log2 #Σ_sync(w)`, the whole horizon being one block. With one clock per spatial
unit, #Σ_sync = 16·8 gives **7 bits per window**. Counting (grid, jitter) sequences adds R·log2 D, which is 0 under J.

*Proof.*
- **The advice cap.** The Program's grid is a function of the recorded ingress, a_c and the sync advice. On accepted
  runs the physical grid equals it, and the recorded ingress is a function of the operator's Z-independent strategy and
  the earlier observations. By induction over buckets, each advice string then determines one accepted grid sequence,
  so the count is at most `2^A_c · ∏_w #Σ_sync(w)`. This is the Lean theorem `encard_accSeqs_le_advice`, with the
  advice type `Ac × (windows → Σ_sync)`, and its corollary `encard_accSeqs_le_sync`.
- **The block cap** is the general bound, `encard_accSeqs_le_blocks`. It holds for any timing advice under the two
  dataflow conditions:
  1. frames and their order read no timing advice (timing-driven batching that changes content is content advice);
  2. each block's occupancy reads only that block's timing advice.

  With free per-bucket advice it gives the envelope. The logical schedule is the case where the advice is tiny. A queue
  carried across a window boundary makes one window's occupancy read the previous window's (δ, ρ), which is why the
  horizon is one block. The total is the same `Σ_w log2 #Σ_sync`. ∎

**How it relates to earlier results.**
- Fixed (δ, ρ) (#Σ_sync = 1) gives zero timing capacity on accepted runs: the Notion zero-capacity theorem.
- Free occupancy advice gives the envelope T·log2(r+1).
- It is the draft's "A bits select at most 2^A transcripts", made adaptive, with the timing part of A made small by
  design.

**Honest runs must meet the schedule.** A window's (δ, ρ) must be one that an honest run meets: every frame ready by
e(k). Calibration picks the set Σ_sync so that some element is met with probability at least 1 − ε per window across
honest load. A miss is a violation.

**Where the advice comes from.**
- Advice declared from outside X is a function of what was emitted, so it adds nothing.
- Advice declared from inside X travels over a boundary link, and is counted there.

**Integrity term.** Under sampled proofs the grid equals the Program's committed values, which are right except at
wrong proof units. The integrity profile allows at most f wrong units out of U, except with probability δ, and F is
the largest total of their output bits. Then `F + log2 Σ_{j≤f} binom(U, j)` is added, once per horizon, except with
probability δ.

### 2.5 Corollaries (accepted runs)

- **Per spatial unit.** `C(∂X, w) ≤ Σ_{ℓ∈∂X} C(ℓ, w)`, reported separately for egress and ingress; every boundary
  link's status counts as egress. With one clock per spatial unit, the timing part is the one sync advice, not a sum
  over links.
- **Across spatial units.** Information about Z_X that reaches Y by time t is at most the sum over windows up to t of
  X's outflow; a relay can store and forward.

  The min with Y's inflow holds only if Y's ingress content is prescribed, absent, or tied to an upstream Program
  output. Otherwise a relay could re-encode timing as content.
- **Ingress content** is declared input, charged as reads: accounted, not covert. An ingress link's covert part is its
  timing. No clock pins it, because the outside sender chooses when requests arrive, so its bound is the ingress
  grid's envelope, `T·log2(r_in+1)` per ingress link-window. That is why the K charge (§3.2) is set by the ingress grid
  parameters, not by the clock-sync advice.
- **The inference-only policy.** Timing reaches the Program's values in three ways:
  - as recorded ingress;
  - as advice;
  - through wrong proof units.

  The policy charges all three, so no IU reads more than its K of timing. What lies outside the Program is bounded by
  C(∂X, w) per window: unaccounted compute, exfiltration, and re-importing state after a wipe. Its charge per IU counts
  ingress only (§3.2).

### 2.6 What an accepted audit establishes

The fields a network profile would carry, beside `IntegrityProfile`, POUS's `StorageProfile` and PoUW's
`WorkProfile`:

~~~text
measure     bits
of          the Program's digest; the content advice's length A_c; the clock-sync set Σ_sync and its choices
over        the spatial unit X's wardened boundary links ∂X, per link-window and summed
window      w, a whole number of buckets (T = |w| / τ_b), within a temporal unit
bound       on accepted runs: C(∂X, w) ≤ A_c + log2 #Σ_sync(w) + Σ_{ℓ∈∂X} R·log2 D
                                        + F + log2 Σ_{j≤f} binom(U, j) + Σ_{unwardened ℓ} capacity(ℓ, w)
            (envelope, if the timing advice were free per bucket: T·log2(r+1) per link-window)
delta       the integrity profile's δ; the counting has δ = 0
rests on    W1–W6; J (tested); the Lean theorems of §5
premises    the integrity profile's allowance (f, U, F, δ); capacities of the unwardened links; the logical schedule
            (checked from the Program)
not covered rejected windows: recorded as violations, the run rejected, and the profile and every premise it
            discharges void from that window on; paths not described as links
~~~

## 3. Numbers

### 3.1 Constant rate at 100 ms

Assumptions: 4 KiB frames, 1-minute windows (T = 600), #Σ_sync = 128 (7 bits), J (D = 1), and a reference spatial
unit with 4 boundary links.

| Allocation r | Bandwidth per link (constant) | Egress sync advice | Egress per link-day, one clock per link | Envelope per link-window (free timing; ingress's bound) |
|---|---|---|---|---|
| 64 | 21 Mbit/s | 7 bits per window | 10,080 bits | 3,613 bits |
| 256 | 84 Mbit/s | 7 bits per window | 10,080 bits | 4,803 bits |
| 1,024 | 335 Mbit/s | 7 bits per window | 10,080 bits | 6,001 bits |

On egress the sync advice doesn't depend on r, so the allocation sets only bandwidth and headroom. On ingress, where no
clock applies, the envelope column is the bound, and it grows with r_in (§3.2).

**Padding share.** It is 1 − utilization, and calibration measures it. With r sized at twice the p99.9 of bursty
per-bucket demand, utilization of 10–20% is plausible, so 80–90% of the bandwidth is padding.

**Latency.**
- **First frame of a session:** δ buckets after its anchor, with δ at the honest high percentile, for example
  δ = 10 (1 s).
- **Later frames:** paced at ρ per bucket.
- **Plus:** up to one bucket per warden hop, and FIFO queueing when the eligible frames exceed r.

### 3.2 Against K (ingress only)

`K = α·Γ = 9.6e−11 × 9.5e17 = 9.12e7 bits`, per IU.

**The charge** (the ontology's decision 7):

~~~text
charge(u) = C_in(∂X, from the last wipe before u starts to the end of u) + Res_mem(X, just after that wipe)
~~~

- An IU may span several temporal units, and covert bits entering X before it starts can wait in memory until the next
  wipe.
- For an IU inside one temporal unit, with one window per temporal unit, this is this document's former default,
  restricted to ingress, plus what survived the wipe.
- Egress is not charged to K.

**Committed weights sit outside the wipe domain** (deployment decision A11, 29 Sep).
- **What a wipe clears:** KV cache, activations, scratch and the warden queues, in HBM, DRAM and NVMe.
- **What stays:** the committed weight image. It is re-verified against its commitment after each wipe.
- **Why this is sound:** the weights' bits are prescribed and checked, so they are no part of Res_mem, and they carry
  no covert bits into the next IU.
- **What isn't exempt:** anything outside the committed image, including slack around the weights. It is in the wipe
  domain.
- **What it saves:** a wipe forces no weight reload over the constant-rate links (68.5 GB at 335 Mbit/s takes about
  27 min) and no POUS re-setup.

The clock-sync advice doesn't enter the charge. The ingress grid parameters do:

| Ingress link | Rate | Per hour since the wipe | Share of K | Per day | Share of K |
|---|---|---|---|---|---|
| r_in = 16, τ_in = 100 ms | 40.9 bit/s | 1.5e5 bits | 0.16% | 3.5e6 bits | 3.9% |
| r_in = 64, τ_in = 100 ms | 60.2 bit/s | 2.2e5 | 0.24% | 5.2e6 | 5.7% |
| r_in = 1,024, τ_in = 100 ms | 100 bit/s | 3.6e5 | 0.39% | 8.6e6 | 9.5% |
| r_in = 64, τ_in = 1 s | 6.0 bit/s | 2.2e4 | 0.024% | 5.2e5 | 0.57% |

**For example,** a spatial unit with a request link at r_in = 64 and a storage link at r_in = 1,024, both at 100 ms,
is charged 0.63% of K per hour since the last wipe, or 15% per day, plus the memory that survived the wipe.
Calibration (§3.6) puts a request link at r_in = 33 at 100 ms: 50.9 bit/s, 0.20% of K per hour.

**The lever** is the ingress grid: few ingress slots and wider ingress buckets, within the request-latency budget.
Decision D fixes it at 100 ms (§7). The egress figures of §3.1 matter for exfiltration.

### 3.3 For the other protocols' premises

These hold on accepted runs, with egress content bound and ingress content prescribed, absent, or tied upstream.

- **POUS locality** is now local. Its challenges never cross a wardened link, and outside help during an answer window
  would have to arrive over ∂X. On accepted runs that is at most the sync advice of the windows the answer overlaps:
  14 bits.
- **PoUW attribution by flow.** An outsourced 4096³ int8 matmul must move its activations, 1.3e8 bits, across ∂X.
  At about 10^4 bits per day that is impossible. It also requires that the activations can't be recomputed outside X.

### 3.4 The envelope's hazards

These are what structure removes. The figures are for a 1-minute window at 1 ms × 16 slots, whose occupancy envelope is
2.5e5 bits.

| Case | Bits per link-window | × envelope |
|---|---|---|
| Sender-chosen slots | 9.6e5 | 3.9 |
| Program fixes M = 100 frames | 1.1e3 | 0.004 |
| Free sender order, full buckets | 1.77e7 | 72 |
| The same, with within-bucket sorting | 1.50e7 | 61 |
| One jitter bit on every slot | 9.6e5 | 3.9 |

### 3.5 The toy (draft §14)

With T = 6 and r = 2, the occupancy envelope is 12 bits with free slots and 9.51 bits left-packed. The toy's
2-bit advice gives at most 4 grids internally. The link to the outside is sorted by request id and carries 1 bit.
Unbound, the grid carries T·r·B = 192 bits.

### 3.6 Calibration: honest traces for decision D

These numbers are the evidence for decision D, which Daniel decided at 100 ms on 29 Sep, 00:45Z (§7). They come from
`network-warden-calibrate` ([PR #326](https://github.com/danielreuter/verity/pull/326)) on honest traces rebuilt from
recorded runs, on CPU, with no new GPU run. The script and every report are `internal/network-transparency/honest_traces.py` (seeded) and
`decision-d-calibration.json`.

**The evidence.** No recorded run has per-token network timestamps. The evidence store does have per-step engine times,
and the traces are built from those:
- **Plaintext and POUS-on vLLM** on one L40S (Qwen2.5-0.5B), from run `r20260928-215545-dbac`
  (`pous_e2e_pod.sh CODEC=band-chain/d12/v1`, run files `art:2bd41187…`):
  - plaintext decode takes 11.4 ms per step (the median of 65 steps), and prefill 6.8 µs per token;
  - POUS-on decode takes 8.05 s per step (5 steps), with prefill inside the step: 4 × 2048 tokens took 8.11 s.
  - That run's audit was not accepted, because its encode didn't match the verifier's. Its serving times still stand.
- **Commit-instrumented** step times come from the admission fixture `steps.jsonl`: 128 steps, a median of 30.6 ms,
  and a 190 ms first step.
- **Batch scaling:**
  - plaintext decode runs at 102.5, 782 and 3,022 tok/s at batch 1, 8 and 32 (`docs/pous-throughput.md`), which is
    about +1.7% of step time per doubling;
  - the b64 Commit row `r20260924-014938-ca81` puts instrumented steps at about +22% per doubling.
- **Request mixes and arrivals** come from the recorded vLLM workloads (`integrations/vllm/workloads/`):
  - B16 staggered: I ≤ 1024, O ≤ 128;
  - B4 staggered: I ≤ 256, O ≤ 32;
  - B64 burst: I ≤ 1024, O ≤ 128, all requests at once.

**The traces:**
- **Replay.** Each workload is replayed open-loop, one instance per period, for 1 hour per workload (24 hours for
  POUS-on). The periods keep each engine below saturation: 1 s, 3 s and 10 s for plaintext; 2 s, 6 s and 20 s for
  Commit-instrumented; 5 and 20 minutes for POUS-on.
- **Ingress.** A request is `⌈(4·prompt_len + 512)/4096⌉` frames. It crosses the ingress grid at τ_in, sized by the
  tool's own rule, and is delivered when its last frame leaves.
- **Engine.** Continuous batching admits delivered requests at each step, first in, first out. A step takes a measured
  step time (resampled), times the batch factor, plus the prefill of the joining prompts.
- **Egress.** Every streamed token is one 4 KiB frame, in step-major canonical order, anchored at the egress bucket of
  its request's delivery.
- **Grid.** T = 600 (1-minute windows), τ_b = 100 ms, and Σ_sync of 16 δ × 8 ρ.
- **Ingress sizing.** r_in is sized two ways:
  - with the tool's default, a p99 queueing delay of at most one ingress bucket;
  - with a p99 of at most 200 ms at every τ_in, so the alternatives are compared at one latency budget.

**Egress, at τ_in = 100 ms.** Across all τ_in and both budgets, r stays within narrow ranges: 862–988 for plaintext,
246–302 for Commit-instrumented and 14–16 for POUS-on. Σ_sync's top rate moves by at most 12%.

| Serving mode | r | Bandwidth, padding | Σ_sync: δ (buckets), ρ (frames per bucket) | Declared δ, ρ | First frame p50 / p99 | Shaping delay p99 | Honest misses |
|---|---|---|---|---|---|---|---|
| Plaintext | 988 | 324 Mbit/s, 98.0% | 0–15, 1–8.29 | 1–3, 6.13–8.29 | 0.2 / 0.3 s | 0.2 s | 0 of 180 windows |
| Commit-instrumented | 302 | 99 Mbit/s, 96.8% | 0–15, 0.33–1.79 | 1–15, 1.41–1.79 | 0.5 / 1.5 s | 1.7 s | 0 of 180 |
| POUS-on | 14 | 4.6 Mbit/s, 99.7% | 0–165, 1/82 (0.0122) | 0–165, 1/82 to 3/245 | 8.8 / 16.5 s | 8.4 s | 0 of 2,865 |

The shaping delay is how long a ready frame waits for its logical bucket. Egress capacity is 7 bits per window in every
mode: 10,080 bits per day per spatial unit, with one clock.

**Ingress, the K charge.** Plaintext and Commit-instrumented give the same r_in, because the B64 burst sets it. Their
delivery delays agree within 3 ms, and the rows show plaintext's. The charge runs from the last wipe, per request link
(K = 9.12e7 bits).

| τ_in | p99 queueing budget | r_in | Covert rate | K per hour | K per day | Delivery p99 |
|---|---|---|---|---|---|---|
| 25 ms | 1 bucket | 33 | 203.5 bit/s | 0.80% | 19.3% | 50 ms |
| 50 ms | 1 bucket | 33 | 101.7 bit/s | 0.40% | 9.6% | 99 ms |
| **100 ms** | 1 bucket | 33 | 50.9 bit/s | 0.20% | 4.8% | 199 ms |
| 200 ms | 1 bucket | 33 | 25.4 bit/s | 0.10% | 2.4% | 398 ms |
| 25 ms | 200 ms | 8 | 126.8 bit/s | 0.50% | 12.0% | 211 ms |
| 50 ms | 200 ms | 14 | 78.1 bit/s | 0.31% | 7.4% | 243 ms |
| 100 ms | 200 ms | 22 | 45.2 bit/s | 0.18% | 4.3% | 299 ms |
| POUS-on, 25 ms | 1 bucket | 2 | 63.4 bit/s | 0.25% | 6.0% | 34 ms |
| POUS-on, 50 ms | 1 bucket | 2 | 31.7 bit/s | 0.13% | 3.0% | 85 ms |
| POUS-on, 100 ms | 1 bucket | 3 | 20.0 bit/s | 0.08% | 1.9% | 151 ms |
| POUS-on, 200 ms | 1 bucket | 4 | 11.6 bit/s | 0.05% | 1.1% | 352 ms |

The delivery delay is the wait for the next ingress bucket plus the FIFO queue. At 200 ms the two budgets coincide.

**What the numbers say:**
- **No honest misses** at any τ_in: 0 in 180 plaintext, 180 Commit-instrumented and 2,865 POUS-on windows. That bounds
  the rate below 1.7% and 0.1% (95%, the rule of three), not below the 1e-4 target.
  - Showing 1e-4 directly needs about 30,000 windows, 500 hours of 1-minute windows, per mode.
  - The resampled step times contain no event rarer than the 5–128 measured steps: no host pauses, preemption or
    network jitter.
- **τ_in is the lever on the K charge.** r_in is set by the largest simultaneous burst (the B64 row's 66 request
  frames), not by τ_in, so the rate falls as 1/τ_in: 204, 102, 51 and 25 bit/s.
  - At one 200 ms latency budget, finer buckets still cost more (127, 78 and 45 bit/s), because a smaller r_in lowers
    `log2(r_in + 1)` only slowly.
- **At the default 100 ms,** a request link is charged 0.20% of K per hour since the wipe (4.8% per day), with 199 ms
  of p99 delivery. That is below §3.2's r_in = 64 example.
- **Egress barely depends on τ_in.** It needs:
  - r ≈ 1,000 frames per bucket for plaintext, about 320 Mbit/s, 98% of it padding;
  - about 300 for Commit-instrumented;
  - 14 for POUS-on.
- **One (δ, ρ) per window costs latency where steps jitter.**
  - Plaintext frames wait at most 0.2–0.3 s.
  - Commit-instrumented frames wait up to 1.7 s at p99: one 190 ms step forces the whole window's ρ below the other
    sessions' pace. Per-session rates (decision A) would recover this.
  - POUS-on frames wait up to one decode step, 8.4 s, against a pace of 8 s per token.
- **One Σ_sync can't serve every mode.** Plaintext needs ρ up to 8 per bucket and δ ≤ 0.3 s. POUS-on needs ρ ≈ 1/82
  and δ up to 16.5 s. One 16-value δ range covering both would coarsen plaintext's δ to 1.1 s steps.
  - The set can be a function of the serving mode, which the Program fixes, so it adds no advice.
  - POUS-on's rates collapse to one value, so it needs only its 16 offsets: 4 bits per window.

**The upgrade path: the per-token trace run,** deferred by decision D and not run:
- **Setup.** One L40S pod runs vLLM's OpenAI server, streaming, with Qwen2.5-0.5B, in three modes: plaintext,
  Commit-instrumented and POUS-on (band-chain d12).
- **Load.** A client replays the three recorded workloads open-loop at the periods above.
- **Recording.** The server logs each request's arrival time and each streamed token's write time, in ms. That is
  exactly the tool's trace format.
- **Duration.** About 15 pod hours:
  - 1 hour per workload per mode for plaintext and Commit-instrumented (6 hours);
  - 8 hours for POUS-on;
  - about 1 hour of setup: the engine build and the 5-minute POUS encode.
- **Cost.** $12–16 at the store's recorded single-GPU L40S rates of $0.79–1.09 per hour.
- **What it replaces:** the engine model and the resampled step times, with measured token times that include host and
  network jitter.
- **What it can't show:** 1e-4 directly, which would take 500 hours per mode, about $400–550 each. That needs a tail
  model of each window's slack, or a target the record-and-reject policy can tolerate as false alarms.

**Fixes to PR #326 found on the way:**
- **ρ as a fraction,** down to 1/1024: POUS-on sessions produce one frame per 82 buckets.
- **The prover's choice in step-major canonical order,** so a long session no longer holds later sessions' frames
  behind it.
- **The honest prover minimises the window's total hand time.** Taking the least δ first had picked ρ = 1 to save one
  bucket. That paced B64 sessions at one frame per bucket and tripled r, to 3,442 at τ_in = 25 ms.
- **Ingress from arrival timestamps,** with a delay budget in ms and the delivery delay reported. This lets τ_in be
  finer than the trace bucket.
- **The shaping delay** is now in the report.

## 4. Minimal ontology

### 4.1 Glossary (network-owned)

- **Bucket:** one of the T equal release intervals of a window, with a cutoff and fixed emission times.
- **Allocation (r):** the constant number of frames a link emits per bucket, real frames first and padding after. It
  also caps the real frames per bucket.
- **Slot:** one of a bucket's r release positions, (t, s). It holds a real frame or padding.
- **Frame:** the fixed B-bit unit released in a slot. **Padding** is the warden's frame for a slot no real frame fills.
- **Release:** a frame leaving the warden in its slot. It is the grid's only event.
- **Grid:** one link's T × r slots for one window, real or padding: the warden's record, with σ, which the Program must
  reproduce.
- **Grid parameters:** T, τ_b, r, B, Q, the cutoffs and emission times, and Σ_sync. The protocol fixes them from a
  security parameter.
- **Occupancy:** the number of real frames released in each bucket, n_0, …, n_{T−1}. It is what the sender still
  controls once content and order are fixed: the timing channel.
- **Left-packing:** the fixed rule that real frames fill slots 0 … n_t − 1 in queue order.
- **Fill:** the map from a frame sequence and an occupancy to a grid.
- **Logical schedule:** each real frame's logical release bucket, `a(k) + δ + ⌊λ(k)/ρ⌋`, from its anchor and its
  logical index.
- **Clock-sync advice:** the per-window (δ, ρ) ∈ Σ_sync that maps the Program's logical clock to buckets. It is the only
  timing advice.
- **Envelope:** what occupancy carries when nothing pins it, T·log2(r+1) per link-window.
- **Jitter:** release-time variation the grid doesn't record. J says a sender can't influence it.
- **Coverage status:** σ, one untimed symbol per link-window.
- **Violation:** a link-window that isn't accepted, because its grid differs from the Program's, its status isn't
  complete, or no verdict came by the deadline. It is recorded, and the protocol rejects.

### 4.2 Terms this result reads (pending the ontology owner's mapping)

- **From Daniel:** spatial unit (X and its boundary ∂X) and temporal unit (a window lies within one).
- **Physical:** link and warden (active, W1–W6).
- **From Verity and the ontology:** advice, prescribed inputs, proof unit (PU), `IntegrityProfile`, residual
  (`Res_net`, which is C here), and the inference unit (IU) of the inference-only policy, for K.

### 4.3 Dropped deliberately

| Dropped | Instead |
|---|---|
| **From the September draft** | |
| communication array, slot array, M[t,s,f], W | grid |
| timestep | bucket |
| release opportunity | slot |
| present bit, canonical empty | occupancy; padding |
| release schedule | grid parameters |
| phase, sequence | bucket, slot |
| computed, queued, received | release is the only event |
| the three notions of "before" | buckets alone are physical time here |
| monitor failure and the other failure words | coverage-status reasons |
| `EpochStep`, `interface: returns`, layout, schema | the Program's projection |
| leafTag, ctx, Merkle | a byte format |
| "capacity is crisp: T·S·B" | the unbound capacity |
| epoch | window |
| execution | run |
| **From Notion** | |
| network tap | passive warden, unused here |
| task ledger, explanation | none |
| declared transcript | grid |
| operator | part of the adversary |
| **From the ontology drafts** | |
| pod, compartment | spatial unit |
| pod-epoch, wipe interval | temporal unit |
| bounded-accumulation policy, "the policy's level" | inference-only policy, inference unit (IU) |
| resource claim, claim window | the protocol's profile (`IntegrityProfile`, `WorkProfile`, `StorageProfile`, and a network profile) and its window; "claim" now means only a `verity.claims` id |
| **Earlier in this document** | |
| residual (for timing) | jitter |
| placement | fill |
| schedule (for warden parameters) | grid parameters |
| grid status | coverage status |
| empty slot, cover frames | padding (constant rate) |
| the halting and hold-until-accepted rules | none: a violation is recorded and rejected |

"Transcript" is avoided throughout.

## 5. Lean

**Where it lives.** `lean/submissions/network-timing/` in the project store, for now: a separate agent is planning the
repo's Lean organization. It is a self-contained Lake package, needing only Mathlib at `5ed29652` and Lean v4.34.0, so
it can move as a unit. `NOTES.md` lists every theorem and its hypotheses.

**Status: all proved, no `sorry`.** Only `propext`, `Classical.choice` and `Quot.sound` are used, and Verity `main`'s Lean
audit passes (kernel replay, layers, dependencies, 31 pins). The red team's statement review is GO. It covers:
- Theorem 1(b) on accepted runs, with the operator reacting to all observations (`encard_acceptedRuns_le`);
- the zero-error bound from the observations (`encard_obsDecodable_le`), and through the wire under W2
  (`encard_decodable_le`);
- W6 on accepted runs;
- Proposition 2 with tightness (`encard_fifoGrids`), and the fixed-M bound at the warden
  (`encard_fifoGrids_le_of_available`);
- Theorem 3's advice cap and block cap, the count instance and the composed statement;
- satisfiability witnesses for every hypothesis, and a joint witness of the composed statement with a reacting operator
  (`joint_witness`, `joint_witness_bound`).

The red team's statement review (`internal/network-transparency/lean-statement-review.md`) asked for the fixed-M bound
at the warden and recommended the joint witness; both are in.

**Model details.**
- Acceptance is modelled separately from emission, and no violation policy appears: every theorem is about accepted
  runs.
- The model's `none` slot is padding on the wire, so constant rate needs no change to the counting.
- The clock-sync form is the advice cap with the advice type `Ac × Σ_sync^windows`, as the named corollary
  `encard_accSeqs_le_sync`.

**Not formalized:** the Shannon form, the unbound count, the logical schedule's arithmetic (a Program definition, not a
theorem), and J, which is tested rather than proved.

## 6. Fitting the protocol pattern and the vLLM options

**The package.** `protocols/network_warden` (`verity_network_warden`, draft
[PR #326](https://github.com/danielreuter/verity/pull/326)) imports only the standard library, `verity` and itself, like `sampled_proofs`, `pous` and PoUW ([PR #218](https://github.com/danielreuter/verity/pull/218)).

**A named, versioned `GridScheme`** (`constant-rate/v1`), with pinned vectors, provides:
- its certificate: W1–W6 and J, the pinned theorems, and (T, τ_b, r, B, Q, Σ_sync);
- the admissibility of a grid;
- the logical schedule;
- the leaf encoding;
- the coverage reasons.

**Lifecycle.**
1. **Registration**, before the window: the grid parameters, the Program's projection of its ordered returns, and its
   logical schedule.
2. **The grid:** the warden's record (grid, σ).
3. **Advice:** the window's (δ, ρ), committed before any challenge that draws units feeding that grid.
4. **Check:** exact equality of every slot, with no sampling, by the verdict deadline. A violation is recorded and the
   run rejected.
5. **Output:** §2.6's fields, on accepted runs, with the violations listed.

The integrity term reads `verity.proofs.profile.IntegrityProfile` from the core.

**As a vLLM option** on [PR #311](https://github.com/danielreuter/verity/pull/311)'s scaffold:
- `network:constant-rate/v1`, with a fourth adapter, `protocol_options/network.py`, whose `keeps_weight_copy` is
  False.
- **The shaper.** One `Service` on the response path is a constant-rate shaper implementing the logical schedule. It
  holds each frame until its bucket e(k), and it declares the window's (δ, ρ) as advice. In CPU tests it also stands in
  for the warden.
- **Methods.** `commitment()` carries the grid parameters, the projection and the schedule. `outside_program` is set
  until the Program emits the grid.
- **Install order.** Outermost, after `sampled-proofs`.
- **Challenge order** (PR #311's question 4): each window's (δ, ρ) must be committed before that window's sampled-proofs
  challenge.

## 7. Decisions for Daniel

**Decided:**
- **Packing:** left-packed.
- **Parameters:** fixed by the protocol from a security parameter.
- **Order:** the Program's canonical gate order.
- **Operating point:** 100 ms buckets, with the allocation r calibrated
  (`internal/network-transparency/calibration-spec.md`).
- **Release:** constant-rate, with clock-sync advice mapping the Program's logical steps to buckets (the design in
  §2.4 is this document's proposal; see A below).
- **Violations:** recorded, and the protocol rejects, as a policy signal. There is no halt, and the bound is on
  accepted runs.
- **Jitter:** a sender can't shift release times (J, tested). The expected distribution is calibrated against honest
  provers on the same hardware.
- **POUS:** its challenges stay inside the spatial unit, so there is no grid constraint.
- **Lean:** stays in the store, movable, while repo-wide Lean organization is planned.
- **D. The ingress grid** (decided 29 Sep, 00:45Z): **100 ms**, with r_in calibrated.
  - *Evidence (§3.6):* at 100 ms a request link costs 0.20% of K per hour since the wipe (4.8% per day), at 199 ms p99
    delivery. r_in is set by the largest request burst, not by τ_in, so a wider bucket is the lever if temporal units
    run for days: 200 ms halves the charge.
  - *The upgrade path, not run:* the per-token trace run of §3.6, which would replace the rebuilt traces. It takes
    about 15 L40S hours and costs $12–16.
  - The grid stays configurable (`--ingress-bucket-ms` in PR #326), so alternatives can still be compared.

**Open,** with defaults:
- **A. The clock-sync advice.** *Default:* one (δ, ρ) per spatial unit per window, from 16 × 8 values, which is
  7 bits per window.
  - One clock per link costs 4× the bits, but lets links drift independently.
  - Per-session rates cost more bits, but cut latency for fast sessions.
  - A fixed (δ, ρ) costs 0 bits, with worst-case latency and more honest misses.

  The ranges come from calibration.
- **B. Relating the bound to K.** *Default:* the ontology's decision 7. An IU is charged the ingress covert capacity
  across ∂X from the last wipe before it starts to its end, plus X's unaccounted memory just after that wipe. Egress
  is not charged to K. For an IU inside one temporal unit, this is the former default restricted to ingress, plus what
  survived the wipe. The alternative is to cap IU lifetime, which tightens the charge only once memory exhaustion
  covers X.
- **C. Window length.** *Default:* 1-minute windows for re-syncing, reported per temporal unit. Shorter windows adapt
  to load faster but spend more advice bits: 7 bits per window.
