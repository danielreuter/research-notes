"""Torture suite: micro Verity programs with hand-derived ``I*`` (SPEC §1 semantics, bytes).

Conventions used in every derivation below: ``V16`` = 2 B, ``V32`` (token ids, lr, seeds) = 4 B, a MatmulT
accumulator crossing an RU boundary = 4 B; ``fixed`` leaves are free; an RU's input is the *set* of
distinct charged values it reads; ``Up_R(gate)`` = the gate plus everything reachable backwards from it
inside its RU; ``MatmulT{M,N,K,CH=1}`` has per output ``Zero32`` (work 0), ``K x Mac1`` (work 1 each) and
``Round16`` (work 1), so ``Up(Round16) = K + 1`` when the whole chain sits in one RU.

Each :class:`Case` carries a circuit, an ``(F, X)`` / ``(F, X, G)`` grid (``G`` = per-RU total-work cap,
omitted or ``None`` = unbounded) and, per grid point, a hand value with a kind: ``"eq"`` (``I* == v``), ``"ge"``
(``I* >= v``: only a lower estimate was derived), ``"le"`` (``I* <= v``: an explicit legal partition of that
cost is exhibited), ``"inf"`` (no legal partition).  Every case additionally gets automatic binding-``G``
points (:func:`g_points`: ``G = ceil(frac * work)`` at its loosest ``(F, X)``).  :func:`run_torture` evaluates
every point with :mod:`accumulation.redteam.harness` and compares.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from accumulation.redteam.circuits import Circuit, Op, Param, build
from accumulation.redteam.harness import Record, evaluate, monotonicity_violations

BIG_F = 1 << 30
BIG_X = 1 << 20

Hand = tuple[str, Optional[int]]        # kind, value


Point = tuple[int, int, Optional[int]]  # (F, X, G); G = None -> unbounded


def _pt(p: tuple) -> Point:
    """Normalise a grid key ``(F, X)`` or ``(F, X, G)`` to ``(F, X, G)``."""
    F, X = int(p[0]), int(p[1])
    G = p[2] if len(p) > 2 else None
    return (F, X, None if G is None else int(G))


@dataclass
class Case:
    name: str
    family: str
    circuit: Circuit
    grid: list[tuple]                    # (F, X) or (F, X, G)
    hand: dict[tuple, Hand]
    doc: str
    time_limit: float = 20.0
    tags: tuple[str, ...] = ()
    expect_violation: tuple[str, ...] = ()   # defects already known to fire on v1 / upper.py (documented)
    #: extra ``G`` points added automatically at the largest ``(F, X)`` of the grid: ``G = ceil(frac * work)``
    #: (binding: strictly below the total work of the circuit).  ``()`` disables.
    g_fracs: tuple[float, ...] = (0.5, 0.25)

    def __post_init__(self):
        self.grid = [_pt(p) for p in self.grid]
        self.hand = {_pt(k): v for k, v in self.hand.items()}


CASES: list[Case] = []


def _case(fn: Callable[[], Case]) -> Callable[[], Case]:
    globals()[fn.__name__] = fn          # the factory reads its own __doc__
    CASES.append(fn())
    return fn


def _hand(pairs: dict) -> dict:
    return {k: (v if isinstance(v, tuple) else ("eq", v)) for k, v in pairs.items()}


# ---------------------------------------------------------------------------------------------------------
# a. independent generation
# ---------------------------------------------------------------------------------------------------------

@_case
def a1_independent_rows() -> Case:
    """``y = x . Wf^T``, ``x`` token ``3 x 2`` (12 B), ``Wf`` fixed ``2 x 2`` (free).  24 gates.

    Every output ``(m, n)`` is its own chain of 2 MACs + Round reading only ``x[m, :]`` and free weights, so
    ``Up(Round) = 3`` in any RU that keeps a chain whole.  Each token element must enter at least one RU:
    ``I* >= 12``; one RU per row (imports ``x[m, :]`` = 4 B) attains it.  Hence ``I* = 12`` for ``X >= 4``,
    ``F >= 3`` -- the recurring charged input beyond the token bytes is 0.

    ``F = 2``: ``Up(Round) = 3`` is illegal, so every chain must be cut between ``Mac`` and ``Round`` (or
    earlier); the cheapest cut is ``Round`` alone in another RU, importing the 4-byte accumulator:
    ``I* = 12 + 4 * 6 outputs = 36`` (per row: ``{Zero, Mac, Mac} x 2`` in one RU reading ``x[m, :]`` = 4 B,
    ``{Round x 2}`` in another reading 2 accumulators = 8 B).

    ``X = 3``: a single ``Mac`` reads one token element (2 B) and the second MAC of a chain also needs the
    4-byte accumulator unless its RU holds both elements (4 B): nothing fits -> infeasible."""
    c = Circuit(params=[Param("x", (3, 2), "token"), Param("Wf", (2, 2), "fixed")],
                ops=[Op("matmul", (("p", "x"), ("p", "Wf")))], name="a1_independent_rows")
    grid = [(BIG_F, BIG_X), (3, 4), (2, BIG_X), (BIG_F, 3)]
    return Case("a1_independent_rows", "a", c, grid,
                _hand({(BIG_F, BIG_X): 12, (3, 4): 12, (2, BIG_X): 36, (BIG_F, 3): ("inf", None)}), a1_independent_rows.__doc__)


@_case
def a2_fixed_chain_F_split() -> Case:
    """``y = (x . Wf1^T) . Wf2^T``, ``x`` token ``1 x 2`` (4 B), ``Wf1`` fixed ``2 x 2``, ``Wf2`` fixed ``1 x 2``.
    12 gates; work: mm1 = 2 outputs x 3 = 6, mm2 = 3.

    ``F >= 9``: one RU, ``I* = 4`` (token bytes only).
    ``F in [3, 8]``: ``Up(Round2)`` in a fused RU = 3 + 6 = 9 > F.  Cut between the matmuls: RU0 = mm1 (reads
    ``x``, 4 B), RU1 = mm2 (reads the two 16-bit intermediates, 4 B): 8.  Keeping one mm1 output with mm2
    (``Up = 6``) costs ``x`` twice (4 + 4 + 2 = 10); cutting mm2's own chain costs an accumulator (4 + 4 + 2
    = 10).  ``I* = 8``.
    ``F = 2``: every Round must be cut from its chain.  The naive layering mm1 -> ``{Zero, Mac, Mac} x 2``
    (reads ``x``: 4) + ``{Round, Round}`` (2 accumulators: 8); mm2 -> ``{Zero, Mac, Mac}`` (2 intermediates:
    4) + ``{Round}`` (4) costs 20, but interleaving two RUs does better: RU0 = mm1's two ``{Zero, Mac, Mac}``
    + mm2's ``{Mac_2, Round}`` (reads ``x`` 4, one intermediate 2, one accumulator 4 = 10), RU1 = mm1's two
    ``Round`` + mm2's ``{Zero, Mac_1}`` (reads 2 accumulators = 8; ``Up(Mac_1) = Zero + Round + Mac_1 = 2``).
    ``I* = 18`` (solver-verified; a corrected hand value)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("Wf1", (2, 2), "fixed"), Param("Wf2", (1, 2), "fixed")],
                ops=[Op("matmul", (("p", "x"), ("p", "Wf1"))), Op("matmul", (("o", 0), ("p", "Wf2")))],
                name="a2_fixed_chain_F_split")
    grid = [(BIG_F, BIG_X), (9, BIG_X), (6, BIG_X), (3, BIG_X), (2, BIG_X)]
    return Case("a2_fixed_chain_F_split", "a", c, grid,
                _hand({(BIG_F, BIG_X): 4, (9, BIG_X): 4, (6, BIG_X): 8, (3, BIG_X): 8, (2, BIG_X): 18}),
                a2_fixed_chain_F_split.__doc__)


# ---------------------------------------------------------------------------------------------------------
# b. single shared compact precursor / c. independent accumulated precursors
# ---------------------------------------------------------------------------------------------------------

