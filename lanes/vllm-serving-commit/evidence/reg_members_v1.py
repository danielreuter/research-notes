"""A multi-member `verity/registration/v1` record (verity_one_stage's record(), the one-stage lane's A4 rules) from a served window and
serving's M0 files, after serving: one record for all members, roots named `<descriptor id>/<port>`, `leaf_layer` = SHA-512 of the
canonical map descriptor id -> SHA-512 of the member's pub file, `window` = the served source.  It checks that `served_domain`
reproduces every domain serving bound, then runs the lane's own `R.check`, as its a4.py does.
usage: reg_members_v1.py WINDOW_DIR M0_FILES_DIR OUT_JSON LAW SET...   (sets in the partition's member order)"""
import hashlib, json, sys
from pathlib import Path

from verity.ir.codec import canonical_json
from verity_numerical.bench.input_sets import InputSet
from verity_one_stage import draw as D, partition as P, registration as R

wd, files, out, law_s = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
sets = sys.argv[5:]
win = json.loads((wd / "window.json").read_text())
v0 = json.loads((wd / "registration.json").read_text())
source, run = v0["commitment"]["source"], v0["commitment"]["source"]["run"]
defs = [InputSet.open(s).subcircuit.definition() for s in sets]
mems = win["members"]
program = P.mixed_population_program([(d, int(m["n"])) for d, m in zip(defs, mems, strict=True)])
query = P.template_instances_query(defs)
part = P.partition(program, query)
pd = P.digest(part)
if pd != v0["partition_digest"]:
    raise SystemExit(f"the verifier's partition {pd[:16]} is not the served window's {v0['partition_digest'][:16]}")
roots, want, publics = [], {}, {}
for k, (d, m) in enumerate(zip(defs, mems, strict=True)):
    tid = P.template_id(d)
    if tid != m["template"]:
        raise SystemExit(f"member {k}: {tid} != served {m['template']}")
    for port, schema in m["frame_v3"]["schemas"].items():
        name = f"{tid}/{port}"
        leaves = v0["leaves"][name]
        dom = R.served_domain(part["program"], pd, name, schema, leaves, run)
        if dom != m["frame_v3"]["domain_ids"][port]:
            raise SystemExit(f"served_domain({name}) {dom[:16]} != serving's {m['frame_v3']['domain_ids'][port][:16]}")
        roots.append({"port": name, "root": m["frame_v3"]["roots"][port], "leaves": leaves, "domain": dom})
        want[name] = {"leaves": leaves, "domain": dom}
    publics[tid] = hashlib.sha512((files / f"m{k}-pub-{m['n']}.bin").read_bytes()).hexdigest()
leaf_layer = hashlib.sha512(canonical_json(publics)).hexdigest()
law = D.parse_law(law_s)
rec = R.record(program, query, law, v0["commitment"]["scheme"], roots, source, leaf_layer=leaf_layer)
v = R.check(rec, program, query, law, v0["commitment"]["scheme"], want, leaf_layer=leaf_layer)
out.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(json.dumps({"registration_sha512": R.digest(rec), "check": v.to_json(), "partition": pd, "program": part["program"],
                  "population": rec["population"], "leaf_layer": leaf_layer, "roots": len(roots)}, indent=1))
