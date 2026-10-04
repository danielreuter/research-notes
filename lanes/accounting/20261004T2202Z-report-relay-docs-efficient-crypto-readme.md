---
id: 20261004T2202Z-report-relay-docs-efficient-crypto-readme
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/efficient-crypto/README.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/efficient-crypto/README.md`, sha256 `10c2f30185893aa60472779dd0e6782442e0bc35c5c3b644d6f976664c552b6d`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Efficient cryptography for POUS (workstream 2)

Started 27 Sep 2026, 14:39Z; plan revised at 15:00Z after Daniel's [prior GPU notes](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/prior-gpu-notes.md), and re-gated at 15:10Z
on Daniel's single operating point. Goal: an encoding that
decodes at **≤ 2× the plaintext matmul sequence at decode batch** (b ≤ 8, H100) and meets the timed audit game of the
[problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md), with a security argument the [Lean trusted layer](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-trusted-layer.md) can check.
Workstream 1 (secure P3 end to end) is separate.

## What the target really is (revised 15:00Z)

**Timing (Daniel, 15:07Z).** The adversary is a CPU core or a GPU core, not an ASIC, and answers are strict, all on
time. A CPU core runs a light hash (one 4-round injection-ARX evaluation) in 58 ns, and honest tails need Δ ≈ 300 µs,
so the adversary gets **D ≈ 5,200 sequential light-hash steps per answer**. P3's certificate assumed D = 20 oracle
rounds (Δ ≈ 5 µs) and holds only up to about 11 game levels. Every candidate has to pass a regeneration-depth gate at
this point. For calibration, the shipping drU stack fails at 64 KB, and a window attack (16:41Z) also breaks its 4-layer version at
128 KB (D* = 3,099). Stacks need at least 5 layers at 128 KB (D* = 7,193).

**Narrow-state compression (suspected, from workstream 1).** A label wider than the internal state of the function
that produced it compresses to that state, and so does (small-state function) ⊕ (known data), since `W` is free. This
is the Ristenpart–Shacham–Shrimpton limit for storage games. Every candidate with keys from a narrow-state hash, a
short digest or an expanded seed must be checked against it.

**Cost.** Measured on H100: at B = 8 fused, 2× means decode at about 1.2–1.3× memcpy. That is **about one layer of the
shipping drU stack** (a 6-parent gather plus 4 double rounds of ARX on 32 B chunks). Sound stacks need at least 4
dependent layers, and parent gathers are about 58% of a layer. The previous campaign measured the stack at 4.52× and
found no sound DRG point at ≤ 2.2× for B ≥ 8.

**What that leaves.** A sound design needs regeneration depth beyond D with a 5.26% deficit, at about a quarter of a
drU layer per dependent layer (or fewer dependent layers). The levers still open:

- cheaper per-layer work: fewer parent gathers (rolling or register-window structures), fewer rounds, keys that don't
  need a hash;
- structures that need fewer dependent layers for the same depth;
- regimes that amortize decode;
- a primitive whose re-encode direction is inherently slower than its decode direction.

Tensor-core mixing is no longer one of them: it was measured slower.

## Operating point every memo reports

One CPU core at 58 ns per light hash, Δ ≈ 300 µs, all answers on time: **D ≈ 5,200 light-hash latencies**, scaled by
the candidate primitive's CPU latency relative to a light hash. The ASIC and tolerated-miss points are dropped.

## Pipeline and gates

1. **Generate.** Workers write candidate memos (spec, cost priced against the measured drU cost surface, regeneration
   depth at D ≈ 5,200, the narrow-state check, security sketch, self-attacks, kill check).
2. **Attack.** A *separate* cryptanalysis agent attacks each promising candidate. No proof work starts before a
   candidate survives.
3. **State.** For survivors, a worker states the claim against the trusted layer's definitions under
   `lean/submissions/efficient-crypto/<candidate>/`. A red team reviews the statements before any proof. Pinning in
   `lean/pous` goes through the root coordinator.
4. **Prove.** Provers target the reviewed statements until the grader passes; the result is written up here.

**Kill criteria** (details in the [worker brief](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/campaign-brief.md)):

- **Cost (revised 15:45Z, while Daniel defers the 2× rule):** a candidate must be materially cheaper than workstream 1's
  P3 at the same primitive assumption *and* have a proof path. 2× stays the recorded long-term line. Price gather-heavy
  designs with the measured drU slope, not the ARX table (brief, 15:45Z correction). Reference points:

  | Reference | Primitives | Decode batch | Prefill |
  |---|---|---|---|
  | [P3 instantiation](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-instantiation.md) (the baseline) | SHAKE256 Feistel `P` and wide sponge `H`, standard assumptions, 64 KB labels | ≈ 2,000× | ≈ 85× |
  | P3 §2c | heuristic wide ARX permutations, 64 KB labels | ≈ 26–50× *est.* | 3–4× *est.* |
  | (5,6,4) stack at 128 KB (16:41Z; the 4-layer stack fails the window attack, D* = 3,099) | injection-ARX; attack-based, no proof; margin 1.38 | R_seq 8.5–9.2 *est.* | ≈ 1.2× |

  Memos state which assumption class their primitives are in and compare like for like.
- **Depth:** the best 5.26%-deficit strategy regenerates the dropped data within D ≈ 5,200 light-hash latencies.
- **Attack:** a saving above `n/19`, one that makes `γ` vacuous, or a label that compresses to a narrower state.
- **Proof:** no route to an ideal-model or named-hypothesis statement in the trusted layer's style.
- **Realism:** something the H100 fused kernel can't do, or a result already settled in the prior notes §5.

## Threads

| Thread | Status after the 15:10Z re-gate | Agent | Output (in `internal/efficient-crypto/`) |
|---|---|---|---|
| Cheap keys (merge the key hash into `P`) | **Killed (16:27Z)** at D ≈ 5,200: stored keys are linear equations (see Dead ends); parked only as a prefill cost lever, which is deferred with the cost rule. Earlier status: **Narrowed.** It must beat the measured per-layer cost, where gathers dominate, not P3's formula. It must also block the per-parent reverse move: invertible keys cost the old stack 12–28% without feed-forward. It moves to D ≈ 5,200. Full-width linear keys pass the narrow-state check by construction; the variant with a tweakable `P` keyed by a short parent digest is expected to fail it (P3.1's short-digest attack). | [designer](https://cursor.com/agents/bc-53389883-0c24-5d61-b990-08c35f71d303) | `candidates/linear-keys.md` |
| Soundness of cheap keys (independent) | **Reported 16:41Z.** Plain XOR and per-edge linear keys without feed-forward are unsound (31% droppable at 128 KB with 4 layers, against 11% for hashed keys). With feed-forward `c = P(x ⊕ K) ⊕ K`, no attack it ran beat hashed keys: stored keys moved its attack about 1%. **Settled at full size (17:01Z):** on the 5-layer stack at 128 KB (n = 4,096), the designer's key-storage strategy costs linear feed-forward keys 26.8% of depth against label storage, the same ratio as at n = 256. So feed-forward does not make linear keys free. Both stay above D there, because the window attack binds. (The resume was then stopped by a content filter; its DSaG part is moot after the DSaG kill.) Side finding: a window attack breaks the hashed (4,6,4) stack at 128 KB (D* = 3,099), so stacks need ≥ 5 layers there. Earlier status: **Relaunched 15:42Z** as a new agent. The first cryptanalyst timed out, then was blocked by a content filter on resume; its `attacks/linear-keys.md` is an unfilled skeleton. Plain XOR keys are already dead (see Dead ends). Order: the per-parent reverse move, then random per-edge coefficients at D ≈ 5,200, then the narrow-state check on the short-digest variant. | [soundness evaluator](https://cursor.com/agents/bc-cedb9aac-f2a4-53ad-ad88-49e2d160a7e5) | `attacks/linear-keys-tightness.md` |
| Tensor-core mixing permutation | **Killed; confirmed on cost-benefit (15:55Z).** The designer shows on paper that the serialization can be removed: a warp per 1 KB label, state kept in the MMA fragment layout as the B operand, byte-permute repacking, about 42 registers. But against ARX with the same measured diffusion it gains at most 0.06–0.32× if the pipes overlap, and loses 0.24–1.0× if they add. With hashed keys every variant is ≥ 9.5×. Its GPU overlap test is deferred (no GPU spend), and nothing in the lead candidates hinges on it: P2 is big-integer, where tensor cores save ≤ 1.7× (report §6.3). No cryptanalysis. | [designer](https://cursor.com/agents/bc-3cf9b81c-6f32-508a-8abb-7bd0fbcf9991) | `candidates/tc-mixer.md` |
| Graphs and connectors | **2× kill accepted (15:50Z).** At D ≈ 5,200 no layered configuration with a secure mixer fits 2× under either key model. Bands and register windows fail at any block size, and rolling linear keys collapse bands. Its R_seq column now uses the corrected mapping (16:25Z): the cheapest passing stacks are R_seq 6.1–6.3, and the kills stand. Its provable route is now the wide-label DSaG candidate (row above). | [designer](https://cursor.com/agents/bc-b01b9931-1f34-5b11-afc0-545e8bc87c24) | `candidates/graphs.md` |
| Amortized regimes | **Done (15:15Z).** No regime allowed by the rule as written puts P3 under 2×: every real regime still issues matmuls at b ≤ 20, where fused cost is flat. Only relaxations help (decisions below). Two side findings: P3 measures about 6.7× at decode batch (8.7× with barriers), not 5.8×; and at 64 ≤ b ≲ 500 even a zero-cost decoder measures 2.0–2.6× with today's kernels, a kernel gap rather than a crypto one. | [analyst](https://cursor.com/agents/bc-2d9447a8-649b-5f5c-842e-090375ffc810) | `candidates/amortized-regimes.md` |
| Other primitives | **Screen done (15:47Z): no survivor under the old gates** (kill table in its memo; main kills under Dead ends). Reopened at 15:55Z for SMS/P2 under Daniel's time model; the survivor is now the P2-5504 candidate (row above). | [scout](https://cursor.com/agents/bc-1d695f79-a999-5568-9660-b13841036977) | `candidates/alt-primitives.md` |
| **Candidate: P2-5504 (square–mask–square over a 5504-bit prime)** | **Status (28 Sep, 09:20Z): now at 16,448 bits. It is proved unconditionally in abstract M1, including the MVP's 2^19-block instance. Its two deployment decisions are with Daniel ([memo](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-deployment-decisions.md)).** Overnight push (28 Sep, 04:40Z):
  - **Why 5504 fails now:** under the settled timing (the adversary gets 0.5 ms plus the round trip; the band covers up
    to about 2.9 ms), P2-5504 fails. Its one protecting root takes 493 µs at the floor and about 1.35 ms with our kernel.
  - **The question:** whether a larger prime rescues it at a decode speed that beats the band's 1,532 MB/s on an L40S.
  - **Timing red team (04:57Z): NOT WORTH IT against P3-ARX.**
    - At the floor, 5504 bits is 0.79× of the 0.5 ms deadline.
    - A 2× margin needs 8,000 / 12,592 / 16,448 bits at round trips of 0 / 1 / 2.4 ms.
    - At 16,448 bits, decode is about 258 int32/B (≈ 41× slowdown on H100), about 62–70 GB/s on an L40S *est.* That is
      ≈ 40× the band, but only on par with P3-ARX.
    - SeqRoot has no shortcut inside the model, and exactly one root gates each block.
    - **Fragile edge:** 4–8 cooperating cores speed each squaring 2.3–4.1× and eat the margin; a hash chain can't be
      split that way. (Superseded at 09:20Z: measured 2.13× at 4 cores, modelled 1.1–2.6× at 8; see the deployment
      decisions memo.)
    - Report: `attacks/p2-redteam-timing.md`.
  - **Algebra red team (05:00Z, stopped by a content filter after Q1):** split hints on both roots never beat storing c.
    - Recovering both needs advice of at least w + O(1) bits.
    - Every lattice success at w = 128–256 needed ≥ 1.055w bits; every point at ≤ 1.005w failed.
    - So exactly one root gates each block, which confirms the timing red team.
    - Report: `attacks/p2-redteam-algebra.md` (partial); mask: `attacks/p2-mask-check.md`.
  - **L40S decode (measured, bit-exact, $0.27), M2 schedule (shared mask, linear tweaks), not covered by the proof:**
    51 / 40 / 32 / 27 / 24 GB/s at w = 5504 / 8192 / 10240 / 12288 / 14336, i.e. 33–16× the band's 1,532 MB/s
    (`candidates/p2-gpu-decode.md`).
  - **Verdict (05:30Z): SOUND WITH PARAMETERS at w ≈ 16,448; next step a Lean statement**
    ([P2 verdict](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/p2-verdict.md)).
    - It decodes ≈ 14× the band at that width (≈ 26× at zero round trip). These ratios came from M2-schedule
      measurements; see the 08:45Z correction below for the covered (M1) number.
    - The Lean claim is the pinned M1 model at P2's parameters, from the proved A3′ plus the open A2.
  - **Lean statement proved (05:47Z), conditional only on the pinned open A2, with no `sorry`:**
    - `p2_meets_m1 (hA2 : Pinned.A2LemmaAM1) : ∀ D, Meets (m1 (2^23) 16448) .sequential D (2^20) 88 εMax`
      (17.2 GB), plus an 8,192-bit instance with k = 90.
    - Lean's three axioms only; grades PASS against a scratch pin.
    - Files: `lean/submissions/efficient-crypto/p2/`.
    - Next: pin `P2MeetsM1` (root coordinator), red-team the statement, prove A2.
  - **Overnight, 05:55Z:** running now:
    - [statement review](https://cursor.com/agents/bc-d1405c07-5e8a-5efb-8b66-087d4bf697fe) on a GPT model; its GO gates
      the pin, which the coordinator makes in `lean/pous` with the reviewer named in the pin record;
    - an [A2 prover](https://cursor.com/agents/bc-26d73714-aabb-5bc5-a7ed-04ef3723a2af), which would also close
      `M1Meets`;
    - a [tuned L40S squaring kernel](https://cursor.com/agents/bc-28faaf0e-1769-5ab3-9e90-059d8825884c) under the
      `vy-pous-p2gpu` guard ($9.5 cap total, 09:30Z).
  - **Pinned (06:25Z).** `P2MeetsM1` and `P2MeetsM1W8192` are now in `lean/pous` (35 pins). The statement reviewer,
    `statement-review-p2 / bc-d1405c07`, gave GO WITH CONDITIONS; the pin-text conditions are in the docstrings.
    - Both grade PASS against the real pins.
    - `check.sh`: ALL CHECKS PASSED.
    - `TRUSTED.sha256` regenerated and verified.
    - Record: `lean/submissions/efficient-crypto/p2/GRADE.txt`.
  - **A2 proved (06:28Z; coordinator re-graded PASS against the pinned layer). Proof review (06:41Z,
    `statement-review-p2`, GPT): GO on A2, GO on the `M1Meets` discharge, and GO on both P2 rows** as unconditional
    abstract-M1 results.
    - Only Lean's three axioms, and no kernel escapes in the sources.
    - Nothing vacuous; B1′ for m1 is now a theorem.
    - The existing pins stay implications in syntax. The unconditional results are the direct theorems in
      `lean/submissions/efficient-crypto/a2/`.
    - Review: `attacks/a2-proof-review.md`.
  - **Unconditional pins (07:30Z).** `P2MeetsM1Uncond`, `P2MeetsM1W8192Uncond` and `M1MeetsUncond` are pinned (38
    pins; the implication pins are kept).
    - The same reviewer gave GO WITH CONDITIONS, with its wording in the docstrings.
    - All three grade PASS; `check.sh` passes (audit: 430 declarations); `TRUSTED.sha256` verifies.
    - `docs/lean-trusted-layer.md` is updated: pin count, table rows, one-line statements, and the plain-words scope.
  - **Tuned L40S kernel (07:15Z, measured), M2 schedule (shared mask, linear tweaks), not covered by the proof:**
    44.3 / 24.2 / 15.5 GB/s at 8,192 / 16,448 / 32,768 bits, i.e. 28.9× / 15.8× / 10.1× the band's 1,532 MB/s.
    - Bit-exact on 64,293 blocks.
    - GPU spend $0.80 in total; no pod left.
    - Details: `candidates/p2-gpu-decode.md` § Tuned kernel.
  - **Correction (08:45Z): which P2 numbers the proof covers.** The pinned `P2MeetsM1Uncond` covers only fresh
    per-block keys (model M2 is not covered). The campaign's two GPU benchmarks used the scout's "cheap keys", a
    shared mask K with tweaks `t_j = t0 + j·step`, i.e. M2; so did every GB/s figure above and in the P2 verdict.
    - **The covered number (corrected 14:30Z):** the POUS MVP owner (bc-13eada34) measured P2 v2 at w = 16,448 on
      Qwen2.5-0.5B on an L40S, with fresh per-block keys derived on the device.
      - **Result:** **23.66 GB/s** effective weight bandwidth, about **15.4× the band's 1,532 MB/s** on the same
        workload, with every gate passing. Attempt `r20260928-142137-28ac`.
      - **Against the shared key:** 25.23 GB/s in the same run.
      - **The expander:** ChaCha8. With SHAKE256 it would be about 21 GB/s, if the 12% device estimate holds (*est.*).
      - **On an H100:** 14.75 GB/s with the kernel not re-tuned; device derivation cost nothing measurable there.
    - **Superseded: 25.0 GB/s.** Attempt `r20260928-081028-0c5f` measured 25.0 GB/s against 25.6 for the shared key.
      - **Its checks:** 2,048 sampled blocks with 0 mismatches; timed audit 20 of 20 accepted (k = 88, 500 µs limit,
        honest maximum 7.4 µs); a negative control accepted 0 of 20.
      - **Why it is superseded:** it read CPU-derived keys from device memory, about 2 GB of keys for a 0.99 GB model,
        which is outside the 1.05× space bound.
    - **Caveat 1, space (closed by P2 v2):** the keys are now derived on the device from the seed.
    - **Caveat 2, block count (closed; see "Block-count pins" below):** the run used 2^19 blocks, not the pinned 2^23.
    - **Caveat 1 was owned by the POUS MVP owner**, who has now measured device-side derivation (above).
    - **Other claims that assumed M2:**
      - the scout's cost estimate (14.5–21×, "cheap keys") and its k = 101–102 "M2 bound" (a paper bound; the
        pinned M1 result has k = 88);
      - the timing red team's decode cost (258 int32/B), which counts no key generation;
      - the throughput table in the P2 verdict.

      The Lean pins, the statement review, the instantiation review, the red-team root and hint analyses, and the CPU
      latency numbers are schedule-independent or already specify per-block keys.
  - **Block-count pins (28 Sep, 09:20Z).** `P2MeetsM1B19Uncond` and `P2MeetsM1FamilyUncond` are pinned (40 pins).
    - **What they say:** in abstract M1 at 16,448 bits, with 2^20 queries per answer and k = 88 challenges, the MVP's
      exact 2^19 blocks meet the requirement. So does every block count from 2^8 to 2^23.
    - **The challenge count:** 88 is the least k this proof route gives. At 2^19, k = 85 is refuted in Lean: storing
      as many blocks raw as fit already passes. k = 86 and 87 are open.
    - **Review:** by `statement-review-p2`. GO on the 2^19 pin; GO WITH CONDITIONS on the family, whose wording fixes
      are in the docstrings.
    - **Checks:** both grade PASS on Lean's three axioms, and `check.sh` passes.
    - Files: `P2Rows.lean` in `lean/submissions/efficient-crypto/a2/`; record: `.../p2/GRADE.txt`.
  - **Deployment decisions (28 Sep, 09:20Z):** a
    [memo for Daniel](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-deployment-decisions.md).
    - **Instantiation:** the recommended default is not to accept it yet. The band stays deployed, and P2 stays
      experimental. The assumption is that square–mask–square behaves like M1's ideal permutation, and a GPT-model
      crypto review rates confidence in it as low.
    - **Cooperating cores:** the recommended default is to allow cooperation within one chiplet. That needs w ≈ 28,200
      at 2.9 ms, or ≈ 10,400 at 0.5 ms. Measured here: 1.41× / 1.73× / 2.13× at 2 / 3 / 4 cores.
  - **CPU evidence round on the memo's six items (started 28 Sep, 09:58Z; GPU freeze in force).** Workers:
    - [small-width compression attacks](https://cursor.com/agents/bc-397b33f2-d49b-5ef6-967b-54a091f52504): the
      hybrid bit/field risk, with SAT, Gröbner and lattice attacks. The
      [first launch](https://cursor.com/agents/bc-94edc550-d42e-5383-a1d0-fba9925893d1), this relaunch and a
      [third](https://cursor.com/agents/bc-5721f6ee-e5bf-595e-adc2-d52426b8ecff) were all stopped by OpenAI's
      cybersecurity safety check;
    - [seed expander](https://cursor.com/agents/bc-400e4a96-69f2-5100-b001-ca8a90f54560);
    - [literature](https://cursor.com/agents/bc-17b12238-4326-5d0b-884b-c98ad843d205);
    - [generic-model bound](https://cursor.com/agents/bc-4f133781-5dc5-5ef4-93db-6e7ae0e61c20);
    - [spec draft and bounty kit](https://cursor.com/agents/bc-c3a6a8ed-8de9-569a-8314-65f93ef79c6a);
    - [exact-domain Lean rerun](https://cursor.com/agents/bc-26d73714-aabb-5bc5-a7ed-04ef3723a2af) (the A2 prover);
    - [character and differential bias](https://cursor.com/agents/bc-3c1ba600-7f9c-584b-b0d9-5c821280e5ed), from the
      literature pass's proposed tests (10:30Z).
    - Reviews afterwards by `crypto-review-p2-instantiation` and `statement-review-p2`, both on GPT models.
    - **Outcome (12:30Z).** The default stays "do not accept yet", and the reviewer's confidence stays low. The memo's
      evidence section has the per-item table.
      - **Moved:** the key expander (P2-EXP-IO, on paper).
      - **Partly moved:** the spec, internal cryptanalysis, the bounty kit, the generic bound, and the exact domain
        [0, p). The last is proved, reviewed and pinned in Lean; the timing re-gate on the fastest hardware remains
        open.
      - **New:** the k = 88 certificate absorbs only 6 bits per block of structural saving; k = 95 absorbs 64 bits and
        k = 103 absorbs 128 bits.
      - **The small-width study:** OpenAI's cybersecurity safety check stopped all three GPT worker launches; the
        coordinator ran a reduced SAT study
        (`attacks/p2-sat-recovery.md`). SAT fails the zero-mask control, so it is no evidence either way.
    - **Exact-domain pins, pinned at 12:38Z on the root's go:** `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond` and
      `P2MeetsM1pW8192Uncond`, plus a new trusted model file, `Pous/Model/M1p.lean`. That makes 43 pins.
      - **Checks:** the statement review is GO after its docstring fixes; all three grade PASS; `check.sh` passes (445
        declarations in 20 modules); `TRUSTED.sha256` verifies 26 of 26.
      - **Status:** added after the snapshot in PRs #162/#183, and pending Daniel's review. They are not synced to the
        repo; that follows once those PRs merge.
      - **Record:** `lean/submissions/efficient-crypto/p2/GRADE.txt`.
    - **Spec freeze, the parts that don't need Daniel (28 Sep, 14:00Z).**
      - **Prime** ([certificate note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-prime-certificate.md)):
        - the current p has no N±1 certificate, but it is **now certified by ECPP** (29 Sep, 02:04Z):
          - CM `ecpp-mpi`, 339 steps, 2 h 39 min on 4 cores;
          - accepted by PARI, CM's `ecpp-check` and `ecpp_verify.py`;
          - `internal/efficient-crypto/p2-prime/cm-cert-p16448-c21065`;
        - the proposed p′ = 2^16448 − 1213·2^8232 − 1 has an N+1 certificate, three independent checks and a Lean
          proof (`lean/submissions/efficient-crypto/p2-prime/`);
        - the crypto review rates p′ acceptable with conditions;
        - the recommendation is to keep p; p′ is needed only if a Lean-checked proof becomes a requirement.
      - **Audit wire formats:** written into the spec draft as `p2-audit-wire/v1`, with reproducible test vectors in
        `internal/efficient-crypto/p2-bounty-kit/audit-vectors.json`. Decision 2 stays open.
    - **Overnight, 29 Sep:**
      - **Margin rows certified in Lean** (`lean/submissions/efficient-crypto/p2-margin/`; not pinned). The lower
        proved k over the family is 96 / 105 / 128 for 64 / 128 / 256 bits of per-block slack. The ideal-model ε
        fits in 2^-129. The statement review is GO after its docstring fixes, and all three grade PASS.
      - **`p2-audit-wire/v1` closed on two checklist items:**
        - 31 negative conformance cases;
        - an independent second implementation written from the spec text alone, matching every vector byte for
          byte (`internal/efficient-crypto/p2-audit-wire-interop.md`). It surfaced a W-packing mismatch and about 20
          ambiguities, all fixed in the spec.
      - **State isolation closed (04:40Z):**
        - a normative "State isolation and state accounting" section in the spec, mapping the Lean game's free
          inputs and its S-bit state at each round boundary onto deployment resources;
        - a state-capped responder harness (`p2-bounty-kit/isolation_harness.py`), whose tests pass;
        - the statement review: sound after its corrections, which are applied.

  Earlier: **Soundness review stopped by a content filter (17:02Z)** after only its skeleton. The coordinator checked the top risk, the mask, analytically: sound if K is uniform (weight ≈ w/2). The attack must guess or store the masked bits of `s ∧ K`, and it only saves anything below weight ≈ 0.11w (`attacks/p2-mask-check.md`). **Zen 5 measurement (17:42Z; Attempts `r20260927-173925-b895` and the failed launch `r20260927-173800-1626`, both preserved on the evidence store's remote; spend $0.01):**
  - **Correctness and latency:** on an AMD EPYC 9655P every root verified, and IFMA latency is 4 cycles as assumed.
  - **Unusable wall clock:** the shared host ran at an effective 0.6 GHz with varying frequency. The fastest roots were
    14.4 ms (5504) and 27.6 ms (5952).
  - **Clean reference (this VM's 4.0 GHz Xeon):** 1.92 ms and 2.36 ms per root, about 1.35 ms and 1.65 ms at 5.7 GHz
    with the same cycle counts. That is 4.5–5.5× over Δ for the campaign's own kernel.
  - **The adversary bound is unchanged:** the architectural IFMA floor (at most 2 per cycle at 5.7 GHz) gives 493 µs at
    5504 (1.64×), and 5952 holds 2×.
  - Outputs: `candidates/alt-primitives/p2-latency/pod-epyc9655p-*`.

  Earlier status: **Re-gated 16:48Z; passes the cost gate; in soundness review.** `c = ρ(σ(ρ(m + t)))` with p = 2^5504 − 869, a dense shared public XOR mask σ and beacon tweaks. Decode is 2 squarings per 688-byte block, 87–130 int32/B ≈ 14.5–21× *est.*, against P3-ARX's 26–50× and SHAKE256 P3's ≈ 2,000×. Prefill 1.6–1.9× is not cheaper than ARX P3. Depth: a stored-hint attack means only one of the two roots counts, so 1279 bits fails (71 µs per root measured-scaled; 55.7 ns per 1279-bit squaring with IFMA on this Xeon). At 5504 bits one root takes 493–681 µs *est.* (1.64–2.27× Δ); 5952 bits holds 2× at the floor. γ ≈ 0.35%, k ≈ 101 (M2 bound) or 92 (M1 plus B1′). Proof route: M1/M2 counting (A3′ proved; M2's Lemma A and `M2Meets` to state) plus two named hypotheses, SMS-IC(Δ) (ideal behaviour) and SeqRoot (sequential root latency on the fastest core). Top risks: the fastest core's squaring latency, and zero-root lattices through the mask (with K = 0 it loses 10–16%, so K's density is load-bearing). | [scout](https://cursor.com/agents/bc-1d695f79-a999-5568-9660-b13841036977); [soundness reviewer](https://cursor.com/agents/bc-e6462688-cae2-5175-b913-958f85a541bc) | `candidates/alt-primitives.md` (§ Re-gate); `attacks/p2-soundness.md` |
| **Candidate: wide-label DSaG** | **Killed (17:00Z) in soundness review; see Dead ends.** With xⁱ coefficients, storing n/3 key inputs rebuilds a layer in 3 rounds. Random coefficients still fall below the δ-lemma certificate. Hashed keys fix it but cost about as much as P3. Earlier status: **Costed 16:25Z; passes the cost gate; in soundness review.** Blocks of 4,096 labels of 1 KB, full power-of-two skip list, Beneš connectors of weak whole-label gates, keys `Π(S) ⊕ S` on a linear combination S of the parents (one wide call per label, with feed-forward). Against the matching P3: SHAKE256, 2 layers, about 898 SASS/B, 14.7× less work (decode ≈ 143× against ≈ 2,100×; prefill ≈ 6.8× against 85×). Heuristic ARX, 3 layers, about 49 ARX/B, 5.6× less work (decode ≈ 6–9× against 26–50×). Proof obligations: the DSaG pebbling theorem (two layers proved on paper), the δ(m) ≥ n − 2m lemma (exhaustively true for n = 16–24, unproved), a rank lemma for the weak gates, and the pebbling-to-ideal-model bridge (conjectural: N10′ at one component per label, plus linear key inputs). **Open risk (16:30Z):** its S is a linear combination of parents, so key storage applies. It hits layer 1, whose input W is known, and shrinks the depth certificate: about 27% extra deficit on drU stacks, against margins of 1.79 (SHAKE) and 2.13 (ARX). A proof would need a LinHard certificate; sponge keys avoid this but cost as much as P3. | [graphs designer](https://cursor.com/agents/bc-b01b9931-1f34-5b11-afc0-545e8bc87c24); [soundness reviewer](https://cursor.com/agents/bc-bd3724c1-de82-5d9c-ba37-bd2a6a088114) | `candidates/graphs.md` (§ Provable route); `attacks/dsag-wide-soundness.md` |
| Timing feasibility | **Done (15:41Z).** Summary below. The cheapest known sound design at D ≈ 5,200 is the (4,6,4) stack at 128 KB: margin 1.20×, R_seq 7.2–7.8 *est.* (attack-based, no proof). 2× would need each layer at 14–28% of a shipping layer; the only combination that fits (register window plus hash-free keys) is ruled out by the reverse move. P3 at 1 KB labels survives no point, which independently confirms workstream 1's move to 64 KB labels (`p3-scheme.md` §2c). | [analyst](https://cursor.com/agents/bc-06dab6d4-ce8d-52d4-abfe-137655a3c469) | `timing-feasibility.md` |

Running workers get the revised brief when they finish or re-read it; they are redirected when they report.

## Decisions from Daniel

- **27 Sep 15:07Z:** the adversary is a CPU core or a GPU core, not an ASIC; answers are strict, all on time. The
  campaign's single operating point is CPU 58 ns per light hash at Δ ≈ 300 µs, D ≈ 5,200.

- **27 Sep 15:30Z:** "I don't care about the 2x rule for now, let's just get something e2e." The cost-rule questions
  below are deferred; the campaign does not block on them and does not raise them again until Daniel does. Priority is
  workstream 1's end-to-end P3. This campaign continues at its current pace with no GPU spend.

Deferred (from the regimes analysis; each changes the cost claim, not the storage guarantee):

1. **Which batch sizes the 2× rule covers.** Read literally it includes mid batch (64 to about 500), where no scheme
   passes until a fused mid-batch kernel exists. Is the target b ≤ 32 plus prefill for now?
2. **Prefill-only or batch ≥ b₀ certification.** P3 is 1.26× at b = 8192 and 1.98× at b₀ ≈ 2,000. The certificate then
   says HBM holds the encoding, not that the encoding does the low-batch serving.
3. **Partial coverage φ.** 2× at b ≤ 8 needs φ ≤ 17.5% for P3 (12.9% with barriers); the audit then certifies about
   ρφ of the model.
4. **2× on a declared serving mix.** Buys little: Splitwise's Azure traces put 60–70% of time at ≤ 20 tokens, where
   P3 comes out at 4.8–5.4× and the mix tolerates only 15–18 ARX/B.

All four went to Daniel through the root coordinator at 15:18Z and were deferred at 15:30Z. The two H100 measurements (a zero-decode fused kernel at
b = 32–256; 55 ARX/B measured directly) are deferred until a surviving candidate hinges on them; until then candidates
are priced from the measured tables.

## Dead ends

Inherited from earlier work:

- **CUDA-core ARX P3 at decode batch.** 2× needs `a ≤ 0.67` ARX/B per fully diffusing pass at `d' = 12`, against a floor
  of 3 ([P3 scheme](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md) §6).
