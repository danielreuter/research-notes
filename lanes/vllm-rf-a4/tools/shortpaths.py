"""Find (or rewrite) old short paths (`harness/card.py`, `tp/worker.py`: verity_vllm-relative, no prefix) left in text.

usage: python shortpaths.py REPO [--apply]

Uses the pathmaps of every group (/tmp/a4-map-*.json).  Only `*.py` / `*.sh` / `*.md` / `*.json` / `*.txt` files under
integrations/vllm are scanned; lint allowlists are skipped.  A hit is a short path preceded by a non-path character.
With --apply, hits inside comments, docstrings and markdown are rewritten; other string hits are only reported.
"""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

GROUPS = ("pipeline", "engine", "program", "query", "observe", "kernels", "commit", "acquire", "check", "properties",
          "collectives")


def load_map() -> dict[str, str]:
    """Compose the per-group pathmaps (short form) in order: old short path -> final short path."""
    comp: dict[str, str] = {}
    for g in GROUPS:
        pm = json.load(open(f"/tmp/a4-map-{g}.json"))["pathmap"]
        step = {k.removeprefix("verity_vllm/"): v.removeprefix("verity_vllm/") for k, v in pm.items()}
        for k, v in list(comp.items()):
            comp[k] = apply(step, v)
        for k, v in step.items():
            comp.setdefault(k, v)
    return {k: v for k, v in comp.items() if k != v}


def apply(m: dict[str, str], p: str) -> str:
    best = None
    for k in m:
        if (p == k or p.startswith(k + "/")) and (best is None or len(k) > len(best)):
            best = k
    return p if best is None else m[best] + p[len(best):]


def main() -> None:
    repo = Path(sys.argv[1]).resolve()
    do = "--apply" in sys.argv
    m = load_map()
    # only file-like keys (with a suffix) and directory keys that end in '/' in the text
    keys = sorted(m, key=len, reverse=True)
    pat = re.compile(r"(?<![\w/.\-])(" + "|".join(re.escape(k) for k in keys) + r")(?=[/`'\")\s:,;.\]]|$)")
    files = subprocess.run(["git", "-C", str(repo), "ls-files", "integrations/vllm"], check=True, capture_output=True,
                           text=True).stdout.splitlines()
    total = 0
    for f in files:
        if f.startswith("integrations/vllm/tests/lint/allowlists/") or Path(f).suffix not in (".py", ".sh", ".md", ".json", ".txt"):
            continue
        p = repo / f
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits = list(pat.finditer(text))
        if not hits:
            continue
        prose = prose_spans(text, f)
        out, pos = [], 0
        for h in hits:
            old = h.group(1)
            if old.endswith("/") is False and "." not in old.rsplit("/", 1)[-1] and text[h.end():h.end() + 1] != "/":
                # a bare directory mention (`tp/`, `harness`) is only rewritten when followed by '/'
                continue
            new = apply(m, old)
            inp = any(a <= h.start() < b for a, b in prose)
            line = text.count("\n", 0, h.start()) + 1
            total += 1
            print(f"{'P' if inp else 'S'} {f}:{line}: {old} -> {new}")
            if do and inp:
                out.append(text[pos:h.start()] + new)
                pos = h.end()
        if do and out:
            out.append(text[pos:])
            p.write_text("".join(out), encoding="utf-8")
    print("hits", total)


def prose_spans(text: str, f: str) -> list[tuple[int, int]]:
    if f.endswith(".md") or f.endswith(".txt"):
        return [(0, len(text))]
    if f.endswith(".sh"):
        spans, off = [], 0
        for ln in text.splitlines(keepends=True):
            i = ln.find("#")
            if i >= 0:
                spans.append((off + i, off + len(ln)))
            off += len(ln)
        return spans
    if not f.endswith(".py"):
        return []
    starts = [0]
    for ln in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(ln))
    spans = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return []
    prev = None
    for t in toks:
        s = starts[t.start[0] - 1] + t.start[1]
        e = starts[t.end[0] - 1] + t.end[1]
        if t.type == tokenize.COMMENT:
            spans.append((s, e))
        elif t.type == tokenize.STRING and (prev is None or prev.type in (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT,
                                                                          tokenize.DEDENT)) and t.string.lstrip("rbuRBU").startswith(('"""', "'''")):
            spans.append((s, e))
        if t.type not in (tokenize.COMMENT, tokenize.NL):
            prev = t
    return spans


if __name__ == "__main__":
    main()
