"""Coarse ``(F, G)`` lower bound for chained-transformer training circuits (SPEC §2.3 "coarse certificate").

Policy model
------------
An RU ``R`` is legal iff ``Work(R) <= G`` and ``Work(Up_R(x)) <= F`` for every value ``x`` produced in ``R``
(``Up_R(x)`` = the ops of ``R`` that ``x`` depends on).  There is no input cap.  ``I(R)`` is the width of every
value that is consumed in ``R`` but produced outside it plus exogenous ingress: fixed-role leaves are free;
non-fixed roots (tokens, seeds, the accumulated / carried step-0 weights) and produced weights / gradients /
activations of other RUs count.  The primary object is ``I* = min over legal partitions of sum_R I(R)``.

Root floor.  A non-fixed root element read by some op is produced outside every RU, so it is imported by at
least one RU: ``I* >= token bytes + root bytes`` where both count the *union of the leaf ranges actually
read* (a row / slice view of a root costs only that slice; ``Edge.ranges``).  This is a charge class
disjoint from the produced values priced below, so it adds to the LP certificate; when the step-0 weights
are dynamic roots and there is no later version (``forward-nonfixed``) they are priced inside the LP
instead (``charge_roots``: every weight element present in an RU is imported at 2 B and the step-0 products
are credited) and ``L = token bytes + max(root bytes, LP)``.

A certificate is a price ``p_m`` on every MAC ``m`` (signed; positive on the *credited* MACs -- matmul MACs
of steps ``k >= 1`` at blocks ``l >= 1``, or of step 0 when its weights are dynamic roots, recompute
excluded) such that ``sum_{m in R} p_m <= I(R)`` for every legal ``R``; then ``I* >= floor + sum_m p_m``.

Theorem (coarse certificate)
----------------------------
Let the circuit be a chained local-SGD program on a pre-norm transformer: weight versions ``W_{k,l}`` for
steps ``k = 0..K-1`` and blocks ``l = 0..L`` (``L`` = LM head), ``W_{k,l} = W_{k-1,l} - lr dW_{k-1,l}`` with
``dW_{k-1,l}`` the full-batch (``Q = Q_step`` tokens) weight gradient.  Block-0 input rows ``h_0`` are free
(exogenous tokens or a gather from a frozen root table).  For a legal RU ``R`` and a cell ``(k, l)`` call a
token *fwd-working* (``n^W``) if some fwd activation element of block ``l`` for that token is produced in
``R``, *bwd-working* (``m^W``) likewise for bwd activations; split the imported bytes of block-``l`` values
into four classes -- fwd internals (``x_l .. s``), the fwd output row ``h_{l+1}``, bwd internals, the bwd
output row ``dh_l`` -- and per class call a token ``I`` if ``>= 2d`` bytes of its own row of that class are
imported (``n^{Ii}, n^{Io}, m^{Ii}, m^{Io}``), every other imported byte of the class going to the cheap pool
``b^{fi}, b^{fo}, b^{bi}, b^{bo}``.  ``n^P`` (``m^P``) are the working tokens that hop: they are neither ``I``
in the internals nor in the row entering the block.  Further: ``w^{imp} / w^{prod}`` weight elements of
``W_{k,l}`` imported / produced in ``R`` (``k >= 1``), ``mf, md, mw`` fwd / dgrad / wgrad MACs performed,
``pc`` elements of ``dW_{k,l}`` completed (all ``Q`` MACs), ``pi`` partial sums of ``dW`` imported, ``fb``
tokens with both wgrad operand rows present, and at the head ``m^T`` produced logit rows.

Then ``I(R) >= 2 sum_{k>=1} w^{imp} + 2 sum pi + 2d sum (n^{Ii} + n^{Io} + m^{Ii} + m^{Io}) + sum (b^{fi} +
b^{fo} + b^{bi} + b^{bo})`` (disjoint leaf sets) and, writing ``a_l = 1/(2d)`` and ``[.]_+ = max(0, .)``,
the shape satisfies (per cell; ``P_l`` weight elements, ``c^f_l, c^b_l`` the forced hop work below):

  (T)  all token counts ``<= Q``; ``w^{imp} + w^{prod} <= P_l``;
  (C)  fwd chain (verified block, ``l >= 1``): the working set is partitioned ``W_l = A_l | B_l | P_l`` with
       ``A_l = W_l & I_l`` (``n^A <= n^I``), ``B_l = (W_l & I_{l-1}) minus I_l`` (``n^B <= n^I_{l-1}``) and the
       hopping tokens ``P_l = W_l minus (I_l | I_{l-1})``; a hopping token produced an element of ``h_l`` (a
       block-``(l-1)`` value) without being ``I`` there, so ``P_l`` is a subset of ``W_{l-1} minus I_{l-1} = B_{l-1} |
       P_{l-1}``: ``n^P_l <= n^B_{l-1} + n^P_{l-1}`` and ``n^B + n^P <= n^W`` (one imported row, or one free
       block-0 row, feeds one chain of working tokens -- a token cannot be counted both as ``I_{l-1}`` and as a
       hopper); bwd chain (``l < L``) likewise downwards with ``m^A, m^B, m^P`` and ``m^P_l <= m^B_{l+1} +
       m^P_{l+1}`` (at the head: ``<= m^T``); ``m^W_L <= m^{Ii}_L + m^T`` and ``m^T <= n^W_L + n^{Ii}_L``;
  (H)  hop work: ``mf_{l-1} >= c^f_{l-1} n^P_l``, ``md_{l+1} >= c^b_{l+1} m^P_l`` (``md_L >= c^b_L
       (m^P_{L-1} - a b^{bo}_L)``), head: ``mf_L >= P_L (m^T - n^{Ii}_L - b^{fi}_L / (4d))`` and
       ``w_L >= P_L (m^T - n^{Ii}_L) / Q``;
  (U)  hop weights: ``n^P_l > 0  =>  w_{l-1} >= c^f_{l-1} - (d-1) s^f_{l-1}`` and ``m^P_l > 0  =>  w_{l+1} >=
       c^b_{l+1} - (d-1) s^b_{l+1}`` (binaries ``u``): a hopping token imported fewer than ``2d`` bytes, i.e.
       at most ``d-1`` elements of the block, each of which spares at most ``s`` weights (the weights of the
       MACs it spares); every other weight of the forced hop work must be present.  Head: a produced logit
       row of a non-``I`` token needs ``P_L - (d-1) d`` head elements present;
  (X)  partial outputs: ``xf >= mf - P_l n^W``, ``xb >= md - P_l m^W`` (MACs of tokens without a complete
       output element) are charged ``(ACC_BYTES - 2) / (2(d-1))`` bytes each: every such MAC ends in a partial
       sum that leaves ``R`` (``ACC_BYTES`` at its consumer, which counts it as one 2-byte item), and one
       partial aggregates at most one MAC per imported item of the token (``<= 2(d-1)`` items);
  (W)  bilinear work: ``mf <= P_l n^W + c^C_l (b^{fi} + b^{fo}_{l-1})``, ``md <= P_l m^W + c^C_l (b^{bi} +
       b^{bo}_{l+1})``, ``mw <= P_l fb + c^C_l (all four cheap pools)``, ``fb <= min(n^W, m^W)``,
       ``mf, md <= Q w`` (tightened by *token slabs*: the shape space is covered by the slabs ``max
       credited-cell token count in [lo_j, hi_j]`` (ratio ``_MC_RATIO``, ``_MC_ENUM`` of them, single-step
       circuits by default), each adding ``n <= hi_j`` and ``m <= hi_j w`` -- a weight element present serves
       at most ``hi_j`` tokens -- with anchor binaries ``sum_l s_l >= 1, n_l >= lo_j s_l`` excluding the smaller
       shapes; every minimisation over the polytope is the minimum over the slabs), ``mw >= Q pc``,
       ``pc + pi <= P_l``, ``pc <= P_l z``, ``z Q <= fb + (cheap bytes)/2``
       with ``z in {0, 1}`` (a completed gradient element needs all ``Q`` token pairs), where ``c^C_l`` = MACs
       one imported byte can feed (the block's widest weight, per element) -- cheap pools may only buy work;
  (P)  produced weights: ``w^{prod}_{k,l} <= pc_{k-1,l} + pi_{k-1,l}`` and ``w^{prod}_{k,l} <= w_{k-1,l}``;
  (F)  if ``z_{k-1,l} = 1``: the forced hop work of the non-exempt tokens of step ``k-1`` on the fwd chain
       below ``l``, the bwd chain above ``l``, (tokens reaching the head without importing its bwd rows) the
       head fwd and dgrad plus the fwd chain from ``l`` to the head, and the ``Q pc`` completing wgrad MACs,
       is ``<= F``; a token is exempt at a hop when it is ``I`` (or cheap-equivalent) in any class between the
       hop and ``l`` or is a cheap wgrad token;
  (G)  ``sum_{cells} (work per MAC) (mf + md + mw) <= G``.

Consequently, for any signed ``lambda`` indexed by price group ``c`` (default: (step, class), with the
uncredited step-0 / layer-0 / head work in groups of its own; the certified vector is then refined to
(step, class, dyadic depth band) groups by warm-started cutting planes -- a deep layer cannot be reached by a
cheap restart from the free block-0 rows, so it may carry a higher price) and ``mu >= 0`` with
``sum_c lambda_c M_c(x) + mu W(x) <= I(x)`` for every ``x`` in the polytope above (verified by MILP), the
circuit's total input satisfies ``I* >= token bytes + root bytes + sum_c lambda_c |M_c| + mu sum P``
(every MAC is performed in exactly one RU, so signed prices telescope; every priced weight element is
present in at least one RU).  ``lower_coarse`` returns this with the cutting-plane optimum of the prices.

Proof sketch
------------
*Charges are disjoint.*  Imported weight elements, imported partial sums of ``dW`` (produced values of other
RUs, 2 bytes each) and imported values of the four per-block classes are pairwise disjoint sets of leaves,
so ``I(R)`` dominates their sum.  An ``I`` token imports ``>= 2d`` bytes of its own row of the class and
distinct tokens own distinct rows; the remaining bytes of the class are counted once in the cheap pool.
Every imported value is counted as a 2-byte item (elements are 2 bytes; a partial sum is ``ACC_BYTES``), so
the ``ACC_BYTES - 2`` bytes of every partial sum that are not counted at its consumer may be charged at its
producer (``(X)``): summed over the partition, ``sum_R (items + exports) <= sum_R I(R)`` because each exported
partial is imported at least once.  *(X)* a token without a complete output element of the block cannot
have absorbed its partial sums (only the accumulation chain consumes them, and the chain's completing MAC is
elsewhere), so each of its MACs lies on a partial that crosses out of ``R``; one partial aggregates at most
one MAC per distinct imported operand item of the token, and a non-``I`` token has ``<= d-1`` items in each
of the two pools it may draw from.

*(C) chain -- token-row lemma.*  Every fwd activation element of block ``l >= 1`` for token ``q`` depends on
the whole input row ``h_l[q,.]`` (rmsnorm normalises the full row; the first projections contract over it),
so a working token that is not ``I`` in the block's internals, has not imported the row entering the block
(``n^{Io}_{l-1}`` or cheap-equivalent) must have a produced element of ``h_l[q,.] = h_{l-1}[q,.] + o + down``:
a produced element at block ``l-1`` (``n^W_{l-1}``).  Backward: every bwd element of block ``l`` for ``q``
depends on the whole row ``dh_{l+1}[q,.]`` (the down-projection dgrad contracts over it, the norm backward
over the row), produced at block ``l+1`` if not imported.  A produced logit row element depends on the full
head input row ``xn[q,.]`` (full contraction), hence on the working/imported block-``L`` fwd row.
Cheap-pool bytes are credited at ``1/(2d)`` token per byte -- an over-count (relaxation).

*(H) hop work -- item budget.*  A hopping token at ``l`` needs the whole row ``h_l[q,.]`` (``d`` elements)
and imported fewer than ``2d`` bytes of block-``(l-1)`` values: at most ``d-1`` *items* (elements or partial
sums).  Each ``h_l`` element is imported (1 item) or produced by the residual add from ``h'[q,n]`` and
``down[q,n]``, each again imported (1 item) or produced.  With ``x`` imported and ``y = d - x`` produced
elements, ``x + (items spent inside produced elements) <= d - 1`` forces at least one produced element whose
``down`` *and* ``h'`` are produced without imports: ``down[q,n]`` needs the full ``s[q,.]`` row (every
non-imported ``s`` element costs its ``g`` and ``u``, ``K_g + K_u`` MACs) and ``h'[q,n]`` needs ``o[q,n]``,
a contraction over the whole attention row, i.e. the full ``q`` row (``|W_q|`` MACs).  Gross forced work
``c^f = ffn (K_g+K_u) + d ffn + |W_q| + |W_o|`` (the whole token MLP, its ``o`` row and ``q`` row), each
imported item sparing at most ``s^f = max(ffn + K_o, K_g + K_u)`` MACs (an ``h_l`` item spares its ``down``
and ``o`` elements; an ``s`` item its ``g`` and ``u``).  Backward symmetric on ``dh_l = dh' + dxa``: the
zero-import element needs its ``dx'`` element (``2 ffn``), the full ``dS`` row (``d ffn``), its ``dxa``
element (``N_q + N_k + N_v``) whose ``dq`` needs the scores' gradient and hence the full ``do = dh' W_o^T``
row (``|W_o|``, which needs every ``dh'`` element: ``d 2 ffn``): ``c^b = 3 d ffn + |W_q|+|W_k|+|W_v|+|W_o|``,
``s^b = max(2 ffn, N_q+N_k+N_v, d)``.  At the head ``c^b_L = P_L`` (a produced ``dxn`` element contracts over
the logit-gradient row; the rmsnorm backward is elementwise in the extracted circuit, so only the ``dxn`` row
is forced) and a produced logit row costs the head forward ``P_L`` MACs and needs the whole head matrix.  The
attention terms are added only when the anatomy ``o = (softmax(q k^T) v) W_o`` with ``q, k, v`` first
projections (and, backward, the four attention dgrads feeding the block output add) is verified.  Verified
structurally per block (``c = 0`` and the chain constraint dropped otherwise).  Prefix / suffix requirements
of attention (other tokens' ``k, v`` / ``do`` rows) are not charged.

*(W) work is bilinear in operands.*  A MAC needs its weight element and its token row present: ``mf <=
(working tokens) P_l + (MACs the cheap bytes can feed)`` and ``mf <= Q (weights present)``.  A wgrad MAC
needs both operand rows for its token; a *completed* ``dW`` element needs all ``Q`` of them (``z``); other
wgrad MACs produce partial sums that are useless unless combined -- they are work in ``G`` only.  The work
per MAC is the op's gate work over its MACs (``>= 1``; accumulator init / rounding), so ``(G)`` under-counts.

*(P) produced weights.*  ``W_{k,l}[n,j]`` produced in ``R`` requires ``dW_{k-1,l}[n,j]`` present (completed
or imported as ``pi``, 2 bytes -- the price of importing ``W`` itself) and ``W_{k-1,l}[n,j]`` present.

*(F) upstream work.*  A completed ``dW_{k-1,l}[n,j]`` depends on ``x_{k-1,l}[q, j]`` and ``dY_{k-1,l}[q, n]``
for every token ``q``.  For a token that hops at a level between the hop and ``l`` (is not exempt), the
hop's forced work is in ``Up_R(dW)``; the exemption set over-counts (every ``I``/cheap token between the hop
and ``l`` is exempted, whichever class), so the constraint is a relaxation.  Linearised with a big-``M`` on
``z_{k-1,l}``.

*(G)* is the definition of legality.  The MILP relaxation enlarges the set of shapes (real-valued tokens and
weights, dropped block structure of unverified blocks), so its minimum of ``I - sum lambda M`` over the
polytope being ``>= 0`` implies ``sum_{m in R} p_m <= I(R)`` for every legal RU; summing over the partition
gives the theorem.  ``mu``: every weight element of every ``k >= 1`` version is present in at least one RU
(its fwd MACs are somewhere), so ``sum_R (w^{imp}+w^{prod})(R) >= sum P_l``.

What is NOT charged (sound but loose): attention structure (its weights and MACs enter only through ``P_l``
and ``G``), recompute, non-matmul work, the embedding table.  Assumptions verified structurally per block,
else the block's hop constants are zeroed and its working tokens are unconstrained: pre-norm residual
``h_{l+1} = h_l + o + down``, SwiGLU MLP ``down(swiglu(g, u))`` (one part, or the expert batch + shared
experts of an MoE block), rmsnorm inputs, inter-block
tensor identity (``h_out`` of ``l-1`` is ``h_in`` of ``l``).  Known gap: circuits with no weight state
(pure activation graphs) get only the root floor -- F/G-forced activation cuts are not credited there.
"""
from __future__ import annotations

