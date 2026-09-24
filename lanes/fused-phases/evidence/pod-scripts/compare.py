"""``compare.py PRE_DIR POST_DIR``: the dumped proofs of two seeded runs (proofs/manifest.json: per rep / sub-batch the proof's
sha256, the statement bytes) -- IDENTICAL iff every entry's proof and statement bytes agree -- and their t.total."""
import hashlib
import json
import sys
from pathlib import Path


def entries(d: Path) -> dict:
    man = json.loads((d / "proofs" / "manifest.json").read_text())
    return {(e["rep"], e["sub"]): (e["proof_sha256"], hashlib.sha256((d / "proofs" / e["stmt"]).read_bytes()).hexdigest())
            for e in man["files"]}


def total(d: Path) -> float:
    r = json.loads((d / "result.json").read_text())
    return next(m["value"] for m in r["measurements"] if m["name"] == "t.total")


pre, post = Path(sys.argv[1]), Path(sys.argv[2])
a, b = entries(pre), entries(post)
diff = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
print(f"{pre.name} vs {post.name}: {len(a)} / {len(b)} proofs, "
      f"{'IDENTICAL' if not diff and a else 'DIFFER at ' + str(diff[:5])}; t.total {total(pre):.4f} -> {total(post):.4f}")
sys.exit(0 if not diff and a else 1)
