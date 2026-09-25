import ast, hashlib, subprocess, sys

ROOT = "integrations/vllm/"


def show(rev, rel):
    return subprocess.run(["git", "show", f"{rev}:{ROOT}{rel}"], check=True, capture_output=True).stdout


def sources(rev):
    tree = ast.parse(show(rev, "verity_vllm/pipeline/build.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "_CONSTRUCTION_SOURCES":
            return ast.literal_eval(node.value)
    raise SystemExit("no _CONSTRUCTION_SOURCES")


for rev in sys.argv[1:]:
    h = hashlib.sha256()
    for rel in sources(rev):
        b = show(rev, rel)
        h.update(rel.encode() + b"\0" + b + b"\0")
    print(rev, h.hexdigest())
