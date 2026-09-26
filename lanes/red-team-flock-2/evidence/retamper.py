#!/usr/bin/env python3
"""red-team-flock-2: rewrite a `flock-pure-instances/v1` file's output words or y-leaf encoding and recompute the y root
(domain rebuilt from the header's binding and owner, and checked against its domain id), for the NV1 re-review.

  retamper.py IN OUT MODE
  MODE: consistent_y_plus1  y[0] += 1 and out[0] = the word it opens (fp8: y << 10): admitted; the proof must fail
        out_lowbit          out[0] ^= 1, y kept (fp8: out is no longer y << 10): NV1 must refuse
        y_unpacked          y[0] = out[0] (fp8 committed as the raw FP32 word): NV1 must refuse
        y_u16               y leaves "u16" / 2 bytes (the low 16 bits of y) under an unchanged check: G4
        y_u32_highbits      y leaves "u32" / 4 bytes, y[0] = out[0] = old | 0x10000 (a bf16 output committed as 32 bits): G4
"""
import json, sys

from verity.commitments.indexed import RangeIndexedDomain
from verity.commitments.merkle import CommitmentDomain, tree_levels


def main(src, dst, mode):
    b = open(src, "rb").read()
    nl = b.index(b"\n")
    h = json.loads(b[:nl])
    n, rb, units = h["vus"], h["row_bytes"], h["units"]
    at = nl + 1
    x, w = b[at:at + n * rb], b[at + n * rb:at + 2 * n * rb]
    at += 2 * n * rb
    accs = b[at:at + n * units * 4]
    at += n * units * 4
    out = [int.from_bytes(b[at + 4 * i:at + 4 * i + 4], "little") for i in range(n)]
    at += 4 * n
    y = [int.from_bytes(b[at + 4 * i:at + 4 * i + 4], "little") for i in range(n)]
    assert at + 4 * n == len(b)
    fp8 = h["relation"].startswith("fp8-")
    if mode == "consistent_y_plus1":
        y[0] += 1
        out[0] = y[0] << 10 if fp8 else y[0]
    elif mode == "out_lowbit":
        out[0] ^= 1
    elif mode == "y_unpacked":
        y[0] = out[0]
    elif mode == "y_u16":
        h["schemas"]["y"], h["y_bytes"] = "u16", 2
    elif mode == "y_u32_highbits":
        h["schemas"]["y"], h["y_bytes"] = "u32", 4
        y[0] |= 0x10000
        out[0] = y[0]
    else:
        sys.exit(f"unknown mode {mode}")
    dom = CommitmentDomain(bytes.fromhex(h["bindings"]["y"]), h["owners"]["y"], RangeIndexedDomain(0, n))
    assert dom.domain_id.hex() == h["domain_ids"]["y"], "the header's y domain is not its binding and owner"
    nb = h["y_bytes"]
    leaves = [dom.leaf(r, r, h["schemas"]["y"], (y[r] & ((1 << (8 * nb)) - 1)).to_bytes(nb, "big")) for r in range(n)]
    old = h["roots"]["y"]
    h["roots"]["y"] = tree_levels(dom, leaves)[-1][0].hex()
    h["instances"] = dict(h["instances"], retamper=mode)
    le = lambda ws: b"".join(v.to_bytes(4, "little") for v in ws)
    with open(dst, "wb") as f:
        f.write(json.dumps(h, sort_keys=True).encode() + b"\n")
        f.write(x); f.write(w); f.write(accs); f.write(le(out)); f.write(le(y))
    print(json.dumps({"out": dst, "mode": mode, "out0": f"{out[0]:08x}", "y0": f"{y[0]:x}", "y_schema": h["schemas"]["y"],
                      "y_bytes": nb, "y_root_changed": old != h["roots"]["y"]}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
