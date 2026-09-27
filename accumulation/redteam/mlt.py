"""Updated matrix multiplications `M_{L,T}` (NCI draft): closed-form bounds on the minimum novel input, checked
against the exact solver on small gate-level instances (cycle-allowed divisions, theta = empty).

    PYTHONPATH=. .venv/bin/python -m accumulation.redteam.mlt [--time-limit 120]

Circuit: layers l = 1..L, positions t = 1..T, weights W_l (d x d, b_w bytes/entry), activations b_a bytes.
Output (l, t, i) is a chain of d fused multiply-add gates over k; gate (l, t, i, k) reads W_l[i, k], a^{l-1}_t[k]
and the previous partial sum.  Variants:
  * `literal`: a^0_t are Input gates (d per position, b_a bytes each) -- the draft's definition.
  * `token`: a^0_t[k] = e_k(token_t), one gate per coordinate reading a b_tok-byte token Input.

Closed form, per MAC, with Gamma in MACs:
    phi(Gamma) = min_{0 < W <= W_max} ( b_w W / Gamma + b_a d / W ),   W_max = weights of all layers,
i.e. 2 sqrt(b_w b_a d / Gamma) while the optimal tile is shallower than the network, else
b_w W_max / Gamma + b_a d / W_max (one IU spans the whole depth).  Lower bound (proof in
results/EXISTING_RESULTS_NCI.md, section 12):
    literal:  I* >= max( T L d^2 min(phi, b_a / d),  L d^2 b_w + T d b_a )
    token:    I* >= T (L-1) d^2 min(phi_{L-1}, b_a / d) - T d b_a + T b_tok + d^2 b_w
Upper bound: the best explicit rectangle tiling (m consecutive layers x t positions per IU, all rows), built and
priced with `exact.solve.partition_cost` / `is_legal`.  The exact I* (HiGHS, cycle-allowed) must lie between."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

from accumulation.exact.solve import is_legal, make_flat, partition_cost

RESULTS = Path(__file__).resolve().parents[1] / "results"


@dataclass(frozen=True)
class Inst:
    d: int
    L: int
    T: int
    b_w: int = 1
    b_a: int = 1
    variant: str = "literal"
    b_tok: int = 1

    def name(self) -> str:
        return f"M(d={self.d},L={self.L},T={self.T}; b_w={self.b_w},b_a={self.b_a}" + (f",tok={self.b_tok})" if self.variant == "token" else ")")


def build(inst: Inst):
    """FlatCircuit plus index maps: mac[(l, t, i, k)] -> gate, a0[(t, k)] -> gate (token variant)."""
    d, L, T = inst.d, inst.L, inst.T
    work, width, ops, role = [], [], [], []

    def add(w, bits, operands, r):
        work.append(w)
        width.append(bits)
        ops.append(tuple(operands))
        role.append(r)
        return len(work) - 1

    W = {(l, i, k): add(0, 8 * inst.b_w, (), "accumulated") for l in range(1, L + 1) for i in range(d) for k in range(d)}
    act: dict[tuple[int, int, int], int] = {}
    a0: dict[tuple[int, int], int] = {}
    if inst.variant == "literal":
        for t in range(T):
            for k in range(d):
                act[(0, t, k)] = add(0, 8 * inst.b_a, (), "token")
    else:
        tok = {t: add(0, 8 * inst.b_tok, (), "token") for t in range(T)}
        for t in range(T):
            for k in range(d):
                a0[(t, k)] = act[(0, t, k)] = add(1, 8 * inst.b_a, (tok[t],), None)
    mac: dict[tuple[int, int, int, int], int] = {}
    for l in range(1, L + 1):
        for t in range(T):
            for i in range(d):
                prev = None
                for k in range(d):
                    o = [W[(l, i, k)], act[(l - 1, t, k)]] + ([prev] if prev is not None else [])
                    prev = mac[(l, t, i, k)] = add(1, 8 * inst.b_a, o, None)
                act[(l, t, i)] = prev
    outs = [act[(L, t, i)] for t in range(T) for i in range(d)]
    return make_flat(work, width, ops, role, outs), mac, a0


def phi(b_w: float, b_a: float, d: float, W_max: float, Gamma: float) -> float:
    """Per-MAC floor: min over held weights W <= W_max of b_w W / Gamma + b_a d / W."""
    W = min(math.sqrt(b_a * d * Gamma / b_w), W_max)
    return b_w * W / Gamma + b_a * d / W


def lower(inst: Inst, Gamma: int) -> float:
    d, L, T, bw, ba = inst.d, inst.L, inst.T, inst.b_w, inst.b_a
    if inst.variant == "literal":
        return max(T * L * d * d * min(phi(bw, ba, d, L * d * d, Gamma), ba / d), L * d * d * bw + T * d * ba)
    if L == 1:
        return d * d * bw + T * inst.b_tok
    main = T * (L - 1) * d * d * min(phi(bw, ba, d, (L - 1) * d * d, Gamma), ba / d) - T * d * ba
    return max(main + T * inst.b_tok + d * d * bw, L * d * d * bw + T * inst.b_tok)


def rectangle_upper(inst: Inst, Gamma: int):
    """Best rectangle tiling (m layers x t positions per IU; a^0 gates ride with the bottom block): (cost, m, t)."""
    flat, mac, a0 = build(inst)
    best = None
    for m in range(1, inst.L + 1):
        for t in range(1, inst.T + 1):
            assign = {}
            for (l, pos, i, k), g in mac.items():
                assign[g] = ((l - 1) // m, pos // t)
            for (pos, k), g in a0.items():
                assign[g] = (0, pos // t)
            ids = {v: j for j, v in enumerate(sorted(set(assign.values())))}
            assign = {g: ids[v] for g, v in assign.items()}
            ok, _ = is_legal(flat, assign, None, None, Gamma, acyclic=False)
            if ok:
                c = partition_cost(flat, assign)
                if best is None or c < best[0]:
                    best = (c, m, t)
    return best


def cpsat_min_input(flat, Gamma: int, hint: dict[int, int] | None, time_limit: float, workers: int = 8) -> dict:
    """Exact min over all divisions (cycles allowed) of sum_R bytes(in(R)) with work(R) <= Gamma, by CP-SAT.

    Two IUs whose works sum to <= Gamma can be merged without increasing the cost (in(R1 u R2) is a subset of
    in(R1) u in(R2)), so some optimum has at most one IU of work <= Gamma/2 and hence <= 2 N / Gamma + 1 IUs."""
    from ortools.sat.python import cp_model

    gates = list(flat.gates)
    N = sum(flat.work[g] for g in gates)
    K = 2 * N // Gamma + 1
    m = cp_model.CpModel()
    x = {(g, r): m.NewBoolVar(f"x{g}_{r}") for g in gates for r in range(K)}
    for g in gates:
        m.AddExactlyOne(x[(g, r)] for r in range(K))
    for r in range(K):
        m.Add(sum(flat.work[g] * x[(g, r)] for g in gates) <= Gamma)
    cons = flat.consumers()
    obj, y = [], {}
    for v, cs in cons.items():
        if flat.is_input[v] and v not in flat.nonfixed_inputs:
            continue
        for r in range(K):
            yv = y[(v, r)] = m.NewBoolVar(f"y{v}_{r}")
            for g in cs:
                if flat.is_input[v]:
                    m.AddImplication(x[(g, r)], yv)
                else:
                    m.AddBoolOr([x[(g, r)].Not(), x[(v, r)], yv])
            obj.append(flat.bytes_of(v) * yv)
    m.Minimize(sum(obj))
    # symmetry (restricted growth): gate j may open IU r only if some earlier gate already uses IU r-1
    for j, g in enumerate(gates):
        for r in range(1, K):
            if r > j:
                m.Add(x[(g, r)] == 0)
            else:
                m.Add(x[(g, r)] <= sum(x[(h, r - 1)] for h in gates[:j]))
    if hint:
        labels = {}
        for g in gates:                                      # relabel the hint so it respects the symmetry rule
            labels.setdefault(hint[g], len(labels))
        if len(labels) <= K:
            for g in gates:
                for r in range(K):
                    m.AddHint(x[(g, r)], int(labels[hint[g]] == r))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"I": None, "status": s.StatusName(st)}
    assign = {g: next(r for r in range(K) if s.Value(x[(g, r)])) for g in gates}
    ok, why = is_legal(flat, assign, None, None, Gamma, acyclic=False)
    assert ok, why
    c = partition_cost(flat, assign)
    assert c == round(s.ObjectiveValue()), (c, s.ObjectiveValue())
    return {"I": c, "optimal": st == cp_model.OPTIMAL, "bound": math.ceil(s.BestObjectiveBound() - 1e-6),
            "n_ius": len(set(assign.values())), "K": K, "seconds": round(s.WallTime(), 1)}


def rect_assignment(inst: Inst, m: int, t: int) -> dict[int, int]:
    _, mac, a0 = build(inst)
    assign = {g: ((l - 1) // m, pos // t) for (l, pos, i, k), g in mac.items()}
    assign.update({g: (0, pos // t) for (pos, k), g in a0.items()})
    ids = {v: j for j, v in enumerate(sorted(set(assign.values())))}
    return {g: ids[v] for g, v in assign.items()}


def check(inst: Inst, Gamma: int, time_limit: float) -> dict:
    flat, _, _ = build(inst)
    lb = lower(inst, Gamma)
    ub = rectangle_upper(inst, Gamma)
    rec = {"inst": inst.name(), "variant": inst.variant, "d": inst.d, "L": inst.L, "T": inst.T, "b_w": inst.b_w, "b_a": inst.b_a,
           "gates": flat.n_gates, "Gamma": Gamma, "LB": lb, "U_rect": ub and ub[0], "rect_m_t": ub and (ub[1], ub[2])}
    rec.update(cpsat_min_input(flat, Gamma, ub and rect_assignment(inst, ub[1], ub[2]), time_limit))
    if rec.get("I") is None:
        rec["LB<=I*"] = None
    elif lb <= rec["bound"] + 1e-9:
        rec["LB<=I*"] = True                                 # proven: LB <= solver bound <= I*
    else:
        rec["LB<=I*"] = False if rec["optimal"] or lb > rec["I"] + 1e-9 else None   # None: not proven either way
    rec["I*<=U"] = None if rec.get("I") is None or ub is None else rec["I"] <= ub[0]
    return rec


CASES: list[tuple[Inst, list[int]]] = [
    # d = 1: the layer x position trade-off alone (tile shallower than the network, and whole-depth tiles)
    (Inst(1, 4, 4), [2, 4, 8]),
    (Inst(1, 4, 6), [4, 6, 12]),
    (Inst(1, 6, 4), [3, 6, 9, 12]),
    (Inst(1, 3, 8), [3, 6, 12]),
    (Inst(1, 4, 6, b_w=2, b_a=1), [4, 8, 12]),
    (Inst(1, 4, 6, b_w=1, b_a=2), [4, 8, 12]),
    # d = 2: multiply-add chains (splitting outputs or the contraction is available to the solver)
    (Inst(2, 2, 4, b_w=1, b_a=4), [4, 8, 16]),
    (Inst(2, 3, 2, b_w=1, b_a=4), [6, 12]),
    (Inst(2, 2, 4, b_w=1, b_a=2), [4, 8, 16]),
    (Inst(2, 2, 3, b_w=1, b_a=1), [4, 8]),
    # token-derived inputs (a^0 = e(token), 1-byte token)
    (Inst(1, 4, 4, variant="token", b_tok=1), [4, 8]),
    (Inst(1, 3, 6, variant="token", b_tok=1), [4, 8]),
    (Inst(2, 2, 3, b_w=1, b_a=4, variant="token", b_tok=1), [10, 20]),
]


# --- read-off at the draft's Kimi-K3 calibration -----------------------------------------------------------------
# Draft: one 1M-token Kimi-K3 session = 2.1e11 T + 7.4e5 T^2 gates; alpha = 32 bits / 2.1e11 gates.  2.1e11 = 2 x 104B
# activated parameters, so a gate is one multiply or one add: 2 gates per MAC, and Gamma in MACs is half the gate count.
KIMI_GAMMA_GATES = 2.1e11 * 1e6 + 7.4e5 * 1e12
ALPHA = 32 / 2.1e11
KIMI = {"L": 93, "d": 7168, "W_layer": 30.2e9, "h_layer": 1.13e9}   # arXiv 2607.24653: 2.78T total, 104.2B active, 93 layers
WIDTHS = {"bf16": (16.0, 16.0), "MXFP4 weights, bf16 cut": (4.25, 16.0)}
STEP_OVER_FWD = 3.0        # training-step gates / forward gates per token at short context (our 8K calibration: 3.04 to 3.15)


def per_position(L: int, W_layer: float, h: float, A: float, b_w: float, b_a: float, Gamma: float, b_first: float) -> dict:
    """Closed-form novel input per position (bits) for a chain of L layers, W_layer weights and h MACs per position per
    layer, cut width A between layers; b_first = entry cost of the bottom block (A b_a literal, b_tok token-derived).
    U: best tiling into blocks of m layers (last block shorter), each IU a block x Gamma/(block MACs per position)
    positions.  LB: the proof's bound, n_{R,t} <= W_R / rho with rho = W_layer / h (rho = 1 is a theorem for dense
    layers; rho > 1 assumes every IU needs all experts of the layers it covers -- balanced routing)."""
    rho = W_layer / h
    best = None
    for m in range(1, L + 1):
        blocks = [m] * (L // m) + ([L % m] if L % m else [])
        cost = sum(b_w * s * s * W_layer * h / Gamma for s in blocks) + b_first + (len(blocks) - 1) * A * b_a
        if best is None or cost < best[0]:
            best = (cost, m, Gamma / (m * h))
    if b_first == A * b_a:                                   # literal inputs
        lb = L * h * min(phi(b_w, b_a * rho, A, L * W_layer, Gamma), b_a / A)
    else:
        lb = (L - 1) * h * min(phi(b_w, b_a * rho, A, (L - 1) * W_layer, Gamma), b_a / A) - A * b_a + b_first
    gates = 2 * L * h
    return {"U_bits": best[0], "LB_bits": lb, "m": best[1], "positions_per_IU": best[2], "gates_per_position": gates,
            "s_U": best[0] / gates / ALPHA, "s_LB": lb / gates / ALPHA}


def readoff() -> list[dict]:
    G = KIMI_GAMMA_GATES / 2
    k = KIMI
    rows = []
    specs = [
        ("draft's M_{L,T} as written: 93 square 7168x7168 layers, a^0 = d-wide novel input", k["L"], k["d"] ** 2, k["d"] ** 2, "literal"),
        ("same, a^0 derived from the 32-bit token", k["L"], k["d"] ** 2, k["d"] ** 2, "token"),
        ("Kimi-K3 matmul weights, routing fully clusterable (rho = 1: IU holds only active weights)", k["L"], k["h_layer"], k["h_layer"], "token"),
        ("Kimi-K3 matmul weights, balanced routing (rho = 26.7: IU holds all experts of its layers)", k["L"], k["W_layer"], k["h_layer"], "token"),
    ]
    for label, L, W_layer, h, variant in specs:
        for wname, (b_w, b_a) in WIDTHS.items():
            b_first = k["d"] * b_a if variant == "literal" else 32.0
            r = per_position(L, W_layer, h, k["d"], b_w, b_a, G, b_first)
            rows.append({"circuit": label, "widths": wname, **r})
    return rows


def markdown(check_rows: list[dict], ro: list[dict]) -> str:
    md = ["### 12a. Exact optimum vs closed form (small instances)", "",
          "| d | L | T | b_w / b_a (B) | a^0 | Gamma (MACs) | gates | closed-form LB | exact I* | proven optimal | best rectangle (m x t) | I* / LB | formula regime |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in check_rows:
        W_max = (r["L"] - (r["variant"] == "token")) * r["d"] ** 2
        regime = phi(r["b_w"], r["b_a"], r["d"], W_max, r["Gamma"]) <= r["b_a"] / r["d"] + 1e-12
        proven = "yes" if r["optimal"] else f"no (bound {r['bound']})"
        m, t = r["rect_m_t"]
        md.append(f"| {r['d']} | {r['L']} | {r['T']} | {r['b_w']} / {r['b_a']} | {r['variant']} | {r['Gamma']} | {r['gates']} | "
                  f"{r['LB']:.2f} | {r['I']} | {proven} | {r['U_rect']} ({m} x {t}) | {r['I'] / r['LB']:.2f} | {'yes' if regime else 'no'} |")
    md += ["", "### 12b. Read-off at the draft's Kimi-K3 Gamma", "",
           "| Circuit | b_w / b_a (bits) | optimal IU: layers x positions | novel bits per position: LB / U | slowdown NCI/alpha: LB / U | "
           "alpha_C = size(M) / size(step) | training rho >= alpha_C x LB |", "|---|---|---|---|---|---|---|"]
    for r in ro:
        bw, ba = WIDTHS[r["widths"]]
        a_C = r["gates_per_position"] / (STEP_OVER_FWD * 2.1e11)
        md.append(f"| {r['circuit']} | {bw:g} / {ba:g} | {r['m']} x {r['positions_per_IU']:.2g} | {r['LB_bits']:,.3g} / {r['U_bits']:,.3g} | "
                  f"{r['s_LB']:,.0f}x / {r['s_U']:,.0f}x | {a_C:.3f} | {a_C * r['s_LB']:,.0f}x |")
    return "\n".join(md) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--readoff", action="store_true", help="only the Kimi-K3 read-off (reuse results/mlt_check.json)")
    args = ap.parse_args()
    ro = readoff()
    (RESULTS / "mlt_readoff.json").write_text(json.dumps(ro, indent=1))
    for r in ro:
        print(f"{r['circuit'][:70]:<70} {r['widths']:<24} m={r['m']:>3} pos/IU={r['positions_per_IU']:.2e} "
              f"U={r['U_bits']:.3g} b/pos LB={r['LB_bits']:.3g}  s_U={r['s_U']:,.0f}x s_LB={r['s_LB']:,.0f}x")
    if args.readoff:
        out = json.loads((RESULTS / "mlt_check.json").read_text())
    else:
        out = []
        for inst, gammas in CASES:
            for G in gammas:
                r = check(inst, G, args.time_limit)
                out.append(r)
                print(json.dumps(r), flush=True)
        (RESULTS / "mlt_check.json").write_text(json.dumps(out, indent=1))
    (RESULTS / "mlt.md").write_text(markdown(out, ro))


if __name__ == "__main__":
    main()
