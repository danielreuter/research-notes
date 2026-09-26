"""site_bundle.py (vllm-vu-export's, copied by vllm-more-exports: templates the exporter cuts beyond Gemm / attention / RoPE -- FP8 block
and MoE expert GEMM coordinates -- come from `vu_export.template_of`, and every K-parameterised template is matched by K)

site_bundle.py EXPORT_DIR OUT_DIR --run R --export-art A --set-arts JSON [--epoch E --branch B --commit C]

The docs site's raw-data bundle for one row's VU export, plus the template mix of every row whose record carries a replay
partition (tests/regression/expected/*.json), written as small JSON files:

  OUT_DIR/index.json            provenance (model, serving config, run, roots, epoch, source) and the template list
  OUT_DIR/templates/<set>.json  one exported subcircuit template: bound parameters, input count in the run, exported count, bytes,
                                a few sample instances with their exact outputs
  OUT_DIR/rows.json             per row: VU counts per Definition spec (template + bound parameters) and the subcircuit instances
                                they decompose into

Words are exact: `hex` = the port's words in order, each word as big-endian hex of its width (u16 -> 4 digits); `f32` is a
decoded preview of bf16 words (first 16), for display only.
"""
import argparse
import glob
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__import__("os").environ.get("VUX_REPO", "/workspace/integrations/vllm"))
WORD = {"u8": np.uint8, "u16": np.uint16, "u32": np.uint32, "u64": np.uint64}
SAMPLES = 3
MAX_SAMPLE_WORDS = 200_000


def statics(spec: str) -> dict:
    if "{" not in spec:
        return {}
    body, out, depth, key, buf = spec[spec.index("{") + 1: spec.rindex("}")], {}, 0, None, ""
    for ch in body + ",":
        depth += ch in "{[(" and 1 or 0
        depth -= ch in "}])" and 1 or 0
        if ch == "," and depth == 0:
            if key is not None:
                out[key] = int(buf) if buf.lstrip("-").isdigit() else buf
            key, buf = None, ""
        elif ch == "=" and depth == 0 and key is None:
            key, buf = buf.strip(), ""
        else:
            buf += ch
    return out


def prim(v) -> str:
    m = re.search(r'"fn"\s*:\s*"([^"]+)"', str(v))
    return m.group(1) if m else str(v)


def template_of(spec: str) -> tuple[str, dict, int]:
    """Definition spec of a VU -> (subcircuit template, bound parameters, instances per VU), the exporter's decomposition."""
    fam, st = spec.split("{", 1)[0], statics(spec)
    if fam in ("Gemm_v1", "Gemm_v2", "MoeExpertGemm_v1", "MoeExpertGemmW_v1") and "K" in st and "N" in st and fam.startswith("Gemm"):
        dot = "AmpereBF16TcDot16_v1" if fam == "Gemm_v1" else prim(st.get("DOT"))
        return "GemmCoordinate", {"K": st["K"], "dot": dot}, int(st["N"])
    if fam in ("Attention_v3", "Attention_v2"):
        dot, inv = ("AmpereBF16TcDot16_v1", "Fa2InvSum_v1") if fam == "Attention_v3" else (prim(st.get("DOT")), prim(st.get("INV")))
        p = {"D": st["D"], "BN": st["BN"], "dot": dot, "inv": inv, "NB": st.get("NB"), "last_block": st.get("last")}
        return "AttentionHead", p, int(st["NH"])
    if fam == "RoPE_v1":
        return "RoPEHead", {"D": st["D"]}, int(st["NHEADS"])
    from verity_vllm.pipeline.vu_export import template_of as cut
    return cut(spec)


def serving(row_key: str) -> dict:
    wl = json.loads((REPO / "workloads" / f"{row_key}.json").read_text())
    parts = row_key.split("__")
    return {"row_key": row_key, "model": wl.get("model"), "dtype": parts[1], "gpu": parts[2], "tp": parts[3], "batch": parts[4],
            "context_class": wl.get("context_class"), "serving_profile": wl.get("serving_profile"),
            "sampling": {"variant": (wl.get("sampling") or {}).get("variant"),
                         **(wl.get("variants") or {}).get((wl.get("sampling") or {}).get("variant"), {})},
            "execution": parts[-1], "prompt_lengths": wl.get("prompt_lengths"), "max_tokens": wl.get("max_tokens"),
            "engine_args_required": wl.get("engine_args_required")}


