"""D11: every Program digest a weights-of-record check can compare, by length, across the fetched records trees."""
import glob, gzip, json, os, re, sys
from collections import Counter
root = sys.argv[1]
lens = Counter()
short = []

def note(where, v):
    s = str(v)
    lens[len(s)] += 1
    if len(s) != 64:
        short.append((where, s))

for f in glob.glob(os.path.join(root, "**", "weights_of_record*.json"), recursive=True):
    try:
        r = json.load(open(f))
    except Exception as e:
        print("unreadable", f, e); continue
    rel = os.path.relpath(f, root)
    if r.get("program_digest") is not None:
        note(rel + ":program_digest", r["program_digest"])
    ors = r.get("of_record_set")
    if isinstance(ors, dict):
        for x in ors.get("program_digests") or []:
            note(rel + ":of_record_set.program_digests", x)
        for x in ors.get("manifest_digests") or []:
            note(rel + ":of_record_set.manifest_digests", x)
        for c in ors.get("components") or []:
            if c.get("program_digest"):
                note(rel + ":of_record_set.components.program_digest", c["program_digest"])
for f in glob.glob(os.path.join(root, "**", "manifest.json"), recursive=True):
    if os.path.getsize(f) > 400_000_000:
        print("skip huge", f); continue
    try:
        m = json.load(open(f))
    except Exception as e:
        print("unreadable", f, e); continue
    rel = os.path.relpath(f, root)
    if m.get("program_digest") is not None:
        note(rel + ":program_digest", m["program_digest"])
    for x in m.get("component_digests") or []:
        note(rel + ":component_digests", x)
    for c in (m.get("components") or {}).values():
        if isinstance(c, dict) and c.get("program_digest"):
            note(rel + ":components.program_digest", c["program_digest"])
# the weights pin as recorded by the Commit (runs.jsonl) and the --program-digest on the Commit's command line
for f in glob.glob(os.path.join(root, "**", "runs.jsonl"), recursive=True):
    rel = os.path.relpath(f, root)
    for ln in open(f):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        wp = (r.get("commit") or {}).get("weights_pin") or {}
        if wp.get("program_digest") is not None:
            note(rel + ":weights_pin.program_digest", wp["program_digest"])
        for x in wp.get("of_record_set") or []:
            note(rel + ":weights_pin.of_record_set", x)
        if wp.get("program_of_record") is not None:
            lens["program_of_record=" + str(wp.get("program_of_record"))] += 1
for f in glob.glob(os.path.join(root, "**", "commit.log"), recursive=True) + glob.glob(os.path.join(root, "**", "*.cmd"), recursive=True):
    rel = os.path.relpath(f, root)
    for m in re.finditer(r"--program-digest[ =](\S+)", open(f, errors="replace").read()):
        note(rel + ":--program-digest", m.group(1).strip("'\""))
print("lengths:", dict(lens))
print("non-64:", len(short))
for w, s in short[:40]:
    print("  ", w, s)

# revisions (SYNTHESIS D11 also names the 10-character revision match; reported, not changed in this lane)
revs = Counter()
for f in glob.glob(os.path.join(root, "**", "weights_of_record*.json"), recursive=True):
    r = json.load(open(f))
    e = ((r.get("checkpoint") or {}).get("entry") or {})
    if e.get("revision") is not None:
        revs["record.checkpoint.entry.revision len=%d" % len(str(e["revision"]))] += 1
for f in glob.glob(os.path.join(root, "**", "workload.json"), recursive=True):
    try:
        w = json.load(open(f))
    except Exception:
        continue
    if isinstance(w, dict) and w.get("tokenizer_revision") is not None:
        revs["workload.tokenizer_revision len=%d" % len(str(w["tokenizer_revision"]))] += 1
print("revisions:", dict(revs))
src = Counter(w.split(":", 1)[1] if ":" in w else w for w, _ in [])
