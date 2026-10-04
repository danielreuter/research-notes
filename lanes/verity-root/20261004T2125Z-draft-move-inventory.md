---
id: 20261004T2125Z-draft-move-inventory
campaign: verity
lane: verity-root
kind: draft
status: open
repo: danielreuter/verity
origin: worker of verity-top's repository-layout agent (bc-d6f8b221)
---

# Move inventory: what a directory move breaks or silently changes

This inventory covers everything in the Verity tree that encodes a repository path or a Python module path, which a directory move would break or silently change. It was taken read-only at `main` 3504da27e (2026-10-04, 5,742 tracked files), with the local evidence store (`~/.research/store`, 4,906 attempts and 49,001 manifests) as the sample of stored records. It has two uses: it is the checklist and the rewrite rules for a move script that every move PR runs, and it is the evidence for deciding whether Python import names follow the new directories or stay as they are.

## Headline

A scan for tokens that resolve to tracked paths found 5,121 path literals in 1,198 files. Python holds 2,666 of them in 749 files, Markdown 834 in 95, JSON 430 in 49, shell 356 in 104, Rust 264 in 74 and TOML 253 in 32. By form, 3,188 are root-relative, 637 are package-relative, 400 are relative to a tracked directory, 135 are globs and 311 don't resolve. Python also anchors on its own location: there are 451 `parents[N]` uses in 375 files, of which 117 reach the repository root and so change meaning with depth, plus 30 `.parent.parent` and 96 literal `../..`. Our import names appear 1,003 times in 322 files that are not Python.

The decisive finding, for category 7: no digest, descriptor id, program digest, Definition id, Lean pin or declared tool's derivation id contains a Python module path. An import rename changes no content-addressed identity of the core. It does force re-pins and data rewrites in about a dozen specific places, listed in category 7, and it changes the derivation ids of 111 stored runs keyed by a `-m module` argv. A directory move without an import rename changes no digest either, but it re-keys 2 path-keyed pin fixtures, changes the derivation ids of 1,593 stored runs whose argv names repository paths, breaks 25 directory-shaped tool specs in research's registry, and leaves several path-prefix gates silently matching nothing.

## How each category is organized

Each category below gives the files and counts, two or three examples, what a pattern can rewrite mechanically, what needs judgment, and any hit that is baked into a digest, a pinned vector or a frozen fixture. "Fails open" means a stale path makes a gate or check pass without checking anything; "fails closed" means a stale path makes something error out, which is the safe case.

## 1. Workspace and packaging

The root `pyproject.toml` lists 22 workspace members by path (`tools/research`, `packages/verity`, `backends/flock`, `protocols/pouw`, …) and 12 `testpaths` for the repository suite. There are 24 member-level `pyproject.toml` files. `benchmarks/pous/pyproject.toml` is a test suite but not a workspace member. Every inter-member dependency is `{ workspace = true }`; no member uses `path =`, hatch `sources`, `force-include` or `dev-mode` settings, and every hatch `packages` entry is relative to its own member (`src/verity`, `python/verity_flock`, `verity_pouw`, `src/research`). Moving a whole member directory therefore changes nothing inside that member's packaging. Only the root members list and `uv.lock` change.

`uv.lock` has 78 path lines: 22 `source = { editable | virtual = "…" }` entries plus the editable entries in `requires-dist`.

The `[tool.verity.tests]` tables hold 93 `inputs` entries and 2 `artifacts` entries. The artifacts are both under `backends/flock/verifier/lean/`: `.lake/build/bin/flock-verify` and the level3 Mathlib build. Research's inputs list every member pyproject, 30 entries in all. Sampled proofs' inputs list 6 soundness Lean files under `backends/flock/verifier/lean/soundness/`. `backends/ligero-verify` appears in inputs but is not a member.

There are five console entry points. They name modules, not paths: `verity-vllm = "verity_vllm.pipeline.cli:main"`, `network-warden-calibrate`, `circuit-check`, `cluster` and `research`.

Mechanical: the members list, testpaths and inputs are path-map rewrites, and `uv lock` regenerates the lock. A stale `inputs` entry fails closed: the suite guard fails any test that reads outside its declared inputs. Judgment: whether `benchmarks/pous` becomes a member, and whether `backends/ligero-verify` stays listed. Nothing here is digest-baked, but every suite's pass cache key includes the lock entries and tree ids, so every moved suite runs cold once. That is expected.