@_case
def b1_compact_precursor_fanout() -> Case:
    """``z = (h . Wf^T) . Wf2^T``, ``h`` accumulated ``1 x 2`` (4 B), ``Wf`` fixed ``4 x 2``, ``Wf2`` fixed
    ``2 x 4``.  28 gates; work 4 x 3 + 2 x 5 = 22.

    Everything downstream of ``h`` is free, so the only charged value is ``h`` (4 B) and one RU holding it
    produces all 6 outputs: ``I* = 4`` whenever ``X >= 4`` and ``F >= Up(Round_z) = 5 + 4 x 3 = 17``.
    ``F = 16``: mm2's outputs cannot sit with all of mm1; put 3 mm1 outputs with mm2 (``Up = 5 + 9 = 14``)
    and the 4th alone: both RUs read ``h`` (4 + 4) and the second imports one intermediate (2): ``I* = 10``
    (moving 2 outputs instead gives 4 + 4 + 4 = 12; all of mm1 apart gives 4 + 8 = 12).
    ``X = 3``: ``h`` does not fit (4 B) and a single element + accumulator is 6 B -> infeasible."""
    c = Circuit(params=[Param("h", (1, 2), "accumulated"), Param("Wf", (4, 2), "fixed"), Param("Wf2", (2, 4), "fixed")],
                ops=[Op("matmul", (("p", "h"), ("p", "Wf"))), Op("matmul", (("o", 0), ("p", "Wf2")))],
                name="b1_compact_precursor_fanout")
    grid = [(BIG_F, BIG_X), (17, 4), (16, BIG_X), (BIG_F, 3)]
    return Case("b1_compact_precursor_fanout", "b", c, grid,
                _hand({(BIG_F, BIG_X): 4, (17, 4): 4, (16, BIG_X): 10, (BIG_F, 3): ("inf", None)}),
                b1_compact_precursor_fanout.__doc__)


@_case
def c1_independent_precursors() -> Case:
    """``y = mul(X, Y)`` element-wise, ``X`` token ``2 x 3`` (12 B), ``Y`` accumulated ``2 x 3`` (12 B).  6 gates.

    Each gate needs its own ``X`` and ``Y`` element (4 B), no sharing anywhere: ``I* = 24`` for ``X >= 4``
    (costs add), infeasible at ``X = 3``."""
    c = Circuit(params=[Param("X", (2, 3), "token"), Param("Y", (2, 3), "accumulated")],
                ops=[Op("mul", (("p", "X"), ("p", "Y")))], name="c1_independent_precursors")
    grid = [(BIG_F, BIG_X), (1, 4), (BIG_F, 3)]
    return Case("c1_independent_precursors", "c", c, grid,
                _hand({(BIG_F, BIG_X): 24, (1, 4): 24, (BIG_F, 3): ("inf", None)}), c1_independent_precursors.__doc__)


@_case
def c2_accumulated_rows_fixed_weights() -> Case:
    """``y = A . Wf^T``, ``A`` accumulated ``3 x 2`` (12 B), ``Wf`` fixed ``2 x 2``.  24 gates.

    Mirror of a1 with the activation charged: ``I* = 12`` for ``X >= 4, F >= 3`` (one RU per row)."""
    c = Circuit(params=[Param("A", (3, 2), "accumulated"), Param("Wf", (2, 2), "fixed")],
                ops=[Op("matmul", (("p", "A"), ("p", "Wf")))], name="c2_accumulated_rows_fixed_weights")
    grid = [(BIG_F, BIG_X), (3, 4)]
    return Case("c2_accumulated_rows_fixed_weights", "c", c, grid, _hand({(BIG_F, BIG_X): 12, (3, 4): 12}),
                c2_accumulated_rows_fixed_weights.__doc__)


# ---------------------------------------------------------------------------------------------------------
# d. two-layer dense mixing (cumulative closure)
# ---------------------------------------------------------------------------------------------------------

