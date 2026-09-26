"""Lower flock-backend's total_proto (total tc_dot16, bf16-ampere) as flock-unit-io/v1 (2^14-row slot allowed)."""
import sys
sys.path[:0] = ["/tmp/total", "/tmp/fb2/backends/flock/python", "/workspace/packages/verity/src"]
import total_proto as T
from verity_flock import lowering as L, unit as U, fp

def build(y16=True):
    C = U.Circuit()
    x = C.input("x", 256); w = C.input("w", 256); c = C.input("c", 32)
    out = T.tc_total(C, c, [x[i * 16:(i + 1) * 16] for i in range(16)], [w[i * 16:(i + 1) * 16] for i in range(16)])
    C.output("c_out", out)
    if y16:
        C.output("y16", fp.f32_to_bf16(C, out, 0x7FFF))
    return C

def netlist(y16=True, relation="bf16-ampere"):
    L.K_LOG = 14
    orig = U.unit
    U.unit = lambda *a, **k: build(y16)
    try:
        pipe = L.PIPES["bf16-ampere"]
        _, ra, rb, const, outs = L._layout(pipe)
        head = [L.FORMAT, relation, len(ra), const, 544, len(L.IN_COLS), *L.IN_COLS, len(outs), *outs]
        lines = [" ".join(map(str, head))] + [" ".join(map(str, [len(a), *a, len(b), *b])) for a, b in zip(ra, rb)]
        return "\n".join(lines) + "\n", len(ra)
    finally:
        U.unit = orig

if __name__ == "__main__":
    for y in (True, False):
        C = build(y); live = C.live()
        ands = sum(1 for v in range(len(C.kind)) if v in live and C.kind[v] == "and")
        text, rows = netlist(y)
        print("y16" if y else "no-y16", "ands", ands, "rows", rows, "fits 2^13", rows <= 8192)
    text, rows = netlist(True)
    open("/tmp/total/net-bf16-ampere-total.txt", "w").write(text)
