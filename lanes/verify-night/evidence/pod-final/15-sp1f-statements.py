"""verify-night: write the SP1 relation-bare/v2 statements of the four sp1-formats rows from MY tree's frozen sets.

    cd /workspace/src && python 15-sp1f-statements.py OUTDIR [FORMAT...]

y per VU from the canonical Ligero recipe loaders of lane/verify-night @ 1b3c7be6 (relchain.instances of the target's frozen
relation, instance_equiv.frozen_relation; fp4.chain.instances_fp4 for NVFP4), no cache: y_final = the last FP32 accumulator
word; bf16-hopper publishes the BF16 cast rel.y_public(y_final) (2 bytes), the others the FP32 word (4 bytes). identity =
FROZEN_INSTANCES[target]. Then compare: the dumped proofs/statement.bin (OUTDIR/<fmt>/proofs/, fetched beforehand) and the
producer's instance file's y (OUTDIR/inst/<fmt>.bin; its header's `instances` against FROZEN_INSTANCES too).
Writes OUTDIR/<fmt>.mine.bin, OUTDIR/<fmt>.neg.bin (last y byte flipped), OUTDIR/statements.json."""
import hashlib
import json
import os
import struct
import sys
from pathlib import Path

import numpy as np

from backends.direct.ligero import relchain
from verity_numerical.bench.instance_equiv import frozen_relation
from verity_numerical.bench.tables import FROZEN_INSTANCES

N, K = 4096, 1536
PROCS = int(os.environ.get("VY_CPU_THREADS", os.cpu_count() or 1))
FORMATS = {  # format -> (format id, target, y bytes)
    "bf16-hopper": (2, "bf16-hopper-mma-draft/2026-09-22", 2),
    "fp8-hopper": (3, "fp8-hopper-wgmma-draft/2026-09-22", 4),
    "fp8-ada": (4, "fp8-ada-mma-draft/2026-09-22", 4),
    "fp4-nvf4": (5, "nvfp4-sm120-mma-draft/2026-09-22", 4),
}


def y_words(fmt, target, yb):
    if fmt == "fp4-nvf4":
        from backends.direct.ligero.fp4.chain import instances_fp4
        vus = instances_fp4(N)
        rel_name = "fp4.chain.instances_fp4"
        ys = [int(v[3]) for v in vus]
    else:
        rel, want = frozen_relation(target, N)
        vus = relchain.instances(rel, N, procs=PROCS)
        rel_name = rel.name
        ys = [int(rel.y_public(int(v[3]))) if yb == 2 else int(v[3]) for v in vus]
    assert len(ys) == N
    dt = "<u2" if yb == 2 else "<u4"
    arr = np.asarray(ys, dtype=np.int64)
    assert arr.min() >= 0 and arr.max() < 2 ** (8 * yb), (fmt, arr.min(), arr.max())
    return rel_name, arr.astype(dt).tobytes()


def inst_file(p):
    d = p.read_bytes()
    assert d[:8] == b"VYSP1FI\x01"
    hl = int.from_bytes(d[8:12], "little")
    h = json.loads(d[12:12 + hl])
    n, rb, yb = h["n"], h["row_bytes"], h["y_bytes"]
    return h, d[12 + hl + 2 * n * rb:][: n * yb]


def main():
    out = Path(sys.argv[1])
    fmts = sys.argv[2:] or list(FORMATS)
    res = {}
    for fmt in fmts:
        fid, target, yb = FORMATS[fmt]
        ref = FROZEN_INSTANCES[target]
        rel_name, y = y_words(fmt, target, yb)
        ident = f"{ref['dataset']}|{ref['tier']}|{ref['range'][0]}|{ref['range'][1]}|{ref['manifest_sha256']}".encode()
        st = b"verity/sp1/relation-bare/v2" + struct.pack("<I", fid) + hashlib.sha256(ident).digest() + struct.pack("<II", K, N) + y
        (out / f"{fmt}.mine.bin").write_bytes(st)
        neg = bytearray(st)
        neg[-1] ^= 1
        (out / f"{fmt}.neg.bin").write_bytes(bytes(neg))
        r = {"target": target, "loader": rel_name, "y_bytes": yb, "y_sha256": hashlib.sha256(y).hexdigest(), "statement_bytes": len(st),
             "statement_sha256": hashlib.sha256(st).hexdigest(), "identity": ident.decode()}
        dump = out / fmt / "proofs" / "statement.bin"
        r["dump_statement_equal"] = dump.read_bytes() == st if dump.exists() else None
        ip = out / "inst" / f"{fmt}.bin"
        if ip.exists():
            h, iy = inst_file(ip)
            r["inst_y_equal"] = iy == y
            r["inst_header_y_sha256_equal"] = h.get("y_sha256") == r["y_sha256"]
            r["inst_instances_is_frozen"] = {k: h["instances"].get(k) for k in ref} == ref
        r["ok"] = bool(r["dump_statement_equal"]) and r.get("inst_y_equal", True) is not False and r.get("inst_instances_is_frozen", True) is not False
        res[fmt] = r
        print(fmt, json.dumps(r), flush=True)
    (out / "statements.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
