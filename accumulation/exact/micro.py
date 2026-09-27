"""Micro Verity programs for the exact solver.

Each factory builds a :class:`~accumulation.algorithms.registry.BuiltProgram` from the real vocabulary
(:mod:`accumulation.ir.blocks`) with ``CH=1`` so every ``MatmulT`` lowers to scalar ``Mac1`` chains:
``MatmulT{M,N,K,CH=1}`` is ``M*N*(K+2)`` non-``Input`` gates (per output: ``Zero32``, ``K`` x ``Mac1``,
``Round16``), ``AddBatch{Q,K}`` is ``Q*K`` ``Add16`` gates.  Root parameters carry the roles the solver
charges (SPEC §1).  Gate counts quoted below are non-``Input`` gates (the partitioned set).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from accumulation.algorithms.registry import ALGORITHMS, BuiltProgram
from accumulation.configs import MODELS, Workload
from accumulation.ir import blocks as K
from accumulation.ir.prims import V16
from verity_ir import Array, Program, bind
from verity_ir.defs import CompositeDefinition

W = lambda n, k: Array(n, Array(k, V16))


def _mm(M: int, N: int, Kd: int):
    return bind(K.MatmulT, M=M, N=N, K=Kd, CH=1)


def _build(name: str, params, roles: dict[str, str], body: Callable, ret, tokens: int, notes: dict | None = None) -> BuiltProgram:
    """Mirror of ``registry.algorithm(...).build``: wrap ``body`` in a static-free composite and lower it."""
    params = tuple(params)
    defn = CompositeDefinition(f"Acc[{name}]", 1, (), lambda S: (params, ret), lambda B, S, *a: body(B, *a),
                               doc=name, register=False)
    prog = Program(bind(defn))
    roles = {n: roles[n] for n, _ in params}
    return BuiltProgram(name, MODELS["tiny"], Workload(tokens=tokens, seq=tokens, chunk=1), prog, roles,
                        tuple(n for n, _ in params), dict(notes or {}))


def gate_count(bp: BuiltProgram) -> int:
    """Non-``Input`` gates of the lowered circuit."""
    return bp.program.gates - bp.program.input_gates


# ---------------------------------------------------------------------------------------------------------
# factories
# ---------------------------------------------------------------------------------------------------------

def matmul_only(M: int, N: int, K_: int, role_B: str = "accumulated", role_A: str = "token") -> BuiltProgram:
    """``C = A . B^T`` (one ``AccMatmulT``): ``M*N*(K+2)`` gates.  ``A`` is ``M x K`` with role ``role_A``
    (``token`` or ``carried``), ``B`` is ``N x K`` with role ``role_B``."""
    params = (("A", W(M, K_)), ("B", W(N, K_)))

    def body(B, A, Bm):
        return B.call(_mm(M, N, K_), A, Bm)

    return _build(f"matmul_only[M={M},N={N},K={K_},A={role_A},B={role_B}]", params, {"A": role_A, "B": role_B},
                  body, W(M, N), M, {"M": M, "N": N, "K": K_})


def two_matmul_chain(M: int, N1: int, K_: int, N2: int, role_A: str = "token") -> BuiltProgram:
    """``C2 = (A . B1^T) . B2^T``: the second matmul consumes the first's output; both weights accumulated.
    ``M*N1*(K+2) + M*N2*(N1+2)`` gates."""
    params = (("A", W(M, K_)), ("B1", W(N1, K_)), ("B2", W(N2, N1)))

    def body(B, A, B1, B2):
        c1 = B.call(_mm(M, N1, K_), A, B1)
        return B.call(_mm(M, N2, N1), c1, B2)

    return _build(f"two_matmul_chain[M={M},N1={N1},K={K_},N2={N2}]", params,
                  {"A": role_A, "B1": "accumulated", "B2": "accumulated"}, body, W(M, N2), M,
                  {"M": M, "N1": N1, "K": K_, "N2": N2})


def matmul_add(M: int, N: int, K_: int, role_R: str = "token", role_A: str = "token") -> BuiltProgram:
    """``R + A . B^T``: matmul then residual add with an ``M x N`` residual input ``R``.
    ``M*N*(K+2) + M*N`` gates."""
    params = (("A", W(M, K_)), ("B", W(N, K_)), ("R", W(M, N)))

    def body(B, A, Bm, R):
        c = B.call(_mm(M, N, K_), A, Bm)
        return B.call(bind(K.AddBatch, Q=M, K=N), R, c)

    return _build(f"matmul_add[M={M},N={N},K={K_},R={role_R}]", params, {"A": role_A, "B": "accumulated", "R": role_R},
                  body, W(M, N), M, {"M": M, "N": N, "K": K_})


def fixed_then_accum(M: int, N: int, K_: int, N2: int | None = None, role_A: str = "token") -> BuiltProgram:
    """``(A . Wf^T) . Wa^T`` with ``Wf`` (``N x K``) *fixed* and ``Wa`` (``N2 x N``) accumulated: the first
    matmul's weights are free, only its activations and the second matmul's weights are charged.
    ``M*N*(K+2) + M*N2*(N+2)`` gates."""
    N2 = N if N2 is None else N2
    params = (("A", W(M, K_)), ("Wf", W(N, K_)), ("Wa", W(N2, N)))

    def body(B, A, Wf, Wa):
        c1 = B.call(_mm(M, N, K_), A, Wf)
        return B.call(_mm(M, N2, N), c1, Wa)

    return _build(f"fixed_then_accum[M={M},N={N},K={K_},N2={N2}]", params,
                  {"A": role_A, "Wf": "fixed", "Wa": "accumulated"}, body, W(M, N2), M,
                  {"M": M, "N": N, "K": K_, "N2": N2})


# ---------------------------------------------------------------------------------------------------------
# multi-step micro suite (corrected policy model: X = inf, F and G finite; SPEC §1 / THEORY §0.1)
# ---------------------------------------------------------------------------------------------------------
#
# The registry circuits are far above exact-solver scale even at ``tiny`` (``inference-dense`` q=2: 656 gates;
# ``local-sgd`` K=1..3, q=2: 2,888 / 5,776 / 8,664 gates; ``tiny2`` is 2-3x larger).  These factories are the
# smallest circuits with the same *structure*: one linear layer ``d x d``, ``q`` token rows per step.
#
# Work measure: the solver's ``work`` is the primitive ``.work`` summed over gates (``Mac16 = 1``, ``Round16 = 1``,
# ``Add16 = 1``, ``Scale16``/``Sub16`` = 1 each, ``Zero32 = 0``).  This is *identical* to the operator-graph work
# (``OpGraph.ops[i].work_per_copy * copies`` sums to ``FlatCircuit.total_work()``; checked on ``tiny``
# ``inference-dense``: 592 = 592), so ``F`` and ``G`` need no conversion between the solver and the bound modules.
# ``fwd`` below = total work of :func:`micro_inference` at the same ``(q, d)`` = ``q*d*(d+1)`` (MACs + rounds).


def micro_inference(q: int = 1, d: int = 2) -> BuiltProgram:
    """Inference forward of one linear layer: ``y = x . Wf^T`` with ``x`` a ``q x d`` token block and ``Wf`` a
    fixed ``d x d`` weight.  ``q*d*(d+2)`` gates, work ``q*d*(d+1)`` (= ``fwd``).  With ``F, G >= fwd`` the whole
    circuit is one legal RU and ``I* = 2*q*d`` bytes = the token bytes (fixed weights are free)."""
    params = (("x", W(q, d)), ("Wf", W(d, d)))

    def body(B, x, Wf):
        return B.call(_mm(q, d, d), x, Wf)

    return _build(f"micro_inference[q={q},d={d}]", params, {"x": "token", "Wf": "fixed"}, body, W(q, d), q,
                  {"q": q, "d": d, "fwd": q * d * (d + 1)})


def local_sgd_chain(K_steps: int = 2, q: int = 1, d: int = 2) -> BuiltProgram:
    """(a) The accumulation chain: ``K_steps`` chained SGD steps on one ``d x d`` accumulated weight.  Step ``k``
    (``x_k``, ``t_k`` token ``q x d``): ``y_k = x_k W_k^T``; ``dy_k = y_k + t_k`` (stands in for the loss gradient,
    keeps the backward *downstream of the forward*); ``dW_k = dy_k^T x_k`` (``AccMatmulTT``); ``W_{k+1} = W_k -
    lr dW_k`` (``AccSgdUpdate``, ``lr`` a 32-bit seed).  Returns ``W_{K+1}``.  Per step ``q*d*(d+2) + q*d +
    d*d*(q+2) + 2*d*d`` gates (30 for ``q=1, d=2``), work ``q*d*(d+1) + q*d + d*d*(q+1) + 2*d*d`` (24).  Charged
    roots: ``W`` (``2*d*d`` B), ``lr`` (4 B), ``x_k``, ``t_k`` (``2*q*d`` B each)."""
    params = [("W", W(d, d)), ("lr", _V32())]
    for k in range(K_steps):
        params += [(f"x{k}", W(q, d)), (f"t{k}", W(q, d))]

    def body(B, Wt, lr, *xt):
        Wk = Wt
        for k in range(K_steps):
            xk, tk = xt[2 * k], xt[2 * k + 1]
            yk = B.call(_mm(q, d, d), xk, Wk)
            dyk = B.call(bind(K.AddBatch, Q=q, K=d), yk, tk)
            dWk = B.call(bind(K.MatmulTT, M=d, N=d, K=q, CH=1), dyk, xk)
            Wk = B.call(bind(K.SgdUpdate, N=d, K=d), Wk, dWk, lr)
        return Wk

    roles = {"W": "accumulated", "lr": "seed"}
    roles.update({f"x{k}": "token" for k in range(K_steps)})
    roles.update({f"t{k}": "token" for k in range(K_steps)})
    return _build(f"local_sgd_chain[K={K_steps},q={q},d={d}]", params, roles, body, W(d, d), K_steps * q,
                  {"K": K_steps, "q": q, "d": d, "fwd": q * d * (d + 1)})


def fanout_shared_weight(n: int = 4, q: int = 1, d: int = 2) -> BuiltProgram:
    """(b) Wide fan-out of independent matmuls sharing one *produced* weight: ``W' = W - lr Gt`` (``W``
    accumulated ``d x d``, ``Gt`` a token gradient, ``lr`` seed), then ``y_i = x_i W'^T`` for ``n`` independent
    token blocks ``x_i`` (``q x d``).  Returns ``y_0`` (every branch is still part of the circuit).  ``2*d*d +
    n*q*d*(d+2)`` gates.  With ``G`` below ``2*d*d + n*q*d*(d+1)`` the branches cannot all sit with the update, so
    ``W'`` (``2*d*d`` B) is re-imported once per extra RU."""
    params = [("W", W(d, d)), ("Gt", W(d, d)), ("lr", _V32())] + [(f"x{i}", W(q, d)) for i in range(n)]

    def body(B, Wt, Gt, lr, *xs):
        Wp = B.call(bind(K.SgdUpdate, N=d, K=d), Wt, Gt, lr)
        ys = [B.call(_mm(q, d, d), xi, Wp) for xi in xs]
        return ys[0]

    roles = {"W": "accumulated", "Gt": "token", "lr": "seed"}
    roles.update({f"x{i}": "token" for i in range(n)})
    return _build(f"fanout_shared_weight[n={n},q={q},d={d}]", params, roles, body, W(q, d), n * q,
                  {"n": n, "q": q, "d": d, "fwd": q * d * (d + 1)})


