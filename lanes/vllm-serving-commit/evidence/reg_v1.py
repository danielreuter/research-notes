"""registration.json in `verity/registration/v1` (verity_one_stage at 43122fa5, the e2e lane's pin) from a serving-rows window and
serving's pub-N.bin, after serving: the committed bytes don't change.  It checks that `R.served_domain` reproduces every domain
serving bound, then runs the e2e lane's own `R.check` against the verifier's program, query, law, scheme and ports.
usage: reg_v1.py WINDOW_DIR PUB_FILE SET_DIR OUT_JSON"""
import hashlib, json, sys
from pathlib import Path

from verity_numerical.bench.input_sets import InputSet
from verity_one_stage import partition as P, registration as R

wd, pub, set_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
win = json.loads((wd / "window.json").read_text())
v0 = json.loads((wd / "registration.json").read_text())
source = v0["commitment"]["source"]
run, n = source["run"], int(win["n"])
tmpl = InputSet.open(set_dir).subcircuit.definition()
prog, q = P.population_program(tmpl, n), P.template_instance_query(tmpl.id)
part = P.partition(prog, q)
pd = P.digest(part)
fv = win["frame_v3"]
leaves = v0["leaves"]
roots = []
for p in ("x", "cs", "out"):
    dom = R.served_domain(part["program"], pd, p, fv["schemas"][p], leaves[p], run)
    if dom != fv["domain_ids"][p]:
        raise SystemExit(f"served_domain({p}) {dom[:16]} != serving's {fv['domain_ids'][p][:16]}")
    roots.append({"port": p, "root": fv["roots"][p], "leaves": leaves[p], "domain": dom})
law = {"law": "subset", "k": 256}
scheme = v0["commitment"]["scheme"]
leaf_layer = hashlib.sha512(pub.read_bytes()).hexdigest()
rec = R.record(prog, q, law, scheme, roots, source, leaf_layer=leaf_layer)
ports = {r["port"]: {"leaves": r["leaves"], "domain": r["domain"]} for r in roots}
v = R.check(rec, prog, q, law, scheme, ports, leaf_layer=leaf_layer)
out.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(json.dumps({"registration_sha512": R.digest(rec), "check": v.to_json(), "partition": pd, "program": part["program"],
                  "population": rec["population"], "leaf_layer": leaf_layer}, indent=1))