def words(d: Path, port: dict, n: int) -> list[np.ndarray]:
    arr = np.frombuffer((d / port["file"]).read_bytes(), dtype=np.dtype(WORD[port["dtype"]]).newbyteorder("<"))
    if port.get("words") is not None:
        return list(arr.reshape(n, int(port["words"])))
    offs = np.frombuffer((d / port["offsets"]).read_bytes(), dtype="<u8").astype(np.int64)
    return [arr[offs[i]:offs[i + 1]] for i in range(n)]


def enc(a: np.ndarray, dtype: str) -> dict:
    w = {"u8": 2, "u16": 4, "u32": 8, "u64": 16}[dtype]
    out = {"dtype": dtype, "words": int(a.size), "hex": "".join(f"{int(x):0{w}x}" for x in a.tolist())}
    if dtype == "u16":
        out["f32"] = [float(v) for v in (a[:16].astype(np.uint32) << 16).view(np.float32)]
    return out


def rows_mix(extra: dict[str, dict] | None = None) -> dict:
    """`extra`: row key -> {"row", "class", "sampled_replay": path, "run"} for rows whose record of choice is a run's own replay."""
    out = {}
    for f in sorted(glob.glob(str(REPO / "tests/regression/expected/*.json"))):
        d = json.loads(Path(f).read_text())
        key = Path(f).stem
        if key in (extra or {}):
            x = extra[key]
            sr = json.loads(Path(x["sampled_replay"]).read_text())["sampled_replay"]
            d = {"row": x["row"], "class": x["class"], "reference": {"run": x["run"], "source": "that run's commit/sampled_replay_p0.json"},
                 "program_digest": {"program_digest_of_record": x.get("program_digest")},
                 "replay_partition": {"strata": sr["strata"], "population": sr["population"]}}
        strata = (d.get("replay_partition") or {}).get("strata") or {}
        entry = {"row": d.get("row"), "class": d.get("class"), "serving": serving(key),
                 "program_digest": d.get("program_digest", {}).get("program_digest_of_record") if isinstance(d.get("program_digest"), dict) else None,
                 "reference": d.get("reference")}
        if not strata:
            entry["template_mix"] = None
            entry["why"] = "no replay partition on this row's record (FAIL class or a record without the sampled replay)"
            out[key] = entry
            continue
        by_spec = Counter()
        for k, v in strata.items():
            by_spec[k.split("|")[0]] += int(v.get("population", 0))
        tmix: dict[str, dict] = {}
        for spec, n in sorted(by_spec.items()):
            t, p, mult = template_of(spec)
            tid = t + json.dumps({k: v for k, v in p.items() if v is not None}, sort_keys=True, separators=(",", ":"))
            e = tmix.setdefault(tid, {"template": t, "params": {k: v for k, v in p.items() if v is not None}, "vus": 0, "instances": 0,
                                      "specs": {}})
            e["vus"] += n
            e["instances"] += n * mult
            e["specs"][spec] = n
        entry["vus_by_family"] = ((d.get("replay_partition") or {}).get("population") or {}).get("by_family")
        entry["vus_by_spec"] = dict(by_spec)
        entry["template_mix"] = sorted(tmix.values(), key=lambda e: -e["instances"])
        out[key] = entry
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("export_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--run", required=True)
    ap.add_argument("--export-art", required=True)
    ap.add_argument("--set-arts", required=True)
    ap.add_argument("--epoch", default="pre-epoch")
    ap.add_argument("--branch", default=None)
    ap.add_argument("--commit", default=None)
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--extra-row", action="append", default=[], metavar="JSON", help='{"key", "row", "class", "run", "sampled_replay", "program_digest"}')
    a = ap.parse_args()
    exp, out = Path(a.export_dir), Path(a.out_dir)
    (out / "templates").mkdir(parents=True, exist_ok=True)
    summary = json.loads((exp / "export.json").read_text())
    prov = summary["provenance"]
    arts = json.loads(a.set_arts)
    mix = rows_mix({x["key"]: x for x in map(json.loads, a.extra_row)})
    row_key = prov["row_key"]
    run_specs = mix.get(row_key, {}).get("vus_by_spec") or {}
    templates = []
    for s in summary["sets"]:
        d = exp / "sets" / s["set"]
        man = json.loads((d / "manifest.json").read_text())
        idx = json.loads((d / "index.json").read_text())
        rel, n = man["relation"], man["n"]
        fam = rel["definition"]
        # the input count in the run: every instance of this template the run's VUs decompose into
        in_run, vus_in_run, specs = 0, 0, {}
        for spec, cnt in run_specs.items():
            if spec.split("{", 1)[0] != fam:
                continue
            t, p, mult = template_of(spec)
            st = rel.get("statics") or {}
            if "K" in p and p["K"] != st.get("K"):
                continue
            if t in ("AttentionHead", "RoPEHead") and p["D"] != st.get("D"):
                continue
            in_run += cnt * mult
            vus_in_run += cnt
            specs[spec] = cnt
        ports = {k: words(d, p, n) for k, p in man["ports"].items()}
        picks = sorted({0, n // 2, n - 1})[:SAMPLES]
        samples = []
        for i in picks:
            row = idx["rows"][i]
            if sum(int(ports[k][i].size) for k in ports) > MAX_SAMPLE_WORDS and samples:
                continue
            outs = {k: enc(ports[k][i], man["ports"][k]["dtype"]) for k in ports if k in ("y", "out") or k.startswith("out.")}
            ins = {k: enc(ports[k][i], man["ports"][k]["dtype"]) for k in ports if k not in outs}
            samples.append({"id": row[0], "source": {"vu": row[1], "request": row[2], "engine_step": row[3], "op_path": row[4],
                                                     "row": row[5], "phase": row[6], "value": row[7], "sub": row[8]},
                            "inputs": ins, "outputs": outs})
        t = {"schema": "vllm-vu-site/template/v1", "set": s["set"], "template": rel.get("subcircuit"), "relation": rel,
             "bound_params": rel.get("statics"), "ports": {k: {kk: vv for kk, vv in p.items() if kk in ("dtype", "words")} for k, p in man["ports"].items()},
             "input_count_in_run": in_run, "vus_in_run": vus_in_run, "vu_specs_in_run": specs,
             "exported": n, "exported_vus": len({r[1] for r in idx["rows"]}), "bytes": s["bytes"], "content_digest": man["content_digest"],
             "artifact": arts.get(s["set"]), "samples": samples,
             "encoding": "hex: the port's words in order, each word big-endian hex of its width; f32: decoded bf16 preview (first 16)"}
        (out / "templates" / f"{s['set']}.json").write_text(json.dumps(t, separators=(",", ":")) + "\n")
        templates.append({k: t[k] for k in ("set", "template", "bound_params", "input_count_in_run", "vus_in_run", "exported",
                                             "exported_vus", "bytes", "artifact")} | {"file": f"templates/{s['set']}.json"})
    index = {"schema": "vllm-vu-site/index/v1", "row": prov.get("row"), "serving": serving(row_key),
             "provenance": {"model": prov.get("model"), "revision": prov.get("revision"), "run": a.run, "run_root": prov["run_root"],
                            "program_digests": prov.get("program_digests"), "manifest_digest": prov.get("manifest_digest"),
                            "epoch": a.epoch, "source": {"commit": a.commit, "dirty": False, "branch": a.branch},
                            "gpu": prov.get("gpu") or serving(row_key)["gpu"], "versions": prov.get("versions"),
                            "selection": prov.get("selection"), "export_artifact": a.export_art},
             "population": summary["population"], "by_family": summary["by_family"], "templates": templates,
             "not_exported": summary["population"].get("not_exported_families"),
             "notes": a.note,
             "table2": "not admitted: captured realistic-distribution sets await Daniel's decision",
             "files": {"templates": "templates/<set>.json", "rows": "rows.json"}}
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    (out / "rows.json").write_text(json.dumps({"schema": "vllm-vu-site/rows/v1",
                                               "source": "tests/regression/expected/<row>.json replay_partition.strata (population per stratum)",
                                               "rows": mix}, indent=1) + "\n")


if __name__ == "__main__":
    main()
