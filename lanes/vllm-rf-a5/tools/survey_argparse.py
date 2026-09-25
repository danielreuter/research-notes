"""Which argparse features do the CLI modules use? No verity_vllm import."""
import ast, json, sys, collections
from pathlib import Path

ROOT = Path(sys.argv[1])
al = json.load(open(ROOT / "tests/lint/allowlists/p06_one_cli.json"))["entries"]
files = sorted({e["file"] for e in al if e["kind"] in ("argparse", "main-block")})
kw = collections.Counter()
actions = collections.Counter()
methods = collections.Counter()
nargs = collections.Counter()
types = collections.Counter()
per_file = {}
envdefault = []
positional = []
for f in files:
    src = (ROOT / f).read_text()
    tree = ast.parse(src)
    fm = collections.Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            m = node.func.attr
            if m == "add_argument":
                for k in node.keywords:
                    kw[k.arg] += 1
                    if k.arg == "action":
                        actions[ast.unparse(k.value)] += 1
                    if k.arg == "nargs":
                        nargs[ast.unparse(k.value)] += 1
                    if k.arg == "type":
                        types[ast.unparse(k.value)] += 1
                    if k.arg == "default" and ("environ" in ast.unparse(k.value) or "getenv" in ast.unparse(k.value)):
                        envdefault.append((f, ast.unparse(node)[:160]))
                if node.args and isinstance(node.args[0], ast.Constant) and not str(node.args[0].value).startswith("-"):
                    positional.append((f, ast.unparse(node)[:120]))
            elif m in ("add_mutually_exclusive_group", "add_subparsers", "add_parser", "set_defaults", "error", "parse_known_args",
                       "print_help", "add_argument_group", "parse_args", "print_usage", "format_help", "exit"):
                methods[m] += 1
                fm[m] += 1
        if isinstance(node, ast.Call) and ast.unparse(node.func).endswith("ArgumentParser"):
            for k in node.keywords:
                methods["AP:" + str(k.arg)] += 1
    per_file[f] = dict(fm)
print("kw", kw.most_common())
print("actions", actions.most_common())
print("nargs", nargs.most_common())
print("types", types.most_common())
print("methods", methods.most_common())
print("env defaults:")
for e in envdefault:
    print("  ", e)
print("positional:")
for e in positional:
    print("  ", e)
print("files with subparsers / groups / known / error:")
for f, fm in per_file.items():
    if any(k in fm for k in ("add_subparsers", "add_mutually_exclusive_group", "parse_known_args", "add_argument_group", "error", "set_defaults", "print_help")):
        print("  ", f, fm)
