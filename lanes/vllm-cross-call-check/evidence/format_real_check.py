"""The three smollm2 / llama32 / gemma2 build_step descriptors of art:7e51cdad through the format spec's checks: the JCS domain,
RFC 8785 bytes equal to canonical_json (the digest input), and a strict decode (node forms, table indices, reference spaces)."""
import glob, gzip, hashlib, json, sys, time
sys.path.insert(0, "/tmp/xc/wt-fmt/packages/verity/tests/ir")
from test_format_spec import jcs
from verity.ir import codec, partition_object as PO
from verity_vllm.check.match.program_compare import _registry

out = []
for p in sorted(glob.glob("/tmp/xc/desc/*/build_step/descriptor.json.gz")):
    d = json.loads(gzip.open(p).read())
    nd = {k: v for k, v in d.items() if k != "annotations"}
    t = time.time()
    c = codec.canonical_json(nd)
    r = {"row": p.split("/")[4], "bytes": len(c), "domain": codec.jcs_domain_error(nd), "jcs_equal": jcs(nd) == c,
         "sha256": hashlib.sha256(c).hexdigest(), "program_digest": codec.program_digest(d)}
    D = codec.decode_program(d, _registry())
    r["decoded_gates"] = D.gates
    r["reencoded_equal"] = codec.canonical_json({k: v for k, v in codec.encode_program(D).items() if k != "annotations"}) == c
    r["calls"] = len(PO.calls(D))
    r["seconds"] = round(time.time() - t, 1)
    print(json.dumps(r), flush=True)
    out.append(r)
json.dump(out, open("/tmp/xc/spec/real_check.json", "w"), indent=1)
