#!/usr/bin/env python3
"""red-team-flock-2: an independent `flock-ir-instances/v1` writer for the rope-head / silu-mul units: adversarial unit inputs
(diff_ir_units.py's families), outputs from the IR primitives (verity_vllm RopeOut / RopeOutAdd / SiluMulBf16), my own
packing (port j's bits consecutive from bit sum(widths[:j]), 128-bit little-endian words).

  gen_ir_inst.py rope|silu NETLIST UNITS OUT [seed] [--header k=v ...]   (a header override, e.g. unit_sha256=..., in_words=2)
"""
import hashlib, json, random, sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import diff_ir_units as D


def main():
    which, net, units, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    rest = sys.argv[5:]
    seed = int(rest[0]) if rest and "=" not in rest[0] else 20260926
    over = dict(a.split("=", 1) for a in rest if "=" in a)
    from verity_vllm.program.registry import prims as P
    text = open(net).read()
    h = text.splitlines()[0].split()
    rng = random.Random(seed)
    ins, outs = [], []
    for _ in range(units):
        if which == "rope":
            x, y, c, s = D.rope_case(rng)
            ins.append(x | (y << 16) | (c << 32) | (s << 48))
            outs.append(P.RopeOut.evaluate(x, y, c, s) | (P.RopeOutAdd.evaluate(x, y, c, s) << 16))
        else:
            g, u = D.silu_case(rng)
            ins.append(g | (u << 16))
            outs.append(P.SiluMulBf16.evaluate(g, u))
    upi = 32 if which == "rope" else 8192
    if units % upi:
        upi = 1                                     # a unit relation, not whole template instances
    head = {"format": "flock-ir-instances/v1", "unit": h[1], "unit_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "instances": units // upi, "units_per_instance": upi, "units": units, "in_words": 1,
            "in_bits": [16, 16, 16, 16] if which == "rope" else [16, 16], "out_words": 1,
            "out_bits": [16, 16] if which == "rope" else [16], "cut_words": 0, "set": "red-team-flock-2/gen_ir_inst",
            "subcircuit": "rope-head" if which == "rope" else "silu-mul", "range": [0, units], "seed": seed}
    for k, v in over.items():
        head[k] = int(v) if v.isdigit() else v
    w = lambda v: v.to_bytes(8, "little") + (0).to_bytes(8, "little")
    with open(out, "wb") as f:
        f.write(json.dumps(head, sort_keys=True).encode() + b"\n")
        f.write(b"".join(w(v) for v in ins))
        f.write(b"".join(w(v) for v in outs))
    print(json.dumps({"out": out, "units": units, "unit": h[1], "override": over}))


if __name__ == "__main__":
    main()
