---
cursor:
  subagentId: "bc-f382702c-2731-5be2-bba6-570cfb945abe"
---

# Handoff from terminology: PR #43 is merge-ready (Glossary plus a repo-wide rollout, no behaviour change); #41 and #42's areas follow when they land

lane: terminology · kind: handoff · from: terminology (agent bc-f382702c) · to: research coordinator (bc-8ece7cde) · created: 2026-09-26T01:45Z

**Superseded by `20260926T0225Z-handoff-from-terminology-merge-request.md`** (Daniel answered the three decisions; #45 added; #43 now contains #44 and #41).

**PR:** [#43](https://github.com/danielreuter/verity/pull/43), branch `cursor/terminology-glossary-5abe`, head `c9b85512`. It already contains origin/main `a50a3614` (#39 and #40), so it merges cleanly today.

**Tests:** the full suite has 9 failures, the same 9 `main` has: `test_repository` ×2, `test_pythonpath` ×3, the evaluation kernel list, `test_pods_connect`, `test_store_honing`, and `test_telemetry`, which is timing-sensitive. `test_live_coins` needs torch. On a cloud VM, run the suite with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=false`. Otherwise `test_notes_sync` hangs on the VM's commit signer.

## What's in it

- **README `## Glossary`**, in line with `docs/ontology.md`:
  - The terms: subcircuit template, subcircuit, input, input set, commitment scheme, statement, backend family, backend (with `A-route-a` for route (a)), cell, and RU/VU.
  - An old-to-new table for names that stay because they're recorded or digest-bearing.
  - A list of words that keep a narrower sense.
- **`AGENTS.md`** gets the rule: "Use the Glossary's terms; when a term changes, update the Glossary and roll it out in the same change."
- **Prose rollout** in markdown, comments, docstrings and `--help`, scripted so string literals and identifiers stay unchanged:
  - "Candidate A/B" becomes A-GKR/B-Ligero.
  - "configured backend" becomes "backend", and "configuration" in the backend-plus-scheme sense becomes "backend and statement".
  - Target-as-subcircuit is now "subcircuit".
  - "Instance set" and "instance" become "input set" and "input".
  - This covers `backends/AGENTS.md`, the `views.py` overview and help, and `verity.proofs.target`.
- **Project store:** seven `docs/architecture/` pages (backends, benchmarks-and-tables, current-state, flows, index, protocols, vllm) now use the same terms, with their frontmatter unchanged.

## Kept on purpose (all mapped in the Glossary)

- Recorded output and fields:
  - printed tables, including the frozen tables' "Candidate" headers;
  - entity fields, fingerprint fields (`profile`, `instances`) and census ids (`instance_sets`);
  - the artifact kinds `instance-equiv/v1` and `vllm-vu-set/v1`, and the `instances_*` labels;
  - the `candidate` label values;
  - the switch's recorded `LABEL`, which still reads "SP1, Flock".
- The frozen renderer's vocabulary in `tables.py` and `drilldown.py`.
- The SP1 guest.
- `integrations/vllm`, where "instance" is a Call and "family"/"kind" name definition and query families, many of them serialized.

## Decisions for you or Daniel (not blocking the merge)

1. **Rename the census and entities' `instance_set`/`instance_sets` to `input_set(s)`?** The docs site reads those fields, so the rename needs a `verity/tables-entities/v2` bump and a site change together. Until then, the Glossary maps them.
2. **Rename the markdown Table 2 column headers?** They still print `SP1` and `Flock`; the entities render already carries `C-Flock`/`D-SP1` as `backend_families[].column`. Changing the headers changes published renders and the parity baseline.
3. **Rename `verity.ir.Subcircuit`?** It is a selected gate set, not the Glossary's subcircuit, so the name now clashes. A rename would be mechanical but touches the core IR's public names. The Glossary flags the clash for now.

## Still to do (follow-up commits on #43 or a new PR)

- #41's (flock) and #42's (vLLM exporter) files, after they merge. I'm subscribed to both. The owner notes, including the 01:40Z input and input-set update, are in `20260926T0022Z-handoff-from-terminology-pr-owner-notes.md` in this folder. Please forward them.
- The files of #30, #34 and #36: `backends/gkr/PROTOCOL.md` (still titled "Candidate A") and the flock sources. These are the same kind of follow-up once those PRs merge or close.
