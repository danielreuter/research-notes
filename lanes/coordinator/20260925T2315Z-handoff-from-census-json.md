---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
created: 2026-09-25T23:15Z
updated: 2026-09-25T23:35Z
---

# census-json: both PRs reworked and ready. Merge after the 01:00Z switch, #39 first.

**To:** research coordinator (bc-8ece7cde). The rework follows Daniel's decision: the census is not part of core. Neither PR touches tonight's switch. Don't move `/workspace/steward/verity` onto either PR until the switch recipe has finished.

## [PR #39](https://github.com/danielreuter/verity/pull/39) (`cursor/census-registry-574a`)

**What it adds.** `census/` is a new top-level distribution: `verity-census`, imported as `verity_census`, a uv workspace member next to `tools/research`.
- It holds four JSON data files: hardware, networks, workloads and instance sets. Every entry has a stable id and its sources, and hardware lines also carry a methodology.
- A thin typed loader reads them.

**Dependency direction.** The census imports nothing from Verity, and core never imports the census. A test on each side enforces this, like the one for `tools/research`.

**Core takes the numbers as parameters.**
- `Target` no longer carries a peak. It names only its `anchor_device`, and `NativePeak` is gone.
- `contract.native_peak_of(target)` returns the census line for the anchor device and the target's operand dtype.
- `latency.pipeline` takes `native_s_per_vu` as a parameter.

## [PR #40](https://github.com/danielreuter/verity/pull/40) (`cursor/tables-json-574a`, contains #39)

`views --format entities` is the docs site's JSON. The reworked census is merged in.

Each configuration's `claims` is a list of properties. Each property lists the assumptions it rests on, and each assumption has:
- a `verity.claims` id;
- a role copied from what the code declares, left empty where the code declares nothing;
- its text.

Properties: soundness (with its bound), ZK, non-interactive or designated-verifier, and transparent setup.

The site's nine assumptions all resolve: `cr/{sha-256,sha-512,blake3,blake2b,poseidon2-babybear,poseidon2-koalabear}`, `xof/shake-256`, `random-oracle` and `honest-verifier`. Core also emits `rs-proximity-udr`, `rs-proximity-johnson`, `logup` and `sis/ajtai-n{64,128}`; the site should add these or tell us to drop them. Beacon, auditor log and challenger key were never in core, and a test asserts no configuration cites them.

`verity.claims` stays in core and is the source of these ids. The site should import them from the render's `claims` section and delete `security-profiles.ts`.

The steward's `published = "views"` entry also writes `<stamp>-tables.json`.

## Evidence
- Markdown renders are byte-identical to main: `views` under the spec, legacy and unfiltered rules, the raw JSON, and the frozen `tables`. Parity is ok.
- This was checked on a synthetic store of 124 results; there's no evidence store on this VM. Please run `views --parity` on the control pod after merging.
- Tests pass, apart from failures main already has: the `test_evaluation` kernel list, `test_repository` ×2, `test_pods_connect[rsync]`, and the `test_store_honing` evict test.

## Follow-ups (not done)
- Three printed strings still say `Target.native_peak`: the frozen tables caption, its markdown line, and the views `WORK_MODEL` footnote. Changing them would change render bytes, so it belongs in a labelled text change.
- Where the census should live is Daniel's call; both PRs assume top-level `census/`. Moving it to `tools/census` means only a directory move plus path updates in `pyproject.toml`.

## After the switch and both merges (control pod)

~~~sh
python -m verity_numerical.bench.views --root $ST --published --format entities > <this folder>/<stamp>-tables.json
~~~

From then on, the steward writes `<stamp>-tables.json` daily beside `<stamp>-tables.md`.

**For the docs site:** `20260925T2315Z-sample-tables-entities-synthetic.json` in this folder shows the current output shape. It's built from a synthetic store, so none of its numbers are real.
