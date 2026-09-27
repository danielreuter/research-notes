---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

# One-stage audit end to end: inventory, gaps, smallest real run

Integration lane `one-stage-e2e`, 2026-09-27 05:26Z. Step 1 (CPU only, $0). Code read at `main` `8515c79e`, M0 PR #83 @ `eb90718f`, partition PR #111 @ `7ddb7cca`, Lean verifier PR #113 @ `9d0d53df`. `docs/audit-protocols.md` doesn't exist yet, so this plan uses the chain in `docs/commitments-and-circuits.md` §5 as the working one-stage definition.

## Headline

- **Every stage has working code except three bindings and one output.** Serving commits, a live draw from the verifier's own OS randomness, M0's prover session, and the Lean verifier all exist. What's missing:
  1. the Lean verifier reads M0's previous statement format, not its current one;
  2. M0's statement binds a placeholder partition (`flock-circuit/unit-cover/v0`) and positions in the input set, not `verity/partition/v1` and its global unit indices;
  3. there's no registration record (M0's `Register` message carries no payload);
  4. nothing builds the `IntegrityProfile` from a verified session.
- **The critical path is the Lean verifier catching up to M0's `eb90718f` format.** It's owned by the flock-verifier lane, which has had the format handoff since 04:45Z.
- **Smallest real run: RoPE d64 over the 1,024 heads captured from served row #101** (`art:16825154…`, Llama-3.2-1B, replayed bit-exact against the served commitment). A CPU check on this VM already passed: M0's staging accepts the captured set in 26 s.
- **Cost: about $1–2** on one 16 vCPU CPU pod at $0.64/h, for about 1.5 h, mostly building. An optional GPU prove on an L40S adds about $0.50.
- **Two calls for Daniel:**
  - Run A commits the served bytes again under M0's scheme, and its link to vLLM's live root is provenance only.
  - The draw picks whole RoPE heads, which breaks the 32-bit unit width rule.

## Overnight status (08:15Z)

Wrong-unit bounds are read as the floor of the relaxation's value: the largest K with $\binom{n-K}{k}/\binom{n}{k} \ge \delta$ (audit-lean's note). So A0 ≤ 254, A1 ≤ 46, A3 ≤ 28 and A2 ≤ 9,675, which corrects the ≤ 47 I wrote earlier for A1.

