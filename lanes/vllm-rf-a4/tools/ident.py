"""Code-identity digests of the tree on sys.path (run from the tree root with its PYTHONPATH): code_identity (= the hot Commit
key and the TP tree of record), the research Tools' closure, construction_version, registry_version.   usage: ident.py REPO_ROOT"""
import hashlib, importlib, json, sys


def mod(*names):
    for n in names:
        try:
            return importlib.import_module(n)
        except ImportError:
            continue
    raise ImportError(names)


root = sys.argv[1]
sid = mod("verity_vllm.pipeline.source_identity", "verity_vllm.harness.source_identity")
rt = mod("verity_vllm.pipeline.research_tools", "verity_vllm.harness.research_tools")
bld = mod("verity_vllm.pipeline.build", "verity_vllm.harness.derive_step")
hot = mod("verity_vllm.pipeline.hot", "verity_vllm.harness.hot_commit")
prov = mod("verity_vllm.program.frontend.provenance")
from verity_vllm.program.frontend.rules.vllm_bindings import VLLM_BINDING_RULES

ci = sid.code_identity(root)
out = {"module_paths": {"source_identity": sid.__name__, "research_tools": rt.__name__, "build": bld.__name__, "hot": hot.__name__},
       "code_identity": ci, "hot_commit_key": hot.code_identity(root)["sha256"]}
for name in dir(rt):
    t = getattr(rt, name)
    if hasattr(t, "closure_manifest") and not isinstance(t, type):
        m = t.closure_manifest(root)
        out.setdefault("research_tools_closure", {})[name] = {
            "files": len(m), "sha256": hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
cv = bld.construction_version(VLLM_BINDING_RULES)
out["construction_version"] = {"sources_sha256": cv["sources_sha256"], "files": [f["file"] for f in cv["files"]]}
rv = prov.registry_version()
out["registry_version"] = {"digest": rv.get("digest"), "sources": rv.get("sources") or rv.get("source_sha256")}
print(json.dumps(out, indent=1, default=str))
