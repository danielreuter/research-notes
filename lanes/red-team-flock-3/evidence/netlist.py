"""red-team-flock-3: an independent reader and evaluator of `flock-ir-unit/v2` netlist text (not the producer's parser).

Row i of the block R1CS is (XOR_{j in A_i} z_j) * (XOR_{j in B_i} z_j) = z_i (C = I). Input rows are A = B = [i]; the constant
row is pinned to 1; an assertion row (B = [const], i in A) forces XOR_{A_i \\ i} = 0. `Net.eval` evaluates lanes bit-sliced
(numpy uint64, 64 lanes per word) and reports, per lane, whether every row is satisfied.
"""
import hashlib
import json

import numpy as np

WORD = 128


class Net:
    def __init__(self, text: str):
        self.text = text
        self.sha256 = hashlib.sha256(text.encode()).hexdigest()
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        h = lines[0].split()
        assert h[0] == "flock-ir-unit/v2", h[0]
        self.name, self.useful, self.const = h[1], int(h[2]), int(h[3])
        at = 4

        def groups():
            nonlocal at
            n = int(h[at]); at += 1
            out = []
            for _ in range(n):
                col, words, np_ = int(h[at]), int(h[at + 1]), int(h[at + 2])
                bits = [int(x) for x in h[at + 3: at + 3 + np_]]
                at += 3 + np_
                out.append({"col": col, "words": words, "bits": bits})
            return out
        self.in_groups, self.out_groups = groups(), groups()
        assert at == len(h), "header has trailing fields"
        self.in_words = self.in_groups[-1]["col"] + self.in_groups[-1]["words"]
        self.A, self.B = [], []
        for i in range(self.useful):
            v = [int(x) for x in lines[1 + i].split()]
            na = v[0]; nb = v[1 + na]
            assert len(v) == 2 + na + nb, f"row {i} length"
            self.A.append(v[1:1 + na]); self.B.append(v[2 + na:2 + na + nb])
        rest = lines[1 + self.useful:]
        self.leaves = self.cut = None
        for ln in rest:
            if ln.startswith("LEAVES "):
                assert self.leaves is None and self.cut is None
                self.leaves = json.loads(ln[7:])
            elif ln.startswith("CUT "):
                assert self.cut is None
                self.cut = json.loads(ln[4:])
            else:
                raise AssertionError(f"unexpected trailing line {ln[:40]!r}")
        self._check()

    def _check(self):
        """Topological order, no free rows; classify rows."""
        first = self.in_words * WORD
        self.inputs = [i for i in range(first) if self.A[i] == [i] and self.B[i] == [i]]
        for i in range(first):
            assert (self.A[i] == [i] and self.B[i] == [i]) or (not self.A[i] and not self.B[i]), f"row {i} in the input region"
        assert self.const == self.useful - 1 and self.A[self.const] == [self.const] and self.B[self.const] == [self.const]
        self.assertions = []
        for i in range(first, self.useful):
            if i == self.const:
                continue
            assertion = self.B[i] == [self.const] and i in self.A[i]
            if assertion:
                self.assertions.append(i)
            for c in self.A[i] + self.B[i]:
                assert c < i or c == self.const or (assertion and c == i), f"row {i} reads {c}"
            assert not (self.A[i] == [i] and self.B[i] == [i]), f"free row {i}"

    def port_cols(self, group):
        cols, c = [], group["col"] * WORD
        for b in group["bits"]:
            cols.append(c); c += b
        return cols

    def eval(self, inputs):
        """inputs: dict col -> uint64 array (packed lanes) for each input column; returns (z list, sat mask)."""
        n = len(next(iter(inputs.values())))
        zero = np.zeros(n, dtype=np.uint64)
        ones = np.full(n, np.uint64(0xFFFFFFFFFFFFFFFF))
        z = [None] * self.useful
        first = self.in_words * WORD
        for i in range(first):
            z[i] = inputs.get(i, zero) if self.A[i] == [i] else zero
        z[self.const] = ones
        sat = ones.copy()
        for i in range(first, self.useful):
            if i == self.const:
                continue
            if i in self._aset:
                x = zero.copy()
                for c in self.A[i]:
                    if c != i:
                        x ^= z[c]
                sat &= ~x
                z[i] = zero
                continue
            A, B = self.A[i], self.B[i]
            x = z[A[0]].copy() if A else zero.copy()
            for c in A[1:]:
                x ^= z[c]
            if B == [self.const]:
                z[i] = x
                continue
            y = z[B[0]].copy() if B else zero.copy()
            for c in B[1:]:
                y ^= z[c]
            z[i] = x & y
        return z, sat

    @property
    def _aset(self):
        if not hasattr(self, "_as"):
            self._as = set(self.assertions)
        return self._as


def pack_words(vals, bits):
    """vals: uint64 array of L lanes (words of `bits` bits) -> list of `bits` packed uint64 arrays (ceil(L/64))."""
    vals = np.asarray(vals, dtype=np.uint64)
    L = len(vals)
    W = (L + 63) // 64
    pad = np.zeros(W * 64, dtype=np.uint64); pad[:L] = vals
    lanes = pad.reshape(W, 64)
    sh = np.arange(64, dtype=np.uint64)
    out = []
    for t in range(bits):
        b = (lanes >> np.uint64(t)) & np.uint64(1)
        out.append(np.bitwise_or.reduce(b << sh, axis=1).astype(np.uint64))
    return out


def unpack_word(zs, L):
    """list of packed uint64 arrays (bit t) -> uint64 array of L lane values."""
    W = len(zs[0])
    sh = np.arange(64, dtype=np.uint64)
    out = np.zeros(W * 64, dtype=np.uint64)
    for t, z in enumerate(zs):
        bits = ((z[:, None] >> sh[None, :]) & np.uint64(1)).reshape(-1)
        out |= bits << np.uint64(t)
    return out[:L]


def unpack_mask(m, L):
    sh = np.arange(64, dtype=np.uint64)
    return ((m[:, None] >> sh[None, :]) & np.uint64(1)).reshape(-1)[:L].astype(bool)


class TcUnit:
    """The attention tensor-core step unit: b (16 x 16-bit leaves, group 0), a (16 x 16-bit) and acc (32-bit) cut ports (group 1),
    result (32-bit) in the output group."""

    def __init__(self, net: Net):
        self.net = net
        g0, g1 = net.in_groups
        assert g0["bits"] == [16] * 16 and g1["bits"] == [16] * 16 + [32], (g0, g1)
        assert len(net.out_groups) == 1 and net.out_groups[0]["bits"] == [32]
        self.b_cols, self.ac_cols = net.port_cols(g0), net.port_cols(g1)
        self.out_col = net.out_groups[0]["col"] * WORD

    def __call__(self, acc, a, b):
        """acc: (L,) u32; a, b: (L, 16) u16 -> (result (L,) u32, sat (L,) bool)."""
        L = len(acc)
        inp = {}
        for j in range(16):
            for t, p in enumerate(pack_words(b[:, j], 16)):
                inp[self.b_cols[j] + t] = p
            for t, p in enumerate(pack_words(a[:, j], 16)):
                inp[self.ac_cols[j] + t] = p
        for t, p in enumerate(pack_words(acc, 32)):
            inp[self.ac_cols[16] + t] = p
        z, sat = self.net.eval(inp)
        res = unpack_word([z[self.out_col + t] for t in range(32)], L)
        return res.astype(np.uint64), unpack_mask(sat, L)
