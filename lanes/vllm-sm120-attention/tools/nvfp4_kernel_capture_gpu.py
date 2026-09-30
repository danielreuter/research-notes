"""Which kernel vLLM's NVFP4 linear launches on this GPU, against core's pinned block-scaled FP4 step.

Writes `<out>/nvfp4_kernel_capture.json`:
  device     name, compute capability, SMs, driver, SM clock and its lock (the `clock-and-power-invariant` operating point)
  reference  the SASS MMA opcodes of `tools/tc_probe_fp4/mma_fp4.cu`'s single-instruction kernels built for this arch: nvfp4 is core's
             pinned `sm120.mma.m16n8k64.e2m1.nvf4` (`kind::mxf4nvf4.block_scale.scale_vec::4X ... ue4m3`), mxfp4 the ue8m0 variant
  loads      per checkpoint and `VLLM_BATCH_INVARIANT` setting, in its own process: the quant method, the linear classes and kernel
             classes by count, one layer's weight / scale / global-scale tensors, the checkpoint's quantization config, and every
             CUDA kernel one short greedy generate launches
  sass       the MMA opcodes of every launched kernel whose SASS is in vLLM's `_C` (cuobjdump, this arch)
  verdict    per load: match (a launched GEMM runs the reference nvfp4 opcode, NVFP4 E4M3 scales per 16), different step (another
             FP4 MMA), or dequant fallback (no FP4 MMA in the launched GEMMs)

    cd integrations/vllm; PYTHONPATH=.:../../packages/verity/src /workspace/jobs/venv312/bin/python \
        tests/properties/nvfp4_kernel_capture_gpu.py --out DIR
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODELS = [("nvidia/Qwen3-8B-FP4", "ccd10a893cbca613259517c3efe08e151ddf2b8e"),
          ("RedHatAI/Qwen3-8B-NVFP4", "e391349c110709b87bfc2ad2fde3f50dc5839fd8")]
LOADS = [(MODELS[0], "1"), (MODELS[1], "1"), (MODELS[0], "0")]
PROBE = Path(__file__).resolve().parents[3] / "tools/tc_probe_fp4/mma_fp4.cu"
MMA = re.compile(r"\b([A-Z]*MMA[A-Z0-9_.]*)")


def _tool(name: str) -> str:
    for home in (os.environ.get("CUDA_HOME"), "/workspace/jobs/cuda-12.9", "/usr/local/cuda"):
        if home and os.path.exists(os.path.join(home, "bin", name)):
            return os.path.join(home, "bin", name)
    return shutil.which(name) or name


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def device() -> dict:
    import torch

    p = torch.cuda.get_device_properties(0)
    q = _run(["nvidia-smi", "--query-gpu=name,driver_version,clocks.sm,clocks.max.sm,clocks.applications.graphics,power.limit",
              "--format=csv,noheader", "-i", os.environ.get("CUDA_VISIBLE_DEVICES", "0").split(",")[0]]).stdout.strip()
    return {"name": p.name, "cc": f"{p.major}.{p.minor}", "sms": p.multi_processor_count, "nvidia_smi": q, "torch": torch.__version__,
            "cuda": torch.version.cuda}


def sass_mma(path: str, arch: str, names: set[str] | None = None) -> dict[str, list[str]]:
    """{mangled function: sorted MMA opcodes} of `path`'s SASS for `arch`, streamed (vLLM's `_C` is large); only functions with an MMA,
    or only `names` when given."""
    out: dict[str, set[str]] = {}
    fn = None
    proc = subprocess.Popen([_tool("cuobjdump"), "-sass", "-arch", arch, path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    for line in proc.stdout:
        if "Function : " in line:
            fn = line.split("Function : ", 1)[1].strip()
            continue
        if fn is None or (names is not None and fn not in names):
            continue
        for m in MMA.finditer(line):
            out.setdefault(fn, set()).add(m.group(1))
    proc.wait()
    return {k: sorted(v) for k, v in out.items()}


def demangle(names: list[str]) -> dict[str, str]:
    if not names:
        return {}
    r = _run(["c++filt"], input="\n".join(names) + "\n")
    return dict(zip(names, r.stdout.splitlines())) if r.returncode == 0 else {n: n for n in names}


def reference(arch: str, work: Path) -> dict:
    cubin = work / "mma_fp4.cubin"
    b = _run([_tool("nvcc"), "-O2", "-cubin", f"-arch={arch}", "-o", str(cubin), str(PROBE)])
    if b.returncode:
        return {"error": b.stderr[-600:]}
    fns = sass_mma(str(cubin), arch)
    dm = demangle(list(fns))
    return {dm[k]: v for k, v in fns.items()}


def child(repo: str, rev: str, bi: str) -> dict:
    os.environ["VLLM_BATCH_INVARIANT"] = bi
    os.environ["VLLM_ENABLE_V1_MULTIPROCESSING"] = "0"
    import torch
    from huggingface_hub import snapshot_download
    from torch.profiler import ProfilerActivity, profile
    from vllm import LLM, SamplingParams

    from verity_vllm.engine.engine_profile import get_model_runner

    path = snapshot_download(repo, revision=rev, local_files_only=True)
    cfg = {}
    for f in ("hf_quant_config.json", "config.json"):
        p = Path(path) / f
        if p.exists():
            d = json.loads(p.read_text())
            cfg[f] = d.get("quantization") if f == "hf_quant_config.json" else d.get("quantization_config")
    llm = LLM(model=path, enforce_eager=True, gpu_memory_utilization=0.6, max_model_len=2048, max_num_seqs=4, seed=0)
    model = get_model_runner(llm).get_model()
    classes: collections.Counter = collections.Counter()
    sample = None
    for name, mod in model.named_modules():
        qm = getattr(mod, "quant_method", None)
        if qm is None or not hasattr(mod, "weight"):
            continue
        scheme = getattr(mod, "scheme", None)
        kernel = getattr(qm, "kernel", None) or getattr(scheme, "kernel", None)
        classes[" / ".join(type(x).__name__ for x in (qm, scheme, kernel) if x is not None)] += 1
        if sample is None and "proj" in name:
            t = {k: getattr(mod, k) for k in ("weight", "weight_scale", "weight_scale_2", "input_global_scale", "input_global_scale_inv",
                                              "alpha", "input_scale") if isinstance(getattr(mod, k, None), torch.Tensor)}
            sample = {"module": name, **{k: {"dtype": str(v.dtype), "shape": list(v.shape)} for k, v in t.items()},
                      "weights_padding_cols": getattr(mod, "weights_padding_cols", None)}
    with profile(activities=[ProfilerActivity.CUDA]) as prof:
        outs = llm.generate(["The capital of France is"], SamplingParams(max_tokens=4, temperature=0.0))
        torch.cuda.synchronize()
    kernels = collections.Counter(e.name for e in prof.events() if e.device_type.name == "CUDA")
    mc = llm.llm_engine.vllm_config.model_config
    return {"repo": repo, "revision": rev, "VLLM_BATCH_INVARIANT": bi, "quantization": mc.quantization, "checkpoint_quant_config": cfg,
            "linear_classes": dict(classes), "sample_layer": sample, "text": outs[0].outputs[0].text,
            "kernels": dict(kernels.most_common())}


def _norm(name: str) -> str:
    name = name.strip()
    return re.sub(r"\s+", "", name[5:] if name.startswith("void ") else name)


def verdict(load: dict, sass: dict[str, list[str]], ref: dict) -> dict:
    nvfp4 = next((set(v) for k, v in ref.items() if "nvfp4_tiles_kernel" in k), set())
    launched = {_norm(n) for n in load["kernels"]}
    gemm = {k: v for k, v in sass.items() if _norm(k) in launched or any(ln.startswith(_norm(k)[:400]) for ln in launched)}
    fp4 = {k: v for k, v in gemm.items() if any("F4" in op or "E2M1" in op for op in v)}
    s = load.get("sample_layer") or {}
    scale16 = s.get("weight_scale", {}).get("dtype") == "torch.float8_e4m3fn"
    if any(set(v) & nvfp4 for v in fp4.values()) and scale16:
        kind = "match"
    elif fp4:
        kind = "different step"
    else:
        kind = "dequant fallback"
    return {"kind": kind, "reference_nvfp4_opcodes": sorted(nvfp4), "launched_fp4_mma_kernels": fp4,
            "launched_mma_kernels": {k[:300]: v for k, v in gemm.items()}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--child", nargs=3, metavar=("REPO", "REV", "BI"))
    a = ap.parse_args()
    if a.child:
        print("NVFP4-CHILD " + json.dumps(child(*a.child)), flush=True)
        return 0
    import torch
    import vllm

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = torch.cuda.get_device_properties(0)
    arch = f"sm_{p.major}{p.minor}a"
    rec: dict = {"schema": "verity-vllm/nvfp4-kernel-capture/v0", "device": device(), "vllm": vllm.__version__, "arch": arch}
    with tempfile.TemporaryDirectory() as work:
        rec["reference"] = reference(arch, Path(work))
    print("[nvfp4] reference", json.dumps(rec["reference"]), flush=True)
    rec["loads"] = []
    for (repo, rev), bi in LOADS:
        r = _run([sys.executable, __file__, "--child", repo, rev, bi], env=os.environ.copy())
        line = next((ln for ln in r.stdout.splitlines() if ln.startswith("NVFP4-CHILD ")), None)
        load = json.loads(line[len("NVFP4-CHILD "):]) if line else {"repo": repo, "VLLM_BATCH_INVARIANT": bi, "error": (r.stderr or r.stdout)[-3000:]}
        (out / f"load-{repo.replace('/', '--')}-bi{bi}.log").write_text(r.stdout[-200000:] + "\n--- stderr ---\n" + r.stderr[-200000:])
        rec["loads"].append(load)
        print(f"[nvfp4] load {repo} bi={bi}: quant={load.get('quantization')} classes={load.get('linear_classes')} "
              f"kernels={len(load.get('kernels', {}))} {load.get('error', '')[:300]}", flush=True)
    so = glob.glob(os.path.join(os.path.dirname(vllm.__file__), "_C*.so"))
    sass = sass_mma(so[0], arch) if so else {}
    dm = demangle(list(sass))
    named = {dm[k]: v for k, v in sass.items()}
    rec["sass_functions_with_mma"] = len(named)
    for load in rec["loads"]:
        if "kernels" in load:
            load["verdict"] = verdict(load, named, rec["reference"])
            print(f"[nvfp4] verdict {load['repo']} bi={load['VLLM_BATCH_INVARIANT']}: {load['verdict']['kind']} "
                  f"{json.dumps(load['verdict']['launched_fp4_mma_kernels'])[:600]}", flush=True)
    (out / "nvfp4_kernel_capture.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("NVFP4-KERNEL-CAPTURE " + json.dumps([(ld["repo"], ld["VLLM_BATCH_INVARIANT"], (ld.get("verdict") or {}).get("kind")) for ld in rec["loads"]]),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
