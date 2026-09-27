r"""Certified lower bounds on the minimum runtime-input volume ``I*(P; F, X)`` (SPEC §2, v2 closure-budget
model).

``lower_bound(g, F, X, program=...)`` returns ``L`` with ``L <= I*(P; F, X)`` for *every* legal partition of
the program into replay units (RUs), where an RU may take at most ``X`` bytes of non-fixed input:

    L = max(L_source,  L_cap + L_token_seed)

* ``L_source`` -- bytes of every non-fixed root parameter read by some gate (each enters at least one RU);
  ``state_floor`` is its ``accumulated | carried`` part, ``token_seed`` the rest.
* ``L_cap = sum_o L_o(X)`` -- the Loomis-Whitney import charge of every matmul op (§2.1) under the operand
  cost model of §2.2 (credits ``kappa``, closures ``Wfree / Welt``, sharing ``share``).  Non-matmul ops are
  charged 0.

Whenever the model has a choice, the choice that makes ``L`` smaller is taken (notes are recorded in
``LowerBound.notes``).  ``F`` is recorded but unused (§2.3 not implemented; ignoring ``F`` only weakens ``L``).

Proof sketch of soundness
=========================

Fix a legal partition ``Pi``; ``in(R)`` is the input byte set of RU ``R`` and ``I = sum_R |in(R)|``.  Tensors
are laid out in *rows* (``rowlen(t)`` elements: ``N`` for a matmul output, ``K / FF / V / D`` for the
row-structured kinds); ``w_t = width/8``; ``share(t) = g.share(t)`` (max per-element consumer multiplicity,
an upper bound on the true one -- the safe direction).

**Credits.**  For every tensor ``t`` we define two lower bounds on *row-specific* imported bytes of ``R``:

* ``kappa_e(t)`` -- bytes of ``in(R)`` *backing* any single element of ``t`` that is present in ``R``
  (imported, or produced by gates of ``R``);
* ``P(t)`` -- bytes backing a *full row* of ``t`` present in ``R`` (all ``rowlen(t)`` elements).

"Backing" is a measure on ``in(R)`` with the *claim discipline*: for every tensor a fraction ``theta_t`` of
the backing of an element may be claimed directly by the matmul ops that read the element (the ``alpha /
beta`` charges of §2.1: each of the ``<= share(t)`` readers claims ``theta_t kappa(t) / share(t)``), and the
remaining ``1 - theta_t`` is handed down, divided by ``share(t)``, to *each* consumer that produces something
from it (``inh(t) = (1 - theta_t) kappa_e(t) / share(t)`` per element, ``(1 - theta_t) P(t) / share(t)`` per
row).  Backing sets of distinct elements of the same tensor are disjoint, and a byte handed down is never
also claimed directly, so by induction over the generation DAG the total of all claims of all ops in ``R`` is
at most ``|in(R)| <= X``.  Tensors without a matmul reader get ``theta = 0`` (nothing to claim);
``accumulated | carried`` root parameters that are read by a matmul get ``theta = 1`` (SPEC: weights are
imported and charged in full by their readers; no credit is inherited from them, because one weight row
serves unboundedly many rows).  Otherwise ``theta`` is a grid value per producer kind of the activation (best
global value, then a coordinate ascent per kind; every fixed choice is sound, so the search only tightens).

The recursion (an element / a row present in ``R`` was imported, or was produced in ``R`` from operands
present in ``R``; the credit is the *minimum* over the two, so it holds for every element):

* Non-free root parameter: every element is an import: ``kappa_e = w``, ``P = rowlen w``.  Free roots
  (``fixed | token | seed``): 0.  Gathers from a table (embedding), ``prim:*``, ``scan:*``, unknown kinds: 0
  (one imported table row / column serves unboundedly many outputs).
* Matmul ``t = A B^T`` (contraction ``K``, ``L = N`` columns per row): an element *produced* in ``R`` (all its
  MACs in ``R``) needs a full ``K``-row of the ``A`` operand and a full ``K``-row of the ``B`` operand in
  ``R``.  Each operand row present in ``R`` is backed by ``per`` disjoint bytes of ``in(R)``: ``K w`` for a
  non-free root (every leaf an import), ``max(P(u), K kappa_e(u))`` for an activation ``u`` (``P(u)`` only when
  the operand is certified to read whole tensor rows in order -- ``K == rowlen(u)``, identity view on the
  program's reference descriptors; ``K kappa_e`` holds for any ``K`` distinct elements).  Hence ``R`` holds
  at most ``n_u = floor(X / per_u)`` rows of that operand (unbounded when ``per_u = 0``).  Consequences:
  (i) at most ``n_B`` *columns* of ``t`` are produced in ``R``, so of a full row of ``t`` present in ``R`` at
  least ``(L - n_B)^+`` elements were imported finished (``w``) or completed from imported 32-bit partial sums
  (``>= 4`` bytes, of which the op's partial-sum charge claims ``theta_gamma * 4``; the rest, ``w' = min(w,
  (1 - theta_gamma) 4)``, is credit); (ii) one ``A`` row yields at most ``min(N, n_B)`` produced elements and
  one ``B`` row at most ``min(M, n_A)``, so a produced element inherits ``pool_A / min(N, n_B) + pool_B /
  min(M, n_A)`` with ``pool_u = (1 - theta_u) P(u) / share(u)`` for a certified activation row, ``(1 -
  theta_u) w K / share(u)`` for a root param (0 with the default ``theta = 1``), 0 otherwise.  Thus
  ``kappa_e(t) = min(w', pool_A / min(N, n_B) + pool_B / min(M, n_A))`` and ``P(t) = min(L w', (L - n_B)^+ w' +
  min(n_B, L) kappa_e)``; when ``n_A = 0`` or ``n_B = 0`` nothing can be produced and ``kappa_e = w'``.  The
  SPEC's root-``B`` rule ``inh(A) K^2 w_B / X`` is the ``pool_A / (X / (K w_B))`` special case; ``MatmulTT``
  operands are read along columns and never certified.
* Element-wise producers (``add, mul, swiglu, gain, rowscale, scale, mask, perturb, sgdupdate, esupdate,
  combine, ...``): one output element needs one element of every *row-aligned* input (whole tensor read in
  order with the same row length; per-row scalars count as one element per row): ``kappa_e = min(w, sum_in
  inh(in))``, ``P = min(L w, sum_in (1 - theta) P(in) / share(in))``.  Broadcast / unaligned inputs give 0.
* Row ops (``rmsnorm, softmax, lossgrad, rowdot``, row sums / means): one output element needs the full input
  row(s): ``kappa_e = min(w, sum_in (1 - theta) P(in) / (share(in) rowlen(t)))``, ``P = min(L w, sum_in
  (1 - theta) P(in) / share(in))``.
* Reductions over rows (``colsum``): at least one input element per output: ``kappa_e = min(w, inh(in))``,
  ``P = min(L w, (1 - theta) P(in) / share(in))``.

The SPEC's ``kappa_gen = inh(A) K^2 w_B / X`` is the special case ``P(A) = K kappa_e(A)`` of the matmul rule;
the row pools are what lets the recursion start: the first matmul whose weight slice exceeds ``X`` forces
``(L - n_B) w'`` bytes of imports per output row even when its operands are free, and those bytes flow down the
residual stream.  ``kappa_e`` is forced to 0 when ``gen(t)`` (below) holds -- consistent with the recursion,
which already yields 0 there, and required by the SPEC.

**Closures and ``gen``.**  ``Wfree(t)`` / ``Welt(t)`` are sets of ``(non-free root param, leaf interval)``
needed by any RU to produce one row / one element of ``t`` from free inputs (§2.2 rules per producer kind,
union semantics).  They are *lower bounds* on the true closure: over-approximate ``Edge.ranges`` are clipped
to ``leaves_per_copy`` leaves and every "one row / one element / k rows" item is placed canonically at the
start of the slice (so unions can only shrink), and a matmul operand that is not certified to be read in full
rows contributes the closure of ``K`` distinct elements instead of ``Wfree``.  For an activation ``B`` one
output row needs *every* element of the copy's ``B`` operand and one output element a ``K``-segment of it;
the closure of ``n`` distinct elements of an op tensor is followed through element-wise producers (``n``
distinct outputs need ``n`` distinct elements of each per-element input, so ``n`` leaves of a per-element root
param -- this is what makes ES / local-SGD produced weights ``W' = f(W, ...)`` carry the whole ``W`` slice into
the closures of their matmul outputs) and is one element for every other producer.  ``gen(t) := |Welt(t)| <=
X`` therefore never wrongly says "cannot generate"; when it says "can", ``kappa = alpha = 0`` (charging nothing
is always sound).  Exception (SPEC "inheritance from root-param weights"): a *root-like* tensor -- produced
element-wise from a per-element non-free root param or another root-like tensor (``perturb``, ``sgdupdate``)
-- has a per-element closure that is injective (one imported ``W`` element per ``W'`` element), so its
recursion credit ``kappa(W') = min(w, (1 - theta_W) w_W / share(W))`` is sound and is kept; ``gen`` is
reported ``False`` for it.  The credit recursion itself never relies on ``gen`` (free inputs carry 0 credit
and gathers give 0), so forcing ``kappa = 0`` on ``gen`` tensors is pure SPEC conservatism.

**Per-op Loomis-Whitney charge (§2.1).**  Fix a matmul op ``o`` with ``Q_o = M copies`` activation rows,
``N`` weight rows, contraction ``K`` (copies merged into one ``Q_o x N x K`` product: merging identifies the
``B`` operands of different copies, which can only reduce the number of distinct ``B`` elements counted, hence
sound; ``A`` must not be shared between copies -- when it is, ``alpha = 0`` for that op).  For an RU ``R`` let
``S_R`` be the set of MAC triples ``(i, j, k)`` of ``o`` executed in ``R``, ``w_R = |S_R|``, and ``a_R, b_R,
c_R`` the sizes of its projections (distinct ``A`` elements, ``B`` elements, outputs touched).

(a) Loomis-Whitney: ``w_R <= sqrt(a_R b_R c_R)``; also ``w_R <= a_R N, b_R Q_o, c_R K`` and ``w_R >= max(a_R,
    b_R, c_R)``.
(b) Claims: ``o`` claims ``alpha a_R + beta b_R`` with ``alpha = theta_A kappa(A) / share(A)`` (``w_A /
    share(A)`` for a non-free root ``A``), ``beta = w_B / share(B)`` for a non-free root ``B``, ``0`` for a fixed
    one, ``theta_B kappa(B) / share(B)`` for an activation; by the claim discipline the claims of all ops in ``R``
    sum to at most ``|in(R)| <= X``, hence ``alpha a_R + beta b_R <= X``.
(c) Partial sums: an output element whose MACs are spread over ``r`` RUs forces ``r - 1`` 32-bit partial sums
    into RUs; ``o`` claims ``gamma = theta_gamma 4`` of each (the remainder is the ``w'`` credit above), so
    ``I >= sum_o [ sum_R (alpha a_R + beta b_R + gamma c_R) - gamma Q_o N ]``.
(d) Reduction to rectangular tiles: with ``a' = w_R / b_R``, ``b' = w_R / a_R``, ``k' = w_R / c_R`` the charge
    per MAC equals ``alpha / b' + beta / a' + gamma / k'`` exactly, ``1 <= a' <= Q_o``, ``1 <= b' <= N``,
    ``1 <= k' <= K`` and ``k' (alpha a' + beta b') <= alpha a_R + beta b_R <= X``.  Hence
    ``L_o = Q_o N K min_{real tiles} (alpha / b' + beta / a' + gamma (1/k' - 1/K))`` -- the minimum over
    **real** tiles (the integer minimum would not be a lower bound), computed exactly by :func:`min_cost_per_mac`
    (closed form for fixed ``k``, finite candidate set for ``k``).  ``alpha + beta > X`` means no RU can
    execute one MAC: the program is infeasible at this ``X`` (sentinel ``INFEASIBLE``).

**Aggregation.**  ``L_source <= I``.  ``L_cap + L_token_seed <= I``: every claim above is on bytes backing
``accumulated | carried`` leaves, op outputs or partial sums, never ``token | seed`` leaves (their credit is
0), so token/seed bytes are additional.  The two bounds are combined with ``max``.

Everything holds for any legal partition, including ones that recompute values: Loomis-Whitney counts
distinct elements touched per RU, and the credits are per element present in ``R`` however it got there.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Any

from accumulation.bounds.adw import ADW, STATE_ROLES
from accumulation.bounds.adw import adw as compute_adw
from accumulation.graph.opgraph import Edge, Op, OpGraph, Tensor

__all__ = [
    "GAMMA_FULL",
    "G_GRID",
    "INFEASIBLE",
    "THETA_GAMMA",
    "THETA_GRID",
    "LowerBound",
    "lower_bound",
    "lower_coarse",
    "matmul_charge",
    "min_cost_per_mac",
]

#: bytes of a 32-bit partial sum (the MatmulT accumulator)
GAMMA_FULL: float = 4.0
#: fraction of a partial sum claimed by the op's partial-sum charge (SPEC: in [1/2, 3/4]); the rest is credit
THETA_GAMMA: float = 0.5
#: candidate split factors for activations read by matmuls (the best one is kept; each is sound)
THETA_GRID: tuple[float, ...] = (0.25, 0.5, 0.75, 1.0)
#: per-op charge reported when no RU can execute even one MAC of the op (``alpha + beta > X``)
INFEASIBLE: int = 1 << 62
#: initial log-grid points in ``k``, refinement steps and relative gap tolerance of the certified tile bound
#: under a total-work cap ``G`` (branch and bound; see :func:`min_cost_per_mac`)
G_GRID: int = 32
G_REFINE: int = 150
G_TOL: float = 1e-6

FREE_ROLES: frozenset[str] = frozenset({"fixed", "token", "seed"})

#: producers whose output element needs one element of each row-aligned input
ELEMENTWISE_KINDS: frozenset[str] = frozenset({
    "add", "mul", "swiglu", "gain", "rowscale", "scale", "mask", "causalmask", "perturb", "sgdupdate",
    "esupdate", "combine", "swiglubwd", "softmaxbwd", "rowscalebroadcast",
})
#: producers whose output element needs the full input row
ROW_KINDS: frozenset[str] = frozenset({"rmsnorm", "softmax", "lossgrad", "rowdot", "rmsnormbwd", "sum", "mean"})
#: reductions over rows (one output row from all input rows)
COLRED_KINDS: frozenset[str] = frozenset({"colsum"})
#: gathers / routing: no credit, closure = one table row
GATHER_KINDS: frozenset[str] = frozenset({"embed", "gatherrows", "scatteradd", "topk", "router"})

#: statics key giving the row length of the output, per kind (None = one element per row)
_ROWLEN_KEY: dict[str, str | None] = {
    "matmul": "N", "rmsnorm": "K", "softmax": "K", "add": "K", "mul": "K", "gain": "K", "rowscale": "K",
    "scale": "K", "mask": "K", "causalmask": "K", "colsum": "K", "sgdupdate": "K", "esupdate": "K",
    "perturb": "K", "rowscalebroadcast": "K", "lossgrad": "V", "swiglu": "FF", "swiglubwd": "FF", "embed": "D",
    "rowdot": None, "sum": None, "mean": None, "combine": "K", "softmaxbwd": "K", "rmsnormbwd": "K",
}

Closure = dict[int, tuple[tuple[int, int], ...]]     # param tid -> merged inclusive leaf intervals


@dataclass
class LowerBound:
    """Result of :func:`lower_bound`.  All byte quantities are ``int``."""
    total: int                                   # L = max(source, cap + token_seed)
    source: int                                  # L_source: bytes of non-fixed root params that are read
    cap: int                                     # L_cap: sum of per-op Loomis-Whitney charges
    per_op: dict[int, int]                       # op id -> L_o (0 for non-matmuls)
    alpha_eff: dict[int, float]                  # tensor id -> per-reader direct charge theta*kappa/share
    kappa: dict[int, float]                      # tensor id -> per-element credit (0 when gen)
    gen: dict[int, bool]                         # tensor id -> |Welt| <= X (False for root-like produced weights)
    welt_bytes: dict[int, int]                   # tensor id -> |Welt(t)|
    wfree_bytes: dict[int, int]                  # tensor id -> |Wfree(t)|
    share: dict[int, int]                        # tensor id -> g.share(t)
    theta: dict[int, float]                      # tensor id -> split factor used
    pool: dict[int, float]                       # tensor id -> row credit P(t) (bytes per row)
    op_params: dict[int, dict[str, Any]]         # op id -> {alpha, beta, gamma, Q, N, K, A, B, ...}
    notes: list[str] = field(default_factory=list)
    worst_ru: dict[str, Any] = field(default_factory=dict)   # THEORY §0.1 worst-RU diagnostic (see _worst_ru)
    state_floor: int = 0                         # accumulated + carried part of ``source``
    token_seed: int = 0                          # token + seed part of ``source``
    kappa_op: dict[int, float] = field(default_factory=dict)  # op id -> MACs per charged byte
    kappa_L: float = 0.0                         # |M| / total  (|M| = target_macs)
    tiles: dict[int, dict] = field(default_factory=dict)      # op id -> optimiser detail (a, b, k, binding, ...)
    theta_act: float = 0.5                       # best single grid value for all activations
    theta_kind: dict[str, float] = field(default_factory=dict)  # producer kind -> theta actually used
    target_macs: int = 0                         # |M|: credited_macs (training) or all_macs (inference)
    F: int = 0
    X: int = 0
    G: int | None = None                         # total-work cap used (None = unbounded)
    infeasible: bool = False                     # some op cannot run in any RU of size X
    # certificate metadata (lower_coarse): ``total`` is always the proven dual bound, never an incumbent
    gap: float = 0.0                             # relative dual gap of the price LP (0 = proven optimum / closed form)
    root_read: int = 0                           # bytes of dynamic roots charged once (the one-time "P read")
    recurring: int = 0                           # total - root_read - token bytes
    certified: bool = True                       # an independent re-check of the certificate passed
    detail: dict[str, Any] = field(default_factory=dict)   # block-model parameters used (jsonable)


# ---------------------------------------------------------------------------------------------------------
# per-op optimisation (unchanged from v1: exact real-tile minimum of the §2.1 problem)
# ---------------------------------------------------------------------------------------------------------

def _inner(alpha: float, beta: float, Y: float, Q: int, N: int) -> tuple[float, float, float]:
    """``min alpha/b + beta/a`` over real ``1 <= a <= Q``, ``1 <= b <= N`` with ``alpha a + beta b <= Y``.

    The caller guarantees feasibility (``alpha + beta <= Y``).  Returns ``(value, a, b)``.  The objective is
    convex and separable and the constraint is linear, so the optimum spends equally on both operands
    (``alpha a = beta b``) up to clipping at the boxes; the equal spend ``s`` solves the piecewise-linear
    equation ``clip(s, alpha, alpha Q) + clip(s, beta, beta N) = Y``."""
    if alpha <= 0.0 and beta <= 0.0:
        return 0.0, float(Q), float(N)
    if alpha <= 0.0:                      # b does not enter the objective: b = 1, a free -> Q
        return beta / Q, float(Q), 1.0
    if beta <= 0.0:
        return alpha / N, 1.0, float(N)
    if alpha * Q + beta * N <= Y:         # both caps affordable
        return alpha / N + beta / Q, float(Q), float(N)
    lo1, hi1, lo2, hi2 = alpha, alpha * Q, beta, beta * N

    def h(s: float) -> float:
        return min(max(s, lo1), hi1) + min(max(s, lo2), hi2)

    pts = sorted({lo1, hi1, lo2, hi2})
    s = pts[-1]
    if Y <= h(pts[0]):
        s = pts[0]
    else:
        for i in range(len(pts) - 1):
            h0, h1 = h(pts[i]), h(pts[i + 1])
            if h0 <= Y <= h1:
                s = pts[i] if h1 == h0 else pts[i] + (Y - h0) * (pts[i + 1] - pts[i]) / (h1 - h0)
                break
    a = min(max(s / alpha, 1.0), float(Q))
    b = min(max(s / beta, 1.0), float(N))
    return alpha / b + beta / a, a, b


def _inner_G(alpha: float, beta: float, Y: float, P: float, Q: int, N: int) -> tuple[float, float, float]:
    """:func:`_inner` with the extra work constraint ``a b <= P`` (``P = G / k``).  Returns ``(inf, 0, 0)``
    when infeasible.  The unconstrained optimum is kept when it satisfies ``a b <= P``; otherwise (objective
    decreasing in both ``a`` and ``b``, feasible set convex) the optimum lies on ``a b = P`` and the problem is
    one-dimensional: ``g(a) = alpha a / P + beta / a`` (convex) on the interval cut out by the boxes and by
    ``alpha a + beta P / a <= Y`` (a quadratic in ``a``), minimised at the clipped ``a* = sqrt(beta P / alpha)``."""
    if P < 1.0:
        return math.inf, 0.0, 0.0
    if alpha + beta <= Y:
        v, a, b = _inner(alpha, beta, Y, Q, N)
        if a * b <= P * (1.0 + 1e-12):
            return v, a, b
    else:
        return math.inf, 0.0, 0.0
    lo, hi = max(1.0, P / N), min(float(Q), P)
    if alpha > 0.0:
        disc = Y * Y - 4.0 * alpha * beta * P
        if disc < 0.0:
            return math.inf, 0.0, 0.0
        r = math.sqrt(disc)
        lo, hi = max(lo, (Y - r) / (2.0 * alpha)), min(hi, (Y + r) / (2.0 * alpha))
        a_star = math.sqrt(beta * P / alpha) if beta > 0.0 else lo
    else:                                        # g(a) = beta / a: take a as large as allowed
        lo = max(lo, beta * P / Y) if Y > 0 else math.inf
        a_star = hi
    if lo > hi * (1.0 + 1e-12):
        return math.inf, 0.0, 0.0
    a = min(max(a_star, lo), hi)
    b = P / a
    return alpha / b + beta / a, a, b


def _x_candidates(alpha: float, beta: float, gamma: float, Q: int, N: int, X: float, kmax: float, grid: int
                  ) -> list[float]:
    """Candidate ``k`` values that contain the exact minimiser of the X-only problem (see
    :func:`min_cost_per_mac`), plus a coarse log grid."""
    cands: list[float] = [1.0, kmax]
    if kmax > 1.0:
        ratio = kmax ** (1.0 / grid)
        cands.extend(ratio ** i for i in range(1, grid))
    if alpha > 0.0 and beta > 0.0:
        lo1, hi1, lo2, hi2 = alpha, alpha * Q, beta, beta * N

        def h(s: float) -> float:
            return min(max(s, lo1), hi1) + min(max(s, lo2), hi2)

        pts = sorted({lo1, hi1, lo2, hi2})
        for Yb in (h(p) for p in pts):                      # piece boundaries
            if Yb > 0:
                cands.append(X / Yb)
        for i in range(len(pts) - 1):                       # interior stationary points
            s_lo, s_hi = pts[i], pts[i + 1]
            if s_hi <= s_lo:
                continue
            s_mid = 0.5 * (s_lo + s_hi)
            n_free, c0, c2 = 0, 0.0, 0.0
            if s_mid < lo1:                                 # a = 1
                c0 += beta / 1.0
                c2 += alpha
            elif s_mid > hi1:                               # a = Q
                c0 += beta / Q
                c2 += alpha * Q
            else:
                n_free += 1
            if s_mid < lo2:                                 # b = 1
                c0 += alpha / 1.0
                c2 += beta
            elif s_mid > hi2:                               # b = N
                c0 += alpha / N
                c2 += beta * N
            else:
                n_free += 1
            if n_free == 0:
                continue
            c1 = n_free * n_free * alpha * beta
            denom = math.sqrt(c1 * X) + math.sqrt(gamma) * c2
            if denom > 0:
                k_star = math.sqrt(gamma) * X / denom
                k_lo, k_hi = X / h(s_hi), X / h(s_lo)
                cands.append(min(max(k_star, k_lo), k_hi))
    return [min(max(k, 1.0), kmax) for k in cands]


def _binding(alpha: float, beta: float, a: float, b: float, k: float, X: float, G: float | None) -> str:
    tight = []
    if k * (alpha * a + beta * b) >= X * (1.0 - 1e-6):
        tight.append("X")
    if G is not None and a * b * k >= G * (1.0 - 1e-6):
        tight.append("G")
    return "+".join(tight) if tight else "box"


def min_cost_per_mac(alpha: float, beta: float, gamma: float, Q: int, N: int, K: int, X: float,
                     grid: int = 16, G: float | None = None) -> tuple[float, dict]:
    """Certified minimum of the SPEC §2.1 tile problem over **real** tiles

        min  alpha/b + beta/a + gamma (1/k - 1/K)
        s.t. k (alpha a + beta b) <= X,  [a b k <= G,]  1 <= a <= Q,  1 <= b <= N,  1 <= k <= K.

    Returns ``(value, detail)``; ``value = math.inf`` when infeasible (``alpha + beta > X`` or ``G < 1``).
    Without ``G`` (or when ``G >= Q N K``, where it cannot bind) the value is the *exact* minimum (below).
    With a binding ``G`` the value is a certified lower bound: for fixed ``k`` the inner problem is exact
    (:func:`_inner_G`); its optimum ``h(k)`` is non-decreasing in ``k`` (both budgets ``X/k``, ``G/k``
    shrink), so on a grid interval ``[k_i, k_{i+1}]`` the cost is ``>= h(k_i) + gamma / k_{i+1}``; the
    reported value is the minimum of that expression over a fixed (``G``-independent) dense log grid that also
    contains the X-only candidates.  Slack is at most ``gamma / k_i (1 - k_i / k_{i+1})`` -- a fraction of a
    percent of the partial-sum term -- and only ever *lowers* the value.  The AM-GM form
    ``3 (alpha beta gamma / G)^{1/3}`` of THEORY §0.1 is the interior special case of this minimum.

    For fixed ``k`` the inner problem is solved in closed form (:func:`_inner`).  Its optimal value ``g(Y)``
    as a function of the budget ``Y = X/k`` is piecewise ``c0 + c1 / (Y - c2)`` (``c1 >= 0``, ``c2 >= 0``): on a
    piece where ``n`` of the two operands are un-clipped (equal spend ``s`` each) and the others sit at a box
    bound, ``Y = n s + c2`` and ``g = c0 + n^2 alpha beta / (Y - c2)``.  The pieces are delimited by the
    ``s``-breakpoints ``{alpha, alpha Q, beta, beta N}``.  Substituting ``Y = X/k``, on each piece
    ``f(k) = c0 + c1 k / (X - c2 k) + gamma/k - gamma/K`` is convex, with stationary point
    ``k* = sqrt(gamma) X / (sqrt(c1 X) + sqrt(gamma) c2)``; the global minimum is therefore attained at one of:
    the clipped stationary point of every piece, every piece boundary, ``k = 1`` and ``k = kmax``.  All
    candidates are evaluated with the exact ``f`` and the smallest value is returned (a coarse log grid is
    evaluated too as a cheap guard).  Every evaluated point is a feasible tile, so the result can never lie
    *below* the true minimum, and completeness of the candidate set makes it equal to it."""
    if alpha <= 0.0 and beta <= 0.0:
        return 0.0, {"a": Q, "b": N, "k": K, "cost": 0.0, "alpha": alpha, "beta": beta, "gamma": gamma,
                     "binding": "none", "work": float(Q) * N * K}
    need = alpha + beta
    kmax = min(float(K), X / need)
    if G is not None:
        if G < 1.0:
            return math.inf, {"infeasible": True, "alpha": alpha, "beta": beta, "binding": "G"}
        if G >= float(Q) * N * K:
            G = None                             # cannot bind: use the exact X-only path
        else:
            kmax = min(kmax, float(G))
    if kmax < 1.0:
        return math.inf, {"infeasible": True, "alpha": alpha, "beta": beta, "binding": "X"}

    cands = sorted(set(_x_candidates(alpha, beta, gamma, Q, N, X, kmax, grid)))
    # exact X-only minimum: the minimiser is one of the candidates (also a valid lower bound under any G)
    x_val, best_a, best_b, best_k = math.inf, 0.0, 0.0, 0.0
    for k in cands:
        v, a, b = _inner(alpha, beta, X / k, Q, N)
        v += gamma / k - gamma / K
        if v < x_val:
            x_val, best_a, best_b, best_k = v, a, b, k
    if G is None:
        detail = {"a": best_a, "b": best_b, "k": best_k, "cost": x_val, "alpha": alpha, "beta": beta,
                  "gamma": gamma, "binding": _binding(alpha, beta, best_a, best_b, best_k, X, None),
                  "work": best_a * best_b * best_k, "exact": True}
        return x_val, detail

    # certified bound with the work cap: branch and bound over k.  An interval [k0, k1] has lower bound
    # h(k0) + gamma/k1 (h non-decreasing, gamma/k decreasing) and the feasible point k0 gives the upper bound
    # f(k0); the interval with the smallest lower bound is split at its geometric midpoint until the gap closes.
    n = max(G_GRID, 2)
    ks = set(cands)
    if kmax > 1.0:
        ratio = kmax ** (1.0 / n)
        ks.update(min(ratio ** i, kmax) for i in range(1, n))
    ks.update((1.0, kmax))
    hcache: dict[float, tuple[float, float, float]] = {}

    def H(k: float) -> tuple[float, float, float]:
        r = hcache.get(k)
        if r is None:
            r = hcache[k] = _inner_G(alpha, beta, X / k, G / k, Q, N)
        return r

    grid_k = sorted(ks)
    ub, best_tile = math.inf, (0.0, 0.0, 0.0)           # best feasible f and its tile
    heap: list[tuple[float, float, float]] = []          # (lower bound, k0, k1)
    for i, k in enumerate(grid_k):
        h, a, b = H(k)
        if math.isinf(h):
            break                                        # h non-decreasing: nothing feasible beyond this k
        fk = h + gamma / k - gamma / K
        if fk < ub:
            ub, best_tile = fk, (a, b, k)
        k1 = grid_k[i + 1] if i + 1 < len(grid_k) else k
        heapq.heappush(heap, (h + gamma / k1 - gamma / K, k, k1))
    for _ in range(G_REFINE):
        if not heap:
            break
        lb0, k0, k1 = heap[0]
        if k1 <= k0 * (1.0 + 1e-12) or ub - lb0 <= G_TOL * abs(ub):
            break
        heapq.heappop(heap)
        km = math.sqrt(k0 * k1)
        h0, _, _ = H(k0)
        hm, am, bm = H(km)
        heapq.heappush(heap, (h0 + gamma / km - gamma / K, k0, km))
        if not math.isinf(hm):
            fm = hm + gamma / km - gamma / K
            if fm < ub:
                ub, best_tile = fm, (am, bm, km)
            heapq.heappush(heap, (hm + gamma / k1 - gamma / K, km, k1))
    best_val = min(heap)[0] if heap else math.inf
    best_val = min(best_val, ub)
    if math.isinf(best_val):
        return math.inf, {"infeasible": True, "alpha": alpha, "beta": beta, "binding": "G"}
    best_val = max(best_val, x_val)              # G only tightens: never report below the exact X-only value
    a, b, k = best_tile
    detail = {"a": a, "b": b, "k": k, "cost": best_val, "tile_cost": ub, "alpha": alpha, "beta": beta,
              "gamma": gamma, "binding": _binding(alpha, beta, a, b, k, X, G), "work": a * b * k, "exact": False}
    return best_val, detail


def matmul_charge(alpha: float, beta: float, Q: int, N: int, K: int, X: float,
                  gamma: float = THETA_GAMMA * GAMMA_FULL, G: float | None = None) -> tuple[int, dict]:
    """``L_o(X, G) = floor(Q N K * min cost/MAC)`` for one matmul (all copies merged), or ``INFEASIBLE``."""
    if alpha <= 0.0 and beta <= 0.0:
        return 0, {"a": Q, "b": N, "k": K, "cost": 0.0, "alpha": alpha, "beta": beta, "gamma": gamma,
                   "binding": "none", "work": float(Q) * N * K}
    lb, detail = min_cost_per_mac(alpha, beta, gamma, Q, N, K, X, G=G)
    if math.isinf(lb):
        return INFEASIBLE, detail
    return max(0, math.floor(Q * N * K * lb)), detail


# ---------------------------------------------------------------------------------------------------------
# graph helpers
# ---------------------------------------------------------------------------------------------------------

def _consumers(g: OpGraph) -> dict[int, list[int]]:
    cons: dict[int, list[int]] = {t.id: [] for t in g.tensors}
    for o in g.ops:
        for e in o.inputs:
            cons[e.src].append(o.id)
    return cons


def _share_inclusive(g: OpGraph, tid: int, cons: list[int]) -> int:
    """Retired: the extractor now records half-open ``Edge.ranges`` so :meth:`OpGraph.share` is exact; kept as an
    alias for older callers."""
    return g.share(tid) if cons else 1


def _topological_tensors(g: OpGraph) -> list[int]:
    """Tensor ids ordered so that every input of a producer precedes its output (iterative DFS)."""
    order: list[int] = []
    seen: set[int] = set()
    for t in g.tensors:
        if t.id in seen:
            continue
        stack: list[tuple[int, bool]] = [(t.id, False)]
        while stack:
            tid, done = stack.pop()
            if done:
                order.append(tid)
                continue
            if tid in seen:
                continue
            seen.add(tid)
            stack.append((tid, True))
            p = g.tensors[tid].producer
            if p is not None:
                for e in g.ops[p].inputs:
                    if e.src not in seen:
                        stack.append((e.src, False))
    return order


def _is_free_param(t: Tensor) -> bool:
    return t.kind == "param" and (t.role or "fixed") in FREE_ROLES


def _producer(g: OpGraph, t: Tensor) -> Op:
    assert t.producer is not None, f"tensor {t.id} ({t.name}) has no producer"
    return g.ops[t.producer]


def _rowlen(o: Op) -> int | None:
    """Elements per row of ``o``'s output (None when unknown or when the layout does not divide)."""
    if o.kind not in _ROWLEN_KEY:
        return None
    key = _ROWLEN_KEY[o.kind]
    if key is None:
        return 1
    v = o.statics.get(key)
    return int(v) if v else None


