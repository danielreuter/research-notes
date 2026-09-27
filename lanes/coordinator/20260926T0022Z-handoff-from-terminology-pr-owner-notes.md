---
cursor:
  subagentId: "bc-f382702c-2731-5be2-bba6-570cfb945abe"
---

# Handoff from terminology: please forward one note to each open PR's owner (#39, #40, #41, #42) asking them to adopt the agreed terms

lane: terminology · kind: handoff · from: terminology (agent bc-f382702c) · to: research coordinator (bc-8ece7cde) · created: 2026-09-26T00:22Z

Daniel wants the agreed terms applied everywhere. The glossary is on branch `cursor/terminology-glossary-5abe` (README `## Glossary`). I don't edit files in open PRs, so I'm asking each owner to adopt the terms in their own branch. Where a name is already recorded (an artifact field, a digest, a registered set name), it stays, and the Glossary maps it. I'll roll the terms into #39/#40's files after they merge (~01:25Z), and into #41/#42's after they land.

The terms:
- **Subcircuit template:** a named template with typed parameters, such as `gemm_coordinate(K, semantics)` or `rmsnorm(d, semantics)`. Shape and semantics are both parameters. This replaces "family" and "kind" for computations.
- **Subcircuit:** a template with every parameter bound, such as `gemm_coordinate(K=1536, semantics=sm90.wgmma.m64n8k32.e4m3)`. It's what a backend proves and what a cell measures. This replaces "circuit", "kind" and "target" where they meant this.
- **Backend family:** A-GKR, B-Ligero, C-Flock, D-SP1. The letter is part of the name.
- **Backend:** an implementation of the Backend interface, such as A-interactive, A-fs, B-interactive, B-fs, C-interactive or D-fs. This replaces "configured backend", "variant" and "instance" where they meant this. A scheme is not part of a backend.
- **Statement** (added 00:40Z): what a backend proves, a subcircuit plus the commitment scheme that binds its inputs and outputs. A backend lowers it into its own circuit. "Configuration" meaning a backend with a scheme becomes "backend and statement".
- **RU and VU:** roles that sampled proofs assigns. "Unit" never names a subcircuit. A tensor-core step is a "transition unit", spelled out.

## To census-json (bc-d763c580), PRs #39 and #40

Most of this is already adopted: `subcircuits.json` holds a template with bound `subcircuits` and `legacy_target`, and the entities have `backends`, `backend_families` and `subcircuits`. What's left:
1. Entities (updated 00:40Z; the Glossary now has **Statement**, a subcircuit plus the commitment scheme that binds it, per `docs/ontology.md`): each backend's members, `configurations`, are a backend with a scheme. In the terms, that's a backend and a statement. Please name a member by its `backend` and its statement (`subcircuit` plus `scheme`) rather than as a "configuration", and drop the `variant` field, which duplicates `id`'s source name. If you rename entity fields, do it before the first published `<stamp>-tables.json`, or bump `verity/tables-entities/v1`. Also, `docs/ontology.md` gives route (a) its own backend id, `A-route-a`.
2. Entities: `table1.rows[].kind` is `"backend_family"` or `"configuration"`. Per the ontology, Table 1 rows are backends, so the second should be `"backend"`.
3. `census/subcircuits.json` holds templates, and its top-level `description` says "that target's epilogue". Please say "the semantics' epilogue" there, and in the schema's descriptions.
4. Prose in `backends/AGENTS.md`: "The target is `verity.proofs.target.FIRST`", "Table 1 configurations" and "algebraic-hash configurations" should become "subcircuit" and "backend" where that's the meaning. `census/README.md` already reads right.
5. The three printed strings that still say `Target.native_peak` (your deferred follow-up) could name the census line instead.

## To flock-vllm-v1 (bc-9713144f), PR #41 (and the flock-backend base, #34 and #30)

1. Recorded result fields stay as they are: `"family": "Flock"` and `"configuration": "Flock(scheme=…)"` in cells that already exist, such as art:56f792bd. For new registrations, please write the family as `C-Flock` if the reader accepts it, or leave it and I'll add a glossary mapping.
2. Prose: "its own Table 1 configuration (`prover=flock-cuda-block`)" should be "its own backend". "One configured backend is one Table 1 row" (`verity_flock/backend.py`) should be "One backend is one Table 1 row". "one target's tensor-core step" should be "one semantics' tensor-core step".
3. "The 48 census units" and "unit u's x and W input bits" mean transition units. Please spell them out in prose. `unit.py`, `verity_unit.rs`, the `flock-unit-io/v1` netlist and `export_unit.py` can keep their names, since they are pinned lowering identities.
4. "Flock" on its own is fine for the prover. Name the family `C-Flock` when you mean the family.

## To vllm-vu-export (bc-eab8c043), PR #42

1. The registered set names stay: `gemm-coordinate-ampere-bf16-k2048` and the rest are recorded under #101. For new sets, please use the census subcircuit id as the set's subcircuit, `gemm_coordinate/k<K>/<semantics id>` (`census/subcircuits.json`, after #39), and name the template (`gemm_coordinate`) where the code now says "family" for the exported relation.
2. "Family" as the vLLM integration's word for a Definition (`Gemm_v1`, `RMSNormFusedCuda_v2`) and its VU population is fine, and the README Glossary now says so. The map from a VU family to the subcircuit template it's cut into is the place to say "subcircuit template". For example, the docstring could read "`Gemm_v1/v2` rows are cut into subcircuits of template `gemm_coordinate`".
3. "Instance" in "instance set" (one input to a subcircuit) is the glossary's sense, so keep it.

No reply is needed unless a rename would touch a recorded field. If so, please tell me through the coordinator, and I'll map the old name in the Glossary instead.

## Update 01:40Z: input and input set (all owners, #42 most of all)

Daniel agreed a new pair of terms. An **input** is one concrete assignment to a subcircuit's input wires, with the output the chip produced recorded alongside. An **input set** is a batch of them, with provenance. They replace "instance" and "instance set" in prose, docstrings and help, and a cell is backend × statement × input set × prover hardware.

Recorded names keep "instance". That covers the `bench-instances/*` datasets and fixtures, the census's `instance_sets` ids, the fingerprint's `instances` and tier, the `instance-equiv/v1` and `vllm-vu-set/v1` kinds, and the `instances_*` labels. The Glossary maps them.

- **vllm-vu-export (#42):** in `vu_export.py`'s prose and help, please say "input set" for what the exporter writes and "input" for one row of it. The `Instance` dataclass can stay or become `Input`, your call. Registered set names and `vllm-vu-set/v1` stay.
- **flock-vllm-v1 (#41):** `verity_flock/instances.py` and "instance file" in its prose become "input set" and "input file". Recorded fields stay.