## 2. Check and CI configuration

All of this is in `tools/check/`, plus research's readers of it.

- `ci.toml`: the job `lean-agreement` has `merge_requires = ["backends/flock/", "!README.md", "!PROTOCOL.md"]`.
- `tool.py`: the same `merge_requires` again, with the command `tools/check/check.py`, `preflight = ["tools/check/preflight.py"]` and `after_land` running `tools/check/post_train.py`. The train gate parses it on `main` with `git show`.
- `queue.toml`: two grants keyed by `paths`, `["integrations/vllm/", "!README.md"]` and `["backends/flock/", "!README.md", "!PROTOCOL.md", "!*/tests/*"]`.
- `check.py`: 49 path hits, including the joins `FLOCK_VERIFIER = ROOT / "backends" / "flock" / "verifier"` and `check_build.sh`, the prefix `"backends/flock/verifier/"` in `agreement_closure`, the prefix `"backends/flock/"` in `rust_tests_inputs`, and `LINTS = ("tests/test_no_wall_clock.py", "tests/test_repository.py")`.
- `lean_audit.py`: 17 path hits. `packages()` discovers Lake packages by glob (any directory holding a `lean-audit.json`), so discovery survives moves.
- `lean-deps.json`: 7 entries, keyed by `deps_key` hash, each with an informational `package` path.
- Smaller files: `suites.py` has 14 hits, `preflight.py` 12 (`ROOT / "tools" / "check" / "lean_audit.py"`), `tools/lean/README.md` 17, `lean_changed.py` 12, `tools/lean/cache.py` 8, `verdicts.py` 6, `tools/lean/tool.py` 6, `post_train.py` 5 (`integrations/vllm/tests/regression/expected`), and `declaration.py` 4.
- Research holds 22 repository-path literals in non-test code that it reads at a given commit:
  - `queue.py`: `RULES = "ci/queue.toml"`, with `RULES_BEFORE_MOVE = "tools/check/queue.toml"` as a fallback (a precedent for move-aware readers) and `LEAN_BUILDS = ("backends/flock/verifier/lean",)`.
  - `jobs/cli.py`: `_show(commit, "tools/check/tool.py")`, `UPSTREAM = "backends/flock/verifier/upstream.json"` and `LEAN_TOOL = "tools/lean/"`.
  - `jobs/trains.py`: `TOOL_PY`.
  - `merge.py`: `SLOT_WRAP` and `PREFLIGHT`.
  - `quick_tier.py`: `SUITES`.
  - `pods/health.py` and `pool_n1.py`: one path each.
- `jobs/train_vectors.json`: 29 path hits. It is shared with the site's TypeScript and embeds fake `tools/check/tool.py` and `backends/flock/` paths.

Two code paths depend on the import name rather than the path. `suites.py`'s `foreign()` globs `verity*/__init__.py` and `*/verity*/__init__.py` under each member to detect a virtualenv pointing at another checkout. `circuit_check.targets._authored` keeps a Definition only if its function's top-level module is `verity`, `verity_vllm` or `verity_pouw`. Both fail open: a package with another name, or one nested deeper, silently drops out of the check.

Mechanical: the literals and joins are path-map rewrites. Judgment:

- Every path-prefix gate fails open. A stale `merge_requires`, a queue grant, `agreement_closure`, `rust_tests_inputs` or `LEAN_BUILDS` matches no changed path, so the gate or job is skipped. A move PR must assert that each still matches at least one tracked file.
- The commit-aware readers in research read old commits as well as new ones, so each needs the old path as a fallback, as `RULES_BEFORE_MOVE` already does.
- The Lean audit cache key (`key_of`) hashes the package path and every input file's path, so moved packages audit cold once. `deps_key` hashes only the bytes of `lake-manifest.json` and `lean-toolchain`, but those bytes change when a path `require` changes (category 4), so the pod's warm Lean dependencies go cold too.

## 3. Boundary and invariant tests

