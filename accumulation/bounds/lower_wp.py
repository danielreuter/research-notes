"""Weight-presence certificate for chained (multi-step) training circuits under ``(F, G)`` RU policies.

A value produced inside the circuit costs nothing only if the RU that consumes it also produces it.  For a
dynamic weight tensor ``W_k`` (the output of step ``k-1``'s update, read by step ``k``'s forward / recompute /
backward kernels and by step ``k``'s update) every element is therefore imported by at least one RU unless a
single RU holds its producer and *all* of its consumers.  Such an RU is convex (SPEC s0: the RU quotient is
acyclic), so it contains every gate on every path from the producer to the step-``k`` update.  At the gate
level those paths run, for every token of the step, from the forward kernel that reads ``W_k`` through the
residual stream, the head and the loss, back down the backward pass to ``dW_k`` (a reduction over *all*
tokens of the step) and into the update: every gate of every op that is at once a descendant of the producer
and an ancestor of the update lies on such a path.  The update gate hence has upstream work at least

    Up_lb(W_k) = sum of ``op.work`` over ops O with  producer(W_k) ->* O ->* update_k(W_k),

and the RU has ``Work >= Up >= Up_lb``.  If ``Up_lb > F`` or ``Up_lb > G`` no legal RU can hold producer and
consumers together, and ``bytes(W_k)`` is charged.  Summing over the chained weights of all steps gives
``L_wp``; it is additive with the root floor (elements of step-0 roots and tokens that are read at least once)
because the two count disjoint values.

Soundness rests on two facts checked per tensor: (i) every non-update consumer reads the whole tensor (each
element has a forward consumer -- true for matmul weights and norm gains; embedding tables read by a gather
are skipped), and (ii) the op-level "between" set is realised gate-by-gate for every element: in a residual
transformer every coordinate of every position of the layers above feeds the loss (full-width contractions,
attention), every position's loss gradient feeds every coordinate of ``dY`` below it, and ``dW`` sums all
positions -- so all gates of the between ops are ancestors of the update gate of every element.  Hand-built
micro chains without that mixing (``exact/micro.py``) violate (ii); the certificate is therefore gated on the
transformer structure (``_transformer_shaped``) and ``redteam/wp_gatecheck.py`` verifies (ii) at the gate
level on the tiny registry circuits.  Forward-only circuits and single-step training have no chained weights
and get ``L_wp = 0``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from accumulation.graph.opgraph import OpGraph

UPDATE_KINDS = frozenset({"sgdupdate", "esupdate", "perturb"})


@dataclass
class WPBound:
    total: int                                   # bytes: forced dynamic-weight imports (sum over chained tensors)
    n_candidates: int                            # chained weight tensors examined
    n_forced: int
    binds: dict = field(default_factory=dict)    # {"F": n, "G": n, "both": n}
    by_producer_step: dict = field(default_factory=dict)   # producer-block index -> forced bytes
    forced: list = field(default_factory=list)   # per tensor (truncated): tid, name, bytes, up_lb
    notes: list = field(default_factory=list)


@dataclass
class ChainedWeight:
    tid: int
    producer: int          # update op producing the tensor
    update: int            # the (first) update op consuming it
    others: list           # non-update consumers (forward / recompute / backward kernels)
    between: set           # ops O with producer ->* O ->* update (op ids; includes both ends)
    up_lb: int             # sum of op.work over ``between``
    bytes: int
    step_block: int        # run index of the producer among the update ops (diagnostics)


def _consumers(g: OpGraph) -> dict[int, list[int]]:
    cons: dict[int, list[int]] = {}
    for op in g.ops:
        for e in op.inputs:
            cons.setdefault(e.src, []).append(op.id)
    return cons


def _transformer_shaped(g: OpGraph, program) -> tuple[bool, str]:
    """The gate-level realisation of the op-level between set (docstring, fact (ii)) is argued for the registry's
    residual transformer training steps -- full-width contractions and attention mix every coordinate and position
    into the loss and back into every ``dW``.  Hand-built micro chains without that mixing (``exact/micro.py``) are
    refused, exactly as ``lower_coarse``'s block term only fires on transformer-shaped circuits."""
    if program is None:
        return False, "no program attached: transformer structure cannot be verified"
    try:
        from accumulation.bounds.coarse import _Ctx, _discover
        st = _discover(_Ctx(g, program))
    except Exception as e:  # noqa: BLE001
        return False, f"structure discovery failed: {type(e).__name__}: {e}"
    if st.generic or not st.steps or not any(s.layers for s in st.steps):
        return False, "not transformer-shaped (no forward blocks recognised)"
    if not any(L.bwd for s in st.steps for L in s.layers):
        return False, "no backward blocks: the update is not downstream of a loss over all positions"
    return True, f"{len(st.steps)} steps x {max(len(s.layers) for s in st.steps)} layers"