def _is_tt(o: Op) -> bool:
    """``MatmulTT``: both operands are read along the contraction (their tensor rows are the *columns* of
    the abstract ``M x K`` / ``N x K`` operands)."""
    return o.fn_id.startswith("AccMatmulTT")


# ---------------------------------------------------------------------------------------------------------
# view certification (program reference descriptors)
# ---------------------------------------------------------------------------------------------------------

class _Views:
    """Decides whether an input edge of an op reads the *whole* source tensor *in leaf order* (so the op's
    rows are the tensor's rows).  With the program: resolved on the reference descriptors through plain
    ``call`` boundaries (mirrors ``bounds/upper.py``).  Without it (``assume_in_order=True``): the
    structural surrogate "exact read of every leaf exactly once" -- not certified, for hand-built graphs."""

    def __init__(self, g: OpGraph, program, assume_in_order: bool) -> None:
        self.g, self.program, self.assume = g, program, assume_in_order
        self._memo: dict[int, set[int]] = {}
        self._op_keys = {o.key: o.id for o in g.ops}

    def in_order(self, o: Op, tid: int) -> bool:
        """True iff some argument of ``o`` is a whole in-order view of op-output tensor ``tid``."""
        if o.id not in self._memo:
            self._memo[o.id] = self._compute(o)
        return tid in self._memo[o.id]

    def _compute(self, o: Op) -> set[int]:
        out: set[int] = set()
        if self.program is None:
            if self.assume:
                for e in o.inputs:
                    t = self.g.tensors[e.src]
                    if t.kind == "op" and e.exact and e.leaves_per_copy * o.copies == t.leaves:
                        out.add(e.src)
            return out
        try:
            node = self._node(o)
            for a in node.args:
                r = self._resolve(o.key[0], a.refs)
                if r is None:
                    continue
                key, base, count = r
                pid = self._op_keys.get(key)
                if pid is None or base != 0:
                    continue
                tid = self.g.ops[pid].out
                if count == self.g.tensors[tid].leaves:
                    out.add(tid)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):  # pragma: no cover
            return set()                         # unknown program layout -> nothing certified (sound)
        return out

    def _fn(self, path: tuple):
        fn = self.program.fn
        for p in path:
            fn = fn.body.nodes[p].fn
        return fn

    def _node(self, o: Op):
        return self._fn(o.key[0]).body.nodes[o.key[1]]

    def _resolve(self, path: tuple, refs):
        from verity_ir.refs import Affine
        for _ in range(64):
            if not isinstance(refs, Affine) or refs.count <= 0:
                return None
            if refs.space == "p":
                if not path:
                    return None
                call = self._fn(path[:-1]).body.nodes[path[-1]]
                if call.form != "call":
                    return None
                refs = call.args[refs.idx].refs.slice(refs.base, refs.base + refs.count)
                path = path[:-1]
                continue
            if refs.space == "n":
                key = (path, refs.idx)
                if key in self._op_keys:
                    return key, refs.base, refs.count
                node = self._fn(path).body.nodes[refs.idx]
                if node.form != "call":
                    return None
                path = path + (refs.idx,)
                refs = node.fn.body.ret.slice(refs.base, refs.base + refs.count)
                continue
            return None
        return None