- `packages/verity/tests/test_boundaries.py`:
  - It anchors on `SRC = parents[1] / "src" / "verity"`.
  - Its rules are keyed by core subpackage name, not path: `ALLOWED` covers `ir`, `evaluation`, `ml`, `commitments`, `proofs`, `resource_accounting`, `randomness` and `claims`, and `NUMPY_FREE = ("ir", "ml/tc", "randomness", "claims")`.
  - `FORBIDDEN_EXTERNAL` holds top-level directory names (`backends`, `frontends`, `integrations`, `protocols`, `tools`) and is applied to import names.
  - A regex reads `"module:attr"` strings.
- `tests/test_protocol_boundaries.py`:
  - It anchors on `ROOT = parents[1] / "protocols"`.
  - It encodes the convention that a protocol in directory `name` imports as `verity_{name}`: `_allowed(name) = {"verity", f"verity_{name}"}`.
  - It holds `EDGES = {"pouw": {"sampled_proofs"}}` and an explicit `ROOT / "pouw" / "verity_pouw" / "protocol.py"`.
- `tests/test_lean_packages.py`: holds `CORE = ROOT / "packages" / "verity" / "lean"`, the rule `pkg.relative_to(ROOT).parts[0] != "protocols"` (which decides what counts as a protocol package), the soundness package's path and `tools/lean/merge.py`.
- `tests/test_backend_boundaries.py`: globs `ROOT / "backends"` and `ROOT / "integrations"`, and holds `KNOWN`, 40 pairs of (backend file path, `verity_vllm` module).
- `tests/test_repository.py`:
  - Path lists: `ALLOWED_EXTRA` (5), `SPLIT_DOCUMENT_DIRS` (2), `PINNED_EVIDENCE` (1), `ALLOWLIST` (8 paths with size caps), `UNSUITED_TEST_DIRS` (`backends/direct/`, `backends/gkr/`, `backends/shared/`) and the registry `fixtures/artifacts.json`.
  - `GENERATED_DIRS` rejects any path under a directory named `reports`, `results`, `renders`, `previews`, `plots`, `evidence`, `assets` or `outputs`, so no directory in the new layout may use those names.
  - `test_every_test_file_is_in_a_suite` derives testpaths from the pyprojects.
- `tests/test_no_wall_clock.py`: `ALLOWED` has 10 entries keyed by path or `path::name`.

`PINNED_EVIDENCE`, `ALLOWLIST` and the wall-clock `ALLOWED` reject stale entries, so they fail closed. The others need checking. A rule like `parts[0] != "protocols"`, or a glob of `ROOT / "backends"`, silently covers fewer files after a move.

Mechanical: the path lists and joins. Judgment: the structural rules. These are the "a protocol package is under `protocols/`" test, the protocol convention that the directory name is the import suffix, `FORBIDDEN_EXTERNAL`'s directory names, and the depth of each `parents[N]` anchor. Each needs a decision about what the rule means in the new layout, not a string swap. Nothing here is digest-baked.

## 4. Lean

There are 9 lakefiles (8 real packages plus the control fixture under `tools/lean`), with 9 `lean-toolchain`, 9 `lake-manifest.json` and 9 `lean-audit.json` files.

Four `require`s are by relative path, and they are the hard breaks:

- level3: `path = ".."`
- soundness: `path = "../level3"`; its manifest also carries the inherited `flock_verifier` at `../level3/..`
- nci and pouw: `path = "../../../packages/verity/lean"`

Each manifest records the same relative `dir`. `protocols/pouw/lean/lake-manifest.json` has `name = "pous"`, an existing oddity worth fixing in passing.

Lean module and constant names don't change when directories move. The pins in `lean-audit.json` are keyed by constant names and type hashes and hold no paths. Pin and read counts:

| Package | Pins | Reads |
|---|---|---|
| flock verifier | 25 | 26 |
| level3 | 56 | 37 |
| soundness | 757 | 345 |
| core | 29 | 13 |
| nci | 8 | 6 |
| network warden | 51 | 6 |
| pous | 104 | 34 |
| pouw | 800 | 128 |

Paths do appear in four places:

- The `runs` sections (warden's `NetTimingDifftest`, pouw's `PouwBulk`) generate their data with package-relative scripts (`scripts/difftest_vectors.py`, `scripts/fp8atom_vectors.py`) run with `{repo}`. `fp8atom_vectors.py` reads `args.verity / "packages/verity/tests/ml/fixtures/golden/ada_e4m3_m16n8k32.json"` and documents `PYTHONPATH=<verity>/packages/verity/src`. `difftest_vectors.py` checks that `verity_network_warden.__file__` lies under the checkout. Both fail closed when stale.
- Soundness's `upstream.scan.baseline` is package-relative.
- `protocols/pouw/lean/scripts/row_prims_vectors.py` writes a header containing its own repository path into the generated `RowPrimVectors.lean` and `RowPrimChecks.lean`, and `test_row_prims_lean.py` compares them byte for byte.
- PoUS's `TRUSTED.sha256` (44 lines) uses package-relative paths and hashes file bytes.

Mechanical: recompute each `require path` and manifest `dir` from the new locations, and rewrite the script path inside the generator and its outputs together. Judgment: core's package moves to `verity/`'s Lean home, so the two `../../../packages/verity/lean` requires change depth as well as text. `tools/cluster/kinds/lean.toml` (`inputs = ["packages/verity/lean", "tools/lean"]`) and the Lean lines of category 2 move with it.

Pinned hits: the generated `RowPrimVectors.lean` and `RowPrimChecks.lean`, byte-checked against their generator. No `lean-audit.json` pin changes for a pure move.

## 5. Infrastructure and deploy

- `tools/research/src/research/pods/nebius/deploy.toml`: 69 `[[file]]` entries (48 `src`, 21 `by`) and 1 `[[tree]]`. Their sources are under `tools/research` (67), `infra/nebius` (2) and `tools/cluster` (1). The node-side `path` and `managed` values are absolute node paths and must not change. AGENTS.md cites the file as `pods/nebius/deploy.toml`, a shorthand that doesn't resolve.
- Systemd units: `infra/nebius/verity-console.{service,timer}`, `tools/cluster/vy-cluster-agent.service`, and 4 services, 4 timers and `user-cpuset.conf` under `research/pods/nebius`. `vy-cluster-agent.service` embeds `PYTHONPATH=/workspace/research/src/@SOURCE@/tools/cluster/src`, `tools/cluster/descriptions/nebius.toml` and `@SOURCE@/READY.json`.
- Node scripts: 69 checkout-relative references (`$SRC/integrations/vllm/…`, `$SRC/tools/research/src`) across 17 files, among them `n2_commit.sh`, `n2_build.sh`, `n2_custody.sh`, `cluster_up.sh`, `vllm_bootstrap.sh`, `shadow-node2.sh` and the SkyPilot jobs under `sky/jobs/*.yaml`.
- Module invocations: node scripts also run `python -m verity_vllm.pipeline.cli` against whatever tree a run checked out.

Mechanical: `deploy.toml` `src` and `by` values, and the `$SRC/<path>` references, are path-map rewrites. Judgment:

- Node paths such as `/workspace/pouw/infra/bin` and `/workspace/jobs/dispatch/infra/nebius` contain our top-level names, so the rewrite pattern must be anchored to repository-relative tokens and must never touch absolute paths.
- A node script runs against trees from before and after the move, so it needs layout detection or must only run against the commit it shipped with.
- `research deploy drift` compares deployed files to `main`'s, so a move shows up as drift until `research deploy install` runs from the moved commit.

Nothing here is digest-baked.

## 6. Fixtures and data

- `fixtures/artifacts.json`: maps 111 art ids to paths (10 tracked, 101 fetched), plus a `previous` block of 3. By prefix:

  | Prefix | Entries |
  |---|---|
  | `backends/ligero-verify` | 32 |
  | `backends/ligerito-verify` | 24 |
  | `integrations/vllm` | 18 |
  | `packages/verity` | 17 |
  | `fixtures/*` | 10 |
  | `backends/gkr` | 3 |
  | `backends/sp1` | 3 |
  | `backends/flock` | 3 |
  | `backends/direct` | 1 |

  A repository fixture's art id is the hash of its bytes and its bare file name (`test_repo_replicas`: "content, not pathname"), so moving a fixture keeps its id as long as the basename is kept. The store index's `repo_path` column is a cache derived from this map.