import math
import os
import sys
import time
import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import coo_matrix, vstack

from accumulation.bounds.lower import LowerBound
from accumulation.graph.opgraph import Op, OpGraph, Tensor

__all__ = ["CoarseModel", "analyse", "lower_coarse", "price_lp"]

_MC_LEVELS = int(os.environ.get("LOWER_COARSE_MC_LEVELS", "0"))   # dyadic token intervals in the bilinear
                          # (tokens x weights) relaxation; 0 = plain McCormick (the interval binaries made the
                          # training shape MILP intractable at 8B for ~2 % gain)
_TOL = 1e-7
_PC_LEVELS = 4            # dyadic levels of completed-gradient elements (operand-column charge), binaries per cell
_MILP_TIME = float(os.environ.get("LOWER_COARSE_MILP_S", "180"))   # seconds per shape MILP (bound-certified)
_MILP_THREADS = int(os.environ.get("LOWER_COARSE_THREADS", "1"))   # HiGHS threads per shape MILP
_REFINE_S = float(os.environ.get("LOWER_COARSE_REFINE_S", "120"))    # wall-clock budget of the per-layer price refinement (0 = off)
_MC_ENUM = int(os.environ.get("LOWER_COARSE_MC_ENUM", "12"))         # token-count slabs of the bilinear relaxation
                          # (one shape MILP per slab; default only for single-step circuits, set the env to force)
_MC_RATIO = float(os.environ.get("LOWER_COARSE_MC_RATIO", str(math.sqrt(2.0))))   # slab ratio (hi / lo)
_INT_TOKENS = 16          # token counts are integer variables when Q <= this (tiny exact-solver cells)
try:                                                               # width of a partial sum crossing an RU boundary
    from accumulation.bounds.coarse import ACC_BYTES as _ACC_BYTES
except Exception:                                                  # pragma: no cover
    _ACC_BYTES = 4


# ---------------------------------------------------------------------------------------------------------
# graph analysis
# ---------------------------------------------------------------------------------------------------------

@dataclass
class BlockInfo:
    l: int
    P: int                       # weight elements per block (= fwd MACs per token)
    r_in: int                    # block input row length (elements)
    dmax: int = 0                # largest dimension of any weight matrix of the block (operand columns per dW)
    c_hop_f: int = 0             # forced fwd MACs of a token hopping through the block with no imports (0 if unverified)
    c_hop_b: int = 0             # forced dgrad MACs of a backward hop with no imports
    s_f: int = 0                 # max fwd MACs one imported block element can save a hopping token
    s_b: int = 0                 # max dgrad MACs one imported element can save
    c_self_f: int = 0            # fwd MACs of the block upstream of its own dW for a token with no imports (g, u, q)
    c_self_b: int = 0            # dgrad MACs of the block upstream of its own dW (dS, dx', do)
    c_cheap: int = 0             # max MACs one imported activation byte can feed (cheap-token yield)
    # mixture of experts (static balanced routing): P = P_dense + E P_exp weight elements, P_act = P_dense +
    # topk P_exp MACs per token, every expert weight element is used by exactly T_e = Q topk / E tokens
    E: int = 1                   # experts (1 = dense block)
    topk: int = 1
    P_dense: int = 0             # weight elements every token uses (attention, router, shared / dense MLP)
    P_exp: int = 0               # weight elements of one expert
    T_e: int = 0                 # tokens routed to one expert
    verified_f: bool = False     # block-l fwd structure verified (Phi(l) lemma applies)
    verified_b: bool = False     # block-l bwd structure verified (Psi(l) lemma applies)
    hop_f: bool = False          # forced-work hop through this block (fwd) is certified
    hop_b: bool = False          # forced-work hop through this block (bwd) is certified
    h_in: dict[int, int] = field(default_factory=dict)      # step -> tensor id of h_l
    h_out: dict[int, int] = field(default_factory=dict)     # step -> tensor id of h_{l+1}
    dh_in: dict[int, int] = field(default_factory=dict)     # step -> tensor id of dh_{l+1}
    dh_out: dict[int, int] = field(default_factory=dict)    # step -> tensor id of dh_l
    notes: list[str] = field(default_factory=list)


@dataclass
class CellInfo:
    k: int
    l: int
    macs: dict[str, int] = field(default_factory=lambda: {"fwd": 0, "dgrad": 0, "wgrad": 0})
    work: dict[str, int] = field(default_factory=lambda: {"fwd": 0, "dgrad": 0, "wgrad": 0})   # incl. overhead
    wr: dict[str, float] = field(default_factory=lambda: {"fwd": 1.0, "dgrad": 1.0, "wgrad": 1.0})
    # min over the class's matmuls of work / MACs: every complete output element carries its chain's overhead
    ops: dict[str, list[int]] = field(default_factory=lambda: {"fwd": [], "dgrad": [], "wgrad": []})
    weights: set[int] = field(default_factory=set)      # tensor ids of the weight version(s) read


@dataclass
class CoarseModel:
    K: int                        # weight versions (steps 0..K-1)
    L: int                        # head block index (blocks 0..L-1 are transformer blocks)
    Q: int                        # tokens per step
    d: int
    V: int
    blocks: list[BlockInfo]
    cells: dict[tuple[int, int], CellInfo]
    token_bytes: int
    root_bytes: int               # non-fixed (accumulated / carried) root weights read by some op: imported >= once
    target_macs: int              # credited MACs (k >= 1, l >= 1, fwd + dgrad + wgrad, no recompute)
    all_macs: int
    dyn_roots: bool = False       # the step-0 weights are non-fixed roots (dynamic values, not members of theta)
    charge_roots: bool = False    # LP mode: step-0 weights must be imported (2 B / element) and are credited
    head_bwd_rows: int = 0        # V (logit row length)
    scale: float = 1.0            # MAC / weight-element unit inside the LP (keeps HiGHS magnitudes sane)
    credit_layer0: bool = False   # also price block-0 MACs (validation mode; the headline excludes block 0)
    extra_root_bytes: int = 0     # read dynamic roots the LP does not price (table, gains): add to the LP cap
    notes: list[str] = field(default_factory=list)

    @property
    def moe(self) -> bool:
        return any(bl.E > 1 for bl in self.blocks)

    def credited(self, k: int, l: int) -> bool:
        lo = 0 if self.credit_layer0 else 1
        return (k >= 1 or self.charge_roots) and lo <= l <= self.L - 1

    def credited_macs(self) -> int:
        return sum(c.macs["fwd"] + c.macs["dgrad"] + c.macs["wgrad"] for (k, l), c in self.cells.items()
                   if self.credited(k, l))


def _read_leaves(T: list[Tensor], ops: list[Op]) -> dict[int, int]:
    """Leaves of each tensor covered by the union of the ranges of every edge reading it (an edge with no
    recorded ranges reads the whole tensor)."""
    spans: dict[int, list[tuple[int, int]]] = {}
    whole: set[int] = set()
    reads: dict[int, int] = {}                   # leaves read with repeats (all copies): caps a range union
    for o in ops:
        for e in o.inputs:
            reads[e.src] = reads.get(e.src, 0) + e.leaves_per_copy * o.copies
            if not e.ranges:
                whole.add(e.src)
            else:
                spans.setdefault(e.src, []).extend(e.ranges)
    out: dict[int, int] = {}
    for tid in set(spans) | whole:
        n = min(T[tid].leaves, reads.get(tid, T[tid].leaves))
        if tid in whole:
            out[tid] = n
            continue
        cov, cur_lo, cur_hi = 0, None, None
        for lo, hi in sorted(spans[tid]):
            lo, hi = max(0, lo), min(hi, n)
            if hi <= lo:
                continue
            if cur_hi is None or lo > cur_hi:
                if cur_hi is not None:
                    cov += cur_hi - cur_lo
                cur_lo, cur_hi = lo, hi
            else:
                cur_hi = max(cur_hi, hi)
        if cur_hi is not None:
            cov += cur_hi - cur_lo
        out[tid] = min(cov, n)
    return out


def _expert_mult(o: Op, w: int) -> int:
    """``E > 1`` when the ``copies`` of matmul ``o`` each read their own slice of weight ``w`` (an expert batch:
    the recorded ranges cover ``copies`` weight matrices), else 1 (a dense matmul or copies sharing ``w``)."""
    if o.copies <= 1:
        return 1
    M, N, K_ = _shape(o)
    a, b = _operands(o)
    wsz = N * K_ if w == b else M * K_
    cov = sum(hi - lo for e in o.inputs if e.src == w for lo, hi in e.ranges)
    return o.copies if cov >= o.copies * wsz else 1


def _shape(o: Op) -> tuple[int, int, int]:
    s = o.statics
    return int(s["M"]), int(s["N"]), int(s["K"])


def _p_act(bl: BlockInfo) -> int:
    """Weight elements one token multiplies in block ``bl`` (= fwd MACs per token)."""
    return bl.P_dense + bl.topk * bl.P_exp if bl.E > 1 else bl.P


def _operands(o: Op) -> tuple[int, int]:
    if len(o.inputs) == 2:
        return o.inputs[0].src, o.inputs[1].src
    return o.inputs[0].src, o.inputs[0].src