def _d_case(M: int, time_limit: float) -> Case:
    c = Circuit(params=[Param("x", (M, 3), "fixed"), Param("W1", (2, 3), "accumulated"), Param("W2", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("matmul", (("o", 0), ("p", "W2")))],
                name=f"d_two_layer_M{M}")
    hand = {(BIG_F, BIG_X): 20, (BIG_F, 12): 12 + 12 * M, (BIG_F, 8): 12 + 16 * M}
    return Case(c.name, "d", c, list(hand), _hand(hand), _d_doc, time_limit=time_limit)


_d_doc = """``y = (x . W1^T) . W2^T`` with ``x`` fixed ``M x 3`` (free), ``W1`` accumulated ``2 x 3`` (12 B),
``W2`` accumulated ``2 x 2`` (8 B).  ``18 M`` gates.

One row of ``y`` needs the whole intermediate row ``h[m, :]`` (2 elements), i.e. all of ``W1`` (12 B).
``X >= 20``: one RU, ``I* = 20``.
``X = 12``: ``W1`` fits alone, ``W1 + W2`` does not.  Stage 1: one RU holding ``W1`` makes all of ``h`` (12).
Stage 2: an RU holding ``W2`` (8) has room for one ``h`` row (4): ``M`` RUs x 12.  (Per ``W2`` row instead:
4 + 4M <= 12 only for ``M <= 2``, same total 24 for M = 2.)  Partial-sum strategies must hold a ``W1`` row
(6) + a ``W2`` column (4) + imported 4-byte partials and do not fit.  ``I* = 12 + 12 M``.
``X = 8``: ``W1`` does not fit; stage 1 per ``W1`` row (6 B each, all ``M`` rows of ``x`` are free): 12.
Stage 2 per output: ``h[m, :]`` (4) + ``W2[i, :]`` (4) = 8 -> ``2M x 8``; a ``W2`` row plus two ``h`` rows
(12) or ``h[m]`` plus ``W2`` (12) do not fit; splitting the contraction costs 4 + 8 = 12 per output.
``I* = 12 + 16 M``.
The certified ``L`` should grow with ``M`` at ``X = 8``; v1 gives ``L = L_source = 20`` for every ``M``."""


CASES.append(_d_case(1, 20.0))
CASES.append(_d_case(2, 60.0))
CASES.append(_d_case(3, 120.0))


# ---------------------------------------------------------------------------------------------------------
# e. shared weights across branches
# ---------------------------------------------------------------------------------------------------------

@_case
def e1_shared_weights_fixed_acts() -> Case:
    """``y_i = A_i . W^T`` for three fixed ``1 x 2`` activations sharing accumulated ``W`` ``2 x 2`` (8 B).  24 gates.

    ``W`` must enter some RU; an RU holding one ``W`` row (4 B) can run every branch's MACs on that row, so
    ``W`` is loaded exactly once for any ``X >= 4``: ``I* = 8`` (not 24 = once per branch, and not per
    element).  ``X = 3``: infeasible (element + accumulator = 6)."""
    c = Circuit(params=[Param("A1", (1, 2), "fixed"), Param("A2", (1, 2), "fixed"), Param("A3", (1, 2), "fixed"),
                        Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", f"A{i}"), ("p", "W"))) for i in (1, 2, 3)], name="e1_shared_weights_fixed_acts")
    grid = [(BIG_F, BIG_X), (3, 8), (3, 4), (BIG_F, 3)]
    return Case("e1_shared_weights_fixed_acts", "e", c, grid,
                _hand({(BIG_F, BIG_X): 8, (3, 8): 8, (3, 4): 8, (BIG_F, 3): ("inf", None)}),
                e1_shared_weights_fixed_acts.__doc__)


@_case
def e2_shared_weights_token_acts() -> Case:
    """As e1 with token activations ``A_i`` (4 B each).  24 gates.

    ``X >= 20``: one RU, ``I* = 20``.
    ``X = 12``: ``W`` (8) + one ``A_i`` (4) per RU -> 3 x 12 = 36 (a ``W`` row + two activations, 12 B, needs
    two RUs per row: 2 x 2 x 12 = 48 is worse).  ``I* = 36``.
    ``X = 8``: an RU holds one ``W`` row + one ``A_i`` (8): 6 RUs x 8 = 48; splitting the contraction costs
    an accumulator per second half (4 + 8 = 12 per output).  ``I* = 48``."""
    c = Circuit(params=[Param("A1", (1, 2), "token"), Param("A2", (1, 2), "token"), Param("A3", (1, 2), "token"),
                        Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", f"A{i}"), ("p", "W"))) for i in (1, 2, 3)], name="e2_shared_weights_token_acts")
    grid = [(BIG_F, BIG_X), (BIG_F, 12), (BIG_F, 8)]
    return Case("e2_shared_weights_token_acts", "e", c, grid, _hand({(BIG_F, BIG_X): 20, (BIG_F, 12): 36, (BIG_F, 8): 48}),
                e2_shared_weights_token_acts.__doc__)


# ---------------------------------------------------------------------------------------------------------
# f. LoRA-style compact low-rank state
# ---------------------------------------------------------------------------------------------------------

@_case
def f1_lora_fixed_x() -> Case:
    """``y = add(x . Wf^T, (x . A^T) . B^T)``: ``x`` fixed ``2 x 2``, ``Wf`` fixed ``1 x 2``, ``A`` accumulated
    ``1 x 2`` (4 B), ``B`` accumulated ``1 x 1`` (2 B).  24 gates.  Adapter closure = 6 B.

    ``X >= 6``: one RU holds ``A`` and ``B`` and generates everything from free ``x``: ``I* = 6`` (no
    per-row charge).
    ``X in {4, 5}``: ``A + B`` do not fit.  ``A`` alone (4) makes ``low`` for both rows; each ``up[m]`` needs
    ``B`` (2) + ``low[m]`` (2) = 4 (``B`` + both ``low`` = 6 does not fit): 4 + 2 x 4 = 12.  Holding ``A``
    with ``B`` is impossible, so ``low`` crosses an RU boundary at least once per row: ``I* = 12``.
    ``X = 3``: ``A`` cannot be split (element 2 B + accumulator 4 B) -> infeasible.
    ``F`` (X large): fully fused, ``Up(add) = 1 + 3 (base chain) + 2 (up chain) + 3 (low chain) = 9``, so
    ``F >= 9`` gives ``I* = 6``.  ``F in [6, 8]``: the adapter RU (``low`` + ``up`` chains, ``Up(up) = 5``)
    reads ``A + B`` = 6 and the base + add RU imports the two ``up`` outputs (4): ``I* = 10``.  ``F in [4, 5]``:
    ``up`` cannot sit with ``low`` (5 > F) -- RU0 = base + ``low`` chains + adds (``Up(add) = 1 + 3 = 4``)
    reads ``A`` (4) + 2 ``up`` (4), RU1 = ``up`` chains reads ``B`` (2) + 2 ``low`` (4): ``I* = 14``.
    ``bounds/upper.py`` fuses the whole thing as a "tile" with ``up_max = 6`` at ``F = 6`` and claims
    ``U = 6 < I* = 10``: the materialised plan has ``Up(add) = 9 > 6`` (``Ulit_illegal``)."""
    c = Circuit(params=[Param("x", (2, 2), "fixed"), Param("Wf", (1, 2), "fixed"), Param("A", (1, 2), "accumulated"),
                        Param("Bm", (1, 1), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "Wf"))), Op("matmul", (("p", "x"), ("p", "A"))),
                     Op("matmul", (("o", 1), ("p", "Bm"))), Op("add", (("o", 0), ("o", 2)))], name="f1_lora_fixed_x")
    grid = [(BIG_F, BIG_X), (BIG_F, 6), (BIG_F, 5), (BIG_F, 4), (BIG_F, 3), (4, BIG_X), (6, BIG_X), (9, BIG_X)]
    hand = _hand({(BIG_F, BIG_X): 6, (BIG_F, 6): 6, (BIG_F, 5): 12, (BIG_F, 4): 12, (BIG_F, 3): ("inf", None),
                  (9, BIG_X): 6, (6, BIG_X): 10, (4, BIG_X): 14})
    return Case("f1_lora_fixed_x", "f", c, grid, hand, f1_lora_fixed_x.__doc__,
                expect_violation=("Ulit_illegal",))


@_case
def f2_lora_token_x() -> Case:
    """As f1 with ``x`` token (8 B).  ``X >= 14``: one RU, ``I* = 14``."""
    c = Circuit(params=[Param("x", (2, 2), "token"), Param("Wf", (1, 2), "fixed"), Param("A", (1, 2), "accumulated"),
                        Param("Bm", (1, 1), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "Wf"))), Op("matmul", (("p", "x"), ("p", "A"))),
                     Op("matmul", (("o", 1), ("p", "Bm"))), Op("add", (("o", 0), ("o", 2)))], name="f2_lora_token_x")
    grid = [(BIG_F, BIG_X), (BIG_F, 14), (BIG_F, 8)]
    return Case("f2_lora_token_x", "f", c, grid, _hand({(BIG_F, BIG_X): 14, (BIG_F, 14): 14}), f2_lora_token_x.__doc__)


# ---------------------------------------------------------------------------------------------------------
# g. residual / copy trees, embedding gather
# ---------------------------------------------------------------------------------------------------------

@_case
def g1_residual_add() -> Case:
    """``y = add(x, x . W^T)``, ``x`` carried ``1 x 2`` (4 B, two consumers), ``W`` accumulated ``2 x 2`` (8 B).
    10 gates.

    ``X >= 12``: one RU, ``I* = 12``.
    ``X = 8``: ``x + W`` do not fit; every RU running a MAC of output ``n`` holds ``W[n, :]`` (4) and both
    ``x`` elements (4) unless it splits the chain (element + accumulator = 6 leaves no room for ``W[n, k]``
    + ``x[k]`` = 4 in the second half: 10 > 8).  So ``x`` enters both output RUs: ``I* = 16``; the add
    gates ride along for free (``x[n]`` is already present).
    ``X = 7``: infeasible (both RU shapes above exceed 7)."""
    c = Circuit(params=[Param("x", (1, 2), "carried"), Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W"))), Op("add", (("p", "x"), ("o", 0)))], name="g1_residual_add")
    grid = [(BIG_F, BIG_X), (BIG_F, 12), (BIG_F, 8), (BIG_F, 7)]
    return Case("g1_residual_add", "g", c, grid,
                _hand({(BIG_F, BIG_X): 12, (BIG_F, 12): 12, (BIG_F, 8): 16, (BIG_F, 7): ("inf", None)}), g1_residual_add.__doc__)


@_case
def g2_embedding_gather() -> Case:
    """``e = embed(toks, tableT)``: ``toks`` token ``(3,)`` at 32 bit (12 B), ``tableT`` accumulated ``2 x 2``
    (D = 2 columns of V = 2 entries, 8 B).  6 gather gates, each reading one token id and one whole column.

    ``X >= 20``: one RU, ``I* = 20``.  Repeated token *values* are a runtime matter; the static gather
    reads the full column regardless, so there is no special case.
    ``X = 16``: the whole table (8) + two token ids (8) = 16 fits, so RU0 = the 4 gathers of tokens 0, 1 and
    RU1 = the 2 gathers of token 2 (table 8 + id 4 = 12): ``I* = 16 + 12 = 28`` (grouping by column instead --
    one column 4 + all ids 12 per RU -- gives 32).
    ``X = 8``: one gate per RU (column 4 + id 4): ``I* = 48``.  ``X = 7``: infeasible."""
    c = Circuit(params=[Param("toks", (3,), "token", width=32), Param("tableT", (2, 2), "accumulated")],
                ops=[Op("embed", (("p", "toks"), ("p", "tableT")))], name="g2_embedding_gather")
    grid = [(BIG_F, BIG_X), (BIG_F, 16), (BIG_F, 8), (BIG_F, 7)]
    return Case("g2_embedding_gather", "g", c, grid,
                _hand({(BIG_F, BIG_X): 20, (BIG_F, 16): 28, (BIG_F, 8): 48, (BIG_F, 7): ("inf", None)}), g2_embedding_gather.__doc__)


@_case
def g3_embedding_then_matmul() -> Case:
    """``y = embed(toks, tableT) . W^T`` with ``W`` accumulated ``2 x 2``: 30 gates.  ``X`` large: one RU,
    ``I* = 12 + 8 + 8 = 28``.  At ``X = 16`` only ``I* >= 28`` is claimed by hand."""
    c = Circuit(params=[Param("toks", (3,), "token", width=32), Param("tableT", (2, 2), "accumulated"),
                        Param("W", (2, 2), "accumulated")],
                ops=[Op("embed", (("p", "toks"), ("p", "tableT"))), Op("matmul", (("o", 0), ("p", "W")))],
                name="g3_embedding_then_matmul")
    grid = [(BIG_F, BIG_X), (BIG_F, 16)]
    return Case("g3_embedding_then_matmul", "g", c, grid, _hand({(BIG_F, BIG_X): 28, (BIG_F, 16): ("ge", 28)}),
                g3_embedding_then_matmul.__doc__, time_limit=60.0)


@_case
def g4_branching_intermediate() -> Case:
    """``h = x . W1^T`` (``x`` fixed ``1 x 2``, ``W1`` accumulated ``2 x 2``), ``y1 = h . W2^T``, ``y2 = h . W3^T``
    (``W2, W3`` accumulated ``1 x 2``): ``h`` has two consumers.  8 + 4 + 4 = 16 gates.

    ``X >= 16``: ``I* = 16``.  ``X = 8``: ``W1`` fits alone -> ``h``; each ``y_j`` needs ``h`` (4) + ``W_j``
    (4) = 8: ``I* = 8 + 8 + 8 = 24``.  Fusing ``y_j`` with ``W1`` (12) does not fit; per ``W1`` row (4) +
    ``W2[0, j]`` + ``W3[0, j]`` (4) = 8 gives partial sums of both ``y`` over ``j`` and the second half
    must import 2 partials (8) on top: no.  ``I* = 24``."""
    c = Circuit(params=[Param("x", (1, 2), "fixed"), Param("W1", (2, 2), "accumulated"), Param("W2", (1, 2), "accumulated"),
                        Param("W3", (1, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("matmul", (("o", 0), ("p", "W2"))),
                     Op("matmul", (("o", 0), ("p", "W3")))], name="g4_branching_intermediate")
    grid = [(BIG_F, BIG_X), (BIG_F, 8)]
    return Case("g4_branching_intermediate", "g", c, grid, _hand({(BIG_F, BIG_X): 16, (BIG_F, 8): 24}),
                g4_branching_intermediate.__doc__)


# ---------------------------------------------------------------------------------------------------------
# h. weight-gradient form and reductions over rows
# ---------------------------------------------------------------------------------------------------------

@_case
def h1_weight_gradient_tt() -> Case:
    """``dW = At^T . Bt`` (``AccMatmulTT``), ``At`` carried ``2 x 2`` (tokens x M, 8 B), ``Bt`` token ``2 x 2``
    (tokens x N, 8 B).  16 gates.

    ``X >= 16``: one RU, ``I* = 16``.  ``X = 8``: a tile of ``a`` ``At`` columns, ``b`` ``Bt`` columns and ``k``
    token rows imports ``2k(a + b)``; whole-K tiles need ``a = b = 1`` (8 B per output, 4 outputs: 32);
    ``k = 1`` tiles with ``a = b = 2`` cost 8 + 8 plus one accumulator per output (16): 32.  ``I* = 32``.
    ``X = 7``: infeasible.  In SPEC §2.2 the token operand ``Bt`` is a *non-free root* ``B`` (``beta =
    w_B/share``) and its bytes also sit in ``L_source_min``: both together would give ``L = 24 > 16``."""
    c = Circuit(params=[Param("At", (2, 2), "carried"), Param("Bt", (2, 2), "token")],
                ops=[Op("matmul_tt", (("p", "At"), ("p", "Bt")))], name="h1_weight_gradient_tt")
    grid = [(BIG_F, BIG_X), (BIG_F, 16), (BIG_F, 8), (BIG_F, 7)]
    return Case("h1_weight_gradient_tt", "h", c, grid,
                _hand({(BIG_F, BIG_X): 16, (BIG_F, 16): 16, (BIG_F, 8): 32, (BIG_F, 7): ("inf", None)}), h1_weight_gradient_tt.__doc__)


@_case
def h2_colsum() -> Case:
    """``g = colsum(X)``, ``X`` carried ``3 x 2`` (12 B): 2 columns x (Zero, 3 x (Widen, Add32), Round) = 16 gates.

    ``X >= 6``: one RU per column (6 B) or one RU: ``I* = 12``.  ``X = 5``: two elements (4 B) fit but the
    third needs the 4-byte running sum plus 2 B = 6: infeasible."""
    c = Circuit(params=[Param("X", (3, 2), "carried")], ops=[Op("colsum", (("p", "X"),))], name="h2_colsum")
    grid = [(BIG_F, BIG_X), (BIG_F, 6), (BIG_F, 5)]
    return Case("h2_colsum", "h", c, grid, _hand({(BIG_F, BIG_X): 12, (BIG_F, 6): 12, (BIG_F, 5): ("inf", None)}), h2_colsum.__doc__)


@_case
def h3_colsum_into_gain() -> Case:
    """``y = gain(Z, colsum(X))``: ``Z`` token ``2 x 2`` (8 B), ``X`` carried ``3 x 2`` (12 B).  20 gates.

    ``X`` large: ``I* = 20``.  ``X = 8``: a column of ``X`` (6) leaves room for one gain gate's ``Z`` element
    (2); the other gain gate of that column re-imports ``g[k]`` (2) + its ``Z`` element (2): per column
    8 + 4 = 12, ``I* = 24``."""
    c = Circuit(params=[Param("Z", (2, 2), "token"), Param("X", (3, 2), "carried")],
                ops=[Op("colsum", (("p", "X"),)), Op("gain", (("p", "Z"), ("o", 0)))], name="h3_colsum_into_gain")
    grid = [(BIG_F, BIG_X), (BIG_F, 8)]
    return Case("h3_colsum_into_gain", "h", c, grid, _hand({(BIG_F, BIG_X): 20, (BIG_F, 8): 24}), h3_colsum_into_gain.__doc__)


@_case
def h4_gram_matrix() -> Case:
    """``G = x . x^T`` with ``x`` carried ``2 x 2`` (8 B): ``A`` and ``B`` are the same tensor.  16 gates.
    ``X >= 8``: ``I* = 8``.  ``X = 6``: a diagonal output needs ``x[i, :]`` (4 B) for both operands and the
    off-diagonal ones need two rows (8 B) or a split chain (element pair 4 B + accumulator 4 B): infeasible."""
    c = Circuit(params=[Param("x", (2, 2), "carried")], ops=[Op("matmul", (("p", "x"), ("p", "x")))], name="h4_gram_matrix")
    grid = [(BIG_F, BIG_X), (BIG_F, 8), (BIG_F, 6)]
    return Case("h4_gram_matrix", "h", c, grid, _hand({(BIG_F, BIG_X): 8, (BIG_F, 8): 8, (BIG_F, 6): ("inf", None)}), h4_gram_matrix.__doc__)


# ---------------------------------------------------------------------------------------------------------
# t. defect-targeted instances (found by the red team; expected to fire on v1 / upper.py)
# ---------------------------------------------------------------------------------------------------------

@_case
def t1_same_row_read_twice() -> Case:
    """Two matmuls read the *same* row of ``W`` (accumulated ``2 x 2``, 8 B) through ``rows(W, 0, 1)``;
    ``A1, A2`` token ``1 x 2`` (4 B each).  8 gates.  Only row 0 of ``W`` (4 B) is ever read:
    ``I* = 4 + 4 + 4 = 12`` at large ``X``.  ``bounds/lower.py`` v1 counts the whole tensor in ``L_source``
    because the *sum* of reads (2 + 2) reaches the leaf count (4): ``L = 16 > 12``.
    ``X = 8``: the two matmuls cannot share an RU (``A1 + A2 + W[0]`` = 12 B), so each RU re-reads ``W[0]``:
    ``I* = (4 + 4) x 2 = 16`` and v1's over-count happens to coincide with ``I*``."""
    c = Circuit(params=[Param("A1", (1, 2), "token"), Param("A2", (1, 2), "token"), Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", "A1"), ("p", "W", "rows", 0, 1))), Op("matmul", (("p", "A2"), ("p", "W", "rows", 0, 1)))],
                name="t1_same_row_read_twice")
    grid = [(BIG_F, BIG_X), (BIG_F, 8)]
    return Case("t1_same_row_read_twice", "t", c, grid, _hand({(BIG_F, BIG_X): 12, (BIG_F, 8): 16}),
                t1_same_row_read_twice.__doc__, expect_violation=("L_gt_Istar",))


@_case
def t2_repeated_row_view_B() -> Case:
    """``y = x . B^T`` where ``B = reprow(W, 0, 2)`` repeats the single row of ``W`` (accumulated ``1 x 2``, 4 B)
    twice; ``x`` token ``1 x 2`` (4 B).  8 gates.  ``I* = 8`` (``W`` once, ``x`` once) for any ``X >= 8``.
    v1's Loomis-Whitney charge uses the positional operand count (``N x K`` = 4 leaves) as if the two rows
    were distinct elements and charges one load of *two* rows (8 B): ``L = 8 + 4 (token) = 12 > 8``."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W", (1, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W", "reprow", 0, 2)))], name="t2_repeated_row_view_B")
    grid = [(BIG_F, BIG_X), (BIG_F, 8)]
    return Case("t2_repeated_row_view_B", "t", c, grid, _hand({(BIG_F, BIG_X): 8, (BIG_F, 8): 8}),
                t2_repeated_row_view_B.__doc__, expect_violation=("L_gt_Istar",))


@_case
def t3_repeated_row_view_A() -> Case:
    """``y1 = reprow(x, 0, 4) . W^T`` and ``y2 = x . Wf^T``: ``x`` carried ``4 x 1`` (8 B, fully read by ``y2``
    whose weights are fixed), ``W`` accumulated ``2 x 1`` (4 B).  36 gates.  ``X = 6``: an RU with ``x[0]``
    (2) + ``W`` (4) runs all of ``y1``; ``x[1..3]`` (6) in another RU runs the rest of ``y2``: ``I* = 12``
    (= source bytes).  v1 treats the 4 repeated rows as 4 distinct rows of an ``alpha = 1`` operand and charges
    ``L = 14 > 12``; at ``X = 4`` (``I* = 14``: ``x[0] + W[n]`` per ``n`` plus ``x[1..3]``) it charges 20."""
    c = Circuit(params=[Param("x", (4, 1), "carried"), Param("W", (2, 1), "accumulated"), Param("Wf", (1, 1), "fixed")],
                ops=[Op("matmul", (("p", "x", "reprow", 0, 4), ("p", "W"))), Op("matmul", (("p", "x"), ("p", "Wf")))],
                name="t3_repeated_row_view_A")
    grid = [(BIG_F, BIG_X), (BIG_F, 6), (BIG_F, 4)]
    return Case("t3_repeated_row_view_A", "t", c, grid, _hand({(BIG_F, BIG_X): 12, (BIG_F, 6): 12, (BIG_F, 4): 14}),
                t3_repeated_row_view_A.__doc__, expect_violation=("L_gt_Istar",), time_limit=60.0)


@_case
def t4_joint_epilogue_F() -> Case:
    """``y = add(x . W1^T, x . W2^T)``, ``x`` token ``1 x 3``, ``W1, W2`` accumulated ``2 x 3`` (12 B each).
    22 gates.  ``F = 5 = K + 2``: a fused RU has ``Up(add) = 1 + 4 + 4 = 9``; the add must be cut from at
    least one chain (2 B per add output, x2) ... the solver gives ``I* = 38`` at ``F <= 8`` and ``30`` at
    ``F >= 9`` (``= 6 + 12 + 12``).  ``upper.py`` fuses the add *jointly* into the shared-``A`` tile and
    declares ``up_max = k + 1 + 1 = 5``: an illegal plan with ``U = 30 < I*``."""
    c = Circuit(params=[Param("x", (1, 3), "token"), Param("W1", (2, 3), "accumulated"), Param("W2", (2, 3), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("matmul", (("p", "x"), ("p", "W2"))), Op("add", (("o", 0), ("o", 1)))],
                name="t4_joint_epilogue_F")
    grid = [(BIG_F, BIG_X), (9, BIG_X), (8, BIG_X), (5, BIG_X), (BIG_F, 12)]
    return Case("t4_joint_epilogue_F", "t", c, grid,
                _hand({(BIG_F, BIG_X): 30, (9, BIG_X): 30, (8, BIG_X): ("ge", 31), (5, BIG_X): ("ge", 31)}),
                t4_joint_epilogue_F.__doc__, expect_violation=("Ulit_illegal", "U_unavailable"))


@_case
def t5_rowfull_epilogue_F() -> Case:
    """``y = rmsnorm(x . W^T, g)``, ``x`` token ``1 x 2``, ``W`` accumulated ``2 x 2``, ``g`` accumulated ``(2,)``.
    18 gates.  Fused in one RU, the last ``Mul16`` of the norm row has ``Up = 1 + 1 + 1 + 2 + 2 + 2 x 3 =
    13``; ``upper.py`` declares ``up_max = 8`` for the row-full fusion.  ``I* = 16`` for ``F >= 13``,
    ``20`` for ``F in [9, 12]`` (the norm row must be cut from the matmul: two 16-bit imports)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W", (2, 2), "accumulated"), Param("g", (2,), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W"))), Op("rmsnorm", (("o", 0), ("p", "g")))], name="t5_rowfull_epilogue_F")
    grid = [(BIG_F, BIG_X), (13, BIG_X), (12, BIG_X), (9, BIG_X)]
    return Case("t5_rowfull_epilogue_F", "t", c, grid, _hand({(BIG_F, BIG_X): 16, (13, BIG_X): 16, (12, BIG_X): 20, (9, BIG_X): 20}),
                t5_rowfull_epilogue_F.__doc__, expect_violation=("Ulit_illegal",))


@_case
def t6_softmax_epilogue_F() -> Case:
    """``y = softmax(x . W^T)``, ``x`` token ``1 x 2``, ``W`` accumulated ``2 x 2``.  22 gates.  The fused
    row's last gate has ``Up = 19``; ``upper.py`` declares 11.  ``I* = 12`` for ``F >= 20``, 16 for
    ``F in [14, 19]``, 22 at ``F = 12``."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W"))), Op("softmax", (("o", 0),))], name="t6_softmax_epilogue_F")
    grid = [(BIG_F, BIG_X), (20, BIG_X), (16, BIG_X), (12, BIG_X)]
    return Case("t6_softmax_epilogue_F", "t", c, grid, _hand({(BIG_F, BIG_X): 12, (20, BIG_X): 12, (16, BIG_X): 16, (12, BIG_X): 22}),
                t6_softmax_epilogue_F.__doc__, expect_violation=("Ulit_illegal",))


@_case
def t7_single_leaf_overlap_share() -> Case:
    """``y1 = A1 . W[0:2]^T``, ``y2 = A2 . W[1:3]^T`` with ``W`` accumulated ``3 x 1``: leaf 1 of ``W`` is read
    by both ops (true per-element multiplicity 2).  ``OpGraph.share(W)`` returns 1 because
    ``_leaf_range`` records inclusive ``(lo, hi)`` while ``share`` sweeps half-open ``[lo, hi)`` (see t9, t10).
    The original v1 ``lower.py`` divided by the consumer count (2) and was unaffected; the §2.2 rewrite
    (``beta = w_B / g.share(B)``) charges ``W[1]`` once per reader: ``L = 4 + 8 = 12 > I* = 2 + 2 + 6 = 10``
    at large ``X``.  ``X = 6``: the ops cannot share an RU (2 + 2 + 6 = 10), so ``W[1]`` really is read
    twice: ``I* = 12`` and the over-count coincides with the optimum.  (Observed ``L = 12`` at large ``X``
    on the 10:22 revision; clean since ``lower.py`` added ``_share_inclusive``.)"""
    c = Circuit(params=[Param("A1", (1, 1), "token"), Param("A2", (1, 1), "token"), Param("W", (3, 1), "accumulated")],
                ops=[Op("matmul", (("p", "A1"), ("p", "W", "rows", 0, 2))), Op("matmul", (("p", "A2"), ("p", "W", "rows", 1, 3)))],
                name="t7_single_leaf_overlap_share")
    grid = [(BIG_F, BIG_X), (BIG_F, 6)]
    return Case("t7_single_leaf_overlap_share", "t", c, grid, _hand({(BIG_F, BIG_X): 10, (BIG_F, 6): 12}),
                t7_single_leaf_overlap_share.__doc__, tags=("share",))


@_case
def t9_scalar_read_by_two_matmuls() -> Case:
    """``y1 = p . Wf1^T``, ``y2 = p . Wf2^T`` with ``p`` accumulated ``1 x 1`` (2 B) and fixed ``1 x 1`` weights.
    6 gates.  One RU reads ``p`` once: ``I* = 2`` for any ``X >= 2``, ``F >= 2``.

    ``graph/opgraph.py``: ``_leaf_range`` records the *inclusive* interval ``(base, base + count - 1)`` =
    ``(0, 0)`` for the single leaf, while ``Edge.ranges`` / ``OpGraph.share`` / ``Edge.covers`` treat it as
    half-open ``[lo, hi)`` = empty.  The sweep line in ``share`` therefore never sees the two readers overlap
    and returns 1 (true multiplicity 2).  ``bounds/lower.py`` (§2.2 model) then lets *each* matmul claim
    ``alpha = w / share = 2`` bytes for ``p``: ``L_cap = 4 > I* = 2``.  Same with ``p`` in the ``B`` role
    (``beta = w_B / share``).  Any single-element charged tensor read by ``n`` ops is over-charged ``n``-fold.
    Status: ``lower.py`` now takes ``max(g.share, _share_inclusive)`` (a local workaround), so ``L = 2``
    again; ``OpGraph.share`` / ``Edge.covers`` in ``graph/opgraph.py`` still read the bounds as half-open
    (``test_redteam.py::test_opgraph_share_counts_single_leaf`` tracks that)."""
    c = Circuit(params=[Param("p", (1, 1), "accumulated"), Param("Wf1", (1, 1), "fixed"), Param("Wf2", (1, 1), "fixed")],
                ops=[Op("matmul", (("p", "p"), ("p", "Wf1"))), Op("matmul", (("p", "p"), ("p", "Wf2")))],
                name="t9_scalar_read_by_two_matmuls")
    grid = [(BIG_F, BIG_X), (2, 2)]
    return Case("t9_scalar_read_by_two_matmuls", "t", c, grid, _hand({(BIG_F, BIG_X): 2, (2, 2): 2}),
                t9_scalar_read_by_two_matmuls.__doc__, tags=("share",))


@_case
def t10_last_leaf_overlap() -> Case:
    """``y1 = x1 . W^T`` (all 3 rows of ``W``), ``y2 = x2 . W[2:3]^T``: ``W`` accumulated ``3 x 1`` (6 B), ``x1, x2``
    fixed.  12 gates.  ``I* = 6`` (one RU).  Recorded ranges are inclusive ``(0, 2)`` and ``(2, 2)``; read as
    half-open they do not overlap, so ``share(W) = 1`` although leaf 2 has two readers; ``lower.py`` charges
    ``W[2]`` twice: ``L = 8 > 6`` (observed before ``lower.py``'s ``_share_inclusive`` workaround; clean since).
    The general form of the t9 defect: the *last* leaf of every recorded range is dropped from the overlap
    count."""
    c = Circuit(params=[Param("W", (3, 1), "accumulated"), Param("x1", (1, 1), "fixed"), Param("x2", (1, 1), "fixed")],
                ops=[Op("matmul", (("p", "x1"), ("p", "W"))), Op("matmul", (("p", "x2"), ("p", "W", "rows", 2, 3)))],
                name="t10_last_leaf_overlap")
    grid = [(BIG_F, BIG_X), (BIG_F, 6)]
    return Case("t10_last_leaf_overlap", "t", c, grid, _hand({(BIG_F, BIG_X): 6, (BIG_F, 6): 6}),
                t10_last_leaf_overlap.__doc__, tags=("share",))


@_case
def t11_reprow_B_deep() -> Case:
    """``h = x . W1^T`` (``x`` carried ``1 x 2``, ``W1`` accumulated ``1 x 2``), ``h' = add(h, c)`` (``c`` fixed),
    ``t = h' . reprow(W, 0, 4)^T`` (``W`` accumulated ``1 x 1``: the four "weight rows" are one element),
    ``y = t . V^T`` (``V`` fixed ``1 x 4``).  23 gates.  Charged bytes: ``x`` 4 + ``W1`` 4 + ``W`` 2 = 10.
    ``X >= 10``: one RU, ``I* = 10``.  ``X = 8``: ``x + W1`` (8) in one RU makes ``h``; a second RU holds
    ``h`` (2) + ``W`` (2) + ... = ``I* = 12``.

    The §2.2 charge of ``t``'s matmul is ``beta * b_R`` with ``b <= N K`` *positional* B elements: the four
    repeated rows are counted as 4 distinct elements (``8 B``) although only one (2 B) exists -- ``per_op[2] =
    8`` and ``L = 16 > I*`` at every feasible ``X``.  Same root cause as t2/t3 (positions != elements), now
    for the v2 ``beta`` term with a produced ``A`` operand."""
    c = Circuit(params=[Param("x", (1, 2), "carried"), Param("W1", (1, 2), "accumulated"), Param("c", (1, 1), "fixed"),
                        Param("W", (1, 1), "accumulated"), Param("V", (1, 4), "fixed")],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("add", (("o", 0), ("p", "c"))),
                     Op("matmul", (("o", 1), ("p", "W", "reprow", 0, 4))), Op("matmul", (("o", 2), ("p", "V")))],
                name="t11_reprow_B_deep")
    grid = [(BIG_F, BIG_X), (BIG_F, 10), (BIG_F, 8)]
    return Case("t11_reprow_B_deep", "t", c, grid, _hand({(BIG_F, BIG_X): 10, (BIG_F, 10): 10, (BIG_F, 8): 12}),
                t11_reprow_B_deep.__doc__, expect_violation=("L_gt_Istar",))


@_case
def t8_add_same_tensor_twice() -> Case:
    """``y = add(x, x)`` with ``x`` carried ``2 x 2`` (8 B).  ``I* = 8`` for ``X >= 2`` (each gate needs one
    element).  ``upper.py`` counts the operand with repeats (16 B per copy) and raises at ``X < 16``."""
    c = Circuit(params=[Param("x", (2, 2), "carried")], ops=[Op("add", (("p", "x"), ("p", "x")))], name="t8_add_same_tensor_twice")
    grid = [(BIG_F, BIG_X), (BIG_F, 8), (BIG_F, 2)]
    return Case("t8_add_same_tensor_twice", "t", c, grid, _hand({(BIG_F, BIG_X): 8, (BIG_F, 8): 8, (BIG_F, 2): 8}),
                t8_add_same_tensor_twice.__doc__, expect_violation=("U_unavailable",))


@_case
def t12_attn_decode_kv_undercount() -> Case:
    """Decode-shaped attention: ``s = q Kc^T`` (``q`` token ``1 x 2``, ``Kc`` **carried** ``2 x 2`` = 2 cached keys),
    ``p = softmax(s)`` (``1 x 2``), ``o = p Vt^T`` (``Vt`` carried ``2 x 2``).  30 gates, work 27.  Charged: ``q`` 4 +
    ``Kc`` 8 + ``Vt`` 8 = 20, so ``I* = 20`` in one RU (``X >= 20``).  ``X = 12`` or ``16``: the three tensors do not
    fit together; ``{scores + softmax}`` imports ``q`` + ``Kc`` = 12 and ``{pv}`` imports ``Vt`` + ``p`` (4) = 12:
    ``I* = 24``.

    **Defect (upper.py):** ``_attn_fwd_unit`` (``bounds/upper.py:998-1014``) sizes the fused RU's K and V slices as
    ``S * DH`` with ``S`` = *query* rows (``M`` of the scores matmul), while ``_detect_attn_fwd`` (``:938-960``) accepts
    ``N != M`` (it only checks ``N == softmax K``).  With 1 query and 2 cached keys the K/V bytes are under-counted
    by ``N / M = 2``: the unit declares ``imports_max = 4 + 4 + 4 = 12`` but the RU actually reads 20 B, so ``U = 12
    < L = I* = 20`` at ``X = inf`` and the plan is illegal at ``X = 12`` (``is_legal``: 20 B > X).  ``check_plan``
    agrees with the plan because it re-derives from the same ``S``.  The work per query row (``wpr``, ``:1020``) is
    under-counted the same way, so ``F`` / ``G`` legality of these units is also unverified.  Fix: use ``N`` (keys)
    for the K/V slice sizes and score-row work, or require ``N == M`` in the detector as ``_detect_attn_bwd``
    (``:1121``) already does.  Same defect on ``i2_inference_attn_decode``."""
    c = Circuit(params=[Param("q", (1, 2), "token"), Param("Kc", (2, 2), "carried"), Param("Vt", (2, 2), "carried")],
                ops=[Op("matmul", (("p", "q"), ("p", "Kc"))), Op("softmax", (("o", 0),)),
                     Op("matmul", (("o", 1), ("p", "Vt")))], name="t12_attn_decode_kv_undercount")
    grid = [(BIG_F, BIG_X), (BIG_F, 16), (BIG_F, 12), (20, BIG_X)]
    return Case("t12_attn_decode_kv_undercount", "t", c, grid,
                _hand({(BIG_F, BIG_X): 20, (BIG_F, 16): 24, (BIG_F, 12): 24, (20, BIG_X): 24}),
                t12_attn_decode_kv_undercount.__doc__, time_limit=30.0,
                expect_violation=("Ulit_lt_Istar", "Ulit_illegal", "Ulit_cost_under", "Ulit_ru_over", "Urec_lt_L", "Ulit_lt_L"))


# ---------------------------------------------------------------------------------------------------------
# k. the total-work cap G (SPEC §1, THEORY §0.1 "Role of G")
# ---------------------------------------------------------------------------------------------------------

@_case
def k1_matmul_G_forced_split() -> Case:
    """``y = x . W^T``, ``x`` token ``2 x 2`` (8 B), ``W`` accumulated ``2 x 2`` (8 B); 16 gates, work 12
    (per output: ``Zero32`` 0, two ``Mac`` 1 each, ``Round16`` 1).  ``F = X = inf`` throughout; only ``G`` binds.

    ``G >= 12``: one RU, ``I* = 16``.  ``G = 11``: one gate must leave; cheapest is a ``Round16`` alone
    (imports its 4-byte accumulator): ``20``.  ``G = 6``: two 3-work chains per RU, grouped by ``x`` row
    (``x[i, :]`` 4 B + all of ``W`` 8 B = 12 per RU) or by ``W`` row (same): ``24``.  ``G = 3``: one chain per
    RU, ``x`` row + ``W`` row = 8 B, four RUs: ``32``.  ``G = 1``: every gate alone -- ``Mac1`` reads
    ``x_ik, W_jk`` (4 B), ``Mac2`` reads the accumulator (4 B) + ``x, W`` (4 B), ``Round`` reads the accumulator
    (4 B): 16 B per output, ``64``.  ``G = 0``: a ``Mac`` alone has work 1 > 0 -- infeasible.  (Cross-checked
    against all three exact solvers in ``tests/test_exact_g.py``.)"""
    c = Circuit(params=[Param("x", (2, 2), "token"), Param("W", (2, 2), "accumulated")],
                ops=[Op("matmul", (("p", "x"), ("p", "W")))], name="k1_matmul_G_forced_split")
    grid = [(BIG_F, BIG_X), (BIG_F, BIG_X, 12), (BIG_F, BIG_X, 11), (BIG_F, BIG_X, 6), (BIG_F, BIG_X, 3),
            (BIG_F, BIG_X, 1), (BIG_F, BIG_X, 0)]
    return Case("k1_matmul_G_forced_split", "k", c, grid,
                _hand({(BIG_F, BIG_X): 16, (BIG_F, BIG_X, 12): 16, (BIG_F, BIG_X, 11): 20, (BIG_F, BIG_X, 6): 24,
                       (BIG_F, BIG_X, 3): 32, (BIG_F, BIG_X, 1): 64, (BIG_F, BIG_X, 0): ("inf", None)}),
                k1_matmul_G_forced_split.__doc__, g_fracs=())


# ---------------------------------------------------------------------------------------------------------
# i. dense inference micro circuits (all weights fixed; tokens / KV cache charged)
# ---------------------------------------------------------------------------------------------------------

@_case
def i1_inference_mlp() -> Case:
    """Dense inference MLP block for one token: ``h1 = x W1^T``, ``h3 = x W3^T``, ``a = swiglu(h1, h3)``,
    ``y = a W2^T``, ``out = x + y``; ``x`` token ``1 x 2`` (4 B), ``W1, W3, W2`` fixed ``2 x 2`` (free).  28 gates,
    work 24 (three matmuls 6 each, swiglu 2 x 2, add 2 x 1).

    Only ``x`` is charged, so ``I* = 4`` whenever one RU is legal (``G >= 24``, ``F >= 5``).  ``G = 12``: the
    exact solver splits by *output column* -- each RU computes column ``c`` of ``h1, h3, a`` and of ``y`` (which
    needs both columns of ``a``, so it imports the other RU's ``a`` element, 2 B) plus ``out[c]``: ``2 x (4 + 2)
    = 12``.  ``G = 6``: one matmul per RU for ``h1``, ``h3`` (``x``, 4 B each) and two RUs of ``{swiglu[c],
    y[:, c] chain, add}`` importing ``h1[c], h3[c]`` (4 B), the other ``a`` element (2 B) and ``x[c]`` (2 B):
    ``4 + 4 + 8 + 8 = 24``.  ``F = 4``: the ``y`` chain (``Up = 3``) may not sit on top of ``a`` (``Up`` would be
    ``>= 6``), so ``a`` crosses an RU boundary (solver: ``16``)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W1", (2, 2), "fixed"), Param("W3", (2, 2), "fixed"),
                        Param("W2", (2, 2), "fixed")],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("matmul", (("p", "x"), ("p", "W3"))),
                     Op("swiglu", (("o", 0), ("o", 1))), Op("matmul", (("o", 2), ("p", "W2"))),
                     Op("add", (("p", "x"), ("o", 3)))], name="i1_inference_mlp")
    grid = [(BIG_F, BIG_X), (BIG_F, BIG_X, 12), (BIG_F, BIG_X, 6), (BIG_F, 4), (BIG_F, 4, 12), (4, BIG_X), (4, BIG_X, 6)]
    return Case("i1_inference_mlp", "i", c, grid,
                _hand({(BIG_F, BIG_X): 4, (BIG_F, BIG_X, 12): 12, (BIG_F, BIG_X, 6): 24, (BIG_F, 4): 4}),
                i1_inference_mlp.__doc__, time_limit=30.0, g_fracs=())