def _layer_map(g: OpGraph, program) -> Optional[dict[int, tuple[int, int]]]:
    """op id -> (step index, layer index) for ops under a transformer layer's forward / backward roots; head ops
    (between the last forward block and the first backward block) map to layer index ``n_layers``.  ``None`` when
    the circuit is not transformer-shaped."""
    if program is None:
        return None
    from accumulation.bounds.coarse import _Ctx, _discover
    st = _discover(_Ctx(g, program))
    if st.generic or not st.steps:
        return None
    out: dict[int, tuple[int, int]] = {}
    for si, s in enumerate(st.steps):
        for li, L in enumerate(s.layers):
            for r in L.fwd + L.bwd:
                for o in st.ops_by_root[r]:
                    out[o] = (si, li)
        for r in s.head:                       # the head sits directly above the top layer: index n_layers
            for o in st.ops_by_root[r]:
                out[o] = (si, len(s.layers))
    return out


def chained_weights(g: OpGraph, program=None) -> tuple[list[ChainedWeight], int]:
    """Every dynamic weight tensor with an update producer, a whole-tensor non-update consumer and an update
    consumer, with its op-level between set and ``Up_lb``.  Returns ``(weights, n_skipped_partial_reads)``.

    With a program the between set is restricted to ops of the layers strictly *above* the weight's own layer
    (plus the head): those are the ops whose every gate feeds the residual-stream gradient ``dX_{l+1}[q, :]`` at
    its position (or the loss), hence every element of ``dW_l``.  Ops of the weight's own layer are only partly
    upstream of a given element (the ``dW`` chain of element ``e``, the column ``i`` of the gradient feeding it)
    and are excluded; ``redteam/wp_gatecheck.py`` verifies the restricted rule gate by gate.  Without a program
    the raw op-level between set is returned (validation use only; not sound as a certificate)."""
    ops = g.ops
    n = len(ops)
    lmap = _layer_map(g, program) if program is not None else None
    cons = _consumers(g)
    preds: list[list[int]] = [[] for _ in range(n)]
    succs: list[list[int]] = [[] for _ in range(n)]
    for op in ops:
        for e in op.inputs:
            t = g.tensors[e.src]
            if t.kind == "op" and t.producer is not None:
                preds[op.id].append(t.producer)
                succs[t.producer].append(op.id)
    work = [op.work for op in ops]
    # producer-block index (diagnostics only): runs of update ops in id order, one run per training step
    block_of: dict[int, int] = {}
    b, prev = -1, -100
    for oid in sorted(op.id for op in ops if op.kind in UPDATE_KINDS):
        if oid - prev > 16:
            b += 1
        block_of[oid] = b
        prev = oid
    out: list[ChainedWeight] = []
    skipped = 0
    memo_anc: dict[int, set[int]] = {}
    for t in g.tensors:
        if t.kind != "op" or t.producer is None or ops[t.producer].kind not in UPDATE_KINDS:
            continue
        cs = cons.get(t.id, [])
        upd = [c for c in cs if ops[c].kind in UPDATE_KINDS]
        others = [c for c in cs if ops[c].kind not in UPDATE_KINDS]
        if not upd or not others:
            continue
        # (i) every element has a non-update consumer: each such consumer reads the whole tensor
        if any(e.src == t.id and e.leaves_per_copy < t.leaves for c in others for e in ops[c].inputs):
            skipped += 1
            continue
        p, u = t.producer, min(upd)
        # every op's id is a topological position (extraction order): an op between p and u has p <= id <= u
        anc = memo_anc.get(u)
        if anc is None:                       # ancestors of u with id >= p, including u
            anc = {u}
            stack = [u]
            while stack:
                o = stack.pop()
                for q in preds[o]:
                    if q >= p and q not in anc:
                        anc.add(q)
                        stack.append(q)
            memo_anc[u] = anc
        desc = {p}                            # descendants of p with id <= u, including p
        stack = [p]
        while stack:
            o = stack.pop()
            for q in succs[o]:
                if q <= u and q not in desc:
                    desc.add(q)
                    stack.append(q)
        between = anc & desc
        if lmap is not None:
            # the weight's own (step, layer): the highest layer holding one of its non-update consumers (forward,
            # recompute, backward; a head weight's backward consumer sits in the top layer's backward composite,
            # its forward consumer in the head) -- only layers strictly above every consumer are counted
            own = [lmap[c] for c in others if c in lmap]
            if not own or len(others) != len(own):        # a consumer outside the recognised structure: nothing certified
                between = set()
            else:
                step_k, lay = max(own)
                # layers >= own + 2 (and the head): layer own+1 is excluded because the ops that *produce* the
                # residual-stream gradient dX_{own+1}[q, j] are per-coordinate -- only coordinate j of them is upstream of
                # dW[j, :] of a weight writing to the residual (W_o, W_down); one layer further up every gate has passed
                # through a full contraction (the MLP down-projection transpose) and an attention mix of positions
                between = {o for o in between if o in lmap and lmap[o][0] == step_k and lmap[o][1] >= lay + 2}
        out.append(ChainedWeight(t.id, p, u, others, between, sum(work[o] for o in between), t.bytes, block_of.get(p, -1)))
    return out, skipped


