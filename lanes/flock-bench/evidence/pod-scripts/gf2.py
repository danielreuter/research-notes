"""A tiny GF(2) R1CS circuit builder in Flock's model.

Wires are GF(2) linear forms over committed bits (inputs, AND outputs, hints). XOR/NOT are free; every AND of two
non-constant, non-trivially-related forms allocates one committed bit (one R1CS row A.z * B.z = z_i, C = I).
Counting is done on the live cone of the declared outputs and assertions, so unused gates cost nothing.

Evaluation is bit-sliced: every committed bit holds a T-bit Python int (one bit per test vector).
"""
from __future__ import annotations


class L:
    """A linear form: XOR of committed bits in `s` plus constant `c`."""

    __slots__ = ("s", "c")

    def __init__(self, s=frozenset(), c=0):
        self.s = s
        self.c = c

    def __xor__(self, o):
        return L(self.s ^ o.s, self.c ^ o.c)

    def inv(self):
        return L(self.s, self.c ^ 1)

    def is_const(self):
        return not self.s

    def key(self):
        return (self.s, self.c)


ZERO = L()
ONE = L(frozenset(), 1)


def const(b):
    return ONE if b else ZERO


class Circuit:
    def __init__(self):
        self.kind = []  # per committed bit: 'in' | 'and' | 'hint'
        self.data = []  # 'in': name; 'and': (a, b); 'hint': (fn, deps)
        self.inputs = {}
        self.outputs = {}
        self.asserts = []  # (name, L) that must evaluate to 0
        self.phase = "misc"
        self.phase_of = []

    # --- allocation -------------------------------------------------------------------------------------------
    def _new(self, kind, data):
        self.kind.append(kind)
        self.data.append(data)
        self.phase_of.append(self.phase)
        return L(frozenset((len(self.kind) - 1,)), 0)

    def input(self, name, n):
        bits = [self._new("in", f"{name}[{i}]") for i in range(n)]
        self.inputs[name] = bits
        return bits

    def AND(self, a, b):
        if a.is_const():
            return b if a.c else ZERO
        if b.is_const():
            return a if b.c else ZERO
        if a.s == b.s:
            return a if a.c == b.c else ZERO  # x.x = x ; x.(x+1) = 0
        return self._new("and", (a, b))

    def assert_zero(self, name, a):
        if a.is_const():
            assert a.c == 0, f"assertion {name} is constant 1"
            return
        self.asserts.append((name, a))

    def output(self, name, bits):
        self.outputs[name] = bits

    # --- liveness and counts -----------------------------------------------------------------------------------
    def live(self):
        seen = set()
        stack = []
        for bits in self.outputs.values():
            for w in bits:
                stack.extend(w.s)
        for _, w in self.asserts:
            stack.extend(w.s)
        for bits in self.inputs.values():
            for w in bits:
                stack.extend(w.s)
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            if self.kind[v] == "and":
                a, b = self.data[v]
                stack.extend(a.s)
                stack.extend(b.s)
        return seen

    def phase_counts(self):
        live = self.live()
        out = {}
        for v in live:
            if self.kind[v] == "and":
                out[self.phase_of[v]] = out.get(self.phase_of[v], 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    def counts(self):
        live = self.live()
        n_in = sum(1 for v in live if self.kind[v] == "in")
        n_and = sum(1 for v in live if self.kind[v] == "and")
        nnz = sum(len(self.data[v][0].s) + len(self.data[v][1].s) for v in live if self.kind[v] == "and")
        # outputs that are not already a single committed bit need one copy row each (IO slot materialisation)
        n_out_copy = sum(1 for bits in self.outputs.values() for w in bits if not (len(w.s) == 1 and w.c == 0))
        return {"inputs": n_in, "ands": n_and, "output_copies": n_out_copy, "asserts": len(self.asserts),
                "committed": n_in + n_and + n_out_copy, "nnz_AB": nnz}

    # --- bit-sliced evaluation ----------------------------------------------------------------------------------
    def evaluate(self, input_values, T):
        """input_values: name -> list of T-bit ints (one per input bit). Returns (outputs, assertion_fail_mask)."""
        mask = (1 << T) - 1
        val = [0] * len(self.kind)
        for name, bits in self.inputs.items():
            vs = input_values[name]
            for w, x in zip(bits, vs):
                (v,) = tuple(w.s)
                val[v] = x & mask

        def ev(w):
            x = mask if w.c else 0
            for v in w.s:
                x ^= val[v]
            return x

        for v, k in enumerate(self.kind):
            if k == "and":
                a, b = self.data[v]
                val[v] = ev(a) & ev(b)
        outs = {name: [ev(w) for w in bits] for name, bits in self.outputs.items()}
        fail = 0
        for _, w in self.asserts:
            fail |= ev(w)
        return outs, fail


# --- arithmetic helpers (little-endian bit lists) -------------------------------------------------------------

def NOT(a):
    return a.inv()


def OR(C, a, b):
    return a ^ b ^ C.AND(a, b)


def or_reduce(C, bits):
    bits = list(bits)
    if not bits:
        return ZERO
    while len(bits) > 1:
        nxt = []
        for i in range(0, len(bits) - 1, 2):
            nxt.append(OR(C, bits[i], bits[i + 1]))
        if len(bits) % 2:
            nxt.append(bits[-1])
        bits = nxt
    return bits[0]


def and_reduce(C, bits):
    bits = list(bits)
    if not bits:
        return ONE
    while len(bits) > 1:
        nxt = []
        for i in range(0, len(bits) - 1, 2):
            nxt.append(C.AND(bits[i], bits[i + 1]))
        if len(bits) % 2:
            nxt.append(bits[-1])
        bits = nxt
    return bits[0]


def maj(C, x, y, z):
    """Majority with one AND: maj = z + (x+z)(y+z); constants simplify."""
    consts = [w for w in (x, y, z) if w.is_const()]
    if len(consts) >= 2:
        vars_ = [w for w in (x, y, z) if not w.is_const()]
        s = sum(w.c for w in consts)
        if s == 0:
            return ZERO
        if s == 2:
            return ONE
        return vars_[0] if vars_ else const(sum(w.c for w in (x, y, z)) >= 2)
    return z ^ C.AND(x ^ z, y ^ z)


def mux(C, s, x, y):
    """s ? x : y, bitwise over equal-length lists."""
    return [yy ^ C.AND(s, xx ^ yy) for xx, yy in zip(x, y)]


def add(C, a, b, cin=ZERO, width=None, carry_out=False):
    n = width if width is not None else max(len(a), len(b))
    a = list(a) + [ZERO] * (n - len(a))
    b = list(b) + [ZERO] * (n - len(b))
    out = []
    c = cin
    for i in range(n):
        out.append(a[i] ^ b[i] ^ c)
        if i < n - 1 or carry_out:
            c = maj(C, a[i], b[i], c)
    if carry_out:
        out.append(c)
    return out


def sub(C, a, b, width):
    """(a - b) mod 2^width, and the borrow bit (1 iff a < b as unsigned width-bit numbers)."""
    a = list(a) + [ZERO] * (width - len(a))
    b = list(b) + [ZERO] * (width - len(b))
    s = add(C, a, [NOT(x) for x in b], ONE, width=width, carry_out=True)
    return s[:width], NOT(s[width])


def ge_const_free(C, a, b, width):
    """a >= b (unsigned, width bits): the carry out of a + ~b + 1."""
    _, borrow = sub(C, a, b, width)
    return NOT(borrow)


def const_bits(value, width):
    return [const((value >> i) & 1) for i in range(width)]


def compress_columns(C, cols):
    """Carry-save reduction of weighted columns to a single binary number (list of bits)."""
    cols = [list(c) for c in cols]
    # fold constants per column into at most one constant bit (with carries)
    changed = True
    while changed:
        changed = False
        for i in range(len(cols)):
            cs = [w for w in cols[i] if w.is_const()]
            if len(cs) >= 2:
                vs = [w for w in cols[i] if not w.is_const()]
                s = sum(w.c for w in cs)
                cols[i] = vs + ([ONE] if s & 1 else [])
                if s >> 1:
                    while len(cols) <= i + 1:
                        cols.append([])
                    # add (s >> 1) at weight i+1 as constant bits
                    for k in range((s >> 1).bit_length()):
                        if (s >> 1) >> k & 1:
                            while len(cols) <= i + 1 + k:
                                cols.append([])
                            cols[i + 1 + k].append(ONE)
                changed = True
    # Wallace-style: full adders until every column has at most 2 bits
    i = 0
    while True:
        if all(len(c) <= 2 for c in cols):
            break
        new = [[] for _ in range(len(cols) + 1)]
        for i, col in enumerate(cols):
            col = list(col)
            while len(col) >= 3:
                x, y, z = col.pop(), col.pop(), col.pop()
                new[i].append(x ^ y ^ z)
                new[i + 1].append(maj(C, x, y, z))
            new[i].extend(col)
        while new and not new[-1]:
            new.pop()
        cols = new
    # final ripple over columns with <= 2 bits
    out = []
    carry = ZERO
    for col in cols:
        col = col + [ZERO] * (2 - len(col))
        x, y = col
        out.append(x ^ y ^ carry)
        carry = maj(C, x, y, carry)
    out.append(carry)
    return out


def multiply(C, a, b):
    """Unsigned a*b via partial products + carry-save tree."""
    cols = [[] for _ in range(len(a) + len(b))]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            cols[i + j].append(C.AND(x, y))
    out = compress_columns(C, cols)
    return out[: len(a) + len(b)]


def shr(C, x, amt, zero_if=ZERO):
    """Logical right shift of x by the unsigned amount `amt` (bit list), result zero if `zero_if`.
    Stages largest first; the zero condition is merged into the first stage."""
    x = list(x)
    n = len(x)
    stages = list(enumerate(amt))[::-1]
    first = True
    for k, s in stages:
        sh = 1 << k
        if sh >= n and not first:
            # shifting by >= n clears everything
            x = [C.AND(NOT(s), w) for w in x]
            continue
        if first:
            p = C.AND(NOT(zero_if), NOT(s))
            q = C.AND(NOT(zero_if), s)
            x = [C.AND(p, x[j]) ^ (C.AND(q, x[j + sh]) if j + sh < n else ZERO) for j in range(n)]
            first = False
        else:
            x = [(x[j] ^ C.AND(s, x[j] ^ x[j + sh])) if j + sh < n else C.AND(NOT(s), x[j]) for j in range(n)]
    if first:  # no amount bits
        x = [C.AND(NOT(zero_if), w) for w in x]
    return x


def shl_window(C, x, amt, lo, hi):
    """Bits [lo, hi) of (x << amt) for unsigned amt (bit list). Only needed bits are built (dead ones are pruned)."""
    width = hi
    cur = list(x) + [ZERO] * max(0, width - len(x))
    cur = cur[:width]
    for k, s in enumerate(amt):
        sh = 1 << k
        cur = [(cur[j] ^ C.AND(s, cur[j] ^ cur[j - sh])) if j - sh >= 0 else C.AND(NOT(s), cur[j]) for j in range(width)]
    return cur[lo:hi]


def lzc(C, bits):
    """Leading-zero count of `bits` (LSB first). Returns (all_zero, count bits LSB first); len(bits) a power of two."""
    n = len(bits)
    assert n & (n - 1) == 0
    if n == 1:
        return NOT(bits[0]), []
    if n == 2:
        lo, hi = bits
        az = C.AND(NOT(hi), NOT(lo))
        return az, [NOT(hi)]
    h = n // 2
    az_lo, c_lo = lzc(C, bits[:h])
    az_hi, c_hi = lzc(C, bits[h:])
    az = C.AND(az_hi, az_lo)
    cnt = mux(C, az_hi, c_lo, c_hi) + [az_hi]
    return az, cnt