@_case
def i2_inference_attn_decode() -> Case:
    """Dense inference decode-step attention head: ``q = x Wq^T`` (``x`` token ``1 x 2``, ``Wq`` fixed), scores
    ``s = q Kc^T`` against a **carried** KV cache ``Kc`` (``2 x 2``, 8 B), ``p = softmax(s)``, ``o = p Vt^T``
    (``Vt`` carried ``2 x 2`` stored transposed, 8 B), ``y = o Wo^T`` (``Wo`` fixed), ``out = x + y``.  48 gates,
    work 41.  Charged inputs: ``x`` (4) + ``Kc`` (8) + ``Vt`` (8) = 20, so ``I* = 20`` with one RU (``G >= 41``).
    ``X = 12`` forces at least the cache to be split across RUs (solver: ``32``).  The automatic ``G = 21``
    point is binding (solver: ``32``); smaller ``G`` values are not proven optimal within the time box.

    Known defect (see ``t12_attn_decode_kv_undercount``): the fused attention unit of ``upper.py`` sizes the K/V
    import by the number of *queries* (1) instead of keys (2), so at ``X = 12`` it declares a 24-byte plan whose
    fused RU really imports 20 B > X (``Ulit_illegal``, ``Ulit_lt_Istar``: 24 < 32)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("Wq", (2, 2), "fixed"), Param("Kc", (2, 2), "carried"),
                        Param("Vt", (2, 2), "carried"), Param("Wo", (2, 2), "fixed")],
                ops=[Op("matmul", (("p", "x"), ("p", "Wq"))), Op("matmul", (("o", 0), ("p", "Kc"))),
                     Op("softmax", (("o", 1),)), Op("matmul", (("o", 2), ("p", "Vt"))),
                     Op("matmul", (("o", 3), ("p", "Wo"))), Op("add", (("p", "x"), ("o", 4)))],
                name="i2_inference_attn_decode")
    grid = [(BIG_F, BIG_X), (BIG_F, 12), (BIG_F, 12, 20)]
    return Case("i2_inference_attn_decode", "i", c, grid, _hand({(BIG_F, BIG_X): 20}),
                i2_inference_attn_decode.__doc__, time_limit=30.0, g_fracs=(0.5,),
                expect_violation=("Ulit_illegal", "Ulit_lt_Istar", "Ulit_cost_under", "Ulit_ru_over"))


# ---------------------------------------------------------------------------------------------------------
# r. dense training micro circuits (accumulated weights, forward + weight gradient + SGD update)
# ---------------------------------------------------------------------------------------------------------

@_case
def r1_train_linear_sgd() -> Case:
    """One linear layer's training step: ``y = x W^T`` (``x`` token ``1 x 2``, ``W`` accumulated ``2 x 2``),
    weight gradient ``dW = dy^T x`` (``AccMatmulTT``, ``dy`` token ``1 x 2``, contraction over the single row),
    ``W' = W - lr dW`` (``AccSgdUpdate``, ``lr`` 32-bit seed).  28 gates, work 22 (forward 6, ``dW`` 8 =
    ``2 x 2`` outputs x (1 MAC + Round), SGD 8).  Charged: ``x`` 4 + ``W`` 8 + ``dy`` 4 + ``lr`` 4 = 20.

    ``I* = 20`` with one RU.  ``G = 11``: split by ``W`` row -- each RU computes ``y[n]`` (needs ``x``, ``W[n,:]``),
    ``dW[n, :]`` (``dy[n]``, ``x``) and ``W'[n, :]`` (``W[n,:]``, ``lr``): ``4 + 4 + 2 + 4 = 14`` each, ``28``.
    ``X = 12``: the ``lr`` scalar (4 B) is re-imported by every RU that updates a row (solver: ``36``)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W", (2, 2), "accumulated"), Param("dy", (1, 2), "token"),
                        Param("lr", (), "seed", width=32)],
                ops=[Op("matmul", (("p", "x"), ("p", "W"))), Op("matmul_tt", (("p", "dy"), ("p", "x"))),
                     Op("sgd", (("p", "W"), ("o", 1), ("p", "lr")))], name="r1_train_linear_sgd")
    grid = [(BIG_F, BIG_X), (BIG_F, BIG_X, 11), (BIG_F, BIG_X, 5), (BIG_F, 12), (BIG_F, 12, 11), (BIG_F, 8)]
    return Case("r1_train_linear_sgd", "r", c, grid,
                _hand({(BIG_F, BIG_X): 20, (BIG_F, BIG_X, 11): 28}), r1_train_linear_sgd.__doc__, time_limit=30.0,
                g_fracs=())


