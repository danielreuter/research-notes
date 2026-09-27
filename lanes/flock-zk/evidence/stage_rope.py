"""Stage a small RoPE (rope-head/d64/neox-bf16) statement for flock-circuit: an input set, the composite circuit, the prover's
and the verifier's instance files."""
import json
import sys
from pathlib import Path

from verity_flock import circuit as FC
from verity_numerical.bench import templates as TM
from verity_numerical.bench.generate import generate
from verity_numerical.bench.input_sets import InputSet

n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
out = Path(sys.argv[2] if len(sys.argv) > 2 else "/home/ubuntu/fzk/rope")
out.mkdir(parents=True, exist_ok=True)
summary = generate(TM.parse_subcircuit_id("rope-head/d64/neox-bf16"), max(n, 4), 20260926, out / "set")
s = InputSet.open(summary["path"])
low = FC.lowering_for_set(s)
info = FC.stage(low, s, 0, n, out / "stage")
print(json.dumps(info, default=str)[:2000])
