"""Check an extracted :class:`OpGraph` against the flattened Verity circuit.

The extractor never expands batches; this module does, on programs small enough to enumerate (a few hundred
thousand gates), and checks that the operator graph is a faithful quotient of the gate graph:

* every non-input gate maps to exactly one op, and the per-op sum of primitive ``.work`` equals ``op.work``;
* the set of *source tensors* (root parameters / producing ops) referenced by an op's gates equals the set of
  ``Edge.src`` of the op;
* the number of distinct external gates each op reads is at most the extractor's (with-repeats) count, and
  equals it whenever every edge is exact and the argument references carry no repeats.

Used by the tests and by the sweep driver's ``--validate`` flag on the exact-solver-scale configs."""

from __future__ import annotations

from verity_ir.defs import PrimitiveDefinition
from verity_ir.layout import Scope, resolve

from accumulation.graph.opgraph import OpGraph, _is_terminal


def _op_key_of_gate(root_scope_chain: list, k_gate: int, acc_spec, n_input_nodes: int) -> tuple:
    """Op key ``(path, node_idx)`` (relative to the algorithm composite) of a gate whose scope chain from the
    root is ``root_scope_chain`` (innermost last) and whose node index in the innermost body is ``k_gate``.
    The lowered root inlines the algorithm body after ``n_input_nodes`` ``Input`` batches, so the first path
    entry is shifted by that count."""
    path = [s.node_idx for s in root_scope_chain[1:]] + [k_gate]  # drop the Root scope itself
    path[0] -= n_input_nodes
    fn = acc_spec
    for depth, k in enumerate(path):
        node = fn.body.nodes[k]
        if node.form == "scan" or _is_terminal(node.fn):
            return (tuple(path[:depth]), k)
        fn = node.fn
    raise AssertionError("gate below no terminal op")


def check_against_flat(bp, g: OpGraph, limit: int = 400_000) -> dict:
    """Raise ``AssertionError`` on mismatch; return summary counters."""
    prog = bp.program
    circ = prog.circuit
    assert circ.size <= limit, f"circuit too large to flatten ({circ.size} gates)"
    acc_spec = prog.fn
    n_input_nodes = len(prog.root.body.nodes) - len(acc_spec.body.nodes)
    assert n_input_nodes >= 0
    # input leaves -> param tensor id
    owner: dict[int, tuple[str, int]] = {}
    for pi, name in enumerate(bp.param_names):
        coll = prog.input_coll(pi)
        for j in range(coll.type.leaves):
            owner[resolve(circ.root_scope, coll.refs[j])] = ("param", g.params[name])
    # non-input gates -> op key
    key_of: dict[int, tuple] = {}
    work: dict[tuple, int] = {}
    for i in range(circ.size):
        if i in owner:
            continue
        gt = circ.gate(i)
        chain = []
        s = gt.scope
        while s is not None:
            chain.append(s)
            s = s.parent
        chain.reverse()
        k_gate = gt.scope.spec.body.node_at(i - gt.scope.offset)
        key = _op_key_of_gate(chain, k_gate, acc_spec, n_input_nodes)
        key_of[i] = key
        work[key] = work.get(key, 0) + int(getattr(gt.prim, "work", 1))
    ops_by_key = {o.key: o for o in g.ops}
    assert set(work) == set(ops_by_key), f"op key sets differ: only-flat={set(work)-set(ops_by_key)} only-graph={set(ops_by_key)-set(work)}"
    for key, w in work.items():
        o = ops_by_key[key]
        assert o.work == w, f"work mismatch for {o.fn_id}: graph {o.work} flat {w}"
    # external sources per op
    ext: dict[tuple, dict[int, set[int]]] = {k: {} for k in work}
    for i, key in key_of.items():
        for od in circ.gate(i).operands:
            if od in owner:
                tid = owner[od][1]
            else:
                ok = key_of[od]
                if ok == key:
                    continue
                tid = ops_by_key[ok].out
            ext[key].setdefault(tid, set()).add(od)
    n_exact_equal = n_edges = 0
    for key, srcs in ext.items():
        o = ops_by_key[key]
        graph_srcs = {e.src: e for e in o.inputs}
        assert set(srcs) == set(graph_srcs), (f"source set mismatch for {o.fn_id}: flat={sorted(srcs)} "
                                             f"graph={sorted(graph_srcs)}")
        for tid, gates in srcs.items():
            e = graph_srcs[tid]
            n_edges += 1
            total = e.leaves_per_copy * o.copies
            assert total >= len(gates), f"{o.fn_id}: edge from {tid} counts {total} < distinct flat {len(gates)}"
            if e.exact and total == len(gates):
                n_exact_equal += 1
    return {"gates": circ.size, "ops": len(g.ops), "edges": n_edges, "edges_exact_equal": n_exact_equal}