@_case
def r2_train_two_layer() -> Case:
    """Two accumulated layers, gradient for the second: ``h = x W1^T``, ``y = h W2^T``, ``dW2 = dy^T h``
    (``AccMatmulTT`` on the *activation* ``h``), ``W2' = W2 - lr dW2``.  ``x``, ``dy`` token ``1 x 2``,
    ``W1, W2`` accumulated ``2 x 2``, ``lr`` 32-bit seed.  36 gates, work 28.  Charged: 4 + 8 + 8 + 4 + 4 = 28.
    ``I* = 28`` in one RU; ``G = 14`` (half the work) forces two RUs -- the shared activation ``h`` is needed by
    both ``y`` and ``dW2``, so splitting the second layer by output row keeps ``h`` local only if ``W1`` is
    imported twice (solver: ``40``).  ``X = 16``: ``I* = 40`` (three RUs)."""
    c = Circuit(params=[Param("x", (1, 2), "token"), Param("W1", (2, 2), "accumulated"), Param("W2", (2, 2), "accumulated"),
                        Param("dy", (1, 2), "token"), Param("lr", (), "seed", width=32)],
                ops=[Op("matmul", (("p", "x"), ("p", "W1"))), Op("matmul", (("o", 0), ("p", "W2"))),
                     Op("matmul_tt", (("p", "dy"), ("o", 0))), Op("sgd", (("p", "W2"), ("o", 2), ("p", "lr")))],
                name="r2_train_two_layer")
    grid = [(BIG_F, BIG_X), (BIG_F, BIG_X, 14), (BIG_F, 16), (BIG_F, 16, 14)]
    return Case("r2_train_two_layer", "r", c, grid, _hand({(BIG_F, BIG_X): 28}), r2_train_two_layer.__doc__,
                time_limit=30.0, g_fracs=())