- **Short parent digests.** Digests under `m/L` bits: storing the digests alone answers every block
  ([P3 cryptanalysis](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-cryptanalysis.md) attack 7).
- **Naive int8 MMA mixing mod 2^8.** It is triangular, and its low bit-plane is GF(2)-affine (attack 6).
- **Sampled or random-parent graphs for P3.** They cannot be certified, and are no better at equal degree (P3 scheme §2a).
- **Per-block trapdoors.** RSA, RW–SMS, lattices and Damgård–Jurik all cost at least one 2048-bit modular multiplication,
  about 68 int32/B. RW–SMS at 2048 bits also factors within the preprocessing budget
  ([sms5 reviews](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/sms5-review-reductions.md)).
- **Lossy twins from rank plus noise, the NTRU shape, or unknown-order groups.** Closed in the source report's §6.

From Daniel's prior measurements (prior notes §5; porep-inference `CATALOG.md` §3.9), adopted at 15:00Z:

- **Tensor-core int8 `mma.sync` mixer.** 2.3× slower than injection-ARX; the phases around the MMA serialize and it
  spills at 128 registers. This killed the tensor-core thread.
- **Tile-shared parent patterns.** Unsound, leaking 15–30%.
- **Degree instead of layers.** Costs more under hashed keys ((3,12,4) > (4,6,4)).
- **Speculative decoding as a ratio lever.** Helps only against a non-speculating baseline.
- **Blackwell.** No help for integer decoders (about 1.9× worse relative to memcpy).
- **The drU DRG construction.** No sound point reaches ≤ 2.2× at B ≥ 8.
- **Keys invertible in each parent, without feed-forward.** They give a reverse move (12–28% leak).

