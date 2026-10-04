---
id: 20261004T2247Z-draft-move-map-answers
campaign: pouw
lane: compute-accounting
kind: draft
status: draft
repo: danielreuter/verity
origin: bc-e90634dd
---

# compute-accounting's answers to the move maps

This draft answers the rows that name compute-accounting, and the rows whose destination looks wrong, in:

- note:20261004T2125Z-draft-move-map-protocols: the sampled_proofs, PoUW Python, PoUW Lean and `benchmarks/pouw` rows,
  and its open questions for compute-accounting;
- the compute-accounting rows of note:20261004T2125Z-draft-move-map-core and
  note:20261004T2125Z-draft-move-map-backends-integrations-tools.

It applies the plan (note:20261004T2058Z-draft-repo-organization-principles) and its rulings. Where the evidence goes
against a standing position, §A says so; nothing below overrides one silently.

**Revised 23:09Z, after Daniel's 4:06 PM ruling: a computation is verified only by a sampled proof over C-Flock with
zero-knowledge, and a replay is a diagnostic.** `audit.Verifier.check_tile` recomputes `scheme.checked` in the clear for
every scheme in `schemes.SCHEMES`, so these answers change:

- **§C 3:** `verity/`'s registry holds only `circuit.SCHEMES` (`ncp-v2`, `ncp-v2-shift24`). ncp-v1 and
  `pearl-c-sm120-v1-h2` sit beside their replay until their circuits run under sampled proofs.
- **§C 11, §C 13–16:** `pc8`, `rowk`, `leaves`, `boolean`, the Pearl-C half of `words` and TurboSHAKE128 are Pearl-C's
  only route to a verdict. They are no longer experimental.
- **§D 3, §E 3 of the decisions:** the tile-check Lean (`TileCheck8`, `RowCircuit` and the rest) is the bridge that a
  new guarantee needs: the circuit's relation equals `TileGood`, and sampled proofs' soundness is a named assumption.
- **§E 4:** the exhaustion audit's `check_tile` is a diagnostic.

The γ statements and price twins are unchanged. Posted at 1791155395.749669.

**Revised 23:29Z, after Daniel's 4:25 PM ruling: the silicon models (the models and their Lean, FP formats, device
instances and gadgets) go to `catalog/silicon/`.**

- **§A 3, §D 1, §G 2:** `Sm120`, `DevicePricesLoop` and `devSm120v1` go to `catalog/silicon/`, along with PoUW's FP8
  atom model `Fp8Atom.{Atom,E4M3,Fp32}`, which the certified γ reads, and `scripts/fp8atom_vectors.py` (§D 8). The γ's
  `Sm120` instance stays in the lock and reads them by definition hash, through lean's catalog-read allowance.
- **§C 6:** `pearl_c_device.py`'s measured part (the `Prices` values, `atom`, `peel`) goes to `catalog/silicon/`, not
  `catalog/devices/`.
- **§C 4:** `pearl_kw`'s FP-format conversions (`bf16_*`, `f32_to_fp8`, `fp8_to_f32`, `f32_*`) go to
  `catalog/silicon/`.
- **§F 4:** the generic TC interpreter goes to `catalog/silicon/` too, not `verity/primitives/`.
- **§C 12:** `ncp2` stays in `verity/` (as ruled).
- **Unchanged:** "Nothing moves to `experimental/`" is scoped to the proof system. PoUW's experimental rows stand as
  revised at 23:09Z.

**Sources.**

- Code: `origin/main` `9400e83d5`, which contains `16749a0ff`, read with `git show` and `git grep`.
- Which module each guarantee reads: main's `protocols/pouw/lean/lean-audit.json` (800 pins, 128 `reads`), and slice 6's
  at #1132 head `f27afa5ef` (PR open). Slice 6 has the same pin and module sets.
- Approach statuses: `campaigns/pouw/APPROACHES.md`, rendered 2026-10-04T21:08Z.
- Method: read-only. No code was changed and nothing was built.

"Read by" below means listed under that module's `reads[...].pins`. "Closure" means the transitive Lean imports of the
modules the five kept pins read.

## A. Where the evidence disagrees with a standing position

1. **The five-pin lock, against Daniel's 2:03 ruling.** Code, ledger rows and a rendered table rely on more PoUW and
   C-Flock results than the five pins.
   - **Served draw weight.** `pearl_c_work.py:214-220` gives the served draw weight as
     `DrawWref("pearlCSampledSm120v1LoopCast8p72Rev1Cap1000", SM120.name, SM120.cap, …)`. Its comment says the served γ and
     ε cite `ServedMixedRev1Gamma` and `HonestTileCapRate`.
     - The pins involved are the 20 `pearlCSampledSm120v1LoopCast8p72Rev1Cap1000_*` pins, the served-layout γ
       `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_{llama31_8b,qwen3_8b}`, and the completeness pins
       `pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_{llama31_8b,qwen3_8b}` (read through `Assumptions.PearlC.HonestCap`).
     - vLLM's Pearl-C option runs `pearl_c_work`.
   - **The attempt ledger's γ.** `benchmarks/pouw/harness/ledger.py` reads γ from `price_twins.lookup`
     (`ledger.py:202-203`). It writes that γ into `kernel-attempt/v1` records in the store, and `panel.py` renders them
     as rows. So `price_twins.json`'s 104 twins are what ledger rows and a table read, not "an internal pricing table".
   - **Audit-law pins.** `protocols/pouw/verity_pouw/circuit/plan.py` cites eight C-Flock audit-law pins:
     `work_escape_le`, `record_sizing`, `record_sizing_one_fewer`, `audit_work_floor`, `audit_work_whole_stratum`,
     `audit_window_split_of_record`, `covers_window` and `harm_le_unsoundWork`. Sampled proofs' `one_stage/draw.py` cites
     `work_escape_le`, and `one_stage/consumers.py` cites `audit_exfiltration` and `card_admissible_le`.
     - The plan names `Audit.Work.work_escape_le`, but the pin is `FlockSoundness.Audit.Law.work_escape_le`.
   - **Recommendation.** pouw-lock keeps these pins, or the code stops citing what the lock drops. That is Daniel's and
     pouw-lock's call (§E 1).
2. **"Tonight's L3 pins enter as reads of `EndToEnd`'s tile check" (the plan, round 2).** On slice 6, `EndToEnd` reads
   the same 7 modules as on main. No pin reads `RowCircuit`, `TileCircuit`, `WholeCircuit`, `TileCheck`, `TileCheck8`,
   `RowSem` or `RowPrims`, on main or on slice 6. #1132's body says "No pin reads `TileCheck.Accepts`".
   - Making them reads would take a new or restated guarantee, which is a change of meaning with a DM. Until then they
     go with their lemmas (§D 3).
