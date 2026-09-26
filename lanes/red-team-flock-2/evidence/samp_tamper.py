#!/usr/bin/env python3
"""red-team-flock-2: tampered verity/flock-ir-sampling/v1 verifier files (and one netlist) from a staged file. Each file is
self-consistent wherever the tamper allows it: the carries after a forged word are rescanned with the IR primitives, and the
token's frame-v3 root (or a public port's) recomputed, so what refuses it (Rust at load, the proof, or only check_native) is
the thing the case isolates. Prints one line per case: its path, public sha256 (what `serve --native-checked` names), the
token before and after, and check_native's verdict.

  samp_tamper.py STAGED_FILE NETLIST OUTDIR
"""
import hashlib, json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from samp_check import base, prims, fv3, uint, root  # noqa: E402

NEG_INF, HUGE = 0xFF800000, 0x7F000000


def dump(path, head, logits, digests, pub, cuts):
    names = [p for p, _ in head["public_ports"]]
    widths = dict(head["public_ports"])
    b = json.dumps(head, sort_keys=True).encode() + b"\n" + np.ascontiguousarray(logits, dtype="<u2").tobytes() + digests.tobytes()
    for i in range(head["instances"]):
        for p in names:
            b += int(pub[p][i]).to_bytes(4 * widths[p], "little")
    b += np.ascontiguousarray(cuts, dtype="<u4").tobytes()
    Path(path).write_bytes(b)


def rescan(c, V, pred=None):
    """Instance cut words c: carries recomputed from its kbit, g and scaled words (the Definition's scan, IR primitives); pred[v]
    is the lane whose carry lane v reads (v - 1 by default). Returns the token."""
    p = prims()
    noisy = int(c[3])
    carry = {}
    for v in range(V):
        b = base(v)
        m = p["sel"](int(c[b]), int(c[b + 2]), NEG_INF)
        y = p["sel"](noisy, p["addftz"](m, int(c[b + 1])), m)
        if v == 0:
            nb, ni = y, 0
        else:
            u = (pred or {}).get(v, v - 1)
            best, best_i, i = (int(c[base(u) + 3]), int(c[base(u) + 4]), int(c[base(u) + 5]))
            gt = p["gt"](y, best)
            nb, ni = p["sel"](gt, y, best), p["seli"](gt, i, best_i)
            i_in = i
        c[b + 3], c[b + 4], c[b + 5] = nb, ni, p["add"](0 if v == 0 else i_in, 1)
    return int(c[base(V - 1) + 4])


def token_root(head, cuts, V, override=None):
    name = "out.sampled_token_ids"
    dom = bytes.fromhex(head["frame_v3"]["domain_ids"][name])
    toks = [int(cuts[i][base(V - 1) + 4]) for i in range(head["instances"])]
    if override:
        toks[override[0]] = override[1]
    head["frame_v3"]["roots"][name] = root(dom, [fv3(b"leaf", [dom, uint(i), uint(i), b"u64", t.to_bytes(8, "big")]) for i, t in enumerate(toks)]).hex()


def public_root(head, pub, port):
    import blake3
    fv = head["frame_v3"]
    key, dom, w = bytes.fromhex(fv["key"]), bytes.fromhex(fv["domain_ids"][port]), fv["public_words"][port]
    fv["roots"][port] = root(dom, [fv3(b"leaf", [dom, uint(i), uint(i), b"blake3-keyed/row/v2",
                                                 blake3.blake3(int(x).to_bytes(4 * w, "little"), key=key).digest()])
                                   for i, x in enumerate(pub[port].tolist())]).hex()