def deep_chain(depth: int = 4, q: int = 1, d: int = 2, role_W: str = "fixed") -> BuiltProgram:
    """(c) Deep serial chain: ``x -> W_1 -> W_2 -> ... -> W_depth`` (``q x d`` token in, ``d x d`` weights, all
    ``role_W``).  ``depth*q*d*(d+2)`` gates.  Fused into one RU the last ``Round16`` has ``Up = depth*(d+1)``
    (one output chain per layer, each ``d`` MACs + round, all ``d`` previous-layer outputs feeding each MAC ->
    the whole previous layer); ``F`` below that forces cuts, each importing one ``2*q*d``-byte activation."""
    params = [("x", W(q, d))] + [(f"W{i}", W(d, d)) for i in range(depth)]

    def body(B, x, *Ws):
        h = x
        for Wi in Ws:
            h = B.call(_mm(q, d, d), h, Wi)
        return h

    roles = {"x": "token"}
    roles.update({f"W{i}": role_W for i in range(depth)})
    return _build(f"deep_chain[depth={depth},q={q},d={d},W={role_W}]", params, roles, body, W(q, d), q,
                  {"depth": depth, "q": q, "d": d, "fwd": q * d * (d + 1)})


def dense_rollout(q_roll: int = 4, d: int = 1, layers: int = 1) -> BuiltProgram:
    """Dynamic-rollout analogue (``forward-nonfixed``): ``q_roll`` independent one-token sequences ``x_t`` through
    ``layers`` chained ``d x d`` **accumulated** weights (one dynamic model version, no backward).  One
    ``_mm(1, d, d)`` per token per layer (``d*(d+2)`` gates, work ``d*(d+1)``).  Per-session work ``fwd(Q_inf=1) =
    layers*d*(d+1)``; with ``G = G_hat * fwd`` the rollout needs ``>= q_roll / G_hat`` RUs, each re-importing every
    weight it touches: ``I* = tokens + (#RUs) * 2*d*d*layers`` when whole layers stay together."""
    params = [(f"W{l}", W(d, d)) for l in range(layers)] + [(f"x{t}", W(1, d)) for t in range(q_roll)]

    def body(B, *args):
        Ws, xs = args[:layers], args[layers:]
        outs = []
        for x in xs:
            h = x
            for Wl in Ws:
                h = B.call(_mm(1, d, d), h, Wl)
            outs.append(h)
        return outs[0]

    roles = {f"W{l}": "accumulated" for l in range(layers)}
    roles.update({f"x{t}": "token" for t in range(q_roll)})
    return _build(f"dense_rollout[q={q_roll},d={d},L={layers}]", params, roles, body, W(1, d), q_roll,
                  {"q_roll": q_roll, "d": d, "layers": layers, "fwd": layers * d * (d + 1), "Q_inf": 1})


