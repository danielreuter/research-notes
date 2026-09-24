"""verify-night: verified=accepted labels whose asserter is in the same succession lineage as one of the result's producers
(lanes/*/binding.json "succeeds"); tables.producers() compares names only, so such a label counts as independent there.

    PYTHONPATH=... python lineage_check.py RENDER.json
"""
import json
import sys
from pathlib import Path

from research.store.local import LocalStore
from verity_numerical.bench import tables as T

NOTES = Path.home() / ".research" / "notes" / "lanes"


def lineages():
    parent = {}
    for b in NOTES.glob("*/binding.json"):
        try:
            s = json.loads(b.read_text()).get("succeeds")
        except ValueError:
            continue
        if s:
            parent[b.parent.name] = s
    def root(x):
        seen = set()
        while x in parent and x not in seen:
            seen.add(x)
            x = parent[x]
        return x
    return root, parent


def main():
    render = json.load(open(sys.argv[1]))
    cells = {c["artifact"] for row in render["table2"]["rows"] for slot in ("cells", "committed") for c in row[slot].values() if c}
    root, parent = lineages()
    st = LocalStore()
    rows = st.index.select_artifacts(kind="bench-result/v1")
    hits = []
    for r in rows:
        art = r["id"]
        labs = st.labels(art)
        acc = [l for l in T._labels(labs) if l.key == "verified" and l.value == "accepted"]
        if not acc:
            continue
        meta = st.get_manifest(art).meta or {}
        _, att = T._attempt_of(st, art)
        prod = T.producers(att, labs, meta)
        for l in acc:
            if l.by in prod:
                continue
            same = [p for p in prod if root(p) == root(l.by)]
            if same:
                hits.append((art, l.by, sorted(same), art in cells))
    for art, by, same, cell in hits:
        print(f"{art} verified=accepted by {by}, same lineage as producer(s) {same}{'  <-- TABLE 2 CELL' if cell else ''}")
    print(f"{len(hits)} lineage self-verifications; successions: {parent}")


if __name__ == "__main__":
    main()
