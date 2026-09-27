"""Serving's multi-member files against M0's own writer (verity_flock.circuit.write, read-only), member by member.

  captured WINDOW_OUT PARTITION_JSON OUT SET...      commit the captured sets as the partition's members (CPU check of the format)
  served   WINDOW_DIR PARTITION_JSON OUT SET...      a served window: its rows equal the captured instances they share, then M0

SET... are the captured input sets in the partition's member order.  For each member: M0 composes the circuit bound to the
partition (--partition, --program); serving writes m<k>-pub/inst from its window; M0's write() gets the same rows, salts, domains
(its identity_digest pointed at serving's bindings) and global unit indices, and the files must be byte-identical.
"""
import hashlib, json, os, sys, time
from pathlib import Path

import numpy as np
import verity.commitments.identity as ID
from verity_numerical.bench.input_sets import InputSet
from verity_flock import circuit as C
from verity_vllm.commit import serving_rows as SR

mode, wd, part_file, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
sets = [InputSet.open(p) for p in sys.argv[5:]]
part = json.loads(part_file.read_text())
out.mkdir(parents=True, exist_ok=True)
res: dict = {"mode": mode, "partition": part["partition_digest"], "members": []}


def cols(s, names, lo=0, hi=None):
    hi = s.n if hi is None else hi
    return {p: np.asarray(s.port(p, lo, hi), dtype=np.uint16).reshape(hi - lo, -1) for p in names}


if mode == "captured":
    tmpls = part["partition"]["query"]["params"]["templates"]
    ms, base = [], 0
    datas = []
    for t, s in zip(tmpls, sets, strict=True):
        ins, outs = [(p.name, int(p.words)) for p in s.subcircuit.inputs], [(p.name, int(p.words)) for p in s.subcircuit.outputs]
        d = {"rows": cols(s, [p for p, _ in ins]), "outs": cols(s, [p for p, _ in outs])}
        tables = ()
        if t.startswith("GemmCoordinate"):                 # the captured coordinates as M0's share() tables them
            tb, rf = C.share(d["rows"])
            d = {"rows": tb, "outs": d["outs"], "refs": np.stack([rf[p] for p, _ in ins], axis=1)}
            tables = tuple((p, len(tb[p])) for p, _ in ins)
        ms.append(SR.Member(t, tuple(ins), tuple(outs), s.n, base, tables=tables))
        datas.append(d)
        base += s.n
    w = SR.Window(part["partition"], part["partition_digest"], base, "captured/" + part["partition_digest"][:16], tuple(ms))
    t0 = time.perf_counter()
    c = SR.commit(w, datas, workers=8)
    res["serving_s"] = round(time.perf_counter() - t0, 3)
    SR.write(c, wd, {"row": 101, "run": w.run}, SR.index_doc(ms, [[] for _ in ms], w.run))

