---
id: 20261004T2202Z-report-relay-docs-project-context
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/project-context.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/project-context.md`, sha256 `14c0d115870079113b8f179e962672c01542afeddea6516b1b7af62cef1624e2`, last written 2026-10-01T02:00Z, after the 30 Sep snapshot `art:8bd64630…42e9`, whose copy may differ. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# POUS project context

Stable goals, constraints and decisions. Status lives in [notes](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/notes.md).

## Goal

Proof of useful space for model weights: a trusted encoding of static weights that a GPU server must actually store (at least 18/19 of it), decodes publicly and bit-exactly on every use, and costs at most 2× the plaintext matmul sequence. Target statement: [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md).

## Decisions (Daniel)

- **Timing is allowed** (27 Sep): responses have a per-answer deadline, target around 1 ms or tighter.
- **Perfect isolation for now** (27 Sep): no outside help during an audit; locality is a later relaxation.
- **Code home** (27 Sep): `protocols/pous` in the Verity repo, following Verity's `AGENTS.md`; Lean beside it in Flock's conventions, audited and merged through Verity's research coordinator.
- **Two workstreams** (27 Sep):
  1. **Secure P3 end to end:** implement the current construction conservatively (serious primitives even if slow), with full machine-checked security proofs, working end to end, then integrated with Verity's vLLM integration. Performance doesn't matter for this workstream (Daniel, 14:58 UTC): choose parameters for security margin.
  2. **More efficient cryptography:** research new constructions that reach the 2× cost target.
- **GPU budget** (27 Sep): $100 for 14:30–17:30 UTC measurements.
- **Adversary hardware** (27 Sep, 15:06 UTC): a CPU core or a GPU core sets the adversary's sequential step time, not an ASIC. For sequential work the CPU is usually faster (58 ns vs 288 ns per light 4-round ARX hash).
- **Strict answers** (27 Sep, 15:06 UTC): every audit answer must be on time; no tolerated late answers. Δ is set from measured honest tails (prior strict single-probe policy ≈ 300 µs).
- **vLLM composition (29 Sep 00:07Z):** hooks are centralized in the integration where useful, and each protocol manages its own challenges; the embedding is not wrapped under POUS yet; PoUW never keeps a resident weight copy beside POUS (per-forward, from the no-copies rule).
- **Sampled proofs with other protocols (29 Sep 00:15Z):** POUS + sampled proofs is of record, with no circuit change (bit-identical). PoUW + sampled proofs: yes, with PoUW's own modeled circuit; there is no verification lottery (unlike Pearl), sampled proofs is the verifier. Resident PoUW weight copies: closed.
- **Naming (29 Sep 00:07Z):** the network transparency package is `network_warden` (not `network_timing`), for now.
- **H-1T weight layout (29 Sep 01:21Z):** option (a): the served FP8 weights are stored once pre-tiled with H-1T's tag rows (+10.3% weight memory, one-time re-layout, no copy), only when FP8 PoUW is switched on, never as a default. The optional β = 1% registration gate is not adopted.
- **PoUW sampled-proofs sizing (29 Sep 03:16Z):** δ = 2⁻⁴⁰ for now, ε = 0.1%; no recompute exception (03:03Z), strip generation proved as sampled units ([PoUW under sampled proofs](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/sampled-proofs-circuit.md) §12).
- **PoUW sampled-proofs circuit rulings (29 Sep 03:22Z):** tile draws sized by work (with an integrity floor); in-circuit tile-local noise with the per-call two-level key; online verifier accepted; keep the conservative leaf hash (security over efficiency for now); batch-invariant serving with regeneration instead of retaining activations; serialization point left to the designer's most elegant choice; width rule (04:35Z): keep the strict partition with Z in the tile; Z is the separator to the served output, so by Draft 2's Lemma 4.7 and Theorem 5.4 no unit behind it needs a width exception.
- **Lean-first protocols (29 Sep ~03:05Z):** implementations (Python) only match vectors generated from the Lean spec; they don't call compiled Lean (except possibly the verifier's decision). Syncing norms in [Lean-first protocols](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-first-protocols.md). Daniel's three tiers (29 Sep 05:04Z): no Lean proof, proof without mechanical connection, proof mechanically connected; tier 1 is fine in exploratory code when it serves velocity, tier 2 fine for many applications, tier 3 the eventual target (replaces the "pins about the executable spec" question).
- **PoUW vLLM adapter #315 (29 Sep 01:37Z, via Verity root):** merge now as an opt-in, clearly labelled placeholder that is not auditable yet; the label stays in the description, the README and `info()`.
- **FP8 transcript binding, audit A6 (29 Sep 01:37Z):** choice C: no binding for FP8 PoUW for now, which stays research, while choice B (H-1T only: tensor-core accumulation with an FP32 add every 4 steps, bound by an integer mix) is tested on CPU and by capture C2 in Round 11.
- **Network warden ingress bucket (29 Sep 00:45Z):** 100 ms is good enough for now (51 bit/s covert rate, 4.8% of K per day on the rebuilt traces); no definitive trace run.
- **PoUW ownership (30 Sep, 5:52 PM PDT, via compute-accounting):** every old PoUW worker takes orders only from compute-accounting (bc-e90634dd); this chat (@old-accounting) is an advisor that relays pointers, not orders. Goal-critical jobs post a READY line in research-notes `lanes/accounting/` at least 20 min before their mark, and a worker with no progress for 30 min is flagged.
- **PoUW migration (30 Sep, 6:55 PM PDT, via compute-accounting):** no PoUW work runs in this Project any more; replacements in compute-accounting's Project take over kept work from each old worker's migration handoff, and this chat stays an advisor that answers questions, wakes nobody, and stops an old agent's turn only on a compute-accounting stop order naming its replacement (nothing deleted).
- **PoUW rulings (30 Sep, 5:52 PM PDT):** the keyed V/O rotation plus head interleave is adopted for Pearl-C4's registered weights, inside the 8-block rotation only and never on an unrotated checkpoint; RowSeed's per-row draw condition is a named Lean assumption (a Prop taken as a hypothesis); GLM 5.3 writes W1's off-pipe microbenchmarks, and the assessor rates `w1-complete/sm120` from the result.
- **What "full security proof" means here:** machine-checked in Lean in the random-oracle and ideal-permutation model, under the timing and isolation assumptions; instantiating H and P with concrete primitives is a heuristic step outside the proof.

## Proof hygiene (coordinator rule, 27 Sep)

- Every named hypothesis in a Lean chain must come with a Lean satisfiability witness before anyone calls it non-vacuous. Degenerate instances (n = 0, k > n, tiny Q) need explicit side conditions. This rule exists because `DecodeHyp3` turned out unsatisfiable after passing review.

## POUS MVP (Daniel, 28 Sep 03:44Z)

- Freeze the band d = 12 result as the MVP: proved end to end, benchmarked, written up, for handoff to a colleague the next day. One agent owns it.
- It is the first implementation of a generic POUS protocol interface (like `protocols/sampled_proofs`), so other implementations share one harness and dataset.
- vLLM integration: default yes, coordinated with Verity's vLLM coordinator.
- Scope (03:51Z): the headline is the one-segment concrete-H band proof, with 14 GB as the next item. The public encoder is a short write-up section (same guarantee, proved), not a separate implementation. The interface is a fully generic Python protocol with abstract interfaces, and vLLM enables it as an option; each scheme implements a few methods. The write-up is a Notion doc only.

## PoUW MVP (Daniel, 28 Sep 03:55Z)

- Same package as the POUS MVP: a generic Python PoUW protocol with abstract interfaces, and two implementations, Pearl's published protocol and our NCP. Both are integrated with vLLM as options and benchmarked on the same harness. Write-up: Notion.
- The POUS and PoUW vLLM options should share one pattern: a weight-decode hook for POUS, and a hook on every matmul for PoUW.

## FP8 PoUW lane (Daniel, 04:36Z)

- A floating-point (FP8) version of PoUW, in the first batch of inefficient but highly secure prototypes. It may degrade the model by up to +10% perplexity and run 3–5× slower or more, but compute must be sound (γ ≤ 1%). Pearl's FP work, from its whitepaper and PR #311, is prior art.
- **Meaning of FP8 PoUW (Daniel, 28 Sep 13:25Z):** the prover must get useful FP8 matmuls out of the work, so the check must cover the FP8 matmul itself, not an integer path. Integer NCP with FP scales (branch E) does not meet the goal; it stays in the PoUW MVP only as an int8 scheme. Defaults confirmed 13:32Z: E4M3 inputs, the tensor cores' native FP32 accumulation, H100 or RTX 4090.
- **FP8 scope (Daniel, 13:46Z):** only matrices of dimension 4096 and above; γ < 1% is firm.
- **FP8 strategy (Daniel, 14:02Z):** several parallel tracks that talk to each other; try the 4096³ routes first, and fall back to 8192³ and above if they fail.
- **Protocols on main and in vLLM (Daniel, 16:28Z and 16:33Z):** the POUS and PoUW protocol interfaces go on `main` and into vLLM now, with placeholder security acceptable. vLLM must toggle PoUW, POUS and sampled proofs independently and compose all three, using shared infrastructure coordinated with the vLLM coordinator.
- **FP8 quality budget (Daniel, 17:24Z):** relaxed to at most +20% perplexity. γ < 1% stays firm.
- **Network transparency (Daniel, 17:41Z):** a new experimental branch. Assume an active warden against physical-layer steganography. The timing channel is the core threat, so prove its covert capacity under the assumption that the warden does bucketing. Establish a minimal, pruned ontology and roll out only those terms.
- **Network grid decisions (Daniel, 19:18Z):** the protocol sets the grid parameters, derived from a security parameter; the warden only executes them. The Program's canonical gate order fixes the release order. Operating point for now: 100 ms buckets, with the slot count chosen to support honest inference. The vLLM integration should ship a calibration for it.
- **Network decisions, round 2 (Daniel, 19:33Z):**
  - Packing is left-packed.
  - Release is constant-rate: a constant bandwidth allocation per link, with a cap. Timing advice is still needed, to sync the logical and physical clocks.
  - POUS challenges come from within the spatial unit and stay isolated there, so they don't cross a wardened link.
  - Jitter is calibrated against honest provers on the same hardware, which gives the expected distribution.
  - On a violation there's no halt: it's recorded and the protocol rejects, as a policy signal for now.
- **Terminology (Daniel, 19:33Z):** "compartment" is retired. Use his spatial unit (machines behind network wardens) and temporal unit (a spatial unit's computation between two wipes). "Claim" reads as stale; prefer the repo's existing terms, such as `IntegrityProfile` and the README Glossary.
- **Lean organization (Daniel, 19:33Z):** plan repo-wide how Lean is organized and what its CI checks, keeping hygiene and elegance. One option: research and older results live elsewhere (perhaps research-notes), and only "prod" proofs ship in Verity.
- **Hardness-shaped matrices for PoUW (Daniel, 17:45Z):** a new workstream. Require the model's matrices to have properties that make matmuls hard to shortcut, projecting A and B to nearby A′ and B′ at small quality cost, since models are noise-robust. Focus on PoUW for now. Daniel's draft framing (the OS model plus hardness training) isn't committed.
- **H-1 hardness route (Daniel, 19:51Z):** adopt the registration check on committed weights, with two blocks and the hybrid floor. Y16 input (19:54Z): reasonable but gerrymandered, so avoid it if possible; X_q is the target. Proving `DistinctLive(0)` in Lean to drop the γ₀ = 1/400 allowance (19:54Z): pursue it, via a bit-exact Lean model of the H100 FP8 accumulator.
- **FP8 deployment rulings (Daniel, 20:31Z):** no extra weight copies (FP16 or FP32); an offline wider copy is not "free", it's an unacceptable deployment requirement. ptxas ≥ 12.9 for the honest kernel is fine. The 16384³ security claim stays the target for now. Daniel is concerned that other agent-made decisions impose nonstandard deployment requirements; an audit is running. Accepted (20:32Z): NCP's ~3× arithmetic and 394× hashing; POUS-in-vLLM's batch-invariant GEMM, deterministic fused kernel and segment-sized decode; constant-rate release's padding and ~1 s first-frame latency; the FP8 routes' registered amplitude table and per-column weight scales. Correction (20:45Z): the amplitude table is 2 bytes per weight, the size of an FP16 copy; re-asked Daniel whether the no-copy ruling covers it (recomputing it costs 32–96 units per weight element).
- **PoUW shape frontier (Daniel, 20:40Z):** every PoUW result is reported over 2048, 4096, 8192, 16384 and 32768. 65536 is dropped, because no real weights are that large. Runs can iterate one size at a time.
- **Colleague handoff layout (Daniel, 19:49Z):** one overview page with PoUW and POUS sections. Each section has a problem statement (the old POUS one assumed a trusted party and is stale) and a subpage per mainline solution with a 1–2 sentence blurb. Protocol notes run core idea, then security (what's proved, under which assumptions), then performance, then details.
- **P3 superseded (Daniel, 20:49Z):** P3 is dominated by the band (about 2× the hashing per byte, no proof when the server encodes itself, its code runs 132 challenges against the proof's 106), so it is dropped from the colleague overview's tables; its subpage stays as a record.
- **PoUW headline size (Daniel, about 20:55Z):** every PoUW headline number is reported at one size, 8192³ ("8000 is ideal"); results at other frontier sizes go in notes.
- **Honest baselines and prefill/decode (Daniel, 21:40Z):** Pearl is reported at 8192³ like everything else, as its code runs, with no cherry-picking; Daniel asked whether prefill and decode should be reported separately for PoUW and POUS (decode timings being gathered).
- **NCP display names (Daniel, 20:52Z and 20:57Z):** in colleague-facing docs the int8 noise-cancelling construction (`ncp-v1`) is NCP-INT and the H100 FP8 route (D-3s, PR #295) is NCP-FP8; code and store docs keep `ncp-v1` and D-3s.
- **FP8 useful work (Daniel, 16:22Z):** the clean BF16→FP8 activation conversion (scale and cast), which every FP8 deployment does anyway, counts as useful work. Converting the noised copies stays PoUW overhead. Weights are converted offline once, as in normal serving.

## Overnight objectives (Daniel, 30 Sep 04:51Z)

- **Scope:** PoUW only; PoUS is out of scope tonight. Landing already-granted PRs continues, coordinated with the research coordinator. Keep the system lean.
- **Two quantities per protocol:** γ is the security property and must be at most 1%; slowdown is the performance characteristic. Find a panel of protocols at γ ≤ 1%, then hillclimb slowdown, ideally to zero. 5× is only a pass line. Pursue the 2–5 most promising candidates, aiming for total victory by about 3 Oct.
- **Assumptions:** protocols may rest on different assumptions, and we hillclimb on those too. One theory workstream keeps a table of precise assumptions (monikers, parameters). Protocols are Lean-proved secure under combinations of those assumptions. An independent red team attacks each assumption on the GPUs and rates it. Tables grow by adding rows.
- **GPUs (Daniel via Verity root, 05:05Z):** PoUW gets **vy-nebius-2**, an 8× RTX PRO 6000 node in uk-south2 (Kueue queue `pouw`, all 8 GPUs on node 2, never lent out while we benchmark).
  - Ready 05:40Z: `research@81.85.2.121` with the research key. Clocks are locked node-wide at 2,100 MHz, and only the Nebius owner changes them. Use `/workspace/pouw` (network SSD, no local NVMe). **The VM stops itself at 2026-10-07T14:55Z** (Daniel extended the hard stop to 2026-10-07T15:00Z on 30 Sep).
  - Shared infra landed on `main` ([PR #478](https://github.com/danielreuter/verity/pull/478)). Urgent pings go on [PR #485](https://github.com/danielreuter/verity/pull/485), everything else in research-notes `lanes/nebius-infra/`.
  - Verity root's launch worker owns all Nebius resource creation; we create none.
- **Server operations (Daniel, 06:53Z):** pous and Verity root are fully in charge of their servers. That means OOM handling, backups, visibility and effective use, with Kueue and SkyPilot where useful. Node 2's ops lane owns it and reports in the [compute plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/compute-plan.md).
- **Approved weights (Daniel, 06:11–06:13Z):**
  - He likes the approved-weights fork: weights bound to a registered checkpoint by hash, noise on activations only. The open question is what properties registered weights must have.
  - Destructive properties are fine, because training can recover performance. Randomly drawn weights are the strongest option; walk from there toward useful weights.
  - The hope: every weight vector, adversarial ones included, is close to one that is much better for verification and not much worse in loss, and search finds it. Owner: [approved weights](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/approved-weights.md).
- **Theme of the night (Daniel, 05:59Z):** pous and Verity root teach each other how to use the server and share infrastructure, so code doesn't drift, without coupling the projects tightly. His suggestion is a shared infra branch everything branches off, with coordinated merges. Squeeze all the research value out of the compute: full utilisation and a constant search for new efficiencies. The agreed rule and the hourly utilisation go in [compute plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/compute-plan.md).
  - RunPod pods (`vy-pouw-rtxpro-`, $25) are only a bridge until the node is up.
- **Morning deliverables:**
  1. Plots of slowdown over optimization attempts at fixed security, at the 8K headline, split into prefill and decode. The x-axis is attempt number, the y-axis is slowdown, and each protocol gets its own coloured line. A new protocol version in the same family (v1, v2, v3) gets its own line, so kernel wins stay separate from cryptography wins.
  2. The assumptions table with the red team's ratings.
  3. Proofs of each protocol's security under those assumptions.

## Morning questions for Daniel (collected overnight)

- **P2 deployment:** see the [deployment memo](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-deployment-decisions.md). (1) The instantiation assumption: default "not yet"; confidence is low against moderate for Feistel-SHAKE, and the memo lists six things that would move it. (2) Cooperating cores: default is to allow cooperation within one chiplet, which means about 28,200 bits at 2.9 ms or 10,400 at 0.5 ms; measuring the verifier's real round trip matters most.
- **POUS MVP:** should the verifier keep refusing an effective D above 5, or scale k with it? Who is the colleague, for Notion access? Where should the Notion handoff page live?
- **FP8 lane (06:23Z):** the lead is integer NCP with FP scales, not genuine FP8, because the FP8 branches are broken by attacks saving 12–32%. γ ≈ 0.69% holds only with the rotation and quantization kept outside the reference work; counting the online Hadamard gives about 1.15%. Four questions for Daniel are in docs/pouw-fp8/design.md §5.
- **FP8 overnight (07:14Z):** with all glue online, γ ≈ 1.37%, which fails. γ ≈ 0.92% only if the producer supplies signs and max values and rescaling is deferred. The optimized pipeline targets 2.21× plain FP8 (from 8.97×). The coarser Hadamard (H2) gives +6.11% perplexity. It is blocked on the route-U checkpoint Lean. Report in docs/pouw-fp8/optimization.md.
- **FP8 on Qwen2.5-3B (07:57Z):** perplexity +9.88% with signed-H2 int7, just inside the 10% budget; the finer Hadamard-128 would lower it but costs more glue γ. Under route S, γ at the 3B's worst shape is 1.335%, which fails; route U (0.887%) is needed and its Lean is in staging.
- **PoUW Theorem 1 (07:59Z):** the quadratic half of A1_cost is now a Lean theorem (`a1CostQuadHolds`, MinRank ≥ 5), so for quadratic closed-pipe FP32 programs TT_NCP follows from A2 alone (`ttNCPQuadOfA2`). Still assumed: A2 (being weakened to checked words, per P9B-1) and A1_nonquad. 156 pins. Tell Daniel in the morning.
- **Correction (09:49Z):** the fixed A2, restricted to checked words, is proved equivalent to per-word TT_NCP (`a2WordsIff`), so the Theorem D chain is not a reduction to a milder assumption. It is proved evidence that no algebraic program class beats 16 per word. The milder route being tried is an embedding theorem: M_4090 as a Lean machine, with FP32 merges as the only residue. Semantic choices get flagged for Daniel. Told Daniel at 09:50Z.
- **GPU account (09:20Z):** the balance is $111.11, falling at $8.07/h on other workstreams, and reaches $60 around 15:40Z. The Verity root has asked Daniel for about a $450 top-up. The POUS/PoUW GPU freeze holds until then.
- **GPU freeze (07:44Z, Verity root):** no new POUS/PoUW pods until Daniel's top-up (about $450, requested by root at 07:31Z) lands. The B200 calibration finishes inside its $8 cap. If the balance falls below about $60, pause pods not mid-measurement and tell root. The non-POUS spend is intended (backend sweep, coordinator checks, M0).
- **PoUW MVP Notion page:** where should it live, and who gets access? Also, the Route U question went to the PoUW coordinator, with the default of redefining checked values as biased sums.
- **Research-notes registry:** should the public APPROACHES.md show hypotheses and kill reasons (full), or titles only (default)?

## Research-notes structure (Daniel, 04:54Z)

- Colleagues will onboard with their own agents in the repo and in research-notes. Enforce structure so parallel approaches aren't duplicated and new agents can see what's been tried. Coordinate the design with the vLLM coordinator and the Verity root.

## Overnight 28 Sep (Daniel, 04:29Z)

- "Tonight's the night to be crazy ambitious." Keep every worker busy overnight, go with the stated defaults on open decisions, keep the benchmark metric frozen, and make no security-changing choices without Daniel. GPU session cap is $200; about $20 had been spent by 04:30Z.

## Worker models (Daniel, 28 Sep 02:53Z)

- Don't use max-reasoning models for workers: they stall. Use extra-high (xhigh) when a task needs deep reasoning.

## Writing conventions (Daniel, 27 Sep)

- No LaTeX in Markdown files: Daniel's viewer doesn't render it. Write math as Unicode (×, ≤, ε, ⊕), with `2^k` and `x_i`, fractions as `a/b`, and longer expressions in code spans or `~~~text` blocks.
- In chat, use LaTeX for math (Daniel, 28 Sep 01:31Z): the chat renders it and plain-Unicode math there is hard to read. Inline \( … \), display \[ … \].

## Proof of useful work (Daniel, 27 Sep)

- A new sibling workstream with the same pattern as POUS: a precise problem statement first, for Daniel to review, before any construction.
- Sources: the Pearl whitepaper, pearl-research-labs/pearl PR #311, pearlpolymath.com, and arXiv 2504.09971.
- Constraints:
  - Get it working end to end at high overhead first.
  - Lean proofs are required.
  - Prefer a safe reduction from standard assumptions over Pearl's conjectures.
  - Restricting to integer matmul is fine.
  - **Hard requirement:** the work gap between an honest prover and the best adversary must be at most ε ≤ 1%. Pearl, even its integer variant at maximally conservative parameters, leaves the adversary a constant advantage.
  - **Security must not come from hashing** (17:32Z): a hash-dominated scheme at ~100× overhead is rejected as uninteresting. The work must be the matmul itself.
  - **Objective is resource exhaustion, not mining:** the scheme runs on every matmul of a workload, taken for now as a standard sequence of integer matmuls, and must hit an assumed or verified lower bound on work. No assumptions yet about hardware compute capacity.
  - **Work unit:** RTX 4090 time; ASICs out of scope.
  - **Verification cost:** out of scope, since random sampling makes it essentially free.
  - **Honest reference:** plain int8 GEMM without Strassen.
- Prior context: `internal/pouw/sparse-verification-note.md` (Daniel's compute-transparency session) and the Notion page "FASR Work Test".
- **Defaults accepted (19:44Z):** tail-bound accounting; worst-case inputs; int7 useful operands; about 130× hashing overhead acceptable for milestone 1 only; TT(0.5%) as the single named hypothesis; RTX 4090 adversaries only. Daniel then said to push the research frontier, so a coordinator now runs the PoUW campaign.
- **New direction (23:00Z):** milestone 1 is KW/Pearl-style low-rank noise and rests on their conjecture. Daniel is happy with full-rank noise and higher overhead, but full-rank additive noise gives the adversary γ ≥ 1/2 at zero inputs (Lemma 1). He wants new cryptography that gets around this, and a campaign is now researching it.
- **Campaign 2 result (28 Sep):** noise-cancelling polarization (NCP) gives γ ≈ 0.51% at the milestone and 0.66–0.92% at 4096² under the new conjecture TT_NCP(0.5%), at about 3× arithmetic and 394× hashing ([new crypto](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md)). Daniel accepted all three (01:23Z): NCP + TT_NCP(0.5%) is the primary construction for transformer shapes (milestone-1 low-rank kept as baseline); ~400× hashing and ~3× arithmetic accepted for the first build.
- **W1 pricing of byte moves (03:35Z):** Daniel chose to price sub-word extraction like PRMT (16 units per word) on both sides, instead of free byte-granular moves. Under it, the FP32 conjecture A1 in [milder assumptions](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/milder-assumptions.md) needs c = 2 (margin ≈ 2.7×).
- **Band at 14 GB (05:21Z):** proved at k = 111 (and k = 106), resting on the same `ChainExPostFactoG` as one segment. It requires per-segment tags that are injective across all segments; `shared_domain_breaks` proves a shared domain breaks it. Red-team review is pending. Tell Daniel in the morning.
- **Pipelining answered (05:16Z):** overlapping the next layer's decode with the current matmuls hides nothing (the matmuls are about 1,000× shorter), and at prefill it's 0.8 s slower. Decoding a forward's unique weights once, in one batch, should roughly halve vLLM's 1.33 s per forward. Tell Daniel in the morning; this settles his pipelining question.
- **Decode ceiling corrected (05:12Z):** band decode is memory-bound, not compute-bound. The 1,550 MB/s on the 0.5B is near the practical ceiling for the frozen scheme on an L40S. The ~2.5 GB/s figure given to Daniel was the INT32 ceiling at full occupancy, and is unreachable. Tell Daniel in the morning summary.
- **A1 restated (05:10Z, coordinator):** with free additions, A1(2) is probably false for large m and n (Brockett–Dobkin), and the best verified algorithm gives only a 1.7× margin. A1 is now stated in W1's own cost model, with FP32 adds at 8, where the known margin is about 5×. The precondition is MinRank ≥ 5, and MinRank = 16 is certified. Tell Daniel in the morning summary; this corrects the 2.7× figure he was given.
- **A1_cost proved on paper for quadratic FP32 programs (05:40Z):** every multiply is of two affine functions of the noise, which covers every known algorithm. Such programs need at least 2·dim V instructions, with only independence and MinRank ≥ 3 assumed. General FP32 programs are still open (only half the target is proved there). Red-team review is pending. Tell Daniel in the morning.
- Deliverables go in `docs/pouw/`.

## Hardware budget (Daniel, 27 Sep)

- **22:06Z sweep:** no POUS pods were running. Spend from worker tallies: $5.49 on the vLLM demo and benchmark, $3.03 on measurements, $0.51 on PoUW, and $0.01 on the Zen 5 run, about $9 of the $200 cap.

- Doubled to $200 total for the session, with pods allowed until 20:30Z. Split: $120 for the vLLM end-to-end demo and $80 for measurements.
- Terminate any idle pod immediately, without asking.
- **Guards (coordinator rule, 28 Sep 23:58Z):** every pod starts a kill timer on the pod itself at the session's hard limit, and runs under root's fleet guard. A guard on a worker VM alone isn't enough: the band run overran its $1.50 cap by $0.50 while its worker VM was suspended.
- The demo uses a small open model of about 0.5B parameters on an RTX 4090 or L40S.

## Priority (Daniel, 27 Sep)

- Get a working end-to-end system first, with security proofs, and accept poor performance. The 2× decode-cost rule and the timing-margin tuning are deferred ("I don't care about the 2x rule for now").

## Scheme for the end-to-end build (Daniel, 27 Sep 19:09Z)

- **The dense single-layer scheme is the secure-first end-to-end scheme,** because its proof has no open research step. P3 stays behind the same codec interface as the fast research track; its proof is blocked on adversarial inverse queries. Rationale: [scheme-choice memo](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/scheme-choice-e2e.md).
- Daniel wants a real throughput benchmark: prefill and decode tokens/s against plaintext vLLM. Benchmarking method (19:52Z): use a small model (Qwen2.5-0.5B) for fast iteration, with batch sizes as if the model barely fit on the GPU (decode at batch ≤ 32, prefill at batch 1–4), so batching doesn't inflate the win. Also report the time per forward pass to decode all weights, so results extrapolate to larger models.

## Secure-first scheme: band graph, d = 12 (Daniel, 01:10Z)

- The secure-first scheme switches from dense to the band graph with d = 12 parents (B = 512, 64 KiB labels, D = 5, k = 111), proved as secure as dense for d ≥ D (`lean/submissions/band-chain/`). Decode is about 20× cheaper: 12.85 calls per block against 256.5.
- Deployment condition: the effective D must not exceed d. The band has a cliff beyond that; see [band vs dense](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/band-vs-dense.md). Dense stays as a selectable codec.
- Its security for the real hash rests on the DAG-generic `ChainExPostFactoG`, now in progress. The switch is contingent on the red team's §40 verification.

## PoUW milestone-1 decisions (Daniel, 01:10Z)

- W1 is the cost model, milestone 1 keeps worst-case inputs, and checking is at depth 16.

## Public encoder (Daniel, 23:43Z)

- A new workstream replaces the private encoder, where the verifier encodes, with a public one. The reading, confirmed by Daniel at 00:06Z: the untrusted server encodes, and the verifier gets trustworthy check data from a public proof that the encoding is correct, without re-encoding. Same rule as elsewhere: build the most secure version first, with Lean proofs, then optimize with security fixed. Deliverables go in `docs/public-encoder/`.
- **Answers (00:16Z):**
  - Milestone 1 is the full decode check.
  - No third-party verifiability.
  - Setup error is charged to ε (default).
  - φ is moot until sampling, to be explained plainly then.
  - The verifier holds only the W commitment.
  - The band-graph idea goes to the red team, and promising alternatives get compared.
  - No SNARKs.

## Dense optimization benchmark (Daniel, 23:18Z)

- The benchmark runs on one L40S with the scheme frozen, so only the implementation changes. The main metric is effective weight bandwidth: plaintext weight bytes consumed per second by matmuls of vLLM's shapes, at decode batch sizes. It uses a standalone matmul microbenchmark rather than vLLM, since decoding is more than 99.9% of the time. vLLM runs only at milestones. The spec goes in `docs/dense-decode-benchmark.md`.

## Coordinator choices (revisable)

- **Secure-first P3 point** (27 Sep): band graph k = 12, n = 220, two layers, 64 KB labels, wide-sponge H (state ≥ label + 512 bits, newest-parent-first), separate 64 KB permutation P, sequential reveal with strict Δ ≈ 300 µs. 64 KB rather than 32 KB so the margin holds even if "GPU core" means a multi-SM cluster. Details: [P3 scheme](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md) §2c.
- **Concrete P3 assumptions** (red-team §19, 27 Sep): SHAKE256 behaves as a random oracle, so the Keccak permutation is treated as ideal. The ideal-cipher indifferentiability of the keyed Feistel network is assumed to carry into P3's storage game; this is a named composition assumption (Ristenpart–Shacham–Shrimpton), argued but not proved.
- **Tweakable P** (27 Sep): P_t with t = (segment tag, layer, node). Proofs need only single-entry deletion (no Lehmer library), and 14 GB targets k ≈ 144.
- **Server-side encoding** is allowed: server commits to W, verifier then draws the salt and computes vk from its own encoding.
- **Lean lock order favours FP8** (30 Sep 14:45Z): the salt-dead fix and rev2's salt-dead delta run at priority 2, right after `Fp4Skip.dead`, so M1 and M2a (FP8 headline pins) land before rev2's v2-hot build and the FP4 builds; FP4 waits on the verifier enforcing its fix anyway.
- **vLLM integration goes through one linear-site interface** (30 Sep 16:17Z, Daniel): `LinearExecutor` plus optional `WeightSource`, combined by one `Stack` per rank; scheme names, hashing formats, schedules and kernel variants are data in `verity_pouw`, with kernel types in `verity_pouw.serving`.
- **No external kernel platform** (30 Sep 16:17Z, Daniel): the harness records every attempt in the evidence store, which becomes the panel's source of truth after a one-day pilot.
- **Pearl-C4 covers NVFP4 only** (30 Sep 15:34Z, Daniel): MXFP4 fails honest coverage under the fix on every model size, so it stays as a comparison line only.
- **FP4 panel lines stay off headline plots until the verifier enforces F1′+F2** (30 Sep 14:40Z): the assessor's C for `tt-out/fp4-sm120` assumes the verifier replays F1′ and F2 and rejects tiles over 1/400, so FP4 lines are unflagged at C only after a verified row is re-measured under the fix.
- **ε₈ on the joint condition** (30 Sep 13:55Z): the fragment rate is stated for blocks whose pre-adds are exact on both operands over the same k pairs, with per-side counts reported beside it; revert to per-side if the assessor finds a one-sided route that profits.
- **Research-notes naming for RC and Verity root** (Verity root, 30 Sep 13:40Z): `research notes inbox` lists only `*handoff*`, `*asks*` and `*reply*` files, so every merge request or note to the research coordinator or Verity root is named `-handoff-`.

## Still open (Daniel)

Exact Δ (from measurements); `pp` size and ε bound (provisional: |C| ≥ |W|, ε ≤ 2^-128); reveal mode; band-graph parameters (being re-chosen for the timing model); public notes stay pointer-level.

## Key documents

- [P3 scheme](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md), [P3 cryptanalysis](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-cryptanalysis.md), [construction paths](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/construction-paths.md)
- [Lean trusted layer](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-trusted-layer.md) and its [review](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-trusted-layer-review.md)
- [POUS audit](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pous-audit.md) (prior work)
- Agent coordination across Projects goes through Slack (compute workspace): handles are user groups, #agent-coordination is the front door, each service agent (infra, console) owns a channel with a pinned contract, subscriptions are top-level only plus threads you join; norms live in the `using-slack` skill (30 Sep 17:50Z).
