#!/usr/bin/env python3
"""red-team-flock-2: a verity/flock-ir-sampling/v1 cell's verifier-staged netlist and instance file checked against the IR,
independently of verity_flock.ir_sampling (whose parser `read` is the only piece used) and of the Rust verifier:

- net: my flock-ir-unit/v2 parser (rms_check.parse_v2); the netlist without its CUT line hashes to the pin; the CUT line is
  my own derivation of the chain (row scalars 0..3, init 4..6, lane v at 7 + 6v: kbit, g, scaled, best, best_i, i+1), and
  every cut word is either native (0..6, kbit, g) or computed by exactly one unit; each carry word is read by the next lane only.
- file: every cut word and the token recomputed per instance with the IR primitives' scalar evaluators, composed as the
  Definition (`TemperatureScale -> TopPMask -> GumbelSelectF32`), `TopPMaskWordx{V}` and `GumbelNoiseLane` called through
  their PrimitiveDefinitions; the whole file's lanes through my bit-sliced evaluation of the netlist (outputs and constraint
  satisfaction); row digests, frame-v3 roots and domain ids recomputed.
- lanes: adversarial lanes through the netlist against the IR composites (`TemperatureLane`, `TopPMaskStep{V}`,
  `GumbelSelectStep`) by verity.ir.evaluate.evaluate_call, and against a primitive composition when g is adversarial.

  samp_check.py net NETLIST V
  samp_check.py file INSTANCE_FILE NETLIST [procs]
  samp_check.py lanes NETLIST V N [seed]
"""
import hashlib, json, random, sys, time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rms_check import parse_v2, port_cols, structure, evaluate, read_port  # noqa: E402
from frame_check import fv3, uint, root  # noqa: E402

NEG_INF, ONE = 0xFF800000, 0x3F800000
M32 = 0xFFFFFFFF


def base(v):
    return 7 + 6 * v


def my_lane_ports(v):
    carry = [4, 5, 6] if v == 0 else [base(v - 1) + 3, base(v - 1) + 4, base(v - 1) + 5]
    return [0, 1, 2, 3, base(v), base(v) + 1, *carry], [base(v) + 2, base(v) + 3, base(v) + 4, base(v) + 5]


def check_net(path, V):
    text = open(path).read()
    lines = text.splitlines()
    assert lines[-1].startswith("CUT "), "no CUT line"
    unit_text = "\n".join(lines[:-1]) + "\n"
    import verity_flock.ir_sampling as IS
    pin = hashlib.sha256(unit_text.encode()).hexdigest()
    nt = parse_v2(path)
    st = structure(nt)
    ig, og = nt["ig"], nt["og"]
    ok_groups = [b for _, _, b in ig] == [[16], [32] * 9] and [b for _, _, b in og] == [[32] * 4]
    cut = json.loads(lines[-1][4:])
    cin = [c for c, _ in port_cols(ig)[1:]]
    cout0 = og[0][0] * 128
    cout = [c - cout0 for c, _ in port_cols(og)]
    bad = []
    words = 7 + 6 * V
    reads = {}
    produced = {}
    for v in range(V):
        a, b = my_lane_ports(v)
        if cut["in"][v] != [[c, k] for c, k in zip(cin, a)] or cut["out"][v] != [[c, k] for c, k in zip(cout, b)]:
            bad.append(v)
        for _, k in cut["in"][v]:
            reads.setdefault(k, []).append(v)
        for _, k in cut["out"][v]:
            produced.setdefault(k, []).append(v)
    native = set(range(7)) | {base(v) for v in range(V)} | {base(v) + 1 for v in range(V)}
    twice = [k for k, us in produced.items() if len(us) != 1]
    cover = set(produced) | native == set(range(words)) and not (set(produced) & native)
    carry_ok = all(reads.get(base(v) + j, []) == [v + 1] for v in range(V - 1) for j in (3, 4, 5)) and \
        all(reads.get(k, []) == [0] for k in (4, 5, 6)) and all(k not in reads for v in range(V) for k in (base(v) + 2,)) and \
        all(k not in reads for k in (base(V - 1) + 3, base(V - 1) + 4, base(V - 1) + 5))
    print(f"NET {path}: sha {hashlib.sha256(text.encode()).hexdigest()[:16]}; unit text (no CUT) sha == PIN {IS.PIN[:16]}: {pin == IS.PIN}; "
          f"rows {st['rows']}, structure violations {st['n_bad']}; ports (16 | 9x32 -> 4x32): {ok_groups}")
    print(f"CUT: words {cut['words']} == 7 + 6V {words}: {cut['words'] == words}; tail {cut['tail']}; native {cut['native']!r}; "
          f"lanes whose ports differ from my chain derivation: {len(bad)} {bad[:3]}; words computed twice: {len(twice)}; "
          f"native + unit-computed words partition all {words}: {cover}; each carry read once, by the next lane (lane V-1's by none, "
          f"scaled by none): {carry_ok}; token word {base(V - 1) + 4}")
    lo = IS.lane(V)
    print(f"REGEN: the tip's lowering (af0bd416) regenerates this netlist byte for byte: {lo.text == text}")
    return nt, cut


