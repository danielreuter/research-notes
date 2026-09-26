#!/usr/bin/env python3
"""red-team-flock-2: tampered copies of a staged flock-ir-frame/v2 instance file (the verifier's own file edited), for the load
checks (check_roots, check_blocks, FrameStmt::new, cut_map_of) and two that are structurally valid, documenting that the
Rust verifier validates the layout's shape, not its meaning (a swapped leaf wiring, a different row key).

  frame_tamper.py STAGED_FILE OUTDIR
"""
import copy, json, sys


def main():
    src, out = sys.argv[1:3]
    b = open(src, "rb").read(); nl = b.index(b"\n"); h = json.loads(b[:nl]); body = bytearray(b[nl + 1:])
    n, widths = h["instances"], [w for _, w in h["in_ports"]]
    row_bytes = sum(2 * w for w in widths)

    def save(name, hh, bb=None):
        with open(f"{out}/f-{name}.bin", "wb") as f:
            f.write(json.dumps(hh, sort_keys=True).encode() + b"\n"); f.write(bytes(body if bb is None else bb))
        print("WROTE", name)
    t = copy.deepcopy(h)
    bb = bytearray(body); bb[n * row_bytes] ^= 1; save("digest_byte", t, bb)                 # first row digest
    t = copy.deepcopy(h); t["blocks"][0][0][1] = t["blocks"][0][0][0]; save("dup_run", t)
    t = copy.deepcopy(h); t["layout"]["out_leaf"][1] = t["layout"]["out_leaf"][0]; save("out_leaf_dup", t)
    t = copy.deepcopy(h); p0 = h["in_ports"][0][0]; t["frame_v3"]["schemas"][p0] = "blake3-keyed/row-nvfp4/v1"; save("schema_changed", t)
    t = copy.deepcopy(h); t["layout"]["wiring"][0][0][1] += 1; save("wiring_odd", t)
    t = copy.deepcopy(h); t["cut"] = {"words": h.get("cut_words", 0)}; save("header_cut", t)
    t = copy.deepcopy(h); t["cut_words"] = h.get("cut_words", 0) + 1; save("cut_words_plus1", t)
    t = copy.deepcopy(h); w = t["layout"]["wiring"][0]; w[0], w[1] = w[1], w[0]; save("wiring_swap", t)
    t = copy.deepcopy(h); k = bytearray(bytes.fromhex(h["frame_v3"]["key"])); k[0] ^= 1; t["frame_v3"]["key"] = k.hex(); save("key_changed", t)


if __name__ == "__main__":
    main()
