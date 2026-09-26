#!/usr/bin/env python3
"""red-team-flock-3: tampered copies of a staged flock-ir-frame/v3 attention file (the verifier's own file edited), for the
verifier's load checks (check_blocks, check_roots, check_leaf_maps, check_public_ports, check_cut_words) run by the real binary
(`flock-ir-frame loadcheck`, exit 2 = REFUSED), and two consistent restatements that pass load and must be refused by the proof
(`selftest --only honest`). Also re-derives the header's frame-v3 roots with my own frame-v3 code (a check of the file).

  frame_tamper3.py STAGED_FILE NETLIST OUTDIR
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import blake3
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402

FRAME = b"veritor/protocol/merkle/frame/v3\0"


def fv3(tag, parts):
    h = hashlib.sha256(FRAME + len(tag).to_bytes(4, "big") + tag)
    for p in parts:
        h.update(len(p).to_bytes(8, "big")); h.update(p)
    return h.digest()


def uint(x):
    b = x.to_bytes(8, "big")
    return b.lstrip(b"\0") or b"\0"


def fv3_root(dom, leaves):
    n = len(leaves); w = 1 << (n - 1).bit_length() if n > 1 else 1
    lvl = leaves + [fv3(b"pad", [dom, uint(r)]) for r in range(n, w)]
    d = 0
    while len(lvl) > 1:
        lvl = [fv3(b"node", [dom, uint(d), uint(i), lvl[2 * i], lvl[2 * i + 1]]) for i in range(len(lvl) // 2)]
        d += 1
    return lvl[0]


class File:
    def __init__(self, path):
        b = open(path, "rb").read(); nl = b.index(b"\n")
        self.h = json.loads(b[:nl]); body = b[nl + 1:]
        h = self.h
        self.n, ports = h["instances"], h["in_ports"]
        self.rb = sum(2 * w for _, w in ports)
        self.np_ = len(ports)
        at = 0
        self.rows = bytearray(body[at:at + self.n * self.rb]); at += self.n * self.rb
        self.dig = bytearray(body[at:at + 32 * self.n * self.np_]); at += 32 * self.n * self.np_
        assert h["outputs"] == "tail"
        self.ow = sum(w for _, w in h["out_ports"])
        self.outs = np.frombuffer(body[at:at + 2 * self.n * self.ow], dtype="<u2").astype(np.uint64).copy(); at += 2 * self.n * self.ow
        self.kc = h["cut_words"]
        self.cuts = np.frombuffer(body[at:at + 4 * self.n * self.kc], dtype="<u4").astype(np.uint64).copy(); at += 4 * self.n * self.kc
        assert at == len(body)

    def digest(self, i, p):
        return bytes(self.dig[32 * (i * self.np_ + p):32 * (i * self.np_ + p + 1)])

    def roots(self):
        fv = self.h["frame_v3"]; out = {}
        for p, (name, _) in enumerate(self.h["in_ports"]):
            dom = bytes.fromhex(fv["domain_ids"][name])
            out[name] = fv3_root(dom, [fv3(b"leaf", [dom, uint(i), uint(i), fv["schemas"][name].encode(), self.digest(i, p)]) for i in range(self.n)]).hex()
        (name, w), = self.h["out_ports"]
        dom = bytes.fromhex(fv["domain_ids"][name])
        out[name] = fv3_root(dom, [fv3(b"leaf", [dom, uint(r), uint(r), b"u16", int(v).to_bytes(2, "big")]) for r, v in enumerate(self.outs)]).hex()
        return out

    def save(self, path, h=None):
        h = self.h if h is None else h
        with open(path, "wb") as f:
            f.write(json.dumps(h, sort_keys=True).encode() + b"\n")
            f.write(bytes(self.rows)); f.write(bytes(self.dig))
            f.write(self.outs.astype("<u2").tobytes()); f.write(self.cuts.astype("<u4").tobytes())


def retail(f, net, forged):
    """Every tail-computed cut word and output recomputed by the IR's primitives from the file's unit outputs and public words
    (after `forged(f)` edits some of them)."""
    import attn_e2e as E
    s = E.Solver(net)
    forged(f)
    produced = {k for u in s.unit_out for _, k in u} | {k for k, _ in s.public}
    for i in range(f.n):
        slots = {k: int(f.cuts[i * f.kc + k]) for k in produced}
        for op in s.tail:
            out, pid, args = op[0], op[1], op[2:]
            slots[out] = (args[0] & 0xFFFFFFFF) if pid == "Const" else s.fns[pid](*[slots[a] for a in args]) & 0xFFFFFFFF
        for k in range(f.kc):
            f.cuts[i * f.kc + k] = slots[k]
        for l, sl in enumerate(s.outputs):
            f.outs[i * f.ow + l] = slots[sl]
    f.h["frame_v3"]["roots"]["out"] = f.roots()["out"]


def main():
    src, netp, out = sys.argv[1:4]
    Path(out).mkdir(parents=True, exist_ok=True)
    net = NL.Net(open(netp).read())
    f0 = File(src)
    r = f0.roots()
    print("ROOTS", json.dumps({k: r[k] == f0.h["frame_v3"]["roots"][k] for k in r}))
    assert all(r[k] == f0.h["frame_v3"]["roots"][k] for k in r), "my frame-v3 roots differ from the header's"
    # my own check of the public port: q's words (public cut words) hash under the x-row key to q's committed digest
    key = bytes.fromhex(f0.h["frame_v3"]["key"])
    pub = net.cut["public"]
    for i in range(f0.n):
        qb = b"".join(int(f0.cuts[i * f0.kc + k]).to_bytes(2, "little") for k, _ in sorted(pub, key=lambda x: x[1]))
        assert blake3.blake3(qb, key=key).digest() == f0.digest(i, 0), f"instance {i}: q words vs digest"
        for p in (1, 2):
            row = bytes(f0.rows[i * f0.rb + 128 + (p - 1) * (f0.rb - 128) // 2: i * f0.rb + 128 + p * (f0.rb - 128) // 2])
            assert blake3.blake3(row, key=key).digest() == f0.digest(i, p), f"instance {i} port {p}: row vs digest"
    print("DIGESTS q (from its public words), k, v (from the rows): all match, keyed BLAKE3 under the x-row key")
    kq0 = sorted(pub, key=lambda x: x[1])[0][0]
    lay, blocks = f0.h["layout"], f0.h["blocks"]
    tail_by = {}
    for op in net.cut["tail"]:
        if op[0] < f0.kc:
            tail_by.setdefault(op[1], op[0])
    unit_outs = [u[0][1] for u in net.cut["out"]]

    def case(name, edit_h=None, edit_f=None):
        f = File(src)
        h = copy.deepcopy(f.h)
        if edit_h:
            edit_h(h)
        if edit_f:
            edit_f(f)
        f.save(f"{out}/f-{name}.bin", h)
        print("WROTE", name)

    case("public_ports_dropped", lambda h: h.__setitem__("public_ports", []))
    case("public_ports_plus_k", lambda h: h.__setitem__("public_ports", [0, 1]))
    case("q_word_flipped", edit_f=lambda f: f.cuts.__setitem__(kq0, f.cuts[kq0] ^ 1))
    case("q_word_high_bit", edit_f=lambda f: f.cuts.__setitem__(kq0, f.cuts[kq0] | (1 << 16)))
    case("q_digest_byte", edit_f=lambda f: f.dig.__setitem__(0, f.dig[0] ^ 1))
    # the partial (masked) 16-key group: a block with empty run slots; a P.V slot's zero leaf rewired to a real run, and a real
    # leaf of every P.V slot to an empty run
    pb = next(b for b, bl in enumerate(blocks) if any(c is None for c in bl[0][:32]) and any(u is not None for u in bl[1]))
    empty_q = next(q for q, c in enumerate(blocks[pb][0][:32]) if c is None)
    real_q = next(q for q, c in enumerate(blocks[pb][0][:32]) if c is not None)

    def zero_to_real(h):
        w = h["layout"]["wiring"][64]
        j = next(j for j, (q, _) in enumerate(w) if h["blocks"][pb][0][q] is None)
        w[j] = [16, w[j][1]]
    case("zero_leaf_to_real_run", zero_to_real)
    case("real_leaf_to_empty_run", lambda h: h["layout"]["wiring"][64].__setitem__(0, [empty_q, h["layout"]["wiring"][64][0][1]]))
    # the block table: a run of a short last chunk dropped; a real run duplicated into an empty slot; a hole given a unit
    sb = next(b for b, bl in enumerate(blocks) if any(c is not None and c[1] == 1 and c[2] == (2 * f0.h["in_ports"][1][1]) // 1024
                                                      for c in bl[0]))
    sq = next(q for q, c in enumerate(blocks[sb][0]) if c is not None and c[1] == 1 and c[2] == (2 * f0.h["in_ports"][1][1]) // 1024)
    case("short_chunk_run_dropped", lambda h: h["blocks"][sb][0].__setitem__(sq, None))
    case("real_run_in_empty_slot", lambda h: h["blocks"][pb][0].__setitem__(empty_q, h["blocks"][pb][0][real_q]))
    hole = next(u for u, g in enumerate(blocks[pb][1]) if g is None)
    case("hole_given_a_unit", lambda h: h["blocks"][pb][1].__setitem__(hole, h["blocks"][pb][1][next(u for u, g in enumerate(blocks[pb][1]) if g is not None)]))
    case("t_plus_one_ports", lambda h: h.__setitem__("in_ports", [[p, w + (64 if p != "q" else 0)] for p, w in h["in_ports"]]))
    # tail-computed words in the file, one per kind (the P.V accumulators' zero, a P word, a rescaled O), and a forged output
    # with the output root recomputed (so check_roots passes and only the tail refuses it)
    for pid, k in sorted(tail_by.items()):
        case(f"tail_word_{pid.split('_')[0]}", edit_f=lambda f, k=k: f.cuts.__setitem__(k, f.cuts[k] ^ (1 << 4)))

    def out_forged(f):
        f.outs[3] ^= 1
        f.h["frame_v3"]["roots"]["out"] = f.roots()["out"]
    f = File(src); out_forged(f); f.save(f"{out}/f-outputs_forged_root_recomputed.bin"); print("WROTE outputs_forged_root_recomputed")
    # consistent restatements (pass load; the proof must refuse): a unit output forged with the tail and outputs recomputed from it
    # (the last P.V step of the first visited block: it feeds the rescale); q forged with its digest and root recomputed
    uo = set(unit_outs)
    k_pv = next(op[2] for op in net.cut["tail"] if op[1] == "F32MulFtz_v1" and op[0] < f0.kc and op[2] in uo)
    f = File(src); retail(f, net, lambda f: f.cuts.__setitem__(k_pv, f.cuts[k_pv] ^ (1 << 12))); f.save(f"{out}/r-unit_output_retailed.bin")
    print("WROTE r-unit_output_retailed (a P.V unit output the tail rescales: cut word", k_pv, ")")
    if len(sys.argv) > 4:   # the same file relabelled for another T's netlist (its unit name and pin)
        other = NL.Net(open(sys.argv[4]).read())
        case("relabelled_other_T", lambda h: (h.__setitem__("unit", other.name), h.__setitem__("unit_sha256", other.sha256)))

    def q_restated(f):
        f.cuts[kq0] ^= 1 << 2
        qb = b"".join(int(f.cuts[k]).to_bytes(2, "little") for k, _ in sorted(pub, key=lambda x: x[1]))
        f.dig[0:32] = blake3.blake3(qb, key=key).digest()
        f.h["frame_v3"]["roots"]["q"] = f.roots()["q"]
    f = File(src); q_restated(f); f.save(f"{out}/r-q_restated.bin"); print("WROTE r-q_restated")


if __name__ == "__main__":
    main()
