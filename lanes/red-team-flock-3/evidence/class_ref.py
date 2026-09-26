#!/usr/bin/env python3
"""red-team-flock-3: the reviewed attention generator's per-T netlists, for checking a key-count class manifest (CP5).

For every T in [lo, hi]: sha256 of `attention_head.lowering(sub, T).text` (the reviewed generator, at the tree on PYTHONPATH),
the sha256 of its unit rows (lines 1..useful: the block circuit, which must not depend on T), of its LEAVES line and of its
CUT line (the leaf maps and the softmax tail, which are T's). Also checks, with my own reader, that the rows are identical
for every T and that the LEAVES / CUT lines parse.

  class_ref.py LO HI OUT.json
"""
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402

from verity_flock.templates import attention_head as AH  # noqa: E402
from verity_numerical.bench import templates as TM  # noqa: E402


def main():
    lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    sub = TM.subcircuit("attention-head", D=64, BN=128)
    ref, rows0 = {}, None
    t0 = time.time()
    for T in range(lo, hi + 1):
        text = AH.lowering(sub, T).text
        lines = text.split("\n")
        net = NL.Net(text)
        rows = "\n".join(lines[1:1 + net.useful])
        rh = hashlib.sha256(rows.encode()).hexdigest()
        rows0 = rows0 or rh
        lv = next(l for l in lines if l.startswith("LEAVES "))
        cut = next(l for l in lines if l.startswith("CUT "))
        ref[T] = {"net": hashlib.sha256(text.encode()).hexdigest(), "rows": rh, "header": lines[0],
                  "leaves": hashlib.sha256(lv.encode()).hexdigest(), "cut": hashlib.sha256(cut.encode()).hexdigest(),
                  "units": len(net.cut["in"]), "cut_words": net.cut["words"], "tail_ops": len(net.cut["tail"]),
                  "in_ports": net.leaves["in_ports"]}
        assert rh == rows0, f"T={T}: unit rows differ from T={lo}'s"
        assert net.leaves["in_ports"] == [[64, 16], [64 * T, 16], [64 * T, 16]], T
        if T % 64 == 0:
            print(f"T={T} {time.time() - t0:.0f}s", flush=True)
    Path(out).write_text(json.dumps({"lo": lo, "hi": hi, "unit_rows_sha256": rows0, "per_T": ref}, indent=0))
    print("CLASS_REF", json.dumps({"lo": lo, "hi": hi, "unit_rows_sha256": rows0, "distinct_nets": len({v["net"] for v in ref.values()}),
                                   "seconds": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
