"""agkr-nvf4: cProfile of bench_result.main (host-side cost of the per-round sumcheck plumbing).
python 07_cprof.py STMT_DIR [bench_result args...]"""
import cProfile
import pstats
import sys

import bench_result

pr = cProfile.Profile()
pr.enable()
rc = bench_result.main(sys.argv[1:])
pr.disable()
st = pstats.Stats(pr)
st.sort_stats("tottime").print_stats(45)
st.sort_stats("cumulative").print_callees("_inputs|set_fold")
sys.exit(rc)