def analyse(g: OpGraph, *, credit_layer0: bool = False) -> CoarseModel:
    """Recover the (step, block) structure of a chained training circuit from its op graph."""
    notes: list[str] = []
    T = g.tensors
    ops = g.ops
    prod = {t.id: (ops[t.producer] if t.producer is not None else None) for t in T}

    # --- weight versions -----------------------------------------------------------------------------
    # root accumulated/carried params that feed a matmul are version-0 weights; sgdupdate chains give k >= 1
    matmul_reads: dict[int, list[Op]] = {}
    for o in ops:
        if o.kind == "matmul":
            for e in o.inputs:
                matmul_reads.setdefault(e.src, []).append(o)
    root_w = {t.id for t in T if t.kind == "param" and t.role in ("accumulated", "carried") and t.id in matmul_reads}
    version: dict[int, tuple[int, int, int]] = {}          # tid -> (k, root tid, layer or -1 for "by ranges")
    dW_of: dict[int, tuple[int, int, int]] = {}            # dW tid -> (k, root, layer)
    for r in root_w:
        version[r] = (0, r, -1)

    per_layer_cache: dict[int, int] = {}

    def _per_layer(root: int) -> int:
        """Weight elements of ``root`` per layer slot: the smallest matrix a matmul reads from it, times the
        expert count when the matmul is an expert batch (each copy reads its own matrix)."""
        if root not in per_layer_cache:
            cand = set()
            for o in matmul_reads.get(root, []):
                M, N, K = _shape(o)
                _a, b = _operands(o)
                cand.add((N * K if b == root else M * K) * _expert_mult(o, root))
            per_layer_cache[root] = min(cand) if cand else T[root].leaves
        return per_layer_cache[root]

    # --- "depends on a loss gradient of the current step": propagation stops at weight updates, otherwise
    # every step-k activation would count as a gradient of step k-1
    grad_dep: dict[int, bool] = {}
    for o in ops:
        d_ = o.kind == "lossgrad"
        if o.kind not in ("sgdupdate", "esupdate"):
            for e in o.inputs:
                p = prod[e.src]
                if p is not None and grad_dep.get(p.id, False):
                    d_ = True
        grad_dep[o.id] = d_

    # head root: weight of the matmul feeding lossgrad (step 0 reads the root directly)
    head_root: int | None = None
    for o in ops:
        if o.kind == "lossgrad":
            for e in o.inputs:
                p = prod[e.src]
                if p is not None and p.kind == "matmul":
                    for t_ in _operands(p):
                        if t_ in version:
                            head_root = version[t_][1]
    if head_root is None:                            # inference graph: the weight of the sink matmul (logits)
        read_t = {e.src for o in ops for e in o.inputs}
        for o in ops:
            if o.kind == "matmul" and o.out not in read_t:
                for t_ in _operands(o):
                    if t_ in version:
                        head_root = version[t_][1]
    layers_of_root: dict[int, int] = {}
    for r in root_w:
        layers_of_root[r] = max(1, T[r].leaves // _per_layer(r))
    n_layers = max((n for r, n in layers_of_root.items() if r != head_root), default=0)
    L = n_layers                                     # head block index
    # Roots stacked over every layer (attention) give the layer of a read directly from its slot; roots present
    # in a subset of the layers (the dense MLP of the leading dense layers, router / experts / shared experts
    # of the MoE layers) map slot -> layer through the nearest full-depth weight matmul upstream of their
    # step-0 forward reads (the block's own W_o, through h' = h + o and rmsnorm).
    full_depth = {r for r, n in layers_of_root.items() if n == n_layers and r != head_root}

    def slot_of(e_src: int, o: Op, root: int) -> int:
        for e in o.inputs:
            if e.src == e_src and e.ranges:
                per = _per_layer(root)
                return e.ranges[0][0] // per if per else 0
        return 0

    def anchor(t: int, depth: int = 6) -> int | None:
        p = prod[t]
        if p is None:
            return None
        if p.kind == "matmul":
            for x in _operands(p):
                if x in version and version[x][1] in full_depth:
                    return slot_of(x, p, version[x][1])
        if depth == 0:
            return None
        found = [a_ for a_ in (anchor(e.src, depth - 1) for e in p.inputs) if a_ is not None]
        return max(found) if found else None

    slot_layer: dict[int, dict[int, int]] = {}      # partial-depth root -> slot -> layer
    for r in root_w:
        if r in full_depth or r == head_root:
            continue
        for o in matmul_reads.get(r, []):
            if grad_dep.get(o.id, False) or o.name == "recompute":
                continue
            a_, b_ = _operands(o)
            act = b_ if a_ == r else a_
            lay = anchor(act)
            if lay is not None:
                slot_layer.setdefault(r, {}).setdefault(slot_of(r, o, r), lay)

    def layer_of(e_src: int, o: Op, root: int) -> int:
        """Layer index of a read of root ``root`` by ``o`` (from the edge ranges; slot-mapped for roots that
        exist in a subset of the layers)."""
        s = slot_of(e_src, o, root)
        if root in full_depth or root == head_root:
            return s
        return slot_layer.get(root, {}).get(s, s)

    for o in ops:
        if o.kind != "sgdupdate":
            continue
        w_prev, dW = o.inputs[0].src, o.inputs[1].src
        if w_prev not in version:
            continue
        k, root, lay = version[w_prev]
        if lay < 0:
            lay = layer_of(w_prev, o, root)
        version[o.out] = (k + 1, root, lay)
        dW_of[dW] = (k, root, lay)
    K = max((v[0] for v in version.values()), default=0) + 1

    # --- classify matmuls into cells -------------------------------------------------------------------

    cells: dict[tuple[int, int], CellInfo] = {}
    op_cell: dict[int, tuple[int, int, str]] = {}    # op id -> (k, l, class)
    attn_ops: set[int] = set()
    for o in ops:
        if o.kind != "matmul":
            continue
        a, b = _operands(o)
        wt = [t_ for t_ in (a, b) if t_ in version]
        if wt:
            w = wt[0]
            k, root, lay = version[w]
            if lay < 0:
                lay = layer_of(w, o, root)
            l = L if root == head_root else lay
            act = b if w == a else a
            p = prod[act]
            cls = "dgrad" if (p is not None and grad_dep.get(p.id, False)) else "fwd"
        elif o.out in dW_of:
            k, root, lay = dW_of[o.out]
            l = L if root == head_root else lay
            cls = "wgrad"
        else:
            attn_ops.add(o.id)
            continue
        if o.name == "recompute":
            continue
        c = cells.setdefault((k, l), CellInfo(k, l))
        c.macs[cls] += o.macs()
        c.work[cls] += o.work
        if o.macs() > 0:
            r_ = o.work / o.macs()
            c.wr[cls] = r_ if c.macs[cls] == o.macs() else min(c.wr[cls], r_)
        c.ops[cls].append(o.id)
        if wt:
            c.weights.add(wt[0])
        op_cell[o.id] = (k, l, cls)
    # steps = weight versions that do forward work (the last update's output is only an output)
    K = 1 + max((k for (k, l), c in cells.items() if c.macs["fwd"] > 0), default=0)
    for key in [key for key in cells if key[0] >= K]:
        notes.append(f"cell {key}: ops beyond the last forward step ignored")
        del cells[key]

    # --- geometry --------------------------------------------------------------------------------------
    blocks: list[BlockInfo] = []
    Q = 0
    d = 0
    V = 0
    for l in range(L + 1):
        c0 = cells.get((0, l))
        if c0 is None:
            blocks.append(BlockInfo(l, 0, 0, notes=[f"block {l}: no step-0 fwd ops"]))
            continue
        P_dense = P_exp = 0
        E = 1
        T_e = 0
        toks = 0
        dmax = 0
        moe_ok = True
        for oid in c0.ops["fwd"]:
            o = ops[oid]
            M, N, K_ = _shape(o)
            a, b = _operands(o)
            wt = b if b in version else a
            wsz = N * K_ if wt == b else M * K_
            dmax = max(dmax, K_, N if wt == b else M)
            E_o = _expert_mult(o, wt)
            if E_o > 1:                              # expert batch: E matrices, each over M (N) tokens
                if E > 1 and E_o != E:
                    moe_ok = False
                E = E_o
                P_exp += wsz
                T_e = max(T_e, M if wt == b else N)
            else:
                P_dense += wsz
                toks = max(toks, o.macs() // wsz)
        bl = BlockInfo(l, P_dense + E * P_exp, 0, dmax=dmax)
        if E > 1 and moe_ok:
            bl.E, bl.P_dense, bl.P_exp, bl.T_e = E, P_dense, P_exp, T_e
        elif E > 1:
            bl.notes.append(f"block {l}: expert batches with inconsistent expert counts; treated as dense weights")
        Q = max(Q, toks)
        blocks.append(bl)
    for bl in blocks:                                # static balanced routing: topk = E T_e / Q tokens' slots
        if bl.E > 1:
            if Q > 0 and (bl.E * bl.T_e) % Q == 0 and 1 <= bl.E * bl.T_e // Q <= bl.E:
                bl.topk = bl.E * bl.T_e // Q
            else:
                bl.notes.append(f"block {bl.l}: expert token count {bl.T_e} x {bl.E} is not a multiple of Q={Q}; "
                                "treated as dense weights")
                bl.P_dense, bl.E, bl.P_exp, bl.T_e = bl.P, 1, 0, 0
        else:
            bl.P_dense = bl.P
    # residual width d: input rmsnorm of block 0's fwd ops (or head)
    for l in range(L + 1):
        c0 = cells.get((0, l))
        if c0 is None:
            continue
        for oid in c0.ops["fwd"]:
            o = ops[oid]
            a, b = _operands(o)
            act = a if b in version else b
            p = prod[act]
            if p is not None and p.kind == "rmsnorm":
                blocks[l].r_in = int(p.statics.get("K", 0))
                break
        if blocks[l].r_in == 0 and c0.ops["fwd"]:
            blocks[l].r_in = _shape(ops[c0.ops["fwd"][0]])[2]
    if blocks:
        d = blocks[0].r_in or (blocks[1].r_in if L >= 1 else 0)
        for bl in blocks:
            if bl.r_in == 0:
                bl.r_in = d
    if L < len(blocks) and cells.get((0, L)):
        o = ops[cells[(0, L)].ops["fwd"][0]]
        M, N, K_ = _shape(o)
        a, b = _operands(o)
        V = N if b in version else M
    for l in range(L + 1):
        for k in range(K):
            c = cells.get((k, l))
            P_act = _p_act(blocks[l])
            if c is not None and c.macs["fwd"] and P_act and c.macs["fwd"] != P_act * Q:
                notes.append(f"cell {(k, l)}: fwd MACs {c.macs['fwd']} != P_act Q = {P_act * Q}")

    # cheap-token yield: MACs per imported *element* of a non-weight operand, summed over the cell's ops that
    # read it (an imported x' element feeds both g and u; an imported dh element feeds the whole dS row)
    for l in range(L + 1):
        best = 0.0
        for k in range(K):
            c = cells.get((k, l))
            if c is None:
                continue
            per_t: dict[int, float] = {}
            for cls in ("fwd", "dgrad", "wgrad"):
                for oid in c.ops[cls]:
                    o = ops[oid]
                    for t_ in set(_operands(o)):
                        if t_ in version or T[t_].leaves == 0:
                            continue
                        per_t[t_] = per_t.get(t_, 0.0) + o.macs() / (T[t_].leaves * T[t_].width / 8)
            best = max(best, max(per_t.values(), default=0.0))
        blocks[l].c_cheap = math.ceil(best)                # MACs per imported byte

    # --- structural verification of blocks ---------------------------------------------------------------
    for l in range(L + 1):
        _verify_block(g, cells, blocks[l], version, prod, d, Q, L)
    # hop constants apply only where block l's output row is exactly block l+1's input row (per step)
    for l in range(L):
        bl, nxt = blocks[l], blocks[l + 1]
        bl.hop_f = bl.verified_f and all(bl.h_out.get(k) == nxt.h_in.get(k) for k in nxt.h_in)
        nxt.hop_b = nxt.verified_b and all(nxt.dh_out.get(k) == bl.dh_in.get(k) for k in bl.dh_in)
        if not bl.hop_f:
            bl.c_hop_f = 0
        if not nxt.hop_b:
            nxt.c_hop_b = 0
    if L < len(blocks):
        blocks[L].c_hop_f = 0
    # block-0 input rows are free: either exogenous tokens (already in ``token_bytes``) or an embedding gather
    # (no work) of a root table that is never updated in these circuits (part of the free step-0 baseline).
    # An updated table would have to enter the weight machinery; flag it.
    for k in range(K):
        t_in = blocks[0].h_in.get(k) if blocks else None
        pr = prod.get(t_in) if t_in is not None else None
        if pr is not None and pr.kind in ("embed", "gather"):
            for e in pr.inputs:
                if T[e.src].kind == "op" and prod[e.src] is not None and prod[e.src].kind in ("sgdupdate", "esupdate"):
                    notes.append(f"step {k}: embedding table is updated; its rows are treated as free (loose)")

    # non-fixed roots enter some RU exactly where they are read: charge the union of the leaf ranges actually
    # read by some op (a row / slice view of a root costs only that slice), not the tensor size
    read_leaves = _read_leaves(T, ops)
    token_bytes = sum(read_leaves.get(t.id, 0) * t.width // 8 for t in T
                      if t.kind == "param" and t.role in ("token", "seed"))
    root_bytes = sum(read_leaves.get(t.id, 0) * t.width // 8 for t in T
                     if t.kind == "param" and (t.role or "fixed") not in ("fixed", "token", "seed"))
    dyn_roots = any((T[w].role or "fixed") != "fixed" for c in cells.values() for w in c.weights
                    if T[w].kind == "param")
    # dynamic roots the LP prices (block weights present in an RU are imported at 2 B); the rest of the root
    # floor (embedding table, norm gains, ...) is a disjoint charge class and adds to the LP certificate
    lp_roots = {w for c in cells.values() for w in c.weights
                if T[w].kind == "param" and (T[w].role or "fixed") not in ("fixed", "token", "seed")}
    lp_root_bytes = sum(read_leaves.get(w, 0) * T[w].width // 8 for w in lp_roots)
    all_macs = sum(o.macs() for o in ops)
    if K <= 1 and not dyn_roots:
        notes.append("fixed weights, no weight versions beyond step 0: nothing is credited (inference circuit)")
    scale = max(1.0, max((bl.P for bl in blocks), default=1.0) / 100.0)
    m = CoarseModel(K=K, L=L, Q=Q, d=d, V=V, blocks=blocks, cells=cells, token_bytes=token_bytes, scale=scale,
                    root_bytes=root_bytes, target_macs=0, all_macs=all_macs, dyn_roots=dyn_roots,
                    charge_roots=(dyn_roots and K <= 1), head_bwd_rows=V, credit_layer0=credit_layer0, notes=notes,
                    extra_root_bytes=max(0, root_bytes - lp_root_bytes))
    m.target_macs = m.credited_macs()
    return m


def _attention_anatomy(prod: dict, first: list[Op], o_t: int, version: dict) -> tuple[int, int, int, int] | None:
    """``(W_q, W_k, W_v, W_o)`` if ``o_t = matmul(PV, W_o)`` with ``PV = matmul(softmax(matmul(q, k)), v)`` and
    ``q, k, v`` outputs of three distinct projections in ``first`` (else ``None``)."""
    o_mm = prod.get(o_t)
    if o_mm is None or o_mm.kind != "matmul":
        return None
    ws = [t for t in _operands(o_mm) if t in version]
    acts = [t for t in _operands(o_mm) if t not in version]
    if len(ws) != 1 or len(acts) != 1:
        return None
    wo = ws[0]
    pv = prod.get(acts[0])
    if pv is None or pv.kind != "matmul" or any(t in version for t in _operands(pv)):
        return None
    by_out = {o.out: o for o in first}
    a, b = _operands(pv)
    sm_t, v_t = (a, b) if b in by_out else (b, a)
    sm = prod.get(sm_t)
    if v_t not in by_out or sm is None or sm.kind != "softmax":
        return None
    sc = prod.get(sm.inputs[0].src)
    if sc is None or sc.kind != "matmul" or any(t in version for t in _operands(sc)):
        return None
    q_t, k_t = _operands(sc)
    if q_t not in by_out or k_t not in by_out:
        return None
    wq = next(t for t in _operands(by_out[q_t]) if t in version)
    wk = next(t for t in _operands(by_out[k_t]) if t in version)
    wv = next(t for t in _operands(by_out[v_t]) if t in version)
    if len({wq, wk, wv, wo}) != 4:
        return None
    return wq, wk, wv, wo


def _verify_block(g: OpGraph, cells: dict, bl: BlockInfo, version: dict, prod: dict, d: int, Q: int, L: int) -> None:
    """Check the pre-norm residual + SwiGLU structure of block ``l`` at every step and record the block's
    interface tensors (``h_in``, ``h_out``, ``dh_in``, ``dh_out``) and hop constants.

    Forward (``l < L``): ``x = rmsnorm(h_in)`` feeds the first projections (``K = d``); ``h' = add(h_in, o)`` with
    ``o`` one of the block's fwd matmuls; ``x' = rmsnorm(h')``; ``g, u`` fwd matmuls on ``x'``;
    ``down = matmul(swiglu(g, u), W_d)`` (every such part of an MoE block reads the same x'); ``h_out = add(h', m)``
    with ``m`` an add / rowscale combination of the down outputs.  Head: ``xn = rmsnorm(h_in)``
    feeds the head matmul.
    Backward (``l < L``): ``dS = matmul(dh_in, W_d)`` (``N = ffn, K = d``); ``dg, du = mul(dS, .)`` feed the
    ``g/u`` dgrads whose outputs are added into ``dx'``; ``dh' = add(dh_in, gain(dx'))``; ``dh_out = add(dh', .)``.
    Head: the head dgrad reads the ``lossgrad`` output and ``dh_out`` is an elementwise function of it."""
    ops, T = g.ops, g.tensors
    l = bl.l
    consumers: dict[int, list[Op]] = {}
    for o in ops:
        for e in o.inputs:
            consumers.setdefault(e.src, []).append(o)

    def act_of(o: Op) -> int:
        a, b = _operands(o)
        return a if b in version else b

    def w_of(o: Op) -> int:
        return next(t_ for t_ in _operands(o) if t_ in version)

    def elementwise_source(t: int, targets: set[int], depth: int = 6) -> bool:
        """``t`` is produced from some tensor in ``targets`` through elementwise ops only."""
        if t in targets:
            return True
        p = prod.get(t)
        if p is None or depth == 0 or p.kind not in ("add", "mul", "gain", "identity_view", "reshape", "scale", "sub",
                                                      "rowscale"):
            return False
        return any(elementwise_source(e.src, targets, depth - 1) for e in p.inputs)

    ok_f = ok_b = True
    c_f = c_b = s_f = s_b = 0
    c_self_f = c_self_b = 0
    steps = sorted(k for (k, ll) in cells if ll == l)
    if not steps:
        bl.notes.append("no cells")
        return
    for k in steps:
        c = cells[(k, l)]
        fwd = [ops[i] for i in c.ops["fwd"]]
        dg = [ops[i] for i in c.ops["dgrad"]]
        if l == L:                                       # ---- head
            if len(fwd) != 1:
                ok_f = False
                bl.notes.append(f"step {k}: {len(fwd)} head matmuls")
            else:
                n0 = prod[act_of(fwd[0])]
                if n0 is None or n0.kind != "rmsnorm" or int(n0.statics.get("K", 0)) != d:
                    ok_f = False
                    bl.notes.append(f"step {k}: head input is not rmsnorm(h) over d")
                else:
                    bl.h_in[k] = n0.inputs[0].src
            if len(dg) != 1:
                ok_b = False
                bl.notes.append(f"step {k}: {len(dg)} head dgrads")
            else:
                lg = prod[act_of(dg[0])]
                if lg is None or lg.kind != "lossgrad":
                    ok_b = False
                    bl.notes.append(f"step {k}: head dgrad input is not the loss gradient")
                else:
                    bl.dh_in[k] = act_of(dg[0])
                    outs = [o for o in consumers.get(dg[0].out, []) if o.kind in ("gain", "mul", "identity_view", "scale")]
                    # dh_L: the elementwise image of the head dgrad output that a block's dS reads
                    cands = [o.out for o in outs if any(cc.kind == "matmul" for cc in consumers.get(o.out, []))]
                    if len(cands) == 1:
                        bl.dh_out[k] = cands[0]
                    elif any(cc.kind == "matmul" for cc in consumers.get(dg[0].out, [])):
                        bl.dh_out[k] = dg[0].out
                    else:
                        ok_b = False
                        bl.notes.append(f"step {k}: cannot identify dh_L")
            continue
        # ---- forward.  MLP parts: every ``down = matmul(swiglu(g, u), W_d)`` of the cell (one for a dense
        # block; the expert batch and the shared expert(s) for an MoE block), all reading the same x'.
        downs = [o for o in fwd if prod[act_of(o)] is not None and prod[act_of(o)].kind == "swiglu"]
        if not downs or (len(downs) != 1 and bl.E <= 1):
            ok_f = False
            bl.notes.append(f"step {k}: {len(downs)} down projections")
            continue
        down = downs[0]
        gu: list[Op] = []
        parts: list[tuple[Op, list[Op]]] = []      # (down, [g, u]) per MLP part
        bad = False
        for dn in downs:
            sw = prod[act_of(dn)]
            gu_p = [prod[e.src] for e in sw.inputs]
            if len(gu_p) != 2 or any(p is None or p.id not in c.ops["fwd"] for p in gu_p):
                bad = True
                break
            if len({p.copies for p in gu_p} | {dn.copies}) != 1:
                bad = True                                       # g, u, down of one part share the expert batch
                break
            gu += gu_p
            parts.append((dn, gu_p))
        if bad:
            ok_f = False
            bl.notes.append(f"step {k}: swiglu inputs are not this block's fwd matmuls")
            continue
        xp = {act_of(p) for p in gu}
        if len(xp) != 1:
            ok_f = False
            bl.notes.append(f"step {k}: g/u read different inputs")
            continue
        xp_t = next(iter(xp))
        n2 = prod[xp_t]
        if n2 is None or n2.kind != "rmsnorm":
            ok_f = False
            bl.notes.append(f"step {k}: MLP input is not rmsnorm")
            continue
        hp = n2.inputs[0].src
        addp = prod[hp]
        if addp is None or addp.kind != "add":
            ok_f = False
            bl.notes.append(f"step {k}: h' not an add")
            continue
        h_in_c = [e.src for e in addp.inputs if not (prod[e.src] is not None and prod[e.src].id in c.ops["fwd"])]
        o_prods = [e.src for e in addp.inputs if prod[e.src] is not None and prod[e.src].id in c.ops["fwd"]]
        if len(h_in_c) != 1 or len(o_prods) != 1:
            ok_f = False
            bl.notes.append(f"step {k}: residual add is not h + projection")
            continue
        h_in = h_in_c[0]
        mlp_ops = {o.id for o in gu} | {o.id for o in downs}
        # first projections read rmsnorm(h_in); the router (MoE) reads x' like the MLP parts and is not one
        first = [o for o in fwd if o.id not in mlp_ops and o.out != o_prods[0] and act_of(o) != xp_t]
        routers = [o for o in fwd if o.id not in mlp_ops and o.out != o_prods[0] and act_of(o) == xp_t]
        if routers and bl.E <= 1:
            ok_f = False
            bl.notes.append(f"step {k}: {len(routers)} extra projections read x'")
        for o in first:
            n1 = prod[act_of(o)]
            if n1 is None or n1.kind != "rmsnorm" or n1.inputs[0].src != h_in or int(n1.statics.get("K", 0)) != d:
                ok_f = False
                bl.notes.append(f"step {k}: projection {o.id} does not read rmsnorm(h_in)")
        if not ok_f:
            continue
        # per token: the MLP parts it runs (an expert part topk times, a dense / shared part once)
        ffn_tok = 0                                      # sum of the token's down contraction lengths
        mlp_tok = 0                                      # the token's MLP MACs: sum ffn_p (K_g + K_u + d)
        Kg_max = 0
        ffn_min = None
        for dn, gu_p in parts:
            _, _, ffn_p = _shape(dn)
            Kg_p = sum(_shape(p)[2] for p in gu_p)
            mult = bl.topk if (bl.E > 1 and dn.copies == bl.E) else 1
            ffn_tok += mult * ffn_p
            mlp_tok += mult * (ffn_p * Kg_p + d * ffn_p)
            Kg_max = max(Kg_max, Kg_p)
            ffn_min = ffn_p if ffn_min is None else min(ffn_min, ffn_p)
        _, _, K_d = _shape(down)
        ffn = K_d
        Kg = sum(_shape(p)[2] for p in parts[0][1])
        if ffn_min < 1 or T[xp_t].leaves != Q * d or T[h_in].leaves != Q * d:
            ok_f = False
            bl.notes.append(f"step {k}: ffn={ffn_min} d={d} leaves(x')={T[xp_t].leaves}")
            continue
        # h_out = add(h', m) with m an elementwise (add / rowscale) combination of the down outputs
        down_outs = {dn.out for dn in downs}
        outs = [o for o in consumers.get(hp, []) if o.kind == "add" and o is not addp
                and any(e.src != hp and elementwise_source(e.src, down_outs, 2 + 2 * len(downs) + bl.topk)
                        for e in o.inputs)]
        if len(outs) != 1:
            ok_f = False
            bl.notes.append(f"step {k}: block output add not found ({len(outs)})")
            continue
        bl.h_in[k], bl.h_out[k] = h_in, outs[0].out
        # a token working at block l+1 that imports < 2d bytes of block-l values (<= d-1 elements) must produce
        # >= 1 element of h_{l+1}, hence its full h_{l+1} row for the next rmsnorm: every down element of every
        # MLP part it runs (needs all of that part's s) and every non-imported s element (K_g + K_u MACs each);
        # with no imports the whole per-token MLP: sum_p ffn_p (K_g + K_u) + d ffn_p.  One imported element
        # saves at most max(sum_p ffn_p, K_g + K_u) MACs (an h element saves its down elements across the
        # parts, an s element its g and u elements).
        c_f = max(c_f, mlp_tok)
        s_f = max(s_f, max(ffn_tok, Kg_max))
        c_self_f = max(c_self_f, mlp_tok - d * ffn_tok)  # dW_g, dW_u, dW_d need the token's x' and s rows
        c_self_b = max(c_self_b, 3 * d * ffn)            # dW_o needs dh' = dh + dx_m: dS row and full dx' row
        # ---- attention (optional tightening): o = matmul(PV, W_o), PV = matmul(softmax(matmul(q, k)), v) with
        # q, k, v first projections of rmsnorm(h_in).  The produced h_{l+1} element also needs h' = h_in + o for
        # its index: o[q,n] contracts over the whole attention row (all heads), which needs the full q row
        # (|W_q| MACs); an imported h element additionally spares its o element (K_o MACs).
        attn = _attention_anatomy(prod, first, o_prods[0], version)
        att_f = att_b = att_sn = 0
        if attn is not None:
            wq, wk, wv, wo = attn
            o_mm = prod[o_prods[0]]
            K_o = _shape(o_mm)[2]
            wsz = {w_of(mm): _shape(mm)[1] * _shape(mm)[2] for mm in first + [o_mm]}   # weight elements (N K)
            att_f = wsz[wq] + wsz[wo]                     # q = A operand of the score matmul (extractor order)
            c_f = max(c_f, mlp_tok + att_f)
            c_self_f = max(c_self_f, mlp_tok - d * ffn_tok + wsz[wq])  # x' needs h' = h + o: the q row
            s_f = max(s_f, ffn_tok + K_o)
            att_b = wsz[wq] + wsz[wk] + wsz[wv] + wsz[wo]
            att_sn = sum(_shape(mm)[1] for mm in first if w_of(mm) in (wq, wk, wv))     # N_q + N_k + N_v
        if len(downs) != 1:                              # MoE backward anatomy is not verified
            ok_b = False
            bl.notes.append(f"step {k}: MoE block backward not verified")
            continue
        # ---- backward
        wd = w_of(down)
        dd = [o for o in dg if wd in _operands(o)]
        if len(dd) != 1:
            ok_b = False
            bl.notes.append(f"step {k}: {len(dd)} down-dgrad ops")
            continue
        ddo = dd[0]
        _, Nd, Kd = _shape(ddo)
        dh_in = act_of(ddo)
        if Nd != ffn or Kd != d or T[dh_in].leaves != Q * d:
            ok_b = False
            bl.notes.append(f"step {k}: down dgrad shape {(Nd, Kd)}")
            continue
        gu_w = {w_of(p) for p in gu}
        gu_d = [o for o in dg if w_of(o) in gu_w]
        if len(gu_d) != 2:
            ok_b = False
            bl.notes.append(f"step {k}: g/u dgrads not found")
            continue
        good = True
        for o in gu_d:
            src = prod[act_of(o)]
            if src is None or src.kind != "mul" or not any(e.src == ddo.out for e in src.inputs):
                good = False
            if _shape(o)[2] != ffn:
                good = False
        if not good:
            ok_b = False
            bl.notes.append(f"step {k}: g/u dgrad inputs are not mul(dS, .) over ffn")
            continue
        # dh' = add(dh_in, gain(dx')) where dx' derives elementwise from the g/u dgrad outputs
        dxp_src = {o.out for o in gu_d}
        dhp = [o for o in consumers.get(dh_in, []) if o.kind == "add"
               and any(e.src != dh_in and elementwise_source(e.src, dxp_src) for e in o.inputs)]
        if len(dhp) != 1:
            ok_b = False
            bl.notes.append(f"step {k}: dh' = dh_in + gain(dx') not found ({len(dhp)})")
            continue
        dh_p = dhp[0].out
        outs_b = [o for o in consumers.get(dh_p, []) if o.kind == "add"]
        if len(outs_b) != 1:
            ok_b = False
            bl.notes.append(f"step {k}: block bwd output add not found ({len(outs_b)})")
            continue
        bl.dh_in[k], bl.dh_out[k] = dh_in, outs_b[0].out
        # symmetric: a produced dh_l element needs its dx' element (2 ffn MACs: dg . Wg + du . Wu) and the full
        # dS row (ffn elements, d MACs each); no imports: d 2 ffn + ffn d.  An imported dh element saves 2 ffn,
        # an imported dS / dg / du element saves d.
        c_b = max(c_b, 3 * d * ffn)
        s_b = max(s_b, max(2 * ffn, d))
        if attn is not None and att_b > 0:
            # dh_l = dh' + dxa with dxa[q,n] = (dq W_q + dk W_k + dv W_v)[q,n] (N_q+N_k+N_v MACs) whose dq needs
            # the scores' gradient, hence the full do = dh' W_o^T row (|W_o| MACs, which needs every dh'
            # element): verified as the four attention dgrad matmuls of the cell feeding the block output add.
            wq, wk, wv, wo = attn
            dws = {w_of(o) for o in dg}
            other = [e.src for e in outs_b[0].inputs if e.src != dh_p]
            att_out = {o.out for o in dg if w_of(o) in (wq, wk, wv)}
            if {wq, wk, wv, wo} <= dws and len(other) == 1 and elementwise_source(other[0], att_out):
                c_b = max(c_b, 3 * d * ffn + att_b)
                s_b = max(s_b, att_sn)
                c_self_b = max(c_self_b, 3 * d * ffn + wsz[wo])   # dW_q needs dq, hence the scores' gradient: do
    if l < L:
        ok_b = ok_b and ok_f                             # the bwd checks reuse the fwd anatomy
    bl.verified_f, bl.verified_b = ok_f, ok_b
    if l == L:
        bl.c_hop_f = 0
        bl.c_hop_b = bl.P if ok_b else 0                  # V d: the full dxn row; an imported dxn element saves V
        bl.s_b = (bl.P // d) if (ok_b and d) else 0
    else:
        bl.c_hop_f, bl.s_f = (c_f, s_f) if ok_f else (0, 0)
        bl.c_hop_b, bl.s_b = (c_b, s_b) if ok_b else (0, 0)
        bl.c_self_f = c_self_f if ok_f else 0
        bl.c_self_b = c_self_b if ok_b else 0


# ---------------------------------------------------------------------------------------------------------
# LP over RU shapes
# ---------------------------------------------------------------------------------------------------------
class _Poly:
    """Mixed-integer polytope ``A x <= b``, ``0 <= x <= ub`` with named variables."""

    def __init__(self) -> None:
        self.names: list[str] = []
        self.rows: list[tuple[dict[int, float], float]] = []
        self.ub: list[float] = []
        self.integer: list[int] = []

    def var(self, name: str, ub: float = math.inf, integer: bool = False) -> int:
        self.names.append(name)
        self.ub.append(ub)
        i = len(self.names) - 1
        if integer:
            self.integer.append(i)
        return i

    def le(self, coef: dict[int, float], rhs: float = 0.0) -> None:
        coef = {k: v for k, v in coef.items() if v != 0.0}
        if coef:
            self.rows.append((coef, rhs))

    @property
    def n(self) -> int:
        return len(self.names)

    def matrices(self):
        data, ri, ci = [], [], []
        b = np.zeros(len(self.rows))
        for r, (coef, rhs) in enumerate(self.rows):
            b[r] = rhs
            for i, v in coef.items():
                data.append(v)
                ri.append(r)
                ci.append(i)
        A = coo_matrix((data, (ri, ci)), shape=(len(self.rows), self.n)).tocsr()
        return A, b


def _dbg(msg: str) -> None:
    if os.environ.get("LOWER_COARSE_DEBUG"):
        print(f"[lower_coarse] {msg}", file=sys.stderr, flush=True)


def _add(c: dict[int, float], i: int, v: float) -> None:
    c[i] = c.get(i, 0.0) + v


def _sub(c: dict[int, float], form: dict[int, float], scale: float = 1.0) -> dict[int, float]:
    for i, v in form.items():
        _add(c, i, -scale * v)
    return c


@dataclass
class _Shapes:
    poly: _Poly
    cost: dict[int, float]                      # I(x) (bytes) as a linear form
    const: float                                # constant part of I (table case B)
    groups: dict[str, dict[int, float]]         # price group -> M_c(x) (MACs)
    weights_form: dict[int, float]              # k >= 1 weight elements present
    meta: dict[str, Any]
    # token-count levels: the shape space is covered by ``max token count in [lo_j, hi_j]`` slabs, each with the
    # tighter bilinear rows ``m <= hi_j w`` and ``m <= P (n - lo_j) + lo_j w``; a minimisation solves one MILP
    # per slab and takes the min (no interval binaries).  Empty = plain McCormick.
    levels: list[list[tuple[dict[int, float], float]]] = field(default_factory=list)
    _level_mats: list[Any] = field(default_factory=list)

    def level_matrices(self) -> list[Any]:
        if not self._level_mats:
            A0, b0 = self.poly.matrices()
            if not self.levels:
                self._level_mats = [(A0, b0)]
            else:
                for rows in self.levels:
                    data, ri, ci = [], [], []
                    b1 = np.zeros(len(rows))
                    for r, (coef, rhs) in enumerate(rows):
                        b1[r] = rhs
                        for i, val in coef.items():
                            data.append(val)
                            ri.append(r)
                            ci.append(i)
                    A1 = coo_matrix((data, (ri, ci)), shape=(len(rows), self.poly.n)).tocsr()
                    self._level_mats.append((vstack([A0, A1]).tocsr(), np.concatenate([b0, b1])))
        return self._level_mats


def _build(model: CoarseModel, F: float, G: float, group_of) -> _Shapes:
    """The polytope of legal RU shapes (theorem constraints).

    Per cell ``(k, l)``: ``nI`` / ``mI`` tokens that imported ``>= 2d`` bytes of block-``l`` fwd / bwd values
    (charged ``2d``), ``bf`` / ``bb`` every other imported byte of those values (charged 1 each), ``nW`` / ``mW``
    tokens with a produced fwd / bwd matmul element of the block, ``nP`` / ``mP`` the working tokens that hop
    (neither ``I`` here nor in the adjacent block whose row they need), ``fb`` tokens with both wgrad operand
    rows, ``mT`` produced logit rows (head), weights ``w = wimp + wprod``, MACs ``mf, md, mw``, completed /
    imported gradient elements ``pc`` / ``pi`` and the completion indicator ``z``."""
    K, L, Q, d = model.K, model.L, model.Q, model.d
    S = model.scale
    p = _Poly()
    cost: dict[int, float] = {}
    groups: dict[str, dict[int, float]] = {}
    wform: dict[int, float] = {}
    v: dict[tuple, int] = {}
    Gs, Fs = G / S, F / S
    blocks = model.blocks
    Ps = [bl.P / S for bl in blocks]
    cf = [bl.c_hop_f / S for bl in blocks]
    cb = [bl.c_hop_b / S for bl in blocks]
    sf = [bl.s_f / (2.0 * S) for bl in blocks]       # forced fwd MACs saved per imported byte
    sb = [bl.s_b / (2.0 * S) for bl in blocks]
    cC = [bl.c_cheap / S for bl in blocks]          # MACs (scaled) one imported byte can feed
    cells = model.cells
    head_ok = L < len(blocks) and (0, L) in cells and blocks[L].verified_b
    int_tokens = Q <= _INT_TOKENS      # tiny circuits: integer token counts (the fractional relaxation is very loose)
    wr_max = max((r for c_ in cells.values() for r in c_.wr.values()), default=1.0)
    M_F = wr_max * Q * (sum(cf) + sum(cb) + (2.0 * Ps[L] if head_ok else 0.0) + max(Ps)
                        + max(bl.c_self_f + bl.c_self_b for bl in blocks) / S) + Fs        # big-M for (F)

    for k in range(K):
        for l in range(L + 1):
            if (k, l) not in cells:
                continue
            for nm in ("nI", "nW", "nP", "nA", "nB", "mI", "mW", "mP", "mA", "mB", "fb"):
                v[(nm, k, l)] = p.var(f"{nm}[{k},{l}]", Q, integer=int_tokens)   # token counts are integers
            if l == L and head_ok:
                v[("mT", k, l)] = p.var(f"mT[{k},{l}]", Q, integer=int_tokens)
            wide = 2.0 * max(d, model.V if l == L else d) * Q
            for nm in ("bf", "bb"):
                v[(nm, k, l)] = p.var(f"{nm}[{k},{l}]", wide)
            v[("w", k, l)] = p.var(f"w[{k},{l}]", Ps[l])
            if k >= 1 or model.charge_roots:
                v[("wimp", k, l)] = p.var(f"wimp[{k},{l}]", Ps[l])
            if k >= 1:
                v[("wprod", k, l)] = p.var(f"wprod[{k},{l}]", Ps[l])
            cell = cells[(k, l)]
            for nm, cls in (("mf", "fwd"), ("md", "dgrad"), ("mw", "wgrad")):
                v[(nm, k, l)] = p.var(f"{nm}[{k},{l}]", cell.macs[cls] / S)
            for nm in ("pc", "pi"):
                v[(nm, k, l)] = p.var(f"{nm}[{k},{l}]", Ps[l])
            v[("z", k, l)] = p.var(f"z[{k},{l}]", 1.0, integer=True)   # the last step's update gates exist too

    def has(k, l):
        return (k, l) in cells

    work_all: dict[int, float] = {}
    levels_pc: dict[tuple[int, int], list[tuple[int, float]]] = {}   # (binary, lo) dyadic levels of pc per cell
    mc_pieces: list[tuple[int, int, int, float]] = []                 # (m, w, n, uses) bilinear pieces of credited cells
    for (k, l), cell in cells.items():
        bl = blocks[l]
        nI, nW, nP, mI, mW, mP, fb = (v[(nm, k, l)] for nm in ("nI", "nW", "nP", "mI", "mW", "mP", "fb"))
        bf, bb = v[("bf", k, l)], v[("bb", k, l)]
        w, mf, md, mw, pc, pi = (v[(nm, k, l)] for nm in ("w", "mf", "md", "mw", "pc", "pi"))
        # --- forward: a working token has the full h_l row: I here, I below, or hopping (forced work below) --
        # The working set is partitioned:  A = W & I_l,  B = (W & I_{l-1}) \ I_l,  P = W \ (I_l | I_{l-1});
        # a hopping token produced an element of h_l (a block-(l-1) value) without being I there, so
        # P_l <= (W_{l-1} \ I_{l-1}) = B_{l-1} | P_{l-1}: one imported row (or the free block-0 row) feeds one
        # chain of working tokens -- the same tokens cannot be counted both as I_{l-1} and as hoppers.
        nA, nB = v[("nA", k, l)], v[("nB", k, l)]
        p.le({nB: 1.0, nP: 1.0, nW: -1.0})                 # B | P subset of W (every block, verified or not)
        if bl.verified_f and l >= 1:
            p.le({nW: 1.0, nA: -1.0, nB: -1.0, nP: -1.0})
            p.le({nA: 1.0, nI: -1.0})
            if has(k, l - 1):
                p.le({nB: 1.0, v[("nI", k, l - 1)]: -1.0})
            else:
                p.le({nB: 1.0})
            if has(k, l - 1) and blocks[l - 1].hop_f:
                p.le({nP: 1.0, v[("nB", k, l - 1)]: -1.0, v[("nP", k, l - 1)]: -1.0})
                p.le({nP: cf[l - 1], v[("bf", k, l - 1)]: sf[l - 1], v[("mf", k, l - 1)]: -1.0})
                # any hop needs the block-(l-1) weights whose products the hopping token (< 2d bytes, i.e.
                # <= d-1 elements, imported) cannot have imported: an indicator, not a fraction
                wf = cf[l - 1] - (d - 1) * sf[l - 1]
                if wf > 0:
                    uf = p.var(f"uf[{k},{l}]", 1.0, integer=True)
                    p.le({nP: 1.0, uf: -float(Q)})
                    p.le({uf: wf, v[("w", k, l - 1)]: -1.0})
            elif not has(k, l - 1):
                p.le({nP: 1.0})
        # --- backward -------------------------------------------------------------------------------------------
        if bl.verified_b:
            if l == L:
                c = {mW: 1.0, mI: -1.0}                            # bwd-working at the head: dlogits imported or produced
                if ("mT", k, l) in v:
                    mT = v[("mT", k, l)]
                    _add(c, mT, -1.0)
                    if bl.verified_f:
                        p.le({mT: 1.0, nW: -1.0, nI: -1.0})        # a produced logit row needs the head input row
                    p.le({mT: Ps[l], nI: -Ps[l], bf: -0.5 * d, mf: -1.0})   # head fwd for the missing logits
                    p.le({mT: Ps[l] / Q, nI: -Ps[l] / Q, w: -1.0})          # whole head matrix present
                    wt = Ps[l] - (d - 1) * d / S                             # <= d-1 imported logits save d each
                    if wt > 0:
                        uT = p.var(f"uT[{k},{l}]", 1.0, integer=True)
                        p.le({mT: 1.0, nI: -1.0, uT: -float(Q)})
                        p.le({uT: wt, w: -1.0})
                p.le(c)
                p.le({mP: 1.0})
            else:
                # same partition as the forward chain, read downwards: A = W & I_l, B = (W & I_{l+1}) \ I_l,
                # P = W \ (I_l | I_{l+1}) subset of W_{l+1} \ I_{l+1} = B_{l+1} | P_{l+1} (at the head: the
                # tokens with produced dlogit rows, mT)
                mA, mB = v[("mA", k, l)], v[("mB", k, l)]
                p.le({mW: 1.0, mA: -1.0, mB: -1.0, mP: -1.0})
                p.le({mB: 1.0, mP: 1.0, mW: -1.0})
                p.le({mA: 1.0, mI: -1.0})
                if has(k, l + 1):
                    p.le({mB: 1.0, v[("mI", k, l + 1)]: -1.0})
                else:
                    p.le({mB: 1.0})
                if has(k, l + 1) and blocks[l + 1].hop_b:
                    if l + 1 == L:
                        src = {mP: 1.0}
                        if ("mT", k, L) in v:
                            src[v[("mT", k, L)]] = -1.0
                        p.le(src)
                    else:
                        p.le({mP: 1.0, v[("mB", k, l + 1)]: -1.0, v[("mP", k, l + 1)]: -1.0})
                        if not blocks[l + 1].verified_b:
                            p.le({v[("mB", k, l + 1)]: 1.0, v[("mP", k, l + 1)]: 1.0, v[("mW", k, l + 1)]: -1.0})
                    p.le({mP: cb[l + 1], v[("bb", k, l + 1)]: sb[l + 1], v[("md", k, l + 1)]: -1.0})
                    wb = cb[l + 1] - (d - 1) * sb[l + 1]
                    if wb > 0:
                        ub_ = p.var(f"ub[{k},{l}]", 1.0, integer=True)
                        p.le({mP: 1.0, ub_: -float(Q)})
                        p.le({ub_: wb, v[("w", k, l + 1)]: -1.0})
                elif not has(k, l + 1):
                    p.le({mP: 1.0})
        # --- work is bilinear in (tokens, weights); cheap bytes buy at most c_cheap MACs each -----------------
        Pa = _p_act(bl) / S                            # weights one token multiplies (= its full-work MACs)
        p.le({mf: 1.0, nW: -Pa, bf: -cC[l]})
        p.le({md: 1.0, mW: -Pa, bb: -cC[l]})
        # (X) partial outputs: MACs of tokens without a complete output element (mf - P nW, md - P mW) end in
        # partial sums that leave R; each aggregates <= 2(d-1) MACs (one per imported item of the token), and the
        # consumer counts the ACC_BYTES accumulator as one 2-byte item, so ACC_BYTES - 2 bytes are charged here.
        if d > 1 and _ACC_BYTES > 2:
            for m_, n_, cls_ in ((mf, nW, "fwd"), (md, mW, "dgrad")):
                if cell.macs[cls_] > 0:
                    x_ = p.var(f"x{cls_[0]}[{k},{l}]", cell.macs[cls_] / S)
                    p.le({m_: 1.0, n_: -Pa, x_: -1.0})
                    _add(cost, x_, (_ACC_BYTES - 2) * S / (2.0 * (d - 1)))
        wg = {mw: 1.0, fb: -Pa, bf: -cC[l], bb: -cC[l]}
        if has(k, l + 1):
            wg[v[("bb", k, l + 1)]] = -cC[l]           # dh_{l+1} elements are the bwd operand of W_o / W_d wgrad
        p.le(wg)
        p.le({fb: 1.0, nW: -1.0})
        p.le({fb: 1.0, mW: -1.0})
        # MACs <= (working tokens) x (weights present).  The bilinear set is non-convex; its McCormick hull over
        # the whole box is just  m <= Q w,  m <= P n.  Tighten it with dyadic token intervals selected by
        # binaries: n in [lo_j, hi_j]  =>  m <= P (n - lo_j) + lo_j w   (exact for full-work tokens: w >= m / n).
        # MoE (static balanced routing): w = w_d + w_x (dense / expert weight elements present) and m = m_d + m_x;
        # a dense element serves <= Q tokens, an expert element exactly T_e = Q topk / E of them (m_x <= T_e w_x:
        # an expert is amortised over its T_e tokens only); per token m_d <= min(w_d, P_dense), m_x <= min(w_x,
        # topk P_exp) -- the McCormick bound with W' = P_dense / topk P_exp.
        moe_parts: list[tuple[int, int]] | None = None
        if bl.E > 1:
            w_d = p.var(f"wd[{k},{l}]", bl.P_dense / S)
            w_x = p.var(f"wx[{k},{l}]", bl.E * bl.P_exp / S)
            p.le({w: 1.0, w_d: -1.0, w_x: -1.0})
            p.le({w_d: 1.0, w_x: 1.0, w: -1.0})
            moe_parts = [(w_d, bl.P_dense), (w_x, bl.topk * bl.P_exp)]
        for m_, n_, cls_, b_ in ((mf, nW, "fwd", bf), (md, mW, "dgrad", bb)):
            if moe_parts is None or cell.macs[cls_] <= 0:
                pieces = [(m_, w, float(Q), Ps[l])]
            else:
                m_d = p.var(f"m{cls_[0]}d[{k},{l}]", cell.macs[cls_] / S)
                m_x = p.var(f"m{cls_[0]}x[{k},{l}]", cell.macs[cls_] / S)
                p.le({m_: 1.0, m_d: -1.0, m_x: -1.0})
                p.le({m_d: 1.0, m_x: 1.0, m_: -1.0})
                p.le({m_d: 1.0, n_: -bl.P_dense / S, b_: -cC[l]})
                p.le({m_x: 1.0, n_: -bl.topk * bl.P_exp / S, b_: -cC[l]})
                pieces = [(m_d, moe_parts[0][0], float(Q), bl.P_dense / S),
                          (m_x, moe_parts[1][0], float(bl.T_e), bl.topk * bl.P_exp / S)]
            for mm, ww, uses, Wp in pieces:
                p.le({mm: 1.0, ww: -uses})
                if cell.macs[cls_] > 0 and model.credited(k, l):
                    mc_pieces.append((mm, ww, n_, uses))
                if cell.macs[cls_] <= 0 or Q < 4 or _MC_LEVELS <= 0:
                    continue
                levels = []
                hi_ = float(Q)
                for _j in range(_MC_LEVELS):
                    lo_ = hi_ / 2.0
                    if lo_ < 1.0:
                        break
                    levels.append((lo_, hi_))
                    hi_ = lo_
                levels.append((0.0, hi_))
                ys = [p.var(f"y[{k},{l},{cls_},{mm},{j}]", 1.0, integer=True) for j in range(len(levels))]
                p.le({y_: 1.0 for y_ in ys}, 1.0)
                p.le({y_: -1.0 for y_ in ys}, -1.0)
                c_hi = {n_: 1.0}
                c_lo = {n_: -1.0}
                for y_, (lo_, hi_) in zip(ys, levels):
                    c_hi[y_] = -hi_
                    c_lo[y_] = lo_
                p.le(c_hi)
                p.le(c_lo)
                mmax = cell.macs[cls_] / S
                for y_, (lo_, hi_) in zip(ys, levels):
                    if lo_ <= 0.0:
                        continue
                    M_ = mmax + Wp * lo_
                    p.le({mm: 1.0, n_: -Wp, ww: -lo_, y_: M_}, M_ - Wp * lo_)
        # --- completed weight gradients need every token's operand elements ------------------------------------
        p.le({mw: -1.0, pc: Q})
        p.le({mw: 1.0, pc: -1.0}, (Q - 1) * Ps[l])     # pigeonhole: an incomplete element has <= Q-1 MACs in R
        p.le({pc: 1.0, pi: 1.0}, Ps[l])
        if ("z", k, l) in v:
            z = v[("z", k, l)]
            p.le({pc: 1.0, z: -Ps[l]})
            p.le({z: Q, nW: -1.0, nI: -1.0, bf: -0.5})                       # fwd operand element per token
            cbw = {z: Q, mW: -1.0, mI: -1.0, bb: -0.5}                       # bwd operand element per token
            if has(k, l + 1):
                cbw[v[("bb", k, l + 1)]] = -0.5
                cbw[v[("mI", k, l + 1)]] = -1.0
            p.le(cbw)
            # operand *columns*: ``pc`` completed elements of an ``N x K`` weight touch >= pc / K output
            # indices and >= pc / N contraction indices, so every token without the operand rows imports
            # >= 2 pc / dmax bytes per side.  Dyadic levels of ``pc`` (binaries) linearise the product.
            if bl.dmax > 0 and _PC_LEVELS > 0:
                ys, hi_ = [], float(bl.P)
                pc_cap = {pc: 1.0}
                M_pc = 2.0 * Q * bl.P / bl.dmax                              # max of the column charge (bytes)
                for j in range(_PC_LEVELS):
                    lo_ = hi_ / 2.0
                    y_ = p.var(f"ypc[{k},{l},{j}]", 1.0, integer=True)
                    ys.append(y_)
                    levels_pc.setdefault((k, l), []).append((y_, lo_))
                    pc_cap[y_] = -hi_ / S
                    cj = lo_ / bl.dmax                                       # operand columns per side
                    cx = {bf: -1.0, nW: -2.0 * cj, nI: -2.0 * cj, y_: 2.0 * cj * Q}
                    cy = dict(cbw)
                    cy = {kk: (-2.0 * cj if kk not in (z, bb) else 0.0) for kk in cy}
                    cy[bb] = -1.0
                    if has(k, l + 1):
                        cy[v[("bb", k, l + 1)]] = -1.0
                        cy[v[("mI", k, l + 1)]] = -2.0 * cj
                    cy[mW], cy[mI] = -2.0 * cj, -2.0 * cj
                    cy.pop(z, None)
                    cy[y_] = 2.0 * cj * Q
                    p.le(cx)
                    p.le(cy)
                    # and within the level, (hi_j - pc) n >= 0:  columns (Q - n) >= (Q pc - hi_j n) / dmax
                    self_x = {bf: -1.0, pc: 2.0 * Q * S / bl.dmax, nW: -2.0 * hi_ / bl.dmax,
                              nI: -2.0 * hi_ / bl.dmax, y_: M_pc}
                    p.le(self_x, M_pc)
                    self_y = {bb: -1.0, pc: 2.0 * Q * S / bl.dmax, mW: -2.0 * hi_ / bl.dmax,
                              mI: -2.0 * hi_ / bl.dmax, y_: M_pc}
                    if has(k, l + 1):
                        self_y[v[("bb", k, l + 1)]] = -1.0
                        self_y[v[("mI", k, l + 1)]] = -2.0 * hi_ / bl.dmax
                    p.le(self_y, M_pc)
                    hi_ = lo_
                pc_cap[z] = -hi_ / S
                p.le(pc_cap)
                p.le({y_: 1.0 for y_ in ys} | {z: -1.0})
                # the catch-all level (z = 1, no y_j): pc <= hi_ = P / 2^J
                yc = {y_: -M_pc for y_ in ys}
                yc[z] = M_pc
                cx0 = dict(yc)
                cx0.update({bf: -1.0, pc: 2.0 * Q * S / bl.dmax, nW: -2.0 * hi_ / bl.dmax, nI: -2.0 * hi_ / bl.dmax})
                p.le(cx0, M_pc)
                cy0 = dict(yc)
                cy0.update({bb: -1.0, pc: 2.0 * Q * S / bl.dmax, mW: -2.0 * hi_ / bl.dmax, mI: -2.0 * hi_ / bl.dmax})
                if has(k, l + 1):
                    cy0[v[("bb", k, l + 1)]] = -1.0
                    cy0[v[("mI", k, l + 1)]] = -2.0 * hi_ / bl.dmax
                p.le(cy0, M_pc)
        # --- weights: free at step 0 (root baseline; charged when dynamic), imported or produced afterwards ------
        if k == 0 and model.charge_roots:
            wimp = v[("wimp", k, l)]
            p.le({w: 1.0, wimp: -1.0})
            _add(cost, wimp, 2.0 * S)
            _add(wform, w, S)
        if k >= 1:
            wimp, wprod = v[("wimp", k, l)], v[("wprod", k, l)]
            p.le({w: 1.0, wimp: -1.0, wprod: -1.0})
            _add(cost, wimp, 2.0 * S)
            _add(wform, w, S)
            if has(k - 1, l):
                k0 = k - 1
                p.le({wprod: 1.0, v[("pc", k0, l)]: -1.0, v[("pi", k0, l)]: -1.0})
                p.le({wprod: 1.0, v[("w", k0, l)]: -1.0})
            else:
                p.le({wprod: 1.0})
        # --- cost and credit -----------------------------------------------------------------------------------
        _add(cost, nI, 2.0 * d)
        _add(cost, mI, 2.0 * d)
        _add(cost, bf, 1.0)
        _add(cost, bb, 1.0)
        _add(cost, pi, 2.0 * S)
        for nm, cls in (("mf", "fwd"), ("md", "dgrad"), ("mw", "wgrad")):
            if cell.macs[cls] > 0:                     # MAC-equivalent work per MAC (accumulator init / round)
                _add(work_all, v[(nm, k, l)], cell.work[cls] / cell.macs[cls])
        for cls, nm in (("fwd", "mf"), ("dgrad", "md"), ("wgrad", "mw")):
            if cell.macs[cls] > 0:                     # every MAC is priced (baseline groups may go negative)
                _add(groups.setdefault(group_of(k, l, cls), {}), v[(nm, k, l)], S)
    # --- (F) upstream work of a completing update gate, for every cell (the last step's gates exist too) --------
    cexpr: dict[tuple[int, int], dict[int, float]] = {}
    for (k0, l), cell in cells.items():
        z0 = v[("z", k0, l)]
        # (F): completing dW_{k0,l} puts the forced hop work of every non-exempt token of step k0 into
        # Up(dW): a token is exempt at a hop when it is I at some block between the hop and l (fwd
        # classes below l, bwd classes above l) or supplies its operand elements by cheap imports.  Every
        # exemption is over-counted and every cheap byte's saving is credited (relaxation).
        c: dict[int, float] = {}

        def wr(kk: int, ll: int, cls: str) -> float:    # work per forced MAC (its output's chain overhead)
            return cells[(kk, ll)].wr[cls] if (kk, ll) in cells else 1.0

        # tokens exempt by cheap operand imports: a token that imports rather than produces its operands of the
        # pc completed elements needs >= 2 pc / dmax bytes per side (operand columns), i.e. at most
        # bf dmax / (2 pc) such tokens -- bounded per dyadic level of pc (pc >= 1 element: 2 bytes per side)
        ecf = p.var(f"ecf[{k0},{l}]", float(Q))
        ecb = p.var(f"ecb[{k0},{l}]", float(Q))
        bbs = {v[("bb", k0, l)]: 1.0}
        if has(k0, l + 1):
            bbs[v[("bb", k0, l + 1)]] = 1.0
        p.le({ecf: 1.0, v[("bf", k0, l)]: -0.5})
        p.le(_sub({ecb: 1.0}, {kk: 0.5 * vv for kk, vv in bbs.items()}))
        for y_, lo_ in levels_pc.get((k0, l), []):
            if lo_ > blocks[l].dmax > 0:
                rate = blocks[l].dmax / (2.0 * lo_)
                p.le({ecf: 1.0, v[("bf", k0, l)]: -rate, y_: float(Q)}, float(Q))
                p.le(_sub({ecb: 1.0, y_: float(Q)}, {kk: rate * vv for kk, vv in bbs.items()}), float(Q))
        cw: dict[int, float] = {ecf: 1.0, ecb: 1.0}
        if has(k0, l + 1):
            _add(cw, v[("mI", k0, l + 1)], 1.0)
        # the block's own operands: tokens not I / cheap-covered at block l produced their x', s rows (fwd) and,
        # not I in the bwd classes, their dS / dx' / do rows (bwd) -- all upstream of dW_{k0,l}
        if l < L and blocks[l].c_self_f > 0:
            exs = {v[("nI", k0, l)]: 1.0, ecf: 1.0}
            ys = p.var(f"ysf[{k0},{l}]")
            p.le(_sub({ys: -1.0, z0: Q}, exs))
            _add(c, ys, blocks[l].c_self_f / S * wr(k0, l, "fwd"))
            _add(c, v[("bf", k0, l)], -sf[l] * wr(k0, l, "fwd"))
        if l < L and blocks[l].c_self_b > 0:
            exs = dict(cw)
            _add(exs, v[("mI", k0, l)], 1.0)
            ys = p.var(f"ysb[{k0},{l}]")
            p.le(_sub({ys: -1.0, z0: Q}, exs))
            _add(c, ys, blocks[l].c_self_b / S * wr(k0, l, "dgrad"))
            _add(c, v[("bb", k0, l)], -sb[l] * wr(k0, l, "dgrad"))
        ex = dict(cw)
        for j in range(l, 0, -1):                        # fwd hops below l: (j-1) -> j
            if not has(k0, j):
                break
            _add(ex, v[("nI", k0, j)], 1.0)
            if not has(k0, j - 1):
                break
            _add(ex, v[("nI", k0, j - 1)], 1.0)
            if blocks[j - 1].hop_f:
                y = p.var(f"yf[{k0},{l},{j - 1}]")
                p.le(_sub({y: -1.0, z0: Q}, ex))
                _add(c, y, cf[j - 1] * wr(k0, j - 1, "fwd"))
                _add(c, v[("bf", k0, j - 1)], -sf[j - 1] * wr(k0, j - 1, "fwd"))
        ex = dict(cw)
        exh: dict[int, float] | None = None
        for j in range(l, L):                            # bwd hops above l: (j+1) -> j
            if not has(k0, j):
                break
            _add(ex, v[("mI", k0, j)], 1.0)
            if not has(k0, j + 1):
                break
            _add(ex, v[("mI", k0, j + 1)], 1.0)
            if blocks[j + 1].hop_b:
                y = p.var(f"yb[{k0},{l},{j + 1}]")
                p.le(_sub({y: -1.0, z0: Q}, ex))
                _add(c, y, cb[j + 1] * wr(k0, j + 1, "dgrad"))
                _add(c, v[("bb", k0, j + 1)], -sb[j + 1] * wr(k0, j + 1, "dgrad"))
                if j + 1 == L:
                    exh = dict(ex)
        if exh is not None and head_ok:
            # tokens reaching the head without importing its bwd values produce their logit row: head fwd
            # plus their fwd chain from l up to the head
            _add(exh, v[("nI", k0, L)], 1.0)
            y = p.var(f"yh[{k0},{l}]")
            p.le(_sub({y: -1.0, z0: Q}, exh))
            _add(c, y, Ps[L] * wr(k0, L, "fwd"))
            _add(c, v[("bf", k0, L)], -0.5 * d / S * wr(k0, L, "fwd"))
            # ... and, not importing the head's bwd values, their dxn_L row: the head dgrad (P_L MACs;
            # an imported head bwd element saves at most V of them)
            _add(c, y, Ps[L] * wr(k0, L, "dgrad"))
            _add(c, v[("bb", k0, L)], -0.5 * blocks[L].s_b / S * wr(k0, L, "dgrad"))
            for jj in range(L, l, -1):                   # hops (jj-1) -> jj for jj in (l, L]
                if not has(k0, jj - 1):
                    break
                _add(exh, v[("nI", k0, jj - 1)], 1.0)
                if blocks[jj - 1].hop_f:
                    y2 = p.var(f"yfh[{k0},{l},{jj - 1}]")
                    p.le(_sub({y2: -1.0, z0: Q}, exh))
                    _add(c, y2, cf[jj - 1] * wr(k0, jj - 1, "fwd"))
                    _add(c, v[("bf", k0, jj - 1)], -sf[jj - 1] * wr(k0, jj - 1, "fwd"))
        _add(c, v[("pc", k0, l)], float(Q) * wr(k0, l, "wgrad"))   # the completing wgrad MACs themselves
        cexpr[(k0, l)] = c
    # The update gate (k0, l) reads W_{k0,l}; when R produced those elements (wprod_{k0,l} > 0) the gate
    # (k0-1, l) is in R and its whole in-RU upstream is upstream of gate (k0, l) as well -- chained along the
    # layer: t[k0,l] >= (forced work of (k0-1, l)) + t[k0-1,l] when wprod_{k0,l} > 0 (binary g), and
    # z_{k0,l} = 1  =>  forced work of (k0, l) + t[k0,l] <= F.
    M_T = K * M_F
    v_t: dict[tuple[int, int], int] = {}
    for (k0, l), c in sorted(cexpr.items()):
        t: dict[int, float] = {}
        if k0 >= 1 and (k0 - 1, l) in cexpr:
            wprod = v[("wprod", k0, l)]
            g_ = p.var(f"g[{k0},{l}]", 1.0, integer=True)
            p.le({wprod: 1.0, g_: -Ps[l]})
            tv = p.var(f"t[{k0},{l}]", M_T)
            prev = dict(cexpr[(k0 - 1, l)])
            if (k0 - 1, l) in v_t:
                _add(prev, v_t[(k0 - 1, l)], 1.0)
            _add(prev, tv, -1.0)
            _add(prev, g_, M_T)
            p.le(prev, M_T)                              # t >= prev + t_prev - M (1 - g)
            v_t[(k0, l)] = tv
            t = {tv: 1.0}
        full = dict(c)
        for kk, vv in t.items():
            _add(full, kk, vv)
        _add(full, v[("z", k0, l)], M_T)
        p.le(full, Fs + M_T)

    p.le(work_all, Gs)
    # token-count slabs (see _Shapes.levels): every credited-cell token count <= hi_j, and each bilinear piece
    # m <= hi_j w (a weight element present serves at most hi_j tokens in this slab).  Dyadic from Q down.
    # Slab j = shapes whose largest credited-cell token count lies in [lo_j, hi_j] (dyadic from Q): anchor
    # binaries s (one per token count, sum >= 1, n >= lo_j s) exclude the smaller shapes, so the loose slab
    # does not dominate the minimum.
    slabs: list[list[tuple[dict[int, float], float]]] = []
    n_slabs = _MC_ENUM if model.K == 1 or os.environ.get("LOWER_COARSE_MC_ENUM") else 0
    if n_slabs > 0 and mc_pieces and Q >= 4:
        tok_vars = sorted({n_ for _, _, n_, _ in mc_pieces})
        anchors = {n_: p.var(f"s[{p.names[n_]}]", 1.0, integer=True) for n_ in tok_vars}
        hi_ = float(Q)
        for _j in range(n_slabs + 1):
            lo_ = hi_ / _MC_RATIO if (_j < n_slabs and hi_ / _MC_RATIO >= 1.0) else 0.0
            rows: list[tuple[dict[int, float], float]] = []
            if hi_ < Q:
                for n_ in tok_vars:
                    rows.append(({n_: 1.0}, hi_))
                for mm, ww, n_, uses in mc_pieces:
                    if hi_ < uses:
                        rows.append(({mm: 1.0, ww: -hi_}, 0.0))
            if lo_ > 0.0:
                rows.append(({s_: -1.0 for s_ in anchors.values()}, -1.0))
                for n_, s_ in anchors.items():
                    rows.append(({s_: lo_, n_: -1.0}, 0.0))
            slabs.append(rows)
            if lo_ <= 0.0:
                break
            hi_ = lo_
    return _Shapes(p, cost, 0.0, groups, wform, {"v": v}, levels=slabs)


def _solve_poly(sh: _Shapes, c: np.ndarray) -> tuple[float, np.ndarray | None, float]:
    """``min c.x`` over the shape polytope (MILP when there are binaries).  Returns ``(primal value, x, proven
    lower bound)``: under the time limit (``LOWER_COARSE_MILP_S``) the incumbent ``x`` (or ``None``) and the
    solver's dual bound -- every certification below uses the bound, never the incumbent.  With token levels
    (``sh.levels``) the minimum is taken over the slabs (their union is the whole shape space)."""
    best: tuple[float, np.ndarray | None, float] | None = None
    mats = sh.level_matrices()
    for A, b in mats:
        try:
            fun, x, lbnd = _solve_milp(sh, A, b, c)
        except RuntimeError:
            if len(mats) == 1:
                raise
            fun, x, lbnd = math.inf, None, math.inf          # an empty slab
        if best is None:
            best = (fun, x, lbnd)
        else:
            best = (min(best[0], fun), x if fun < best[0] else best[1], min(best[2], lbnd))
    assert best is not None
    return best


def _solve_milp(sh: _Shapes, A, b, c: np.ndarray) -> tuple[float, np.ndarray | None, float]:
    n = sh.poly.n
    integrality = np.zeros(n)
    integrality[sh.poly.integer] = 1
    ub = np.array(sh.poly.ub, dtype=float)
    opts: dict[str, Any] = {"disp": False, "mip_rel_gap": 1e-7, "time_limit": _MILP_TIME}
    if _MILP_THREADS > 1:                              # passed to HiGHS verbatim (scipy warns once)
        opts["threads"] = _MILP_THREADS
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        res = milp(c, constraints=LinearConstraint(A, -np.inf, b), integrality=integrality,
                   bounds=Bounds(np.zeros(n), ub), options=opts)
        if res.status not in (0, 1, 2):                # HiGHS solve error (numerical): once more without presolve
            _dbg(f"shape MILP solver error ({res.message}); retrying without presolve")
            res = milp(c, constraints=LinearConstraint(A, -np.inf, b), integrality=integrality,
                       bounds=Bounds(np.zeros(n), ub), options=dict(opts, presolve=False))
    if res.status == 2:
        raise RuntimeError(f"shape MILP infeasible: {res.message}")
    x = res.x
    fun = float(c @ x) if x is not None else math.inf
    if res.status == 0 and x is not None:
        return fun, x, fun
    lbnd = getattr(res, "mip_dual_bound", None)
    if lbnd is None or not np.isfinite(lbnd):
        lbnd = -math.inf
    if x is None and res.status != 1:
        _dbg(f"shape MILP failed ({res.message}); treated as an unclosed separation")
        return math.inf, None, -math.inf
    _dbg(f"shape MILP hit the time limit: incumbent {fun:.4e} bound {lbnd:.4e}")
    return fun, x, float(lbnd)


def _min_over_poly(sh: _Shapes, prices: dict[str, float], mu: float = 0.0) -> tuple[float, np.ndarray | None, float]:
    """``min I(x) - sum_c lambda_c M_c(x) - mu W(x)`` over the polytope: ``(value, minimiser, proven bound)``."""
    c = np.zeros(sh.poly.n)
    for i, val in sh.cost.items():
        c[i] += val
    for grp, form in sh.groups.items():
        lam = prices.get(grp, 0.0)
        for i, val in form.items():
            c[i] -= lam * val
    if mu:
        for i, val in sh.weights_form.items():
            c[i] -= mu * val
    val, x, lbnd = _solve_poly(sh, c)
    return val + sh.const, x, lbnd + sh.const


def _eval(sh: _Shapes, x: np.ndarray) -> tuple[float, dict[str, float], float]:
    I = float(sum(x[i] * c for i, c in sh.cost.items())) + sh.const
    M = {grp: float(sum(x[i] * c for i, c in form.items())) for grp, form in sh.groups.items()}
    W = float(sum(x[i] * c for i, c in sh.weights_form.items()))
    return I, M, W


def _ratio(sh: _Shapes, denom: dict[int, float], iters: int = 40) -> tuple[float, np.ndarray]:
    """``min I(x) / D(x)`` over the (mixed-integer) polytope by Dinkelbach iteration: solve
    ``min I - lam D``; if the value is ``>= 0`` then ``lam`` is the ratio's minimum (certified), else update
    ``lam = I(x*) / D(x*)``.  Returns ``(lam, minimiser)``."""
    base = np.zeros(sh.poly.n)
    for i, val in sh.cost.items():
        base[i] += val
    dvec = np.zeros(sh.poly.n)
    for i, val in denom.items():
        dvec[i] += val
    # start from the shape maximising D (any point with D > 0)
    _, x, _ = _solve_poly(sh, -dvec)
    if x is None:
        return 0.0, None
    D = float(dvec @ x)
    if D <= 1e-12:
        return math.inf, x
    lam = (float(base @ x) + sh.const) / D
    best_x = x
    for _ in range(iters):
        val, x, lbnd = _solve_poly(sh, base - lam * dvec)
        if lbnd + sh.const >= -1e-9 * max(1.0, abs(lam) * D):
            return lam, best_x
        if x is None:
            break
        D = float(dvec @ x)
        if D <= 1e-12:
            return lam, best_x
        new = (float(base @ x) + sh.const) / D
        if new >= lam:
            return lam, best_x
        lam, best_x = new, x
    # not converged: certify the last lam by shrinking until the proven bound of min I - lam D is >= 0
    for _ in range(60):
        _, _, lbnd = _solve_poly(sh, base - lam * dvec)
        if lbnd + sh.const >= -1e-9 * max(1.0, abs(lam) * D):
            return lam, best_x
        lam *= 1.0 - 1e-4
    return 0.0, best_x


def default_group(model: CoarseModel):
    """Default price groups: credited cells by ``(step, class)``; the uncredited work of step ``k`` by
    ``(step, 'layer0' | 'head' | class)``."""
    def group_of(k: int, l: int, cls: str) -> str:
        if model.credited(k, l):
            return f"k{k}:{cls}"
        if l == 0:
            return f"k{k}:layer0"
        if l == model.L:
            return f"k{k}:head"
        return f"k{k}:{cls}"
    return group_of


def layer_group(model: CoarseModel, bands: bool = True):
    """Fine price groups: credited cells by ``(step, class, depth band)`` -- a deep layer cannot be reached by
    a cheap restart from the free block-0 rows (the restart tile's weight cost grows linearly with depth), so
    it may carry a higher price than a shallow one.  Bands are dyadic in the depth (``{1}, {2,3}, {4..7},
    ...``; ``bands=False`` gives one group per layer); the uncredited work keeps the :func:`default_group`
    names."""
    base = default_group(model)

    def group_of(k: int, l: int, cls: str) -> str:
        if model.credited(k, l):
            if l == model.L:
                return f"k{k}:{cls}:head"
            b = int(math.floor(math.log2(max(l, 1)))) if bands else l
            return f"k{k}:{cls}:b{b}"
        return base(k, l, cls)
    return group_of


def price_lp(model: CoarseModel, F: float, G: float, group_of=None, max_iter: int = 300, *,
             init: tuple[dict[str, float], float] | None = None, init_shapes: list[np.ndarray] | None = None,
             time_budget: float | None = None) -> dict[str, Any]:
    """Certified prices by cutting planes on the exact-partition dual.

    Every MAC of every cell is priced (``lambda_c`` per group ``c``, *signed*: since each MAC is performed in
    exactly one RU, ``sum_R sum_c lambda_c M_c(R) = sum_c lambda_c |M_c|`` for any sign, so baseline work --
    step 0, layer 0, the head -- may carry a negative price that pays for an RU absorbing a whole step and then
    executing credited MACs for free) together with the weight-floor price ``mu >= 0`` on the weights present
    (``sum_R W(R) >= sum P``).  Master: ``max sum_c lambda_c |M_c| + mu sum P`` s.t.
    ``sum_c lambda_c M_c(x^j) + mu W(x^j) <= I(x^j)`` over the accumulated cuts; separation: the shape MILP
    ``min I - sum lambda M - mu W``.  The returned vector is certified (separation value ``>= -tol``), else
    shrunk towards zero until it is.  Also reports the uniform credited ratio ``lambda_uniform`` (a positive
    price on credited MACs only, zero elsewhere) with its minimising shape -- the cheapest attack.

    ``init`` is a price vector (in this call's group names) already proven feasible -- it becomes the initial
    stability centre (the result is then never worse than it); ``init_shapes`` are shapes of the same polytope
    (earlier cuts), re-evaluated under this call's groups; ``time_budget`` stops the cutting planes (seconds,
    wall clock) and returns the certified centre."""
    t_start = time.monotonic()
    if group_of is None:
        group_of = default_group(model)
    sh = _build(model, F, G, group_of)
    groups = sorted(sh.groups)
    totals = {grp: 0.0 for grp in groups}
    credited_groups: set[str] = set()
    for (k, l), cell in model.cells.items():
        for cls in ("fwd", "dgrad", "wgrad"):
            if cell.macs[cls] > 0:
                totals[group_of(k, l, cls)] += cell.macs[cls]
                if model.credited(k, l):
                    credited_groups.add(group_of(k, l, cls))
    k_lo = 0 if model.charge_roots else 1
    P_tot = sum(model.blocks[l].P for k in range(k_lo, model.K) for l in range(model.L + 1) if (k, l) in model.cells)
    out: dict[str, Any] = {"groups": groups, "totals": totals, "credited_groups": sorted(credited_groups),
                           "P_total_k_ge_1": P_tot}

    # uniform credited ratio and its minimising shape (diagnostic)
    denom: dict[int, float] = {}
    for grp in credited_groups:
        for i, val in sh.groups[grp].items():
            _add(denom, i, val)
    lam_u, shape = (_ratio(sh, denom) if denom else (math.inf, None))
    out["lambda_uniform"] = lam_u if lam_u != math.inf else 0.0
    out["shape"] = _describe(model, sh, shape) if shape is not None else {}

    # signed per-group prices + weight floor by cutting planes
    # master variables are the group totals lam_c |M_c| and mu sum P (rows then have entries in [0, 1])
    n_g = len(groups)
    obj = -np.ones(n_g + 1)
    B = 64.0                                                # |lambda| <= B bytes per MAC, mu <= B bytes/element
    norm = np.array([max(totals[grp], 1.0) for grp in groups] + [max(float(P_tot), 1.0)])
    box = [(-B * norm[i], B * norm[i]) for i in range(n_g)] + [(0.0, B * norm[n_g])]
    cuts: list[tuple[dict[str, float], float, float]] = []
    seeds: list[np.ndarray] = []
    if shape is not None:
        seeds.append(shape)
    for grp in groups:                                     # shapes maximising each group's MACs (and the weights)
        c = np.zeros(sh.poly.n)
        for i, val in sh.groups[grp].items():
            c[i] -= val
        xs_ = _solve_poly(sh, c)[1]
        if xs_ is not None:
            seeds.append(xs_)
    if sh.weights_form:
        c = np.zeros(sh.poly.n)
        for i, val in sh.weights_form.items():
            c[i] -= val
        xs_ = _solve_poly(sh, c)[1]
        if xs_ is not None:
            seeds.append(xs_)
    xs: list[np.ndarray] = []
    for x in list(init_shapes or []) + seeds:
        Ix, Mx, Wx = _eval(sh, x)
        cuts.append((Mx, Wx, Ix))
        xs.append(x)
    # in-out stabilised Kelley: the master candidate is an upper bound on the certifiable total; the separation
    # is run at a point between the last certified vector (stability centre, starts at 0) and the candidate.
    def total(lam_, mu_):
        return sum(lam_[g_] * totals[g_] for g_ in groups) + mu_ * P_tot

    center = ({grp: 0.0 for grp in groups}, 0.0)
    if init is not None:
        center = ({grp: float(init[0].get(grp, 0.0)) for grp in groups}, float(init[1]))
    lb = total(*center)
    ub = math.inf
    alpha = 0.5
    misses = 0
    stalls = 0
    iters = 0
    cand = None
    mu_c = 0.0
    for iters in range(1, max_iter + 1):
        if time_budget is not None and time.monotonic() - t_start > time_budget:
            _dbg(f"price LP time budget exhausted at iteration {iters}; returning the certified centre")
            break
        A = np.array([[cut[0].get(grp, 0.0) for grp in groups] + [cut[1]] for cut in cuts]) / norm
        b = np.array([cut[2] for cut in cuts])
        res = linprog(obj, A_ub=A, b_ub=b, bounds=box, method="highs")
        if res.status != 0:                                # numerical trouble: retry without presolve
            res = linprog(obj, A_ub=A, b_ub=b, bounds=box, method="highs", options={"presolve": False})
        if res.status != 0:
            _dbg(f"master LP failed at iteration {iters}: {res.message}")
            break
        cand = {grp: float(res.x[i]) / norm[i] for i, grp in enumerate(groups)}
        mu_c = float(res.x[n_g]) / norm[n_g]
        ub = min(ub, -float(res.fun))
        if ub - lb <= _TOL * max(1.0, ub):
            break
        sep = ({grp: center[0][grp] + alpha * (cand[grp] - center[0][grp]) for grp in groups},
               center[1] + alpha * (mu_c - center[1]))
        val, x, lbv = _min_over_poly(sh, sep[0], sep[1])
        _dbg(f"iter {iters}: ub {ub:.4e} lb {lb:.4e} alpha {alpha:.3f} separation {val:.4e} (bound {lbv:.4e}) "
             f"cuts {len(cuts)}")
        if lbv >= -_TOL * max(1.0, ub):
            center, lb = sep, total(*sep)
            misses = stalls = 0
            alpha = min(1.0, 2.0 * alpha)
        else:
            if x is not None and val < -_TOL * max(1.0, ub):
                Ix, Mx, Wx = _eval(sh, x)
                cuts.append((Mx, Wx, Ix))
                xs.append(x)
                stalls = 0
            else:                                       # time limit: neither proven nor a violated shape
                stalls += 1
                if stalls >= 3:
                    _dbg("separation MILP cannot be closed at this point; returning the certified centre")
                    break
            misses += 1
            if misses >= 3:
                alpha, misses = max(0.05, 0.5 * alpha), 0
    lam, mu = center
    certified = True                                    # the centre is proven at every update (bound >= -tol)
    # a final Dinkelbach scaling of the last master candidate may beat the centre
    if ub > lb and iters and cand is not None:
        t = 1.0
        best = None
        for _ in range(12):
            cand_t = ({grp: t * cand[grp] for grp in groups}, t * mu_c)
            val, x, lbv = _min_over_poly(sh, cand_t[0], cand_t[1])
            if lbv >= -_TOL * max(1.0, ub):
                best = cand_t
                break
            if x is None or val >= -_TOL * max(1.0, ub):
                break                                   # unproven and no violated shape to scale by
            Ix, Mx, Wx = _eval(sh, x)
            D = sum(cand[g_] * Mx.get(g_, 0.0) for g_ in groups) + mu_c * Wx
            if D <= 0:
                break
            t = min(t * (1.0 - 1e-6), Ix / D)
        if best is not None and total(*best) > total(lam, mu):
            lam, mu = best
    # independent re-check of the returned vector: the separation MILP at (lam, mu) must have a proven bound
    # >= -tol (every legal shape pays at least its charge).  A failed proof zeroes the certificate; a time-out
    # keeps it (the centre and the scaled candidate were proven when adopted) but reports ``certified = False``.
    val, x_, lbv = _min_over_poly(sh, lam, mu)
    if lbv >= -_TOL * max(1.0, abs(total(lam, mu))):
        out["recheck"] = "passed"
    elif x_ is not None and val < -_TOL * max(1.0, abs(total(lam, mu))):
        _dbg(f"re-check found a violated shape ({val:.4e}); certificate dropped")
        lam, mu, certified = {grp: 0.0 for grp in groups}, 0.0, False
        out["recheck"] = "violated"
    else:
        certified = False
        out["recheck"] = "time limit (bound not closed)"
    out["upper_bound_bytes"] = ub
    cert_total = total(lam, mu)
    out["gap"] = (max(0.0, ub - cert_total) / ub) if (ub != math.inf and ub > 0) else (0.0 if ub == 0 else 1.0)
    # the attacks that limit the certificate: cuts binding at the returned price vector, ranked by tightness
    slack = []
    for j, (Mx, Wx, Ix) in enumerate(cuts):
        charge = sum(lam[g_] * Mx.get(g_, 0.0) for g_ in groups) + mu * Wx
        slack.append((Ix - charge, j))
    slack.sort()
    out["binding_shapes"] = [dict(_describe(model, sh, xs[j]), slack_bytes=sl) for sl, j in slack[:5]]
    out["lambda"] = lam
    out["mu"] = mu
    out["iterations"] = iters
    out["converged"] = certified
    out["lambda_bytes"] = sum(lam[grp] * totals[grp] for grp in groups)
    out["weight_floor_bytes"] = mu * P_tot
    out["certified_bytes"] = max(0.0, out["lambda_bytes"] + out["weight_floor_bytes"])
    out["uniform_bytes"] = out["lambda_uniform"] * sum(totals[g_] for g_ in credited_groups)
    out["_shapes_x"] = xs                               # for a warm-started refinement (stripped by the caller)
    out["_lambda_of"] = group_of
    return out


def _describe(model: CoarseModel, sh: _Shapes, x: np.ndarray) -> dict[str, Any]:
    """Human-readable minimising shape: non-zero variables per cell (MACs / elements unscaled)."""
    v = sh.meta["v"]
    S = model.scale
    scaled = {"mf", "md", "mw", "pc", "pi", "w", "wimp", "wprod"}
    cells: dict[str, dict[str, float]] = {}
    for key, i in v.items():
        nm = key[0]
        val = float(x[i]) * (S if nm in scaled else 1.0)
        if abs(val) > 1e-6:
            cell = f"({key[1]},{key[2]})" if len(key) == 3 else f"step {key[1]}"
            cells.setdefault(cell, {})[nm] = val
    I, M, W = _eval(sh, x)
    work = sum(float(x[v[key]]) * S for key in v if key[0] in ("mf", "md", "mw"))
    tot = sum(M.values())
    return {"input_bytes": I, "target_macs": M, "work": work, "weights_present": W,
            "bytes_per_mac": I / tot if tot else math.inf, "cells": cells, "table_case": "B" if sh.const else "A"}


# ---------------------------------------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------------------------------------

def lower_coarse(g: OpGraph, F: int | None, G: int | None, *, program: Any = None, group_of=None,
                 credit_layer0: bool = False) -> LowerBound:
    """Coarse ``(F, G)`` certificate (module docstring).

    ``L = token bytes + root bytes + cap`` where *root bytes* are the non-fixed (accumulated / carried) root
    tensors read by some op -- produced outside every RU, hence imported at least once (a charge class disjoint
    from the produced values the LP prices) -- and ``cap = sum_c lambda_c |M_c| + mu sum P`` is the LP
    certificate over produced values (weights of steps ``k >= 1``, partial gradients, activation / gradient
    rows).  For a single-step circuit whose weights are dynamic roots (``forward-nonfixed``) the roots are
    priced inside the LP instead (``charge_roots``: every weight element present in an RU is imported at 2 B and
    the step-0 products are credited); then ``L = token bytes + max(root bytes, cap)``.

    ``F`` / ``G`` may be ``None`` (unbounded).  ``worst_ru`` holds the model geometry, the prices, the cuts
    binding at the certified price vector (the attacks that limit the certificate) and the uniform-ratio
    minimising shape.  ``program`` is accepted for API symmetry and unused."""
    total_work = float(sum(o.work for o in g.ops))
    F = total_work if F is None else F
    G = total_work if G is None else G
    if F <= 0 or G <= 0:
        raise ValueError("F and G must be positive")
    model = analyse(g, credit_layer0=credit_layer0)
    notes = list(model.notes)
    lam_bytes = mu_bytes = 0.0
    prices: dict[str, Any] = {}
    if model.target_macs > 0:
        prices = price_lp(model, float(F), float(G), group_of=group_of)
        n_credited_layers = len({l for (k, l) in model.cells if model.credited(k, l)})
        if group_of is None and _REFINE_S > 0 and n_credited_layers >= 3 and prices.get("recheck") == "passed":
            # refinement: per-layer prices warm-started from the certified (step, class) vector -- never worse
            coarse_of = prices["_lambda_of"]
            fine_of = layer_group(model)
            lam0 = prices["lambda"]
            init = ({fine_of(k, l, cls): lam0.get(coarse_of(k, l, cls), 0.0)
                     for (k, l), cell in model.cells.items() for cls in ("fwd", "dgrad", "wgrad")
                     if cell.macs[cls] > 0}, prices["mu"])
            fine = price_lp(model, float(F), float(G), group_of=fine_of, init=init,
                            init_shapes=prices["_shapes_x"], time_budget=_REFINE_S)
            if fine.get("recheck") == "passed" and fine["certified_bytes"] > prices["certified_bytes"] * (1 + 1e-9):
                fine["coarse_certified_bytes"] = prices["certified_bytes"]
                fine["coarse_lambda"] = lam0
                prices = fine
            else:
                prices["refine_certified_bytes"] = fine.get("certified_bytes")
        prices.pop("_shapes_x", None)
        prices.pop("_lambda_of", None)
        lam_bytes = prices["lambda_bytes"]
        mu_bytes = prices["weight_floor_bytes"]
    cap = int(max(0.0, lam_bytes + mu_bytes))
    if model.charge_roots:
        # the LP prices the block weights; the other read dynamic roots (embedding table, norm gains) are a
        # disjoint charge class and add to it
        floor_used = max(model.root_bytes, cap + model.extra_root_bytes)
        notes.append("dynamic step-0 weights priced inside the LP; L = tokens + max(root bytes, LP certificate + "
                     f"unpriced dynamic roots {model.extra_root_bytes} B)")
    else:
        floor_used = model.root_bytes + cap
    total = model.token_bytes + floor_used
    per_op = {o.id: 0 for o in g.ops}
    by_class = {"tokens": model.token_bytes, "roots": model.root_bytes, "block_prices": lam_bytes,
                "weight_floor": mu_bytes, "root_lp_mode": model.charge_roots}
    # metadata: the price LP's master bound is an upper bound on what these cuts could certify; the gap is
    # what L could still gain from closing it (0 when the root floor dominates or the LP closed)
    cap_ub = float(prices.get("upper_bound_bytes", cap)) if prices else float(cap)
    if not math.isfinite(cap_ub):
        cap_ub = float(cap)
    if model.charge_roots and cap_ub + model.extra_root_bytes <= model.root_bytes:
        gap = 0.0
    else:
        gap = max(0.0, cap_ub - cap) / total if total else 0.0
    certified = bool(prices.get("converged", True)) if prices else True
    if prices and prices.get("recheck") not in (None, "passed"):
        certified = False
    root_read = model.root_bytes                      # every dynamic root element is read at least once
    recurring = max(0, total - root_read - model.token_bytes)
    shape = (prices or {}).get("shape") or {}
    detail: dict[str, Any] = {
        "K": model.K, "L": model.L, "Q": model.Q, "d": model.d, "V": model.V,
        "P_blocks": [bl.P for bl in model.blocks], "P_act_blocks": [_p_act(bl) for bl in model.blocks],
        "verified_f": sum(1 for bl in model.blocks if bl.verified_f),
        "verified_b": sum(1 for bl in model.blocks if bl.verified_b),
        "c_hop_f": [bl.c_hop_f for bl in model.blocks], "c_hop_b": [bl.c_hop_b for bl in model.blocks],
        "charge_roots": model.charge_roots, "credited_macs": model.target_macs, "all_macs": model.all_macs,
        "lambda": {k_: float(v_) for k_, v_ in (prices.get("lambda") or {}).items()} if prices else {},
        "mu": float(prices.get("mu", 0.0)) if prices else 0.0,
        "lambda_uniform": float(prices.get("lambda_uniform", 0.0)) if prices else 0.0,
        "lp_upper_bound_bytes": cap_ub, "iterations": prices.get("iterations") if prices else 0,
        "recheck": prices.get("recheck") if prices else None,
        "cheapest_shape": {"input_bytes": shape.get("input_bytes"), "work": shape.get("work"),
                           "weights_present": shape.get("weights_present"), "bytes_per_mac": shape.get("bytes_per_mac"),
                           "tokens_per_cell": {c_: v_.get("nW") for c_, v_ in (shape.get("cells") or {}).items()
                                               if v_.get("nW")}},
        "milp_time_s": _MILP_TIME,
    }
    if model.moe:
        detail["moe"] = [{"l": bl.l, "E": bl.E, "topk": bl.topk, "T_e": bl.T_e, "P_dense": bl.P_dense, "P_exp": bl.P_exp,
                          "P_act": _p_act(bl)} for bl in model.blocks if bl.E > 1]
    lb = LowerBound(total=total, source=model.token_bytes, cap=cap, per_op=per_op, alpha_eff={}, kappa={}, gen={},
                    welt_bytes={}, wfree_bytes={}, share={}, theta={}, pool={}, op_params={}, notes=notes,
                    worst_ru={"model": {"K": model.K, "L": model.L, "Q": model.Q, "d": model.d, "V": model.V,
                                        "P": [bl.P for bl in model.blocks],
                                        "c_hop_f": [bl.c_hop_f for bl in model.blocks],
                                        "c_hop_b": [bl.c_hop_b for bl in model.blocks],
                                        "verified": [(bl.verified_f, bl.verified_b) for bl in model.blocks],
                                        "block_notes": [bl.notes for bl in model.blocks],
                                        "dyn_roots": model.dyn_roots, "moe": detail.get("moe")},
                              "by_class": by_class, "prices": prices, "block_bytes": lam_bytes,
                              "weight_floor_bytes": mu_bytes, "root_bytes": model.root_bytes},
                    token_seed=model.token_bytes, state_floor=model.root_bytes, target_macs=model.target_macs,
                    kappa_L=(model.target_macs / total if total else 0.0), F=int(F), X=0, G=int(G),
                    gap=float(gap), root_read=int(root_read), recurring=int(recurring), certified=certified,
                    detail=detail)
    return lb
