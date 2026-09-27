import hashlib, json
v = json.load(open("/tmp/vec/serving-row-leaf-vector.json"))
FRAME = b"veritor/protocol/merkle/frame/v3\0"
def H(tag, parts):
    h = hashlib.sha512(FRAME + len(tag).to_bytes(4, "big") + tag)
    for p in parts:
        h.update(len(p).to_bytes(8, "big") + p)
    return h.digest()
def uint(x):
    return x.to_bytes(max(1, (x.bit_length() + 7) // 8), "big")
dom = bytes.fromhex(v["domain"]["domain_id"])
schema = b"hm96-sha512/row/v1"
pre = bytes.fromhex(v["row_prefix_block"])
lp = bytes.fromhex(v["hm96"]["leaf_prefix"]); sp = bytes.fromhex(v["hm96"]["salt_prefix"])
leaves = []
for r in v["rows"]:
    rb = b"".join(w.to_bytes(2, "little") for w in r["words_u16"])
    assert rb.hex() == r["row_bytes"]
    x = hashlib.sha512(pre + rb).digest(); assert x.hex() == r["x_sha512_row_v1"]
    y = bytes.fromhex(r["salt_y"]); c = hashlib.sha512(sp + y).digest(); assert c.hex() == r["c"]
    bc = bytes.fromhex(r["b"]) + c
    t = hashlib.sha512(lp + bc).digest(); assert t.hex() == r["tree_leaf"]
    leaf = H(b"leaf", [dom, uint(r["index"]), uint(r["index"]), schema, t]); assert leaf.hex() == r["frame_leaf"], r["index"]
    leaves.append(leaf)
n = len(leaves); w = 1 << (n - 1).bit_length()
level = leaves + [H(b"pad", [dom, uint(i)]) for i in range(n, w)]
d = 0
while len(level) > 1:
    level = [H(b"node", [dom, uint(d), uint(i), level[2 * i], level[2 * i + 1]]) for i in range(len(level) // 2)]
    d += 1
assert level[0].hex() == v["root"]
# the prefix block per spec: tag, role, word_bits, u32be n_words, zero padded to 128
assert pre == (b"verity/sha512-row/v1\0" + bytes([1, 16]) + (8).to_bytes(4, "big")).ljust(128, b"\0")
print("from-scratch framing reproduces every leaf and the root")