# ---------------------------------------------------------------------------------------------------------
# closures (Wfree / Welt), lower-bound conventions
# ---------------------------------------------------------------------------------------------------------

def _merge(iv: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    if not iv:
        return ()
    iv = sorted(iv)
    out = [list(iv[0])]
    for lo, hi in iv[1:]:
        if lo <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return tuple((lo, hi) for lo, hi in out)


def _union(*cs: Closure) -> Closure:
    if len(cs) == 1:
        return cs[0]
    acc: dict[int, list[tuple[int, int]]] = {}
    for c in cs:
        for k, iv in c.items():
            acc.setdefault(k, []).extend(iv)
    return {k: _merge(v) for k, v in acc.items()}


def _closure_bytes(g: OpGraph, c: Closure) -> int:
    tot = 0
    for k, iv in c.items():
        t = g.tensors[k]
        n = sum(min(hi, t.leaves - 1) - lo + 1 for lo, hi in iv if lo < t.leaves)
        tot += n * t.width // 8
    return tot


def _edge_slice(e: Edge, t: Tensor, n: int | None = None) -> Closure:
    """Canonical closure item for ``n`` leaves of param ``t`` read through edge ``e`` (``None`` = the whole
    per-copy slice).  A lower bound: the item is the *first* ``n`` leaves of the recorded half-open ranges
    ``[lo, hi)`` (stored inclusively), and never more than ``leaves_per_copy`` -- ranges may over-approximate
    a copy's read."""
    if _is_free_param(t):
        return {}
    want = e.leaves_per_copy if n is None else min(n, e.leaves_per_copy)
    want = max(0, min(want, t.leaves))
    if want == 0:
        return {}
    ranges = e.ranges or ((0, t.leaves),)          # Edge.ranges are half-open [lo, hi)
    out: list[tuple[int, int]] = []
    left = want
    for lo, hi in sorted(ranges):
        hi = min(hi, t.leaves)
        if hi <= lo:
            continue
        take = min(left, hi - lo)
        out.append((lo, lo + take - 1))
        left -= take
        if left <= 0:
            break
    return {t.id: _merge(out)} if out else {}


# ---------------------------------------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------------------------------------

@dataclass
class _Ctx:
    g: OpGraph
    X: int
    G: int | None
    views: _Views
    cons: dict[int, list[int]]
    share: dict[int, int]
    rowlen: dict[int, int | None]          # tensor id -> row length (None unknown)
    matmul_reader: dict[int, bool]         # tensor id -> read by some matmul op
    notes: list[str]


def _aligned(ctx: _Ctx, o: Op, e: Edge, row: int | None) -> str:
    """Alignment class of input edge ``e`` of ``o`` whose rows have ``row`` elements: ``"row"`` (whole tensor
    in order, same row length), ``"scalar"`` (whole tensor in order, one element per row), ``"param"`` (a root
    parameter) or ``"none"``."""
    t = ctx.g.tensors[e.src]
    if t.kind == "param":
        return "param"
    if row is None or not ctx.views.in_order(o, e.src):
        return "none"
    rl = ctx.rowlen.get(e.src)
    if rl == row:
        return "row"
    if rl == 1 and row != 1:
        return "scalar"
    return "none"


def _matmul_operands(o: Op) -> tuple[Edge, Edge] | None:
    if len(o.inputs) == 1:
        return o.inputs[0], o.inputs[0]
    if len(o.inputs) == 2:
        return o.inputs[0], o.inputs[1]
    return None


def _operand_rows(ctx: _Ctx, o: Op, e: Edge, K: int) -> bool:
    """Operand read as full tensor rows in order with row length ``K`` (never for ``MatmulTT``)."""
    if _is_tt(o):
        return False
    return _aligned(ctx, o, e, K) == "row"


def _elementwise_param_inputs(ctx: _Ctx, p: Op, t: Tensor) -> list[tuple[Edge, Tensor]]:
    """Non-free root params read by element-wise ``p`` one leaf per output element (``W`` of ``perturb`` /
    ``sgdupdate``): each output element is backed by its *own* imported param element."""
    out = []
    for e in p.inputs:
        s = ctx.g.tensors[e.src]
        if s.kind == "param" and not _is_free_param(s) and e.exact and e.leaves_per_copy * p.copies == t.leaves:
            out.append((e, s))
    return out


def _closures(ctx: _Ctx, order: list[int]) -> tuple[dict[int, Closure], dict[int, Closure]]:
    g = ctx.g
    WF: dict[int, Closure] = {}
    WE: dict[int, Closure] = {}
    wall_memo: dict[tuple[int, int], Closure] = {}

    def wall(tid: int, n: int) -> Closure:
        """Closure of *any* ``n`` distinct elements of op tensor ``tid`` (lower bound).  Through element-wise
        producers ``n`` distinct outputs need ``n`` distinct elements of every per-element input (so ``n``
        leaves of a per-element root param); for every other producer fall back to one element."""
        t = g.tensors[tid]
        if n <= 1 or t.kind != "op":
            return WE[tid]
        key = (tid, n)
        if key in wall_memo:
            return wall_memo[key]
        p = _producer(g, t)
        res = WE[tid]
        if p.kind in ELEMENTWISE_KINDS:
            row = ctx.rowlen.get(tid)
            items: list[Closure] = []
            for e in p.inputs:
                s = g.tensors[e.src]
                cls = _aligned(ctx, p, e, row)
                if cls == "param":
                    per_elem = e.exact and e.leaves_per_copy * p.copies == t.leaves
                    items.append(_edge_slice(e, s, n if per_elem else 1))
                elif cls == "row":
                    items.append(wall(e.src, n))
                else:
                    items.append(WE[e.src])
            res = _union(*items) if items else {}
        wall_memo[key] = res
        return res

    for tid in order:
        t = g.tensors[tid]
        if t.kind == "param":
            if _is_free_param(t):
                WF[tid] = WE[tid] = {}
            else:                                # context-dependent; consumers use _edge_slice
                WF[tid] = WE[tid] = {tid: ((0, 0),)}
            continue
        p = _producer(g, t)
        row = ctx.rowlen.get(tid)

        def part(e: Edge, whole_row: bool, n_param: int | None) -> Closure:
            """Contribution of one input edge: row closure or element closure of an activation, or a
            canonical slice of ``n_param`` leaves (``None`` = slice read) of a param."""
            s = g.tensors[e.src]
            if s.kind == "param":
                return _edge_slice(e, s, n_param)
            return WF[e.src] if whole_row else WE[e.src]

        if p.kind == "matmul":
            ops = _matmul_operands(p)
            if ops is None:
                WF[tid] = WE[tid] = _union(*[part(e, False, 1) for e in p.inputs])
                continue
            eA, eB = ops
            K = int(p.statics.get("K", 0))
            A, B = g.tensors[eA.src], g.tensors[eB.src]
            a_rows = _operand_rows(ctx, p, eA, K)
            if A.kind == "param":
                Apart = _edge_slice(eA, A, K)
            elif a_rows:
                Apart = WF[eA.src]
            else:                                # K distinct A elements per output element
                Apart = wall(eA.src, K) if (eA.exact and eA.leaves_per_copy <= A.leaves) else WE[eA.src]
            if B.kind == "param":
                WF[tid] = _union(Apart, _edge_slice(eB, B, None))
                WE[tid] = _union(Apart, _edge_slice(eB, B, K))
            else:
                # one output row needs every element of the copy's B operand (N K distinct leaves when the
                # edge is exact), one output element needs one K-segment of it: closures of that many
                # distinct B elements (SPEC's Wfree(B) / one row is the n = rowlen(B) special case)
                if eB.exact and eB.leaves_per_copy <= B.leaves:
                    WF[tid] = _union(Apart, wall(eB.src, eB.leaves_per_copy))
                    WE[tid] = _union(Apart, wall(eB.src, K))
                else:
                    WF[tid] = WE[tid] = _union(Apart, WE[eB.src])
        elif p.kind in GATHER_KINDS:
            items = [part(e, False, row if row else 1) for e in p.inputs]      # one table row (D leaves)
            WF[tid] = WE[tid] = _union(*items) if items else {}
        elif p.kind in ELEMENTWISE_KINDS:
            wf: list[Closure] = []
            we: list[Closure] = []
            for e in p.inputs:
                cls = _aligned(ctx, p, e, row)
                s = g.tensors[e.src]
                if cls == "param":
                    # a param aligned with the rows (weights of perturb/sgd) contributes one row; a broadcast
                    # gain contributes the slice read -- we cannot tell them apart, so use the smaller
                    n_row = min(row, e.leaves_per_copy) if row else e.leaves_per_copy
                    wf.append(_edge_slice(e, s, n_row))
                    we.append(_edge_slice(e, s, 1))
                elif cls in ("row", "scalar"):
                    wf.append(WF[e.src])
                    we.append(WE[e.src])
                else:
                    wf.append(WE[e.src])
                    we.append(WE[e.src])
            WF[tid] = _union(*wf) if wf else {}
            WE[tid] = _union(*we) if we else {}
        elif p.kind in ROW_KINDS or p.kind in COLRED_KINDS:
            wf = []
            we = []
            for e in p.inputs:
                cls = _aligned(ctx, p, e, row)
                s = g.tensors[e.src]
                if cls == "param":
                    wf.append(_edge_slice(e, s, None))
                    we.append(_edge_slice(e, s, None) if p.kind in ROW_KINDS else _edge_slice(e, s, 1))
                elif cls in ("row", "scalar"):
                    wf.append(WF[e.src])
                    we.append(WF[e.src] if p.kind in ROW_KINDS else WE[e.src])
                else:
                    wf.append(WE[e.src])
                    we.append(WE[e.src])
            WF[tid] = _union(*wf) if wf else {}
            WE[tid] = _union(*we) if we else {}
        else:                                    # prim:*, scan:*, unknown: at least one element of each input
            items = [part(e, False, 1) for e in p.inputs]
            WF[tid] = WE[tid] = _union(*items) if items else {}
    return WF, WE


def _credits(ctx: _Ctx, order: list[int], theta: dict[int, float], gen: dict[int, bool]
             ) -> tuple[dict[int, float], dict[int, float]]:
    """Per-element credit ``kappa_e`` and per-row pool ``P`` for every tensor (see the module docstring)."""
    g, X = ctx.g, float(ctx.X)
    kap: dict[int, float] = {}
    pool: dict[int, float] = {}
    w_partial = (1.0 - THETA_GAMMA) * GAMMA_FULL

    def inh(tid: int) -> float:                  # per-element credit handed to one consumer
        return (1.0 - theta[tid]) * kap[tid] / ctx.share[tid]

    def inh_pool(tid: int) -> float:             # per-row credit handed to one consumer
        return (1.0 - theta[tid]) * pool[tid] / ctx.share[tid]

    def operand(p: Op, e: Edge, t_: Tensor, K: int) -> tuple[float, float]:
        """(bytes of in(R) backing one full K-row of the operand, per-row credit handed down)."""
        if t_.kind == "param":
            if _is_free_param(t_):
                return 0.0, 0.0
            w_ = t_.width / 8                    # every leaf is an import; theta = 1 for matmul-read params
            return K * w_, 0.0 if _is_tt(p) else (1.0 - theta[t_.id]) * w_ * K / ctx.share[t_.id]
        cert = _operand_rows(ctx, p, e, K)
        per = max(pool[t_.id] if cert else 0.0, K * kap[t_.id])
        if cert:
            return per, inh_pool(t_.id)
        # uncertified rows (e.g. per-head column slices in attention): one output element still contracts K
        # *distinct* elements of the operand when the edge is exact, each carrying its per-element credit
        return per, (K * inh(t_.id) if e.exact else 0.0)

    for tid in order:
        t = g.tensors[tid]
        w = t.width / 8
        if t.kind == "param":
            if _is_free_param(t):
                kap[tid] = pool[tid] = 0.0
            else:
                kap[tid] = w
                pool[tid] = w * (ctx.rowlen.get(tid) or 1)
            continue
        p = _producer(g, t)
        row = ctx.rowlen.get(tid)
        L = float(row) if row else 1.0
        ke = 0.0
        P = 0.0
        if p.kind == "matmul":
            wp = min(w, w_partial)
            ops = _matmul_operands(p)
            if ops is not None and "K" in p.statics:
                eA, eB = ops
                K = int(p.statics["K"])
                M = int(p.statics.get("M", 1))
                N = int(p.statics.get("N", 1))
                A, B = g.tensors[eA.src], g.tensors[eB.src]
                perA, poolA = operand(p, eA, A, K)
                perB, poolB = operand(p, eB, B, K)
                # an RU can hold at most floor(X / per) full operand rows (disjoint backing per row)
                nA = math.floor(X / perA) if perA > 0 else None
                nB = math.floor(X / perB) if perB > 0 else None
                if nA == 0 or nB == 0:               # nothing can be produced: every element is imported
                    ke, P = wp, L * wp
                else:
                    capA = N if nB is None else min(N, nB)      # produced elements one A row can serve
                    capB = M if nA is None else min(M, nA)      # produced elements one B row can serve
                    ke = min(wp, poolA / capA + poolB / capB)
                    forced = 0.0 if nB is None else max(0.0, L - nB)
                    P = min(L * wp, forced * wp + (L - forced) * ke)
        elif p.kind in ELEMENTWISE_KINDS:
            for e in p.inputs:
                cls = _aligned(ctx, p, e, row)
                if cls == "param":
                    s = g.tensors[e.src]
                    if _is_free_param(s) or not row:
                        continue
                    # aligned only if the param is read row by row (one leaf per output element)
                    if e.leaves_per_copy * p.copies == t.leaves:
                        ke += inh(e.src)
                        P += (1.0 - theta[e.src]) * (s.width / 8) * L / ctx.share[e.src]
                elif cls == "row":
                    ke += inh(e.src)
                    P += inh_pool(e.src)
                elif cls == "scalar":
                    ke += inh_pool(e.src) / L
                    P += inh_pool(e.src)
            ke, P = min(w, ke), min(L * w, P)
        elif p.kind in ROW_KINDS:
            for e in p.inputs:
                if _aligned(ctx, p, e, row) in ("row", "scalar"):
                    P += inh_pool(e.src)
            P = min(L * w, P)
            ke = min(w, P / L)
        elif p.kind in COLRED_KINDS:
            for e in p.inputs:
                if _aligned(ctx, p, e, row) == "row":
                    ke += inh(e.src)
                    P += inh_pool(e.src)
            ke, P = min(w, ke), min(L * w, P)
        # gathers, prim:*, scan:*, unknown: 0
        if gen[tid]:
            ke = 0.0
        kap[tid] = ke
        pool[tid] = P
    return kap, pool


def _op_charges(ctx: _Ctx, o: Op, kap: dict[int, float], gen: dict[int, bool], theta: dict[int, float],
                notes: list[str] | None) -> dict[str, Any] | None:
    """``alpha, beta, gamma`` and the merged ``Q, N, K`` of matmul ``o`` (None when it cannot be charged)."""
    g = ctx.g
    s = o.statics
    try:
        M, N, K = int(s["M"]), int(s["N"]), int(s["K"])
    except KeyError:
        if notes is not None:
            notes.append(f"op {o.id} ({o.fn_id}): matmul without M/N/K statics; charged 0")
        return None
    ops = _matmul_operands(o)
    if ops is None:
        if notes is not None:
            notes.append(f"op {o.id}: matmul with {len(o.inputs)} input edges; charged 0")
        return None
    eA, eB = ops
    A, B = g.tensors[eA.src], g.tensors[eB.src]

    def direct(t: Tensor) -> float:
        if t.kind == "param":
            return 0.0 if _is_free_param(t) else (t.width / 8) / ctx.share[t.id]
        if gen[t.id]:
            return 0.0
        return theta[t.id] * kap[t.id] / ctx.share[t.id]

    alpha, beta = direct(A), direct(B)
    if eA is eB:                                 # one tensor used as both operands: split its slot
        alpha = beta = alpha / 2.0
        if alpha > 0 and notes is not None:
            notes.append(f"op {o.id}: A and B are the same tensor {A.name}; slot split alpha = beta = charge/2")
    if alpha > 0 and ((not eA.exact) or eA.leaves_per_copy != M * K or eA.leaves_per_copy * o.copies > A.leaves):
        if notes is not None:
            notes.append(f"op {o.id}: A operand {A.name} is shared between copies or its read count is inexact "
                         f"({eA.leaves_per_copy} x {o.copies} of {A.leaves} leaves); alpha set to 0")
        alpha = 0.0
    if beta > 0 and ((not eB.exact) or eB.leaves_per_copy != N * K):
        if notes is not None:
            notes.append(f"op {o.id}: B operand {B.name} read count {eB.leaves_per_copy} != N*K={N * K} or "
                         f"inexact; beta set to 0")
        beta = 0.0
    return {"alpha": alpha, "beta": beta, "gamma": THETA_GAMMA * GAMMA_FULL, "Q": M * o.copies, "N": N, "K": K,
            "A": A.id, "B": B.id, "theta_A": theta[A.id], "theta_B": theta[B.id]}


def _evaluate(ctx: _Ctx, order: list[int], theta: dict[int, float], gen: dict[int, bool], notes: list[str] | None
              ) -> tuple[int, bool, dict[int, int], dict[int, dict], dict[int, dict], dict[int, float], dict[int, float]]:
    kap, pool = _credits(ctx, order, theta, gen)
    per_op: dict[int, int] = {}
    op_params: dict[int, dict] = {}
    tiles: dict[int, dict] = {}
    cap = 0
    infeasible = False
    for o in ctx.g.ops:
        if o.kind != "matmul":
            per_op[o.id] = 0
            continue
        prm = _op_charges(ctx, o, kap, gen, theta, notes)
        if prm is None:
            per_op[o.id] = 0
            continue
        L_o, detail = matmul_charge(prm["alpha"], prm["beta"], prm["Q"], prm["N"], prm["K"], float(ctx.X),
                                    gamma=prm["gamma"], G=None if ctx.G is None else float(ctx.G))
        if L_o == INFEASIBLE:
            infeasible = True
            if notes is not None:
                notes.append(f"op {o.id} ({o.fn_id}): alpha + beta = {prm['alpha'] + prm['beta']:.4g} > X = {ctx.X}; "
                             f"no RU can execute a MAC of this op -- program infeasible at this X")
        per_op[o.id] = L_o
        op_params[o.id] = prm
        tiles[o.id] = detail
        cap = INFEASIBLE if (infeasible or cap >= INFEASIBLE) else cap + L_o
    return (INFEASIBLE if infeasible else cap), infeasible, per_op, op_params, tiles, kap, pool


# ---------------------------------------------------------------------------------------------------------
# worst-RU diagnostic (THEORY §0.1)
# ---------------------------------------------------------------------------------------------------------

def _op_class(g: OpGraph, o: Op, grad_dep: dict[int, bool] | None) -> str:
    try:
        from accumulation.bounds.upper import classify_op
        return classify_op(g, o, None, grad_dep)
    except (ImportError, ValueError, KeyError, IndexError):   # pragma: no cover - reporting only
        return "matmul"


def _worst_ru(ctx: _Ctx, adw: ADW, per_op: dict[int, int], op_params: dict[int, dict], tiles: dict[int, dict],
              kap: dict[int, float], gen: dict[int, bool], theta: dict[int, float]) -> dict[str, Any]:
    """The most constraining legal RU the certificate found (THEORY §0.1 "worst-RU diagnostic").

    For every charged matmul the optimiser's real tile ``(a, b, k)`` is a legal RU shape whose price per MAC
    (``alpha/b + beta/a + gamma/k``, i.e. the certificate's claim on the RU divided by its MACs) is the
    smallest the op admits; the headline ``L`` is the sum of these minima times the ops' MACs.  ``worst`` is
    the target (accumulation-dependent, non-recompute) op with the lowest realised price ``L_o / MACs`` among
    ops with a positive charge -- *the attack that prevents a stronger bound*.  ``uncharged`` lists target ops
    priced 0 (``alpha = beta = 0``: both operands free or gen).  ``deficit_top`` ranks op groups (same class
    and shape) by ``MACs * (best price - price)``, the bytes the certificate would gain if the group were
    priced like the best-priced op.  ``input_bytes`` is what a literal RU of that tile imports if its operands
    enter at full width (``k (a w_A + b w_B)``); ``claimed_bytes`` is the certificate's claim
    ``k (alpha a + beta b)``; ``up_work`` is the serial chain per output element (``k`` MACs)."""
    g = ctx.g
    try:
        from accumulation.bounds.upper import _grad_dependent
        grad_dep: dict[int, bool] | None = _grad_dependent(g)
    except ImportError:  # pragma: no cover
        grad_dep = None
    rows: list[dict[str, Any]] = []
    for o in g.ops:
        if o.kind != "matmul" or o.id not in op_params:
            continue
        macs = o.macs()
        if macs <= 0:
            continue
        prm, d = op_params[o.id], tiles[o.id]
        target = adw.per_op.get(o.id, False) and o.name != "recompute"
        if adw.credited_macs == 0:               # inference circuit: every matmul is target work
            target = True
        A, B = g.tensors[prm["A"]], g.tensors[prm["B"]]
        a, b, k = float(d.get("a", 0.0)), float(d.get("b", 0.0)), float(d.get("k", 0.0))
        rows.append({
            "op_id": o.id, "fn_id": o.fn_id, "class": _op_class(g, o, grad_dep), "target": bool(target),
            "shape": (a, b, k), "work": a * b * k, "up_work": k, "target_macs": a * b * k if target else 0.0,
            "op_macs": macs, "price": per_op[o.id] / macs, "charge": per_op[o.id],
            "bytes_per_mac": float(d.get("tile_cost", d.get("cost", 0.0))),
            "claimed_bytes": k * (prm["alpha"] * a + prm["beta"] * b),
            "input_bytes": k * (a * A.width / 8 + b * B.width / 8),
            "binding": d.get("binding", "none"),
            "operands": [(A.id, A.name, A.role if A.kind == "param" else "op", k * a * A.width / 8, "A"),
                         (B.id, B.name, B.role if B.kind == "param" else "op", k * b * B.width / 8, "B")],
            "alpha": prm["alpha"], "beta": prm["beta"], "gamma": prm["gamma"],
            "theta": {"A": theta[A.id], "B": theta[B.id]}, "gen": {"A": gen[A.id], "B": gen[B.id]},
            "kappa": {"A": kap[A.id], "B": kap[B.id]}, "share": {"A": ctx.share[A.id], "B": ctx.share[B.id]},
        })
    targets = [r for r in rows if r["target"]]
    charged = [r for r in targets if r["charge"] > 0]
    worst = min(charged, key=lambda r: r["price"]) if charged else (min(targets, key=lambda r: r["price"]) if targets else {})
    best_price = max((r["price"] for r in targets), default=0.0)
    groups: dict[tuple, dict[str, Any]] = {}
    for r in targets:
        key = (r["class"], r["fn_id"], r["binding"])
        gr = groups.setdefault(key, {"class": r["class"], "fn_id": r["fn_id"], "binding": r["binding"], "n_ops": 0,
                                     "macs": 0, "charge": 0, "price": r["price"], "deficit": 0.0,
                                     "example_op": r["op_id"]})
        gr["n_ops"] += 1
        gr["macs"] += r["op_macs"]
        gr["charge"] += r["charge"]
        gr["deficit"] += r["op_macs"] * (best_price - r["price"])
    for gr in groups.values():
        gr["price"] = gr["charge"] / gr["macs"] if gr["macs"] else 0.0
    deficit_top = sorted(groups.values(), key=lambda gr: -gr["deficit"])[:5]
    uncharged = [r for r in targets if r["charge"] == 0]
    return {
        "worst": worst,
        "best_price": best_price,
        "deficit_top": deficit_top,
        "uncharged": {"n_ops": len(uncharged), "macs": sum(r["op_macs"] for r in uncharged),
                      "examples": [(r["op_id"], r["fn_id"], r["class"]) for r in uncharged[:8]]},
        "n_target_ops": len(targets),
        "binding_counts": {b: sum(1 for r in targets if r["binding"] == b) for b in sorted({r["binding"] for r in targets})},
    }


# ---------------------------------------------------------------------------------------------------------
# the bound
# ---------------------------------------------------------------------------------------------------------

def lower_bound(g: OpGraph, F: int, X: int, *, G: int | None = None, adw: ADW | None = None, program=None,
                theta_grid=None, theta_by_kind: bool = True, assume_in_order: bool = False) -> LowerBound:
    """Certified lower bound ``L(P; F, G, X) <= I*(P; F, G, X)`` for the operator graph ``g`` (SPEC §2, §5).

    ``G``: total-work cap per RU (``Work(R) <= G``; ``None`` = unbounded).  It enters only the per-op tile
    problem: the MACs of op ``o`` inside an RU are at most ``Work(R) <= G``, so the real tile of §2.1 also
    satisfies ``a b k <= G`` (``a b k = w_R^3 / (a_R b_R c_R) <= w_R`` by Loomis-Whitney).  Regeneration work
    inside the RU is *not* exploited (it only makes ``Work(R)`` larger, so ``w_R <= G`` stays valid); the
    closure-budget credits (``gen``, ``kappa``, ``theta``) are byte counts against ``X`` and are unchanged.
    ``program``: the Verity ``Program`` the graph was extracted from (or set ``g.program``); it certifies
    which operands are read as whole in-order rows, which is what lets row credits flow.  Without it the
    bound is sound but weak (``assume_in_order=True`` enables the uncertified structural surrogate for
    hand-built graphs).  ``theta_grid``: candidate split factors for activations (default ``THETA_GRID``; the
    best resulting ``L`` is returned); ``theta_by_kind=True`` additionally runs a coordinate ascent choosing one
    grid value per producer kind (every choice is sound; this only tightens).  ``F`` is accepted for the
    contract but unused (§2.3 not implemented).
    ``adw`` may be supplied to avoid recomputing it (used for ``kappa_L`` and ``worst_ru``)."""
    notes: list[str] = []
    X = int(X)
    if G is not None:
        G = int(G)
        if G < 1:
            raise ValueError("G must be a positive work cap or None")
    if adw is None:
        adw = compute_adw(g)
    cons = _consumers(g)
    program = program if program is not None else getattr(g, "program", None)
    views = _Views(g, program, assume_in_order)
    if program is None:
        notes.append("no program given: operand row views are " +
                     ("assumed from leaf counts (uncertified)" if assume_in_order else
                      "not certified; row credits do not flow (sound, weak) -- pass program="))

    # -- L_source ------------------------------------------------------------------------------------------
    source = state_floor = token_seed = 0
    for t in g.tensors:
        if t.kind != "param" or (t.role or "fixed") == "fixed" or not cons[t.id]:
            continue
        reads = 0
        biggest = 0
        for oid in cons[t.id]:
            o = g.ops[oid]
            for e in o.inputs:
                if e.src == t.id:
                    reads += e.leaves_per_copy * o.copies
                    biggest = max(biggest, e.leaves_per_copy)
        leaves = t.leaves
        if reads < t.leaves:
            leaves = min(t.leaves, biggest)
            notes.append(f"param {t.name}: total reads {reads} < leaves {t.leaves}; L_source counts only "
                         f"{leaves} leaves (largest single read)")
        b = leaves * t.width // 8
        source += b
        if t.role in STATE_ROLES:
            state_floor += b
        else:
            token_seed += b

    # -- static per-tensor data ---------------------------------------------------------------------------
    share: dict[int, int] = {}
    rowlen: dict[int, int | None] = {}
    matmul_reader: dict[int, bool] = {}
    for t in g.tensors:
        share[t.id] = max(1, g.share(t.id)) if cons[t.id] else 1      # Edge.ranges are half-open (fixed in extractor)
        matmul_reader[t.id] = any(g.ops[c].kind == "matmul" for c in cons[t.id])
        if t.kind == "op":
            p = _producer(g, t)
            rl = _rowlen(p)
            rowlen[t.id] = rl if (rl and t.leaves % rl == 0) else None
        else:
            # a non-free root param: its row is what its matmul readers contract over (K), else unknown
            ks = {int(g.ops[c].statics["K"]) for c in cons[t.id]
                  if g.ops[c].kind == "matmul" and "K" in g.ops[c].statics}
            rowlen[t.id] = ks.pop() if len(ks) == 1 else None
    ctx = _Ctx(g=g, X=X, G=G, views=views, cons=cons, share=share, rowlen=rowlen, matmul_reader=matmul_reader,
               notes=notes)
    order = _topological_tensors(g)

    # -- closures / gen -----------------------------------------------------------------------------------
    WF, WE = _closures(ctx, order)
    welt_bytes = {tid: _closure_bytes(g, WE[tid]) for tid in order}
    wfree_bytes = {tid: _closure_bytes(g, WF[tid]) for tid in order}
    gen = {tid: welt_bytes[tid] <= X for tid in order}
    rootlike: dict[int, bool] = {}
    n_rootlike = 0
    for tid in order:
        t = g.tensors[tid]
        if t.kind == "param":
            gen[tid] = _is_free_param(t)         # a non-free root param is never "generated"
            rootlike[tid] = not _is_free_param(t)
            continue
        p = _producer(g, t)
        rl = False
        if p.kind in ELEMENTWISE_KINDS:
            # produced weights (perturb / sgdupdate / adapter merges): every element is backed by its own
            # imported root-param element (or a root-like one), so the per-element credit is sound even when
            # the (tiny, per-element) closure fits X -- the SPEC's "inheritance from root-param weights"
            rl = bool(_elementwise_param_inputs(ctx, p, t)) or any(
                rootlike.get(e.src, False) and g.tensors[e.src].kind == "op"
                and _aligned(ctx, p, e, ctx.rowlen.get(tid)) == "row" for e in p.inputs)
        rootlike[tid] = rl
        if rl and gen[tid]:
            gen[tid] = False
            n_rootlike += 1
    if n_rootlike:
        notes.append(f"{n_rootlike} root-like produced-weight tensors with |Welt| <= X keep their per-element "
                     f"credit (gen forced False; SPEC 'inheritance from root-param weights')")

    # -- credits and charges over the theta grid ----------------------------------------------------------
    grid = tuple(theta_grid) if theta_grid is not None else THETA_GRID

    def kind_of(t: Tensor) -> str:
        return _producer(g, t).kind if t.kind == "op" else "param"

    def make_theta(by_kind: dict[str, float]) -> dict[int, float]:
        theta: dict[int, float] = {}
        for t in g.tensors:
            if t.kind == "param":
                theta[t.id] = 1.0 if (matmul_reader[t.id] and not _is_free_param(t)) else 0.0
            else:
                theta[t.id] = by_kind[kind_of(t)] if matmul_reader[t.id] else 0.0
        return theta

    def better(res, best) -> bool:
        return best is None or (res[0] > best[0] and not res[1]) or (best[1] and not res[1])

    kinds = sorted({kind_of(t) for t in g.tensors if t.kind == "op" and matmul_reader[t.id]})
    best = None
    best_kind: dict[str, float] = {}
    for th in grid:                                            # one global value first
        by_kind = dict.fromkeys(kinds, th)
        res = _evaluate(ctx, order, make_theta(by_kind), gen, None)
        if better(res, best):
            best, best_kind, th_global = res, by_kind, th
    if theta_by_kind and len(grid) > 1:                        # coordinate ascent per producer kind
        for _sweep in range(2):
            changed = False
            for k in kinds:
                for th in grid:
                    if th == best_kind[k]:
                        continue
                    trial = dict(best_kind, **{k: th})
                    res = _evaluate(ctx, order, make_theta(trial), gen, None)
                    if better(res, best):
                        best, best_kind, changed = res, trial, True
            if not changed:
                break
    assert best is not None
    theta = make_theta(best_kind)
    th = th_global
    # re-run once with notes for the chosen theta
    cap, infeasible, per_op, op_params, tiles, kap, pool = _evaluate(ctx, order, theta, gen, notes)

    alpha_eff: dict[int, float] = {}
    for t in g.tensors:
        if t.kind == "param":
            alpha_eff[t.id] = 0.0 if _is_free_param(t) else (t.width / 8) / share[t.id]
        else:
            alpha_eff[t.id] = 0.0 if gen[t.id] else theta[t.id] * kap[t.id] / share[t.id]

    kappa_op: dict[int, float] = {}
    for o in g.ops:
        if o.kind != "matmul":
            continue
        L_o = per_op[o.id]
        kappa_op[o.id] = (o.macs() / L_o) if 0 < L_o < INFEASIBLE else (math.inf if L_o == 0 else 0.0)

    total = INFEASIBLE if infeasible else max(source, cap + token_seed)
    # |M|: credited (accumulation-dependent, recompute excluded) MACs for training circuits, all MACs for
    # inference circuits (nothing accumulation-dependent there) -- SPEC §6
    target_macs = adw.credited_macs if adw.credited_macs > 0 else adw.all_macs
    kappa_L = (target_macs / total) if 0 < total < INFEASIBLE else 0.0
    notes.append(f"theta grid {grid}: best global theta_act = {th}; theta_gamma = {THETA_GAMMA}"
                 + (f"; per-kind {best_kind}" if theta_by_kind else ""))
    notes.append("kappa_L uses |M| = " + ("credited_macs (training)" if adw.credited_macs > 0 else
                                          "all_macs (inference: no accumulation-dependent work)"))
    notes.append("F is not used (SPEC §2.3 not implemented); the bound holds for every F")
    if G is not None:
        notes.append(f"G = {G}: tile work a*b*k <= G per op (regeneration work inside the RU not exploited)")
    worst = _worst_ru(ctx, adw, per_op, op_params, tiles, kap, gen, theta) if not infeasible else {}
    return LowerBound(total=int(total), source=int(source), cap=int(cap), per_op=per_op, alpha_eff=alpha_eff,
                      kappa=kap, gen=gen, welt_bytes=welt_bytes, wfree_bytes=wfree_bytes, share=share, theta=theta,
                      pool=pool, op_params=op_params, notes=notes, worst_ru=worst, state_floor=int(state_floor),
                      token_seed=int(token_seed), kappa_op=kappa_op, kappa_L=kappa_L, tiles=tiles, theta_act=th,
                      theta_kind=best_kind, target_macs=int(target_macs), F=int(F), X=X, G=G, infeasible=infeasible)


def lower_coarse(g: OpGraph, F: int | None, G: int | None, *, program: Any = None, **kw) -> LowerBound:
    """Coarse ``(F, G)`` certificate for the corrected policy model (no ``X``); see
    :mod:`accumulation.bounds.lower_coarse` for the theorem, proof and LP.  Thin re-export (the module imports
    :class:`LowerBound` from here, hence the late import)."""
    from accumulation.bounds.lower_coarse import lower_coarse as _lc
    return _lc(g, F, G, program=program, **kw)
