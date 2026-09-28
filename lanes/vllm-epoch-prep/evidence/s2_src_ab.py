"""s2_src_ab.py OUT.json BUILD_DIR... : the S2 A/B on stored Builds. For every `descriptor.json.gz` under each BUILD_DIR (step, request
and workload Programs), recompute the stored Program digest (must equal result.json's), then the digest with the SRC static's `class`
replaced by the wrapper's declared DERIVE_SOURCE (lane vllm-epoch-prep, S2). Both spellings of SRC move together: the descriptor's full
dict and the 12-hex short form `{SRC={..}}` that other ids (the workload's) carry. Prints and writes old/new digests and what moved."""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

DECLARED = {"EngineStep": "verity-vllm/engine-step/v1", "GreedyRequest": "verity-vllm/greedy-request/v1",
            "PaddedGreedyRequest": "verity-vllm/padded-greedy-request/v1",
            "StochasticEngineStep": "verity-vllm/stochastic-engine-step/v1", "StochasticRequest": "verity-vllm/stochastic-request/v1"}
PREFIXES = ("verity_vllm.program.frontend.vllm_meta.", "verity_capture.experimental.cb_a.vllm_meta.")
SRC_RE = re.compile(rb'\\"class\\":\\"((?:verity_vllm\.program\.frontend|verity_capture\.experimental\.cb_a)\.vllm_meta\.(\w+))\\",'
                    rb'\\"config_sha256\\":\\"([0-9a-f]+)\\",\\"inputs\\":(\[[0-9,\[\] ]*\]),\\"mode\\":\\"([\w-]+)\\",\\"profile\\":\\"([\w.-]*)\\"')


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def short(src: dict) -> str:
    return hashlib.sha256(json.dumps(src, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]


def moved(raw: bytes, subst: dict) -> bytes:
    for old, new in subst.items():
        raw = raw.replace(old, new)
    return raw


def main() -> None:
    out, dirs = Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]
    rows, subst_all = [], {}
    descs = sorted(p for d in dirs for p in d.rglob("descriptor.json.gz"))
    # pass 1: every SRC dict (class, config, inputs, mode, profile) the step/request Programs carry, old and new short forms
    for p in descs:
        raw = canonical({k: v for k, v in json.load(gzip.open(p)).items() if k != "annotations"})
        for m in SRC_RE.finditer(raw):
            cls_path, cls = m.group(1).decode(), m.group(2).decode()
            base = {"config_sha256": m.group(3).decode(), "inputs": json.loads(m.group(4)), "mode": m.group(5).decode(),
                    "profile": m.group(6).decode()}
            o, n = short({"class": cls_path, **base}), short({"class": DECLARED[cls], **base})
            subst_all[f"{{SRC={{{o}}}}}".encode()] = f"{{SRC={{{n}}}}}".encode()
            subst_all[f'\\"class\\":\\"{cls_path}\\"'.encode()] = f'\\"class\\":\\"{DECLARED[cls]}\\"'.encode()
        del raw
    for p in descs:
        desc = json.load(gzip.open(p))
        raw = canonical({k: v for k, v in desc.items() if k != "annotations"})
        del desc
        res = json.loads((p.parent / "result.json").read_text()) if (p.parent / "result.json").exists() else {}
        stored = (res.get("program") or {}).get("digest") or res.get("digest")
        old = hashlib.sha256(raw).hexdigest()
        hits = {k.decode(): raw.count(k) for k in subst_all if raw.count(k)}
        new_raw = moved(raw, subst_all)
        new = hashlib.sha256(new_raw).hexdigest()
        left = sum(new_raw.count(pfx.encode()) for pfx in PREFIXES)
        row = {"descriptor": str(p), "stored_digest": stored, "recomputed": old, "recomputed_equals_stored": stored in (None, old),
               "new_digest": new, "moved": old != new, "substitutions": hits, "bytes_delta": len(new_raw) - len(raw),
               "module_paths_left": left}
        rows.append(row)
        print(f"{p.parent.name:<28} stored={str(stored)[:12]} old={old[:12]} eq={row['recomputed_equals_stored']} new={new[:12]} "
              f"subs={sum(hits.values())} left={left}", flush=True)
    out.write_text(json.dumps({"schema": "vllm-epoch-prep/s2-src-ab/v1", "declared": DECLARED,
                               "substitutions": {k.decode(): v.decode() for k, v in subst_all.items()}, "rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