def prims():
    from verity_vllm.program.registry import prims as P, ref_prims as RP, sampling as SM
    from verity.ml import scalar as S
    return dict(bf=P.Bf16ToF32.evaluate, dsa=P.DivFullScaleA.evaluate, mul=P.F32Mul.evaluate, sel=P.SelectF32.evaluate,
                seli=P.SelectI32.evaluate, add=P.I32Add.evaluate, rcp=P.DivFullRcp.evaluate, addftz=P.F32AddFtz.evaluate,
                gt=RP.F32GtStrict.evaluate, eq=S.F32Eq.evaluate, bor=S.BitOr.evaluate, bnot=S.BitNot.evaluate,
                key=SM.GumbelStreamKey.evaluate, noise=SM.GumbelNoiseLane.evaluate, SM=SM)


def row_ir(logits, top_p, seed, pos, temp, splits):
    """Every cut word of one instance and the token, by the IR primitives composed as the Definition."""
    p = prims()
    V = len(logits)
    rcp = p["rcp"](temp)
    skip = p["bor"](p["eq"](temp, 0), p["eq"](temp, ONE))
    noisy = p["bnot"](p["eq"](temp, 0))
    scaled = []
    for x in logits:
        xf = p["bf"](int(x))
        scaled.append(p["sel"](skip, xf, p["mul"](p["dsa"](xf, temp), rcp)))
    keep = p["SM"].topp_mask_word(V).evaluate(*scaled, top_p, splits)
    bit = p["SM"].bit_at(V).evaluate
    key = p["key"](seed, pos)
    out = [temp, rcp, skip, noisy, 0, 0, 0]
    best = best_i = None
    for v in range(V):
        kb = bit(keep, v)
        m = p["sel"](kb, scaled[v], NEG_INF)
        g = p["noise"](key, v)
        y = p["sel"](noisy, p["addftz"](m, g), m)
        if v == 0:
            best, best_i = y, 0
        else:
            gt = p["gt"](y, best)
            best, best_i = p["sel"](gt, y, best), p["seli"](gt, v, best_i)
        out += [kb, g, scaled[v], best, best_i, p["add"](v, 1)]
    return np.array(out, dtype=np.uint32), best_i


def _row_job(args):
    i, logits, pub = args
    t0 = time.time()
    w, tok = row_ir(logits, *pub)
    return i, w, tok, time.time() - t0


