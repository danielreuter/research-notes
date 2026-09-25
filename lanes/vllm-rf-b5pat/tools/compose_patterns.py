"""Compose observe/fold/patterns/<mod>.py from <mod>.head (docstring + imports) and <mod>.body (split_patterns.py output).

    uvx --python 3.12 python compose_patterns.py SPLITDIR PKGDIR
"""
import sys
from pathlib import Path

SPLIT, PKG = Path(sys.argv[1]), Path(sys.argv[2])
PKG.mkdir(parents=True, exist_ok=True)
for head in sorted(SPLIT.glob("*.head")):
    mod = head.stem
    body = (SPLIT / f"{mod}.body").read_text()
    first = body.lstrip("\n").split("\n", 1)[0]
    sep = "\n\n\n" if first.startswith(("def ", "class ", "@")) else "\n\n"
    text = head.read_text().rstrip("\n") + sep + body.strip("\n") + "\n"
    (PKG / f"{mod}.py").write_text(text)
    print(f"{mod:12s} {text.count(chr(10)):5d} lines")
