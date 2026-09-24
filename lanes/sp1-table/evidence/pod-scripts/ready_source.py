"""sp1-table (pod): make /workspace/research/src/<sha>/ READY from a `git archive --format=tar HEAD` streamed over ssh, with
the research tool's own manifest and READY document (what `research run --source` does, whose laptop launcher holds the
229 MB archive in memory and is SIGKILLed by the laptop disk guardian below 3.5 GB free).

    ready_source.py TAR SHA TREE LAPTOP_ARCHIVE_SHA256
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, "/workspace/research/tool/fdc139c9183a52e8")
from research.remote import READY_FILE, _ready_doc, archive_manifest  # noqa: E402

tar_path, sha, tree, laptop_sha256 = sys.argv[1:5]
tar = open(tar_path, "rb").read()
man = archive_manifest(tar)
if man["archive_sha256"] != laptop_sha256:
    sys.exit(f"archive sha256 {man['archive_sha256']} is not the laptop's {laptop_sha256}")
dest = f"/workspace/research/src/{sha}"
if os.path.exists(dest):
    sys.exit(f"{dest} exists; not touching it")
partial = f"{dest}.partial-streamed"
os.makedirs(partial)
subprocess.run(["tar", "-xf", tar_path, "-C", partial], check=True)
got = {os.path.relpath(os.path.join(r, f), partial) for r, _, fs in os.walk(partial) for f in fs}
if got != set(man["files"]):
    sys.exit(f"extracted file set differs from the archive manifest: {len(got ^ set(man['files']))} paths")
doc = _ready_doc(sha, tree, man, "archive-sha256+file-manifest")
doc["launcher"] = "Daniels-MacBook-Pro.local: git archive | ssh, manifest and READY built on vy-sp1-a100 by research.remote"
with open(os.path.join(partial, READY_FILE), "w") as f:
    json.dump(doc, f)
os.rename(partial, dest)
os.remove(tar_path)
print(json.dumps({k: doc[k] for k in ("identity", "tree", "archive_sha256", "files", "bytes", "verified")}))
