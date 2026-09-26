#!/usr/bin/env python3
"""red-team-flock-3: an attention cell's verifier-staged flock-ir-frame/v3 statement (its instance file and netlist) checked
against the IR, independently of the Rust verifier:
- the netlist is the reviewed lowering of AttentionHead_v3{T} for the file's T (text equality), and T is the key count of every
  instance's rows;
- every real unit slot's wiring reads, for each leaf port, exactly the row element the pinned LEAVES map names, from a run of
  its own instance; a zero leaf (-1) reads an empty run slot; a hole (an empty unit slot of a real block) reads only empty run
  slots; every run of every K / V row chunk and every unit sits exactly once; q (the public port) has no run;
- the K / V row digests are keyed BLAKE3 (x key) of the rows; q's digest is that of its row AND of its public cut words; the
  frame-v3 roots (my own frame-v3 code) of the digests and of the output words are the header's;
- my end-to-end solver (units by my netlist evaluator, the tail by the IR's primitives) reproduces every cut word and output
  word in the file, and the IR reference evaluator gives the same outputs.

  cell_check.py INSTANCE_FILE NETLIST [INPUT_SET_DIR]
"""
import hashlib
import json
import sys
from pathlib import Path

import blake3
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import attn_e2e as E  # noqa: E402
import frame_tamper3 as FT  # noqa: E402
import netlist as NL  # noqa: E402


def main():
    ipath, npath = sys.argv[1:3]
    text = open(npath).read()
    net = NL.Net(text)
    f = FT.File(ipath)
    h = f.h
    D = 64
    T = h["in_ports"][1][1] // D
    assert h["in_ports"] == [["q", D], ["k", T * D], ["v", T * D]] and h["out_ports"] == [["out", D]], h["in_ports"]
    same = text == E.net_for(T)[1].text
    print(f"NETLIST T={T} {net.sha256[:16]} == reviewed lowering of AttentionHead_v3{{T={T}}}: {same}; header unit_sha256 matches: {h['unit_sha256'] == net.sha256}")
    lv, lay, blocks = net.leaves, h["layout"], h["blocks"]
    n, upi, nb = f.n, h["units_per_instance"], lay["nb"]
    run_bytes = 64 * nb
    starts = [0, D, D + T * D]
    bad, seen_runs, seen_units, holes = [], set(), set(), 0
    for bi, (chunks, units) in enumerate(blocks):
        real_block = any(u is not None for u in units)
        for c in chunks:
            if c is not None:
                seen_runs.add(tuple(c))
        for u, g in enumerate(units):
            w = lay["wiring"][u]
            if g is None:
                if real_block:
                    holes += 1
                    if any(chunks[q] is not None for q, _ in w):
                        bad.append((bi, u, "hole wired to a real run"))
                continue
            seen_units.add(g)
            i, lu = g // upi, g % upi
            for j, (q, off) in enumerate(w):
                want = lv["in"][lu][j]
                if want == -1:
                    if chunks[q] is not None:
                        bad.append((bi, u, g, j, "zero leaf on a real run"))
                    continue
                if chunks[q] is None:
                    bad.append((bi, u, g, j, "real leaf on an empty run")); continue
                ci, p, c, r = chunks[q]
                leaf = starts[p] + (1024 * c + run_bytes * r + off) // 2
                if ci != i or leaf != want or off % 2:
                    bad.append((bi, u, g, j, (ci, p, c, r, off), want))
    want_runs = set()
    for i in range(n):
        for p in (1, 2):
            nbytes = 2 * T * D
            for c in range((nbytes + 1023) // 1024):
                blocks_c = min(1024, nbytes - 1024 * c) // 64
                for r in range(blocks_c // nb):
                    want_runs.add((i, p, c, r))
    print(f"LAYOUT {len(blocks)} blocks, {len(seen_units)} of {h['units']} units, {len(seen_runs)} runs == every K/V run once: "
          f"{seen_runs == want_runs}, q runs: {sum(1 for x in seen_runs if x[1] == 0)}, holes: {holes}; wiring differences from the "
          f"pinned leaf maps: {len(bad)} {bad[:3]}")
    key = bytes.fromhex(h["frame_v3"]["key"])
    from verity.commitments.rowleaf import ROLE_X, blake3_row_key
    ok_d = key == blake3_row_key(ROLE_X)
    for i in range(n):
        for p, (lo, w) in enumerate(((0, D), (D, T * D), (D + T * D, T * D))):
            row = bytes(f.rows[i * f.rb + 2 * lo:i * f.rb + 2 * (lo + w)])
            ok_d &= blake3.blake3(row, key=key).digest() == f.digest(i, p)
        qb = b"".join(int(f.cuts[i * f.kc + k]).to_bytes(2, "little") for k, _ in sorted(net.cut["public"], key=lambda x: x[1]))
        ok_d &= blake3.blake3(qb, key=key).digest() == f.digest(i, 0)
    r = f.roots()
    ok_r = all(r[k] == h["frame_v3"]["roots"][k] for k in r)
    print(f"COMMIT key = blake3_row_key(ROLE_X) and every digest (q from its row and its public words) keyed BLAKE3: {ok_d}; "
          f"frame-v3 roots = header's: {ok_r}")
    flat = np.stack([np.frombuffer(bytes(f.rows[i * f.rb:(i + 1) * f.rb]), dtype="<u2").astype(np.uint64) for i in range(n)])
    s = E.Solver(net)
    slots, outs, st = s.solve(flat)
    fc = f.cuts.reshape(n, f.kc); fo = f.outs.reshape(n, f.ow)
    ir = E.ir_outputs(T, flat)
    res = {"undetermined": st["undetermined_cut_words"], "sat": st["sat"], "cut_mismatch_words": int((slots[:, :f.kc] != fc).sum()),
           "out_mismatch_words_vs_file": int((outs != fo).sum()), "ir_vs_file_out_words": int((ir != fo).sum())}
    if len(sys.argv) > 3:
        from verity_numerical.bench.input_sets import InputSet
        cs = InputSet.open(sys.argv[3]); lo, hi = h["range"]
        cq, ck, cv, co = cs.port("q"), cs.port("k"), cs.port("v"), cs.port("out")
        cap = np.stack([np.concatenate([cq[i], ck[i], cv[i]]).astype(np.uint64) for i in range(lo, hi)])
        res["rows_equal_input_set"] = bool((cap == flat).all())
        res["captured_out_vs_file_words"] = int((np.stack([np.asarray(co[i], dtype=np.uint64) for i in range(lo, hi)]) != fo).sum())
        res["set_key_counts"] = sorted({len(x) // D for x in ck})
    print("E2E", json.dumps(res))
    ok = same and not bad and seen_runs == want_runs and ok_d and ok_r and res["undetermined"] == 0 and res["sat"] and \
        res["cut_mismatch_words"] == 0 and res["out_mismatch_words_vs_file"] == 0 and res["ir_vs_file_out_words"] == 0 and \
        res.get("rows_equal_input_set", True) and res.get("captured_out_vs_file_words", 0) == 0 and res.get("set_key_counts", [T]) == [T]
    print("CELL_CHECK", "PASS" if ok else "FAIL", ipath)


if __name__ == "__main__":
    main()
