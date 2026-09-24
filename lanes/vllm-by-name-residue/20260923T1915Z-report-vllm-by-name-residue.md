# Lane report — vLLM by-name residue (2026-09-23)

Branch `lane/vllm-by-name-residue`, worktree `~/projects/verity-wt/resid`, from `origin/main` = `22e10e0`.
HEAD pushed: `4132fc3`. Six commits, each one file/area:

| sha | area |
|---|---|
| `72898ff` | `commit/sampled_replay.py` — embed op by dataflow, address family by address rule, plane label by member; dead MoE tables dropped |
| `65492fa` | `verity_vllm/lifting/correspondence.py` — plane rows by manifest-family route, not op_path prefix |
| `42c0090` | `verity_capture/fold.py` — TokenSelect fallback through `verity_vllm.ir.sampling_event` |
| `9722409` | `verity_vllm/ir/workload.py` + `verity_vllm/lifting/record.py` — step boundaries via the one sampling-event vocabulary; the inactive constant by its value |
| `951e7bc` | allowlist — a `decision` on every remaining S entry the lane owns (what derives it, which lane owns the source) |
| `4132fc3` | `sampled_replay.py` — label-less population addresses named by their address schema (restores `test_committed_store_aliases`) |

## Counts (allowlist entries, `tests/test_no_by_name_rules.py`: `uncovered 0, stale 0` at HEAD)

Whole file 438 → 426. Lane-owned files 202 → 190 (12 retired, 5 reclassified S→P with decisions, 94 S entries given a `decision`; nothing added).

| file | before | after | S→ | note |
|---|---|---|---|---|
| `commit/sampled_replay.py` | 27 | 21 | 13→5 | 6 retired; `_MOE_LAYER_RE`, `moe_plane_alias_check` S→P (moe_block_stream op_path schema) |
| `verity_vllm/lifting/correspondence.py` | 3 | 0 | 3→0 | retired |
| `verity_capture/fold.py` | 1 | 0 | 1→0 | retired |
| `verity_vllm/ir/workload.py` | 1 | 0 | 1→0 | retired |
| `verity_vllm/lifting/record.py` | 1 | 0 | 1→0 | retired |
| `verity_vllm/ir/sampling_event.py` | 2 | 2 | 2→0 | S→P: the single sampling-event vocabulary site |
| `commit/executed_prefix.py` | 1 | 1 | 1→0 | S→P: `fam` is the manifest identity's own `family` field |
| `analytic.py` | 10 | 10 | 10→9 | `^llama3$` S→P (HF `rope_scaling.rope_type` enum); 9 left for profiles lane |
| all other owned files | unchanged | | | decisions recorded (below) |

## Derivations used (retired entries)

