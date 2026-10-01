#!/usr/bin/env python3
"""Append the grid's 3 more models (circuits 1555Z: 2-3 more small ungated models, smallest first, TP1) to gm-feed's items.json as wave 5,
and their questions to the labeller's questions.json. Pleias-350m, danube3-500m and salamandra-2b, registered on
cursor/grid-models-more-be5a (the boundary tree + the checkpoints and 72 workloads), synced to node 1 as TREE.

    add_models.py [--write]      (on vy-nebius-1, in /workspace/jobs/gm-feed; backs both files up first)

Keys continue after the last item (cov-gm373...) and must be new to log.jsonl, done.jsonl and attempted.txt. Order: make_items.py's tiers
(cheapest first), smallest model first within a tier. Resources and env as make_items.py's."""
import json
import sys
import time
from pathlib import Path

HERE = Path("/workspace/jobs/gm-feed")
LABEL = Path("/workspace/jobs/gm-label")
DISPATCH = Path("/workspace/jobs/dispatch")
TREE = "/workspace/research/trees/cursor-grid-models-more-be5a"
#: (role, model id, repo, revision, family, vocab)
MODELS = [("PLEIAS_350M", "pleias-350m", "PleIAs/Pleias-350m-Preview", "f175e52d0411f2c5273b5de549ddc98ce7f3f5d6", "pleias", 65536),
          ("DANUBE3_500M", "danube3-500m", "h2oai/h2o-danube3-500m-base", "0ac6d9d2999a15761bf1cb03d480a1f8e2c845a6", "danube", 32000),
          ("SALAMANDRA_2B", "salamandra-2b", "BSC-LT/salamandra-2b", "f3a6092c93948fea08ab618388d7b78c40ad63df", "salamandra", 256000)]
#: make_items.py's GumbelTopPTokenSelect_v2 limits at S=32, plus the two new vocabularies: 32000 takes 32768's limit (it is smaller),
#: 65536 is 64000's scaled by the vocabulary (both interpolated from the measured gates, ~15% over)
MAX_GATES = {32000: 30_000_000, 65536: 62_000_000, 256000: 225_000_000}
SAMPLINGS = ["greedy", "stoch-t0.8-p0.95", "stoch-t0.8-p1"]
STOCH = SAMPLINGS[1:]
TIERS = [([1], [(256, 32)], ["greedy"]), ([8], [(256, 32)], ["greedy"]), ([1], [(1024, 128)], ["greedy"]),
         ([8], [(256, 32)], STOCH), ([8], [(1024, 128)], ["greedy"]), ([8], [(1024, 128)], STOCH),
         ([1], [(256, 32)], STOCH), ([1], [(1024, 128)], STOCH),
         ([16], [(256, 32)], SAMPLINGS), ([32], [(256, 32)], SAMPLINGS), ([16], [(1024, 128)], SAMPLINGS), ([32], [(1024, 128)], SAMPLINGS)]


def resources(B, I, s, vocab):
    build = 48 if B <= 8 else 64 if (B == 16 and I == 256) else 80 if B == 16 else 96 if I == 256 else 128
    if B == 1 and s != "greedy":
        build = max(build, int(MAX_GATES[vocab] * 648.6 / 2**30 * 1.15) + 8)
    return {"build": {"cpus": 4, "memory": build}, "gpu": {"cpus": 4, "gpus": 1, "memory": 64 if B == 1 else 170}}


def main():
    items = json.loads((HERE / "items.json").read_text())
    questions = json.loads((LABEL / "questions.json").read_text())
    have = {i["key"] for i in items}
    assert not any(i["item"]["env"]["ROLE"] == MODELS[0][0] for i in items), "already added"
    named = (DISPATCH / "log.jsonl").read_text() + ((DISPATCH / "done.jsonl").read_text() if (DISPATCH / "done.jsonl").exists() else "")
    named += (HERE / "attempted.txt").read_text()
    n = max(int(k[len("cov-gm"):]) for k in have if k[len("cov-gm"):].isdigit())
    out = []
    for t, (bs, ctx, ss) in enumerate(TIERS):
        for role, mid, repo, rev, fam, vocab in MODELS:
            for B in bs:
                for I, O in ctx:
                    for s in ss:
                        n += 1
                        key, row = f"cov-gm{n:03d}", f"{mid}__bf16__rtxpro6000__tp1__b{B}__i{I}__o{O}__mixed__{s}__bi-eager"
                        assert key not in have and f"/{key}\"" not in named and key not in named.split(), key
                        assert Path(f"{TREE}/integrations/vllm/workloads/{row}.json").exists(), row
                        q = (f"Does the {fam} family's {repo} ({mid}, {role}) hold through Build, Commit and the 460-unit replay at "
                             f"TP1 B{B} {I}/{O} {s} on sm_120? (circuits-grid-models, overnight grid: the 3 more models of circuits 1555Z)")
                        env = {"BUILD_TIMEOUT": "7200", "CAMPAIGN": "overnight-sep30", "COMMIT_STALL_S": "3600", "CONFIG_BASELINE": "1",
                               "CONFIG_RUN": "1", "REPLAY_K": "460", "REPO": repo, "RESEARCH_QUESTION": q, "REVISION": rev, "ROLE": role,
                               "ROW": row, "SWEEP_DIR": f"/workspace/jobs/cov/{key}"}
                        if B == 1 and s != "greedy":
                            g = f"GumbelTopPTokenSelect_v2={MAX_GATES[vocab]}"
                            env.update(VERITY_QWORD_MAX_GATES=g, VERITY_QWORD_MAX_GATES_ALLOWED=g)
                        out.append({"key": key, "wave": 5, "tier": t, "role": role, "batch": B, "tp": 1,
                                    "item": {"env": env, "resources": resources(B, I, s, vocab), "template": "config-run", "tree": TREE}})
                        questions[key] = {"q": q, "row": row, "role": role, "wave": 5, "tier": t}
    assert len(out) == 72, len(out)
    print(len(out), out[0]["key"], out[-1]["key"])
    for o in out[:4]:
        print(o["key"], o["item"]["env"]["ROW"], o["item"]["resources"]["build"]["memory"])
    if "--write" in sys.argv:
        stamp = time.strftime("%H%MZ", time.gmtime())
        for path, doc in ((HERE / "items.json", items + out), (LABEL / "questions.json", questions)):
            path.with_name(f"{path.stem}.bak-{stamp}.json").write_text(path.read_text())
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(doc, indent=1) + "\n")
            tmp.replace(path)
        print("wrote", HERE / "items.json", LABEL / "questions.json", "backups", stamp)


if __name__ == "__main__":
    main()
