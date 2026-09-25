"""Code-identity pins of one tree: registry_version(), ref_vocab_digest(), every Vocabulary.version (all registry modules imported).
usage: PYTHONPATH=<tree>/integrations/vllm:<tree>/packages/verity/src python pins.py OUT.json"""
import importlib
import json
import pkgutil
import sys

import verity.ml.gemm, verity.ml.kernels, verity.ml.prims, verity.ml.scalar  # noqa: E401, F401
from verity_vllm.program import registry

failed = {}
for m in sorted(m.name for m in pkgutil.walk_packages(registry.__path__, registry.__name__ + ".")):
    try:
        importlib.import_module(m)
    except Exception as e:  # noqa: BLE001
        failed[m] = f"{type(e).__name__}: {e}"[:300]
from verity_vllm.program.frontend.provenance import registry_version
from verity_vllm.program.frontend.rules import vocab as V
from verity_vllm.program.registry import ref_prims as R

out = {"import_failed": failed, "registry_version": registry_version()["digest"], "ref_vocab_digest": R.ref_vocab_digest(),
       "vocabularies": {k: v.version for k, v in sorted(vars(V).items()) if isinstance(v, V.Vocabulary)}}
json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