- `.gitignore`: 138 rules, 101 with a top-level prefix. The fetched fixtures' paths are gitignored, so a stale rule would let a 256 KiB-plus fixture be committed.
- Data files holding repository paths: 78 files, 560 hits. Beyond the files already covered:
  - `census/subcircuits.json` (83), `census/workloads.json` (18, naming `integrations/vllm/tests/regression/expected/*.json`) and `census/input_sets.json` (5, naming `fixtures/bench-instances/v1/manifest.json` and `backends/direct/ligero/fp8/chain.py`). The census is meant to move to its own repository, where these references rot regardless.
  - `fixtures/discrepancy_log.json` (62).
  - The two path-keyed pin fixtures, `backends/flock/tests/fixtures/randomness_lean.json` (10) and `protocols/sampled_proofs/tests/fixtures/exfiltration_lean.json` (9).
  - `backends/flock/verifier/vectors.json` (10).
  - Frozen copies of store records under `backends/numerical/tests/bench/data/flock-runs/*/job.json` and `tools/research/tests/fixtures/run_v0.2/job.json`.
  - `benchmarks/pouw/harness/price_twins.json` (its `sources` give a path and sha256 for each pin file it was built from).
  - vLLM's `census_roots.txt`, `dead_code_keep.json`, `by_name_allowlist.json` and `lint/allowlists/p12_shared_keys.json` (`integrations/vllm/**`, `packages/verity/src/verity/**`).
- Census readers: `verity_numerical.bench.census` anchors on `Path(__file__).resolve().parents[5] / "census"` unless `VERITY_CENSUS` is set. 26 files read `census/` by path.

Mechanical: the values in `artifacts.json` (keep basenames and the ids stay), `.gitignore` rules, the allowlists, and the keys of the two pin fixtures. Each fixture maps a repository path to a sha256, for example `"backends/flock/verifier/lean/soundness/FlockSoundness/Audit/Law.lean": "335f8f…"` and `"packages/verity/tests/randomness/vectors.json": "1718bb…"`. A key rewrite must assert that every hash is unchanged.

Judgment: frozen records and provenance must not be rewritten. That covers the `job.json` copies, `price_twins.json` `sources`, the generator strings in `vectors.json` and the 62 paths inside `discrepancy_log.json`, all of which describe what was true when they were made.

Pinned or digest-baked hits:

- `randomness_lean.json` and `exfiltration_lean.json`: path-keyed, so their keys change and their hashes don't.
- `fixtures/discrepancy_log.json` and `fixtures/hawkeye/PIN.json`: registered in `artifacts.json`, so rewriting their content changes their art id.
- `vectors.json`: read from the checkout by the agreement job. `ci-bundle.sh` packs only the store artifacts it references into the bundle that `upstream.json` pins, so a text edit to `vectors.json` changes no pin. Changing or adding a replayable set does require a rebuild and re-pin.

## 7. Serialized Python module paths (the decisive category)

The question is whether anything stored, pinned or hashed contains a Python import name, so that renaming imports (for example `verity.ir` to `verity.primitives.circuits`) would change a digest, a pinned vector, a fixture or a stored record.

**Free of module names.** I checked each of these by reading the code that builds the identity:

- Descriptor ids and digests, and Definition ids: ids are `f"{self.name}_v{self.version}"` in `verity/ir/defs.py`, and the codec writes no `__module__`.
- Program digests and partition objects (`verity/partition/v1`).
- The kernel registry: `register_kernel` is keyed by the Definition id.
- The randomness vectors.
- All Lean pins: they use Lean constant names.
- The 191 distinct `verity/<id>/v<n>` domain and schema identifiers (620 occurrences): every one is a literal string, none built from `__name__`.
- Research derivation ids for declared tools: `_tool_identity` hashes only `{name, version}`, never the registry spec. Published attempts record `tool {name, version}` only, while the run's own store section also records `spec`.
- Repository fixture art ids: bytes plus basename.
- The vLLM engine's `profile_id_of`: its manifest holds vLLM's class names, and `worker_extension_cls` is excluded from `engine_kwargs`.
- The generic `profile_id`: a literal format.

For all the digests that matter, the import name is not an input.

**Would change under an import rename.** Hits that are pinned or stored:

