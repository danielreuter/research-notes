# agkr-fp8: bench_result.main under faulthandler (every thread's stack to stderr every $FH_EVERY s): py-spy cannot attach
# in the RunPod container (no SYS_PTRACE).
import faulthandler, os, sys
sys.path.insert(0, "/workspace/src/backends/gkr")
faulthandler.dump_traceback_later(int(os.environ.get("FH_EVERY", "30")), repeat=True, file=sys.stderr)
import bench_result
sys.exit(bench_result.main(sys.argv[1:]))
