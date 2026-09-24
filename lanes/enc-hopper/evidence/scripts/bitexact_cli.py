"""Lane enc-hopper: bit-exactness through the CLI (run.py bench-vu --dump-dir) with DETERMINISTIC randomness (os.urandom
replaced by a seeded SHAKE stream, as hostphase's bitexact.py) -- for the paths bitexact.py does not drive: the Ampere
BF16 relation (vu.py on the frozen instance set) and fp4-nvf4 (fp4/chain.py).

usage: bitexact_cli.py --tree DIR --seed N -- <run.py argv ...>       (argv includes --dump-dir)
"""
import argparse
import hashlib
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--tree", required=True)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("argv", nargs=argparse.REMAINDER)
args = ap.parse_args()
argv = args.argv[1:] if args.argv and args.argv[0] == "--" else args.argv

_calls = [0]
_seed = args.seed.to_bytes(8, "little")


def _urandom(n: int) -> bytes:
    _calls[0] += 1
    return hashlib.shake_256(b"enc-hopper-bitexact|" + _seed + _calls[0].to_bytes(8, "little")).digest(n)


os.urandom = _urandom
os.chdir(args.tree)
sys.path.insert(0, args.tree)
for sub in ("packages/verity/src", "backends/numerical/python"):
    sys.path.insert(0, os.path.join(args.tree, sub))
from backends.direct.ligero.run import main  # noqa: E402

print(f"tree={args.tree} seed={args.seed} argv={argv}")
sys.exit(main(argv))