- **`sampled_replay.embed_op_path`** (`Embedding` family prefix) → the first Program row whose arguments read the prompt-ids parameter (`ids_params`: every parameter that is not `weights`/`seed`/`splits` — the same reading `_gather_inputs` uses). Program dataflow names the consumer of the declared ids.
- **`sampled_replay._address_family`** (`op_path.startswith("moe/")`, `member.startswith(("part_rank","shard_rank"))`, `== SAMPLER_OP`) → the address rule that produces a `population(..., addresses=)` record labels it `manifest_family` (sampler op / plane description / `required_manifest.alias_family(member)`). A label-less record (a caller's own accumulator, as in the tests) falls back to its address schema (`SAMPLER_OP`, `_MOE_LAYER_RE`, `alias_family`) — the two retained P vocabularies.
- **`sampled_replay._describe_plane`** plane label `MOE_PLANE_OF_KIND[kind]` → `mem[0][0]` (the plane a row produces is its first member's name); the `M vs M*TOPK` message reads `n_rows == M`. `MOE_PLANE_FAMILIES`/`MOE_PRODUCER_FAMILIES` were dead.
- **`lifting/correspondence.is_plane/record_planes`** (`op.startswith(HIDDEN_FAMILIES)`) → `ident["family"]` routed through `acquire.plan`'s tap routes (`TAP_ROUTES`: hidden_tap / moe_tap) — the gm lane's public table, not its internals.
- **`fold._token_select_output`** (`spec.startswith("TokenSelect_v")`) and **`ir/workload.request_component`** (`startswith("TokenSelect_v1")`) → `verity_vllm.ir.sampling_event.is_sampling_event`. For greedy rows identical by construction (`family_of(spec) == "TokenSelect_v1"` ⇔ the prefix test; `TokenSelect_v12` does not exist). For seeded-Gumbel programs the step segmentation now also ends at `GumbelTopPTokenSelect_v1`/`GumbelTokenSelect_v1` instances, which the old prefix silently did not — flagged, not exercised by the four harness rows (all greedy).
- **`lifting/record.activity_closure`** (`sid.startswith("LBot")`) → the guard node whose Definition is the nullary `Const` with `evaluate() == enc_bot(ret.w - 1)` (AGREED A3): the inactive constant is recognised by its value, not its id.
- **`executed_prefix` `fam in NAMED_INPUT_FAMILIES`**: `fam` is the manifest identity's own `family` field → schema lookup (P).
- **`analytic` `^llama3$`**: dispatch on `config.json` `rope_scaling.rope_type`, an HF enum value, not a model name (P).

## Evidence

Machine `vyv-v2cpu3` (runpod `5r1r0i3bwbdtbt`), `/workspace/lanes/resid/{src2,src3,src4,scratch_*,out/}`; main tree `/workspace/research/src/22e10e0e…/`.

**Harness** (`tests/regression`, `VERITY_REGRESSION=1`, rows root `/workspace/census/rows`, `-k "r57 or r60 or r73 or r74"`, main and lane run concurrently):
- lane tree `42c0090` vs `main`: 40/40 test outcomes identical (only `T0-manifest_digest-r57` fails on both); 211/211 scratch artifacts (rebuilt manifests, Program views, commit views, `commit_summary.json`) byte-identical, the four `manifest.rebuilt.log` differing only in paths/timings. Logs `out/main_small2.{log,xml}`, `out/lane_small.{log,xml}`.
- lane tree `9722409` (`out/lane3_small.log`) completed with the *environment* failure signature (`commit_summary … source=recomputed: $.engine_settings: expected object, got NoneType`) that `main`'s first run (`out/main_small.log`) shows identically on r57/r60 — the store-view flip, not a code difference. The clean concurrent pair for the final tree (`out/main3_small`, `out/lane4_small`) was mid-run when the pod disappeared (`pod(5r1r0i3bwbdtbt)` → `null` at ~19:05Z); not re-runnable from here. The two commits after `42c0090` touch step segmentation (identical for greedy specs, shown above), the lifted-guard constant (not on the harness path; covered by `tests/ir/test_lifted_*`), and a fallback branch that `population`-produced addresses never take.

**Offline tests** (`tests` − `tests/regression`, `verity_capture/commit/tests`, `verity_capture/tests`; `test_source_identity.py` ignored — needs the `research` package on the path):
- full suite, lane `42c0090` vs `main`: identical failure set except `test_committed_store_aliases::…same_table` (fixed in `4132fc3`; `verity_capture/commit/tests` at `4132fc3` = `main`'s failure set, `out/off_commit_lane4.log`) and `test_twins::test_check_writes_the_evidence_schema` (fails on `main` too in the split run `out/off_cap_main.log` — order-dependent).
- local (`~/projects/verity-wt/v2/.venv`, py3.13): `tests -k "workload or lifting or record or sampling or guard or by_name"` 243 passed at `9722409`; `verity_capture/commit/tests -k "population or sampled_replay or store or alias or moe"` all pass at `4132fc3`.

**Pre-existing failures on `main` (32, py3.12 pod venv):**
`tests/ir/test_derive.py::test_s3_untied_lm_head_loses_sharing_and_is_refused_by_family`; `tests/ir/test_derive_hf5b_realhf.py::test_hf5b_case[gpt2-…]`, `[llama-…]`, `[qwen2-…]`, `[qwen3-…]`; `tests/ir/test_derive_realhf.py::test_realhf_case[gpt2-…]`, `[llama-…tie0-fwd]`, `[mistral-…]`, `[qwen2-…]`; `tests/ir/test_lifted_tiny.py::test_specified_list_is_closed`; `tests/ir/test_norm_chain.py::test_mean_pins_match_installed_vllm`; `tests/ir/test_ref_prims.py::test_gelu_ref_vs_torch[none-bf16]`, `[none-f32]`; `tests/ir/test_sampling_rows.py::test_nv_logf_and_nv_log1pf_…`; `verity_capture/commit/tests/test_admit_r19_host_working_set.py::test_fork_gc_freeze_opt_out_is_named_on_the_record`, `::test_forked_children_inherit_a_frozen_heap_…`; `verity_capture/tests/test_analytic.py::test_check_cos_sin_against_the_captured_b0_table`; `test_cov_difr_b0.py::test_t1_workloads_load_as_seeded_temperature_one_headers`; `test_gates_fixtures.py::test_card_json_roundtrip_and_schema`; `test_gen_batch.py::test_attribution_m1_on_schedule`; `test_gen_dense2.py::test_inv_freq_models_cuda_reciprocal_multiply_…`; `test_gen_ov_easy.py::test_serve_untied_differs_from_serve_v4_…`, `::test_serve_untied_is_not_registered_…`; `test_gen_ov_sampling.py::test_b1_workloads_load_to_the_intended_sampling`, `::test_mixed_batch_per_request_variant`; `test_gen_sampling.py::test_load_workload_honours_sampling_block_…`; `test_native_jit_keying.py::test_pod_release_fails_closed_on_a_stale_so_…`; `test_patterns_synthetic.py::test_gumbel_two_stage_sampler_is_one_token_select`; `test_release_json.py::test_pod_release_busy_pattern_…`, `::test_pod_release_sh_writes_through_the_module_and_checks`; `test_ship_roots.py::test_r17_sparse_patterns_re_include_hf_configs`, `::test_ship_roots_name_out_gen_hf_configs`; plus order-dependent `test_twins.py::test_check_writes_the_evidence_schema`.

## Kept / left (decision recorded on each entry)

- **Left for the profiles lane (family facts keyed by `model_type`)**: `analytic.py` `FAMILY_RULES` + the 7 `model_type` keys (this *is* the facts table — qkv_bias, default theta); `root_policy.py` (3: `model|gpt_neox` prefix, `rotary_emb.cos_sin_cache`, `gpt_neox.embed_in.weight`); `telemetry/admission.py` (6: sizing table — layers/hidden/heads/dtype derivable from `config_of`'s `C`, `weights_bytes` and calibration constants are measured facts with `source`); the `gpt_neox.*` names in `compare.py` / `noninterference.py`.
- **Left for gm/TP lanes' plan API**: `experimental/commit_integ/tp_partial_source.py` (6, `MOE_SITE_CLASSES`/`COVERS_FAMILIES` = `ROUTE_OF_FAMILY` by module class); `prefix_cache.py` `KV_PRODUCER_RE` (the KV-write route).
- **Deferred with the v1 GPU-only experimental tools** (not on the CPU harness, structural source = CorrespondenceTable owning module/slot + Definition family field): `experimental/commit_integ/native_host.py` (18), `noninterference.py` (17), `compare.py` (16), `experimental/cb_a/compare.py` (6).
- **Left, reason recorded**: `verity_vllm/correspondence/core.py` (3: typed-b1 weight table, source = flip lane's `weights_of_record` binding); `commit/weights_of_record.py` (7: vLLM loader naming facts, see finding); `frontend/rules/family.py` (1: select the rotary rule by its class's name attribute, not a string prefix); `analytic.quant_refusal` (see finding).
- **L / P kept as-is** (already justified): `registry/{lifted,b1}.py` (13: `Lifted[` id scheme, provenance pins), `correspondence/program.py` (4), `frontend/provenance.py`, `card.py` (4), `gates.py`, `observer.py`, `protected.py` (2), `quarantine_lint.py`, `vu_canonical.py`, `sweep/hot_commit.py` (2). Note: `sweep/` "≈18" was almost entirely `sweep/finalize.py` (flip lane); the lane owns only `hot_commit.py`'s 2 P entries.

## Findings not derivable from Program + correspondence (ontology)

1. **Sampling event is a name, not an attribute.** `SAMPLING_EVENT_FAMILIES` is now the only vocabulary site (fold, workload, required_manifest route through it), but the Definition carries no "this call is the step's sampling event" attribute; a Definition-level role (or the Program's step markers) would retire the last tuple.
2. **Loader placeholder vs served weight** (`weights_of_record` `ENGINE_*`/`PLACEHOLDER_RE`): `config.json` + Program cannot distinguish an `Fp8KVCacheMethod` placeholder (`.attn.k_scale`) or the derived rotary buffer from a checkpoint weight; only the runtime record (parameter-vs-buffer role, owning module class) can. The CorrespondenceTable should carry the root's role.
3. **Linear vs norm from `quantization_config.modules_to_not_convert`** (`analytic.quant_refusal`): the HF config names modules but not their class; the refusal needs the served module's class.
4. **Family naming facts** (`model.` vs `gpt_neox.` prefixes, `self_attn` vs `attention`, `rotary_emb.cos_sin_cache`, `embed_in`): vLLM naming, not HF config — belongs in the profiles lane's provenance-carrying table.
5. **Behavioural note for stochastic rows**: step segmentation (`workload.request_component`) previously ended only at greedy `TokenSelect_v1`; Gumbel programs collapsed into one step. Now unified — worth a Gumbel harness row before the integrator merges if any such row is on the fixture list.

## Not done

- Final concurrent harness pair for `4132fc3` (pod terminated mid-run; the `42c0090` pair is the last complete one).
- The full offline `tests/` directory at the final tree on the pod (the `42c0090` full run is the last complete one; targeted local runs cover the two later code commits).
