"""The grid-models dispatcher items, in submission order: [{"key", "item"}] -> /tmp/gm/items.json."""
import json
from pathlib import Path

TREE = "/workspace/research/trees/cursor-grid-models-8c79"
plan = {m["role"]: m for m in json.loads(Path("/tmp/gm/plan.json").read_text())}
SMALL = ["QWEN3_06B", "QWEN25_05B_INSTRUCT", "FALCON3_1B", "QWEN25_CODER_15B", "R1_DISTILL_QWEN_15B", "QWEN3_17B", "SMOL17B",
         "QWEN25_3B", "LLAMA32_3B", "YI15_6B"]
BIG = ["QWEN3_8B", "LLAMA31_8B", "R1_DISTILL_LLAMA_8B", "MISTRAL7B_INSTRUCT", "FALCON3_7B", "OLMOE_0125_INSTRUCT", "QWEN3_30B_A3B_2507"]
TP2 = ["QWEN3_14B", "PHI4"]
LAST = ["GEMMA2_9B"]
SAMPLINGS = ["greedy", "stoch-t0.8-p0.95", "stoch-t0.8-p1"]
CTX = [(256, 32), (1024, 128)]
#: GumbelTopPTokenSelect_v2's raised limit at S=32 by vocabulary (note:20260930T1133Z-handoff-from-vllm-coverage-defs-topp-maxgates-table;
#: 64000, 100352 and 131072 interpolated from its measured gates, ~15% over)
MAX_GATES = {32768: 30_000_000, 49152: 44_000_000, 50304: 45_000_000, 64000: 60_000_000, 100352: 92_000_000, 128256: 113_000_000,
             131072: 120_000_000, 151936: 136_000_000, 256000: 225_000_000}
HFC = Path("/workspace/integrations/vllm/verity_vllm/engine/profiles/hf_configs")
FAMILY = {"QWEN25_3B": "qwen25", "QWEN25_05B_INSTRUCT": "qwen25", "QWEN25_CODER_15B": "qwen25", "R1_DISTILL_QWEN_15B": "qwen25",
          "QWEN3_06B": "qwen3", "QWEN3_17B": "qwen3", "QWEN3_8B": "qwen3", "QWEN3_14B": "qwen3", "QWEN3_30B_A3B_2507": "qwen3",
          "LLAMA32_3B": "llama3", "LLAMA31_8B": "llama3", "R1_DISTILL_LLAMA_8B": "llama3", "SMOL17B": "smollm2",
          "MISTRAL7B_INSTRUCT": "mistral", "GEMMA2_9B": "gemma2", "OLMOE_0125_INSTRUCT": "olmoe", "PHI4": "phi", "YI15_6B": "yi",
          "FALCON3_1B": "falcon3", "FALCON3_7B": "falcon3"}


def rows(role, batches):
    m = plan[role]
    for B in batches:
        for I, O in CTX:
            for s in SAMPLINGS:
                yield role, B, I, O, s, f"{m['model_id']}__bf16__rtxpro6000__tp{m['tp']}__b{B}__i{I}__o{O}__mixed__{s}__bi-eager"


def resources(role, B, I, s, tp):
    vocab = json.loads((HFC / f"{role}.config.json").read_text())["vocab_size"]
    build = 48 if B <= 8 else 64 if (B == 16 and I == 256) else 80 if B == 16 else 96 if I == 256 else 128
    if B == 1 and s != "greedy":
        build = max(build, int(MAX_GATES[vocab] * 648.6 / 2**30 * 1.15) + 8)
    if tp == 2:
        return {"build": {"cpus": 4, "memory": build}, "gpu": {"cpus": 8, "gpus": 2, "memory": 128 if B == 1 else 340}}
    return {"build": {"cpus": 4, "memory": build}, "gpu": {"cpus": 4, "gpus": 1, "memory": 64 if B == 1 else 170}}


