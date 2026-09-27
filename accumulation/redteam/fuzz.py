"""Seeded random fuzzer for the certified bounds (SPEC §5 contracts) on micro Verity circuits.

Generator
    :func:`gen_circuit` draws a random DAG of 1..``max_ops`` ops from the block vocabulary of
    :mod:`accumulation.redteam.circuits` (``matmul`` / ``matmul_tt`` with ``CH=1``, ``add`` / ``mul`` /
    ``swiglu`` with shared inputs, ``gain`` / ``rowscale`` / ``rmsnorm`` / ``softmax``, ``colsum``, ``embed``),
    random shapes ``M, N, K in [1, max_dim]``, random roles on every new root parameter, operand reuse
    (shared tensors, ``add(x, x)``, Gram matrices) and occasional views (``rows`` slices, repeated rows,
    ``as2d`` of a column-sum).  The gate count is capped so the exact solver stays cheap.

Driver
    Every circuit is evaluated on a small ``F x X x G`` grid (``X`` from tiny to "everything fits", ``F`` from 1
    to infinity, ``G`` = ``None`` plus binding total-work caps strictly below the circuit's work) with
    :func:`accumulation.redteam.harness.evaluate`: ``extract`` -> ``lower_bound`` /
    ``upper_bound`` (recompute and literal, the literal plan materialised and re-checked with ``is_legal`` /
    ``partition_cost``) / ``exact_min_input`` (time-boxed).  Every triple is appended to a JSONL under
    ``/tmp/redteam/``; violations (``L > I*``, ``U_lit < I*``, illegal literal plan, ``U < L``, missing ``U``
    although a legal partition exists, ...) are shrunk (drop sink ops, decrement a dimension everywhere,
    drop a view, turn a charged root ``fixed``) while the violation persists, and the minimal instance is saved
    as a runnable Python snippet under ``/tmp/redteam/counterexamples/``.  Monotonicity of ``L``, ``U``, ``U_lit``,
    ``I*`` in ``X``, in ``F`` and in ``G`` is checked per circuit.

Reproducibility
    circuit ``i`` of run ``seed`` is drawn from ``random.Random(seed * 1_000_003 + i)``; ``--regen SEED:I``
    rebuilds it.

Usage::

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.fuzz --seed 1 --n 300 --time-limit 5
    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.fuzz --summary /tmp/redteam/fuzz_*.jsonl
"""

from __future__ import annotations

import argparse
import glob
import itertools
import json
import math
import os
import random
import statistics
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

from accumulation.exact.solve import flatten
from accumulation.graph.opgraph import extract
from accumulation.redteam.circuits import Circuit, Op, Param, build
from accumulation.redteam.harness import BIG, Record, evaluate, monotonicity_violations, op_gate_lists

OUT_DIR = "/tmp/redteam"
CE_DIR = os.path.join(OUT_DIR, "counterexamples")

ROLE_W = {"fixed": 3.0, "accumulated": 3.0, "carried": 1.0, "token": 2.0, "seed": 0.4}
KIND_W = {"matmul": 4.0, "matmul_tt": 1.5, "add": 2.0, "mul": 1.5, "gain": 1.0, "rowscale": 1.0, "colsum": 1.2,
          "embed": 1.0, "swiglu": 0.5, "rmsnorm": 0.35, "softmax": 0.25}

# violations worth shrinking, most severe first (the shrinker preserves the first one present)
SEVERITY = ["L_gt_Istar", "Ulit_lt_Istar", "Ulit_illegal", "Ulit_cost_under", "Ulit_ru_over", "U_but_infeasible",
            "L_infeasible_but_Istar", "Lnoprog_gt_Istar", "Urec_lt_L", "Ulit_lt_L", "L_gt_found", "Lnoprog_gt_found",
            "Ulit_materialize_assert",
            "Ulit_materialize_error", "U_unavailable", "L_error"]


def _wchoice(rng: random.Random, weights: dict[str, float]) -> str:
    ks = list(weights)
    return rng.choices(ks, weights=[weights[k] for k in ks], k=1)[0]


# ---------------------------------------------------------------------------------------------------------
# generator
# ---------------------------------------------------------------------------------------------------------