# ---------------------------------------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------------------------------------

def check_hand(rec: Record, hand: Hand) -> Optional[bool]:
    kind, v = hand
    if kind == "inf":
        return rec.Istar_infeasible if (rec.Istar is not None or rec.Istar_infeasible) else None
    if rec.Istar is None:
        return None
    if kind == "eq":
        return rec.Istar == v if rec.Istar_optimal else (rec.Istar >= v)
    if kind == "ge":
        return rec.Istar >= v if rec.Istar_optimal else None
    if kind == "le":
        return rec.Istar <= v
    raise ValueError(kind)


_PREP: dict[str, tuple] = {}


def _prepare(case: Case) -> tuple:
    """``(bp, flat, g, op_gates, snippet)`` for a case (cached: the build is deterministic)."""
    if case.name not in _PREP:
        from accumulation.exact.solve import flatten
        from accumulation.graph import extract
        from accumulation.redteam.harness import op_gate_lists
        bp = build(case.circuit)
        flat = flatten(bp)
        g = extract(bp)
        _PREP[case.name] = (bp, flat, g, op_gate_lists(bp, g, flat), case.circuit.to_python())
    return _PREP[case.name]


_MEMO: dict[tuple, Record] = {}


def run_point(case: Case, F: int, X: int, G: int | None = None, *, time_limit: float | None = None, lower_fn=None,
              upper_fn=None) -> Record:
    """Evaluate one grid point of ``case`` and attach the hand verdict (memoised for the default bounds)."""
    default = time_limit is None and lower_fn is None and upper_fn is None
    key = (case.name, F, X, G)
    if default and key in _MEMO:
        return _MEMO[key]
    rec = _run_point(case, F, X, G, time_limit=time_limit, lower_fn=lower_fn, upper_fn=upper_fn)
    if default:
        _MEMO[key] = rec
    return rec


