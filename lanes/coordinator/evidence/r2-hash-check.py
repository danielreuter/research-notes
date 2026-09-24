"""Which large local research files are in R2 byte-for-byte (direct hash check, not the laptop catalog).

For every file >= MIN bytes under ~/.research/store/objects and ~/.research/runs: sha256 + md5 locally (streamed), HEAD
objects/sha256/<sha256> on R2, compare size and ETag (single-part md5, or the multipart ETag recomputed from the local file
with the part size in the remote's .parts.json sidecar).  Writes results.tsv: status, bytes, path.
"""
import hashlib, json, os, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projects/verity-main-wt/cli/tools/research/src"))
from research.store.remote import load_remote  # noqa: E402
from research.store.remote_s3 import multipart_etag, parts_of, sidecar_key  # noqa: E402

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 1 << 20
H = Path.home() / ".research"
out = Path("/tmp/coord-evict/results.tsv")


def files():
    for root in (H / "store/objects", H / "runs"):
        for dp, _, fns in os.walk(root):
            for fn in fns:
                p = Path(dp) / fn
                try:
                    if p.stat().st_size >= MIN and not p.is_symlink():
                        yield p
                except OSError:
                    pass


def digests(p: Path):
    s, m = hashlib.sha256(), hashlib.md5(usedforsecurity=False)
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            s.update(chunk)
            m.update(chunk)
    return s.hexdigest(), m.hexdigest()


def part_etag(p: Path, part: int) -> str:
    md5s = []
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(part), b""):
            md5s.append(hashlib.md5(chunk, usedforsecurity=False).hexdigest())
    return multipart_etag(md5s)


remote = load_remote(H / "store.toml")


def check(p: Path):
    size = p.stat().st_size
    sha, md5 = digests(p)
    key = f"objects/sha256/{sha}"
    h = remote.head(key)
    if h is None:
        return "MISSING", size, p
    if h.get("bytes") != size:
        return "SIZE-MISMATCH", size, p
    et = h.get("etag")
    if et and parts_of(et) is None:
        return ("OK" if et == md5 else "ETAG-MISMATCH"), size, p
    if et:
        with tempfile.TemporaryDirectory() as td:
            sc = Path(td) / "sc.json"
            try:
                remote.get(sidecar_key(key), sc)
                part = json.loads(sc.read_text())["part_bytes"]
            except Exception as e:  # noqa: BLE001
                return f"NO-SIDECAR({type(e).__name__})", size, p
        return ("OK" if part_etag(p, part) == et else "ETAG-MISMATCH"), size, p
    return "NO-ETAG", size, p


with ThreadPoolExecutor(8) as ex, open(out, "w") as o:
    for st, size, p in ex.map(check, files()):
        o.write(f"{st}\t{size}\t{p}\n")
print("done", out)