@dataclass
class _Gen:
    rng: random.Random
    max_dim: int
    p_reuse: float
    p_view: float
    params: list[Param] = field(default_factory=list)
    ops: list[Op] = field(default_factory=list)
    shapes: list[tuple[int, ...]] = field(default_factory=list)   # op output shapes

    # -- pools ---------------------------------------------------------------------------------------------
    def _pool(self, nd: int, pred: Callable[[tuple[int, ...]], bool]) -> list[tuple[tuple, tuple[int, ...]]]:
        out = []
        for p in self.params:
            if len(p.shape) == nd and p.width == 16 and pred(p.shape):
                out.append((("p", p.name), p.shape))
        for i, s in enumerate(self.shapes):
            if len(s) == nd and pred(s):
                out.append((("o", i), s))
        return out

    def _new_param(self, shape: tuple[int, ...], *, role: str | None = None, width: int = 16) -> tuple:
        name = f"p{len(self.params)}"
        self.params.append(Param(name, shape, role or _wchoice(self.rng, ROLE_W), width))
        return ("p", name)

    def _dim(self) -> int:
        return self.rng.randint(1, self.max_dim)

    def _get2d(self, pred: Callable[[tuple[int, ...]], bool], fresh: Callable[[], tuple[int, ...]],
               allow_view: bool = True) -> tuple[tuple, tuple[int, ...]]:
        """A 2-D operand satisfying ``pred``: reuse from the pool or a fresh parameter; maybe a view."""
        pool = self._pool(2, pred)
        if allow_view and self.rng.random() < self.p_view:
            # rows slice / repeated row of a pool tensor or a fresh parameter whose *rows* are unconstrained
            base_pool = [(r, s) for r, s in self._pool(2, lambda s: True) if pred((1, s[1]))]
            if base_pool and self.rng.random() < 0.7:
                ref, s = self.rng.choice(base_pool)
            else:
                s = fresh()
                s = (self.rng.randint(1, self.max_dim), s[1])
                if not pred((1, s[1])):
                    return self._get2d(pred, fresh, allow_view=False)
                ref = self._new_param(s)
            if self.rng.random() < 0.5 and s[0] >= 2:
                lo = self.rng.randrange(0, s[0])
                hi = self.rng.randint(lo + 1, s[0])
                if pred((hi - lo, s[1])):
                    return ref + ("rows", lo, hi), (hi - lo, s[1])
            n = self.rng.randint(1, self.max_dim)
            i = self.rng.randrange(0, s[0])
            if pred((n, s[1])):
                return ref + ("reprow", i, n), (n, s[1])
        if pool and self.rng.random() < self.p_reuse:
            return self.rng.choice(pool)
        s = fresh()
        return self._new_param(s), s

    def _get1d(self, n: int) -> tuple:
        pool = self._pool(1, lambda s: s == (n,))
        if pool and self.rng.random() < self.p_reuse:
            return self.rng.choice(pool)[0]
        return self._new_param((n,))

    # -- one op ----------------------------------------------------------------------------------------------
    def add_op(self, kind: str) -> None:
        rng = self.rng
        if kind == "matmul":
            a, (M, Kd) = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            if rng.random() < 0.12:
                # 1-D column-sum output viewed as a (1, K) row
                pool1 = self._pool(1, lambda s: s == (Kd,))
                if pool1:
                    a, (M, Kd) = (rng.choice(pool1)[0] + ("as2d",), (1, Kd))
            b, (N, _) = self._get2d(lambda s: s[1] == Kd, lambda: (self._dim(), Kd))
            self.ops.append(Op("matmul", (a, b)))
            self.shapes.append((M, N))
        elif kind == "matmul_tt":
            a, (Kd, M) = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            b, (_, N) = self._get2d(lambda s: s[0] == Kd, lambda: (Kd, self._dim()))
            self.ops.append(Op("matmul_tt", (a, b)))
            self.shapes.append((M, N))
        elif kind in ("add", "mul", "swiglu"):
            a, s = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            if rng.random() < 0.15:
                b = a                              # add(x, x)
            else:
                b, _ = self._get2d(lambda t: t == s, lambda: s)
            self.ops.append(Op(kind, (a, b)))
            self.shapes.append(s)
        elif kind in ("gain", "rmsnorm"):
            a, s = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            g = self._get1d(s[1])
            self.ops.append(Op(kind, (a, g)))
            self.shapes.append(s)
        elif kind == "rowscale":
            a, s = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            g = self._get1d(s[0])
            self.ops.append(Op(kind, (a, g)))
            self.shapes.append(s)
        elif kind == "softmax":
            a, s = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            self.ops.append(Op(kind, (a,)))
            self.shapes.append(s)
        elif kind == "colsum":
            a, s = self._get2d(lambda s: True, lambda: (self._dim(), self._dim()))
            self.ops.append(Op(kind, (a,)))
            self.shapes.append((s[1],))
        elif kind == "embed":
            Q = self._dim()
            toks = self._new_param((Q,), role=rng.choice(["token", "token", "fixed"]), width=32)
            tab, (D, V) = self._get2d(lambda s: s[1] >= 2, lambda: (self._dim(), rng.randint(2, self.max_dim)),
                                      allow_view=False)
            self.ops.append(Op("embed", (toks, tab)))
            self.shapes.append((Q, D))
        else:
            raise ValueError(kind)

    def circuit(self, name: str) -> Circuit:
        return Circuit(params=list(self.params), ops=list(self.ops), name=name)


