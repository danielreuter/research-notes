"""Rewrite segment-split path literals (``ROOT / "verity_vllm" / "harness" / "x.py"``, ``os.path.join(R, "verity_vllm",
"harness", "x.py")``) with one group's path map.  usage: python splitfix.py REPO GROUP"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SEG = r"""(["'])[\w.\-]+\1"""
SPLIT = re.compile(r"""(["'])verity_vllm\1((?:\s*[/,]\s*(["'])[\w.\-]+\3)+)""")


def main():
    repo = Path(sys.argv[1]).resolve()
    d = json.load(open(f"/tmp/a4-map-{sys.argv[2]}.json"))
    pathmap = d["pathmap"]

    def ren(p):
        best = None
        for k in pathmap:
            if (p == k or p.startswith(k + "/")) and (best is None or len(k) > len(best)):
                best = k
        return p if best is None else pathmap[best] + p[len(best):]

    files = subprocess.run(["git", "-C", str(repo), "ls-files", "integrations/vllm", "tools/research"], capture_output=True,
                           text=True, check=True).stdout.split()
    for f in files:
        if not f.endswith(".py"):
            continue
        p = repo / f
        s = p.read_text(encoding="utf-8")
        if "verity_vllm" not in s:
            continue

        def fix(m):
            q = m.group(1)
            tail = m.group(2)
            segs = re.findall(r"""\s*([/,])\s*(["'])([\w.\-]+)\2""", tail)
            sep = segs[0][0]
            if any(s_[0] != sep for s_ in segs):
                return m.group(0)
            parts = ["verity_vllm", *[s_[2] for s_ in segs]]
            # map the longest prefix that is a known path; keep any trailing segments
            for n in range(len(parts), 1, -1):
                pre = "/".join(parts[:n])
                new = ren(pre)
                if new != pre:
                    newparts = new.split("/") + parts[n:]
                    joiner = " / " if sep == "/" else ", "
                    out = joiner.join(f"{q}{x}{q}" for x in newparts)
                    print(f"  {f}: {'/'.join(parts)} -> {'/'.join(newparts)}")
                    return out
            return m.group(0)

        s2 = SPLIT.sub(fix, s)
        if s2 != s:
            p.write_text(s2, encoding="utf-8")


if __name__ == "__main__":
    main()
