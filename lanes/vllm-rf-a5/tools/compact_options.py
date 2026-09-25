"""Join wrapped `option(...)` fields and options-class docstrings onto one line each (the files' own long-line style).

    python3 compact_options.py FILE...
"""
import ast
import sys


def compact(path: str) -> int:
    src = open(path).read()
    lines = src.split("\n")
    tree = ast.parse(src)
    spans = []          # (start, end) 1-based inclusive line spans to join
    drop = []           # 1-based blank lines to drop
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        fields = [b for b in node.body if isinstance(b, ast.AnnAssign) and isinstance(b.value, ast.Call)
                  and getattr(b.value.func, "id", None) == "option"]
        if not fields:
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            d = body[0]
            if d.end_lineno > d.lineno:
                spans.append((d.lineno, d.end_lineno))
            nxt = d.end_lineno + 1
            if nxt <= len(lines) and not lines[nxt - 1].strip():
                drop.append(nxt)
        for f in fields:
            if f.end_lineno > f.lineno:
                spans.append((f.lineno, f.end_lineno))
    if not spans and not drop:
        return 0
    removed = set(drop)
    new = {}
    for a, b in spans:
        first = lines[a - 1].rstrip()
        rest = [lines[i - 1].strip() for i in range(a + 1, b + 1)]
        new[a] = " ".join([first] + rest)
        removed.update(range(a + 1, b + 1))
    out = []
    for i, ln in enumerate(lines, 1):
        if i in removed:
            continue
        out.append(new.get(i, ln))
    text = "\n".join(out)
    ast.parse(text)
    open(path, "w").write(text)
    return len(lines) - len(out)


for p in sys.argv[1:]:
    print(p, -compact(p))
