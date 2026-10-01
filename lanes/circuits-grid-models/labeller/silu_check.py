#!/usr/bin/env python3
"""Every SiluMul_v1 mismatch of a cov-gm item's replay, element by element, against the registered SiluMulBf16_v1 and the quarantined
SiluMulBf16_v2 (lane vllm-coverage-defs: vLLM `_C.silu_and_mul` on the red-team's sm_120 edge words). Reads the row's slim keep and
sampled replay record in place on vy-nebius-1, elsewhere fetches them from there into /tmp/gm/dive/<item>/, and reads the committed
words through the replay's own CommittedStore.

    cd /workspace/integrations/vllm && /workspace/.venv/bin/python <this> cov-gm001
"""
import json
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np

from verity_vllm.check.replay.opening import CommittedStore
from verity_vllm.commit import store_dump as SD
from verity_vllm.commit.opened import OpenedReader
from verity_vllm.program.registry import prims as P
from verity_vllm.program.registry.quarantine.act import silu_mul_bf16 as Q

RESEARCH = "/workspace/.venv/bin/research"


def fetch(item: str) -> Path:
    here = sorted(Path(f"/workspace/jobs/cov/{item}").glob("*/commit"))
    if here and (here[0] / "replay_slim_p0" / "slim.json").exists():
        return here[0]
    d = Path("/tmp/gm/dive") / item
    if not (d / "replay_slim_p0" / "slim.json").exists():
        d.mkdir(parents=True, exist_ok=True)
        ssh = subprocess.run([RESEARCH, "pods", "ssh", "vy-nebius-1", "--print"], capture_output=True, text=True, check=True).stdout.split()
        tar = subprocess.run([*ssh, f"cd /workspace/jobs/cov/{item}/*/commit && tar -cf - replay_slim_p0 sampled_replay_p0.json"],
                             capture_output=True, check=True, timeout=300).stdout
        subprocess.run(["tar", "-C", str(d), "-xf", "-"], input=tar, check=True)
    return d


def bf(b: int) -> float:
    return struct.unpack(">f", struct.pack(">I", int(b) << 16))[0]


def main(item: str) -> int:
    d = fetch(item)
    sr = json.loads((d / "sampled_replay_p0.json").read_text())["sampled_replay"]
    k = d / "replay_slim_p0"
    cs = CommittedStore(json.loads((k / "binding_map.json").read_text()), OpenedReader(*SD.load(k / "store")))
    v1, v2 = P.SiluMulBf16.evaluate, Q.SiluMulBf16.evaluate
    rc = 0
    for m in sr.get("mismatch") or []:
        if not m["spec"].startswith("SiluMul_v1"):
            print(f"{item}: {m['spec']} at {m['op_path']}: not a SiluMul_v1 mismatch, not checked")
            rc = 1
            continue
        n = int(m["spec"].split("I=")[1].rstrip("}"))
        rid, step, row = m["request_id"], int(m["engine_step"]), int(m["row"])
        ident = m["inputs"][0]["identity"]
        gu, _ = cs.words(rid, step, ident[2], ident[3], int(ident[4][0]), int(ident[4][1]))
        out, _ = cs.words(rid, step, m["op_path"], "out", row * n, (row + 1) * n)
        if gu is None or out is None:
            print(f"{item}: {m['op_path']} row {row}: the slim keep does not open these words")
            rc = 1
            continue
        gu, out = np.asarray(gu).astype(np.uint16), np.asarray(out).astype(np.uint16)
        e = lambda fn: [i for i in range(n) if fn(int(gu[i]), int(gu[n + i])) != int(out[i])]  # noqa: E731
        d1, d2 = e(v1), e(v2)
        print(f"{item}: {m['op_path']} {rid} step {step} row {row}: v1 differs at {len(d1)} of {n} elements, v2 at {len(d2)}")
        for i in d1[:8]:
            g, u = int(gu[i]), int(gu[n + i])
            print(f"  [{i}] gate 0x{g:04x} ({bf(g)}) up 0x{u:04x} ({bf(u)}): committed 0x{int(out[i]):04x}, v1 0x{v1(g, u):04x}, "
                  f"v2 0x{v2(g, u):04x}")
        if d2:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