def gen_circuit(rng: random.Random, *, max_ops: int = 6, max_dim: int = 4, gate_cap: int = 60,
                p_reuse: float = 0.55, p_view: float = 0.15, name: str = "fuzz") -> Circuit:
    """One random micro-circuit; at most ``gate_cap`` gates, at least one charged root."""
    n_ops = rng.randint(1, max_ops)
    g = _Gen(rng, max_dim, p_reuse, p_view)
    for _ in range(n_ops):
        snap = (list(g.params), list(g.ops), list(g.shapes))
        try:
            g.add_op(_wchoice(rng, KIND_W))
            c = g.circuit(name)
            c.shapes()
            if c.n_gates() > gate_cap:
                raise OverflowError
        except (AssertionError, OverflowError, ValueError):
            g.params, g.ops, g.shapes = snap
            if not g.ops:
                continue
            break
    if not g.ops:                                   # fall back to a plain matmul
        g = _Gen(rng, max_dim, p_reuse, 0.0)
        g.add_op("matmul")
    circ = g.circuit(name)
    circ = _prune_params(circ)
    if not any(p.charged for p in circ.params):
        j = rng.randrange(len(circ.params))
        circ.params[j] = _with_role(circ.params[j], "accumulated")
    return circ


def _with_role(p: Param, role: str) -> Param:
    return Param(p.name, p.shape, role, p.width)


def _prune_params(c: Circuit) -> Circuit:
    used = {r[1] for o in c.ops for r in o.args if r[0] == "p"}
    return Circuit(params=[p for p in c.params if p.name in used], ops=list(c.ops), name=c.name, notes=dict(c.notes))


def family(c: Circuit) -> str:
    """Structural tag: sorted kinds, plus ``shared`` (a tensor read by two op operands), ``view``, ``chain``."""
    kinds = "+".join(sorted({o.kind for o in c.ops}))
    refs = [r[:2] for o in c.ops for r in o.args]
    flags = []
    if len(refs) != len(set(refs)):
        flags.append("shared")
    if any(len(r) > 2 for o in c.ops for r in o.args):
        flags.append("view")
    if any(r[0] == "o" for o in c.ops for r in o.args):
        flags.append("chain")
    return kinds + ("|" + ",".join(flags) if flags else "")


# ---------------------------------------------------------------------------------------------------------
# (F, X) grids
# ---------------------------------------------------------------------------------------------------------

def _charged_bytes(c: Circuit) -> int:
    return sum(p.bytes for p in c.params if p.charged)


def _all_bytes(c: Circuit) -> int:
    inter = sum(2 * math.prod(s) for s in c.shapes())
    return _charged_bytes(c) + inter


