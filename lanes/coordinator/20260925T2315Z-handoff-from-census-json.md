---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
created: 2026-09-25T23:15Z
updated: 2026-09-26T01:40Z
---

# census-json: both PRs pushed and ready. Merge after the 01:00Z switch, #39 first.

**To:** research coordinator (bc-8ece7cde).

## 01:40Z: merged, plus one follow-up PR

#39 and #40 merged at 01:29Z with their final heads (`669ffaae`, `e9792869`). The merge-commit titles quote the PRs' first descriptions ("verity_census distribution", "configurations"), but the trees are current.

The "input set" rename is a follow-up, [PR #44](https://github.com/danielreuter/verity/pull/44) (`cursor/input-sets-574a`, off main), ready to merge:
- `census/input_sets.json` and its schema;
- `census.INPUT_SETS`;
- `input_set` fields in the entities JSON.

Recorded names (`instance-equiv/v1`, `instances` refs, `tier`) and printed strings are unchanged. Renders are byte-identical.

## Push status

Both branches are on origin:
- [PR #39](https://github.com/danielreuter/verity/pull/39) `cursor/census-registry-574a` @ `669ffaae`
- [PR #40](https://github.com/danielreuter/verity/pull/40) `cursor/tables-json-574a` @ `406c1980`

The GitHub token came back at about 00:45Z, so the fallback bundle has been deleted. The PR descriptions are current.

## Since 00:45Z: statements (#40)

- **`statements`:** each statement id is `<subcircuit>+<scheme>`, and it carries its scheme's assumptions.
- **Result keys:** each result is keyed by backend × statement × instance set × prover hardware.
- **Assumption sets:** a result's full set is its backend's plus its statement's. Backend profiles now leave out statement-commitment hashes, which belong to the statement.
- **Configurations:** no longer emitted. They are an implementation detail, listed only as `implementations`.
- **Table 1:** lists backends.
- **Checks:** markdown and raw JSON are still byte-identical to main.

## [PR #39](https://github.com/danielreuter/verity/pull/39) census (at `669ffaae`)

`census/` is data only: five JSON files (hardware, datatypes, networks, subcircuits, instance_sets), a JSON Schema for each, and a README. What the files carry:
- **Subcircuits:** `subcircuits.json` holds subcircuit templates, currently one, `gemm-coordinate`, with typed parameters `K`, `datatype` and `semantics`. Under it are the bound subcircuits:
  - each has a stable id (`gemm-coordinate/k1536/sm90-wgmma-e4m3`), a display name ("GemmCoordinate<1536> · sm90 wgmma · FP8 (E4M3)"), `legacy_target` and `fidelity_notes`;
  - the only fidelity note so far is H100 BF16: "models mma; vLLM runs wgmma".
- **Instance sets:** named by dataset, each with its `provenance` (captured or synthetic) and the id of the subcircuit it belongs to.
- **Display names:** datatypes show the common name first, then the format ("FP8 (E4M3)"). Hardware has short names ("H100 SXM5").
- **No units:** the census encodes none, and a test checks it.

Core never reads `census/` (boundary test). The renderer reads it with `verity_numerical.bench.census`.

## [PR #40](https://github.com/danielreuter/verity/pull/40) entities JSON (at `406c1980`; the statements change is summarised above)

`views --format entities` follows the ontology's "A result" and "Presentation rules":
- **`results`:** every admissible backend's best result, not only each family's pick (`best` marks the pick). Each result has:
  - its `backend`, and a row `key`: subcircuit id, template, parameters, hardware, instance set, scheme;
  - `hardware` (the semantics chip, which supplies N) and `prover_hardware` (which supplies P);
  - the instance set with its provenance;
  - soundness: the whole-cell bound, plus the per-proof bound where the result records `security.per_proof_total_log2`; otherwise it is null and not derived;
  - native N as `work-model/v0` plus a census peak id;
  - phases, with fused stages as a span, "Other" clamped or flagged, `other_raw`, and setup in its own field.
- **Table 2 and 3 cells** use the same keys and name their backend.
- **`backends`:** `A-route-a` is a composed backend. It renders in the A-GKR column, and its soundness also rests on C-Flock's assumptions and the sigma link's. Other backends: `A-fs`, `B-interactive`, `B-fs`, `C-interactive`, `D-fs`.
- **`schemes`:** ids name the leaf hash (`frame-v3/blake3-keyed`, …), with the tree and leaf hashes and a structured `algebraic` flag.
- **blake3-xob:** decided from the code. It commits keyed BLAKE3's bytes (same schema and params digest in `ligero-verify/src/leaf.rs`; `conformance_test.py` asserts this), so it is a circuit of `frame-v3/blake3-keyed`, not a new scheme. A test checks `leaf.rs`.
- **Also present:** `backend_families` (A–D), `subcircuits` (display names, fidelity notes, provenance), `best_standard_hash`, `claims` (the ids come from `verity.claims` in core), `census`, `provenance`.

## Evidence
- **Renders:** markdown and raw JSON are byte-identical to main. `views` under the spec, legacy and unfiltered rules, the frozen `tables`, and parity all match on a synthetic store. Please still run `views --parity` on the control pod after merging.
- **Tests:** 1,620 passed. The only failures are three that main already has: the `test_evaluation` kernel list and `test_repository` ×2. `test_notes`: 61 passed.

## Open decisions and follow-ups
- **Markdown columns:** Table 2 still reads SP1 and Flock, in the old order. Renaming the published columns is a labelled render change and needs a decision.
- **Instance sets:** ids no longer encode units, but the `tier` field keeps the fixtures' real tier names (`vu-k1536…`), which recorded results match on.
- **Printed wording:** three printed strings still say `Target.native_peak`. They were kept so renders stay byte-identical.
- **Claim ids beyond the site's nine:** `rs-proximity-udr`, `rs-proximity-johnson`, `logup`, and `sis/ajtai-n{64,128}`.
- **Template id:** it is now `gemm-coordinate` (kebab-case), to match the requested subcircuit id form. The terminology lane's Glossary wasn't on main when checked, so please check the naming against it once it lands.

## After the switch and both merges (control pod)

~~~sh
python -m verity_numerical.bench.views --root $ST --published --format entities > <this folder>/<stamp>-tables.json
~~~

The synthetic sample `20260925T2315Z-sample-tables-entities-synthetic.json` in this folder shows the output shape at `406c1980`; its numbers aren't real.
