"""regen13.py ROWS_DIR OLD_DIR OUT_DIR [ROW ...]: the 13 rows' program.json under the fixed max_scaled mapping (PR #99) with #94's
param_inputs, the dataset superseding art:f0c33059.

Rows with a programs artifact (fetched into ROWS_DIR/<row>/): rebuilt from their instance sequences exactly as the vu-export lane did
(its evidence program_graphs.py, --record expected), then catalogued (program_graph.catalog) and given Q_word_v1 (with_word_rules).
#4 and #101: their graphed Programs (the redraw run r20260926-035624-a133's Builds) are not in the store, so their program.json is
the previous one (OLD_DIR) with Q_word_v1 re-applied -- the label fix, no param_inputs."""
import copy
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from verity_vllm.pipeline import program_graph as PG

ROWS = {57: ("gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager", "art:5e925a59d73127305b8f6065c2ee519097c22b45c1e9d3452db338a39b65122d"),
        11: ("llama32-1b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager", "art:db4499e73020f5d761b55a801bc4d926eaad36c15099d90f170ffe00928aaaf7"),
        23: ("llama32-1b__bf16__l40s__tp1__b64__i1024__o128__mixed__greedy__bi-eager", "art:9556460da4f92484fc409d279753f26e7883853bd1b7ca9b33580d7ba9863947"),
        60: ("mistral-7b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager", "art:7d8d822f5f033d24cdc4a4e3c5d960db3fd93e00cfa5161a04b209f5d27f2580"),
        68: ("olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed-arrivals__greedy__bi-eager", "art:d3fa83361d58c702318733f7382fc41b47800ebe401c6d772e6caaad6ed72737"),
        67: ("olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager", "art:a31f7b72eb62f9d66af6f4fc861b6b351f790ece9e730dd359c2a697898292b2"),
        70: ("olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager", "art:2cadc0fc95730a77ee7117cf39bc403a3b895ad6b05642e8b403769214daf841"),
        39: ("qwen25-15b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager", "art:37cd49bd1fd652447ac421ffc6967798f67fb9b1c2d9bd13aa0d3422d15cd905"),
        75: ("qwen3-30b-a3b__bf16__l40s__tp2__b2__i1024__o128__mixed__greedy__bi-eager", "art:fad11673693df8642202ec381552ebf62f2c1c34cd437c3ec3de53d9366a884b"),
        74: ("qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager", "art:9d14bd1194738e46c0c4e56b16ecb44187e19b77389f93fd19d7cb3f5d629eda"),
        73: ("qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager", "art:f94391548214af4edbea90da0bd676d46e853989454e0693e39499f8239e1289")}
KEEP = {4: "smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager",
        101: "llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager"}
PGPY = Path.home() / ".research/notes/lanes/vllm-vu-export/evidence/program_graphs.py"


def main() -> None:
    rows_dir, old, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    only = {int(x) for x in sys.argv[4:]}
    out.mkdir(parents=True, exist_ok=True)
    for row, (key, art) in ROWS.items():
        if (only and row not in only) or (out / f"{key}.program.json").exists():
            continue
        t = time.time()
        r = subprocess.run([sys.executable, str(PGPY), str(out), key, str(rows_dir / str(row)), "--record", "expected", "--programs-art", art],
                           capture_output=True, text=True, env=dict(os.environ, VUX_REPO="/workspace/integrations/vllm"))
        print(f"#{row} graph rc={r.returncode} {time.time() - t:.0f}s {r.stdout.strip()[-300:]} {r.stderr.strip()[-600:]}", flush=True)
    for row, key in KEEP.items():
        if (only and row not in only) or (out / f"{key}.program.json").exists():
            continue
        g = json.loads((old / f"{key}.program.json").read_text())
        for x in g["groups"]:
            x.pop("q_word_v1", None)
        g.pop("q_word_v1", None)
        g["row"]["param_inputs"] = "not recorded: the redraw run's Build (r20260926-035624-a133) is not in the store"
        (out / f"{key}.program.json").write_text(json.dumps(g, separators=(",", ":"), default=str) + "\n")
        print(f"#{row} kept (label fix only)", flush=True)


def finish(out: Path) -> None:
    """catalog, then Q_word_v1 on every graph (the lane's order)."""
    PG.catalog(out)
    for f in sorted(out.glob("*.program.json")):
        t = time.time()
        g = json.loads(f.read_text())
        for x in g["groups"]:
            x.pop("q_word_v1", None)
        g = PG.with_word_rules(copy.deepcopy(g))
        f.write_text(json.dumps(g, separators=(",", ":"), default=str) + "\n")
        q = g["q_word_v1"]
        print(f"{f.name[:48]} units={q['units']} gates={q['gates']} committed={q['committed_interior_words']} viol={q['violations']} "
              f"{time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--finish":
        finish(Path(sys.argv[2]))
    else:
        main()
