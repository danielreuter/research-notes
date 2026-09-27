"""Generate the docs site's coverage support table (`verity-docs/coverage-support/v1`) from the vLLM integration's registry.

Usage (from a checkout of verity main, torch-free):
    PYTHONPATH=packages/verity/src:integrations/vllm python3 gen_coverage_support.py --repo . --out coverage-support.json

Every status comes from an object the integration defines, or from the pinned checkpoint's own config.json; nothing names a cell by hand:
  * the pins: `integrations/vllm/manifests/checkpoints.json` (repo, revision); config.json is read from the repo's stored copy
    (`engine/profiles/hf_configs/<ROLE>.config.json`) when one exists, else from the Hugging Face hub at the pinned revision, and is
    checked against the manifest's `config_sha256` when the manifest has one;
  * architectures: `engine.profiles.family_facts.FAMILY_FACTS` (the families the Build can profile);
  * operations: the served vocabulary `program.frontend.rules.vocab.PROFILE_B1_EAGER_V3` (the kinds the frontend binds; the CPU
    reference vocabulary does not count);
  * GPU targets: `program.registry.gemm_targets.gemm_target_for` for sm_89 (L40S) and sm_90 (H100);
  * target-specific facts read off the vocabulary: softcapped attention exists only as the FA2 kind (`attention_softcap`, BN =
    `fa2_kblock_n`), the MoE expert GEMM kinds take no tensor-core step (`DOT`) parameter, block FP8 is bound only for the sm_90 CUTLASS
    blockwise kernel (`TargetProfile.fp8_block_gemm`), and the per-tensor FP8 GEMM (`ScaledMmFp8_v1`) has no vocabulary kind.

Statuses: `cant-represent` (no Definition / binding for an architecture or operation), `infeasible` (representable, but vLLM cannot serve
this configuration: context beyond the model's window, weights beyond the GPUs' memory, heads not divisible by TP), `not-run`
(representable and servable, not recorded). The 12 recorded cells must come out `not-run`; the generator asserts it.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools
import json
import sys
import urllib.request
from pathlib import Path

AXES = ("model", "quantization", "gpu", "tp", "context", "sampling")
QUANT = ("none", "fp8")
GPUS = {"l40s": {"cc": (8, 9), "mem_gb": 48}, "h100": {"cc": (9, 0), "mem_gb": 80}}
TPS = (1, 2)
CONTEXTS = {"I256-O32": 288, "I1024-O128": 1152, "I4096-O512": 4608}
SAMPLING = ("greedy", "top-p 0.95, T 0.8")
#: weights may use at most this share of the GPUs' memory (KV cache and activations need the rest)
WEIGHT_SHARE = 0.9
#: the recorded cells (the 13 rows' configurations; #67/#68 share one cell): (model, quantization, gpu, tp, context, sampling)
RECORDED = [
    ("HuggingFaceTB/SmolLM2-135M", "none", "l40s", 1, "I1024-O128", "greedy"),
    ("unsloth/Llama-3.2-1B", "none", "l40s", 1, "I4096-O512", "greedy"),
    ("unsloth/Llama-3.2-1B", "none", "l40s", 1, "I1024-O128", "greedy"),
    ("Qwen/Qwen2.5-1.5B", "none", "l40s", 1, "I4096-O512", "greedy"),
    ("unsloth/gemma-2-2b", "none", "l40s", 1, "I1024-O128", "greedy"),
    ("unsloth/mistral-7b-v0.3", "none", "l40s", 1, "I1024-O128", "greedy"),
    ("allenai/OLMoE-1B-7B-0924", "none", "l40s", 1, "I1024-O128", "greedy"),
    ("allenai/OLMoE-1B-7B-0924", "none", "l40s", 2, "I1024-O128", "greedy"),
    ("Qwen/Qwen3-4B-Instruct-2507", "none", "h100", 1, "I1024-O128", "greedy"),
    ("Qwen/Qwen3-4B-Instruct-2507", "fp8", "h100", 1, "I1024-O128", "greedy"),
    ("Qwen/Qwen3-30B-A3B", "none", "l40s", 2, "I1024-O128", "greedy"),
    ("unsloth/Llama-3.2-1B", "none", "l40s", 1, "I256-O32", "top-p 0.95, T 0.8"),
]


def load_registry():
    from verity_vllm.engine.profiles.family_facts import FAMILY_FACTS
    from verity_vllm.program.frontend.rules.vocab import PROFILE_B1_EAGER_V3 as V
    from verity_vllm.program.registry.gemm_targets import gemm_target_for
    kinds, notes = V.kinds, V.notes
    targets = {}
    for g, spec in GPUS.items():
        try:
            targets[g] = gemm_target_for(spec["cc"]).key
        except Exception as e:  # UnregisteredGemmTarget
            targets[g] = None
            print(f"gpu {g}: no registered GEMM target ({e})", file=sys.stderr)
    softcap_fa3 = any(k.startswith("attention_softcap") and k != "attention_softcap" for k in kinds)
    softcap_is_fa2 = "attention_softcap" in kinds and "FA2" in (notes.get("attention_softcap") or "")
    moe_dot = "DOT" in inspect.signature(kinds["moe_expert_gemm"]).parameters if "moe_expert_gemm" in kinds else False
    return {
        "families": set(FAMILY_FACTS),
        "family_arch": {k: v.get("arch") for k, v in FAMILY_FACTS.items()},
        "kinds": set(kinds),
        "targets": targets,
        "softcap_h100": softcap_fa3 or not softcap_is_fa2,
        "moe_h100": moe_dot,
        "fp8_block": "scaled_mm_fp8_block" in kinds,
        "fp8_per_tensor": any(k in kinds for k in ("scaled_mm_fp8", "scaled_mm_fp8_tensor")),
        "awq": any("awq" in k for k in kinds),
        "layer_norm": "layer_norm" in kinds,
        "gelu_exact": "gelu" in kinds or "gelu_mul" in kinds,
    }


def load_pins(repo: Path):
    man = json.loads((repo / "integrations/vllm/manifests/checkpoints.json").read_text())
    stored = repo / "integrations/vllm/verity_vllm/engine/profiles/hf_configs"
    merged: dict = {}
    for c in man["checkpoints"]:
        m = merged.setdefault(c["repo"], dict(c))
        m["downloaded"] = bool(m.get("downloaded")) or bool(c.get("downloaded"))
        m["config_sha256"] = m.get("config_sha256") or c.get("config_sha256")
        m["role"] = f"{m.get('role', '')} {c.get('role', '')}" if m is not c and m.get("role") != c.get("role") else m.get("role", "")
    pins = []
    for c in merged.values():
        cfg, src = None, None
        want = c.get("config_sha256")
        for p in sorted(stored.glob("*.config.json")):
            b = p.read_bytes()
            if want and hashlib.sha256(b).hexdigest() == want:
                cfg, src = b, f"repo:{p.relative_to(repo)}"
                break
        if cfg is None:
            url = f"https://huggingface.co/{c['repo']}/resolve/{c['revision']}/config.json"
            with urllib.request.urlopen(url, timeout=30) as r:
                cfg = r.read()
            src = f"hub:{c['repo']}@{c['revision'][:12]}"
        want = c.get("config_sha256")
        got = hashlib.sha256(cfg).hexdigest()
        verified = (want == got) if want else None
        pins.append({"repo": c["repo"], "revision": c["revision"], "downloaded": c.get("downloaded"), "config": json.loads(cfg),
                     "config_source": src, "config_sha256": got, "config_verified": verified})
    return pins


def params_b(cfg: dict) -> float:
    """Weight count (billions) from config.json: embeddings (+ untied lm_head) + per layer attention, MLP or experts."""
    H, L, V = cfg["hidden_size"], cfg["num_hidden_layers"], cfg["vocab_size"]
    NH = cfg["num_attention_heads"]
    KVH = cfg.get("num_key_value_heads") or NH
    D = cfg.get("head_dim") or H // NH
    attn = H * NH * D + 2 * H * KVH * D + NH * D * H
    E = cfg.get("num_experts") or cfg.get("num_local_experts") or 0
    if E:
        I = cfg.get("moe_intermediate_size") or cfg["intermediate_size"]
        mlp = E * 3 * H * I + H * E
    else:
        mlp = 3 * H * cfg["intermediate_size"]
    emb = V * H * (1 if cfg.get("tie_word_embeddings") else 2)
    return (emb + L * (attn + mlp)) / 1e9


def fp8_scheme(cfg: dict) -> str | None:
    q = cfg.get("quantization_config") or {}
    if q.get("quant_method") != "fp8":
        return None
    return "block" if q.get("weight_block_size") else "per-tensor"


def decide(pin, fp8_ckpt, R, quant, gpu, tp, ctx):
    cfg = pin["config"]
    mt = cfg.get("model_type")
    arch = (cfg.get("architectures") or ["?"])[0]
    qm = (cfg.get("quantization_config") or {}).get("quant_method")
    # -- model-level representation
    if mt not in R["families"]:
        return "cant-represent", f"no family profile for model_type '{mt}' ({arch}): not in FAMILY_FACTS"
    if qm == "awq":
        return "cant-represent", "no Definition for vLLM's AWQ int4 GEMM (no AWQ kind in the served vocabulary)"
    if R["family_arch"].get(mt) == "dense-ln" and not (R["layer_norm"] and R["gelu_exact"]):
        return "cant-represent", f"no served Definition for {arch}'s LayerNorm / exact GELU (only the CPU reference vocabulary has them)"
    if R["targets"].get(gpu) is None:
        return "cant-represent", f"no registered GEMM target for {gpu}"
    # -- quantization
    if quant == "fp8":
        scheme = fp8_scheme(fp8_ckpt["config"]) if fp8_ckpt else None
        if scheme == "block":
            if not R["fp8_block"]:
                return "cant-represent", "no Definition for the block-FP8 GEMM"
            if R["targets"][gpu] != "hopper":
                return "cant-represent", "block-FP8 GEMM is registered only for the sm_90 CUTLASS blockwise kernel; on sm_89 vLLM runs its Triton w8a8 block kernel, which has no Definition"
        elif not R["fp8_per_tensor"]:
            return "cant-represent", "no FP8 checkpoint pinned: vLLM's online FP8 uses the per-tensor scaled_mm, whose Definition (ScaledMmFp8_v1) has no vocabulary binding"
    # -- attention and MoE per GPU
    if cfg.get("attn_logit_softcapping") and gpu == "h100" and not R["softcap_h100"]:
        return "cant-represent", "softcapped attention is registered only for FA2 (attention_softcap); no FA3 softcap Definition"
    if (cfg.get("num_experts") or cfg.get("num_local_experts")) and gpu == "h100" and not R["moe_h100"]:
        return "cant-represent", "the MoE expert GEMM kinds take no tensor-core step (DOT): Ampere-family only, no Hopper wgmma variant"
    total = CONTEXTS[ctx]
    win = cfg.get("sliding_window")
    uses_win = win and cfg.get("use_sliding_window", True) is not False
    # -- feasibility (vLLM refuses or cannot place the configuration)
    maxpos = cfg.get("max_position_embeddings")
    if maxpos and total > maxpos:
        return "infeasible", f"{total} tokens exceed the model's max_position_embeddings ({maxpos})"
    if uses_win and total > win:
        return "cant-represent", f"{total} tokens exceed the sliding window ({win}); the attention Definition has no sliding-window mask"
    NH = cfg["num_attention_heads"]
    KVH = cfg.get("num_key_value_heads") or NH
    if NH % tp or (KVH % tp and tp % KVH):
        return "infeasible", f"{NH} query / {KVH} KV heads do not shard over TP={tp}"
    wgb = params_b(cfg) * (1 if quant == "fp8" else 2)
    if wgb > WEIGHT_SHARE * GPUS[gpu]["mem_gb"] * tp:
        return "infeasible", f"weights (~{wgb:.0f} GB) exceed {int(WEIGHT_SHARE * 100)}% of {tp}x {gpu} memory ({GPUS[gpu]['mem_gb'] * tp} GB)"
    return "not-run", "representable, not recorded"


def compress(model, cells):
    """Rules for one model's cells: each (status, reason) group as the fewest axis-product matches (first match wins; groups are disjoint)."""
    rest = AXES[1:]
    full = {"quantization": set(QUANT), "gpu": set(GPUS), "tp": set(TPS), "context": set(CONTEXTS), "sampling": set(SAMPLING)}
    groups: dict = {}
    for key, v in cells.items():
        groups.setdefault(v, []).append(key)
    rules = []

    def cover(keys):
        sets = [sorted({k[i] for k in keys}, key=str) for i in range(len(rest))]
        if len(keys) == len(list(itertools.product(*sets))):
            return [dict(zip(rest, sets))]
        # split on the first axis with more than one value
        i = next(j for j, s in enumerate(sets) if len(s) > 1)
        out = []
        for val in sets[i]:
            out += cover([k for k in keys if k[i] == val])
        return out

    for (status, reason), keys in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        for m in cover(keys):
            match = {"model": model}
            for a, vals in m.items():
                if set(vals) == full[a]:
                    continue
                if len(vals) == 1:
                    match[a] = vals[0]
                else:
                    match[a] = vals
            rules.append({"match": match, "status": status, "reason": reason})
    return rules


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    R = load_registry()
    pins = load_pins(repo)
    by_repo = {p["repo"]: p for p in pins}
    # the site folds an FP8 checkpoint into its base model: the base is the repo without the trailing "-FP8"
    fp8_of = {p["repo"][: -len("-FP8")]: p for p in pins if p["repo"].endswith("-FP8") and fp8_scheme(p["config"])}
    models = [p for p in pins if p["repo"] not in {f["repo"] for f in fp8_of.values()}]
    all_rules, statuses = [], {}
    for p in models:
        cells = {}
        for quant, gpu, tp, ctx, samp in itertools.product(QUANT, GPUS, TPS, CONTEXTS, SAMPLING):
            cells[(quant, gpu, tp, ctx, samp)] = decide(p, fp8_of.get(p["repo"]), R, quant, gpu, tp, ctx)
        for (quant, gpu, tp, ctx, samp), (st, _r) in cells.items():
            statuses[(p["repo"], quant, gpu, tp, ctx, samp)] = st
        all_rules += compress(p["repo"], cells)
    bad = [c for c in RECORDED if statuses.get(c) != "not-run"]
    assert not bad, f"recorded cells not representable: {bad}"
    counts: dict = {}
    for st in statuses.values():
        counts[st] = counts.get(st, 0) + 1
    doc = {
        "schema": "verity-docs/coverage-support/v1",
        "source": "vllm-coordinator (bc-ecac3029), generated by gen_coverage_support.py from verity main's vLLM integration registry "
                  "(FAMILY_FACTS, the served vocabulary b1-eager-v3, gemm_targets) and the pinned checkpoints' config.json",
        "statuses": {"cant-represent": "no Definition or binding for an architecture or operation",
                     "infeasible": "representable, but vLLM cannot serve this configuration (context, memory or TP sharding)",
                     "not-run": "representable and servable, not recorded"},
        "cells": len(statuses), "counts": counts,
        "rules": all_rules + [{"match": {}, "status": "not-run", "reason": "representable, not recorded"}],
        "models": [{"repo": p["repo"], "revision": p["revision"], "model_type": p["config"].get("model_type"),
                    "architecture": (p["config"].get("architectures") or [None])[0], "downloaded": p["downloaded"],
                    "config_source": p["config_source"], "config_sha256_verified": p["config_verified"],
                    "fp8_checkpoint": fp8_of[p["repo"]]["repo"] if p["repo"] in fp8_of else None} for p in models],
    }
    Path(a.out).write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"models": len(models), "cells": len(statuses), "counts": counts, "rules": len(all_rules) + 1}))


if __name__ == "__main__":
    main()