def moe_rollout(q_roll: int = 4, d: int = 1, experts: int = 2, topk: int = 1, shared: int = 1) -> BuiltProgram:
    """MoE dynamic-rollout analogue (``forward-nonfixed-moe``): ``q_roll`` independent one-token sequences with
    **static balanced routing** -- token ``t`` is routed to experts ``(t + i) mod experts`` for ``i < topk`` -- and
    ``shared`` always-on experts; every expert is a ``d x d`` **accumulated** weight; expert outputs are summed
    (``AddBatch``).  No router matmul (the routing trace is static, as in the registry circuit).  Per token:
    ``(topk + shared)`` matmuls (``d*(d+2)`` gates each) + ``(topk + shared - 1)`` adds (``d`` gates each).
    Per-session work ``fwd(Q_inf=1) = (topk + shared) * d*(d+1)``: useful work per token is the *active* parameter
    count, while the dynamic state is all ``experts + shared`` weights -- the MoE gap the certificate must price
    (``P_l Q`` vs active params x Q)."""
    params = [(f"E{e}", W(d, d)) for e in range(experts)] + [(f"S{s}", W(d, d)) for s in range(shared)] + \
             [(f"x{t}", W(1, d)) for t in range(q_roll)]

    def body(B, *args):
        Es, Ss, xs = args[:experts], args[experts:experts + shared], args[experts + shared:]
        outs = []
        for t, x in enumerate(xs):
            acc = None
            for s in Ss:
                y = B.call(_mm(1, d, d), x, s)
                acc = y if acc is None else B.call(bind(K.AddBatch, Q=1, K=d), acc, y)
            for i in range(topk):
                y = B.call(_mm(1, d, d), x, Es[(t + i) % experts])
                acc = y if acc is None else B.call(bind(K.AddBatch, Q=1, K=d), acc, y)
            outs.append(acc)
        return outs[0]

    roles = {f"E{e}": "accumulated" for e in range(experts)}
    roles.update({f"S{s}": "accumulated" for s in range(shared)})
    roles.update({f"x{t}": "token" for t in range(q_roll)})
    return _build(f"moe_rollout[q={q_roll},d={d},E={experts},k={topk},S={shared}]", params, roles, body, W(1, d), q_roll,
                  {"q_roll": q_roll, "d": d, "experts": experts, "topk": topk, "shared": shared,
                   "fwd": (topk + shared) * d * (d + 1), "Q_inf": 1})


