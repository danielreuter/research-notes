---
id: 20261004T2202Z-report-relay-docs-pous-audit
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pous-audit.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pous-audit.md`, sha256 `c032085f615052b832e7b6d31545057190ad5de44a64a23676bc81c8423d6a3e`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# POUS handoff audit (27 Sep 2026)

Source: read-only audit of `~/projects/porep-inference/research/POUS_STATE.md` and surrounding files on Daniel's MacBook.

**Bottom line:** `POUS_STATE.md` is an accurate systems summary of the latest work, but it is not a research handoff and doesn't prepare a Lean campaign. No Lean work on POUS exists anywhere, and nothing mathlib-based is built on the laptop. The design it favours (RW–SMS, section 2.A) doesn't meet the project's own written problem statement. The repo's only git remote points at a pod that was terminated, so the laptop may hold the only copy.

## 1. What POUS is

**Setting.** An operator declares how each GPU's HBM (the GPU's on-package memory) is divided: `weights | KV pool | filler | workspace`. We want proof, for each region, of four properties:

- **Possession:** the bytes exist.
- **Locality:** they are in this GPU's HBM, not in host memory, a peer GPU or disk.
- **Dedication:** the data can't be held in less than (1−ε) of its size, with ε ≈ 5% (the formal documents use r = 18/19, i.e. ε = 5.26%).
- **Usefulness:** the bytes really are the declared model weights or KV of real sequences.

**Threat model.** The adversary is the operator. It controls host, driver and serving stack, knows the weights and all public parameters, and can precompute arbitrary advice. The only levers are bandwidth (PCIe is 50× slower than HBM on H100) and wall-clock deadlines enforced by a trusted on-node challenger.

**The target primitive.** Stated formally in `research/paper4/open_problem.md` and in the Notion [Problem statement](https://app.notion.com/p/3e2399515d9e81babf54e79df0080220) (21 Sep). A trusted encoder turns weights W (adversarial, possibly all zeros) into an encoding C plus public parameters, then erases its secrets. Requirements:

- **Space:** |C| + |pp| ≤ 1.05|W|.
- **Decoding:** public and bit-exact, run on every weight use.
- **Security:** Moran–Wichs incompressibility of the whole encoding given W. A server keeping at most (18/19)|C| bits passes a k-block raw audit with probability at most 1%.
- **Audit rules:** no deadline, no locality assumption, all indices revealed at once, 128-bit security.
- **Cost:** at most 2× the plaintext matmul sequence, including low batch. That leaves about 4.5 int32 operations, or about 120 int8 tensor-core multiply-accumulates, per decoded byte after the keystream.

The wanted object is either:

- a lossy "twin" function with a small hidden image that does not rely on rounding noise, or
- a single-round map with a direct whole-encoding proof in an idealised model.

## 2. Current state

"Proved" below means a written, agent-reviewed paper proof, never a machine-checked one. The sms5 memos have had no independent review.

**Proved on paper (phase 4, reviewed):**

- Moran–Wichs over Damgård–Jurik is secure but about 10^7× too slow.
- The raw-block audit is equivalent to incompressibility given W (template_bound Lemma 3).
- Lower bound of about 250 int32/B for rank-plus-noise lattice twins under the Moran–Wichs proof route.
- An exact linear interface Eval(X, C) = XW makes C compressible; a weights-dependent setup doesn't help.
- The NTRU shape is closed.
- The factoring cap (Coppersmith at 25%).

**Proved on paper (sms5, unreviewed):**

- Ideal-model completion bound (Theorem 1 in `sms5/ideal/tradeoff.md`).
- No fully black-box reduction to any single-stage assumption (Theorem 2 in `reduction.md`).
- No information-theoretic theorem for any encoder with a short secret (Prop. 1 in `redesign.md`).
- Theorem A, and the equivalence of design (a) with a two-root Rabin game.

**Conjectured:**

- RW-IC: RW–SMS loses no more than an ideal permutation. This is effectively the conclusion assumed, up to a constant.
- 2RG-C: Coppersmith is optimal for jointly leaked Rabin roots.
- B1′-M2: the log_2 g loss term disappears in the shared-oracle model.
- The memos' own estimates: P(reduction to factoring) ≤ 0.05, P(actually secure at s/w = 0.95) ≈ 0.75, P(provable design of this kind) ≈ 0.05.

**Tried and failed:**

- DCR/Damgård–Jurik, lattice/LWR/NTRU: too slow or blocked by rank.
- Single-round RSA: broken by the shift-and-kangaroo attack.
- The other team's 61-bit VDE: broken by Coppersmith.
- The +10% cost target: closed for this architecture, because the keystream alone costs 1.17–1.28×.
- Public DRG PoRep: attack-based only, measured at 4.5×.

**Open:**

- Plaintext compressibility inside the bandwidth-audit slack.
- Whether shift-and-kangaroo stacks on Coppersmith.
- The five cryptanalysis questions in `redesign.md` §5.
- The RW–SMS decode kernel is unmeasured.
- Latency of the chained raw-block audit.
- A tensor-core-native PRG or hash, the one thing that would reopen the +10% target.

## 3. Resources (laptop paths)

- **Repo:** `/Users/danielreuter/projects/porep-inference` (branch `main`, head `86ae77f`).
  - 18 worktrees at `/Users/danielreuter/projects/porep{2,4}-*`.
  - `p2/k1` is unmerged, but it is a wording-only commit.
  - Key files: `research/POUS_STATE.md`, `research/sms5/{spec.md, ideal/tradeoff.md, reduction/reduction.md, redesign/redesign.md}` (with `.py` checkers), `research/paper4/{report.md, open_problem.md}`, `research/trusted4/theory/template_bound.md`, `research/{OPTIONS,REPORT4,PLAN4,CONTEXT4,CATALOG}.md`.
- **Lean:** none for POUS. elan is installed with toolchains 4.26.0, 4.32.2 and 4.33.1, and no default set.
  - Closest template is `/Users/danielreuter/projects/proofs/proofs`: a "lean-grader-mvp" on Lean 4.32.2 with mathlib `v4.32.2` (`905b958`). It pins trusted `Harness/` statements, keeps an axiom registry, and the grader checks definitional equality with the pinned type and audits the axioms used.
  - Its mathlib source is checked out, but no compiled files exist (`lake exe cache get` has never been run). It is not in git.
  - `/Users/danielreuter/projects/veritor/lean` is core-Lean only (4.33.1), built, and unrelated.
- **Compute:** no pods are running.
  - `infra/ledger-porep.json` shows everything terminated on 21 Sep; phase 4 spent $18.
  - Launch tooling: `infra/runpod_ctl.py`, `infra/pod.sh`, and `infra/pod-*.env` (the endpoints in those files are stale).
- **Notes:** `~/.research/notes` has no POUS content. Its lane contract and research CLI are Verity-specific but could be adapted for a campaign.
- **Notion (not referenced in any repo file):**
  - [Problem statement](https://app.notion.com/p/3e2399515d9e81babf54e79df0080220) and [Two-pager](https://app.notion.com/p/3e2399515d9e8197a90ae89caa03d4b3), under "Trusted incompressible encodings of model weights".
  - [Context dump on Proof of Useful Space](https://app.notion.com/p/3bc399515d9e8008b0c4f57dcbe2d981) (14 Aug).
  - [Verification contest sync](https://app.notion.com/p/3c2399515d9e81f49fa4c24363a098cf) (20 Aug): plans a PoUS competition with manual judges and Pearl as a possible partner, and prefers low-risk existing ciphers over new primitives.

## 4. Handoff gaps and inconsistencies

1. **Wrong audience.** The doc is written "for whoever designs the reference implementation". It doesn't mention Lean, doesn't say that nothing is machine-checked, and doesn't say the sms5 results are unreviewed ("one afternoon of adversarial attention", in `reduction.md`'s own words).
2. **Its preferred design doesn't meet the problem statement.**
   - RW–SMS uses sequential reveal with Δ ≤ 1 ms and an online budget T ≤ 2^34. The statement forbids deadlines and reveals all indices at once.
   - Without a deadline, T is effectively unbounded and the 2048-bit bound becomes vacuous: the loss exceeds the 94.8-bit budget.
   - It also costs 12–20× at decode batch against a 2× target that includes low batch. `POUS_STATE.md` quietly retargets to prefill and a timed game without saying the problem changed.
3. **It merges two different idealisations under one "ideal-model" label.**
   - `tradeoff.md` idealises the Rabin squaring itself (the XOR-mixer design, ≈100 int32/B).
   - `redesign.md`'s design (a) idealises only the middle mixer (Keccak Feistel, 127 or 206 int32/B), under a different conjecture.
   - The open kangaroo-stacking question belongs to design (a). `reduction.md` says the XOR blocks the kangaroo attack in the XOR design.
4. **The memos' own probabilities are omitted:** ≤ 0.05 for a reduction to factoring, ≈ 0.75 for actual security, and the hourglass precedent (a similar incompressibility conjecture that fell to an elementary attack).
5. **Decode-cost estimates disagree by about 2×.** `spec.md` gives 20–30 int32/B for two 1279-bit squarings; `redesign.md` gives 50 per 2048-bit squaring. Both are estimates.
6. **The index documents are stale.** `CATALOG.md`, `OPTIONS.md` and `REPORT4.md` predate sms5 and don't mention it. There are no plan, context or team files for sms5, and no reviews.
7. **One broken pointer:** bare `template_bound.md` should be `research/trusted4/theory/template_bound.md`. The other cited paths resolve.
8. **Durability risk.** The only remote is `volume` (an ssh remote on a pod), which TEAM4 records as terminated on 21 Sep. Four infra logs are untracked.
9. **No mention of the Notion pages or the competition framing.** The contest notes prefer a faster composition of existing ciphers, which sits uneasily with "find new primitives".

## 5. What a Lean campaign needs

**Decisions first:**

- Which game is canonical: the untimed statement or the timed RW–SMS game.
- Whether the target is ε = 5% or 5.26%.
- Whether low-batch decode is in scope.

**Trusted layer (human-written and human-reviewed; this is the critical step).** Reuse the `proofs/proofs` pattern of pinned statement types, an axiom registry and an axiom audit. Lean statements would cover:

- the encoding scheme, incompressibility given W, and raw-block audits with sequential and simultaneous reveal;
- a finite random-permutation or random-oracle model, with queries counted.

Computational assumptions (factoring, RW-IC, 2RG-C) can only go in as registered axioms: plain Lean has no practical way to state polynomial-time bounds. Mathlib has no random-oracle model or compression-argument library. VCVio is an external option and is not on disk.

**Problems that can be parcelled out**, roughly easiest first:

1. Prop. 1 (no information-theoretic theorem for short-secret encoders), plus the fibre-counting bound |C| − |W|.
2. Lemma 3 (audit ≡ incompressibility given W).
3. The corollary that Eval = XW makes C compressible by Gaussian elimination.
4. Lemma A and Theorem 1, the compression counting argument in model M1, then M2/M3.
5. Theorem 2 (simultaneous reveal), Theorem A, and the equivalence of design (a) with the two-root game.
6. The lattice template lower bound and NTRU Lemma L / Theorem D.
7. Parameter tables certified as rational inequalities, cross-checked against the `.py` scripts.
8. Research-grade: the MW20 Thm 8.1 meta-reduction for the ideal-permutation plus random-oracle model; a direct single-round proof for a new candidate map; B1′-M2 (removing log_2 g).

**How results are checked:**

- Lean covers only definitional equality with the pinned statement plus an allowed-axiom set.
- Cost (measured R_seq on an H100 fused kernel) and cryptanalysis (kangaroo stacking, the XOR-between-squarings question, a tensor-core PRG) sit outside Lean. They need pods and Python/Sage.

**Blockers:**

- Problem-statement choice.
- Nobody has written the trusted statements yet.
- Mathlib compiled files not fetched.
- No random-oracle model or probability framework.
- The repo has no live remote.
- No compute provisioned; RunPod credentials would be needed.
- The sms5 claims need independent review before agents build on them.