def weight_presence_bound(g: OpGraph, F: Optional[int], G: Optional[int], *, program=None, max_records: int = 64,
                          require_transformer: bool = True) -> WPBound:
    """``L_wp`` (module docstring).  ``F`` / ``G`` ``None`` = unbounded.  ``require_transformer=False`` skips the
    class-T structure gate (for harnesses that check the op-level rule against the gate level)."""
    program = program if program is not None else getattr(g, "program", None)
    if require_transformer:
        ok, why = _transformer_shaped(g, program)
        if not ok:
            return WPBound(0, 0, 0, {"F": 0, "G": 0, "both": 0}, {}, [], [f"L_wp = 0: {why}"])
    cands, skipped = chained_weights(g, program)
    total = n_forced = 0
    binds = {"F": 0, "G": 0, "both": 0}
    by_step: dict[int, int] = {}
    records: list[dict] = []
    for w in cands:
        f_bind = F is not None and w.up_lb > F
        g_bind = G is not None and w.up_lb > G           # Work(R) >= Up(u) >= up_lb
        if not (f_bind or g_bind):
            continue
        total += w.bytes
        n_forced += 1
        binds["both" if (f_bind and g_bind) else ("F" if f_bind else "G")] += 1
        by_step[w.step_block] = by_step.get(w.step_block, 0) + w.bytes
        if len(records) < max_records:
            records.append({"tid": w.tid, "name": g.tensors[w.tid].name, "bytes": w.bytes, "producer": w.producer, "update": w.update,
                            "step_block": w.step_block, "up_lb": w.up_lb, "up_over_F": (w.up_lb / F) if F else None,
                            "up_over_G": (w.up_lb / G) if G else None})
    notes = [f"{len(cands)} chained weight tensors, {n_forced} forced ({binds['F']} by F, {binds['G']} by G, {binds['both']} by both)"]
    if skipped:
        notes.append(f"{skipped} chained tensors skipped: a consumer reads only part of the tensor (e.g. embedding gathers)")
    return WPBound(int(total), len(cands), n_forced, binds, {str(k): v for k, v in sorted(by_step.items())}, records, notes)