def check_file(ipath, npath, procs=4):
    import blake3
    import verity_flock.ir_sampling as IS
    from verity.commitments.indexed import RangeIndexedDomain
    from verity.commitments.merkle import CommitmentDomain
    head, logits, digests, pub, cuts = IS.read(ipath)
    n, V = logits.shape
    names = [p for p, _ in head["public_ports"]]
    assert names == ["in1", "in2", "in3", "in4", "in5"]
    pubs = [[int(pub[p][i]) for p in names] for i in range(n)]
    print(f"FILE {ipath}: {n} instances, V {V}, cut words {head['cut_words']}; public words per instance "
          f"(top_p, seed, pos, temp, splits): {[[hex(x) if k in (0, 3) else x for k, x in enumerate(r)] for r in pubs]}", flush=True)
    t0 = time.time()
    with Pool(procs) as pool:
        res = sorted(pool.map(_row_job, [(i, logits[i].tolist(), pubs[i]) for i in range(n)]))
    toks = []
    for i, w, tok, dt in res:
        diff = np.flatnonzero(w != cuts[i])
        toks.append(tok)
        nat = [k for k in diff.tolist() if k < 7 or (k - 7) % 6 in (0, 1)]
        print(f"  instance {i}: IR words vs file: {len(diff)} differ ({len(nat)} native) [first {diff[:3].tolist()}]; token {tok} "
              f"== file word {int(cuts[i][base(V - 1) + 4])}: {tok == int(cuts[i][base(V - 1) + 4])}; temp {pubs[i][3]:#x}, "
              f"kept lanes {int(cuts[i][7::6].sum())}, noisy {int(cuts[i][3])} ({dt:.0f} s)", flush=True)
    print(f"IR recomputation: {time.time() - t0:.0f} s")
    # the file's lanes through the netlist: every unit's outputs are the file's cut words, and every constraint holds
    nt = parse_v2(npath)
    icols = port_cols(nt["ig"])
    ocols = port_cols(nt["og"])
    idx_in = np.array([my_lane_ports(v)[0] for v in range(V)])
    idx_out = np.array([my_lane_ports(v)[1] for v in range(V)])
    mism = unsat = 0
    CH = 1 << 16
    flat_x = logits.reshape(-1).astype(np.uint64)
    cin = [cuts[:, idx_in[:, j]].reshape(-1).astype(np.uint64) for j in range(9)]
    cout = [cuts[:, idx_out[:, j]].reshape(-1).astype(np.uint64) for j in range(4)]
    for s in range(0, n * V, CH):
        e = min(n * V, s + CH)
        assign = [(icols[0][0], 16, flat_x[s:e])] + [(icols[1 + j][0], 32, cin[j][s:e]) for j in range(9)]
        z, okl = evaluate(nt, assign, e - s)
        unsat += int((~okl).sum())
        for j in range(4):
            mism += int((read_port(z, ocols[j][0], 32, e - s) != cout[j][s:e]).sum())
    print(f"UNITS: {n * V} lanes of the file through my netlist evaluation: output-word mismatches {mism}, unsatisfied lanes {unsat}")
    # commitments
    key = bytes.fromhex(head["frame_v3"]["key"])
    from verity.commitments.rowleaf import ROLE_X, blake3_row_key
    fv = head["frame_v3"]
    ok_key = key == blake3_row_key(ROLE_X)
    ok_d = all(blake3.blake3(logits[i].astype("<u2").tobytes(), key=key).digest() == digests[i].tobytes() for i in range(n))
    roots, doms = {}, {}
    for name in fv["roots"]:
        b = bytes.fromhex(fv["bindings"][name])
        doms[name] = CommitmentDomain(b, fv["owner"], RangeIndexedDomain(0, n)).domain_id.hex() == fv["domain_ids"][name]
    dom = lambda nm: bytes.fromhex(fv["domain_ids"][nm])
    roots["in0"] = root(dom("in0"), [fv3(b"leaf", [dom("in0"), uint(i), uint(i), b"blake3-keyed/row/v2", digests[i].tobytes()]) for i in range(n)])
    for k, p in enumerate(names):
        w = fv["public_words"][p]
        roots[p] = root(dom(p), [fv3(b"leaf", [dom(p), uint(i), uint(i), b"blake3-keyed/row/v2",
                                              blake3.blake3(pubs[i][k].to_bytes(4 * w, "little"), key=key).digest()]) for i in range(n)])
    out = "out.sampled_token_ids"
    roots[out] = root(dom(out), [fv3(b"leaf", [dom(out), uint(i), uint(i), b"u64", toks[i].to_bytes(8, "big")]) for i in range(n)])
    print(f"COMMIT: key = x-row key {ok_key}; row digests = keyed BLAKE3 of the rows {ok_d}; domain ids = CommitmentDomain(binding, owner, "
          f"[0, n)) {all(doms.values())}; roots recomputed (token root from MY IR tokens) == header: "
          f"{ {k: r.hex() == fv['roots'][k] for k, r in roots.items()} }")
    print(f"BINDING: {bind_check(head)}")
    bad = IS.check_native(ipath)
    print(f"check_native (the producer's) on this file: {bad or 'clean'}")


def bind_check(head):
    """Each port's binding = identity_digest(ir_frame.BINDING_TAG, set, content digest, range, port, schema)."""
    import verity_flock.ir_frame as IF
    from verity.commitments.identity import identity_digest
    fv = head["frame_v3"]
    lo, hi = head["range"]
    return all(identity_digest(IF.BINDING_TAG, {"set": head["set"], "content_digest": head["content_digest"], "lo": lo, "hi": hi,
                                                "port": nm, "schema": fv["schemas"][nm]}) == fv["bindings"][nm] for nm in fv["roots"])