- Three pinned vLLM profile fixtures: `integrations/vllm/verity_vllm/engine/profiles/expected/derived_GEMMA2_2B.json`, `derived_GEMMA2_2B_FP8.json` and `derived_GEMMA2_9B.json`. They hold 6 `"__callable__": "verity_vllm.program.registry.dense.…"` names, written by `canonical.py` from `f"{x.__module__}.{x.__qualname__}"`, and `test_profiles_generic.py` compares them structurally. They would need a re-pin. No digest is involved, because the profile id is a literal.
- Five SHA-pinned Lean files whose comments name Python modules:
  - `RandomnessVectors.lean`, `Flock/Draw.lean` and `FlockSoundness/Randomness.lean`, pinned by `randomness_lean.json` (for example `` `verity.randomness.Key.uniform` ``).
  - `Audit/Stratified.lean` and `StratifiedMiss.lean`, pinned by `exfiltration_lean.json`.

  Rewriting those comments changes the files' sha256 and so the pins. Leaving them stale breaks nothing but the prose.
- Two files under PoUS's `TRUSTED.sha256`, `Pous/Protocol/Model/Continuous.lean` and `SecureErasure.lean`, for the same reason.
- Generated Lean that names Python modules: `RowPrimVectors.lean` (18 `verity_pouw.circuit.words`, byte-checked against its generator) and `EncVectors.lean` (14 `verity.ml.tc.cast.…`).
- The registered fixture `fixtures/discrepancy_log.json` (12 `verity.*` names). Rewriting it changes its art id, so its `artifacts.json` entry must be re-put.
- Stored attempts: 111 of the 2,990 argv-keyed derivations run a dotted `-m` module (`verity_vllm` 95, `verity_numerical` 11, `research` 4, `verity_capture` 1). A rerun under a new name is a new derivation, unmatched to the old one. The old records don't change.
- Provenance in artifact metadata, for example input sets' `"generator": "verity_numerical.bench.generate"` and `weights_of_record`'s `{"tool": "verity_vllm.check.weights_of_record"}`. `ArtifactManifest.to_doc()` includes `meta` (`store/model.py`), and the art id hashes `to_doc()`, so a regenerated input set with identical bytes would get a new art id. Stored ones keep theirs.
- Data resolved by `import_module` at run time:
  - `engine/profiles/quarantine/GEMMA2_2B.json` holds 17 `"adapter": "verity_ir.registry.…"` strings, a legacy module name that `admission.py` still resolves. Data has already outlived one rename.
  - `pipeline/cli.py`'s `COMMANDS` table, `profiles/__init__.py`'s `f"verity_vllm.engine.profiles.{name}"`, with short names that recorded runs cite.
  - `program/boolean.py`'s `"verity.ml.boolean"`.
  - `benchmarks/numerical`'s `templates.py`, with 8 `module:attr` specs such as `"verity_vllm.program.registry.b1:RMSNormFusedCuda"`.
  - About 20 more `import_module` call sites in non-test code. Each fails closed with an `ImportError`.
- Module-keyed test data: `lint/allowlists/p01_core_abstractions.json` (26, for example `verity.ir.codec._spec_id`), `dead_code_keep.json` (20), `by_name_allowlist.json` (19), `census_roots.txt` (9) and `p04_one_result.json` (4).
- Prose `source` strings in `census/subcircuits.json`: 82 module names.
- Structural code: the 5 entry points; `test_boundaries.py`'s subpackage-keyed rules; the protocol convention `verity_{dirname}`; the 40 `KNOWN` pairs; `_authored` in `circuit_check` and `foreign()` in `suites.py` (both fail open); and node scripts that run `-m verity_vllm.pipeline.cli` against old and new trees.
- Historical generator strings, such as `vectors.json`'s "PR #83 967b8d06's verity_flock.circuit.write". These are correct as history and must not be rewritten under either option.

**Would change under a pure directory move (import names kept).** No digest changes. What does change:

- The keys of the 2 path-keyed pin fixtures.
- The derivation ids of the 1,593 stored argv-keyed runs whose argv names a repository path, for example `bash backends/flock/pod/30-cell.sh`. A rerun is a new derivation.
- 982 attempts whose closure manifests are keyed by repository paths. A Tool's `closure` globs that go stale match nothing, so the closure is silently empty and the identity weaker.
- Research's `REGISTRY`: all 25 specs are directory-shaped dotted paths, for example `"bench_vu": "backends.direct.ligero.tool:BENCH_VU"`, `"vllm.build": "integrations.vllm.verity_vllm.pipeline.research_tools:VLLM_BUILD"` and `"flock_agreement": "backends.flock.verifier.tool:FLOCK_AGREEMENT"`. All 25 break.
- `backends/direct`'s argv `-m backends.direct.ligero.run`, and the 48 directory-shaped dotted names in 16 non-Python files (`cell.sh`, `pod_bootstrap.sh`, `rtsh_fp4_e2e.py`'s `f"backends.direct.ligero.redteam.{mod}"`).

