"""flock-pure-instances/v1 for fp4-nvf4 (k = 1536, 864-byte NVFP4 rows), flock-gpu-link test inputs.

  python3 /tmp/inst_fp4.py N out.bin [blake3|sha256]

VUs are B-Ligero's synthetic NVFP4 set (ligero.fp4.chain.instances_fp4: seed 20260922, edge families cycling per VU, model-
recorded accumulators); rows are verity.commitments.rowleaf.nvfp4_row_bytes (768 code bytes, then 96 scale bytes); the
statement commits them as blake3-keyed/row-nvfp4/v1 or sha256/row-nvfp4/v1 row leaves and a u32 word leaf of the final
FP32 accumulator, bound like flock-backend's instances.statement.
"""
import json
import sys
import types

sys.modules.setdefault("torch", types.ModuleType("torch"))
sys.path[:0] = ["/tmp/main/packages/verity/src", "/tmp/main/backends/direct", "/tmp/main/backends/numerical/python"]
import numpy as np  # noqa: E402
from ligero import auth, hashauth  # noqa: E402
from ligero.fp4.chain import INSTANCE_SEED, instances_digest, instances_fp4  # noqa: E402
from verity.commitments.frame_v3 import FrameV3, Port, WordLeaf, tree_levels  # noqa: E402
from verity.commitments.indexed import RangeIndexedDomain  # noqa: E402
from verity.commitments.merkle import CommitmentDomain  # noqa: E402
from verity.commitments.rowleaf import (ROLE_W, ROLE_X, SCHEMA_BLAKE3_ROW_NVFP4, SCHEMA_SHA256_ROW_NVFP4,  # noqa: E402
                                        blake3_row_nvfp4_digest, nvfp4_row_bytes, sha256_row_nvfp4_digest)
from verity_numerical.bench import contract  # noqa: E402

K = 1536


def main():
    n, out, scheme = int(sys.argv[1]), sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "blake3")
    data = instances_fp4(n)
    rows = {0: [], 1: []}
    for A, B, _, _ in data:
        for r, M in ((0, A), (1, B)):
            rows[r].append(nvfp4_row_bytes([int(c) for s in M for c in s[:64]], [int(c) for s in M for c in s[64:68]]))
    accs = np.asarray([d[2] for d in data], dtype="<u4")
    y = [int(a[-1]) for a in accs]
    rs = SCHEMA_SHA256_ROW_NVFP4 if scheme == "sha256" else SCHEMA_BLAKE3_ROW_NVFP4
    dig = sha256_row_nvfp4_digest if scheme == "sha256" else blake3_row_nvfp4_digest
    ysch, ybytes = hashauth.word_schema(32)
    manifest = instances_digest(n)
    schemas = {"a": rs, "b": rs, "y": ysch}
    bind = {t: hashauth.binding_digest(dataset=contract.NVFP4_INSTANCES_DATASET, tier=contract.NVFP4_INSTANCES_TIER,
                                       manifest_sha256=manifest, lo=0, hi=n, K=K, tree=t, schema=schemas[t]) for t in "aby"}
    dom = {t: CommitmentDomain(bind[t], auth.OWNER[t], RangeIndexedDomain(0, n)) for t in "aby"}
    fv = FrameV3({"y": Port(dom["y"], WordLeaf(ysch, ybytes))})
    leaves = {}
    for t, r, role in (("a", 0, ROLE_X), ("b", 1, ROLE_W)):
        leaves[t] = [dom[t].leaf(i, i, rs, dig([int(c) for s in (data[i][r]) for c in s[:64]], [int(c) for s in data[i][r] for c in s[64:68]], role))
                     for i in range(n)]
    leaves["y"] = [fv.tree_leaf("y", i, fv.leaf_layout("y", i).digest(v.to_bytes(ybytes, "big"))) for i, v in enumerate(y)]
    roots = {t: tree_levels(dom[t], leaves[t])[-1][0].hex() for t in "aby"}
    ref = {"dataset": contract.NVFP4_INSTANCES_DATASET, "tier": contract.NVFP4_INSTANCES_TIER, "range": [0, n],
           "manifest_sha256": manifest, "seed": INSTANCE_SEED}
    header = {"format": "flock-pure-instances/v1", "relation": "fp4-nvf4", "vus": n, "k": K, "word_bits": 4, "units": 24,
              "row_bytes": 864, "epilogue": False, "instances": ref, "roots": roots,
              "domain_ids": {t: dom[t].domain_id.hex() for t in "aby"}, "bindings": {t: bind[t].hex() for t in "aby"},
              "owners": dict(auth.OWNER), "schemas": schemas, "y_bytes": ybytes}
    with open(out, "wb") as f:
        f.write(json.dumps(header, sort_keys=True).encode() + b"\n")
        f.write(b"".join(rows[0]))
        f.write(b"".join(rows[1]))
        f.write(accs.tobytes())
        f.write(np.asarray(y, dtype="<u4").tobytes())
        f.write(np.asarray(y, dtype="<u4").tobytes())
    print(json.dumps({"relation": "fp4-nvf4", "vus": n, "scheme": scheme, "roots": roots}))


if __name__ == "__main__":
    main()