def _run_point(case: Case, F: int, X: int, G: int | None, *, time_limit: float | None, lower_fn, upper_fn) -> Record:
    bp, flat, g, og, snippet = _prepare(case)
    kw = {}
    if lower_fn is not None:
        kw["lower_fn"] = lower_fn
    if upper_fn is not None:
        kw["upper_fn"] = upper_fn
    rec = evaluate(bp, F, X, G, family=case.family, name=case.name, snippet=snippet,
                   time_limit=time_limit or case.time_limit, g=g, flat=flat, op_gates=og, **kw)
    h = case.hand.get((F, X, G))
    if h is not None:
        rec.hand_kind, rec.hand = h
        rec.hand_ok = check_hand(rec, h)
    return rec


def g_points(case: Case) -> list[Point]:
    """Automatic binding-``G`` points: at the loosest ``(F, X)`` of the grid, ``G = ceil(frac * work)`` for every
    ``frac`` in ``case.g_fracs`` (only values strictly below the total work and at least the largest single gate
    work, so that they bind without being trivially infeasible)."""
    if not case.g_fracs:
        return []
    flat = _prepare(case)[1]
    W = flat.total_work()
    wmax = max((flat.work[x] for x in flat.gates), default=0)
    F0, X0, _ = max(case.grid, key=lambda p: (p[0], p[1]))
    out: list[Point] = []
    for fr in case.g_fracs:
        G = max(wmax, -(-int(W * fr) // 1))
        if G < W and (F0, X0, G) not in case.grid and (F0, X0, G) not in out:
            out.append((F0, X0, G))
    return out


def run_case(case: Case, *, time_limit: float | None = None, lower_fn=None, upper_fn=None, with_g: bool = True) -> list[Record]:
    g = _prepare(case)[2]
    pts = list(case.grid) + (g_points(case) if with_g else [])
    out = [run_point(case, F, X, G, time_limit=time_limit, lower_fn=lower_fn, upper_fn=upper_fn) for F, X, G in pts]
    if "share" in case.tags:
        # record the extractor's per-element share of every charged root (true multiplicity is 2 in these cases)
        shares = {p.name: g.share(g.params[p.name]) for p in case.circuit.params if p.charged and p.name in g.params}
        for r in out:
            r.snippet += f"\n# OpGraph.share = {shares} (true per-element multiplicity of the shared leaf = 2)"
    return out


def run_torture(names: list[str] | None = None, *, time_limit: float | None = None, lower_fn=None, upper_fn=None,
                verbose: bool = True) -> tuple[list[Record], list[str]]:
    recs: list[Record] = []
    mono: list[str] = []
    for case in CASES:
        if names and case.name not in names:
            continue
        rs = run_case(case, time_limit=time_limit, lower_fn=lower_fn, upper_fn=upper_fn)
        recs.extend(rs)
        for m in monotonicity_violations(rs):
            mono.append(f"{case.name}: {m}")
        if verbose:
            for r in rs:
                print(format_row(r))
    return recs, mono


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "T" if v else "F"
    return str(v)


def _fmtL(r: Record) -> str:
    """``L`` with the SPEC-required marker when the certificate ran at ``G=None`` for a binding-``G`` row."""
    if r.L_error:
        return "ERR"
    L = "INF" if r.L_infeasible else _fmt(r.L)
    if r.G is not None and r.L_G is None and r.L is not None:
        L += "@G=None"
    return L


def _fmtG(r: Record) -> str:
    return "-" if r.G is None else str(r.G)


def format_row(r: Record) -> str:
    F = "inf" if r.F >= BIG_F else str(r.F)
    X = "inf" if r.X >= BIG_X else str(r.X)
    hand = "-" if r.hand_kind == "" else (f"{r.hand_kind}:{'inf' if r.hand_kind == 'inf' else r.hand}")
    istar = "INF" if r.Istar_infeasible else ("T/O" if r.Istar_timeout else _fmt(r.Istar) + ("" if r.Istar_optimal or r.Istar is None else "?"))
    U = _fmt(r.U) if not r.U_error else "ERR"
    Ul = _fmt(r.Ulit) if not r.Ulit_error else "ERR"
    leg = "-" if r.Ulit_legal is None else ("ok" if r.Ulit_legal else "ILLEGAL")
    return (f"{r.name:32s} F={F:>4s} G={_fmtG(r):>4s} X={X:>4s} | hand={hand:8s} L={_fmtL(r):>4s} I*={istar:>5s} U={U:>4s} "
            f"Ulit={Ul:>4s} legal={leg:7s} handok={_fmt(r.hand_ok):2s} | {','.join(r.violations) or 'clean'}")


def table(recs: list[Record]) -> str:
    head = ("| case | F | G | X | hand | L | I* | U | U_lit | U_lit legal | hand ok | violations |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for r in recs:
        F = "inf" if r.F >= BIG_F else str(r.F)
        X = "inf" if r.X >= BIG_X else str(r.X)
        hand = "" if r.hand_kind == "" else (f"{r.hand_kind} {'inf' if r.hand_kind == 'inf' else r.hand}")
        istar = "infeasible" if r.Istar_infeasible else ("timeout" if r.Istar_timeout else _fmt(r.Istar) + ("" if r.Istar_optimal or r.Istar is None else " (not proven)"))
        U = _fmt(r.U) if not r.U_error else "error"
        Ul = _fmt(r.Ulit) if not r.Ulit_error else "error"
        leg = "" if r.Ulit_legal is None else ("ok" if r.Ulit_legal else "ILLEGAL")
        rows.append(f"| {r.name} | {F} | {_fmtG(r)} | {X} | {hand} | {_fmtL(r)} | {istar} | {U} | {Ul} | {leg} | {_fmt(r.hand_ok)} | {', '.join(r.violations)} |")
    return head + "\n" + "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="red-team torture suite")
    ap.add_argument("--case", action="append", help="run only these cases")
    ap.add_argument("--out", default="/tmp/redteam/torture.jsonl")
    ap.add_argument("--md", default="/tmp/redteam/torture.md")
    ap.add_argument("--time-limit", type=float, default=None)
    a = ap.parse_args(argv)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    recs, mono = run_torture(a.case, time_limit=a.time_limit)
    with open(a.out, "w") as f:
        for r in recs:
            f.write(json.dumps(r.to_json()) + "\n")
    with open(a.md, "w") as f:
        f.write(table(recs) + "\n")
        if mono:
            f.write("\nMonotonicity violations:\n" + "\n".join(f"- {m}" for m in mono) + "\n")
    bad = [r for r in recs if r.violations]
    print(f"\n{len(recs)} points, {len(bad)} with violations, {len(mono)} monotonicity violations; "
          f"hand mismatches: {sum(1 for r in recs if r.hand_ok is False)}")
    for m in mono:
        print("MONO:", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