A directory-shaped name is the only kind of module string that a directory move breaks.

## 8. Documentation links

Markdown files hold 834 path mentions in 95 files, 593 of them root-relative. Only 72 are real Markdown links, in 18 files:

- 35 cross directories, all in the root `README.md` (for example `packages/verity/README.md`, `protocols/sampled_proofs/README.md`, `protocols/pouw/PROTOCOL.md`).
- 30 are local, mostly `backends/ligero-verify/DISCREPANCIES.md` linking its `discrepancies/dN.md`.
- 6 are URLs.
- 1 is already broken: `backends/gkr/PROTOCOL.md` links `x`.

The rest are backtick paths: 49 in `README.md`, 77 in `AGENTS.md` and 64 in 8 skill files.

No test checks that a documentation path resolves, so every stale doc reference fails silently. Outside the tree, 1,075 Markdown files in the notes repository mention repository paths. They are records and must not be rewritten.

Mechanical: links and backtick paths that resolve at the base commit can be path-mapped. Judgment: prose that describes a directory's role ("everything under `backends/`", or the AGENTS.md map) must be rewritten by hand. AGENTS.md and the skills are the docs agents actually follow. Nothing here is digest-baked.

## 9. Rust and CUDA

- Cargo manifests: 33 tracked files (Cargo.toml, Cargo.lock, build.rs, .cargo config), with two Cargo workspaces (`backends/sp1`, `backends/sp1/tcdot`) whose members are relative.
- Path dependencies: all relative. Most stay inside their component; the cross-component ones are `backends/redteam/{logup-b,vu-battery-b}` → `../../direct` and `../../direct/vendor/p3-*`.
- Deep relative paths in code: 15 in Rust, and all reach outside their crate:
  - `backends/gkr/verifier/src/commitments.rs` and `vllm_v1.rs` use `include_str!("../../../../packages/verity/src/verity/commitments/{frame_v3,vllm_v1}/vectors.json")`, a compile-time read of core's vectors.
  - `backends/gkr/verifier/src/instances.rs`, `backends/sp1/common/src/*.rs` and `tests/*.rs`, and `backends/direct/tests/*.rs` reach the root `fixtures/` through `CARGO_MANIFEST_DIR` + `/../../../fixtures/…`.
- `include_*!` macros: 48 in 13 files, mostly crate-local fixtures in `backends/ligerito-verify`.
- CUDA: relative includes stay within `benchmarks/pouw` and `benchmarks/pous` (`../pearl_c/hash_h2.cuh`, `../p2_gpu/p2dec.cu`). vLLM's JIT sources are package-relative (`CPP_DIR = Path(__file__).resolve().parent / "cpp"`).
- Patches:
  - The six flock patches `backends/flock/*-b684b12.patch` and the SP1, swanky and FA2 patches use paths inside the upstream tree they patch. They are unaffected.
  - The four `backends/flock/verifier/circuit-vectors*.patch` files and `netlist-vectors.patch` use repository paths (`backends/flock/live/src/bin/flock-circuit.rs`). `ci-bundle.sh` applies them to worktrees of historical PR #83 commits, reads them with `git show "$at:backends/flock/verifier/$p"`, and copies `backends/flock/live` out of those worktrees. The result is pinned in `upstream.json` (`bundle_sha256`, 8 binary hashes).

Mechanical: crate-local paths need nothing. The cross-component `include_str!` and `CARGO_MANIFEST_DIR` joins need a depth recomputation, and they fail closed at compile or test time. Judgment: the vectors patches must keep their old paths, because they apply to commits from before the move. `ci-bundle.sh` must read the patch from HEAD's new path but from the old path at the historical commits. Its `at` column mixes HEAD with commits like 9605a77d, so a move needs the same fallback as `RULES_BEFORE_MOVE`. The pinned upstream build is unaffected as long as nobody rebuilds it.