def pick_grid(rng: random.Random, c: Circuit, n_x: int = 3, n_f: int = 2, n_g: int = 2, work: int | None = None,
              wmax: int = 1) -> list[tuple[int, int, Optional[int]]]:
    """Random ``(F, X, G)`` grid.  ``G = None`` is always included; the other ``n_g - 1`` values are *binding*
    total-work caps in ``[wmax, work)`` (``work`` = total work of the circuit, ``wmax`` = largest single gate), so
    that ``G`` forces a split without being trivially infeasible.  ``work=None`` (or ``n_g <= 1``) -> ``G=None`` only."""
    cb, ab = _charged_bytes(c), _all_bytes(c)
    xs = {2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64, cb, cb + 4, cb + 8, ab}
    xs = sorted(x for x in xs if 2 <= x <= max(ab, cb) + 8)
    X = set(rng.sample(xs, min(n_x - 1, len(xs))))
    X.add(BIG if rng.random() < 0.7 else (ab if ab >= 2 else BIG))
    while len(X) < n_x and len(xs) > len(X):
        X.add(rng.choice(xs))
    fs = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 17, 25]
    Fs = set(rng.sample(fs, min(n_f - 1, len(fs))))
    Fs.add(BIG if rng.random() < 0.7 else rng.choice(fs))
    while len(Fs) < n_f:
        Fs.add(rng.choice(fs))
    Gs: list[Optional[int]] = [None]
    if work is not None and n_g > 1 and work > wmax:
        cands = sorted({max(wmax, -(-work * num // den)) for num, den in ((1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 6))}
                       | {wmax, wmax + 1, work - 1, work // 2 + 1})
        cands = [g for g in cands if wmax <= g < work]
        for g in rng.sample(cands, min(n_g - 1, len(cands))):
            Gs.append(g)
    return [(F, X_, G) for F in sorted(Fs) for X_ in sorted(X) for G in Gs]


# ---------------------------------------------------------------------------------------------------------
# evaluation of a circuit on a grid
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Prepared:
    circ: Circuit
    bp: object
    flat: object
    g: object
    op_gates: dict


def prepare(circ: Circuit) -> Prepared:
    bp = build(circ)
    flat = flatten(bp)
    g = extract(bp)
    return Prepared(circ, bp, flat, g, op_gate_lists(bp, g, flat))


def eval_point(prep: Prepared, F: int, X: int, G: Optional[int] = None, *, time_limit: float, exact_limit: int,
               name: str, fam: str, lower_fn=None, upper_fn=None) -> Record:
    kw = {}
    if lower_fn is not None:
        kw["lower_fn"] = lower_fn
    if upper_fn is not None:
        kw["upper_fn"] = upper_fn
    return evaluate(prep.bp, F, X, G, family=fam, name=name, time_limit=time_limit, exact_limit=exact_limit,
                    g=prep.g, flat=prep.flat, op_gates=prep.op_gates, **kw)


def primary(rec: Record) -> Optional[str]:
    for v in SEVERITY:
        if v in rec.violations:
            return v
    return rec.violations[0] if rec.violations else None


# ---------------------------------------------------------------------------------------------------------
# shrinking
# ---------------------------------------------------------------------------------------------------------

def _remap_drop(c: Circuit, drop: int) -> Optional[Circuit]:
    """Drop op ``drop`` (must be a sink) and renumber."""
    if drop not in c.sinks():
        return None
    ops = []
    for i, o in enumerate(c.ops):
        if i == drop:
            continue
        args = tuple((r[0], r[1] - 1 if r[0] == "o" and r[1] > drop else r[1]) + tuple(r[2:]) for r in o.args)
        ops.append(Op(o.kind, args, o.name))
    if not ops:
        return None
    return _prune_params(Circuit(params=list(c.params), ops=ops, name=c.name, notes=dict(c.notes)))


def _dec_dim(c: Circuit, d: int) -> Optional[Circuit]:
    """Replace dimension value ``d`` by ``d - 1`` in every parameter shape and view size."""
    if d < 2:
        return None
    params = [Param(p.name, tuple(d - 1 if s == d else s for s in p.shape), p.role, p.width) for p in c.params]
    ops = []
    for o in c.ops:
        args = []
        for r in o.args:
            r = tuple(r)
            if len(r) > 2:
                if r[2] == "rows":
                    lo, hi = r[3], r[4]
                    if hi - lo == d:
                        hi -= 1
                    r = r[:3] + (lo, hi)
                elif r[2] == "reprow":
                    i, n = r[3], r[4]
                    n = n - 1 if n == d else n
                    i = min(i, max(0, n - 1))
                    r = r[:3] + (i, n)
            args.append(r)
        ops.append(Op(o.kind, tuple(args), o.name))
    return Circuit(params=params, ops=ops, name=c.name, notes=dict(c.notes))


def _fix_role(c: Circuit, name: str) -> Circuit:
    return Circuit(params=[_with_role(p, "fixed") if p.name == name else p for p in c.params], ops=list(c.ops),
                   name=c.name, notes=dict(c.notes))


def _drop_view(c: Circuit, oi: int, ai: int) -> Optional[Circuit]:
    o = c.ops[oi]
    r = o.args[ai]
    if len(r) <= 2:
        return None
    shapes = c.shapes()
    before = c._ref_shape(r, shapes)
    base = r[:2]
    if c._ref_shape(base, shapes) != before:
        return None
    args = tuple(base if j == ai else a for j, a in enumerate(o.args))
    ops = [Op(o.kind, args, o.name) if j == oi else x for j, x in enumerate(c.ops)]
    return _prune_params(Circuit(params=list(c.params), ops=ops, name=c.name, notes=dict(c.notes)))


def _reprow_shrink(c: Circuit, oi: int, ai: int) -> Optional[Circuit]:
    """``reprow(., i, n)`` -> ``reprow(., i, n - 1)`` (repeated-row views are the LW hot spot)."""
    r = c.ops[oi].args[ai]
    if len(r) > 2 and r[2] == "reprow" and r[4] >= 2:
        nr = r[:4] + (r[4] - 1,)
        args = tuple(nr if j == ai else a for j, a in enumerate(c.ops[oi].args))
        ops = [Op(c.ops[oi].kind, args, c.ops[oi].name) if j == oi else x for j, x in enumerate(c.ops)]
        return Circuit(params=list(c.params), ops=ops, name=c.name, notes=dict(c.notes))
    return None


def _valid(c: Optional[Circuit]) -> bool:
    if c is None or not c.ops:
        return False
    try:
        c.shapes()
        return c.n_gates() >= 1
    except (AssertionError, ValueError):
        return False


def shrink_candidates(c: Circuit) -> Iterable[tuple[str, Circuit]]:
    for i in reversed(range(len(c.ops))):
        cand = _remap_drop(c, i)
        if _valid(cand):
            yield f"drop op {i}", cand
    for oi, o in enumerate(c.ops):
        for ai in range(len(o.args)):
            cand = _reprow_shrink(c, oi, ai)
            if _valid(cand):
                yield f"reprow-1 op {oi} arg {ai}", cand
            cand = _drop_view(c, oi, ai)
            if _valid(cand):
                yield f"drop view op {oi} arg {ai}", cand
    dims = sorted({s for p in c.params for s in p.shape} | {r[4] for o in c.ops for r in o.args if len(r) > 2 and r[2] == "reprow"},
                  reverse=True)
    for d in dims:
        cand = _dec_dim(c, d)
        if _valid(cand):
            yield f"dim {d}->{d - 1}", cand
    for p in c.params:
        if p.charged:
            cand = _fix_role(c, p.name)
            if _valid(cand):
                yield f"role {p.name}->fixed", cand


def shrink(circ: Circuit, F: int, X: int, target: str, *, G: Optional[int] = None, time_limit: float, exact_limit: int,
           budget: int = 80, lower_fn=None, upper_fn=None,
           log: Callable[[str], None] = lambda s: None) -> tuple[Circuit, Record, int]:
    """Greedy shrink preserving violation ``target`` at the same ``(F, X, G)``.  Returns the minimal circuit,
    its record and the number of evaluations spent.  (A binding ``G`` is kept as is: shrinking the circuit can
    only make it less binding, so a violation that survives is a genuine one at that ``G``.)"""
    cur = circ
    prep = prepare(cur)
    cur_rec = eval_point(prep, F, X, G, time_limit=time_limit, exact_limit=exact_limit, name=circ.name, fam=family(cur),
                         lower_fn=lower_fn, upper_fn=upper_fn)
    spent = 1
    improved = True
    while improved and spent < budget:
        improved = False
        for how, cand in shrink_candidates(cur):
            if spent >= budget:
                break
            try:
                p = prepare(cand)
                r = eval_point(p, F, X, G, time_limit=time_limit, exact_limit=exact_limit, name=circ.name, fam=family(cand),
                               lower_fn=lower_fn, upper_fn=upper_fn)
            except Exception as e:  # noqa: BLE001
                log(f"    shrink {how}: build/eval error {type(e).__name__}: {e}")
                spent += 1
                continue
            spent += 1
            if target in r.violations:
                log(f"    shrink {how}: {cand.n_gates()} gates, still {target}")
                cur, cur_rec = cand, r
                improved = True
                break
    return cur, cur_rec, spent


# ---------------------------------------------------------------------------------------------------------
# counterexample snippets
# ---------------------------------------------------------------------------------------------------------

def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, int) and v >= BIG:
        return "inf"
    return str(v)


def snippet(circ: Circuit, rec: Record, *, seed: int, idx: int, how: str = "") -> str:
    lines = [
        f"# red-team counterexample: {', '.join(rec.violations)}",
        f"# seed={seed} circuit={idx} {how}".rstrip(),
        f"# F={_fmt(rec.F)} G={_fmt(rec.G)} X={_fmt(rec.X)}  gates={rec.gates} work={rec.work}"
        f"{'  (L computed at G=None)' if rec.G is not None and rec.L_G is None else ''}",
        f"# L={_fmt(rec.L)} (source {_fmt(rec.L_source)}, cap {_fmt(rec.L_cap)})  I*={_fmt(rec.Istar)}"
        f"{'' if rec.Istar_optimal or rec.Istar is None else '?'}{' (infeasible)' if rec.Istar_infeasible else ''}"
        f"  U={_fmt(rec.U)}  U_lit={_fmt(rec.Ulit)} (materialised cost {_fmt(rec.Ulit_cost)}, legal={rec.Ulit_legal})",
    ]
    if rec.U_error:
        lines.append(f"# U_error: {rec.U_error.splitlines()[0][:160]}")
    if rec.Ulit_error:
        lines.append(f"# Ulit_error: {rec.Ulit_error.splitlines()[0][:160]}")
    if rec.Ulit_legal_why:
        lines.append(f"# Ulit_legal_why: {rec.Ulit_legal_why[:200]}")
    for s in rec.Ulit_ru_over[:4]:
        lines.append(f"# Ulit_ru_over: {s}")
    if rec.Ulit_unmat_reason:
        lines.append(f"# Ulit not materialised: {rec.Ulit_unmat_reason.splitlines()[0][:160]}")
    if rec.Istar_partition:
        lines.append("# optimal partition (exact solver):")
        for ru in rec.Istar_partition[:12]:
            lines.append(f"#   RU{ru['ru']}: work={ru['work']} in={ru['in_bytes']}B ops={ru['ops']} imports={ru['imports']}")
    lines.append("")
    lines.append(circ.to_python())
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    from accumulation.redteam.circuits import build")
    lines.append("    from accumulation.redteam.harness import evaluate")
    lines.append(f"    rec = evaluate(build(circ), {rec.F}, {rec.X}, {rec.G}, time_limit=60.0)")
    lines.append("    print('L', rec.L, 'I*', rec.Istar, 'optimal', rec.Istar_optimal, 'U', rec.U, 'U_lit', rec.Ulit,")
    lines.append("          'legal', rec.Ulit_legal, rec.Ulit_legal_why, 'violations', rec.violations)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Stats:
    circuits: int = 0
    build_errors: int = 0
    points: int = 0
    timeouts: int = 0
    infeasible: int = 0
    exact_skipped: int = 0
    violations: dict = field(default_factory=dict)
    mono: int = 0
    shrunk: int = 0
    seconds: float = 0.0

    def to_json(self) -> dict:
        return {k: (dict(v) if isinstance(v, dict) else v) for k, v in self.__dict__.items()}


def circuit_rng(seed: int, idx: int) -> random.Random:
    return random.Random(seed * 1_000_003 + idx)


def run(seed: int, n: int, *, max_ops: int = 6, max_dim: int = 4, gate_cap: int = 60, time_limit: float = 5.0,
        exact_limit: int = 200, n_x: int = 3, n_f: int = 2, n_g: int = 2, do_shrink: bool = True, out_dir: str = OUT_DIR,
        lower_fn=None, upper_fn=None, verbose: bool = True, max_seconds: float | None = None,
        p_view: float = 0.15) -> Stats:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "counterexamples"), exist_ok=True)
    path = os.path.join(out_dir, f"fuzz_{seed}.jsonl")
    mono_path = os.path.join(out_dir, f"fuzz_{seed}_mono.txt")
    st = Stats()
    t0 = time.perf_counter()
    seen_ce: set[tuple[str, str]] = set()
    with open(path, "w") as fout, open(mono_path, "w") as fmono:
        for idx in range(n):
            if max_seconds is not None and time.perf_counter() - t0 > max_seconds:
                if verbose:
                    print(f"[seed {seed}] time budget reached after {idx} circuits")
                break
            rng = circuit_rng(seed, idx)
            name = f"s{seed}c{idx}"
            circ = gen_circuit(rng, max_ops=max_ops, max_dim=max_dim, gate_cap=gate_cap, p_view=p_view, name=name)
            try:
                prep = prepare(circ)
            except Exception as e:  # noqa: BLE001
                st.build_errors += 1
                fout.write(json.dumps({"kind": "build_error", "name": name, "error": f"{type(e).__name__}: {e}",
                                       "circuit": circ.to_python()}) + "\n")
                continue
            st.circuits += 1
            fam = family(circ)
            recs: list[Record] = []
            work = prep.flat.total_work()
            wmax = max((prep.flat.work[x] for x in prep.flat.gates), default=1)
            for F, X, G in pick_grid(rng, circ, n_x=n_x, n_f=n_f, n_g=n_g, work=work, wmax=wmax):
                try:
                    rec = eval_point(prep, F, X, G, time_limit=time_limit, exact_limit=exact_limit, name=name, fam=fam,
                                     lower_fn=lower_fn, upper_fn=upper_fn)
                except Exception as e:  # noqa: BLE001
                    fout.write(json.dumps({"kind": "eval_error", "name": name, "F": F, "X": X, "G": G,
                                           "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc(limit=4),
                                           "circuit": circ.to_python()}) + "\n")
                    continue
                rec.snippet = circ.to_python()
                recs.append(rec)
                st.points += 1
                st.timeouts += int(rec.Istar_timeout)
                st.infeasible += int(rec.Istar_infeasible)
                st.exact_skipped += int(rec.Istar is None and not rec.Istar_timeout and not rec.Istar_infeasible
                                        and not rec.Istar_error)
                for v in rec.violations:
                    st.violations[v] = st.violations.get(v, 0) + 1
                d = rec.to_json()
                d["kind"] = "point"
                d["seed"], d["idx"] = seed, idx
                fout.write(json.dumps(d) + "\n")
                if rec.violations and verbose:
                    print(f"[seed {seed}] c{idx} F={_fmt(F)} G={_fmt(G)} X={_fmt(X)} gates={rec.gates} L={_fmt(rec.L)} "
                          f"I*={_fmt(rec.Istar)} U={_fmt(rec.U)} Ulit={_fmt(rec.Ulit)} -> {','.join(rec.violations)}")
                    sys.stdout.flush()
                tgt = primary(rec)
                if tgt is not None and do_shrink:
                    key = (tgt, fam, G is None)
                    if key in seen_ce and tgt in ("U_unavailable",):
                        continue                    # plenty of these; keep one shrunk example per family
                    seen_ce.add(key)
                    try:
                        small, srec, spent = shrink(circ, F, X, tgt, G=G, time_limit=time_limit, exact_limit=exact_limit,
                                                    lower_fn=lower_fn, upper_fn=upper_fn,
                                                    log=(print if verbose else (lambda s: None)))
                    except Exception as e:  # noqa: BLE001
                        small, srec, spent = circ, rec, 0
                        if verbose:
                            print(f"    shrink failed: {type(e).__name__}: {e}")
                    st.shrunk += 1
                    fn = os.path.join(out_dir, "counterexamples", f"{tgt}_s{seed}c{idx}_F{_fmt(F)}_G{_fmt(G)}_X{_fmt(X)}.py")
                    with open(fn, "w") as f:
                        f.write(snippet(small, srec, seed=seed, idx=idx, how=f"(shrunk from {rec.gates} to {srec.gates} gates in {spent} evals)"))
                    if verbose:
                        print(f"    -> {fn}")
            mono = monotonicity_violations(recs)
            for m in mono:
                st.mono += 1
                fmono.write(f"{name} [{fam}]: {m}\n")
                fout.write(json.dumps({"kind": "mono", "name": name, "seed": seed, "idx": idx, "family": fam,
                                       "msg": m, "circuit": circ.to_python()}) + "\n")
                if verbose:
                    print(f"[seed {seed}] c{idx} MONO: {m}")
            if verbose and idx % 25 == 0:
                el = time.perf_counter() - t0
                print(f"[seed {seed}] {idx + 1}/{n} circuits, {st.points} points, {el:.0f}s, "
                      f"violations={st.violations}, timeouts={st.timeouts}")
                sys.stdout.flush()
    st.seconds = time.perf_counter() - t0
    with open(os.path.join(out_dir, f"fuzz_{seed}_stats.json"), "w") as f:
        json.dump(st.to_json(), f, indent=1)
    return st


# ---------------------------------------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------------------------------------

def _q(xs: list[float]) -> str:
    if not xs:
        return "n/a"
    xs = sorted(xs)
    n = len(xs)
    pct = lambda p: xs[min(n - 1, int(p * (n - 1)))]  # noqa: E731
    eq1 = sum(1 for x in xs if abs(x - 1) < 1e-9) / n
    return (f"n={n} ==1: {eq1:5.1%}  p50={pct(.5):.3f}  p90={pct(.9):.3f}  p99={pct(.99):.3f}  "
            f"max={xs[-1]:.3f}  mean={statistics.fmean(xs):.3f}")


def summarize(paths: list[str], *, by_family: bool = True, top: int = 25) -> str:
    pts = []
    mono = []
    errs = 0
    for p in paths:
        for line in open(p):
            d = json.loads(line)
            k = d.get("kind", "point")
            if k == "point":
                pts.append(d)
            elif k == "mono":
                mono.append(d)
            else:
                errs += 1
    out = []
    out.append(f"points: {len(pts)}  circuits: {len({(d['seed'], d['idx']) for d in pts})}  build/eval errors: {errs}  "
               f"mono violations: {len(mono)}")
    n_opt = sum(1 for d in pts if d["Istar_optimal"])
    n_to = sum(1 for d in pts if d["Istar_timeout"])
    n_inf = sum(1 for d in pts if d["Istar_infeasible"])
    n_skip = sum(1 for d in pts if d["Istar"] is None and not d["Istar_timeout"] and not d["Istar_infeasible"])
    out.append(f"I*: optimal {n_opt}, found-not-proven {sum(1 for d in pts if d['Istar'] is not None) - n_opt}, "
               f"timeouts {n_to}, infeasible {n_inf}, skipped {n_skip}")
    viol: dict[str, int] = {}
    for d in pts:
        for v in d["violations"]:
            viol[v] = viol.get(v, 0) + 1
    out.append(f"violations: {dict(sorted(viol.items(), key=lambda kv: -kv[1]))}")

    def ratios(sel):
        UL, UI, IL, ULitI = [], [], [], []
        for d in sel:
            L, U, I, Ul = d["L"], d["U"], d["Istar"], d["Ulit"]
            if d["L_infeasible"] or L is None:
                continue
            if U is not None and L > 0:
                UL.append(U / L)
            if I is not None and d["Istar_optimal"]:
                if U is not None and I > 0:
                    UI.append(U / I)
                if Ul is not None and I > 0:
                    ULitI.append(Ul / I)
                if L > 0:
                    IL.append(I / L)
        return UL, UI, IL, ULitI

    UL, UI, IL, ULitI = ratios(pts)
    out.append("ratios over all points (I* ratios only where the solver proved optimality):")
    out.append(f"  U/L     : {_q(UL)}")
    out.append(f"  U/I*    : {_q(UI)}")
    out.append(f"  U_lit/I*: {_q(ULitI)}")
    out.append(f"  I*/L    : {_q(IL)}")
    # where is L loose? group by family
    if by_family:
        fams: dict[str, list] = {}
        for d in pts:
            fams.setdefault(d["family"], []).append(d)
        rows = []
        for f, sel in fams.items():
            _, _, il, _ = ratios(sel)
            if not il:
                continue
            loose = sum(1 for x in il if x > 1 + 1e-9) / len(il)
            rows.append((statistics.fmean(il), loose, max(il), len(il), f))
        rows.sort(reverse=True)
        out.append(f"\nfamilies ranked by mean I*/L (L loose = I* > L), top {top}:")
        out.append(f"  {'mean I*/L':>9} {'frac loose':>10} {'max':>6} {'n':>5}  family")
        for m, lo, mx, n, f in rows[:top]:
            out.append(f"  {m:9.3f} {lo:10.1%} {mx:6.2f} {n:5d}  {f}")
        rows.sort(key=lambda r: (r[3],), reverse=True)
        # tight families
        tight = [r for r in rows if r[1] == 0 and r[3] >= 5]
        out.append(f"\nfamilies where L == I* on every proven point (n >= 5): {len(tight)}")
        for m, lo, mx, n, f in sorted(tight, key=lambda r: -r[3])[:top]:
            out.append(f"  n={n:4d}  {f}")
    # L loose by (F, G, X) regime
    reg: dict[str, list] = {}
    for d in pts:
        if d["L"] is None or d["L_infeasible"] or not d["Istar_optimal"] or d["L"] <= 0:
            continue
        key = (("F=inf" if d["F"] >= BIG else "F<inf") + "," + ("G=None" if d.get("G") is None else "G<work") + ","
               + ("X=inf" if d["X"] >= BIG else "X<inf"))
        reg.setdefault(key, []).append(d["Istar"] / d["L"])
    out.append("\nI*/L by regime:")
    for k, v in sorted(reg.items()):
        out.append(f"  {k:22} {_q(v)}")
    n_g = sum(1 for d in pts if d.get("G") is not None)
    n_lg = sum(1 for d in pts if d.get("G") is not None and d.get("L_G") is None and d["L"] is not None)
    out.append(f"\nbinding-G points: {n_g} (of which L computed at G=None: {n_lg})")
    # U legality summary
    n_mat = sum(1 for d in pts if d["Ulit_materialized"])
    n_ill = sum(1 for d in pts if d["Ulit_legal"] is False)
    n_unmat = sum(1 for d in pts if d["Ulit"] is not None and not d["Ulit_materialized"])
    out.append(f"\nliteral plans: {sum(1 for d in pts if d['Ulit'] is not None)} produced, {n_mat} materialised, "
               f"{n_ill} illegal per is_legal, {n_unmat} not materialisable, "
               f"{sum(1 for d in pts if d['Ulit_cost'] is not None and d['Ulit_cost'] > d['Ulit'])} cost under-stated, "
               f"{sum(1 for d in pts if d['Ulit_ru_over'])} with an RU over its declared imports_max")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="red-team random fuzzer")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n", type=int, default=200, help="number of circuits")
    ap.add_argument("--max-ops", type=int, default=6)
    ap.add_argument("--max-dim", type=int, default=4)
    ap.add_argument("--gate-cap", type=int, default=60)
    ap.add_argument("--time-limit", type=float, default=5.0, help="exact solver time box per point (s)")
    ap.add_argument("--exact-limit", type=int, default=200)
    ap.add_argument("--n-x", type=int, default=3)
    ap.add_argument("--n-f", type=int, default=2)
    ap.add_argument("--n-g", type=int, default=2, help="G values per (F, X): None plus n_g-1 binding caps (1 = no G)")
    ap.add_argument("--p-view", type=float, default=0.15)
    ap.add_argument("--no-shrink", action="store_true")
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--summary", nargs="*", help="summarise these JSONL files (default: all fuzz_*.jsonl) and exit")
    ap.add_argument("--regen", help="SEED:IDX -- print the circuit and exit")
    a = ap.parse_args(argv)
    if a.regen:
        s, i = (int(t) for t in a.regen.split(":"))
        c = gen_circuit(circuit_rng(s, i), max_ops=a.max_ops, max_dim=a.max_dim, gate_cap=a.gate_cap, p_view=a.p_view,
                        name=f"s{s}c{i}")
        print(c.to_python())
        print("# gates", c.n_gates(), "family", family(c))
        return 0
    if a.summary is not None:
        paths = a.summary or sorted(glob.glob(os.path.join(a.out_dir, "fuzz_*.jsonl")))
        print(summarize(paths))
        return 0
    st = run(a.seed, a.n, max_ops=a.max_ops, max_dim=a.max_dim, gate_cap=a.gate_cap, time_limit=a.time_limit,
             exact_limit=a.exact_limit, n_x=a.n_x, n_f=a.n_f, n_g=a.n_g, do_shrink=not a.no_shrink, out_dir=a.out_dir,
             verbose=not a.quiet, max_seconds=a.max_seconds, p_view=a.p_view)
    print(json.dumps(st.to_json(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
