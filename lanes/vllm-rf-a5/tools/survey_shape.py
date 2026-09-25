"""Shape of each argparse main: where the parser is built, what surrounds parse_args. No verity_vllm import."""
import ast, json, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
al = json.load(open(ROOT / "tests/lint/allowlists/p06_one_cli.json"))["entries"]
files = sorted({e["file"] for e in al if e["kind"] in ("argparse", "main-block")})


def parents(tree):
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            c._parent = n


for f in files:
    src = (ROOT / f).read_text()
    tree = ast.parse(src)
    parents(tree)
    notes = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("ArgumentParser"):
            p = n
            while p is not None and not isinstance(p, (ast.FunctionDef, ast.Module)):
                p = getattr(p, "_parent", None)
            fn = p.name if isinstance(p, ast.FunctionDef) else "<module>"
            sig = ast.unparse(p.args) if isinstance(p, ast.FunctionDef) else ""
            idx = None
            if isinstance(p, ast.FunctionDef):
                body = p.body
                for i, st in enumerate(body):
                    if n in list(ast.walk(st)):
                        idx = i
                pre = [ast.unparse(s)[:70] for s in body[:idx] if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                parse_i = None
                for i, st in enumerate(body):
                    if "parse_args" in ast.unparse(st) or "parse_known_args" in ast.unparse(st):
                        parse_i = i
                        break
                between = []
                if parse_i is not None:
                    for s in body[idx + 1:parse_i]:
                        u = ast.unparse(s)
                        if ".add_argument(" not in u and "add_parser" not in u and "add_subparsers" not in u:
                            between.append(u[:70])
                pl = ast.unparse(body[parse_i])[:90] if parse_i is not None else None
                rets = [ast.unparse(r.value)[:30] if r.value else "None" for r in ast.walk(p) if isinstance(r, ast.Return)]
                notes.append(f"  fn={fn}({sig}) pre={pre} between={between} parse={pl!r} returns={sorted(set(rets))[:6]}")
            else:
                notes.append("  MODULE-LEVEL parser")
    mains = [ast.unparse(n)[:120].replace("\n", " | ") for n in tree.body if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test)]
    print(f)
    for x in notes:
        print(x)
    for m in mains:
        print("  MAIN:", m)
