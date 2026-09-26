"""red-team-hm96 (PR #93): negatives against the SHA-512 schemes' reference verifiers and the vLLM gate (head cd00f704).

    python negatives_sha512.py      # prints {"n": ..., "failed": [...]}; exit 1 on a failed expectation
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

from verity.commitments import hm96, vllm_v1 as V
from verity.commitments.frame_v3 import FrameV3, Port, RowLeaf
from verity.commitments.indexed import RangeIndexedDomain
from verity.commitments.merkle import CommitmentDomain, MerkleTree, verify_opening, Commitment
from verity.commitments.multiproof import multiproof, verify_multiproof
from verity.commitments.rowleaf import ROLE_X, sha512_row_layout, sha256_row_layout

FAIL: list[str] = []
N = 0


def check(cond: bool, what: str) -> None:
    global N
    N += 1
    if not cond:
        FAIL.append(what)
        print("FAIL", what, flush=True)


def raises(fn, what: str, exc=Exception) -> None:
    try:
        fn()
    except exc:
        check(True, what)
        return
    check(False, what + " (accepted)")


S5 = lambda b: hashlib.sha512(b).digest()  # noqa: E731
BIND = hashlib.sha256(b"rt93/binding").digest()


def dom(n: int, h: str, binding: bytes = BIND) -> CommitmentDomain:
    return CommitmentDomain(binding, 0, RangeIndexedDomain(n), hash=h)


def frame() -> None:
    d5, d2 = dom(6, "sha512"), dom(6, "sha256")
    raises(lambda: FrameV3({"r": Port(d5, RowLeaf("sha256", ROLE_X, 16, 8))}), "frame: SHA-512 frame refuses a sha256/row/v1 port", ValueError)
    raises(lambda: FrameV3({"r": Port(d5, RowLeaf("blake3", ROLE_X, 16, 8))}), "frame: SHA-512 frame refuses a BLAKE3 row port", ValueError)
    raises(lambda: FrameV3({"r": Port(d2, RowLeaf("sha512", ROLE_X, 16, 8))}), "frame: SHA-256 frame refuses a sha512/row/v1 port", ValueError)
    raises(lambda: FrameV3({"a": Port(d5, RowLeaf("sha512", ROLE_X, 16, 8)), "b": Port(d2, RowLeaf("sha256", ROLE_X, 16, 8))}),
           "frame: one configuration, one frame hash", ValueError)
    raises(lambda: CommitmentDomain(BIND, 0, RangeIndexedDomain(3), hash="sha384"), "frame: an unknown frame hash is refused", ValueError)
    check(d5.domain_id != d2.domain_id and len(d5.domain_id) == 64 and len(d2.domain_id) == 32, "frame: SHA-512 and SHA-256 domain ids differ")
    s5 = FrameV3({"r": Port(d5, RowLeaf("sha512", ROLE_X, 16, 8))})
    s2 = FrameV3({"r": Port(d2, RowLeaf("sha256", ROLE_X, 16, 8))})
    rows = [os.urandom(16) for _ in range(6)]
    lv5 = [s5.tree_leaf("r", i, s5.leaf_layout("r", i).digest(v)) for i, v in enumerate(rows)]
    lv2 = [s2.tree_leaf("r", i, s2.leaf_layout("r", i).digest(v)) for i, v in enumerate(rows)]
    r5, r2 = s5.root("r", lv5), s2.root("r", lv2)
    p5, p2 = s5.path("r", lv5, 3), s2.path("r", lv2, 3)
    check(s5.verify_path("r", r5, 6, 3, lv5[3], p5), "frame: honest SHA-512 path verifies")
    check(not s5.verify_path("r", r5, 6, 3, lv5[3][:32], p5), "frame: a 32-byte leaf under the SHA-512 frame")
    check(not s5.verify_path("r", r5, 6, 3, lv5[3], tuple(p[:32] for p in p5)), "frame: truncated 32-byte siblings under SHA-512")
    check(not s5.verify_path("r", r2, 6, 3, lv2[3], p2), "frame: a SHA-256 root/leaf/path under the SHA-512 verifier")
    check(not s2.verify_path("r", r5[:32], 6, 3, lv5[3][:32], tuple(p[:32] for p in p5)), "frame: SHA-512 digests truncated, SHA-256 verifier")
    check(not s2.verify_path("r", r5, 6, 3, lv5[3], p5), "frame: SHA-512 opening under the SHA-256 verifier")
    raises(lambda: s5.tree_leaf("r", 0, bytes(32)), "frame: a 32-byte row digest under sha512/row/v1", ValueError)
    raises(lambda: s2.tree_leaf("r", 0, bytes(64)), "frame: a 64-byte row digest under sha256/row/v1", ValueError)
    # merkle.verify_opening and multiproofs over the SHA-512 domain
    from verity.commitments.limits import VerificationLimits
    from verity.commitments.merkle import Opening as MOpening

    lim = VerificationLimits()
    vals = {p: os.urandom(2) for p in range(6)}
    t5, t2 = MerkleTree(d5, vals, lambda _p: "u16"), MerkleTree(d2, vals, lambda _p: "u16")
    o5, o2 = t5.open(2), t2.open(2)
    check(verify_opening(d5, t5.commitment, o5, "u16", lim), "frame: honest merkle.verify_opening under SHA-512")
    check(verify_opening(d2, t2.commitment, o2, "u16", lim), "frame: control, SHA-256 opening verifies")
    check(not verify_opening(d5, t5.commitment, o2, "u16", lim), "frame: a SHA-256 opening against the SHA-512 commitment")
    check(not verify_opening(d2, t2.commitment, o5, "u16", lim), "frame: a SHA-512 opening against the SHA-256 commitment")
    check(not verify_opening(d5, Commitment(t5.commitment.root[:32], 6), o5, "u16", lim), "frame: a 32-byte root under the SHA-512 domain")
    check(not verify_opening(d5, t5.commitment, MOpening(2, o5.value, tuple(p[:32] for p in o5.path)), "u16", lim),
          "frame: 32-byte siblings under the SHA-512 domain")
    mixed = MOpening(2, o5.value, (o5.path[0][:32] + o5.path[0][:32],) + o5.path[1:])
    check(not verify_opening(d5, t5.commitment, mixed, "u16", lim), "frame: a doctored 64-byte sibling")
    check(not verify_opening(d5, t5.commitment, MOpening(2, bytes([o5.value[0] ^ 1]) + o5.value[1:], o5.path), "u16", lim),
          "frame: changed value")
    check(not verify_opening(dom(6, "sha512", hashlib.sha256(b"other").digest()), t5.commitment, o5, "u16", lim),
          "frame: another binding (cross-session)")
    ranks = [1, 4]
    mp5, mp2 = multiproof(t5, ranks), multiproof(t2, ranks)
    lf5 = {r: t5._levels[0][r] for r in ranks}
    lf2 = {r: t2._levels[0][r] for r in ranks}
    check(verify_multiproof(t5.commitment.root, 6, d5.domain_id, lf5, mp5, hash="sha512"), "frame: SHA-512 multiproof verifies with hash=sha512")
    check(not verify_multiproof(t5.commitment.root, 6, d5.domain_id, lf5, mp5), "frame: SHA-512 multiproof under the default SHA-256 fails")
    check(verify_multiproof(t2.commitment.root, 6, d2.domain_id, lf2, mp2), "frame: control, SHA-256 multiproof verifies")
    check(not verify_multiproof(t2.commitment.root, 6, d2.domain_id, lf2, mp2, hash="sha512"), "frame: SHA-256 multiproof under hash=sha512 fails")


def vllm() -> None:
    prog, ctx, geo, lay = (hashlib.sha256(x).digest() for x in (b"p", b"c", b"g", b"l"))
    d5 = V.StepDomain(prog, ctx, geo, lay, 5, hash="sha512")
    d2 = V.StepDomain(prog, ctx, geo, lay, 5)
    raises(lambda: V.VllmV1({"a": d5, "b": d2}, {"a": lambda i: 8, "b": lambda i: 8}), "vllm: one configuration, one hash", Exception)
    s5 = V.VllmV1({"v": d5}, {"v": lambda i: 8})
    s2 = V.VllmV1({"v": d2}, {"v": lambda i: 8})
    check(s5.name == "vllm-v1-sha512" and s2.name == "vllm-v1", "vllm: names")
    vals = [os.urandom(8) for _ in range(5)]
    l5 = [d5.leaf(i, v) for i, v in enumerate(vals)]
    l2 = [d2.leaf(i, v) for i, v in enumerate(vals)]
    r5, r2 = s5.root("v", l5), s2.root("v", l2)
    p5, p2 = s5.path("v", l5, 2), s2.path("v", l2, 2)
    check(V.verify(d5, r5, 2, l5[2], p5), "vllm: honest SHA-512 opening")
    check(not V.verify(d5, r5, 2, l2[2], p2), "vllm: SHA-256 leaf and path under the SHA-512 domain")
    check(not V.verify(d2, r2, 2, l5[2], p5), "vllm: SHA-512 leaf and path under the SHA-256 domain")
    check(not V.verify(d2, r5[:32], 2, l5[2][:32], tuple(None if p is None else p[:32] for p in p5)), "vllm: truncated SHA-512 digests under SHA-256")
    check(not V.verify(d5, r5, 2, l5[2], tuple(None if p is None else p[:32] for p in p5)), "vllm: 32-byte siblings under SHA-512")
    check(not V.verify(d5, r5, 2, d5.leaf(2, bytes([vals[2][0] ^ 1]) + vals[2][1:]), p5), "vllm: changed value")
    check(not V.verify(d5, r5, 3, l5[2], p5), "vllm: moved index")
    check(not s5.verify_path("v", r5, 5, 2, l5[2], p2), "vllm: VllmV1.verify_path with a SHA-256 path")
    check(V.domain_digest(d5) != V.domain_digest(d2), "vllm: SHA-512 and SHA-256 domain digests differ")
    raises(lambda: V.step_root(prog, ctx, geo, lay, 5, r5[:32], hash="sha512"), "vllm: 32-byte tree root in a SHA-512 step binding", Exception)
    raises(lambda: V.step_root(prog, ctx, geo, lay, 5, bytes(64)), "vllm: 64-byte tree root in a SHA-256 step binding", Exception)


def hm96_neg() -> None:
    I5, I2 = hm96.SHA512, hm96.SHA256
    K5, K2 = I5.default_key, I2.default_key
    raises(lambda: I5.check_key(K2), "hm96: a 160-byte (SHA-256) key under hm96-sha512", Exception)
    raises(lambda: I5.check_key(K5[:-1] + bytes([K5[-1] | 0x80])), "hm96: bit 2047 set is refused", Exception)
    raises(lambda: I2.check_key(K5), "hm96: a 256-byte key under hm96-sha256", Exception)
    raises(lambda: I5.salt_digest(os.urandom(128)), "hm96: a 128-byte salt under hm96-sha512", Exception)
    raises(lambda: I5.commit_string(K5, os.urandom(32), os.urandom(192)), "hm96: a 32-byte inner digest under hm96-sha512", Exception)
    raises(lambda: I5.tree_leaf(K5, os.urandom(64)), "hm96: a 64-byte commit string under hm96-sha512", Exception)
    raises(lambda: I2.tree_leaf(K2, os.urandom(128)), "hm96: a 128-byte commit string under hm96-sha256", Exception)
    raises(lambda: hm96.HidingLayout(V.pos_leaf_layout(8), K5, I5), "hm96: SHA-512 rule over a SHA-256 inner layout", Exception)
    raises(lambda: hm96.HidingLayout(sha512_row_layout(ROLE_X, 16, 4), K2, I2), "hm96: SHA-256 rule over a sha512/row/v1 layout", Exception)
    raises(lambda: hm96.HidingLayout(sha256_row_layout(ROLE_X, 16, 4), K5, I5), "hm96: SHA-512 rule over a sha256/row/v1 layout", Exception)
    prog = hashlib.sha256(b"p").digest()
    b2 = V.VllmV1({"v": V.StepDomain(prog, prog, prog, prog, 3)}, {"v": lambda i: 8})
    b5 = V.VllmV1({"v": V.StepDomain(prog, prog, prog, prog, 3, hash="sha512")}, {"v": lambda i: 8})
    raises(lambda: hm96.Hm96Sha512(b2), "hm96: Hm96Sha512 over a SHA-256 vllm-v1", TypeError)
    raises(lambda: hm96.Hm96Sha256(b5), "hm96: Hm96Sha256 over vllm-v1-sha512", TypeError)
    h5 = hm96.Hm96Sha512(b5)
    vals, salts = [os.urandom(8) for _ in range(3)], [I5.fresh_salt() for _ in range(3)]
    leaves = [h5.tree_leaf("v", i, h5.leaf_layout("v", i).commit(v, s)) for i, (v, s) in enumerate(zip(vals, salts))]
    root = h5.root("v", leaves)
    path = h5.path("v", leaves, 1)
    check(h5.verify_path("v", root, 3, 1, leaves[1], path), "hm96: honest hm96-sha512 opening over vllm-v1-sha512")
    check(not h5.verify_path("v", root, 3, 1, h5.tree_leaf("v", 1, h5.leaf_layout("v", 1).commit(vals[1], salts[2])), path),
          "hm96: another position's salt")
    check(not h5.verify_path("v", root, 3, 1, h5.tree_leaf("v", 1, h5.leaf_layout("v", 1).commit(vals[1], I5.fresh_salt())), path),
          "hm96: a fresh salt")
    # an hm96-sha256 leaf of the same (value, first 128 salt bytes) is never an hm96-sha512 leaf: sizes and tags differ
    x2 = V.pos_leaf(vals[1])
    l2 = I2.tree_leaf(K2, I2.commit_string(K2, x2, salts[1][:128]))
    check(len(l2) == 32 and not h5.verify_path("v", root, 3, 1, l2, path), "hm96: a SHA-256 hm96 leaf in the SHA-512 tree")
    check(I5.scheme_digest(K5) != I2.scheme_digest(K2) and len(I5.scheme_digest(K5)) == 64, "hm96: scheme digests differ (64 vs 32 bytes)")
    check(I5.statistical_distance_log2(1) == -256 and I5.statistical_distance_log2(1 << 64, key_failure_log2=64) == -128, "hm96: bound")
    # the setup claim exists and is what the spec cites
    from verity.claims import ENTRIES
    e = ENTRIES.get("hash-derived-key")
    check(e is not None and e.kind == "assumption", "claims: hash-derived-key is an assumption entry")
    check(all(k in ENTRIES for k in ("statistical-hiding", "common-reference-string")), "claims: statistical-hiding and common-reference-string exist")


def vllm_gate() -> None:
    try:
        from verity_vllm.commit import hiding
        from verity_vllm.commit.committer.native_host import NativeHostCommitter
    except Exception as e:  # noqa: BLE001
        check(False, f"vllm gate import: {e!r}")
        return
    raises(lambda: NativeHostCommitter(None, leaf_scheme="hm96-sha512/v1"), "vllm gate: the committer refuses hm96-sha512/v1", ValueError)
    h = hiding.HidingLeaves(instance=hm96.SHA512)
    raises(lambda: h.leaves_with([os.urandom(32) for _ in range(4)], os.urandom(4 * 192)), "vllm gate: SHA-512 batch path refuses 32-byte digests",
           Exception)
    raises(lambda: h.leaves_with([os.urandom(64) for _ in range(4)], os.urandom(4 * 128)), "vllm gate: SHA-512 batch path refuses 128-byte salts",
           Exception)
    c = NativeHostCommitter(None, run_id="rt93", chunk=64, hash_threads=1, program_digest=hashlib.sha256(b"p").digest(), leaf_scheme=hm96.NAME)
    check(c.hiding.instance is hm96.SHA256, "vllm gate: the hm96 committer is hm96-sha256/v1")


if __name__ == "__main__":
    if os.environ.get("RT_NO_TORCH") == "1":
        sys.modules["torch"] = None  # type: ignore[assignment]
    frame()
    vllm()
    hm96_neg()
    vllm_gate()
    print(json.dumps({"n": N, "failed": FAIL}))
    raise SystemExit(1 if FAIL else 0)