def f32_word(rng, fam):
    s = rng.getrandbits(1) << 31
    if fam == "nan":
        return s | 0x7F800000 | rng.randrange(1, 1 << 23)
    if fam == "inf":
        return s | 0x7F800000
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 1 << 23)
    if fam == "big":
        return s | rng.randrange(0x7E800000, 0x7F800000)
    if fam == "tiny":
        return s | rng.randrange(0x00800000, 0x01000000)
    if fam == "one":
        return rng.choice([ONE, 0x3F800001, 0x3F7FFFFF, 0xBF800000])
    return rng.getrandbits(32)


FAMS = ["any", "nan", "inf", "zero", "sub", "big", "tiny", "one"]


def check_lanes(npath, V, N, seed=20260926):
    from verity.ir.evaluate import evaluate_call
    import verity_flock.ir_lower as IL
    p = prims()
    SM = p["SM"]
    rng = random.Random(seed)
    tl = IL.standalone(SM.TemperatureLane)
    ms = IL.standalone(SM.bind(SM.TopPMaskStep, V=V))
    gs = IL.standalone(SM.GumbelSelectStep)
    rows, kinds = [], []
    for t in range(N):
        fx, ft, fg, fb = (rng.choice(FAMS) for _ in range(4))
        x = rng.getrandbits(16) if rng.random() < 0.5 else (f32_word(rng, fx) >> 16)
        temp = f32_word(rng, ft)
        rcp = p["rcp"](temp)
        skip = p["bor"](p["eq"](temp, 0), p["eq"](temp, ONE))
        noisy = p["bnot"](p["eq"](temp, 0))
        if rng.random() < 0.1:
            skip, noisy = rng.getrandbits(1), rng.getrandbits(1)   # the circuit reads the words as given
        kbit = rng.getrandbits(1)
        i = rng.choice([0, 0, 1, V - 1, rng.randrange(V)])
        real_g = rng.random() < 0.3
        key = rng.getrandbits(32)
        g = p["noise"](key, i) if real_g else f32_word(rng, fg)
        best = f32_word(rng, fb)
        best_i = rng.randrange(V)
        rows.append((x, temp, rcp, skip, noisy, kbit, g, best, best_i, i, key, real_g))
    nt = parse_v2(npath)
    icols, ocols = port_cols(nt["ig"]), port_cols(nt["og"])
    arr = np.array([r[:10] for r in rows], dtype=np.uint64)
    assign = [(icols[j][0], icols[j][1], arr[:, j]) for j in range(10)]
    z, okl = evaluate(nt, assign, N)
    got = np.stack([read_port(z, ocols[j][0], 32, N) for j in range(4)], axis=1)
    bad, t0 = [], time.time()
    for t, (x, temp, rcp, skip, noisy, kbit, g, best, best_i, i, key, real_g) in enumerate(rows):
        (scaled,) = evaluate_call(tl[0].circuit, tl[1], [x, temp, rcp, skip])
        keep = kbit << i
        _, masked = evaluate_call(ms[0].circuit, ms[1], [i, scaled, keep])
        if real_g:
            r = evaluate_call(gs[0].circuit, gs[1], [best, best_i, i, masked, key, noisy])
            nb, ni, nxt = r[0], r[1], r[2]
            y = p["sel"](noisy, p["addftz"](masked, g), masked)
        else:
            y = p["sel"](noisy, p["addftz"](masked, g), masked)
            gt = p["gt"](y, best)
            nb, ni, nxt = p["sel"](gt, y, best), p["seli"](gt, i, best_i), p["add"](i, 1)
        if i == 0:
            nb, ni = y, 0
        want = [scaled, nb, ni, nxt]
        if [int(v) for v in got[t]] != want or not okl[t]:
            bad.append((t, [hex(v) for v in want], [hex(int(v)) for v in got[t]], bool(okl[t])))
    print(f"LANES: {N} adversarial lanes (seed {seed}; x/temp/g/best over {FAMS}, 30% real noise words via GumbelSelectStep, 10% free "
          f"skip/noisy words): mismatches or unsatisfied {len(bad)} {bad[:2]}; unsatisfied {int((~okl).sum())} ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "net":
        check_net(sys.argv[2], int(sys.argv[3]))
    elif cmd == "file":
        check_file(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 4)
    elif cmd == "lanes":
        check_lanes(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 20260926)
