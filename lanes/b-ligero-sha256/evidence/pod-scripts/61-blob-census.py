#!/usr/bin/env python3
"""b-ligero-sha256: which blobs of a store tree artifact are missing from this machine's store objects, and whether the run-dir file
with that path (under TREE) has the blob's content.  With --ingest, copies each matching run-dir file into the store as that blob
(`LocalStore._store_blob`), so `research data push` never has to fetch it from the remote first.
Usage (PYTHONPATH = the pod's research tool): 61-blob-census.py ART TREE [--ingest]"""
import sys
from pathlib import Path

from research.store.local import LocalStore, sha256_file

art, tree = sys.argv[1], Path(sys.argv[2])
ingest = "--ingest" in sys.argv
st = LocalStore(None)
m = st.get_manifest(art)
paths = {f.sha256: f.path for f in (m.payload.files or [])}
missing = matched = ingested = 0
for h, n in m.blobs():
    if st.object_path(h).exists():
        continue
    missing += 1
    p = tree / paths.get(h, "")
    if paths.get(h) and p.is_file() and sha256_file(p)[0] == h:
        matched += 1
        if ingest:
            st._store_blob(p, h)
            ingested += 1
    else:
        print(f"missing and not in {tree}: {h} {paths.get(h)} ({n} B)")
print(f"{art}: {len(list(m.blobs()))} blobs, {missing} not local, {matched} of those match the run dir, {ingested} ingested")
