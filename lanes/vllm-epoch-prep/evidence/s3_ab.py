"""s3_ab.py PROGRAM_DIR... : the S3 A/B on stored Builds (lane vllm-epoch-prep): `manifest.build` with the four tap policies off (the old
default) and on (S3's), identities by family and the manifest digests; what moves must be the tap families only (norm_scales, the guarded
max's MS class on every attention stream identity, router_softmax / vocab_range where they apply)."""
import sys
from collections import Counter

from verity_vllm.pipeline import manifest as MF

for d in sys.argv[1:]:
    off = MF.build(d)
    on = MF.build(d, norm_scales=True, guarded_max=True, taps=MF.taps_of(True, True))
    fo, fn = Counter(x["family"] for x in off["identities"]), Counter(x["family"] for x in on["identities"])
    key = lambda x: (x["family"], x["step"], x["op_path"], x["output_member"])
    ro = {key(x): x["element_range"] for x in off["identities"]}
    changed = Counter(x["family"] for x in on["identities"] if key(x) in ro and ro[key(x)] != x["element_range"])
    print(f"{d}: identities {len(off['identities'])} -> {len(on['identities'])}; added by family {dict(fn - fo)}; removed {dict(fo - fn)}; "
          f"ranges changed by family {dict(changed)}; digest {off['manifest_digest'][:12]} -> {on['manifest_digest'][:12]}; "
          f"query keys added {sorted(set(on['query']) - set(off['query']))}", flush=True)