Found by this campaign:

- **Serving regimes as a lever under the rule as written (15:15Z).** Speculation, MTP, chunked prefill, continuous
  batching, MoE, TP/PP, `lm_head` and the embedding: none moves the low-batch matmuls every regime still issues, and the
  fused kernel is flat up to b = 16. So the design must fit about 13.3 ARX/B by itself unless Daniel relaxes the rule.
  MoE and pipeline parallelism make large-batch relaxations worse. Evidence:
  [amortized regimes](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/candidates/amortized-regimes.md).
- **2× at decode batch with any known sound DRG design at D ≈ 5,200 (15:41Z).**
  - R_seq ≤ 2 leaves about 0.26 ns·SM per layer at the l = 4 the deadline forces (0.53 optimistically), i.e. 14–28% of
    a shipping layer.
  - Fewer rounds, lower degree, register-window graphs and connectors don't reach it, alone or combined. The one
    combination that does (register window plus hash-free keys) is ruled out by the reverse move.
  - The cheapest unruled combination, register window plus 3 rounds, is about 4.0× *est.*, with its timed depth
    envelope unmeasured.
  - Evidence: [timing feasibility](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/timing-feasibility.md) Q3.
  - The graphs designer confirmed this independently for both key models. Bands and register windows fail the depth
    gate at any block size: their exact profile δ(m) = ⌈(n − m)/(⌊m/k⌋ + 1)⌉ makes D\* independent of n. Even with free
    keys and free gathers, the rounds the gate forces cost ≥ 1.47× memcpy. Evidence:
    [graphs](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/candidates/graphs.md).