## Recommendation on the import-name question

Keep Python import names as they are while directories move, at least for this migration, and treat import names as the stable handle that move-proof references should use.

The evidence from category 7 is that renaming gains nothing in content-addressed identity, because no digest, id or Lean pin contains a module path. The rename is also not free:

- It re-pins 3 vLLM profile fixtures, 5 SHA-pinned Lean files plus 2 in PoUS's `TRUSTED.sha256`, and 2 generated Lean files.
- It re-puts one registered art.
- It rewrites about 80 entries of module-keyed test data and the structural rules of three boundary tests.
- It forks the derivation identity of every `-m` run.
- It needs an alias layer for data that already outlives renames (the `verity_ir.*` adapters) and for node scripts that run old and new trees.

Keeping names costs one new mechanism. Today every member's hatch `packages` is local to the member, so moving a whole member needs no packaging change. Putting `verity.ir` under `verity/primitives/circuits/` without renaming it is different: it splits the `verity` distribution's sources across directories, which needs hatch `sources` remapping or one distribution per directory. The tree has no precedent for either, and uv's editable install must be probed before committing to it.

Separately, and whichever option is chosen, convert research's 25 directory-shaped `REGISTRY` specs and the `-m backends.…` invocations to import names or file paths resolved through the move map, because those break under any directory move.

## Rewrite rules for the move script

1. **Path map, anchored.** Rewrite a token only if it resolves to a tracked path, or a prefix of one, at the base commit, matched with `(?<![\w./-])`. Never touch `verity/<id>/v<n>` identifiers, URLs, or absolute node paths (`/workspace/…`, `@SOURCE@/…` stays as is).
2. **Python joins.** Rewrite `ROOT / "seg" / "seg"` chains by AST, not by text.
3. **Depth anchors.** Shift `parents[N]` by the depth change wherever the anchor's target lies outside the moved subtree, and do the same for `.parent.parent`, `dirname(dirname(…))` and literal `../..` in Python, shell, Rust `include_*!` and `CARGO_MANIFEST_DIR` joins.
4. **Lean requires.** Recompute each lakefile `require … path` and each `lake-manifest.json` `dir` from the new locations.
5. **Dotted specs.** Rewrite directory-shaped dotted specs (`backends.x.y`, research's `REGISTRY`, `-m backends.…`) through the same map, or better, retire them in favor of import names first.
6. **Path-keyed pins.** Rewrite the keys of the two path-keyed pin fixtures (`randomness_lean.json`, `exfiltration_lean.json`) and assert that every hash is unchanged.
7. **Generated files.** Rewrite a generator and its byte-checked outputs together (`row_prims_vectors.py` with `RowPrimVectors.lean` and `RowPrimChecks.lean`; `lift_expected.py` with `fixtures.toml`), or regenerate the outputs.
8. **Lockfile.** Regenerate `uv.lock` with `uv lock` after the members list changes.
9. **Ignore rules and fixture map.** Rewrite `.gitignore` rules and `artifacts.json` values, keeping each fixture's basename so its art id is unchanged.
10. **Gates fail closed.** Add a test that every path-prefix gate (`merge_requires` in `ci.toml` and `tool.py`, queue grants, `agreement_closure`, `rust_tests_inputs`, `LEAN_BUILDS`, suite `inputs`, Tool closures) matches at least one tracked file.
11. **Commit-aware readers.** Give every reader that reads a path at another commit (research's `_show` and `git show` sites, `ci-bundle.sh`) an old-path fallback, following `RULES_BEFORE_MOVE`.
12. **Deploy.** Rewrite `deploy.toml` `src` and `by`, the systemd units' checkout-relative parts and the node scripts' `$SRC/…` references, and give node scripts layout detection for older trees.
13. **Never rewrite frozen content.** Leave the contents of SHA-pinned files, registered fixtures, historical generator strings (`vectors.json`), historical patches, frozen `job.json` copies, provenance strings and store records alone, unless the same PR regenerates their pins.
14. **Documentation.** Map-rewrite resolving links and backtick paths. Hand-review prose that names a directory's role, starting with `AGENTS.md`, `README.md` and the skills.
