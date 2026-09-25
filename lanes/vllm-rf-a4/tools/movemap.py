"""Library move map for lane vllm-rf-a4: (old, new) paths relative to integrations/vllm/verity_vllm, applied in order.

A directory entry moves the whole directory.  Package inits for new packages are listed in NEW_INITS.
"""

PIPELINE = [
    ("harness/__init__.py", "pipeline/__init__.py"),
    ("harness/derive_step.py", "pipeline/build.py"),
    ("harness/run_config.py", "pipeline/match.py"),
    ("harness/commit_delta.py", "pipeline/commit.py"),
    ("harness/card.py", "pipeline/report.py"),
    ("harness/hot_commit.py", "pipeline/hot.py"),
    ("build_paths.py", "pipeline/layout.py"),
    ("query/cli.py", "pipeline/cli.py"),
    ("program/global_program.py", "pipeline/global_program.py"),
    ("observe/m1_capture.py", "pipeline/m1_capture.py"),
    ("tp/capture.py", "pipeline/tp/capture.py"),
    ("tp/commit.py", "pipeline/tp/commit.py"),
    ("tp/match.py", "pipeline/tp/match.py"),
    ("tp/fold_match.py", "pipeline/tp/fold_match.py"),
    ("harness/telemetry", "pipeline/telemetry"),
    ("harness/planner_calibration.jsonl", "pipeline/planner_calibration.jsonl"),
] + [(f"harness/{m}.py", f"pipeline/{m}.py") for m in (
    "admission_bound", "admission_planner", "compiled_merge", "coverage_workloads", "experiment", "gc_tuning",
    "launch_context", "release_json", "research_outputs", "research_result", "research_tools", "source_identity", "spans",
    "timeline", "topp_split_probe", "workload")] + [
    ("harness/target_family.py", "target_family.py"),
]

ENGINE = [
    ("observe/vllm_adapter.py", "engine/vllm_adapter.py"),
    ("observe/engine_profile.py", "engine/engine_profile.py"),
    ("observe/arrivals.py", "engine/arrivals.py"),
    ("observe/engine_driver.py", "engine/engine_driver.py"),
    ("observe/profiles", "engine/profiles"),
    ("tp/worker.py", "engine/rank_worker.py"),
]

PROGRAM = [
    ("program/numerics/relations.py", "program/numerics/gemm_relation.py"),
    ("program/numerics", "program/backends"),
    ("check/twins.py", "program/backends/twins.py"),
    ("check/relations.py", "program/backends/relations.py"),
    ("input_provenance/analytic.py", "program/model.py"),
    ("correspondence/emit.py", "program/frontend/emit.py"),
    ("tp/export_ops.py", "program/frontend/export_ops.py"),
]

QUERY = [
    ("query/v1_bridge.py", "query/required.py"),
]

OBSERVE = [
    ("correspondence/runtime_tree.py", "observe/runtime_tree.py"),
    ("correspondence/chunk_attribution.py", "observe/chunks.py"),
    ("observe/fold.py", "observe/fold/fold.py"),
] + [(f"observe/{m}.py", f"observe/fold/{m}.py") for m in (
    "tree", "views", "memory", "resolver", "resolve_log", "patterns", "patterns_fp8", "patterns_prefix")] + [
    ("tp/collective_pattern.py", "observe/fold/collective_pattern.py"),
]

COMMIT = [(f"acquire/{m}", f"commit/committer/{m}") for m in (
    "native_host.py", "native_collect.py", "leafhash.py", "flush_points.py", "native_jit.py", "native_collect.cpp",
    "native_gather.cu", "native_leafhash.cu", "native_tree.cu", "hidden_gpu_src")]

ACQUIRE = [(f"acquire/{m}.py", f"acquire/sources/{m}.py") for m in (
    "hidden_source", "moe_source", "compiled_source", "compiled_kernel_source")] + [
    ("tp/partial_source.py", "acquire/sources/partial_source.py"),
    ("query/manifest/compiled.py", "acquire/compiled.py"),
]

CHECK = [(f"check/{m}.py", f"check/match/{m}.py") for m in ("global_match", "global_match_fast", "program_compare")] + [
    ("correspondence/batch_decomp.py", "check/match/batch_decomp.py"),
    ("tp/rank_match.py", "check/match/rank_match.py"),
    ("tp/xrank_collectives.py", "check/match/xrank_collectives.py"),
] + [(f"check/{m}.py", f"check/replay/{m}.py") for m in (
    "replay", "sampled_replay", "stoch_recompute", "compiled_kernel_check", "replay_codes", "replay_dump")] + [
    ("query/vu_query.py", "check/replay/vu_query.py"),
    ("input_provenance/weights_of_record.py", "check/weights_of_record.py"),
    ("input_provenance/root_policy.py", "check/root_policy.py"),
]

PROPERTIES = [(f"check/{m}.py", f"properties/{m}.py") for m in (
    "noninterference", "census", "kernel_allowlist", "golden", "holdout", "quarantine_lint", "protected",
    "fa_tap_exactness")] + [
    ("check/golden", "properties/golden"),
    ("check/difftest.py", "properties/admission.py"),
]

COLLECTIVES = [(f"tp/{m}.py", f"collectives/{m}.py") for m in ("collective_record", "collective_sites", "embedding_shard")]

# library modules bound for tests (paths relative to integrations/vllm)
TO_TESTS = [
    ("verity_vllm/tp/analyze.py", "tests/collectives/analyze.py"),
    ("verity_vllm/tp/collective_link.py", "tests/collectives/collective_link.py"),
]

DELETED_INITS = ["input_provenance/__init__.py", "tp/__init__.py"]

# new package inits: path -> docstring
NEW_INITS = {
    "pipeline/tp/__init__.py": "Tensor-parallel stage drivers: rank capture, commit, match and fold match.",
    "engine/__init__.py": "The vLLM engine: construction from a row, env pins, request driving, the rank worker and engine profiles.",
    "properties/__init__.py": "Property harnesses: non-interference, kernel census, golden and holdout corpora, admission difftests, quarantine and FA-tap exactness.",
    "collectives/__init__.py": "Collectives: the collective record, the communicator hook sites and the shard layout.",
    "check/match/__init__.py": "Match checks: global match, program compare, batch decomposition and rank match.",
    "check/replay/__init__.py": "Replay checks: sample, open, evaluate and compare.",
    "observe/fold/__init__.py": "The fold: raw observation log -> record Program (resolver, versioned memory, kernel patterns).",
    "acquire/sources/__init__.py": "Acquisition sources: the hidden FA tap, MoE, compiled kernels and rank partials.",
    "commit/committer/__init__.py": "The GPU committer: host, native collector, leaf hashing and the CUDA/C++ sources.",
}

GROUPS = [("pipeline", PIPELINE), ("engine", ENGINE), ("program", PROGRAM), ("query", QUERY), ("observe", OBSERVE),
          ("commit", COMMIT), ("acquire", ACQUIRE), ("check", CHECK), ("properties", PROPERTIES),
          ("collectives", COLLECTIVES)]
