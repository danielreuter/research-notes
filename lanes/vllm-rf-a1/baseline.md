---
id: vllm-rf-a1/baseline
lane: vllm-rf-a1
kind: baseline
status: gate (b) measured (xdist); serial gate (b) and gate (a) being added
created: 2026-09-24T18:10Z
---
# Baseline: the vLLM integration's test gates at `72884c8a`

> **Coordinator, 19:42Z:** for gate (a) fixtures, use `../vllm-refactor/20260924T1942Z-gate-a-credential-route.md`: mint your own short-lived read-only credential, prefetch every row, delete the credential, then run gate (a) without it. Never reuse a1's `/root/r2ro.env`.

Gate (b) is not green at the base: 3,904 tests, 3,536 passed, 54 failed, 11 errors, 297 skipped, 6 xfailed.  Of the 65
failures and errors, 10 fail in any environment (files missing from the tree; a `NameError` in an extracted adapter
function), 34 come from how the pod tree is set up (subprocess builds that cannot import core `verity`; no `.git` in a
tar-shipped tree), and 21 are CPU-host numerics and real-HF derivation checks.  So "0 failures" cannot be met at this
commit: judge a lane's gate (b) as no failure or error outside the list below, and no skip reason outside the list below.

## Commit

`main` at `72884c8a21ccd8e7b127e85f0e4e162b6d684dbd` (tree `7db3f3ba863be6ae896e4db00d8de8eb1c903525`), shipped clean
(`dirty: false`) with `research pods sync`.

## Environment recipe (fresh CPU pod)

Pod used: `vyv-rf-a1` = RunPod `cpu3g`, 16 vCPU / 64 GB RAM / 80 GB volume, EUR-IS-1, $0.64/h.  Pod-wide memory
peaked at 29.8 GB with the parallel gate (b), the serial gate (b) and gate (a) running at once; a single run fits a
smaller pod (not measured).

~~~bash
# laptop, in the checkout at the commit under test
# (`research` = `PYTHONPATH=<checkout>/tools/research/src python3.12 -m research` if it is not on PATH)
research pods create --name vyv-rf-<lane> --cpu cpu3g --vcpu 16 --disk 80
research pods sync vyv-rf-<lane> --dest /workspace/base        # tar ship, ~5 min for 2,814 files

# pod: venv + pinned vLLM wheel + torch, checkpoint B0 (SmolLM2-135M) into HF_HOME=/workspace/hf, readiness checks
cd /workspace/base/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap   # -> BOOTSTRAP-OK (~2.5 min)
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0   # only for the parallel run

# gate (b), from the tree root
cd /workspace/base
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$PWD/integrations/vllm:$PWD/packages/verity/src:$PWD/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
python -m pytest integrations/vllm/tests -ra                                              # the brief's command (serial)
OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile     # same tests, parallel

# gate (a): the frozen rows' fixture trees come from the store remote; mint a read-only credential on the laptop
( set -a; source ~/.config/verity/r2.env; set +a
  research data mint-credential --ttl 3h --permission object-read-only --via local --env ) \
  | research pods ssh vyv-rf-<lane> -- 'umask 077; cat > /root/r2ro.env'     # never echo it
# pod, same PATH/PYTHONPATH/HF_HOME as gate (b), plus:
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$PWD/tools/research/store.pod.toml
export VERITY_REGRESSION_SCRATCH=/workspace/scratch VERITY_REGRESSION=1
python -m pytest integrations/vllm/tests/regression -m regression -ra
~~~

The exact scripts used for the numbers below are `baseline-gate_b.sh` and `baseline-gate_a.sh` beside this note
(`gate_b.sh TREE TAG [pytest args]`, logs to `/workspace/rfa1/logs/TAG.{log,xml,env}`).  Use a separate copy of the
tree per concurrent run (`cp -a /workspace/base /workspace/base-reg`): the suites write under the tree.

Versions (full `uv pip freeze`: `baseline-freeze.txt`):

| | |
|---|---|
| python | 3.12.14 (uv CPython, `/workspace/venv312`), Linux 5.15.0-94, glibc 2.35 |
| torch | 2.13.0+cu129 (CPU only: `cuda_available: false`, 16 threads) |
| vllm | 0.28.1rc1.dev472+gd9105ea80 (wheel `vllm-0.28.1rc1.dev472+gd9105ea80.cu129-cp38-abi3-manylinux_2_28_x86_64.whl`) |
| triton | 3.7.1 |
| numpy / transformers / tokenizers / safetensors / huggingface-hub | 2.3.5 / 5.17.0 / 0.23.2 / 0.8.0 / 1.33.0 |
| flashinfer-python | 0.6.18 |
| pytest / pytest-xdist | 9.1.1 / 3.8.0 |

## Gate (b): `python -m pytest integrations/vllm/tests`