def _V32():
    from accumulation.ir.prims import V32
    return V32


# ---------------------------------------------------------------------------------------------------------
# the suite
# ---------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class MicroSpec:
    name: str
    factory: Callable[..., BuiltProgram]
    kwargs: dict

    def build(self) -> BuiltProgram:
        return self.factory(**self.kwargs)


def _spec(name: str, factory, **kw) -> MicroSpec:
    return MicroSpec(name, factory, kw)


#: every micro program the tests sweep; comments give the non-Input gate count
MICRO_SUITE: tuple[MicroSpec, ...] = (
    _spec("mm_1x1x1", matmul_only, M=1, N=1, K_=1),                       # 3
    _spec("mm_1x1x2", matmul_only, M=1, N=1, K_=2),                       # 4
    _spec("mm_1x1x3", matmul_only, M=1, N=1, K_=3),                       # 5
    _spec("mm_1x2x2", matmul_only, M=1, N=2, K_=2),                       # 8
    _spec("mm_2x1x2", matmul_only, M=2, N=1, K_=2),                       # 8
    _spec("mm_2x1x2_carried", matmul_only, M=2, N=1, K_=2, role_A="carried"),  # 8
    _spec("mm_3x1x1", matmul_only, M=3, N=1, K_=1),                       # 9
    _spec("mm_1x3x1", matmul_only, M=1, N=3, K_=1),                       # 9
    _spec("mm_2x2x1", matmul_only, M=2, N=2, K_=1),                       # 12
    _spec("mm_2x2x2", matmul_only, M=2, N=2, K_=2),                       # 16
    _spec("mm_2x2x3", matmul_only, M=2, N=2, K_=3),                       # 20
    _spec("mm_3x2x2", matmul_only, M=3, N=2, K_=2),                       # 24
    _spec("mm_3x3x2", matmul_only, M=3, N=3, K_=2),                       # 36
    _spec("chain_1x1x1x1", two_matmul_chain, M=1, N1=1, K_=1, N2=1),      # 6
    _spec("chain_1x1x2x1", two_matmul_chain, M=1, N1=1, K_=2, N2=1),      # 7
    _spec("chain_1x2x1x1", two_matmul_chain, M=1, N1=2, K_=1, N2=1),      # 10
    _spec("chain_2x1x1x1", two_matmul_chain, M=2, N1=1, K_=1, N2=1),      # 12
    _spec("chain_1x2x2x2", two_matmul_chain, M=1, N1=2, K_=2, N2=2),      # 16
    _spec("chain_2x2x2x2", two_matmul_chain, M=2, N1=2, K_=2, N2=2),      # 32
    _spec("mmadd_1x1x1", matmul_add, M=1, N=1, K_=1),                     # 4
    _spec("mmadd_1x1x2", matmul_add, M=1, N=1, K_=2),                     # 5
    _spec("mmadd_2x1x1", matmul_add, M=2, N=1, K_=1),                     # 8
    _spec("mmadd_1x2x2", matmul_add, M=1, N=2, K_=2),                     # 10
    _spec("mmadd_1x2x2_carried", matmul_add, M=1, N=2, K_=2, role_R="carried"),  # 10
    _spec("mmadd_2x2x2", matmul_add, M=2, N=2, K_=2),                     # 20
    _spec("fixacc_1x1x1", fixed_then_accum, M=1, N=1, K_=1),              # 6
    _spec("fixacc_1x1x2", fixed_then_accum, M=1, N=1, K_=2),              # 7
    _spec("fixacc_2x1x1", fixed_then_accum, M=2, N=1, K_=1),              # 12
    _spec("fixacc_1x2x1", fixed_then_accum, M=1, N=2, K_=1),              # 14
    _spec("fixacc_1x2x2", fixed_then_accum, M=1, N=2, K_=2),              # 16
    _spec("fixacc_2x2x1", fixed_then_accum, M=2, N=2, K_=1),              # 28
    _spec("fixacc_2x2x2", fixed_then_accum, M=2, N=2, K_=2),              # 32
)


