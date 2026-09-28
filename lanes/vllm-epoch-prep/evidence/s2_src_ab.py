"""s2_src_ab.py OUT.json [--max-gz-mb N] BUILD_DIR... : the S2 A/B on stored Builds. For every `descriptor.json.gz` under each BUILD_DIR
(step and request Programs first, then the workload Program), recompute the stored Program digest (must equal result.json's /
workload_program.json's), then the digest with the SRC static's `class` replaced by the wrapper's declared DERIVE_SOURCE (lane
vllm-epoch-prep, S2). What moves: the class token (at any JSON escape level), the 12-hex short form `{SRC={..}}`, and -- in the workload
Program, whose `WorkloadRequest_v1{program_digest=..}` embeds them -- the request Programs' own digests. Descriptors over N MB gz are
skipped (VM memory), and named."""
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


def load(p: Path) -> bytes:
    return canonical({k: v for k, v in json.load(gzip.open(p)).items() if k != "annotations"})


def stored_digest(d: Path):
    if (d / "result.json").exists():
        r = json.loads((d / "result.json").read_text())
        return (r.get("program") or {}).get("digest")
    if (d / "workload_program.json").exists():
        return json.loads((d / "workload_program.json").read_text()).get("workload_digest")
    return None


def main() -> None:
    args = sys.argv[1:]
    out = Path(args.pop(0))
    max_mb = 40.0
    if args and args[0] == "--max-gz-mb":
        args.pop(0)
        max_mb = float(args.pop(0))
    descs = sorted(p for d in map(Path, args) for p in d.rglob("descriptor.json.gz"))
    descs = [p for p in descs if "workload" not in p.parent.name] + [p for p in descs if "workload" in p.parent.name]
    subst: dict[bytes, bytes] = {}
    rows = []
    for p in descs:
        if p.stat().st_size > max_mb * 2**20:
            rows.append({"descriptor": str(p), "skipped": f"{p.stat().st_size / 2**20:.0f} MB gz > {max_mb:.0f} MB (VM memory)"})
            print(f"{p.parent.name:<28} skipped ({p.stat().st_size / 2**20:.0f} MB gz)", flush=True)
            continue
        raw = load(p)
        for m in SRC_RE.finditer(raw):
            cls_path, cls = m.group(1).decode(), m.group(2).decode()
            base = {"config_sha256": m.group(3).decode(), "inputs": json.loads(m.group(4)), "mode": m.group(5).decode(),
                    "profile": m.group(6).decode()}
            subst[f"{{SRC={{{short({'class': cls_path, **base})}}}}}".encode()] = f"{{SRC={{{short({'class': DECLARED[cls], **base})}}}}}".encode()
            subst[cls_path.encode()] = DECLARED[cls].encode()
        stored = stored_digest(p.parent)
        old = hashlib.sha256(raw).hexdigest()
        hits = {k.decode(): raw.count(k) for k in subst if raw.count(k)}
        new_raw = moved(raw, subst)
        new = hashlib.sha256(new_raw).hexdigest()
        left = sum(new_raw.count(pfx.encode()) for pfx in PREFIXES)
        if "workload" not in p.parent.name:
            subst[old.encode()] = new.encode()
        row = {"descriptor": str(p), "stored_digest": stored, "recomputed": old, "recomputed_equals_stored": stored in (None, old),
               "new_digest": new, "moved": old != new, "substitutions": hits, "bytes_delta": len(new_raw) - len(raw), "module_paths_left": left}
        rows.append(row)
        del raw, new_raw
        print(f"{p.parent.name:<28} stored={str(stored)[:12]} old={old[:12]} eq={row['recomputed_equals_stored']} new={new[:12]} "
              f"subs={sum(hits.values())} left={left}", flush=True)
    out.write_text(json.dumps({"schema": "vllm-epoch-prep/s2-src-ab/v2", "declared": DECLARED, "rows": rows,
                               "substitutions": {k.decode(): v.decode() for k, v in subst.items()}}, indent=1) + "\n")


if __name__ == "__main__":
    main()