Run: `OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile` (xdist; the same tests as
the brief's serial command), 17:42-18:22Z, 2,403 s.  Exit 1.  The serial run of the brief's exact command is below
once it finishes; it tells whether any of these depend on the thread count or on xdist.

| total | passed | failed | error | skipped | xfailed | xpassed |
|---|---|---|---|---|---|---|
| 3904 | 3536 | 54 | 11 | 297 | 6 | 0 |

Test ids below are relative to `integrations/vllm/tests/`.  Failures and errors: 65 (54 failed, 11 errors), by cause:

**Files the tests read are not in the tree at `72884c8a` (not tracked by git), so these fail in any environment** (6):

- `acquire/test_native_jit_keying.py::test_pod_release_fails_closed_on_a_stale_so_and_records_the_digest`: `tests/sweep/pod_release.sh` missing
- `check/test_gates_fixtures.py::test_card_json_roundtrip_and_schema`: `out/gen/cards/SCHEMA.md` missing
- `harness/test_release_json.py::test_pod_release_busy_pattern_names_the_stage_processes_launched_outside_row_pod`: `verity_vllm/ops/pod_release.sh` missing
- `harness/test_release_json.py::test_pod_release_sh_writes_through_the_module_and_checks`: `verity_vllm/ops/pod_release.sh` missing
- `program/test_ship_roots.py::test_r17_sparse_patterns_re_include_hf_configs`: `out/gen/r17/sparse-patterns.txt` missing
- `program/test_ship_roots.py::test_ship_roots_name_out_gen_hf_configs`: `record_v5/ship.sh` missing

**Subprocess builds cannot import core `verity`: the tests launch them with `PYTHONPATH` set to the integration tree only, and the bootstrap puts core on `PYTHONPATH` rather than in the venv (`ModuleNotFoundError: No module named 'verity'` in every build log)** (30):

The integrator's pods show the same 11 `test_applicability` errors ("same on main"). The 19
`test_artifact_applicability_independent` failures need `HF_HOME` set when that file's builder probe runs: exported, as
in this recipe, or set by `commit_delta.apply_env()` when a module importing `commit_delta` was collected earlier in
the same process. Without it the file skips as a whole (integrator, `20260924T0550Z-state`: the file alone with
`HF_HOME` gives 19 F / 3 P / 3 S, without it all skip). A run that shows these 19 as skips instead has the same defect,
not a new skip. Installing core into the venv would make the builds importable, but that is not what the bootstrap
does, so the recipe keeps the bootstrap's environment.

- `program/test_applicability.py::test_case_i_b_capability_applied_only_around_the_export_is_refused` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_i_same_digest_different_identity_manifest_reports_applied[cap80_108-cap0-108]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_i_same_digest_different_identity_manifest_reports_applied[sms132-cap1-132]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_ii_consistently_changed_target_is_refused_verbatim[cap100-numerics_unregistered: no registered GEMM specialization for target cc 10.0 (tuned_gemm_arch_family='blackwell')-applied0]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_ii_consistently_changed_target_is_refused_verbatim[triton_attn-numerics_unregistered: attention impl='vllm.v1.attention.backends.triton_attn.TritonAttentionImpl' (observed on layer 'model.layers.0.self_attn.attn') differs from the target's 'vllm.v1.attention.backends.flash_attn.FlashAttentionImpl'-applied1]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_iii_identity_is_host_independent` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_iv_hopper_target_binds_the_registered_hopper_definitions[cap90-3-Attention_v2{T,NH,KVH,D,BN=fa3_kblock_n(D,seqlen_q,NH/KVH),DOT=HopperBF16WgmmaDot16_v1,INV=Fa3InvSum_v1}-bi-eager]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_iv_hopper_target_binds_the_registered_hopper_definitions[cap90_fa2-2-Attention_v2{T,NH,KVH,D,BN=fa2_kblock_n(D),DOT=HopperBF16WgmmaDot16_v1,INV=Fa2InvSum_v1}-bi-eager-fa2]` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_case_iv_reuse_under_mismatched_profile_is_rejected` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_dead_env_var_is_recorded_as_ignored_not_declared` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_applicability.py::test_program_digest_of_b0_8_4_unchanged_and_cross_host` (error): setup error: the base build's `result.json` is missing (its build log ends in the `verity` import error)
- `program/test_artifact_applicability_independent.py::test_i_a_base_manifest_declares_the_capability_the_shim_applied`: AssertionError: base manifest declared capabilities set() (expected exactly {'8.9'}) assert set() == {'8.9'} Extra items in the right set: '8.9' Use -v to ge...
- `program/test_artifact_applicability_independent.py::test_i_b_mutating_the_applied_capability_changes_the_manifest[verity_vllm/program/frontend/target_profile.py]`: AssertionError: mutation of verity_vllm/program/frontend/target_profile.py touched nothing: [] assert [] + where [] = Build(name='cap90_site__verity_vllm__pr...
- `program/test_artifact_applicability_independent.py::test_i_c_artifact_identity_distinguishes_targets_even_when_digests_are_equal`: AssertionError: base artefact carries NO artifact/cache identity (files: []; manifest keys: []) assert None is not None
- `program/test_artifact_applicability_independent.py::test_i_d_host_answering_another_capability_than_declared`: AssertionError: host_says_90_profile_89: refusal does not name the field /capab|flash_attn_version|target profile mismatch/: assert None + where None = <func...
- `program/test_artifact_applicability_independent.py::test_ii_a_capability_9_0_declared_consistently`: AssertionError: cap90_consistent: refusal does not name the field /flash_attn_version|capab/: assert None + where None = <function search at 0x7f0efb616200>(...
- `program/test_artifact_applicability_independent.py::test_ii_b_target_8_0_with_108_sms_declared_consistently`: AssertionError: [] assert [] + where [] = Build(name='cap80_sms108_consistent', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/cap80_sms108_c...
- `program/test_artifact_applicability_independent.py::test_ii_c_num_sms_repinned_132_consistently`: AssertionError: [] assert [] + where [] = Build(name='sms132_pin', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/sms132_pin/tree'), out=Posi...
- `program/test_artifact_applicability_independent.py::test_iii_identity_excludes_host_facts`: assert None is not None
- `program/test_artifact_applicability_independent.py::test_iii_identity_is_recomputable_from_its_published_definition`: AssertionError: no wrapper with an 'identity' field in [] assert []
- `program/test_artifact_applicability_independent.py::test_iii_manifest_and_wrapper_agree_on_the_identity`: AssertionError: no identity value found in manifest or wrapper assert set()
- `program/test_artifact_applicability_independent.py::test_iii_two_hosts_same_profile_same_identity`: AssertionError: (' ', ' ') assert (False) + where False = Build(name='base', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/tree'), out=...
- `program/test_artifact_applicability_independent.py::test_iv_reuse_under_mismatched_applicability_is_rejected`: AssertionError: untestable: no TargetProfile: ModuleNotFoundError("No module named 'verity'") assert None is not None
- `program/test_artifact_applicability_independent.py::test_iv_reuse_under_mismatched_profile_is_rejected`: AssertionError: assert False + where False = Build(name='base', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/tree'), out=PosixPath('/t...
- `program/test_artifact_applicability_independent.py::test_iv_reuse_under_the_matching_profile_is_accepted`: assert None is not None
- `program/test_artifact_applicability_independent.py::test_iv_tampered_wrapper_is_rejected[<program digest>-ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff-requester1]`: AssertionError: assert None is not None + where None = identity_of(Build(name='base', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/tre...
- `program/test_artifact_applicability_independent.py::test_iv_tampered_wrapper_is_rejected[applicability.vllm_flash_attn_version-value2-requester2]`: AssertionError: assert None is not None + where None = identity_of(Build(name='base', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/tre...
- `program/test_artifact_applicability_independent.py::test_iv_tampered_wrapper_is_rejected[target_profile.compute_capability-value0-requester0]`: AssertionError: assert None is not None + where None = identity_of(Build(name='base', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/tre...
- `program/test_artifact_applicability_independent.py::test_v_program_digest_unchanged_by_the_patch`: AssertionError: base build refused/crashed (rc=1): Traceback (most recent call last): File "/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/base/driver.py", l...
- `program/test_artifact_applicability_independent.py::test_vi_dead_env_var_is_not_recorded_as_a_declared_fact`: AssertionError: (' ', None) assert (False) + where False = Build(name='attn_env_dead', tree=PosixPath('/tmp/pytest-of-root/pytest-0/popen-gw7/cbtest0/attn_en...

**The pod tree is a `research pods sync` tar export with no `.git` (and no export json): `repo_root_of()` returns None and the source-identity precheck cannot resolve the repo** (4):

- `harness/test_source_identity.py::test_negative_requested_sha_mismatch_fails_by_name`: the precheck exits 0 instead of 3 (no repo to compare the requested sha against)
- `harness/test_source_identity.py::test_precheck_passes_with_matching_veritor_repo_and_sha[integration]`: the precheck does not pass (no repo root)
- `harness/test_source_identity.py::test_precheck_passes_with_matching_veritor_repo_and_sha[repo]`: the precheck does not pass (no repo root)
- `harness/test_source_identity.py::test_repo_root_resolution_prefers_export_json_then_git_then_markers`: `repo_root_of(...)` is None, expected `/workspace/base`

**The tests exec `vllm_adapter.load_workload` standalone (torch-free), and at this commit it calls `execution_of_workload`, which the extraction does not include (`NameError`), so these fail in any environment** (4):

- `observe/test_cov_difr_b0.py::test_t1_workloads_load_as_seeded_temperature_one_headers`: NameError: name 'execution_of_workload' is not defined
- `observe/test_gen_ov_sampling.py::test_b1_workloads_load_to_the_intended_sampling`: NameError: name 'execution_of_workload' is not defined
- `observe/test_gen_ov_sampling.py::test_mixed_batch_per_request_variant`: NameError: name 'execution_of_workload' is not defined
- `observe/test_gen_sampling.py::test_load_workload_honours_sampling_block_and_keeps_greedy_default`: NameError: name 'execution_of_workload' is not defined

**Real-HF derivation on CPU: the derived program disagrees with torch CPU (`realhf` bf16 cases), or the program digest misses its pinned prefix (`hf5b` f32 greedy cases)** (8):

- `program/test_derive_hf5b_realhf.py::test_hf5b_case[gpt2-sdpa-f32-tie1-greedy-gelu_pytorch_tanh]`: AssertionError: ('gpt2-sdpa-f32-tie1-greedy-gelu_pytorch_tanh', 'df10ea4b096188d5a4710586f10d8ea4bd8384ef7484cd5749ad70a7466da503', '03925eb18841') assert Fa...
- `program/test_derive_hf5b_realhf.py::test_hf5b_case[llama-sdpa-f32-tie1-greedy]`: AssertionError: ('llama-sdpa-f32-tie1-greedy', 'b95d27f1f80a56445cdbadcfe3800df0f585dffa4e059e23826364c4ed019db7', '538319a3770a') assert False + where False...
- `program/test_derive_hf5b_realhf.py::test_hf5b_case[qwen2-sdpa-f32-tie1-greedy]`: AssertionError: ('qwen2-sdpa-f32-tie1-greedy', '38a35673ceb9347db3e73e29562fca98047ba86bc2126d3b955f41770c52c5ef', 'e9d32625a99b') assert False + where False...
- `program/test_derive_hf5b_realhf.py::test_hf5b_case[qwen3-sdpa-f32-tie1-greedy]`: AssertionError: ('qwen3-sdpa-f32-tie1-greedy', '06fc85bb2911c167c12b5973ac7b9b3775557a4cf0b501570283e87da920457e', '46ed593f82a3') assert False + where False...
- `program/test_derive_realhf.py::test_realhf_case[gpt2-sdpa-bf16-tie1-greedy-gelu_pytorch_tanh]`: AssertionError: gpt2-sdpa-bf16-tie1-greedy-gelu_pytorch_tanh: derived program disagrees with torch CPU: {'evaluated': True, 'words': 5, 'exact_words': 2, 'bi...
- `program/test_derive_realhf.py::test_realhf_case[llama-sdpa-bf16-tie0-fwd]`: AssertionError: llama-sdpa-bf16-tie0-fwd: derived program disagrees with torch CPU: {'evaluated': True, 'words': 1024, 'exact_words': 294, 'bit_exact': False...
- `program/test_derive_realhf.py::test_realhf_case[mistral-sdpa-bf16-tie0-fwd]`: AssertionError: mistral-sdpa-bf16-tie0-fwd: derived program disagrees with torch CPU: {'evaluated': True, 'words': 1024, 'exact_words': 294, 'bit_exact': Fal...
- `program/test_derive_realhf.py::test_realhf_case[qwen2-sdpa-bf16-tie0-fwd]`: AssertionError: qwen2-sdpa-bf16-tie0-fwd: derived program disagrees with torch CPU: {'evaluated': True, 'words': 1024, 'exact_words': 245, 'bit_exact': False...

**Untied-`lm_head` expectations** (3):

- `observe/test_gen_ov_easy.py::test_serve_untied_differs_from_serve_v4_only_at_the_lm_head_operands`: no lm_head operand difference found (0 == 3)
- `observe/test_gen_ov_easy.py::test_serve_untied_is_not_registered_and_binds_from_the_profile_config`: binding list gains `lm_head`
- `program/test_derive.py::test_s3_untied_lm_head_loses_sharing_and_is_refused_by_family`: `input_gates` equal where the untied program should be larger (7158595 > 7158595)

**Numerics or host facts that differ on this CPU host** (7):

- `check/test_twins.py::test_check_writes_the_evidence_schema`: the evidence carries an extra `openmp` key on this host
- `input_provenance/test_analytic.py::test_check_cos_sin_against_the_captured_b0_table`: 29,154 words differ from the captured B0 cos/sin table (tolerance 2)
- `observe/test_gen_dense2.py::test_inv_freq_models_cuda_reciprocal_multiply_and_is_identity_for_power_of_two_D`: reciprocal-multiply model off by one element (15 vs 14 equal)
- `program/test_norm_chain.py::test_mean_pins_match_installed_vllm`: pinned `src_sha256` compared with e3b0c442... (the SHA-256 of empty input): the pinned vLLM source was not found
- `program/test_ref_prims.py::test_gelu_ref_vs_torch[none-bf16]`: max ulp inf against torch CPU GELU (98.99% exact)
- `program/test_ref_prims.py::test_gelu_ref_vs_torch[none-f32]`: max ulp nan against torch CPU GELU (67.9% exact)
- `program/test_sampling_rows.py::test_nv_logf_and_nv_log1pf_are_word_equal_to_the_libdevice_transcriptions_on_every_non_nan_word`: NaN sign: `nv_logf(0xcfbec2f8)` gives 0x7fc00000, expected 0xffc00000

**Needs CUDA but does not skip without it** (1):

- `acquire/test_compiled_source.py::test_renumber_assigns_invocations_per_call_site`: `CUDA driver version is insufficient for CUDA runtime version`

**Sampler pattern not matched by this vLLM** (1):

- `observe/test_patterns_synthetic.py::test_gumbel_two_stage_sampler_is_one_token_select`: `Unsupported(..._gumbel_sample_kernel, 'sampler logits are not ... the vocabulary')`

**Timing: a 15 s subprocess timeout under full load** (1):

- `ops/test_row_pod_cancel_forwarding.py::test_sigint_is_forwarded_the_same_way`: `subprocess.TimeoutExpired` after 15 s

Skip reasons, grouped (297 skips, 50 distinct reasons):

- 157 x set VERITY_REGRESSION=1 to run the R19 reference regression  [test_regression.py]
- 11 x needs a GPU and the JIT-built native_collect extension  [test_p0_footprint.py]
- 10 x recorded evidence <path> not present in this tree  [test_harden_guards.py]
- 9 x R17 fixture not present  [test_admission_telemetry.py]
- 9 x fixture record r16_0434_b1_unitB not checked out  [test_compiled_merge_identity.py]
- 9 x row-of-record output code not present  [test_compiled_manifest.py]
- 8 x full-size build: set CAPTURE_BIG=1 (DESIGN §11)  [test_fold_m1.py, test_replay_m1.py, test_twins.py]
- 8 x needs the git tree (git ls-files)  [test_relayout_map.py]
- 6 x CUDA device required  [test_native_collect_flush.py]
- 5 x W11 attention fixtures not present: <path>  [test_composition.py]
- 5 x GPU pod end-to-end only (needs vLLM + a workload)  [test_commit_fail_closed.py, test_p0_footprint.py]
- 4 x W11R stress fixtures not present: <path>  [test_composition.py]
- 4 x CUDA needed: MeanTriton models the GPU mean_kernel's reduction order  [test_norm_chain.py]
- 4 x M1 capture / fixture not present  [test_root_policy.py]
- 3 x collection skipped  [test_leafhash_device.py, test_native_collect.py, test_triton_sha256.py]
- 3 x wave-1 capture <path> not present  [test_gen_ov_moe.py]
- 3 x CUDA needed to build the native collector extension  [test_commit_fail_closed.py]
- 2 x M1 MoE fixtures not present: <path>  [test_composition.py]
- 2 x CBTEST_GPU_HOST=1 to run the GPU-visible host-mismatch build  [test_artifact_applicability_independent.py]
- 2 x evidence dir absent: <path>  [test_stoch_draw_ledger.py]
- 2 x needs CUDA (cudaHostRegister)  [test_pinned_pool_exact.py]
- 2 x literal Triton kernels need CUDA  [test_compiled_norm_literal.py]
- 2 x could not import 'veritor.core.pad_serve': No module named 'veritor'  [test_pad_prims.py]
- 1 x B1 GEMM fixtures (RTX 4090 eager) not present: <path>  [test_composition.py]
- 1 x HP's tc-hopper archive not present: /root/veritor-artifacts/hp/tc-hopper/r1/precision.npz  [test_composition.py]
- 1 x W11R RMSNorm fixtures not present: <path>  [test_composition.py]
- 1 x B0 divergence fixture not present: <path>  [test_composition.py]
- 1 x run artefact not present  [test_gen_dense2.py]
- 1 x sweep workloads not in this checkout  [test_admission_telemetry.py]
- 1 x real Programs: set VERITY_DENSE_PROGRAM_DIRS / VERITY_MOE_PROGRAM_DIRS (':'-separated Program dirs)  [test_sampled_replay.py]
- 1 x reference manifests not in this checkout (sparse tree without out/gen)  [test_artifact_applicability_independent.py]
- 1 x probe artifacts not fetched  [test_gen_ov_sampling.py]
- 1 x lane ov-moe's recorded topk_softmax cases not in this checkout  [test_gen_ov_moe.py]
- 1 x out/gen/r9 is not part of the Verity tree (materialised on the pod by pod_hidden_gpu.sh)  [test_source_identity.py]
- 1 x CUDA needed  [test_norm_chain.py]
- 1 x heavy audit probe; set XFER_HEAVY=1  [test_derive_transfer.py]
- 1 x workload_cov_b0_b1_c1024.json not generated in this checkout  [test_coverage_workloads.py]
- 1 x live constructions need the pod venv (vLLM); set HARDEN_LIVE=1  [test_harden_guards.py]
- 1 x opt-in (FA2_COMMIT_ORIGINAL_LOADER=1): the original MufuTables.load peaks at 268.1 MB resident [M], 0.3 MiB under the laptop guardian's 256-MiB kill line; the low-peak loader checks the same digest...  [test_oracle.py]
- 1 x flip branch needs a CUDA tensor (exercised on the pod by neg_flip_partial)  [test_tp2_xrank_collectives.py]
- 1 x allocator did not reuse the pointer  [test_observer_encoding.py]
- 1 x torch backend: run on the pod with CMT_TORCH=1  [test_commit_host.py]
- 1 x local m1 capture absent  [test_run_config_dry_run.py]
- 1 x 2^32-word scan (~100 s vectorised): VERITY_EXHAUSTIVE=1  [test_sampling_rows.py]
- 1 x workload file not in this checkout  [test_fa3_launch_context.py]
- 1 x got empty parameter set for (path)  [test_nan_conversion.py]
- 1 x needs CUDA  [test_pinned_pool_exact.py]
- 1 x CUDA required  [test_compiled_source.py]
- 1 x not a git checkout (pod tree)  [test_ship_roots.py]
- 1 x B0 bundle not present: <path>  [test_rmsnorm_fused.py]

The per-file counts are in the appendix at the end.

## Gate (a): `VERITY_REGRESSION=1 python -m pytest integrations/vllm/tests/regression -m regression`

_Pending._

## Appendix: gate (b) per-file counts (xdist run)

| file | total | passed | failed | error | skipped | xfailed | xpassed |
|---|---|---|---|---|---|---|---|
| acquire/test_bound_phases.py | 6 | 6 |  |  |  |  |  |
| acquire/test_compiled_source.py | 4 | 2 | 1 |  | 1 |  |  |
| acquire/test_fa2_tap_bounded.py | 51 | 51 |  |  |  |  |  |
| acquire/test_fa2_tap_geometry.py | 14 | 14 |  |  |  |  |  |
| acquire/test_gate.py | 10 | 10 |  |  |  |  |  |
| acquire/test_install.py | 5 | 5 |  |  |  |  |  |
| acquire/test_leafhash_device.py | 1 |  |  |  | 1 |  |  |
| acquire/test_native_collect.py | 1 |  |  |  | 1 |  |  |
| acquire/test_native_collect_flush.py | 11 | 5 |  |  | 6 |  |  |
| acquire/test_native_collect_splits.py | 3 | 3 |  |  |  |  |  |
| acquire/test_native_host_security.py | 13 | 13 |  |  |  |  |  |
| acquire/test_native_jit_keying.py | 7 | 6 | 1 |  |  |  |  |
| acquire/test_openings_after_release.py | 12 | 12 |  |  |  |  |  |
| acquire/test_p0_footprint.py | 17 | 5 |  |  | 12 |  |  |
| acquire/test_pinned_pool_exact.py | 4 | 1 |  |  | 3 |  |  |
| acquire/test_plan.py | 9 | 9 |  |  |  |  |  |
| acquire/test_plan_key.py | 4 | 4 |  |  |  |  |  |
| acquire/test_promoted_input_acquisition.py | 7 | 7 |  |  |  |  |  |
| acquire/test_security.py | 31 | 31 |  |  |  |  |  |
| acquire/test_stage.py | 1 | 1 |  |  |  |  |  |
| acquire/test_x03_identities.py | 7 | 7 |  |  |  |  |  |
| acquire/test_x03_plane_classes.py | 20 | 20 |  |  |  |  |  |
| check/test_alias_reference_fixture.py | 6 | 6 |  |  |  |  |  |
| check/test_build_relocation.py | 6 | 6 |  |  |  |  |  |
| check/test_commit_verdict_b2_attribution_note.py | 5 | 5 |  |  |  |  |  |
| check/test_commit_verdict_hopper_no_evaluator_gap.py | 8 | 8 |  |  |  |  |  |
| check/test_commit_verdict_replay_seed_of_record.py | 5 | 5 |  |  |  |  |  |
| check/test_commit_verdict_selector_no_evaluator_gap.py | 13 | 13 |  |  |  |  |  |
| check/test_committed_reader_shared_module.py | 5 | 5 |  |  |  |  |  |
| check/test_committed_store_aliases.py | 4 | 4 |  |  |  |  |  |
| check/test_compare_divergence_report.py | 5 | 5 |  |  |  |  |  |
| check/test_compare_skipped_entries.py | 1 | 1 |  |  |  |  |  |
| check/test_compare_splits_binding.py | 3 | 3 |  |  |  |  |  |
| check/test_compare_synthetic.py | 4 | 4 |  |  |  |  |  |
| check/test_compiled_autotune.py | 2 | 2 |  |  |  |  |  |
| check/test_compiled_linkage_attribution.py | 6 | 6 |  |  |  |  |  |
| check/test_difftest.py | 8 | 8 |  |  |  |  |  |
| check/test_executed_prefix.py | 13 | 13 |  |  |  |  |  |
| check/test_flip_weight_negative.py | 2 | 2 |  |  |  |  |  |
| check/test_gates_fixtures.py | 45 | 44 | 1 |  |  |  |  |
| check/test_gen_adversarial.py | 15 | 10 |  |  |  | 5 |  |
| check/test_global_match.py | 60 | 60 |  |  |  |  |  |
| check/test_global_match_multi_weight_nodes.py | 5 | 5 |  |  |  |  |  |
| check/test_golden.py | 3 | 3 |  |  |  |  |  |
| check/test_oracle_compare.py | 24 | 24 |  |  |  |  |  |
| check/test_oracle_compare_promoted_key.py | 5 | 5 |  |  |  |  |  |
| check/test_oracle_compare_shared_module.py | 4 | 4 |  |  |  |  |  |
| check/test_oracle_compare_v2_producers.py | 9 | 9 |  |  |  |  |  |
| check/test_provenance.py | 7 | 7 |  |  |  |  |  |
| check/test_quarantine_lint.py | 2 | 2 |  |  |  |  |  |
| check/test_replay_m1.py | 3 |  |  |  | 3 |  |  |
| check/test_replay_synthetic.py | 12 | 12 |  |  |  |  |  |
| check/test_rev_r16_duplicate_binding.py | 7 | 7 |  |  |  |  |  |
| check/test_rev_r16_named_population_gap.py | 12 | 12 |  |  |  |  |  |
| check/test_sampled_replay.py | 49 | 48 |  |  | 1 |  |  |
| check/test_sampled_replay_aliased_module.py | 3 | 3 |  |  |  |  |  |
| check/test_sampled_replay_fp8.py | 7 | 7 |  |  |  |  |  |
| check/test_sampled_replay_query_population.py | 18 | 18 |  |  |  |  |  |
| check/test_sampled_replay_stoch.py | 8 | 8 |  |  |  |  |  |
| check/test_sampled_replay_tp_member_alias.py | 3 | 3 |  |  |  |  |  |
| check/test_sampled_replay_v2_addresses.py | 7 | 7 |  |  |  |  |  |
| check/test_stoch_draw_ledger.py | 11 | 9 |  |  | 2 |  |  |
| check/test_twins.py | 21 | 19 | 1 |  | 1 |  |  |
| check/test_verdict.py | 32 | 32 |  |  |  |  |  |
| commit/test_binding_moe_b2.py | 4 | 4 |  |  |  |  |  |
| commit/test_binding_negatives.py | 21 | 21 |  |  |  |  |  |
| commit/test_binding_star_member_index.py | 4 | 4 |  |  |  |  |  |
| commit/test_commit_fail_closed.py | 19 | 12 |  |  | 7 |  |  |
| commit/test_commit_host.py | 9 | 8 |  |  | 1 |  |  |
| commit/test_derived_rule.py | 2 | 2 |  |  |  |  |  |
| commit/test_encoding.py | 20 | 20 |  |  |  |  |  |
| commit/test_form_b_collector_perturbation.py | 5 | 5 |  |  |  |  |  |
| commit/test_hidden_stream.py | 7 | 7 |  |  |  |  |  |
| commit/test_kernel_dump.py | 7 | 7 |  |  |  |  |  |
| commit/test_negatives.py | 11 | 11 |  |  |  |  |  |
| commit/test_oracle.py | 12 | 11 |  |  | 1 |  |  |
| commit/test_padding_steps.py | 4 | 4 |  |  |  |  |  |
| commit/test_roundtrip.py | 13 | 13 |  |  |  |  |  |
| commit/test_semantic_layout.py | 3 | 3 |  |  |  |  |  |
| commit/test_stream_merkle.py | 62 | 62 |  |  |  |  |  |
| commit/test_torch_sha256.py | 23 | 23 |  |  |  |  |  |
| commit/test_triton_sha256.py | 1 |  |  |  | 1 |  |  |
| commit/test_weights_pin_acceptance.py | 9 | 9 |  |  |  |  |  |
| correspondence/test_batch_decomp.py | 14 | 14 |  |  |  |  |  |
| correspondence/test_batch_decomp_e2e.py | 9 | 9 |  |  |  |  |  |
| correspondence/test_correspondence_source_acquire.py | 6 | 6 |  |  |  |  |  |
| correspondence/test_correspondence_source_query.py | 5 | 5 |  |  |  |  |  |
| correspondence/test_descriptor_annotation_stream.py | 10 | 10 |  |  |  |  |  |
| correspondence/test_runtime_correspondence.py | 9 | 9 |  |  |  |  |  |
| correspondence/test_tp_collective_site.py | 1 | 1 |  |  |  |  |  |
| harness/test_admission_commit.py | 10 | 10 |  |  |  |  |  |
| harness/test_admission_hook.py | 4 | 4 |  |  |  |  |  |
| harness/test_admission_planner.py | 6 | 6 |  |  |  |  |  |
| harness/test_admission_telemetry.py | 25 | 15 |  |  | 10 |  |  |
| harness/test_admit_r19_host_working_set.py | 8 | 8 |  |  |  |  |  |
| harness/test_commit_delta_cli.py | 1 | 1 |  |  |  |  |  |
| harness/test_commit_delta_placement_b1.py | 2 | 2 |  |  |  |  |  |
| harness/test_compiled_merge_identity.py | 9 |  |  |  | 9 |  |  |
| harness/test_coverage_workloads.py | 13 | 12 |  |  | 1 |  |  |
| harness/test_engine_schedule.py | 4 | 4 |  |  |  |  |  |
| harness/test_experiment_index.py | 5 | 5 |  |  |  |  |  |
| harness/test_gc_tuning.py | 12 | 12 |  |  |  |  |  |
| harness/test_hot_commit.py | 25 | 25 |  |  |  |  |  |
| harness/test_prescribed_input_linkage.py | 30 | 30 |  |  |  |  |  |
| harness/test_release_json.py | 13 | 11 | 2 |  |  |  |  |
| harness/test_research_outputs_tp.py | 8 | 8 |  |  |  |  |  |
| harness/test_run_config_dry_run.py | 11 | 10 |  |  | 1 |  |  |
| harness/test_run_config_load_stages.py | 2 | 2 |  |  |  |  |  |
| harness/test_snapshot_cap.py | 4 | 4 |  |  |  |  |  |
| harness/test_source_identity.py | 23 | 18 | 4 |  | 1 |  |  |
| harness/test_target_family.py | 12 | 12 |  |  |  |  |  |
| input_provenance/test_analytic.py | 8 | 7 | 1 |  |  |  |  |
| input_provenance/test_root_policy.py | 4 |  |  |  | 4 |  |  |
| input_provenance/test_weights_of_record.py | 15 | 15 |  |  |  |  |  |
| input_provenance/test_weights_of_record_root_host_independent.py | 4 | 4 |  |  |  |  |  |
| input_provenance/test_weights_of_record_routed_experts.py | 6 | 6 |  |  |  |  |  |
| observe/test_chunked_attribution.py | 18 | 18 |  |  |  |  |  |
| observe/test_compiled_execution_header.py | 7 | 7 |  |  |  |  |  |
| observe/test_cov_difr_b0.py | 3 | 2 | 1 |  |  |  |  |
| observe/test_dense_generic.py | 13 | 13 |  |  |  |  |  |
| observe/test_ensure_distributed_port_race.py | 2 | 2 |  |  |  |  |  |
| observe/test_events_log_tree.py | 5 | 5 |  |  |  |  |  |
| observe/test_execution_label.py | 8 | 8 |  |  |  |  |  |
| observe/test_fold_group_part_event.py | 3 | 3 |  |  |  |  |  |
| observe/test_fold_m1.py | 4 |  |  |  | 4 |  |  |
| observe/test_fold_ov_sampling.py | 4 | 4 |  |  |  |  |  |
| observe/test_fold_synthetic.py | 6 | 6 |  |  |  |  |  |
| observe/test_gen_batch_engine_arg.py | 1 | 1 |  |  |  |  |  |
| observe/test_gen_dense2.py | 34 | 32 | 1 |  | 1 |  |  |
| observe/test_gen_dense_gemma2_patterns.py | 6 | 6 |  |  |  |  |  |
| observe/test_gen_dense_softcap.py | 14 | 14 |  |  |  |  |  |
| observe/test_gen_llama.py | 40 | 40 |  |  |  |  |  |
| observe/test_gen_ln.py | 12 | 12 |  |  |  |  |  |
| observe/test_gen_ov_easy.py | 13 | 11 | 2 |  |  |  |  |
| observe/test_gen_ov_moe.py | 21 | 17 |  |  | 4 |  |  |
| observe/test_gen_ov_moe_padded.py | 13 | 13 |  |  |  |  |  |
| observe/test_gen_ov_moe_qwen3.py | 23 | 23 |  |  |  |  |  |
| observe/test_gen_ov_sampling.py | 27 | 24 | 2 |  | 1 |  |  |
| observe/test_gen_ovbatch.py | 5 | 5 |  |  |  |  |  |
| observe/test_gen_sampling.py | 15 | 14 | 1 |  |  |  |  |
| observe/test_hybrid_kv_groups.py | 9 | 9 |  |  |  |  |  |
| observe/test_m1_log.py | 14 | 14 |  |  |  |  |  |
| observe/test_memory_refs_semantics.py | 5 | 5 |  |  |  |  |  |
| observe/test_memory_torture.py | 27 | 27 |  |  |  |  |  |
| observe/test_observe_resolve.py | 17 | 17 |  |  |  |  |  |
| observe/test_observer_encoding.py | 10 | 9 |  |  | 1 |  |  |
| observe/test_patterns_synthetic.py | 27 | 26 | 1 |  |  |  |  |
| observe/test_prefix_cache.py | 16 | 16 |  |  |  |  |  |
| observe/test_profiles_generic.py | 37 | 37 |  |  |  |  |  |
| observe/test_ref_integrity.py | 21 | 21 |  |  |  |  |  |
| observe/test_resolve_log_group_label.py | 2 | 2 |  |  |  |  |  |
| observe/test_resolve_m1.py | 5 | 5 |  |  |  |  |  |
| observe/test_views.py | 25 | 25 |  |  |  |  |  |
| ops/test_pod_bootstrap.py | 10 | 10 |  |  |  |  |  |
| ops/test_row_pod_cancel_forwarding.py | 4 | 3 | 1 |  |  |  |  |
| ops/test_row_pod_commit_record_precheck.py | 3 | 3 |  |  |  |  |  |
| ops/test_row_pod_match_summary_resume.py | 6 | 6 |  |  |  |  |  |
| ops/test_row_pod_policy_defaults.py | 1 | 1 |  |  |  |  |  |
| ops/test_row_pod_weights_of_record_reuse.py | 11 | 11 |  |  |  |  |  |
| program/test_applicability.py | 12 | 1 |  | 11 |  |  |  |
| program/test_artifact_applicability_independent.py | 25 | 3 | 19 |  | 3 |  |  |
| program/test_b1_authored.py | 18 | 18 |  |  |  |  |  |
| program/test_broadcast_bias_add.py | 11 | 11 |  |  |  |  |  |
| program/test_codec.py | 14 | 14 |  |  |  |  |  |
| program/test_compact.py | 12 | 12 |  |  |  |  |  |
| program/test_compiled_norm_literal.py | 4 | 2 |  |  | 2 |  |  |
| program/test_compiled_replay_seed_source.py | 4 | 4 |  |  |  |  |  |
| program/test_composition.py | 40 | 25 |  |  | 15 |  |  |
| program/test_conformance_record.py | 3 | 3 |  |  |  |  |  |
| program/test_continuation.py | 47 | 47 |  |  |  |  |  |
| program/test_derive.py | 48 | 47 | 1 |  |  |  |  |
| program/test_derive_gate_path.py | 6 | 6 |  |  |  |  |  |
| program/test_derive_hf5.py | 60 | 60 |  |  |  |  |  |
| program/test_derive_hf5_heldout.py | 6 | 6 |  |  |  |  |  |
| program/test_derive_hf5b_realhf.py | 31 | 27 | 4 |  |  |  |  |
| program/test_derive_negative.py | 61 | 61 |  |  |  |  |  |
| program/test_derive_realhf.py | 71 | 67 | 4 |  |  |  |  |
| program/test_derive_stochastic.py | 9 | 9 |  |  |  |  |  |
| program/test_derive_transfer.py | 17 | 16 |  |  | 1 |  |  |
| program/test_derived_rows.py | 58 | 58 |  |  |  |  |  |
| program/test_derived_rows_fp8.py | 10 | 10 |  |  |  |  |  |
| program/test_descriptor_equivalence.py | 3 | 3 |  |  |  |  |  |
| program/test_fa3_launch_context.py | 6 | 5 |  |  | 1 |  |  |
| program/test_fp8.py | 37 | 37 |  |  |  |  |  |
| program/test_fp8_profile.py | 15 | 15 |  |  |  |  |  |
| program/test_frontend_analyses.py | 6 | 6 |  |  |  |  |  |
| program/test_frontend_rulings.py | 15 | 15 |  |  |  |  |  |
| program/test_gateset_api.py | 25 | 25 |  |  |  |  |  |
| program/test_gemm_targets.py | 16 | 16 |  |  |  |  |  |
| program/test_gen_ov_moe_vu_shapes.py | 9 | 9 |  |  |  |  |  |
| program/test_global_program_regress.py | 22 | 22 |  |  |  |  |  |
| program/test_gp01_moe_construction.py | 9 | 9 |  |  |  |  |  |
| program/test_harden_alias.py | 27 | 27 |  |  |  |  |  |
| program/test_harden_guards.py | 13 | 2 |  |  | 11 |  |  |
| program/test_harden_moe.py | 4 | 4 |  |  |  |  |  |
| program/test_heldout_codec_compose.py | 12 | 11 |  |  |  | 1 |  |
| program/test_lifted_dense_b1.py | 12 | 12 |  |  |  |  |  |
| program/test_lifted_dense_b1_padrev.py | 10 | 10 |  |  |  |  |  |
| program/test_lifted_mixed.py | 9 | 9 |  |  |  |  |  |
| program/test_lifted_mixed_padrev.py | 4 | 4 |  |  |  |  |  |
| program/test_lifted_moe.py | 5 | 5 |  |  |  |  |  |
| program/test_lifted_moe_padrev.py | 18 | 18 |  |  |  |  |  |
| program/test_lifted_r17.py | 48 | 48 |  |  |  |  |  |
| program/test_lifted_request.py | 8 | 8 |  |  |  |  |  |
| program/test_lifted_request_padrev.py | 7 | 7 |  |  |  |  |  |
| program/test_lifted_tiny.py | 117 | 117 |  |  |  |  |  |
| program/test_lifted_tiny_padrev.py | 62 | 62 |  |  |  |  |  |
| program/test_lifted_workload_padrev.py | 10 | 10 |  |  |  |  |  |
| program/test_lint.py | 31 | 31 |  |  |  |  |  |
| program/test_lowering.py | 1 | 1 |  |  |  |  |  |
| program/test_moe_pad_route_a3.py | 6 | 6 |  |  |  |  |  |
| program/test_moe_pad_stage2.py | 15 | 15 |  |  |  |  |  |
| program/test_nan_conversion.py | 5 | 4 |  |  | 1 |  |  |
| program/test_norm_chain.py | 16 | 10 | 1 |  | 5 |  |  |
| program/test_pad_prims.py | 4 | 2 |  |  | 2 |  |  |
| program/test_padded_commit_tiny.py | 2 | 2 |  |  |  |  |  |
| program/test_padding_pod_consumer.py | 11 | 11 |  |  |  |  |  |
| program/test_profile_descriptor.py | 1 | 1 |  |  |  |  |  |
| program/test_ref_prims.py | 39 | 37 | 2 |  |  |  |  |
| program/test_refs_runs.py | 3 | 3 |  |  |  |  |  |
| program/test_relayout_map.py | 8 |  |  |  | 8 |  |  |
| program/test_rmsnorm_fused.py | 5 | 4 |  |  | 1 |  |  |
| program/test_running_example.py | 11 | 11 |  |  |  |  |  |
| program/test_sampling_operands.py | 13 | 13 |  |  |  |  |  |
| program/test_sampling_policy.py | 16 | 16 |  |  |  |  |  |
| program/test_sampling_rows.py | 10 | 8 | 1 |  | 1 |  |  |
| program/test_scalar_tensor_mul.py | 15 | 15 |  |  |  |  |  |
| program/test_serve3.py | 12 | 12 |  |  |  |  |  |
| program/test_serve3_authored.py | 3 | 3 |  |  |  |  |  |
| program/test_ship_roots.py | 4 | 1 | 2 |  | 1 |  |  |
| program/test_spec.py | 7 | 7 |  |  |  |  |  |
| program/test_splits_for_v1.py | 4 | 4 |  |  |  |  |  |
| program/test_target_profile.py | 13 | 13 |  |  |  |  |  |
| program/test_topp_split_geometry.py | 8 | 8 |  |  |  |  |  |
| program/test_topp_splits_operand.py | 25 | 25 |  |  |  |  |  |
| program/test_torch_frontend.py | 21 | 21 |  |  |  |  |  |
| program/test_vllm_bindings_pins.py | 12 | 12 |  |  |  |  |  |
| program/test_workload_compose_padrev.py | 4 | 4 |  |  |  |  |  |
| program/test_workload_program.py | 11 | 11 |  |  |  |  |  |
| query/test_boundary_oracle.py | 29 | 29 |  |  |  |  |  |
| query/test_compare.py | 3 | 3 |  |  |  |  |  |
| query/test_compiled_manifest.py | 9 |  |  |  | 9 |  |  |
| query/test_literal_operands.py | 4 | 4 |  |  |  |  |  |
| query/test_manifest_format.py | 4 | 4 |  |  |  |  |  |
| query/test_module_body.py | 13 | 13 |  |  |  |  |  |
| query/test_partition_structural.py | 37 | 37 |  |  |  |  |  |
| query/test_partition_stubs.py | 3 | 3 |  |  |  |  |  |
| query/test_partition_sweep.py | 18 | 18 |  |  |  |  |  |
| query/test_program_view_columns.py | 5 | 5 |  |  |  |  |  |
| query/test_query_artifact.py | 10 | 10 |  |  |  |  |  |
| query/test_query_counterexamples.py | 56 | 56 |  |  |  |  |  |
| query/test_query_fixtures.py | 92 | 92 |  |  |  |  |  |
| query/test_vu_conformance.py | 17 | 17 |  |  |  |  |  |
| regression/test_attempt_resolution.py | 10 | 10 |  |  |  |  |  |
| regression/test_check_lifts.py | 5 | 5 |  |  |  |  |  |
| regression/test_global_match_lift.py | 3 | 3 |  |  |  |  |  |
| regression/test_rebaseline.py | 5 | 5 |  |  |  |  |  |
| regression/test_regression.py | 158 | 1 |  |  | 157 |  |  |
| regression/test_step_segmentation.py | 7 | 7 |  |  |  |  |  |
| regression/test_stoch_value.py | 3 | 3 |  |  |  |  |  |
| test_imports_resolve.py | 1 | 1 |  |  |  |  |  |
| test_no_by_name_rules.py | 3 | 3 |  |  |  |  |  |
| test_no_dead_modules.py | 4 | 4 |  |  |  |  |  |
| tp/test_tp2_analyze.py | 4 | 4 |  |  |  |  |  |
| tp/test_tp2_attribution.py | 8 | 8 |  |  |  |  |  |
| tp/test_tp2_commit_query_population.py | 8 | 8 |  |  |  |  |  |
| tp/test_tp2_d90_fixture.py | 33 | 33 |  |  |  |  |  |
| tp/test_tp2_match_mid_module_rows.py | 3 | 3 |  |  |  |  |  |
| tp/test_tp2_match_provenance_digests.py | 3 | 3 |  |  |  |  |  |
| tp/test_tp2_match_sites.py | 5 | 5 |  |  |  |  |  |
| tp/test_tp2_rank_profiles.py | 3 | 3 |  |  |  |  |  |
| tp/test_tp2_request_program_dirs.py | 5 | 5 |  |  |  |  |  |
| tp/test_tp2_sampled_replay_fold.py | 9 | 9 |  |  |  |  |  |
| tp/test_tp2_serve_shard_from.py | 10 | 10 |  |  |  |  |  |
| tp/test_tp2_t6_4_check.py | 4 | 4 |  |  |  |  |  |
| tp/test_tp2_xrank_collectives.py | 12 | 11 |  |  | 1 |  |  |
| tp/test_tp_collective.py | 27 | 27 |  |  |  |  |  |
| tp/test_tp_partial_match_oracle.py | 8 | 8 |  |  |  |  |  |
| tp/test_tp_partial_source_mid_module.py | 6 | 6 |  |  |  |  |  |
| tp/test_tp_partial_source_moe.py | 4 | 4 |  |  |  |  |  |
| tp/test_tp_world_n.py | 14 | 14 |  |  |  |  |  |
