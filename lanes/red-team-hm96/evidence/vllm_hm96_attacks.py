"""red-team-hm96: attacks on the vLLM host committer's opt-in hm96-sha256/v1 leaves, and the default path's byte identity.

    python vllm_hm96_attacks.py identity OUT.json   # default-path fingerprint (run on base 2431e3c1 and head f1df809f; diff)
    python vllm_hm96_attacks.py attacks             # hm96 negatives, freshness, cross-run, range openings (head only)
    python vllm_hm96_attacks.py failopen            # hm96 committer + commit_block_offline (needs torch): unsalted leaves verify

RT_NO_TORCH=1 blocks `import torch` so base and head run the same offline core.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys

if os.environ.get("RT_NO_TORCH") == "1":
    sys.modules["torch"] = None  # type: ignore[assignment]

from verity_vllm.acquire.committer_api import Opening  # noqa: E402
from verity_vllm.commit import scheme  # noqa: E402
from verity_vllm.commit.committer.native_host import NativeHostCommitter, TensorMeta, _StepJob  # noqa: E402
from verity_vllm.commit.native_ranges import RangeOpening  # noqa: E402

H = lambda b: hashlib.sha256(b).digest()  # noqa: E731
PROGRAM = H(b"rt-hm96/program")
FAIL: list[str] = []
N = 0


def check(cond: bool, what: str) -> None:
    global N
    N += 1
    if not cond:
        FAIL.append(what)
        print("FAIL", what, flush=True)


def stream(seed: int, steps: int = 3, tensors: int = 4, nbytes: int = 700, dup: bool = False) -> list[list[tuple[str, bytes]]]:
    rng = random.Random(seed)
    out = []
    for _ in range(steps):
        ts = [(f"layer{k}.op", rng.randbytes(nbytes + 13 * k)) for k in range(tensors)]
        if dup:                                   # repeated identical values: an unsalted leaf leaks their equality
            ts.append(("dup.a", b"\x07" * 64))
            ts.append(("dup.b", b"\x07" * 64))
        out.append(ts)
    return out


class _Ev:
    def synchronize(self) -> None:
        return None


def commit_packed(c: NativeHostCommitter, steps: list) -> object:
    """The packed step stream (4-B aligned, as online) through `_commit_step`, every step, then `finalize()`."""
    c.reset()
    for tensors in steps:
        job = _StepJob(c._step_index, [], _Ev())
        c._step_index += 1
        buf = bytearray()
        for k, (name, raw) in enumerate(tensors):
            off = (len(buf) + 3) // 4 * 4
            buf.extend(b"\0" * (off - len(buf)))
            m = TensorMeta(k, name, "uint8", (len(raw),), len(raw), c.chunk, 0, 0)
            m.stream_off = off
            job.metas.append(m)
            buf.extend(raw)
        mv = memoryview(bytes(buf))
        for m in job.metas:
            m.host = mv[m.stream_off:m.stream_off + m.nbytes]
        job.stream = mv
        c._cur = None
        c._commit_step(job)
    return c.finalize()


def make(chunk: int, threads: int = 1, run_id: str = "rt-hm96", **kw) -> NativeHostCommitter:
    return NativeHostCommitter(None, run_id=run_id, chunk=chunk, hash_threads=threads, program_digest=PROGRAM, **kw)


def in_tensor_ranges(c: NativeHostCommitter, step: int) -> list[tuple[int, int]]:
    """Ranges a per-tensor step can open (inside one tensor), or across the packed stream."""
    if step in c._streams:
        n = len(c._levels[step][0])
        return [(1, n - 1)] if n >= 3 else []
    return [(m.first_leaf, m.first_leaf + m.n_leaves) for m in c._layouts[step] if m.n_leaves >= 2]


def fingerprint(c: NativeHostCommitter, run) -> dict:
    ops, ranges = [], []
    for s in run.steps:
        for o in c.open([(s.step, i) for i in range(s.n_leaves)]):
            ops.append(H(json.dumps([o.step, o.index, o.value.hex(), [None if p is None else p.hex() for p in o.path], o.identity],
                                    sort_keys=True).encode()).hex())
            check(c.verify(run, o), f"default opening verifies {s.step}/{o.index}")
        for lo, hi in in_tensor_ranges(c, s.step):
            ro = c.open_range(s.step, lo, hi)
            ranges.append(H(json.dumps([ro.step, ro.lo, ro.hi, ro.value.hex(), [[None if x is None else x.hex() for x in p] for p in ro.path]]).encode()).hex())
            check(c.verify_range(run, ro), f"default range verifies {s.step}")
    return {
        "name": c.name,
        "run_root": run.run_root.hex(),
        "steps": [[s.step, s.root.hex(), s.merkle_root.hex(), s.n_leaves, s.n_bytes, s.layout_digest.hex()] for s in run.steps],
        "levels": H(b"".join(d for lv in c._levels.values() for level in lv for d in level)).hex(),
        "ctx0": c._ctx_digest(0).hex(),
        "openings": H("".join(ops).encode()).hex(),
        "ranges": H("".join(ranges).encode()).hex(),
        "persistent_bytes": run.persistent_bytes,
        "extra_keys": sorted(k for k in run.extra),
    }


def identity(out: str) -> int:
    rec = {}
    for chunk in (64, 4096):
        for threads in (1, 2):
            c = make(chunk, threads)
            rec[f"tensor/c{chunk}/t{threads}"] = fingerprint(c, c.commit_offline(stream(11, nbytes=5000 if chunk == 4096 else 700)))
        c = make(chunk)
        rec[f"packed/c{chunk}"] = fingerprint(c, commit_packed(c, stream(12, nbytes=5000 if chunk == 4096 else 700)))
    rec["_checks"] = {"n": N, "failed": FAIL}
    open(out, "w").write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps(rec["_checks"]))
    return 1 if FAIL else 0


def op(o: Opening, **kw) -> Opening:
    d = {"step": o.step, "index": o.index, "value": o.value, "path": o.path, "identity": o.identity, "salt": o.salt}
    d.update(kw)
    return Opening(d["step"], d["index"], d["value"], d["path"], d["identity"], d["salt"])


def attacks() -> int:
    from verity.commitments import hm96
    from verity_vllm.commit import hiding

    NAME = hiding.NAME
    # --- the salts are exactly what os.urandom returned, one call per step, and nothing else draws randomness
    calls: list[bytes] = []
    real = hiding.os.urandom

    def rec(n: int) -> bytes:
        b = real(n)
        calls.append(b)
        return b

    hiding.os.urandom = rec
    try:
        c = make(64, leaf_scheme=NAME)
        st = stream(21, dup=True)
        run = c.commit_offline(st)
    finally:
        hiding.os.urandom = real
    check(len(calls) == len(run.steps), f"one os.urandom call per step ({len(calls)} for {len(run.steps)})")
    check(all(c._salts[s.step] == calls[s.step] for s in run.steps), "retained salts are the os.urandom bytes verbatim")
    check(all(len(c._salts[s.step]) == 128 * s.n_leaves for s in run.steps), "128 salt bytes per leaf")
    salts = [c._salts[s.step][128 * i:128 * (i + 1)] for s in run.steps for i in range(s.n_leaves)]
    check(len(set(salts)) == len(salts), "every salt distinct within a run")
    check(run.extra["salt_bytes"] == 128 * sum(s.n_leaves for s in run.steps), "salt_bytes counted")
    # hiding sanity: identical values at two positions give different tree leaves under hm96 (equal under vllm-v1)
    for s in run.steps:
        ident = [c.identity_of(s.step, i) for i in range(s.n_leaves)]
        da = next(i for i, d in enumerate(ident) if d["name"] == "dup.a")
        db = next(i for i, d in enumerate(ident) if d["name"] == "dup.b")
        lv0 = c._levels[s.step][0]
        check(lv0[da] != lv0[db], f"equal values -> distinct hm96 leaves (step {s.step})")
    plain = make(64)
    prun = plain.commit_offline(st)
    for s in prun.steps:
        ident = [plain.identity_of(s.step, i) for i in range(s.n_leaves)]
        da = next(i for i, d in enumerate(ident) if d["name"] == "dup.a")
        db = next(i for i, d in enumerate(ident) if d["name"] == "dup.b")
        check(plain._levels[s.step][0][da] == plain._levels[s.step][0][db], "control: vllm-v1 leaves of equal values are equal")
    # the tree leaf is the core reference's hm96 leaf over pos_leaf; no unsalted digest is retained in the levels
    for s in run.steps:
        for i in range(s.n_leaves):
            o = c.open([(s.step, i)])[0]
            ref = hm96.tree_leaf(hm96.DEFAULT_KEY, hm96.commit_string(hm96.DEFAULT_KEY, scheme.pos_leaf(o.value), o.salt))
            check(c._levels[s.step][0][i] == ref, f"level-0 leaf = core hm96 leaf {s.step}/{i}")
            check(c._levels[s.step][0][i] != scheme.pos_leaf(o.value), "level 0 holds no unsalted pos_leaf")
    # retry / re-commit on the same committer: fresh salts, old openings no longer verify against the new run
    old = {s.step: c._salts[s.step] for s in run.steps}
    old_op = c.open([(1, 3)])[0]
    run2 = c.commit_offline(st)
    check(all(c._salts[s.step] != old[s.step] for s in run2.steps), "re-commit draws fresh salts for every step")
    check(not c.verify(run2, old_op), "an opening of the first commit does not verify against the re-commit")
    check(run2.run_root != run.run_root, "re-commit of the same stream has a new run root")
    run = run2

    # --- point openings: every negative in the brief
    s = run.steps[1]
    o = c.open([(1, 3)])[0]
    o5 = c.open([(1, 5)])[0]
    check(c.verify(run, o), "honest opening verifies")
    for t in (0, 1, 7, 8, 511, 1023):
        y = bytearray(o.salt)
        y[t >> 3] ^= 1 << (t & 7)
        check(not c.verify(run, op(o, salt=bytes(y))), f"wrong nonce: salt bit {t}")
    check(not c.verify(run, op(o, salt=hm96.fresh_salt())), "wrong nonce: fresh salt")
    check(not c.verify(run, op(o, salt=bytes(128))), "wrong nonce: zero salt")
    check(not c.verify(run, op(o, value=o5.value, salt=o5.salt)), "swapped leaf: value+salt of 5 at 3")
    check(not c.verify(run, op(o, value=o5.value, salt=o5.salt, path=o5.path)), "swapped leaf: value+salt+path of 5 at 3")
    check(not c.verify(run, op(o5, index=3)), "swapped leaf: opening 5 relabelled as 3")
    check(not c.verify(run, op(o, salt=o5.salt)), "randomness of a different position (same step)")
    o_other_step = c.open([(2, 3)])[0]
    check(not c.verify(run, op(o, salt=o_other_step.salt)), "randomness of the same index in another step")
    check(not c.verify(run, op(o, salt=o.salt[:127])), "truncated opening: 127-byte salt")
    check(not c.verify(run, op(o, salt=b"")), "truncated opening: no salt")
    check(not c.verify(run, op(o, salt=o.salt + b"\0")), "over-long salt: 129 bytes")
    check(not c.verify(run, op(o, salt=o.salt + o5.salt)), "two salts on one opening")
    check(not c.verify(run, op(o, value=o.value[:-1])), "truncated opening: value short by one")
    check(not c.verify(run, op(o, path=o.path[:-1])), "truncated opening: path short by one level")
    # length-extension-style substitution: value || md-pad || ext (the SHA-256 continuation) and value/salt boundary shifts
    L = 26 + len(o.value)
    pad = b"\x80" + b"\0" * ((55 - L) % 64) + (8 * L).to_bytes(8, "big")
    check(not c.verify(run, op(o, value=o.value + pad + b"ext")), "length extension: value || pad || ext")
    check(not c.verify(run, op(o, value=o.value + o.salt[:1], salt=o.salt[1:])), "boundary shift: one salt byte moved into the value")
    check(not c.verify(run, op(o, value=o.value[:-1], salt=o.value[-1:] + o.salt[:-1])), "boundary shift: one value byte moved into the salt")
    # mixed rules: a salt-less (vllm-v1) opening at an hm96 committer, an hm96 opening at a vllm-v1 committer
    plain = make(64)
    prun = plain.commit_offline(st)
    po = plain.open([(1, 3)])[0]
    check(po.salt == b"" and plain.verify(prun, po), "control: vllm-v1 opening verifies")
    check(not c.verify(run, op(po)), "vllm-v1 opening against the hm96 run")
    check(not plain.verify(prun, op(po, salt=o.salt)), "salt on a vllm-v1 opening refused")
    check(not plain.verify(run, op(o)), "hm96 opening verified by a vllm-v1 verifier against the hm96 run")
    check(not plain.verify(run, op(o, salt=b"")), "hm96 opening, salt stripped, vllm-v1 verifier, hm96 run")
    # cross-run: same run_id, same program, same stream, two committers
    c2 = make(64, leaf_scheme=NAME)
    runb = c2.commit_offline(st)
    ob = c2.open([(1, 3)])[0]
    check(ob.value == o.value and ob.salt != o.salt, "cross-run: same value, independent salt")
    check(not c.verify(run, ob), "cross-run: run B's opening against run A (same run_id)")
    check(not c.verify(run, op(o, salt=ob.salt)), "cross-run: run B's salt at run A")
    check(all(a.root != b.root for a, b in zip(run.steps, runb.steps)), "cross-run: every step root differs")
    c3 = make(64, run_id="rt-hm96-other", leaf_scheme=NAME)
    runc = c3.commit_offline(st)
    check(not c.verify(run, c3.open([(1, 3)])[0]) and not c3.verify(runc, o), "cross-run: different run_id both ways")
    # another key: an hm96 committer built with a different key (patched in) must not accept key-A openings
    ck = make(64, leaf_scheme=NAME)
    ck.commit_offline(st)
    ck._layouts = c._layouts
    ck.hiding = hiding.HidingLeaves(hm96.fresh_key())
    ck._leaf_ctx = c._leaf_ctx                      # the same step-root context: only the leaf rule's key differs
    check(not ck.verify(run, o), "an opening does not verify under a different key's rule")
    ck.hiding = c.hiding
    check(ck.verify(run, o), "control: the same verifier with the committing key accepts")

    # --- range openings
    ro = c.open_range(2, 2, 9)
    check(ro is not None and len(ro.salts) == 7 * 128 and c.verify_range(run, ro), "honest range verifies")
    sl = [ro.salts[128 * k:128 * (k + 1)] for k in range(7)]
    sw = sl[:]
    sw[1], sw[4] = sw[4], sw[1]
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, b"".join(sw))), "range: two salts swapped")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, b"".join(sl[1:] + sl[:1]))), "range: salts rotated")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, ro.salts[:-1])), "range: salts short by a byte")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, ro.salts[:-128])), "range: one salt missing")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, ro.salts + hm96.fresh_salt())), "range: extra salt")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value + ro.salts[:1], ro.path, ro.salts[1:])), "range: boundary shift")
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path)), "range: no salts")
    ro_other = c.open_range(2, 3, 10)
    check(not c.verify_range(run, RangeOpening(ro.step, ro.lo, ro.hi, ro.value, ro.path, ro_other.salts)), "range: salts of a shifted range")
    rob = c2.open_range(2, 2, 9)
    check(not c.verify_range(run, rob), "range: run B's range against run A")
    check(not plain.verify_range(prun, RangeOpening(ro.step, ro.lo, ro.hi, plain.open_range(2, 2, 9).value, plain.open_range(2, 2, 9).path, ro.salts)),
          "range: salts on a vllm-v1 range refused")
    # --- packed mode under hm96: salted too, openings verify, negatives fail
    cp = make(64, leaf_scheme=NAME)
    runp = commit_packed(cp, stream(22))
    check(all(len(cp._salts[s.step]) == 128 * s.n_leaves for s in runp.steps), "packed: 128 salt bytes per leaf")
    opp = cp.open([(0, 2)])[0]
    check(cp.verify(runp, opp) and not cp.verify(runp, op(opp, salt=hm96.fresh_salt())), "packed: opening verifies, wrong salt fails")
    rop = cp.open_range(1, 1, 6)
    check(cp.verify_range(runp, rop) and not cp.verify_range(runp, RangeOpening(rop.step, rop.lo, rop.hi, rop.value, rop.path)),
          "packed: range verifies, salt-less range fails")
    # --- hash_threads > 1 (the pool path) is salted after the pool
    ct = make(64, threads=2, leaf_scheme=NAME)
    runt = ct.commit_offline(stream(23))
    check(all(len(ct._salts[s.step]) == 128 * s.n_leaves for s in runt.steps) and ct.verify(runt, ct.open([(0, 1)])[0]), "threads=2 salted")
    # --- refusals
    for kw in ({"gpu_tree": True}, ):
        try:
            make(64, leaf_scheme=NAME, **kw)
            check(False, f"refused {kw}")
        except ValueError:
            check(True, "")
    print(json.dumps({"n": N, "failed": FAIL}))
    return 1 if FAIL else 0


def failopen() -> int:
    """An hm96 committer (gpu_tree off, so the switch accepts it) that commits a step through `commit_block_offline` (the CPU
    reference of the chunk tree): the step's leaves are unsalted chunk leaves, yet the step root binds the hm96 scheme digest,
    and openings verify with no salt or any salt.  The same shape as NativeCollectCommitter(gpu_tree=False, native_worker=True)."""
    from verity_vllm.commit import hiding

    os.environ["VERITY_RETAIN"] = "host"                    # as tests/commit/test_openings_after_release.py (no CUDA)
    c = make(256, leaf_scheme=hiding.NAME)                   # gpu_tree=False: the switch accepts hm96
    del os.environ["VERITY_RETAIN"]
    stream_ = bytes(random.Random(5).randbytes(256 * 6 - 40))
    metas = [TensorMeta(0, "layer0.op", "uint8", (len(stream_),), len(stream_), 256, 0, 6)]
    metas[0].dev_off = 0
    c.commit_block_offline(0, stream_, metas)
    run = c.finalize()
    o = c.open([(0, 2)])[0]
    res = {
        "committer_leaf_scheme": c.leaf_scheme,
        "extra_leaf_scheme": run.extra.get("leaf_scheme"),
        "extra_salt_bytes": run.extra.get("salt_bytes"),
        "ctx_binds_hm96": c._ctx_digest(0) == H(f"{c.run_id}/step=0".encode() + b"/leaf=" + c.hiding.digest),
        "opening_salt_len": len(o.salt),
        "verifies_without_salt": c.verify(run, o),
        "verifies_with_garbage_salt": c.verify(run, op(o, salt=b"\x01" * 128)),
        "step_salted": 0 in c._salts,
        "leaf_is_unsalted_chunk_leaf": c._leaf_digests_of(0)[2] == scheme.chunk_leaf(
            scheme.chunk_header(c._gpu_layout(0, len(c._leaf_digests_of(0)) * 256 // 4), 0, 2, 256 // 4, c.GPU_TREE_SRC), o.value),
    }
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "identity":
        raise SystemExit(identity(sys.argv[2]))
    if what == "attacks":
        raise SystemExit(attacks())
    raise SystemExit(failopen())
