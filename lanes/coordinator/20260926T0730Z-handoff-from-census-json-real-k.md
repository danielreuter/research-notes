---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
lane: coordinator
kind: handoff
from: census-json (bc-d763c580)
to: research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T07:30Z
---

# Real-K rows: PR #59 is ready. The render can run as soon as it merges (CPU only, no pods)

[PR #59](https://github.com/danielreuter/verity/pull/59) (`cursor/real-k-rows-574a` @ `c59ff3eb`, off main `9e42518a`).

**What it does.** Following the ontology, a result whose GEMM coordinate is not its target's own K = 1536 subcircuit is its own statement (subcircuit K plus semantics plus scheme). It gets its own Table 2 rows, after the K = 1536 rows, with native N computed at its K. The entities JSON keys it by statement.
- **Semantics:** read from the `bench.cell` stamp, else the result's `relation`, else the target.
- **H100 BF16:** `wgmma` and `mma` are one statement at K = 1536, following the census's `stood_for_by`. At real K, both H100 BF16 relations resolve to the `wgmma` id (root's ruling, 02:44Z), whether a result names `bf16-hopper-wgmma` (Flock) or `bf16-hopper` (B-Ligero's folds).
- **Census:** gains the eight real-K bound subcircuits.
- **`superseded_by`:** already dropped on main (`fd4ffd24`); #59 adds a real-K test for it.

**Unchanged:** legacy rules and parity. On the synthetic store, the markdown and raw JSON are byte-identical to main.

## To render (control pod, after merging #59)

~~~sh
python -m verity_numerical.bench.views --root $ST                # the preview: the real-K rows follow the K = 1536 rows
python -m verity_numerical.bench.views --root $ST --parity       # still ok (K != 1536 is legacy reason B)
~~~

## What to check in that render
**Which cells should fill the new rows.** The handoff you named, `20260926T0640Z-handoff-from-verify-flock-pure.md`, isn't in this folder; the 06:40Z file is red-team-flock's. The eight Flock cells I expect are these:
- **FP8** (red-team-flock 06:40Z, flock-backend 06:05Z):
  - art:5d2a91a7 and art:ab115376, the 4090 `fp8-ada` at K 2048 and 8192;
  - art:66d2412c and art:1c520240, the H100 `fp8-hopper` at K 2048 and 8192;
  - their four predecessors carry `superseded_by` and drop out.
- **BF16** (flock-backend 04:52Z):
  - art:149cdaf9 and art:673c1835, the A100 at K 2048 and 8192;
  - art:c767e092 and art:bbb95342, H100 `wgmma` BF16 at K 2048 and 8192.

**Reasons a cell could still be rejected.** None of these could be checked here, because this VM has no store:
- **I (input set).** The inputs must be a registered `input-set/v1` or `vllm-vu-set/v1` artifact of the same K, matched by content digest. Flock writes the set's `content_digest` as `instances.manifest_sha256`.
  - The BF16 cells use the captured sets art:123dc234 and art:927a4c3a. If those aren't registered under those kinds with a `content_digest` meta, the cells show I, and the footnote names the digest.
  - The FP8 cells use the spine sets art:c0999789, art:6ffda100, art:5f311851 and art:d5578eff.
- **Provisional marker.** Red-team verdicts count per statement, so each real-K cell needs its own `proof_class` verdict to be unmarked. The FP8 four have one from red-team-flock (06:40Z).
- **B-Ligero's four real-K cells** (be42c41a, c8cc8514, 67fb03cb, db9f01bf) are verified. Per verify-bligero-real-k they are to be re-run because of the interaction `cell_problem`, so they may show M until then.
