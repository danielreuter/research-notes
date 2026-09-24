"""``python seeded_run.py <run.py args>``: backends.direct.ligero.run with ``os.urandom`` (the verifier's coins, the ZK mask keys)
replaced by a stream seeded from $URANDOM_SEED, so two runs with the same seed and arguments dump byte-identical proofs iff
their provers are.  COMPARISON ONLY: a seeded run's coins are predictable -- never register one."""
import os
import random
import runpy
import sys
import threading

_rng, _lock = random.Random(int(os.environ["URANDOM_SEED"])), threading.Lock()


def _urandom(n: int) -> bytes:
    with _lock:
        return _rng.randbytes(n)


os.urandom = _urandom
sys.argv = ["backends.direct.ligero.run", *sys.argv[1:]]
runpy.run_module("backends.direct.ligero.run", run_name="__main__", alter_sys=True)