3. **"Device instances in Lean" go to `catalog/` (the Layout), and architecture's recommendation to restate the
   certified γ over a device parameter** (note:20261004T2227Z-draft-catalog-entry-format).
   - The pin's statement fixes `devSm120v1 Prices.sm120Loop`, cap `1/1000`, cast `218/25 − 8953/1000`, `sh8192`, and the
     literal γ `1648180439/446072750000`. That literal is computed from those prices.
   - Stated over a device parameter, the theorem becomes a family whose only instance sits outside the lock. That is a
     change of meaning. A spec that `require`s catalog Lean also breaks P6.
   - **Compute-accounting's ruling (22:58Z), taking lean's answer (1791153016.351199) over this entry's first
     recommendation.** γ is stated once, as a lemma in `security_proofs/pouw/`, for every device that satisfies the
     named device assumption. The guarantee in the lock is its instance at `Sm120`, with that device's assumption as a
     hypothesis. Its statement keeps the concrete prices, cap, cast, shape and the literal γ, so `--update --moved`
     must print it as the same statement, and the change needs no reviewer. If it doesn't print that, the restatement
     waits for Daniel's review. `Sm120`, `DevicePricesLoop` and `devSm120v1` (split out of `Device.lean`) become catalog
     Lean. Each entry's `value` is the definition hash that the lock's `reads` records, and lean's reads check admits
     catalog reads, which answers the P6 objection. Every other instance leaves with its pins.
   - Python takes the device as a parameter. A test checks that the catalog's sm_120 record equals the Lean instance's
     numbers.