| Run | Source | What | Result |
|---|---|---|---|
| **A2 `r20260927-074743-5461`** | **served** (vllm-serving-commit run `r20260927-061338-8809`: #101's 183,680 RoPE heads committed at serving time; registration `2f1b6dab…`) | registration checked as received, against the pre-canonical partition object it binds (`f6e07626…`); session on the verifier's re-headered copies for M0 `e51e2b86`'s unbound statement (leaf layer byte for byte serving's); k = 256 | **accepted, `complete: true`**: M0 verifier, Lean U1–U3, Lean #118 `636dc78f` `verify` (628 s, most of it recomputing the served roots); ≤ 9,675 wrong of 183,680 at δ = 2⁻²⁰; 4/4 negatives refused |
| **A1 bound `r20260927-075018-180a`** | stand-in | the M0 `e51e2b86` statement binds the canonical partition (`ba90a294…`), `program_sha512` and the unit indices; Lean `636dc78f` with `--partition` | **accepted, `complete: true`**; ≤ 46 wrong of 1,024 at 2⁻²⁰; 16/16 negatives refused, incl. a statement bound to another partition |
| **A2 bound `r20260927-080759-2c1e`** | **served** (re-served under the canonical partition `17478e85…`, run `r20260927-073101-9c1c`, registration `7b7a1ca3…`) | the statement binds the canonical partition, the program and the unit indices; Lean #118 `1aa5e0e1` with `--partition` and `--program` | **accepted, `complete: true`**. Lean: "units derived: `Q_template_instance` v0 over the verifier's program (183,680 units); the statement's 256 units are instances of `RoPEHead_v1{D=64}`". ≤ 9,675 wrong of 183,680 at 2⁻²⁰; 4/4 negatives refused; preserved |
| A3b `r20260927-081249-3764` | stand-in | layer 0 with GEMM: RMSNorm Triton 256, GEMM K = 2048 384 (qkv, o_proj, gate_up), RoPE 64, RMSNorm fused 8, SiLU·mul 16, GEMM K = 8192 128 (down_proj); N = 856, k = 256; M0 `25519ba1`; each template served its share of the verifier's Lean draw (`--draw-file`) | running |

**Notes from these runs:**
- **Core's `IntegrityProfile.worst_case` couldn't serve N = 183,680.** It enumerates pairs, and its float `accept(m)` underflows.
  - `verity_one_stage.audit.wrong_units_bound` computes it directly (`6ccb9b7b`).
  - audit-lean's [#135](https://github.com/danielreuter/verity/pull/135) fixes core, with the same numbers to the last digit. Switch back once it merges.
- **The first A2 attempts** were refused by Lean only for format reasons, both fixed:
  - an `eb90718f`-format unbound copy, where Lean at `a464d547`+ reads `verity/flock-circuit` as `e51e2b86`'s format;
  - absolute symlinks in the run dir, which break `research fetch --all`.

## Overnight status (07:20Z)

All runs are **stand-in** (fresh commitments to #101's captured values) unless marked served. Code is on `cursor/one-stage-e2e-6014` ([PR #116](https://github.com/danielreuter/verity/pull/116)).

| Run | What | Result |
|---|---|---|
| A1 `r20260927-061630-0645` | RoPE d64, 1,024 heads; M0 `eb90718f`; Lean #118 `verify`; k = 256 | **accepted, `complete: true`**; wrong heads ≤ 47 of 1,024 at δ = 2⁻²⁰; 15/15 negatives refused |
| A3 `r20260927-064317-9536` | layer 0 of #101: RMSNorm Triton 256, RoPE 64, RMSNorm fused 8, SiLU·mul 16 (N = 344); k = 128 over the union; one registration, one draw, one profile | **accepted, `complete: true`**, all 12 verdicts (M0, Lean U1–U3, Lean `verify` per template); wrong units ≤ 28 of 344 at δ = 2⁻²⁰; 5/5 negatives refused |
| A2 | served roots from vllm-serving-commit (N = 183,680 RoPE heads) | waiting on their files (~07:45Z); driver rehearsed; `--unbind` fallback ready |

**Timings on a 16 vCPU CPU pod, per template session in A3:**

| Template | Drawn | Prove | Lean `verify` |
|---|---|---|---|
| RMSNorm Triton | 96 | 8.5 s | 175 s |
| RoPE | 23 | 0.7 s | 26 s |
| RMSNorm fused | 3 | 2.7 s | 142 s |
| SiLU·mul | 6 | 4.8 s | 235 s |

**What A3 doesn't cover:** GEMM coordinates (M0's `compose` refuses tensor-core output tails) and attention (not in M0's statement yet).

**Blocker for bound statements: the partition object's form.**
- Lean #118 at `a464d547` checks `--partition` as exactly `{format, program, query: {name, version, params}}`, with the query `Q_word` v1.
- My object, per the ruling as relayed, is `{program, query}` with `Q_template_instance` v0. Serving already bound its digest into A2's domains.
- With Lean's form check relaxed locally, Lean accepts the bound A1 session. So the object's form is the only gap.
- It needs one canonical form (cross-call-check's #111 rework?), and a Lean verifier that doesn't hard-code `Q_word`.

**Side PR:** [#121](https://github.com/danielreuter/verity/pull/121), the `TwoStageLaw.profile` coarse fix. red-team C1 is met at `8312474c`, and it's ready.

## Run A0 result (05:52Z)

**Accepted, and all 12 negatives refused.** Glue is on `cursor/one-stage-e2e-6014` @ `d27e6941`, [PR #116](https://github.com/danielreuter/verity/pull/116).

- **Runs:** `r20260927-054332-8ba7`, then the rerun with registration domains, `r20260927-055014-8abd`. Both are preserved on R2.
- **Setup:** CPU pod `vy-one-stage-e2e` at $0.64/h for about 21 min, **about $0.23**, now terminated. Binaries built from the pinned archives: `flock-circuit` sha256 `1fab5856…`, `flock-verify` `5283cb0a…`.
- **What ran:**
  1. 1,024 captured #101 heads staged as a **stand-in** commitment;
  2. registration (partition `8797a174…`, registration `be510875…`, source `stand-in`, domains fixed);
  3. `serve --draw subset:16` drew 16 heads from OS randomness after `Register`;
  4. the CPU prover proved them: 8 blocks, `k_log` 22, witness 0.16 s, prove 0.50 s, end to end 1.23 s, proofs 2 × 560 KB;
  5. M0's verifier accepted (verify 0.33 s), and Lean `draw-test` passed U1–U3.
- **Audit record:**
  - `accepted: true`, `complete: false`, because Lean `verify` is recorded as not run (format gap);
  - the profile has one level `unit` of 1,024 units, `Subset(16)`, δ = 0.01;
  - except with probability 0.01, an accepted transcript has **at most about 254 wrong heads of 1,024**. That's the honest strength of k = 16; k scales it.
- **Negatives, all refused:**
  - registration root mismatch;
  - partition mismatch;
  - public-file domain mismatch;
  - draw over another population, outside the partition, or under another law;
  - draw altered after the session, a wrong instance count, a draw dropped from the record (Lean U1 and U3);
  - a prover that ignores the draw (M0 selftest, refused at `Hello` R7);
  - M0's own `unit_draw_session` case passed;
  - **wrong output word:** the tampered commitment's draw hit heads 2 and 5, and the verifier refused the proof (`PcsAb(RingSwitch(ClaimMismatch))`).

## Stage by stage

| # | Stage | Exists today | Missing for one-stage | Owner |
|---|---|---|---|---|
| 1 | Serving commitments and roots | vLLM commits under `vllm-v1` (SHA-256; `hm96-sha256/v1` hiding is opt-in via `commit/hiding.py` and off by default): step roots bind the program, context, geometry and layout digests, and the run root binds the step roots. `verity_vllm/commit/scheme.py` (`run_root`, `step_root`, `stream_root`, `weights_root`), a binding map fixed before the challenge (`commit/binding.py`). M0 commits a template's instances under `frame-v3-sha512` with `hm96-sha512/row/v1` row leaves and fresh OS salts (`verity_flock/circuit.py` `statement`, `write`, `stage`). | vLLM roots aren't in the scheme M0 proves, and don't bind a partition digest. The switch to `hm96-sha512` plus partition-binding roots waits for the re-baseline (E6, on hold). For Run A, M0's staging stands in as the serving commit. | vLLM lanes (re-baseline); none for Run A |
| 2 | Partition object | #111 (draft, in revision): `verity.ir.partition_object` (`build`, `digest`, `validate`, `verify`, `Units.population`, `Units.locate`) and `verity.ir.cut`. vLLM builds it from `word.partition` (`word.partition_object`). For #101 it's 858 MB, with 4.77 M units. | Merge #111, or pin a SHA. A one-template population Program to build it over (one `RoPEHead_v1{D=64}` Call per instance). M0's per-unit circuit SHA-512 as `classes`. | cross-call-check (#111); glue is mine |
| 3 | Registration | Only implicit. M0's wire `Register` (tag 10) is a bare "registration done" signal. The verifier's population is its own staged public file: roots, every row's `b ‖ c`, and the outputs. vLLM's challenge is still Fiat–Shamir on the run root (`commit/challenge.py`, `LEGACY = True`). | A registration record written before the draw: scheme, roots, leaf counts, program SHA-512, partition digest, population. The verifier checks its staged public file against it. | mine (glue), shaped by `docs/audit-protocols.md` |
| 4 | Draw | Lean: `flock-verify draw --population N (--k K \| --p NUM/DEN)`, exact `uniform`/`subset`/`bernoulli` on OS bytes, and U1–U3 on the record (#113, `Flock/Draw.lean`). M0 live: `flock-circuit serve --draw subset:K` draws after `Register`, answers `Draw(json)`, and rebuilds the drawn statement. Instance i is population position `units[i]`, and the header gets `unit_draw`, `instances`, `population` (#83). Selftests `unit_draw_session` and `unit_draw_ignored_refused` pass on CPU. | The population must be `Units(obj).population` of the partition; today it's the staged instance count (the same thing when one instance is one unit). Which verifier process draws in production, Lean or the live server, is a design call. | M0 and flock-verifier have both; the design worker decides |
| 5 | M0 statement binding | META `program_digests` holds core's SHA-256 `program_digest` per template. META `partition` is `{"rule": "flock-circuit/unit-cover/v0", "digest"}`. The header's `units.indices` are positions `[lo, hi)` in the input set. All of it sits under the statement digest and Σ. | `partition.rule = verity/partition/v1` with its digest passed in. The program as `program_sha512`, which the partition object names. `units.indices` as global indices from `Units`, passed in. Per-instance circuit SHA-512 exposed for `classes`. M0 already plans this "when cross-call-check lands it in core". | M0 (#83) |
| 6 | Prover session | `flock-circuit prove --verifier HOST:PORT --instances inst-N.bin --circuit circuit.txt [--gpu]` against `serve --instances pub-N.bin --pin SHA512 --out DIR [--draw …]`, with the step-0 coin commitment (`coin-commit/sha512`), retained round bytes, and records under `--out`. One table ("circuit") per session. Multi-table glue is queued after attention. CPU and GPU both work. | Nothing for a single-template run. A served row needs multi-table statements plus every class of the row lowered. | M0 |
| 7 | Lean `verify --archive` | `flock-verify verify [--archive DIR] --circuit H --comp H --public H --session DIR…`, SHA-512 archive by content, `archive-put`, U1–U3 after S4, `unit-cut` (partition invariant on one cut). 3 of 3 agreement with upstream on RoPE at M0's previous format `631567f7`. | It doesn't parse M0's `eb90718f` format. `Circuit.lean` still reads META `row_key` and has no `sha512x3`/`hm96` slots, no `row_key_sha512`, no population-wide public digest for drawn statements, no `digests: sha512` `Hello`, and no `_sha512` record fields. Later: check the partition object by content and each drawn unit's class. | flock-verifier (#113 follow-up) |
| 8 | Audit output | `verity.proofs.profile.IntegrityProfile` (levels, sizes, draws `Bernoulli`/`Subset`, δ, `programs`, `prescribed`, `linked`, `covered`, `drawn`; `accept`, `rho`, `worst_case`, `to_json`). `TwoStageLaw.profile` builds it for two stages. | A one-stage constructor: one level `unit`, `sizes = (population,)`, `draws = {unit: Subset(k)}`, `drawn = {unit: k}`, `programs = (program SHA-512,)`, built only from a Lean-accepted session. An audit record beside it that cites the registration, the draw, the statement digests and the Lean verdict (the profile has no field for roots or partition). | mine (glue); definition from the design worker |

## Smallest real end-to-end run

**Run A: RoPE d64, 1,024 heads captured from served row #101.**
- **The set:** `art:16825154f08f…` (`vllm-vu-set/v1`, 0.5 MB):
  - run `r20260925-233347-8515`, program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`;
  - every head replayed bit-exact against its committed outputs by `vu_export`.
- **Why RoPE:** smallest template, no lookups, already agreed 3 of 3 between Lean and upstream.
- **Unit layout:** 32 `rope-head/neox-bf16/pair` units per head, 2 heads per block, `k_log` 22.
- **Checked on this VM** (CPU, $0, M0 @ `eb90718f` read-only):
  - `python -m verity_flock.circuit --input-set <set> --n 1024` stages it in 26 s;
  - circuit pin `c84261e7…`;
  - `frame-v3-sha512` roots over `x`, `cs`, `out`;
  - `units.indices` 0..1023.

Steps, with real bytes at each:
1. **Serving commit (stand-in).** M0's `stage` with fresh OS salts gives `pub-1024.bin` (roots, `b ‖ c`, outputs), and the prover keeps `inst-1024.bin`. `provenance.json` links the set to #101's `vllm-v1` run root.
2. **Partition.** A population Program of 1,024 `RoPEHead_v1{D=64}` Calls. #111 `build` with one unit per Call and M0's per-head circuit SHA-512 as its class, then `digest`. `Units.population = 1024`.
3. **Registration.** Write `registration.json` before any draw: scheme, three roots and their leaf counts, program SHA-512, partition digest, population, UTC time. The verifier checks its `pub-1024.bin` roots against it.
4. **Draw.** `serve --draw subset:16` draws 16 heads from OS randomness after `Register`. The record keeps `unit_draw`.
5. **Prove.** `flock-circuit prove` on the drawn statement: 16 heads = 8 blocks, CPU, well under a minute.
6. **Lean.** `archive-put` the circuit, the public file and any `comp`, then `flock-verify verify --archive … --session <record>`. It must accept, and pass U1–U3 against the registration's population.
7. **Profile.** `IntegrityProfile(levels=("unit",), sizes=(1024,), draws={"unit": Subset(16)}, delta=δ, programs=(sha512,), drawn={"unit": 16})`, written with the audit record. At k = 16, n = 1,024, a transcript with m wrong heads passes with probability $\binom{1024-m}{16}/\binom{1024}{16}$.
8. **Negatives:**
   - a flipped output word;
   - a prover that ignores the draw;
   - a draw altered after the session;
   - a registration that doesn't match the public file.
   Each must be refused, the last one by my driver.

**Staging.**
- **Run A0, possible today:** steps 1–5 plus Lean's U1–U3 on the draw, with M0's own verifier accepting. The partition is attached beside the statement, not bound in it.
- **Run A1, the full chain:** needs the Lean format catch-up (stage 7) and M0's partition, program and index binding (stage 5).

**Run B, a served row, later.** #4 (SmolLM2-135M) or #101 through their own roots needs:
- serving under `frame-v3-sha512`/`hm96` with roots binding the partition digest (re-baseline), or M0 proving `vllm-v1` SHA-256 rows in the circuit;
- multi-table statements;
- M0 lowerings for every class a draw can hit (GEMM coordinates, attention, norms, sampling);
- a partition object at row scale (858 MB for #101; a class-index variant would be 244 MB).

## Run A2: the served roots (planned, 05:50Z)

Daniel approved linking the run to what serving actually committed. The lane `vllm-serving-commit` (bc-819f6247) will make vLLM commit #101's values at serving time in M0's row format, and hand over the served roots and the registration record.
- **A0 and A1 stay on the stand-in,** labelled as such.
- **A2 is A1 with one change:** step 1, the serving commit, comes from serving instead of M0's staging. Partition, draw, prover, verifiers, profile and negatives are unchanged.

**What `vllm-serving-commit` hands over.** Four files; the prover's file never reaches the verifier.
1. **`registration.json`** in `verity/one-stage/registration/v0`, passing `registration.check` against the verifier's own program and query:
   - `commitment.scheme = "frame-v3-sha512/hm96-sha512"`, and a source of kind `served` (row, run, committer build) instead of a stand-in;
   - `roots`, `leaves` and **`domains`** for the ports `x`, `cs` and `out`;
   - the partition: SHA-512 of `TemplateInstances{N}` over `RoPEHead_v1{D=64}`, with `Q_template_instance` v0;
   - `partition_digest`, and `population = N`.
2. **The verifier's public file `pub-N.bin`,** M0's `flock-circuit-inputs` with `rows: false`:
   - `frame_v3` holds the roots, `domain_ids`, schemas and `row_key_sha512`;
   - `units.indices` runs 0..N−1;
   - `circuit_sha512` is M0's `rope-head/d64` composite pin (`c84261e7…` at `eb90718f`);
   - then every row's `b ‖ c`, then every output word.
   - The easiest byte-exact route is M0's `circuit.write` fed with the served rows and serving's own salts.
3. **The prover's file `inst-N.bin`:** rows and salts. It goes to the prover only. Serving draws the salts (ChaCha20 from a fresh OS seed) and keeps them only for the prover.
4. **`index.json`:** population index i → served identity (request, engine step, layer, `op_path`, invocation, head), in the order the population program's instances follow.

**Two interface points to agree.**
- **Domains.** M0's verifier takes each port's frame domain id from the public header (`check_public`), so the registration must fix the domains too. The verifier then recomputes them from registration fields. Proposed rule, for the vLLM lane to confirm or amend:
  - `identity_digest("verity/one-stage/served-domain/v0", {program, partition, port, schema, leaves, run})`, using `verity.commitments.identity`;
  - this makes the served roots bind the program, the partition, the scheme and the leaf count, per commitments-and-circuits §5.
  - A0 and A1 record M0's set-bound domains the same way.
- **N and order.** The population is every `RoPEHead_v1{D=64}` instance #101 served, or a declared subset rule such as "layer 0". The order is canonical and fixed before serving. Ideally the verifier derives N from its own copy of #101's program. If that's too heavy for A2, it takes N from the registration, and the audit record says so.

**My side.**
- **Glue, landing with the A0 rerun:** `domains` in the registration, checked in `matches_public`, and `commitment.source` (kind `served` or `stand-in`) in place of `stand_in`.
- **For A2:** `a0.py` gets a mode taking `--registration`, `--public` and `--private` instead of staging. The verifier composes the circuit itself and checks the header's pin against its own. Everything else is unchanged.
- **One added negative:** a public file with one flipped `b ‖ c` byte, refused by root recomputation.

**Cost.** A2 runs on the same CPU pod in minutes once the files arrive. The public file is about 384 B per head. Serving's own cost is the vLLM lane's.

## Glue I'd write (branch `cursor/one-stage-e2e-6014`, off `main`)

- **`protocols/one_stage/`** (stdlib + `verity` only, per `test_protocol_boundaries.py`):
  - the registration record (canonical JSON, SHA-512 digest);
  - checks that the draw is a subset of `Units(obj).population`, and that the drawn statement's indices are those units;
  - the one-stage `IntegrityProfile` constructor and the audit record.
  - It lands as the one-stage module beside `sampled_proofs` (two-stage). I'll rename it if `docs/audit-protocols.md` names it differently.
- **Population Program builder** for a template input set (one Call per instance), plus the partition object through #111's `build`, pinned to #111's SHA until it merges.
- **Runner:** `protocols/one_stage/e2e/run.sh`, one pod script: stage → partition → register → `serve --draw` → `prove` → `archive-put` → Lean `verify` → profile, and the negatives. It shells out to the M0 and Lean binaries built from pinned PR SHAs, so no Python imports cross boundaries.
- **Tests:**
  - the registration digest vector;
  - profile values for n = 1,024, k = 16;
  - the draw-subset and index checks, with mutations.

## Requests to owners (through the coordinator)

- **M0 (#83):**
  - the partition field as `verity/partition/v1` with a caller-supplied digest;
  - `program_sha512` in META;
  - caller-supplied global `units.indices`;
  - the per-instance circuit SHA-512 exposed for `classes`;
  - confirm that `serve --out` records are what Lean's `--session` reads.
- **flock-verifier (#113 follow-up):** parse the `eb90718f` format, per the 04:45Z handoff §1–§5: `hm96-sha512` rows proved in the circuit, `sha512x3`/`hm96` slots and row wires, `row_key_sha512`, population-wide public digest for drawn statements, SHA-512 record fields, the `units` header. Then the partition object by content and class membership (commitments-and-circuits §8 item 5).
- **cross-call-check (#111):** a stable SHA or merge. Also, is a whole-head cut (one unit per Call, width rule off) acceptable as the demo's partition, or should the demo draw pairs?
- **Design worker (`docs/audit-protocols.md`):**
  - the registration record's fields;
  - where roots and the partition digest sit relative to `IntegrityProfile`;
  - which verifier process draws in production;
  - δ for the demo.

## Decisions to surface to Daniel

1. **Stand-in commitment.** Run A proves real served values, but under a fresh `frame-v3-sha512`/`hm96` commitment made from the captured set, not under vLLM's live `vllm-v1` root. The link to root `7adcef49…` is `vu_export`'s bit-exact replay (provenance), not a proof. The alternative is to wait for the re-baseline, or have M0 prove `vllm-v1` SHA-256 rows.
2. **Draw granularity.** One M0 instance is a whole head: 32 pair units, 1,024 output bits. #111's width rule (≤ 32 bits) would make pairs the units, with a population of 32,768, and U3 (instances = drawn units) would then need M0 to prove a single pair or the rule to change. The demo draws heads with the width rule off. The unit-shape decision S settles it for real.

## Pod cost

| Step | Where | Estimate |
|---|---|---|
| Staging, partition, profile, tests | this VM | $0 |
| Build `flock-circuit` (CPU) and the Lean verifier (`lake build`), run A0 and A1 with negatives | one 16 vCPU CPU pod at $0.64/h, about 1.5 h | about $1 |
| Optional GPU prove of the same drawn statement (M0's device witness for the row slots is still incomplete, so this may wait) | L40S at about $1.09/h, about 0.5 h | about $0.55 |
| **Cap asked** | | **$3** |

## Cross-checks (05:27Z)

Three read-only surveys agree with the tables above:
- [Map vLLM serving commits and registration](https://cursor.com/agents/bc-700087cc-a225-5dd8-acb2-02bfa467d05e): `internal/one-stage-audit-serving-inventory.md`;
- [Map M0 Flock circuit statement (#83)](https://cursor.com/agents/bc-84a84d8d-4e74-552a-b161-53abae2f342b): `internal/flock-circuit-m0-e2e-status.md`;
- [Map Lean verifier verify and draw](https://cursor.com/agents/bc-6234dc23-40dd-5095-8c63-3d3b083de074): `internal/one-stage-e2e-flock-verifier-readout.md`.

What they add:
- **Lean statement heads.** The accepted heads are the M0 statements at `19c7269a` and `fd02e847`, plus a default `verity/flock-circuit` head. The default head still proves a BLAKE3 row leaf in the circuit and uses SHA-256 statement and Σ digests.
  - `Public.lean` expects 32-byte digests, `Record.lean` checks `*_sha256`, and `--comp` is the BLAKE3 compression.
  - So the format catch-up also drops or replaces `--comp`.
- **Lean builds cheaply.** The executable has no Lake dependencies (Lean `v4.34.0`; Mathlib is only for the proofs). Honest RoPE verifies in about 32 s on CPU, so the Lean half of the run is cheap.
- **No live-draw sessions recorded yet.** No recorded session carries a non-vacuous `unit_draw` for Lean to replay. Run A0 would produce the first.
- **M0's PR body is stale.** Its tip already has the serving row leaf, SHA-512 digests and the live draw. `identity().hashes` still labels the statement and Σ as SHA-256, which is cosmetic.
- **Smallest served checkpoint.** It's B0, SmolLM2-135M (row #4's model).

Evidence: staged header and META from the CPU check are reproducible with the command in "Smallest real end-to-end run". The captured set's meta is from `research data show art:16825154`.