win = json.loads((wd / "window.json").read_text())
rec = json.loads((wd / "registration.json").read_text())
idx = json.loads((wd / "index.json").read_text())
ok = True
for k, (mem, s) in enumerate(zip(win["members"], sets, strict=True)):
    n, rports, oports = int(mem["n"]), mem["ports"], mem["out_ports"]
    shared = mem.get("shared_rows")
    priv = np.frombuffer((wd / f"m{k}-private.bin").read_bytes(), dtype=np.uint8)
    pub = np.frombuffer((wd / f"m{k}-public.bin").read_bytes(), dtype=np.uint8)
    served, tables, tsalts, off = {}, {}, {}, 0
    if shared:                                              # tables, their salts, then b || c, refs, outputs
        for p, w in rports:
            R = int(shared[p]); tables[p] = priv[off:off + R * w * 2].view("<u2").reshape(R, w); off += R * w * 2
        for p, _ in rports:
            R = int(shared[p]); tsalts[p] = [bytes(priv[off + i * SR.SALT_BYTES: off + (i + 1) * SR.SALT_BYTES]) for i in range(R)]; off += R * SR.SALT_BYTES
        o = sum(int(shared[p]) for p, _ in rports) * SR.BC_BYTES
        refs = pub[o:o + n * len(rports) * 4].view("<u4").reshape(n, len(rports))
        outs_all = pub[o + n * len(rports) * 4:].view("<u2").reshape(n, -1)
        for j, (p, _) in enumerate(rports):
            served[p] = tables[p][refs[:, j]]               # the instances' rows, for the capture comparison and M0's input
    else:
        rw = sum(w for _, w in rports)
        rows_all = priv[:n * rw * 2].view("<u2").reshape(n, rw)
        ys = priv[n * rw * 2:].reshape(n, len(rports), SR.SALT_BYTES)
        outs_all = pub[n * len(rports) * SR.BC_BYTES:].view("<u2").reshape(n, -1)
        for p, w in rports:
            served[p] = rows_all[:, off:off + w]; off += w
    off = 0
    for p, w in oports:
        served[p] = outs_all[:, off:off + w]; off += w
    mr = {"k": k, "template": mem["template"], "n": n}
    if mode == "served":                                       # the served rows at the captured instances equal the capture
        rows_idx = idx["members"][k]["rows"]
        key = {(e[2], int(e[3]), e[5], int(e[7])): (int(e[0]) - int(mem["base"]), int(e[1]) - int(e[0])) for e in rows_idx}
        cidx = json.loads((Path(s.path) / "index.json").read_text())
        col = {c: i for i, c in enumerate(cidx["columns"])}
        units, cap_i, outside = [], [], 0
        for i, r in enumerate(cidx["rows"]):
            kk = (r[col["request"]], int(r[col["engine_step"]]), r[col["op_path"]], int(r[col["row"]]))
            if kk not in key:
                outside += 1
                continue
            lo, nh = key[kk]
            units.append(lo + int((r[col["sub"]] or {}).get("head", 0)) if nh > 1 else lo)
            cap_i.append(i)
        cap = cols(s, list(served))
        eq = {p: bool(np.array_equal(served[p][units], cap[p][cap_i])) for p in served} if units else {}
        mr["captured"] = {"in_population": len(units), "outside_scope": outside, "equal": eq, "ok": bool(units) and all(eq.values())}
        ok &= mr["captured"]["ok"]
    low = C.lowering_for_set(s)
    text = C.compose(low, s.subcircuit, partition=part["partition_digest"], program=part["partition"]["program"])
    mr["pin"], mr["class"] = C.digest(text), C.class_digest(text)
    mine = SR.flock_input_files(wd, k, text, out / "serving", s.subcircuit.id)

    class Served:
        name, content_digest, subcircuit, n = f"served/{rec['commitment']['source']['run']}/m{k}", win["index_sha512"], s.subcircuit, n
        def port(self, p, lo, hi):
            return served[p][lo:hi]
    bind = mem["frame_v3"]["bindings"]
    orig = ID.identity_digest
    ID.identity_digest = lambda tag, doc: bind[doc["port"]] if "port" in doc and doc["port"] in bind and "set" in doc else orig(tag, doc)
    if shared:
        C.stage_salts = lambda input_set, lo, hi, ports, key_, tables_=None: tsalts
    else:
        C.stage_salts = lambda input_set, lo, hi, ports, key_, tables_=None: {p: [bytes(ys[i, j]) for i in range(n)] for j, (p, _) in enumerate(rports)}
    (out / "m0").mkdir(exist_ok=True)
    t = time.perf_counter()
    kw = {"indices": list(range(int(mem["base"]), int(mem["base"]) + n))}
    if shared:
        kw.update(share_rows=True, rows={p: served[p] for p, _ in rports}, outs={p: served[p] for p, _ in oports})
        if os.environ.get("M0_TABLES"):                     # M0's no-dedupe mode: the tables and refs as served
            kw.update(tables=tables, refs={p: refs[:, j] for j, (p, _) in enumerate(rports)})
    C.write(text, Served(), 0, n, out / "m0" / f"m{k}-inst-{n}.bin", out / "m0" / f"m{k}-pub-{n}.bin", **kw)
    mr["m0_write_s"] = round(time.perf_counter() - t, 3)
    ID.identity_digest = orig
    for kind in ("pub", "inst"):
        a, b = Path(mine[kind]).read_bytes(), (out / "m0" / f"m{k}-{kind}-{n}.bin").read_bytes()
        ha, hb = json.loads(a.split(b"\n", 1)[0]), json.loads(b.split(b"\n", 1)[0])
        mr[kind] = {"file_equal": a == b, "header_fields_differing": sorted(x for x in set(ha) | set(hb) if ha.get(x) != hb.get(x)),
                    "file_sha512": hashlib.sha512(a).hexdigest(), "bytes": len(a)}
        ok &= a == b
    res["members"].append(mr)
    print(json.dumps({x: mr[x] for x in mr if x not in ("class",)}), flush=True)
res["ok"] = ok
(out / "members.json").write_text(json.dumps(res, indent=1) + "\n")
print("SC-MEMBERS", "OK" if ok else "FAIL")