def main():
    src, netp, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    import verity_flock.ir_sampling as IS
    from verity_vllm.program.registry import sampling as SM
    head0, logits, digests, pub0, cuts0 = IS.read(src)
    n, V = logits.shape
    dump(out / "roundtrip.bin", head0, logits, digests, pub0, cuts0)
    assert (out / "roundtrip.bin").read_bytes() == Path(src).read_bytes(), "the writer does not round-trip the staged file"
    p = prims()
    f = lambda w: float(np.uint32(w).view(np.float32))

    def lanes(i):
        c = cuts0[i]
        kb = c[7::6][:V]
        return c, kb, int(c[base(V - 1) + 4])

    def top_masked(i):
        """(margin, lane): instance i's masked lane with the largest noisy value, and how far it beats the row's best."""
        c, kb, _ = lanes(i)
        masked = [v for v in range(V) if not kb[v]]
        if not masked or int(kb.sum()) < 2:
            return (float("-inf"), None)
        v = max(masked, key=lambda v: f(p["addftz"](int(c[base(v) + 2]), int(c[base(v) + 1]))))
        return (f(p["addftz"](int(c[base(v) + 2]), int(c[base(v) + 1]))) - f(int(c[base(V - 1) + 3])), v)

    # the instance to forge: the one whose best masked lane would win by the most once unmasked
    I = max(range(n), key=lambda i: top_masked(i)[0])
    margin, v1 = top_masked(I)
    c, kb, tok = lanes(I)
    print(f"INSTANCE {I}: V {V}, kept lanes {int(kb.sum())}, token {tok}, temp {int(c[0]):#x}, public "
          f"{ {q: int(pub0[q][I]) for q in pub0} }; unmasking lane {v1} beats the best by {margin:.3f}")
    cases = {}

    def new():
        return json.loads(json.dumps(head0)), {q: a.copy() for q, a in pub0.items()}, cuts0.copy()

    # T1 a masked lane's keep bit set (the masked lane with the largest noisy value), carries and token root following
    h, pub, cuts = new()
    cuts[I][base(v1)] = 1
    t1 = rescan(cuts[I], V)
    token_root(h, cuts, V)
    cases["kbit_forged"] = (h, pub, cuts, f"lane {v1} unmasked: token {tok} -> {t1}")
    # T2 a kept lane's noise word set huge, carries and token root following
    h, pub, cuts = new()
    v2 = next(v for v in range(V) if kb[v] and v != tok)
    cuts[I][base(v2) + 1] = HUGE
    t2 = rescan(cuts[I], V)
    token_root(h, cuts, V)
    cases["noise_forged"] = (h, pub, cuts, f"lane {v2} noise -> {HUGE:#x}: token {tok} -> {t2}")
    # T3 a kept lane's tempered value (a unit output) forged; the keep bits recomputed natively from the forged row, so
    # check_native holds; carries and token root following. Only the proof can refuse it (scaled = TemperatureLane(x)).
    h, pub, cuts = new()
    sc = cuts0[I][9::6][:V].astype(np.uint32).view(np.float32)
    cuts[I][base(v2) + 2] = int(np.float32(np.nanmax(sc) + np.float32(8)).view(np.uint32))
    scaled = cuts[I][9::6][:V].astype(np.uint32)
    keep = SM.topp_mask_word(V).evaluate(*[int(x) for x in scaled], int(pub0["in1"][I]), int(pub0["in5"][I]))
    for v in range(V):
        cuts[I][base(v)] = (keep >> v) & 1
    t3 = rescan(cuts[I], V)
    token_root(h, cuts, V)
    cases["scaled_forged"] = (h, pub, cuts, f"lane {v2} scaled -> row max + 8 ({int(cuts[I][base(v2) + 2]):#x}), keep bits recomputed ({int(cuts[I][7::6][:V].sum())} kept): token {tok} -> {t3}")
    # T4 the token word (lane V-1's best_i, a unit output) and its root forged
    h, pub, cuts = new()
    t4 = (tok + 1) % V
    cuts[I][base(V - 1) + 4] = t4
    token_root(h, cuts, V)
    cases["token_word_forged"] = (h, pub, cuts, f"token word {tok} -> {t4} with its root")
    # T5 the token root alone forged
    h, pub, cuts = new()
    token_root(h, cuts, V, (I, t4))
    cases["token_root_forged"] = (h, pub, cuts, f"token root for {t4}, word {tok} kept")
    # T6 the public seed changed with its root recomputed (the units' words unchanged)
    h, pub, cuts = new()
    pub["in2"][I] += np.uint64(1)
    public_root(h, pub, "in2")
    cases["seed_forged_rooted"] = (h, pub, cuts, "seed + 1, its root recomputed, words unchanged")
    # T7 the public seed changed, root kept
    h, pub, cuts = new()
    pub["in2"][I] += np.uint64(1)
    cases["seed_forged_unrooted"] = (h, pub, cuts, "seed + 1, root kept")
    # T8 splits = 3 (not a split count) with its root
    h, pub, cuts = new()
    pub["in5"][I] = 3
    public_root(h, pub, "in5")
    cases["splits_invalid_rooted"] = (h, pub, cuts, "splits = 3, its root recomputed")
    # T10 the CUT line: the lane after the token reads the carry of the lane before it (the winning lane dropped from the
    # chain); the file's carries follow that netlist and the header names it
    text = open(netp).read()
    lines = text.splitlines()
    cut = json.loads(lines[-1][4:])
    if 1 <= tok < V - 1:
        w = tok + 1
        for j in range(3):
            cut["in"][w][6 + j][1] = base(tok - 1) + 3 + j
        ntext = "\n".join(lines[:-1] + ["CUT " + json.dumps(cut, sort_keys=True, separators=(",", ":"))]) + "\n"
        (out / "net-chain-broken.txt").write_text(ntext)
        h, pub, cuts = new()
        h["unit_sha256"] = hashlib.sha256(ntext.encode()).hexdigest()
        toks = [(int(cuts0[k][base(V - 1) + 4]), rescan(cuts[k], V, {w: tok - 1})) for k in range(n)]   # the netlist is every instance's
        token_root(h, cuts, V)
        cases["cut_chain_broken"] = (h, pub, cuts, f"lane {w} reads lane {tok - 1}'s carry in every instance (lane {tok} dropped): tokens "
                                                   f"{toks}; netlist sha {h['unit_sha256'][:16]}")
    for name, (h, pub, cuts, what) in cases.items():
        path = out / f"t-{name}.bin"
        dump(path, h, logits, digests, pub, cuts)
        try:
            bad = IS.check_native(path)
            nat = "clean" if not bad else "refuses: " + bad[0]
        except Exception as e:  # noqa: BLE001
            nat = f"raises: {type(e).__name__}: {e}"[:160]
        print(f"CASE\t{name}\t{path}\t{IS.public_sha256(path)}\t{what}\tcheck_native {nat}")


if __name__ == "__main__":
    main()
