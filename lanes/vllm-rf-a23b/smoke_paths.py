"""Resolve every path the lane changed, in a tree at the branch head, with HF_HOME unset."""
import hashlib
import json
import os
import sys

os.environ.pop("HF_HOME", None)

from verity_vllm import config
from verity_vllm.check import fold_compare
from verity_vllm.harness import admission_planner, workload
from verity_vllm.input_provenance import weights_of_record as WR
from verity_vllm.observe import engine_profile
from verity_vllm.program.numerics import fa2_relation, rms_relation
from verity_vllm.program.registry import prims


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


out = {
    "config.ROOT": str(config.ROOT),
    "config.MANIFESTS": [str(config.MANIFESTS), config.MANIFESTS.is_dir()],
    "config.WORKLOADS": [str(config.WORKLOADS), config.WORKLOADS.is_dir()],
    "config.CHECKPOINTS": [str(config.CHECKPOINTS), config.CHECKPOINTS.is_file()],
    "checkpoints_hf_home()": config.checkpoints_hf_home(),
    "WR._default_manifest()": WR._default_manifest(),
    "workload.CORPUS": [str(workload.CORPUS), workload.CORPUS.is_file()],
    "workload.case_for(SmolLM2)": workload.case_for("HuggingFaceTB/SmolLM2-135M", "main", None),
    "fold_compare.DEFAULT_COS_SIN": [str(fold_compare.DEFAULT_COS_SIN), sha(fold_compare.DEFAULT_COS_SIN)],
    "admission_planner.CALIBRATION": [str(admission_planner.CALIBRATION), sha(str(admission_planner.CALIBRATION))],
    "fa2_relation.tables_dir()": [str(fa2_relation.tables_dir()), sorted(os.listdir(fa2_relation.tables_dir()))],
    "prims.MUFU_TANH_TABLE_DIR": str(prims.MUFU_TANH_TABLE_DIR),
}
env = engine_profile.apply_env()
out["apply_env() HF_HOME"] = os.environ.get("HF_HOME")
out["rms_relation.tables()"] = sorted(rms_relation.tables().keys()) if hasattr(rms_relation.tables(), "keys") else str(type(rms_relation.tables()))
json.dump(out, sys.stdout, indent=1)
print()
