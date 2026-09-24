"""The dtype derive_step's `model_pin` records for a recorded Build: rebuild the engine's model config the way `_construct` does (the
Build's own declared target profile and model pin, `vllm_meta.make_vllm_config`'s EngineArgs) and apply `engine_dtype`.  On a host
without a GPU the CUDA wheel cannot make a DeviceConfig, so `create_engine_config()` stops after the model config; the probe then builds
that same ModelConfig with `EngineArgs.create_model_config()`, the first step of `create_engine_config()`.

    python fp8_dtype.py BUILD_DIR/result.json
"""
import json
import sys

from verity_vllm.harness.derive_step import engine_dtype
from verity_vllm.program.frontend import vllm_meta as vm
from verity_vllm.program.frontend.export_compat import apply_target_profile
from verity_vllm.program.frontend.target_profile import TargetProfile

rec = json.load(open(sys.argv[1]))
target = TargetProfile.from_json(rec["target"]["declared"])
pin = rec["model_pin"]
with apply_target_profile(target):
    try:
        mc, how = vm.make_vllm_config(model=pin["model"], revision=pin["revision"], max_model_len=pin["max_model_len"], **target.engine_args(),
                                      tensor_parallel_size=pin["tp"]).model_config, "create_engine_config"
    except RuntimeError as e:
        if "Device string must not be empty" not in str(e):
            raise
        from vllm.engine.arg_utils import EngineArgs
        args = EngineArgs(model=pin["model"], revision=pin["revision"], tokenizer_revision=pin["revision"], dtype=vm.PIN["dtype"], enforce_eager=True,
                          tensor_parallel_size=pin["tp"], max_model_len=pin["max_model_len"], gpu_memory_utilization=0.2, skip_tokenizer_init=True,
                          **target.engine_args())
        mc, how = args.create_model_config(), "create_model_config"
print(json.dumps({"model": pin["model"], "recorded_model_pin_dtype": pin["dtype"], "engine_dtype": engine_dtype(mc),
                  "model_config.quantization": mc.quantization, "model_config.dtype": str(mc.dtype), "via": how}))