- **Alternative primitive families (15:47Z).** Evidence: [alternative primitives](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/candidates/alt-primitives.md).
  - **One-round power maps** (Sloth-1, MinRoot, VeeDo): an online lattice of dimension 4–11 recovers 6.7–40% of every
    block, confirmed at 128 and 256 bits.
  - **Any per-block power map:** regeneration depth is capped at about 128F/c multiplications for a decode budget of F
    int32/B.
  - **Small-field and extension-field power maps:** fall to online roots or Frobenius linearity.
  - **Exact linear, knapsack, lattice, code and MQ decoders:** fall to online partial recovery; a 26-dimensional LLL
    takes 75% of a 32-coordinate block.
  - **Secret layouts, secret block permutations and space-hard white-box tables:** a keyless decode makes the secret
    public, and erased coins buy at most about 4.8% of |C| (report Props 9–12).
  - **Also closed:** cuPoW-style matmul hardness and "useful work" inside the model's own GEMM.
- **Wide-label DSaG with linear-combination keys (17:00Z).** The keys were `Π(S) ⊕ S` with S = Σᵢ xⁱ L₍ᵥ₋₂ⁱ₎ on the
  full skip list.
  - **Commuting coefficients collapse on any graph.** In characteristic 2, Σᵢ xⁱ S₍ᵥ₋₂ⁱ₎ = Σᵢ x²ⁱ L₍ᵥ₋₂ⁱ⁺¹₎ + public
    terms (the cross terms cancel in pairs). Storing the key inputs S at positions ≡ 1, 3 (mod 6), i.e. n/3 of them,
    rebuilds a whole layer in 3 rounds at every n tested (32–256). This covers powers of x, plain XOR and per-slot
    constants.
  - **Random per-edge coefficients** avoid that collapse but still reach less depth than the δ(m) ≥ n − 2m bound in
    exhaustive small-n runs (for example n = 12, 3 stored: 5 levels against the lemma's 6 and hashed keys' 8). The
    optimal strategy stores key inputs, and feed-forward doesn't block that.
  - **The only fix is hashed (sponge) keys,** which cost about P3/1.07, so the candidate is no longer materially cheaper.
  - Evidence: [DSaG soundness](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/attacks/dsag-wide-soundness.md) Q1 (the reviewer was
    stopped by a content filter after Q1–Q2; the algebraic identity was checked by the coordinator).
