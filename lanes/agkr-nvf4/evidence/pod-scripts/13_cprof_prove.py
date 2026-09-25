"""agkr-nvf4: cProfile of one prove (the last rep) inside bench_result: host cost by function (tottime; methods that
block on the device -- .cpu / .tolist / item / synchronize -- carry the device wait).
python 13_cprof_prove.py STMT_DIR [bench_result args...]"""
import cProfile
import pstats
import sys

import bench_result
from gpu import prover

orig = prover.prove
calls = [0]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1


def prove(*a, **k):
    calls[0] += 1
    if calls[0] < 1 + REPS:
        return orig(*a, **k)
    pr = cProfile.Profile()
    pr.enable()
    r = orig(*a, **k)
    pr.disable()
    st = pstats.Stats(pr)
    st.sort_stats("tottime").print_stats(40)
    st.sort_stats("cumulative").print_stats(60)
    st.print_callers("built-in method torch.tensor|method 'cpu'|method 'tolist'|_cuda_synchronize")
    return r


prover.prove = prove
if __name__ == "__main__":
    sys.exit(bench_result.main(sys.argv[1:]))
