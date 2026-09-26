---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
created: 2026-09-25T23:15Z
updated: 2026-09-26T00:10Z
---

# census-json: both PRs ready. Merge after the 01:00Z switch, #39 first.

**To:** research coordinator (bc-8ece7cde). This reflects every direction up to 00:05Z:
- the census is data only;
- families are A-D, with instances per interaction mode;
- datatype and hardware display names;
- the subcircuit rename;
- scheme entities;
- circuits' kind, silicon target and target fields.

Neither PR touches the switch. Don't move `/workspace/steward/verity` onto them until the switch recipe has finished.

## [PR #39](https://github.com/danielreuter/verity/pull/39) (`cursor/census-registry-574a` @ `6cf47082`)

**The `census/` directory** is data only, with no Python, so it can move to its own repository unchanged. It holds:
- five JSON files: `hardware`, `datatypes`, `networks`, `subcircuits` and `instance_sets`;
- a JSON Schema for each, under `schemas/`;
- a README with the id scheme and the sourcing rules.

**Notable ids and displays:**
- the subcircuit is `subcircuit/gemm-coordinate-k1536`, and no ids encode units;
- instance sets are named by dataset, such as `bench-instances-fp8-ada-v1`;
- datatypes display as `BF16`, `FP8 (E4M3)` and `FP4 (NVFP4, E2M1)`;
- hardware has short names, such as `H100 SXM5`.

**Readers:**
- The renderer and benchmarks read the files with `verity_numerical.bench.census` (a few lines), and tests validate the files against the schemas.
- The docs site reads the same files.
- Core never reads `census/`, and a boundary test enforces it. `Target` names only its `anchor_device`, and `contract.native_peak_of(target)` picks the matching census line.

## [PR #40](https://github.com/danielreuter/verity/pull/40) (`cursor/tables-json-574a` @ `6552b001`, contains #39)

`views --format entities` is the docs site's JSON. Its main sections:
- **`instances`:** one per family and interaction mode (`A-interactive`, `A-fs`, `B-interactive`, `B-fs`, `C-interactive`, `D-fs`), with the claims written out in full.
- **`circuits`:** separate `subcircuit_kind`, `silicon_target` and `target` fields, plus the hardware short name and datatype display.
- **`schemes`:** each scheme's assumptions, taken from the code. For example, BLAKE3 rows rest on `cr/sha-256` and `cr/blake3`, which confirms the site's reading.
- **`results`:** keyed by scheme id, with their instance.
- **`best_standard_hash`:** the best standard-hash cell per family and circuit.
- **`tables`:** every printed cell.

`verity.claims`, in core, is the source of the claim ids, and the site should import them from the render.

The steward's `published = "views"` entry also writes `<stamp>-tables.json`.

## Evidence
- Markdown renders are byte-identical to main: `views` under the spec, legacy and unfiltered rules; the raw JSON; and the frozen `tables`. Parity is ok.
  - This was checked on a synthetic store of 124 results, since there's no evidence store on this VM. Please run `views --parity` on the control pod after merging.
- The broad test run passes except for three failures that main already has: the `test_evaluation` kernel list and `test_repository` ×2.

## Open decisions and follow-ups
- **Families are renamed only in the JSON.** The markdown's Table 2 columns still read A-GKR, B-Ligero, SP1, Flock, in that order. Renaming the published columns to the lettered names is a render change and needs a labelled decision; `table2.column_labels` maps the two sets of names.
- **An instance's properties are those all its members share.** Its assumptions are the union across members, and each assumption lists the configurations that cite it.
- **Instance-set ids and tiers differ.** The ids no longer encode units, but the `tier` field keeps the fixtures' real tier names (`vu-k1536…`). Those are external identities, and renaming them would break matching against recorded results.
- **Stale wording in renders.** Three printed strings still say `Target.native_peak`: the frozen caption, its markdown line, and the `WORK_MODEL` footnote. Changing them changes render bytes, so they're left for a labelled text change.
- **Extra claim ids.** Core emits five assumption ids beyond the site's nine: `rs-proximity-udr`, `rs-proximity-johnson`, `logup` and `sis/ajtai-n{64,128}`. The site should add them or ask us to drop them.

## After the switch and both merges (control pod)

~~~sh
python -m verity_numerical.bench.views --root $ST --published --format entities > <this folder>/<stamp>-tables.json
~~~

**Synthetic sample:** `20260925T2315Z-sample-tables-entities-synthetic.json` in this folder shows the current output shape. It's built from a synthetic store, so none of its numbers are real.