4. **"Parsing a name grants nothing, since the lookup in `SCHEMES` fails closed"** (the map's `serving.py` row). This is
   false today. I agree with compute-accounting's lean (two registries, the caller chooses, no hook); here is what has
   to change for it to hold.
   - **Three registries:**
     - `schemes.SCHEMES` (9 entries);
     - `circuit.SCHEMES = {"ncp-v2": "word", "ncp-v2-shift24": "shift24"}`;
     - vLLM's `protocol_options/pouw_pearl_c_device.py:108`, whose `SCHEMES` is built from
       `C.PearlC(forming="v1", device=d, hashing=h).name` over `(SM120,"h1")`, `(SM120_UNPROMOTED,"h1")` and
       `(SM120,"h2")`.
   - **vLLM's `scheme_of` (line 155) skips the protocol registry.** It builds
     `C.PearlC(forming=…, device=DEVICES[sid.device], hashing=…)` without `schemes.SCHEMES`. vLLM's `pouw.py` (line 99)
     unions all three registries.
   - **`audit.Verifier(scheme, epoch, limits)`** accepts any `PoUWScheme` object.
   - **Result.** The served `pearl-c-sm120-v1-h1`/`-h2` and `pearl-c-sm120-unpromoted-v1-h1` are not in `SCHEMES`.
     `pearl_c_device.py`'s own docstring says the unpromoted record has "no scheme registered", yet vLLM serves it.
   - **What must change.** Each entry point refuses a name outside `verity/`'s registry: `Verifier`, `identifier`, vLLM's
     `scheme_of` and `EXECUTED`.
5. **The Layout's PoUW split: `verity/` holds `pearl-c-sm120-v1` "(and `-h2`)".** This is compute-accounting's own text,
   so this entry corrects it rather than disagreeing with anyone.
   - The registry has `pouw/pearl-c-hash-h0` and `-h1` superseded, `-h2` merged, and `pouw/pearl-c-sm120-v1` merged
     "(served as -h2)".
   - So `verity/` holds `pearl-c-sm120-v1-h2`.
   - `pearl-c-sm120-v1` (h0, in `SCHEMES` today) and `-v1-h1` are superseded, and still build, so they go to
     experimental under P8.
   - `pouw/pearl-c-sm120-unpromoted` is parked, so it is experimental.
6. **The H100 lane stays experimental (12:51).** I agree. `pouw/pearl-c-h100-v1` and `pouw/kernel-pearl-c-h100` are
   parked. But H100 is the default device today in `PearlC.__init__` (`pearl_c.py:387`, which also defaults
   `forming="v0"`), `pearl_c_debit.py` and `pearl_c_u.py`. Moving that code with these defaults would make the
   experimental lane the default inside `verity/`, so every default has to go (§C 6–8).
7. **The #1144 root constraint.** Nothing here conflicts with it. The modules that §D sends to `security_proofs/pouw/`
   take the `PouwProofs.*` root and keep their `Pouw.*` namespaces. Spec modules keep `Pouw.*`, so the keys of `reads`
   do not change.

## B. sampled_proofs (`protocols/sampled_proofs/`)

1. **`one_stage/audit.py`** (where sampled proofs lives).
   - **Answer.** `verity/protocols/verification/sampled_proofs/`, beside C-Flock, rather than a protocol of its own.
   - **Evidence.**
     - `tests/test_protocol_boundaries.py` has `EDGES = {"pouw": {"sampled_proofs"}}`, Daniel's ruling of 2026-10-03:
       "PoUW's tile check is a sampled proof". So it is a verification protocol that the accounting protocols consume.
     - Its Lean is C-Flock's `FlockSoundness.Audit.*`.
     - Its importers are `benchmarks/one_stage/a0,a2,a3.py`, `backends/flock/verifier/stratified_agree.py` (`audit`,
       `draw`, `partition`) and C-Flock's tests (`registered`, `partition`, `draw`).
   - **Confidence:** medium-high.
2. **`one_stage/registration.py`.**
   - **Answer.** The destination stands, but its evidence is wrong: vLLM does not import it.
   - **Evidence.** vLLM's `serving_rows.py` keeps its own `verity/one-stage/registration/v0`. The only importers are
     `benchmarks/one_stage`.
   - **Confidence:** high.
3. **`one_stage/consumers.py`** (part of a cited result, or consumer code?).
   - **Answer.** Consumer code. It goes to `experimental/sampled_proofs/consumers.py` with its test and the Lean
     difftest, until a consumer adopts it.
   - **Evidence.**
     - Nothing imports it outside its own tests and the README.
     - It is the Python twin of `audit_exfiltration` and `card_admissible_le`, which it cites. `test_consumers.py` checks
       it against `tests/fixtures/exfiltration_lean.json`.
     - `verity.claims` has no sampled-proofs id.
     - AGENTS.md: consumers read the profile "with their own utilities; their readers stay out of core".
   - **Confidence:** medium.
4. **`one_stage/partition.py`** (are the demo programs `examples/` or a shared fixture?).
   - **Answer.** Neither: don't split it. `population_program` and `mixed_population_program` are two small builders
     (about 40 of the module's 126 lines). They build the program shape the audit runs on, and hold no data.
   - **Evidence.** Their users are the package's own `tests/test_one_stage.py`, C-Flock's agreement check
     `stratified_agree.py`, and `benchmarks/one_stage/a0,a2,a3`. Sending them to `examples/` would make `verity/`'s own
     test import `examples/`, which is core open question 5.
   - **Confidence:** medium.
5. **`law.py`** (does a guarantee read it? experimental?).
   - **Answer.** No guarantee reads it today, so it goes to `experimental/sampled_proofs/law.py` while vLLM's `LEGACY` is
     true, and is promoted, with the two-stage pins, when decision 42 flips it.
   - **The map's evidence is inverted.**
     - vLLM's `commit/challenge.py:30` imports `ReplayUnit`, `Stage`, `TwoStageLaw`, `select_verification_units` and
       `vu_key` for the **non-legacy** draws, and line 33 sets `LEGACY = True` ("decision 42 retires them at the
       re-baseline epoch").
     - The README's "`ru_key` and `vu_key` only for vLLM's legacy challenge" is backwards too.
   - **Lean.** C-Flock's soundness pins `Audit.Partition.Refines.twoStage_exfiltration`, `twoStage_influence` and
     `Audit.Partition.flock_two_stage_exfiltration`. No Python cites them.
   - **Approach.** `pouw/sp-layout-a` (two-stage, layout A) is live.
   - **No prior split needed.** vLLM's import is an integration → experimental edge, which P6 allows, so nothing has to
     move first.
   - **Confidence:** medium. If decision 42 is close, keeping it in `verity/` saves a round trip (§E 9).
6. **`plan.py`** (superseded infrastructure to delete?).
   - **Answer.** Not deleted. It goes to `experimental/sampled_proofs/` with `law.py`, under P8.
   - **Evidence.** It imports `.law`. Its users are its own test and vLLM's `tests/program/test_running_example.py`
     (`weight_binding_plan`, `Obligation`). The README says the two-stage driver is "not built yet", and its approach is
     live.
   - **Confidence:** medium.
7. **`tests/lean/ExfiltrationVectors.lean`, `generate.sh`, `fixtures/exfiltration_lean.json`.**
   - **Answer.** They go with `consumers.py` (entry 3). Which package the difftest builds against is lean's call.
   - **Confidence:** medium.
8. **The section's Lean count.**
   - **Correction.** `FlockSoundness/Audit/` has 38 files, not 27: 26 at its top level and 12 under `Partitioning/`.
     The pin count of 120 is right.
   - **Confidence:** high.

## C. PoUW Python (`protocols/pouw/`)

1. **`identifier.py`** (one registry or two?).
   - **Answer.** Two. `verity/`'s identifier looks schemes up only in `verity/`'s `SCHEMES`. If experimental work needs
     identifiers, `experimental/pouw/` calls the shared encoder with its own registry, explicitly.
   - **Evidence.**
     - `identifier._name` refuses a name not in `SCHEMES`.
     - Nothing outside its tests imports it.
     - C-Flock's verifier compares `tests/vectors/identifier_v1.json` byte for byte, so the encoding stays one.
   - **Confidence:** medium.
2. **`serving.py`** (does Pearl-C4's grammar stay with the rest?).
   - **Answer.** Yes, whole. It is one `SchemeId` grammar (`_FP4` at line 61, `FP4_PRECISIONS` at line 58), and its
     module docstring requires every name in use to parse and print back unchanged. It imports only the stdlib and
     `verity.commitments.blake3`.
   - **Who else reads it.** `ledger.py` and `price_twins.py` read `KernelVariant` and `GateRecord`. Those may move to the
     kernel registry later, but not now.
   - **Correction.** The map's evidence ("parsing grants nothing") holds only once the entry points refuse (§A 4). The
     `-sm120-v1-h1`/`-h2` names are not "only parsed": vLLM serves them.
   - **Confidence:** high for "whole".
3. **`schemes/__init__.py`.**
   - **Corrected destination.** `verity/` takes `ncp-v1`, `ncp-v1-shift24` and `pearl-c-sm120-v1-h2`, not
     `pearl-c-sm120-v1`. The other seven of today's nine go to `experimental/pouw/schemes.py`: `pearl-c-sm120-v1` (h0)
     plus the six the map names. The experimental registry also takes the served `-h1` and the unpromoted scheme.
   - **Answer to the question.** Two registries, the caller chooses, and nothing experimental fills.
   - **Also in `verity/`.**
     - `circuit.SCHEMES` (`ncp-v2`, `ncp-v2-shift24`; `pouw/ncp-v2-circuit` is merged) stays as the second guaranteed
       registry.
     - vLLM's `PPD.SCHEMES` must be derived from `verity/`'s registry instead of built on its own.
   - **Evidence:** §A 4 and §A 5.
   - **Confidence:** high on the direction; medium on h2-only (§E 8).
4. **`schemes/pearl_kw.py`.**
   - **Answer.** The split stands, with the line drawn precisely.
   - **Shared pieces → `verity/…/pouw/schemes/pearl.py`:**
     - `Reject`, `SIGMA_MIN`, `NOISE_NORM`, `R`, `TILE`, `WINDOW`;
     - `f32_bits`, `f32_of_bits`, `f32`, `bf16_mul`, `bf16_to_f32`, `f32_to_bf16`, `f32_to_fp8`, `fp8_to_f32`;
     - `hash_labelled`, `sample_line`.

     They are used by `pearl_c.py`, `pearl_c_debit.py` (`Reject`), `pearl_c_work.py` (`f32_of_bits`, `Reject`,
     `SIGMA_MIN`), `circuit/pc8.py` (`sample_line`) and vLLM's `pouw_pearl_c_screen.py` (`SIGMA_MIN`).
   - **To experimental with `pearl-fp8-v4`/v0:** `Device`, `H100`, `B200`, `ADA`, `DEVICES`, `replay`, `device_dot`,
     `parse_row`, `open_row`, `exact_norms`, `noisy_quantize`, `Built` and `delta_consts`.
   - **A second device set.** `pearl_kw` has its own device records (`pearl_kw.py:80-102`). v0 is their only Pearl-C user:
     `P.noisy_quantize(P.H100, …)` at `pearl_c.py:503`.
   - **Elsewhere.** The BF16/FP8 conversions may belong in core's FP module (core open question 1). The 14 benchmark
     scripts that `import pearl_kw as P` need their imports updated.
   - **Confidence:** high.
5. **`schemes/pearl_c.py`** (split v0 out, or keep it behind a refusal?).
   - **Answer.** Split it out.
   - **Evidence.**
     - v0 branches sit inside `PearlC.__init__`, `_forming`, `credit_of`, `_side`, `admissible`, `useful` and
       `line_norm`, and in `peel_a`/`peel_b` and `NAME`.
     - The constructor defaults to `forming="v0"`, `device=H100` (line 387). Lines 391 and 396 refuse v0 off the H100.
     - `pouw/pearl-c-h100-v0` is superseded.
     - Behind a refusal, the default constructor would still build the superseded scheme.
   - **Shape of the split.** `verity/` keeps a v1-only `PearlC` with no device default. It also keeps `LABELS =
     pearl-c/v0/…`, the seed labels v1 still uses as wire constants. `tests/vectors/pearl_c.json` checks that no byte
     moved.
   - **Confidence:** medium-high.
6. **`schemes/pearl_c_device.py`** (who passes the device in?).
   - **Answer.** The scheme object carries its device. The registry entry builds it (`_pearl_c(device=DEVICES[d])` in
     `schemes/__init__.py:27-28`, from catalog records), and every function takes the scheme or a `Device`, with no
     module-level import of a record and no default.
   - **Split the record itself.** It mixes device measurements with protocol parameters. Its docstring: "G, the prices,
     the k bound and the cap are statement parameters".
     - **To `catalog/devices/`:** `Prices` values, `atom` and `peel` (references to `verity.ml.tc.models`).
     - **Scheme or statement parameters in `verity/`:** `g`, `k_max`, `cap` and `standins`.
   - **Direct importers and call sites on main:**
     - `schemes/__init__.py:27-28`: `DEVICES[device]`.
     - `pearl_c.py:84`: `H100`, `H100_PRICES`, `PRICES`, `SM120_PRICES`, `Device`, `Prices`. H100 defaults at lines 147,
       168, 239, 254, 262, 346 and 387.
     - `pearl_c_debit.py:41`: `H100`, `Device`, `Prices`. Constants at lines 43-47. Defaults at lines 56, 118, 123, 149
       and 166.
     - `pearl_c_u.py:52`: `H100`, `Device`. Defaults at lines 130, 135, 156 and 204.
     - `pearl_c_work.py:76`: `SM120`, `Prices`, used at lines 217-220 (`SM120_LOOP_CAST_8P72`, `DRAW_WREF`).
     - `circuit/pc8.py:63`: `DEVICES`, used at lines 88, 159, 214, 290 and 345-348.
     - `circuit/rowk.py:54`: `DEVICES`, at line 323.
     - vLLM `protocol_options/pouw_pearl_c_device.py`: line 71 (`SM120`, `SM120_UNPROMOTED`), 108, 157 and 161.
     - Benchmarks: `exhaustion/window.py`, `pearl_c/{decode_served,twin}.py`, `pearl_c_sm120/{fixture,pearlc_arm,verify}.py`
       and `pearl_c_vllm/{e2e,panel_rows,profile_decode,served_debit,verify_run}.py`.
   - **The map's evidence needs a fix.** The certified γ reads Lean's `Sm120`, `DevicePricesLoop` and `devSm120v1`, not
     this Python record. The record's `SM120_PRICES.fadd = 8` is the credited price, while the γ is stated at the loop
     price `1047/125`, which `pearl_c_work` substitutes.
   - **Confidence:** medium.
7. **`schemes/pearl_c_debit.py`.**
   - **Answer.** Agreed. The H100 default has to go, and with it the module constants `G = H100.g`, `ATOM`,
     `CAP = H100.cap`, `ATOM_UNITS` and `ELEMENT_UNITS` (lines 43-47).
   - **Confidence:** high.
8. **`schemes/pearl_c_work.py`.**
   - **Answer.** Agreed, with one addition. `DRAW_WREF` is built at import from `SM120` (lines 217-220) and names a pinned
     statement, so it becomes a catalog entry keyed by (device, prices, cap). Its value is checked against the spec's
     `Prices.sm120Loop` and cast.
   - **Confidence:** high.
9. **`schemes/pearl_c4_replay.py`** (superseded tooling to delete?).
   - **Answer.** No. Its docstring calls it a development shortcut, but it is live: `benchmarks/pouw/pearl_c4/pearl_c4_arm.py:170`
     imports it (`write_dump`). It goes to `experimental/pouw/nvfp4/` with Pearl-C4, whose approach is parked.
   - **Confidence:** high.
10. **`circuit/plan.py`** (can it take the tile-check templates as data?).
    - **Answer.** Yes. `tile_layout(shape, w_ref)` imports `pc4`/`pc8` lazily and uses only `mod.units`, `mod.call` and
      `mod.weight`, so it can take that triple as an argument.
    - **Also.** It cites eight C-Flock audit-law pins (§A 1).
    - **Confidence:** high.
11. **`circuit/hashes.py`** (where do SHAKE256 and TurboSHAKE128 go?).
    - **Answer.** Split the module.
      - **To `verity/primitives/circuits/hashes.py`:** SHA-512 and SHAKE256, through `KeccakF1600`. `ncp2` uses `sha512`,
        `shake256`, `sha_words` and `keccak_lanes` for the call key K and the noise rows (`ncp2.py:57`), and ncp-v2 is in
        `verity/`.
      - **To experimental with `pc8`:** TurboSHAKE128 and `KeccakP1600R12`. They serve only `leaves` (Pearl-C's tile
        digest, for `pc4`/`pc8`) and the parked `pouw/ncp-v2-lowbyte-leaf`.
    - **Confidence:** medium-high. The gate format is circuits' call.
12. **`circuit/ncp2.py`** (does the guarantee's circuit stay in `verity/`, or does `verify` take it from a catalog entry?).
    - **Answer.** It stays in `verity/`. This disagrees with architecture's Q3 recommendation and core open question 2.
    - **Why.** `circuit.Traced` builds the Program itself for any (m, k, n), and `check_descriptor` refuses a descriptor
      whose digest differs from that Program (X-SPC-73). So the builder is already what the verifier trusts. With a
      catalog-by-digest design, each served shape would need a pinned digest, and m varies per call. Otherwise the
      builder stays trusted code under another directory's name.
    - **Importers:**
      - vLLM: `check/replay/pouw_circuit.py`, `program/registry/pouw_rows.py` and
        `protocol_options/{pouw_circuit,pouw_device,pouw_native}.py`;
      - the circuit package: `__init__`, `anchors`, `partition`, `plan` and `reference`;
      - `circuit_check.targets`.
    - **Confidence:** medium (§E 5).
13. **`circuit/words.py`, `boolean.py`.**
    - **Corrected destination.** Split `words.py`.
      - **With `ncp2` in `verity/`:** lines 44-209 (the 32-bit words, bytes and int7 entries, the accumulator,
        dequantization).
      - **With `pc4`/`pc8` in experimental:** the Pearl-C4 section (lines 210-245) and the Pearl-C section (lines
        246-298).
    - `boolean.py` is "PoUW's own word primitives … Pearl-C4's (`pc4`) and Pearl-C's (`pc8`) row units call", so it goes
      with them. Its importers are `test_circuit_boolean.py` and `circuit_check.targets`.
    - **Confidence:** medium.
14. **`circuit/leaves.py`.**
    - **Corrected destination.** `experimental/pouw/pearl_c/`, not `catalog/`.
    - **Evidence.**
      - Only `pc4` and `pc8` use it.
      - Its approaches `pouw/circuit-pc8` and `pouw/circuit-hidden-tile` are parked.
      - No pin reads `TileCheck*`.
    - **Confidence:** medium-high.
15. **`circuit/pc8.py`.**
    - **Corrected destination.** Both checks, the sm_120 one included, go to `experimental/pouw/pearl_c/`.
    - **Evidence.**
      - `circuit.SCHEMES` refuses it: "No scheme of theirs in SCHEMES yet".
      - No vLLM option imports `pc8`, `pc4` or `rowk`.
      - `pouw/circuit-pc8` is parked.
      - No pin reads `TileCheck8`, on main or on slice 6.
    - It is promoted together with a tile-check guarantee, if Daniel wants one (§E 3).
    - **Confidence:** medium-high.
16. **`circuit/rowk.py`.**
    - **Corrected destination.** Experimental. `pouw/circuit-row-k` is parked and "opt-in", and the module imports `pc4`,
      `pc8` and `DEVICES` (line 323).
    - **Confidence:** high.
17. **`tests/*_vectors.py`, `quicknet.py`, `pearl_vectors.rs`, `ncp_lean.py`.**
    - **Answer.** Most of these are tests of the trusted code's wire formats, so they stay beside its tests. Core keeps
      `tests/ir/format_vectors.json` the same way. They are not `tools/catalog/` builders.
    - **Stay with `verity/`'s tests:**
      - `identifier_vectors.py`: C-Flock's verifier compares its output byte for byte.
      - `pouw_vectors.py` (`ncp.json`).
      - `pouw_regions_vectors.py`: C-Flock's public-input regions.
      - `ncp_lean.py`: a Python↔Lean difftest over `Pouw.Protocol.NCP.RouteU`.
      - `pearl_c_vectors.py`: v1; any v0 cases go with v0.
      - `quicknet.py` is not a generator; it loads recorded drand rounds for tests.
    - **To experimental with their schemes:** `pearl_vectors.py`/`.rs` (Pearl's Rust, `pearl-fp8-v4`),
      `pearl_c_u_vectors.py`, `pearl_c4_vectors.py`, and `pouw_rows_vectors.py` (`leaves`).
    - **Confidence:** medium.
18. **`tests/vectors/*.json`.**
    - **Corrected destination.** The same split as entry 17. `identifier_v1`, `ncp`, `ncp_lean`, `pouw_regions`,
      `pearl_c` and `quicknet` stay with `verity/`'s tests. `pearl_kw`, `pearl_c_u`, `pearl_c4` and `pouw_rows` go to
      experimental. The skip vectors go with whichever module reads them.
    - **Confidence:** medium.

Checked, and I agree with the map: `protocol.py`, `audit.py`, `beacon.py`, `bls12_381.py`, `schemes/ncp.py`,
`pearl_c_u.py`, `pearl_c4.py`/`pearl_c4_c_L.py`, `circuit/__init__.py`, `anchors.py`, `partition.py`, `reference.py`,
`pc4.py`, `PROTOCOL.md` and `tests/`.

## D. PoUW Lean (`protocols/pouw/lean/`)

1. **The 33 read modules** (the device instances).
   - **Answer.** All 33 stay spec, but most of the "device instance" modules aren't instances:
     - `DeviceRev1` (121 lines) and `DeviceKernelWref` (55 lines) are generic over `d : PearlCDevice`. They are protocol
       definitions. Confidence high.
     - `Sm120` (39 lines; `sm120E4m3K32`, `sm120E4m3`, read by 240 pins) and `DevicePricesLoop` (`Prices.sm120Loop :=
       ⟨1047/125, 2, ⟨40, 2⟩⟩`, read by 161 pins) are the instance the guarantee is about. They stay spec (§A 3).
     - `Device.lean` (205 lines) mixes the generic `PearlCDevice` and `Prices` structures with instances (`Prices.h100`,
       `devH100`, `devSm120v1`, `devSm120v2`, `devAt`), and it imports `Tile`. Split it: the generic part and
       `devSm120v1` stay spec, and the other instances go with their pins.
   - **Slice 6 changes this pin's records.** It changes definitions the certified γ reads:
     - `Defs`: `FormChain*`, `Noise*`, `lineCodes`, and a new `mulCode`;
     - `Device`: `unitUsefulDev`, `pearlCProtocolDev`;
     - `DeviceRev1`: `pearlCProtocolDevRev1`;
     - `FormingPDefs`: `atomMixP`, `saltDeadP`;
     - `Game`: `Protocol`, `weightOK`, `InDomain`;
     - `Instance`: a new `RowOK` and `codeBf16`, plus `unitUseful` and `pearlCProtocol`;
     - `SaltDead`: four definitions.

     So the certified γ's read records change when #1132 lands, which needs a statement reviewer, and Daniel's DM fires
     then. The five pins' own signature records do not change.
   - **Confidence:** medium-high.
2. **Missing row: the import closure** (corrects the "NCP, Barrier, TileBound, M1, Witness and Deadline families" row).
   - **The problem.** 15 modules sit in the import closure of the 33 read modules. A spec module can't import the math
     package, so they must stay spec:
     - `Assumptions.NCP.{Assumptions, Chain, GamePinned, RouteUGame, RouteUWord}`;
     - `Assumptions.Pinned`;
     - `Protocol.Barrier.Defs`;
     - `Protocol.M1`;
     - `Protocol.NCP.{Pinned, Relation, Witness, Word}`;
     - `Protocol.PearlC.Tile`;
     - `Protocol.Witness.{Copy, Model}`.
   - **The import chains:**
     - `Guarantees.Game` imports `Assumptions.Pinned`, which imports `M1` and `Witness.*`.
     - `Guarantees.NCP` imports `RouteUGame`, `RouteUWord`, `NCP.Pinned` and `NCP.Relation`, which pull in the rest of
       the NCP chain and `Barrier.Defs`.
     - `Assumptions.PearlC.TTOut` and `Protocol.PearlC.Device` import `Tile`.
   - **The way out.** Trim `Guarantees.Game`'s and `Guarantees.NCP`'s imports down to what the guarantees read. After
     that the 15 can go to `security_proofs/pouw/`. Whether a change of imports alone moves a record is lean's call
     (§E 4).
   - **Confidence:** high, from `reads` and the imports at `9400e83d5`.
3. **Tile-check modules** (which does `EndToEnd` read after slice 6?).
   - **Answer.** None (§A 2).
     - `Tile` stays spec only because of the import closure (entry 2). It is read by 189 pins, none of the five kept, so
       the map's "no pin reads today" is wrong for it.
     - The other seven go to `security_proofs/pouw/`, or to experimental Lean beside `pc8`. They are `RowCircuit`,
       `TileCircuit`, `WholeCircuit`, `TileCheck`, `TileCheck8`, `RowSem` and `RowPrims`.
   - **Confidence:** high.
4. **`Pouw/SecurityProofs/Dimension/Lifting.lean`.**
   - **Answer.** It goes to `security_proofs/pouw/` at the split. Only `Pouw/SecurityProofs.lean:21` imports it, no spec
     module does, and it isn't in `reads`. It sits in the spec today only because it is in `layers`.
   - **Confidence:** medium-high; lean's call.
5. **The Dimension and route-U pipe family** (spec through S3.1, or move on the validator's report?).
   - **Answer.** Move it at S3.1. No kept pin reads it: `Protocol.Dimension.Defs` is read by 111 pins and
     `Guarantees.Dimension` by one (`A2WordsIff`). None of it is in the kept reads' closure, and outside Lean only
     `protocols/pouw/PROTOCOL.md` names it.
   - **Confidence:** medium-high.
6. **Pearl-C modules no kept guarantee reads** (are `Hidden*` and the cap assumptions future reads?).
   - **Answer.** Not of `EndToEnd` or the certified γ.
     - **Hidden tile.** `Hidden` and `Assumptions.PearlC.HiddenTile` are read by `gammaHidden_of_sampled_all`,
       `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192` and `tileProofSoundAll_of_tileGame`, and `HiddenTileGame` by the
       last of these. Nothing outside Lean cites them, and `pouw/circuit-hidden-tile` is parked, so they leave.
     - **The cap.** `HonestCap` and `Completeness` are read by `completeSampledDevRev1K` and
       `pearlCCompleteSm120v1LoopCast8p72Rev1Cap1000_{llama31_8b,qwen3_8b}`, and `pearl_c_work.py:214-215` cites
       `HonestTileCapRate` for the served ε. Under the 2:03 ruling these are candidates to keep (§A 1).
     - **The chain cap.** `DeviceChainCap` (27 pins) and `DeviceChainCapKernel` (6) belong to the parked sm120 v2 chain
       cap, so they leave.
   - **Confidence:** medium.
7. **The NCP family** (does `GammaFromTTNCP_U_v1` read `Assumptions.NCP.Assumptions` or `RouteUGame`?).
   - **Answer.** Neither. It reads `Assumptions.NCP.RouteUAssumptions`, along with `Guarantees.NCP`, `Basic.*`, `D1`,
     `Game.{Defs,Params}` and `NCP.{Defs,Protocol,RouteU}`. Both modules still stay spec through the closure (entry 2).
   - **Confidence:** high.
8. **`scripts/fp8atom_vectors.py`, `h1t_vectors.py`, `row_prims_vectors.py`, `fp8atom_cover.json`.**
   - **Answer.** Each goes with what it generates.
     - `fp8atom_*` generates the `Fp8Atom` vector modules, which no kept pin reads. The kept pins read `Atom`, `E4M3` and
       `Fp32`. It goes wherever those vectors go.
     - `h1t_vectors.py` goes with the H100 `-h1` family, to experimental.
     - `row_prims_vectors.py` imports `circuit.words`' Pearl-C section, so it goes with `RowPrims` and `pc8`.
   - **Confidence:** medium.
9. **`lean-audit.json`** (the spec keeps the five).
   - **Answer.** Five, plus whatever §A 1 decides. pouw-lock should also keep this package's `reads` list by hand until
     the validator derives it.
   - **Confidence:** medium.

## E. `benchmarks/pouw`

1. **`nvfp4_sm120/`** (could the plain FP8 baseline stay in `benchmarks/`?).
   - **Corrected destination.** The whole directory stays in `benchmarks/pouw/`. It is not Pearl-C4, which lives in
     `pearl_c4/`.
   - **Evidence.**
     - `harness/native/build.sh:29` builds `../../nvfp4_sm120/nvf4_plain.cu` with `mainloop_nvf4.cuh` into the harness's
       baseline registry (`cutlass_registry.cu`).
     - `baselines.py:360`: "`verity` for nvf4_plain.cu's (#543's NVFP4, #570's FP8)". `test_harness.py:844` checks it.
     - `pouw/kernel-nvfp4-sm120-plain` is merged.
     - Moving it would make the harness build from `experimental/`.
   - **Confidence:** high.
2. **`harness/`** (does the gate sit in the registry's build or in `tools/`? Where do `price_twins` go?).
   - **There are two gates.**
     - **Kernel build gate.** `pearl_c_sm120/sass_gate.py`, run by `pearl_c_sm120/build.sh:25`, checks the QMMA/HMMA
       counts and that nothing spills. It goes with the kernel (the map has it).
     - **FTZ/MUFU gate on timed binaries.** `harness/sass_gate.py` with `sass_pins.json` and `ieee_pin.*` is the gate
       that `bench.py` runs on every timed arm's binaries (lines 51, 917 and 1278). `ledger.py` records its version (lines
       258 and 350), and `tools/tc_probe_fp4` uses it too. P5 wants "the SASS/FTZ gate on every cache fill", so it goes
       in the kernel registry's build, with the harness calling it there.
   - **`price_twins.py`/`.json`.**
     - They stay in the harness, as the readers. `ledger.py` and `exhaustion/audit.py` use them.
     - The table already marks each twin `pinned` or `staged`. Once `DevicePrices`' pins leave the lock, the ledger would
       publish staged γ unless it refuses them (§A 1).
    - verity#1154 renames the certified γ's pin to `Pouw.SecurityProofs.PearlC.GammaSm120v1LoopCast8p72Rev1Cap1000_8192`.
      `price_twins.py` reads γ off a pin's signature, which is now `X : G`, so it must read the `Guarantees` definition
      instead. Settle this together with the lock's size.
   - **Confidence:** medium.
3. **`kernels/pouw_gemm.cu`** (is it a registry entry?).
   - **Answer.** No. It stays in `benchmarks/`.
   - **The map's evidence is wrong.** `e2e_audit.py` is not its only user. `kernels/__init__.py`'s `load` is used by
     `check_route_u_sass.py`, `e2e_audit.py`, `gemm_bench.py`, `route_u_bench.py`, `ncp2_gpu_bench.py:391` and
     `tests/test_route_u_shift.py`. Research's `tools_registry` lists `benchmarks.pouw.tool` (the `pouw_gemm` tool).
   - **Why it isn't an entry.** No vLLM option loads it: there is no `route_u` in `integrations/vllm`. The kept NCP
     guarantees are about the scheme, not this binary. `pouw/kernel-pouw-gemm-4090` is merged as a benchmark route.
   - **Confidence:** medium.
4. **`exhaustion/`** (does a cited result rest on `exhaustion/audit.py`?).
   - **Answer.** Not yet. It stays in `benchmarks/`.
   - **Evidence.**
     - Its γ is the kept pin: it is looked up through `price_twins.lookup`, and `test_exhaustion.py:111` asserts
       `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192`.
     - Each tile is checked by `verity_pouw.audit.Verifier(...).check_tile`, which is already in `verity/`.
     - Nothing outside `benchmarks/pouw/` reads the certified fraction, and `pouw/pearl-c-sm120-window-60pct` was killed.
   - **If a fraction is ever cited,** steps 1-2 of its audit move into `verity/…/pouw/audit.py`: the salt from
     `derive(source, SEED_DOMAIN, …)`, the clock, and the draw over the window root.
   - **Confidence:** medium.
5. **`pearl_calibration.py`.**
   - **Corrected destination.** It stays in `benchmarks/`, not `tools/pouw_calibrate/`. It is a benchmark of Pearl's own
     miner against plain vLLM on a B200 (`r20260928-075340-f1bb`), run in Pearl's environment. It calibrates no
     parameter and builds no entry. `tool.py` registers it as `pouw_pearl_cal`.
   - **Confidence:** medium.

Checked, and I agree with the map: `pearl_c_sm120/` with the hash headers, `pearl_c/` (H100), `pouw_hash/`,
`pearl_c4/`, `pearl_c_vllm/` and the top-level scripts.

## F. Rows in the core and backends maps

1. **Core `evaluation/batch.py`** (does `register_kernel` move to `verity/kernels/registry`?).
   - **Answer.** PoUW has no stake: no PoUW code calls `register_kernel`, and its only caller outside core is vLLM's
     `program/kernels/kernel_registry.py`. P5's wording supports the move, but that is circuits' call.
   - **Confidence:** medium.
2. **Core `ml/fp32.py`** (consolidate the duplicate bit functions now, or in step 5?).
   - **Answer.** In step 5, bridged by vectors, and not in the move train.
   - **Evidence.** `ncp2` registers `F32Mul_v2` and `Bf16Add_v1` from it (`ncp2.py:51`), and `pc4`/`pc8`/`rowk` use
     `F32*V2`. The ncp-v2 Program's digest depends on those Definitions, so the consolidation must keep the digest.
   - **Confidence:** medium.
3. **Core `ml/kernels.py`.**
   - **Answer.** Agreed: the generic numpy kernels become the `tc` entries of `verity/kernels/`.
   - **Evidence.** PoUW uses `f32_to_bf16_rn_batch` (vLLM's `pouw_native.py:35`), and the benchmark twins use
     `group_sum_total_batch`, `block_scaled_batch` and `chain_batch`.
   - **Confidence:** medium.
4. **Core `ml/tc/__init__.py`, and open question 1** (where do the FP and tensor-core semantics live?).
   - **Answer.** PoUW supports the split: the generic interpreter goes to `verity/primitives/fp/`, and the instances to
     `catalog/hardware/tc/`.
   - **Evidence.**
     - PoUW's trusted Python uses the generic `ml.tc.fp32` (`pearl_c.py:79`, `pearl_c_debit.py:38`) and `words.py` uses
       `ml.tc.cast`/`ml.tc.fp32`.
     - Only `pearl_c_device.py:30` uses instances (`BLACKWELL_SM120_E4M3_M16N8K32`, `HOPPER_BF16_M16N8K16`, …), and that
       record is bound for the catalog anyway.
     - PoUW's Lean does not read core's TC spec. The certified γ reads PoUW's own `Fp8Atom.{Atom,E4M3,Fp32}`.
   - **Confidence:** medium.
5. **Core `ml/boolean/fp4.py`, and open question 6** (is NVFP4 catalog or experimental?).
   - **Answer.** PoUW does not bind this module, so its fate is C-Flock's and circuits' call.
   - **Evidence.**
     - No PoUW module imports `verity.ml.boolean.fp4` or the NVFP4/MXFP4 coordinates. The importers are C-Flock's
       `unit_fp4`, `class_statement` and `pod/gemm_{fp,hill}.py`, core's tests and `circuit_check`.
     - Pearl-C4 uses `ml.tc.models`' `BLACKWELL_SM120_NVF4`/`MXF4` and its own `pc4`.
     - PoUW's NVFP4 is experimental: `pouw/pearl-c4-nvfp4` is parked and `pouw/pearl-c4-mxfp4` was killed.
   - **Confidence:** high, on PoUW's side.
6. **Core `fixtures/bench-instances/`.**
   - **Answer.** No PoUW reader: no PoUW module, `benchmarks/pouw` script or vLLM PoUW option reads it. It is infra's and
     proofs' call.
   - **Confidence:** high.
7. **Core `tests/ml/fixtures/gemm-B1-…`** (is it a row capture under the 1:30 ruling?).
   - **Answer.** It is not a served-row capture.
   - **Evidence.** It is 30 authenticated GEMM coordinates from the RTX 4090 eager vLLM port: for each, `x.u16`,
     `w_row.u16`, `out_row.u16` and `fixture.json`, in 117 files totalling 718,696 bytes. The Merkle openings were not
     copied. So it is already shrunk to what the coordinate relation reads, and it stays as a hardware-semantics test
     fixture.
   - **Confidence:** medium; circuits' call.
8. **Backends `soundness/…/Audit.*`.**
   - **Answer.** There is nothing to decide for the move. The count is 38 files, not 27, and the Python cites the pins
     listed in §A 1.
   - **Confidence:** high.
9. **Backends `commit/challenge.py`** (verifier draws or prover draws?).
   - **Answer.** The non-legacy forms are the verifier's draws, or public coins that anyone recomputes: `derive` from a
     beacon round published after the run root was registered, or from an auditor key. `replay_key` is sampled proofs'
     `vu_key`/`select_verification_units`. Those go with sampled proofs, so `law.py` becomes trusted code when `LEGACY`
     flips (§B 5).
   - The legacy forms are Fiat–Shamir over the prover's own commitment, kept for replay until decision 42.
   - **Confidence:** medium.
10. **Backends `protocol_options/pouw_native.py`** (is it the reference `pouw_device` is gated against?).
    - **Answer.** Yes, leaf for leaf, but it is itself a fast path.
    - **Evidence.**
      - `pouw_device.first_difference` gates each build against `pouw_native` (`test_pouw_device.py:54`, `:136`,
        `:146`).
      - `test_pouw_native.py` checks `pouw_native` against the Programs through `verity.evaluation.evaluate` and
        `circuit.reference`.
    - **So, under P5,** the reference is the Program plus `circuit/reference.py`, and `pouw_native` is a numpy kernel
      entry with that test.
    - **Confidence:** medium-high.
11. **Backends `pouw_device.py`, `pouw_cuda/`.**
    - **Answer.** Agreed: split first. `pouw_device.py:29-30` imports `pouw_circuit` (`unit_leaf`) and `pouw_native`, so
      the unit-leaf functions have to move with the kernel entry.
    - **Confidence:** medium.
12. **Backends `pouw_pearl_c_{device,graphs,host,screen,triton,whole}.py`** (does the torch and Triton screen sit on a
    path a result rests on?).
    - **Answer.** Not for soundness.
    - **Evidence.**
      - `screen` only pre-filters rows. The band's rows are decided exactly by `pearl_c.live_row` (`screen.py:77-83`).
      - The verifier's `PearlC.admissible` (`pearl_c.py:516-522`) recomputes the noise floor and `live_row` exactly on
        every opened tile.
      - So a wrong screen changes the honest prover's records (completeness, credited rows), not what the verifier
        accepts.
    - **Placement.** It can be an honest-prover kernel entry. P5's "torch is a container only" applies to trusted code,
      and this is not trusted code.
    - **Confidence:** medium.
13. **`tools/tc_probe_fp4/`** (live or killed?).
    - **Answer.** They are measurement tools, not schemes: F1 rates, F2 Strassen and F3 LUT-GEMM search for attacker
      shortcuts on NVFP4, and W1 measures prices. They stay in `tools/tc_probe_fp4/`, since P3 makes capture a tool.
    - **Evidence.**
      - Core's `pyproject.toml:30` lists `tools/tc_probe_fp4/probe.py` as a test input.
      - `ml/tc/models.py:810` and `:875` cite its runs.
      - `tools_registry` names `tc_probe_fp4` and `tc_price_fp4`.
    - **Status.** The registry has no approach for F1–F3 or W1, so I can't confirm whether they are live or killed.
      Their consumer, Pearl-C4, is parked.
    - **Confidence:** low-medium.

## G. The map's open questions for compute-accounting

1. **The registry:** two registries, the caller chooses explicitly, and nothing experimental fills (§A 4, §C 1, §C 3).
2. **The device record:** the scheme carries its device, and the record splits (§C 6). The certified γ is stated over a
   device parameter, and its instance at `Sm120` is the guarantee in the lock. `Sm120` is catalog Lean, keyed by
   definition hash (§A 3, as ruled at 22:58Z).
3. **`ncp2`:** it stays in `verity/` (§C 12).
4. **Slice 6:** `EndToEnd` reads no tile-check module, and only `Tile` stays, through the closure. `Hidden*` aren't
   future reads; the cap pins are candidates (§A 2, §D 3, §D 6).
5. **Sampled proofs:** it goes under `verification/`. `law.py` and `plan.py` go to experimental until decision 42, and
   neither is deleted (§B 1, §B 5, §B 6).
6. **`pouw_gemm.cu` and the exhaustion audit:** `pouw_gemm.cu` is not a registry entry, and no cited result rests on
   `exhaustion/audit.py` yet (§E 3, §E 4).

## Decisions that need Daniel or another owner

1. **Daniel and pouw-lock: the lock's size.** Served code, the attempt ledger and a rendered table read pins beyond the
   five (§A 1). Either the lock keeps them, or `pearl_c_work`, `ledger.py`/`price_twins` and `plan.py` cite only kept
   pins.
2. **Daniel (statement reviewer):**
   - The γ is restated over a device parameter with the instance at `Sm120` in the lock (§A 3). This needs Daniel's
     review only if `--moved` doesn't print the instance as the same statement.
   - Separately, #1132 changes definitions the γ reads, so its read records change and need review when it lands
     (§D 1).
3. **Daniel: is a tile-check guarantee wanted?** If not, `pc8`, `rowk`, `leaves`, `boolean`, the Pearl-C half of `words`
   and TurboSHAKE128 go to experimental, and seven tile Lean modules leave the spec (§A 2, §C 11–16).
4. **lean:**
   - Trim `Guarantees.Game`'s and `Guarantees.NCP`'s imports so the 15 closure modules can leave (§D 2).
   - Does an import-only change move a record?
   - `Lifting` goes to `security_proofs/pouw/` (§D 4).
5. **architecture and circuits:** `ncp2` stays in `verity/`, against catalog-by-digest (§C 12).
6. **circuits:**
   - Split `hashes.py` (§C 11).
   - Consolidate `ml.fp32` in step 5, keeping digests (§F 2).
   - `gemm-B1` (§F 7).
7. **proofs, with pouw-lock:** the C-Flock audit-law pins that `plan.py`, `draw.py` and `consumers.py` cite (§A 1).
8. **The vLLM PoUW option's owner:**
   - `pouw_pearl_c_device.SCHEMES` and `scheme_of` go through `verity/`'s registry.
   - The served `-h1` and `sm120-unpromoted` move to the experimental registry or stop being served (§A 4, §A 5).
   - Also: is `-h1` still served on purpose, now that `pouw/pearl-c-hash-h1` is superseded?
9. **Daniel or the coordinator: decision 42's timing.** If the `LEGACY` flip is close, `law.py` and `plan.py` stay in
   `verity/` instead of making a round trip through experimental (§B 5).
