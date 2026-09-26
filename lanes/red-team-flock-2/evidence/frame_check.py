#!/usr/bin/env python3
"""red-team-flock-2: a cell's verifier-staged flock-ir-frame/v2 statement (its instance file and netlist) checked against the
IR, independently of the Rust verifier's structural checks:
- the netlist is the reviewed frame lowering (sha, text);
- every unit slot's wiring reads, for each leaf port, exactly the row element the IR's leaf map names (in_src) from a run of
  its own instance, and out_leaf is the IR's output leaf map (out_src);
- the block table holds every run of every row chunk and every unit exactly once;
- the row digests are keyed BLAKE3 (x-row key) of the rows, and the frame-v3 roots (my own frame-v3 hashing) of the digests
  and of the units' output words are the header's.

  frame_check.py TEMPLATE INSTANCE_FILE NETLIST
"""
import hashlib, json, sys

from verity.commitments import blake3 as B3
from verity.commitments.rowleaf import ROLE_X, blake3_row_key

FRAME = b"veritor/protocol/merkle/frame/v3\0"
PARAMS = {"rope-head": {"D": 64}, "silu-mul": {"I": 8192}, "rmsnorm-fused-cuda": {"N": 2048, "EPS": 1e-5}, "rmsnorm-triton": {"N": 2048, "EPS": 1e-5}}


def fv3(tag, parts):
    h = hashlib.sha256(FRAME + len(tag).to_bytes(4, "big") + tag)
    for p in parts:
        h.update(len(p).to_bytes(8, "big")); h.update(p)
    return h.digest()


def uint(x):
    b = x.to_bytes(8, "big")
    z = next((i for i, c in enumerate(b) if c), 7)
    return b[z:]


def root(dom, leaves):
    n = len(leaves); w = 1 << max(0, (n - 1).bit_length())
    level = list(leaves) + [fv3(b"pad", [dom, uint(r)]) for r in range(n, w)]
    d = 0
    while len(level) > 1:
        level = [fv3(b"node", [dom, uint(d), uint(i), level[2 * i], level[2 * i + 1]]) for i in range(len(level) // 2)]
        d += 1
    return level[0]


def main():
    tpl, ipath, npath = sys.argv[1:4]
    from verity_numerical.bench import templates as TM
    import importlib
    mod = importlib.import_module("verity_flock.templates." + tpl.replace("-", "_"))
    low = mod.frame_lowering(TM.subcircuit(tpl, **PARAMS[tpl]))
    text = open(npath).read()
    sha = hashlib.sha256(text.encode()).hexdigest()
    print("NETLIST", tpl, sha[:16], "== reviewed frame lowering:", text == low.text)
    b = open(ipath, "rb").read(); nl = b.index(b"\n"); h = json.loads(b[:nl])
    assert h["unit_sha256"] == sha
    L, U = h["layout"], low.units
    n, upi, nb, chunk_nb = h["instances"], h["units_per_instance"], L["nb"], L["chunk_nb"]
    widths = [w for _, w in h["in_ports"]]
    starts = [sum(widths[:p]) for p in range(len(widths))]
    runs = chunk_nb // nb
    nleaf = len(L["leaf_cols"])
    bad, seen_runs, seen_units = [], set(), set()
    for bi, (chunks, units) in enumerate(h["blocks"]):
        for c in chunks:
            if c is not None:
                seen_runs.add(tuple(c))
        for u, g in enumerate(units):
            if g is None:
                continue
            seen_units.add(g)
            i, lu = g // upi, g % upi
            for j, (q, off) in enumerate(L["wiring"][u]):
                ci, p, c, r = chunks[q]
                byte = 1024 * c + 64 * r * nb + off
                leaf = starts[p] + byte // 2
                want = U.in_src[lu][j]
                if ci != i or want != ("leaf", leaf):
                    bad.append((bi, u, g, j, (ci, p, c, r, off), want))
            if [p for k, p in U.out_src[lu] if k == "ret"] != L["out_leaf"][lu]:
                bad.append((bi, u, g, "out_leaf"))
    want_runs = {(i, p, c, r) for i in range(n) for p in range(len(widths)) for c in range((2 * widths[p] + 1023) // 1024) for r in range(runs)}
    print(f"LAYOUT {tpl}: {len(h['blocks'])} blocks, {len(seen_units)} of {h['units']} units, {len(seen_runs)} of {len(want_runs)} runs "
          f"(equal: {seen_runs == want_runs}); wiring / out_leaf differences from the IR's leaf map: {len(bad)} {bad[:3]}")
    assert all(len(w) == nleaf for w in L["wiring"])
    row_bytes = sum(2 * w for w in widths)
    rows = b[nl + 1:nl + 1 + n * row_bytes]
    at = nl + 1 + n * row_bytes
    digs = b[at:at + 32 * n * len(widths)]; at += 32 * n * len(widths)
    rw = L["ret_group"][1]
    outs = b[at:at + 16 * h["units"] * rw]
    key = blake3_row_key(ROLE_X)
    fv = h["frame_v3"]
    ok_d = ok_r = True
    for p, (name, w) in enumerate(h["in_ports"]):
        mine = []
        for i in range(n):
            off = i * row_bytes + 2 * starts[p]
            d = B3.keyed(key, rows[off:off + 2 * w])
            ok_d &= d == digs[32 * (i * len(widths) + p):32 * (i * len(widths) + p) + 32]
            mine.append(d)
        dom = bytes.fromhex(fv["domain_ids"][name])
        leaves = [fv3(b"leaf", [dom, uint(i), uint(i), fv["schemas"][name].encode(), mine[i]]) for i in range(n)]
        ok_r &= root(dom, leaves).hex() == fv["roots"][name]
    ow = [w for _, w in h["out_ports"]]; ost = [sum(ow[:p]) for p in range(len(ow))]
    vals = [[None] * (n * w) for w in ow]
    for g in range(h["units"]):
        i, lu = g // upi, g % upi
        word = outs[16 * g * rw:16 * (g + 1) * rw]
        for j, leaf in enumerate(L["out_leaf"][lu]):
            c = L["ret_cols"][j]
            v = int.from_bytes(word[c // 8:c // 8 + 3], "little") >> (c % 8) & 0xFFFF
            p = max(k for k in range(len(ow)) if ost[k] <= leaf)
            assert vals[p][i * ow[p] + leaf - ost[p]] is None
            vals[p][i * ow[p] + leaf - ost[p]] = v
    for p, (name, w) in enumerate(h["out_ports"]):
        dom = bytes.fromhex(fv["domain_ids"][name])
        leaves = [fv3(b"leaf", [dom, uint(r), uint(r), b"u16", v.to_bytes(2, "big")]) for r, v in enumerate(vals[p])]
        ok_r &= root(dom, leaves).hex() == fv["roots"][name]
    print(f"COMMIT {tpl}: row digests = keyed BLAKE3 (x key) of the rows: {ok_d}; frame-v3 roots (rows and outputs) = header's: {ok_r}; "
          f"key = blake3_row_key(ROLE_X): {fv['key'] == key.hex()}")


if __name__ == "__main__":
    main()
