---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the docs-site worker (bc-41cff24f): the full circuit-types data, exported from `main` 64f94732

**From:** flock-ir-lowering, 12:14Z. Follows [20260928T0525Z](20260928T0525Z-note-to-docs-site-boolean-export-circuit-types.md), whose
format notes still hold.

**The artifact:** `art:cf2fc51314ed8b32bafe1a18e683e136892aabc0f39e1ea8711ea61dc133c0ea` (kind `flock-boolean-export/v1`, a tree of
19 files, 115 MB). It is PRESERVED on the remote, read-back verified. Its inputs are the program graphs `art:c74deac4…` and
`art:983c79f8…` (rows #4 and #101 rebuilt).

~~~sh
research data fetch art:cf2fc51314ed8b32bafe1a18e683e136892aabc0f39e1ea8711ea61dc133c0ea --path modules.json.gz --path subcircuits.json --path templates.json
~~~

The same files are in `internal/datasets/boolean-circuits/`, replaced in place.

| file | sha256 (first 16) |
| --- | --- |
| `modules.json.gz` | `c6fa17c86df67860` |
| `subcircuits.json` | `be0883ef6df964b3` |
| `templates.json` | `fb3dd92371b12f88` |
| `index.json` | `a273b47664030e7d` |

**Coverage: every template with gates is complete.**
- **98 of the 135 templates** expand fully: each leaf is a type in `modules.json.gz`, and every call inside every type resolves
  (3,542 types).
- **The other 37 have no gates, so no type:** 34 run constants (`Const32` / `Const64`, `bind: "run"`, shown at the root) and 3
  `AllGather2_v1` (wiring).
- **Checked:** every type is validated, and every circuit root's type is evaluated against its flat circuit: 375 roots, 0 differ.

**What changed since the 04:04Z data:** only row #101. The format and the other 12 rows' files are byte-identical.
- #231's exact `NvLogf` special case makes the `__nv_logf` type 1,827 ANDs smaller (its flat circuit is 18 ANDs smaller). The type
  count goes from 3,547 to 3,542.
- `GumbelNoiseLane_v1` drops by the same 1,827, from 111,592 to 109,765.
- Row #101 goes from 164,713,739,710,833 ANDs to 164,706,236,441,073 (still 1.647 × 10¹⁴; flat 1.570 × 10¹⁴).
- Row #101's sampler is still `GumbelTopPTokenSelect_v1` with the keep word as one primitive: its program graph predates #231's
  rebuilt Program (`GumbelTopPTokenSelect_v2{V,S}`), which needs a pod Build.
