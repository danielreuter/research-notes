#!/usr/bin/env python3
"""red-team-flock-2: IR6 tampers of a staged flock-ir-frame/v2 file (2f55d2d3) and its netlist, beyond the producer's four.
Each keeps the block table and the frame-v3 roots valid, so only the pinned leaf maps can refuse it:

- wiring_neighbour: unit slot 0's first leaf port reads the next leaf of the same run (offset + 2)
- wiring_other_run: unit slot 0's first leaf port reads the same offset of another run slot
- units_across_blocks: the unit in slot 0 of block 0 and of the next block of the same instance swapped
- out_leaf_units_swapped: units 0 and 1's output maps swapped with their returned words (instance outputs, roots unchanged)
- netlist_no_leaves: the c53d9148 netlist form (no LEAVES line), header naming it
- leaves_consistent: LEAVES edited to swap every unit's leaf ports 0 and 1, the header's wiring swapped to match and naming
  that netlist: accepted without a pin, refused under the verifier's (the meaning is the pin's)

  ir6_tamper.py STAGED_FILE NETLIST OUTDIR
"""
import copy, hashlib, json, sys


def main():
    src, netp, out = sys.argv[1:4]
    b = open(src, "rb").read(); nl = b.index(b"\n"); h = json.loads(b[:nl]); body = bytearray(b[nl + 1:])
    assert json.dumps(h, sort_keys=True).encode() == b[:nl], "the header does not round-trip"
    L = h["layout"]; n, upi = h["instances"], h["units_per_instance"]
    run_bytes = 64 * L["nb"]

    def save(name, hh, bb=None, net=None):
        if net is not None:
            open(f"{out}/n-{name}.txt", "w").write(net)
            hh["unit_sha256"] = hashlib.sha256(net.encode()).hexdigest()
        with open(f"{out}/f-{name}.bin", "wb") as f:
            f.write(json.dumps(hh, sort_keys=True).encode() + b"\n"); f.write(bytes(body if bb is None else bb))
        print("WROTE", name, "netlist" if net is not None else "")

    t = copy.deepcopy(h); w = t["layout"]["wiring"][0][0]
    w[1] = w[1] + 2 if w[1] + 2 < run_bytes else w[1] - 2
    save("wiring_neighbour", t)
    t = copy.deepcopy(h); w = t["layout"]["wiring"][0][0]
    real = [q for q, c in enumerate(h["blocks"][0][0]) if c is not None]
    others = [q for q in real if q != w[0]]
    if others:
        w[0] = others[0]; save("wiring_other_run", t)
    t = copy.deepcopy(h); B = t["blocks"]
    g0 = B[0][1][0]
    b1 = next((k for k in range(1, len(B)) if B[k][1][0] is not None and B[k][1][0] // upi == g0 // upi and B[k][1][0] != g0), None)
    if b1 is not None:
        B[0][1][0], B[b1][1][0] = B[b1][1][0], g0; save("units_across_blocks", t)
    if upi >= 2 and L["out_leaf"][0] and L["out_leaf"][1]:
        t = copy.deepcopy(h); t["layout"]["out_leaf"][0], t["layout"]["out_leaf"][1] = h["layout"]["out_leaf"][1], h["layout"]["out_leaf"][0]
        row_bytes = sum(2 * w for _, w in h["in_ports"])
        at = n * row_bytes + 32 * n * len(h["in_ports"])
        rw = L["ret_group"][1]; sz = 16 * rw
        bb = bytearray(body)
        for i in range(n):
            u0, u1 = at + (i * upi) * sz, at + (i * upi + 1) * sz
            bb[u0:u0 + sz], bb[u1:u1 + sz] = body[u1:u1 + sz], body[u0:u0 + sz]
        save("out_leaf_units_swapped", t, bb)
    text = open(netp).read(); lines = text.splitlines()
    save("netlist_no_leaves", copy.deepcopy(h), net="\n".join(l for l in lines if not l.startswith("LEAVES ")) + "\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("LEAVES "))
    lv = json.loads(lines[i][7:])
    if all(len(x) >= 2 for x in lv["in"]):
        lv2 = copy.deepcopy(lv)
        for x in lv2["in"]:
            x[0], x[1] = x[1], x[0]
        lines2 = list(lines); lines2[i] = "LEAVES " + json.dumps(lv2, sort_keys=True, separators=(",", ":"))
        t = copy.deepcopy(h)
        for w in t["layout"]["wiring"]:
            w[0], w[1] = w[1], w[0]
        save("leaves_consistent", t, net="\n".join(lines2) + "\n")
    # the 16-bit assertions: a pinned port that is not [n, 16], and a returned-output port that is not 16 bits
    for side in ("out_ports", "in_ports"):
        lv2 = copy.deepcopy(lv); lv2[side][0][1] = 32
        lines2 = list(lines); lines2[i] = "LEAVES " + json.dumps(lv2, sort_keys=True, separators=(",", ":"))
        save(f"leaves_{side[:-1]}_32", copy.deepcopy(h), net="\n".join(lines2) + "\n")
    tok = lines[0].split()
    at = 4
    for _ in range(int(tok[at])):                  # skip the input groups
        at += 3 + int(tok[at + 3])
    at += 1                                         # the output group count; group 0 is the returned outputs
    col, words, nports = int(tok[at + 1]), int(tok[at + 2]), int(tok[at + 3])
    bits = [int(x) for x in tok[at + 4:at + 4 + nports]]
    if sum(bits) + 16 <= 128 * words:               # room in the group: its first port widened to 32 bits
        tok[at + 4] = str(bits[0] + 16)
    elif nports >= 2:                                # a full group: its first two ports merged into one 32-bit port
        tok = tok[:at + 3] + [str(nports - 1), str(bits[0] + bits[1])] + tok[at + 6:]
    save("ret_port_32", copy.deepcopy(h), net="\n".join([" ".join(tok)] + lines[1:]) + "\n")
    t = copy.deepcopy(h)
    if len(t["layout"]["ret_cols"]) >= 2:
        t["layout"]["ret_cols"][0], t["layout"]["ret_cols"][1] = t["layout"]["ret_cols"][1], t["layout"]["ret_cols"][0]
        save("ret_cols_swapped", t)


if __name__ == "__main__":
    main()