STOCH = SAMPLINGS[1:]
#: cheapest first within a wave: (batches, contexts, samplings)
B1B8 = [([1], [(256, 32)], ["greedy"]), ([8], [(256, 32)], ["greedy"]), ([1], [(1024, 128)], ["greedy"]),
        ([8], [(256, 32)], STOCH), ([8], [(1024, 128)], ["greedy"]), ([8], [(1024, 128)], STOCH),
        ([1], [(256, 32)], STOCH), ([1], [(1024, 128)], STOCH)]
B16B32 = [([16], [(256, 32)], SAMPLINGS), ([32], [(256, 32)], SAMPLINGS), ([16], [(1024, 128)], SAMPLINGS),
          ([32], [(1024, 128)], SAMPLINGS)]
#: circuits 07:19Z: TP1 B1/B8 of the 10 models under 7B first, then the rest; the 14B models' TP1 rows are B1/B8 256/32 on node 1, and
#: their TP2 rows wait for infra's answer on routing TP2 to node 2. (wave, tiers, roles, tp override, contexts allowed)
WAVES = [(1, B1B8, SMALL, None, None),
         (2, B1B8, BIG + LAST + TP2, {"QWEN3_14B": 1, "PHI4": 1}, {"QWEN3_14B": [(256, 32)], "PHI4": [(256, 32)]}),
         (3, B16B32, SMALL, None, None),
         (4, B1B8, TP2, None, None)]
order = []
for wave, tiers, roles, tp_over, ctx_only in WAVES:
    for t, (bs, ctx, ss) in enumerate(tiers):
        for role in roles:
            m = plan[role]
            tp = (tp_over or {}).get(role, m["tp"])
            for B in bs:
                for I, O in ctx:
                    if ctx_only and role in ctx_only and (I, O) not in ctx_only[role]:
                        continue
                    for s in ss:
                        order.append((wave, t, role, tp, B, I, O, s,
                                      f"{m['model_id']}__bf16__rtxpro6000__tp{tp}__b{B}__i{I}__o{O}__mixed__{s}__bi-eager"))
assert len(order) == len(set(r[-1] for r in order)) == 372, len(order)
out = []
for n, (wave, tier, role, tp, B, I, O, s, row) in enumerate(order, 1):
    m = plan[role]
    assert Path(f"/workspace/integrations/vllm/workloads/{row}.json").exists(), row
    key = f"cov-gm{n:03d}"
    vocab = json.loads((HFC / f"{role}.config.json").read_text())["vocab_size"]
    q = (f"Does the {FAMILY[role]} family's {m['repo']} ({m['model_id']}, {role}) hold through Build, Commit and the 460-unit replay at "
         f"TP{tp} B{B} {I}/{O} {s} on sm_120? (circuits-grid-models, overnight grid: 30 models / 10 families / 400 deployments)")
    env = {"BUILD_TIMEOUT": "7200", "CAMPAIGN": "overnight-sep30", "COMMIT_STALL_S": "3600", "CONFIG_BASELINE": "1", "CONFIG_RUN": "1",
           "REPLAY_K": "460", "REPO": m["repo"], "RESEARCH_QUESTION": q, "REVISION": m["revision"], "ROLE": role, "ROW": row,
           "SWEEP_DIR": f"/workspace/jobs/cov/{key}"}
    if B == 1 and s != "greedy":
        g = f"GumbelTopPTokenSelect_v2={MAX_GATES[vocab]}"
        env.update(VERITY_QWORD_MAX_GATES=g, VERITY_QWORD_MAX_GATES_ALLOWED=g)
    if role == "QWEN3_30B_A3B_2507":
        # 56.9 GiB of weights at TP1: row.py's default 0.5 of a 96 GB card leaves the KV cache -9.8 GiB (cov-gm127)
        env["GPU_UTIL"] = "0.9"
    out.append({"key": key, "wave": wave, "tier": tier, "role": role, "batch": B, "tp": tp,
                "item": {"env": env, "resources": resources(role, B, I, s, tp), "template": "config-run", "tree": TREE}})
Path("/tmp/gm/items.json").write_text(json.dumps(out, indent=1) + "\n")
print(len(out), out[0]["key"], out[-1]["key"])
for o in out[:2] + out[3:4] + out[150:151] + out[-13:-12]:
    print(o["key"], json.dumps(o["item"])[:600])