- **Linear keys in P3's label form, with any coefficients (16:27Z).**
  - A stored key, or the pre-image of any one-way pass over a linear combination of parents, costs one label, yields
    that label with one call, and is also a linear equation in the parents.
  - Measured: 16–18 stored keys out of 32 rebuild a layer whose inputs are known; about 27% extra deficit on deep
    stacks; X = d/2 on P3's band, refuting the X = 3 certificate.
  - Whitening and feed-forward don't help. P3-LK also regenerates from nothing in about 450–720 light-hash latencies,
    far below 5,200.
  - Evidence: [cheap keys](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/candidates/linear-keys.md) (A4, E4, E5).
- **Plain XOR, or any shift-invariant linear keys (15:35Z).** `K_{v+1} = K_v ⊕ c_v ⊕ c_{v−k}`, so one stored key restarts a
  rebuild front, and fronts spaced `s` apart run in parallel. On P3's two layers at depth 10 this saves 58% of C,
  replayed bit-exactly on a toy. Powers of one matrix and slot rotations collapse the same way. Random per-edge
  coefficients leave a front rank of 5–7 labels against 12 for hashed keys; their verdict is pending. Found by the graphs
  designer: `internal/efficient-crypto/candidates/graphs/xor_collapse.py` and its log.

## Index

- [Worker brief](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/campaign-brief.md) (internal): yardsticks, the 15:00Z update, lessons, kill
  criteria, output conventions.
- [P2 deployment decisions](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-deployment-decisions.md): the freeze decision list,
  frozen 29 Sep 2026 at the six defaults (default, Daniel deferred, 2026-09-29); Decision 1 (P2–M1-SGI) not accepted.
- [P2 verdict](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/efficient-crypto/p2-verdict.md) (internal).
- [P2 specification v1, frozen](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/efficient-crypto/p2-spec-draft.md) (29 Sep 2026): k = 105, the
  current prime kept (ECPP-certified, no Lean proof); it includes the MVP conformance table and "Remaining before deployment".
