"""baseline-jdiff.py with the base run's test ids renamed through the test-file moves (testmap.txt), so a moved test is
compared with itself.   usage: jdiff_moved.py BASE.xml[.gz] HEAD.xml[.gz] [jdiff args]     prints the renamed ids first.
"""
import importlib.util, sys
from pathlib import Path

here = Path(__file__).parent
spec = importlib.util.spec_from_file_location("jdiff", Path.home() / ".research/notes/lanes/vllm-rf-a1/baseline-jdiff.py")
J = importlib.util.module_from_spec(spec)
spec.loader.exec_module(J)

dotted = {}
for line in (here / "testmap.txt").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or not line.split()[0].endswith(".py"):
        continue
    src, dst = line.split()
    name = src.rsplit("/", 1)[1][:-3]
    dotted["tests." + src[:-3].replace("/", ".")] = "tests." + (name if dst == "." else f"{dst.replace('/', '.')}.{name}")


def rename(tid):
    cls, _, rest = tid.partition("::")
    for old, new in dotted.items():
        if cls == old or cls.endswith("." + old):
            return cls[: len(cls) - len(old)] + new + "::" + rest
    return tid


_outcomes = J.outcomes
base_path = sys.argv[1]
renamed = []


def outcomes(path):
    out, reasons = _outcomes(path)
    if path != base_path:
        return out, reasons
    o2, r2 = {}, {}
    for tid in out:
        new = rename(tid)
        if new != tid:
            renamed.append((tid, new))
        o2[new], r2[new] = out[tid], reasons[tid]
    return o2, r2


J.outcomes = outcomes
J.UNSTABLE = frozenset(J.UNSTABLE | {rename(t) for t in J.UNSTABLE})
_main = J.main


def main():
    try:
        return _main()
    finally:
        mods = sorted({(a.split("::")[0], b.split("::")[0]) for a, b in renamed})
        print(f"renamed test ids: {len(renamed)} in {len(mods)} files")
        for a, b in mods:
            print(f"  {a} -> {b}")


sys.exit(main())
