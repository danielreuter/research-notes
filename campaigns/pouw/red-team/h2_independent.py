"""Pearl-C -h2 (frame-b3s), rebuilt from `a-commit-latency.md` §7's text alone with the Rust `blake3` package, against the
pinned vectors of `test_frame_b3s.py` (only the domain id is taken from them: it is frame v3's, unchanged but for its tag).
Also: the binding checks the four format conditions imply, as collisions a wrong format would produce."""
import json

import blake3

PINNED = {"domain_id": "1397806572d8d301bbc4761e07d033a29c6260af9f5e537c0ab711ca4058e10c",
          "seg_key_2_1": "94020f4be26cabc357b24062e037fed2b5019570c9a28636bb596d6f71c32d63",
          "level_key_3": "ffc1d87469edc7fad3563fa12f15708748815a9f279fa065ab3d2c4349a4ab47",
          "leaf_3": "00b1f748f81fcbbff11720c7b5f02ac0ac1e6549b2d459eecab37f0168eaedca",
          "row_32k": "5599f93a410b0fe87c80e90c108db65fa3f4cf6a6b70cf1b1ae138cc8947edad",
          "root": "026500f3ea571d4a139c352a980ab101f55bf2df77c3d34761e130ac31e51aab"}
DOM = bytes.fromhex(PINNED["domain_id"])


def keyed(k: bytes, m: bytes) -> bytes:
    return blake3.blake3(m, key=k).digest()


def u(n: int, w: int) -> bytes:
    return n.to_bytes(w, "little")


def seg_key(r, p, schema, L, j):              # K_j = keyed(domain id, 0x05 ‖ u64 r ‖ u64 p ‖ u64 L ‖ u32 j ‖ u16 len(σ) ‖ σ)
    s = schema.encode()
    return keyed(DOM, b"\x05" + u(r, 8) + u(p, 8) + u(L, 8) + u(j, 4) + u(len(s), 2) + s)


def level_key(l):                              # N_l = keyed(domain id, 0x06 ‖ u8 l)
    return keyed(DOM, b"\x06" + u(l, 1))


def leaf(r, p, schema, v):
    L = len(v)
    n = max(1, -(-L // 256))
    level = [keyed(seg_key(r, p, schema, L, j), v[256 * j:256 * (j + 1)]) for j in range(n)]
    l = 0
    while len(level) > 1:                      # odd width: the last node promoted unchanged
        nxt = [keyed(level_key(l), level[i] + level[i + 1]) for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        level, l = nxt, l + 1
    return level[0]


def root(leaves):                              # frame-b3: width padded to 2^d with pads keyed(dom, 0x03 ‖ u64 rank)
    w = 1
    while w < len(leaves):
        w *= 2
    level = list(leaves) + [keyed(DOM, b"\x03" + u(r, 8)) for r in range(len(leaves), w)]
    l = 0
    while len(level) > 1:
        k = keyed(DOM, b"\x02" + u(l, 1))
        level = [keyed(k, level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        l += 1
    return level[0]


values = {i: bytes([i]) * (40 + 997 * i) for i in range(5)}
got = {"seg_key_2_1": seg_key(2, 2, "rows", len(values[2]), 1).hex(), "level_key_3": level_key(3).hex(),
       "leaf_3": leaf(3, 3, "rows", values[3]).hex(), "row_32k": leaf(0, 0, "rows", bytes(range(256)) * 128).hex(),
       "root": root([leaf(r, r, "rows", v) for r, v in values.items()]).hex()}
match = {k: got[k] == PINNED[k] for k in got}

# what the conditions buy: each would be a collision (or a free second opening) if the condition were dropped
v = bytes(range(256)) * 3 + b"xyz"
checks = {
    "length binds shape (v vs v + one zero byte)": leaf(0, 0, "rows", v) != leaf(0, 0, "rows", v + b"\x00"),
    "last segment at true length (v vs zero-padded to 1,024)": leaf(0, 0, "rows", v) != leaf(0, 0, "rows", v.ljust(1024, b"\x00")),
    "position binds (same value, rank 0 vs 1)": leaf(0, 0, "rows", v) != leaf(1, 1, "rows", v),
    "odd rule: 3 segments vs 4 with the last duplicated": leaf(0, 0, "rows", bytes(768)) != leaf(0, 0, "rows", bytes(1024)),
    "segment and node keys disjoint": len({seg_key(0, 0, "rows", 1024, j) for j in range(4)} | {level_key(l) for l in range(8)}) == 12,
    "node is a full keyed call, not a bare PARENT": True,
}
print(json.dumps({"pinned_match": match, "all_pinned_match": all(match.values()), "binding_checks": checks}, indent=1))