def micro_programs(max_gates: int = 40, min_gates: int = 0) -> list[tuple[str, BuiltProgram]]:
    """Build the suite and keep programs with ``min_gates <= gates <= max_gates`` (non-``Input`` gates)."""
    out = []
    for s in MICRO_SUITE:
        bp = s.build()
        if min_gates <= gate_count(bp) <= max_gates:
            out.append((s.name, bp))
    return out


def smallest_registry_programs(limit: int = 40, chunk: int = 1, models: tuple[str, ...] = ("tiny", "tiny2")) \
        -> tuple[list[tuple[str, str, BuiltProgram, int]], dict[str, str]]:
    """Registry algorithms built at the tiny model configs with ``Workload(tokens=2, seq=2)`` whose
    circuits have ``<= limit`` non-``Input`` gates.  Returns ``(kept, skipped)`` where ``kept`` is a list of
    ``(algorithm, model, bp, gates)`` and ``skipped`` maps ``"algo@model"`` to the reason (build error or gate
    count).  At these dimensions every registry algorithm is far above the exact-solver scale, so ``kept``
    is expected to be empty; the micro factories above are the test bed."""
    kept: list[tuple[str, str, BuiltProgram, int]] = []
    skipped: dict[str, str] = {}
    for mname in models:
        cfg = MODELS[mname]
        for aname, alg in ALGORITHMS.items():
            wl = Workload(tokens=2, seq=2, chunk=chunk, population=1, rank=1, local_steps=1)
            key = f"{aname}@{mname}"
            try:
                bp = alg.build(cfg, wl)
                n = gate_count(bp)
            except Exception as e:  # noqa: BLE001 - report, do not hide
                skipped[key] = f"build failed: {type(e).__name__}: {e}"
                continue
            if n <= limit:
                kept.append((aname, mname, bp, n))
            else:
                skipped[key] = f"{n} gates > {limit}"
    return kept, skipped


__all__ = [
    "MICRO_SUITE",
    "MicroSpec",
    "deep_chain",
    "fanout_shared_weight",
    "fixed_then_accum",
    "local_sgd_chain",
    "micro_inference",
    "gate_count",
    "matmul_add",
    "matmul_only",
    "micro_programs",
    "smallest_registry_programs",
    "two_matmul_chain",
]
