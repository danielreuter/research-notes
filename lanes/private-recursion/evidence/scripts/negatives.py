"""The prototype's own negatives (spec I.9): each one a witness or public input a cheating prover could submit."""
import json, sys, time, copy, os
ART=os.environ.get('ART','/tmp/pr/arts')
import numpy as np
from verity_flock.recursion import session as S, statement as T, vb, coins, witness as W, program as P, hm

circ = T.parse_circuit(open(ART+'/d9837120/circuit.txt').read())
pub = T.load_public(ART+'/d9837120/pub-8.bin', circ)
st = T.Statement(circ, pub, T.load_comp(ART+'/04259cdd/comp.rows'))
fr = vb.Frame.of(st)
prog = vb.build(fr)
sess = S.load_session(ART+'/bd9f7efb/honest')
tabs = coins.tables(fr, st, sess)
C = st.C


def run(name, C_wit=C, c_of=None, data=pub, edit=None, expect="R"):
    t = time.time()
    try:
        pubi, wit = W.convert(fr, st, C_wit, data, sess, tabs, c_of=c_of, rng=np.random.default_rng(11))
        inputs = {**tabs, **pubi, **wit}
        if edit:
            edit(inputs)
        r = P.evaluate(prog, inputs)
        v, why = ("A" if r.accepted else "R"), [f"{w} x{n}" for w, n in r.failed]
    except W.Refused as e:
        v, why = "R", ["refused: " + str(e)]
    print(json.dumps({"negative": name, "expect": expect, "vb": v, "ok": v == expect, "why": why, "s": round(time.time() - t, 1)}), flush=True)


def with_(C0, **kw):
    C1 = copy.deepcopy(C0)
    for k, v in kw.items():
        setattr(C1, k, v)
    return C1


run("honest", expect="A")

# a wrong C
C_one_off = with_(C, b=C.b[:-1] + [(C.b[-1][0], (C.b[-1][1] + 1) % C.b[-1][0])])
run("enc-one-entry-off (c commits to C)", C_wit=C_one_off, c_of=C)
run("different-C-registered (C' opens c, session is C's)", C_wit=C_one_off, c_of=C_one_off)
C_gptj = with_(C, leaves_in=[[2 * (u % 16) + 32 * (u // 16), 2 * (u % 16) + 1 + 32 * (u // 16),
                              64 + 2 * (u % 16) + 32 * (u // 16), 65 + 2 * (u % 16) + 32 * (u // 16)] for u in range(32)])
run("gptj-pairing-C (a different circuit, same B)", C_wit=C_gptj, c_of=C_gptj)

# Φ violations, registered (C' opens c), isolated from the fold where possible
r0, c0 = C.b[5]
later = (r0, r0 + 1)
C_later = with_(C, b=C.b + [later, later])                         # a later-column entry, twice: the fold is unchanged
run("phi-later-column (entry twice, fold unchanged)", C_wit=C_later, c_of=C_later)
C_dup = with_(C, leaves_out=[list(x) for x in C.leaves_out])
C_dup.leaves_out[1][0] = C_dup.leaves_out[0][0]
run("phi-leaf-bound-twice (leaves_out not a permutation)", C_wit=C_dup, c_of=C_dup)
C_cp = with_(C, useful=100)
run("phi-constant-row-is-an-input-row", C_wit=C_cp, c_of=C_cp)


def noncanonical(inp):
    ra = inp["enc.ra"].copy(); ca = inp["enc.ca"].copy()
    ca[-1, 0] = 1                                                    # a padding entry with a nonzero column
    inp["enc.ca"] = ca


run("phi-noncanonical-padding (witness edit, c from C)", edit=noncanonical)

# a broken inner transcript / mismatched commitments
fo = vb.field_offsets(fr)


def flip_msg(key, byte=0):
    def f(inp):
        m = inp["m"].copy(); m[fo[key][0][byte]] ^= 1; inp["m"] = m
    return f


run("msg-zc-ab-flipped (message does not open c_j)", edit=flip_msg(("zc_ab",)))
run("msg-free-digest-field-flipped (opening fails)", edit=flip_msg(("digest",)))


def swap_cj(inp):
    cj = inp["cj"].copy(); cj[[5, 6]] = cj[[6, 5]]; inp["cj"] = cj


run("cj-two-rounds-swapped", edit=swap_cj)


def wrong_c(inp):
    c = inp["c"].copy(); c[0] ^= 1; inp["c"] = c


run("c-mismatched", edit=wrong_c)


def wrong_salt(inp):
    r = inp["r"].copy(); r[3, 0] ^= 1; inp["r"] = r


run("round-salt-wrong", edit=wrong_salt)

# the data: a flipped bit in an output leaf
def flip_out(inp):
    o = inp["data.out"].copy(); o[0, 0, 0] ^= 1; inp["data.out"] = o


run("output-bit-flipped (witness; D is the true root)", edit=flip_out)
bad_pub = copy.deepcopy(pub)
bad_pub.outputs[0][0] ^= 1
import hashlib


def fv3(tag, parts):
    h = hashlib.sha256(b"veritor/protocol/merkle/frame/v3\0" + len(tag).to_bytes(4, "big") + tag)
    for x in parts:
        h.update(len(x).to_bytes(8, "big") + x)
    return h.digest()


def uint(x):
    return x.to_bytes(8, "big").lstrip(b"\0") or b"\0"


dom = bytes.fromhex(pub.header["frame_v3"]["domain_ids"]["out"])
lv = [fv3(b"leaf", [dom, uint(r), uint(r), b"u16", v.to_bytes(2, "big")]) for r, v in enumerate(x for inst in bad_pub.outputs for x in inst)]
d = 0
while len(lv) > 1:
    lv = [fv3(b"node", [dom, uint(d), uint(i), lv[2 * i], lv[2 * i + 1]]) for i in range(len(lv) // 2)]
    d += 1
bad_pub.header = copy.deepcopy(pub.header)
bad_pub.header["frame_v3"]["roots"]["out"] = lv[0].hex()
run("output-bit-flipped (a false statement: D recomputed over the flipped output)", data=bad_pub)
