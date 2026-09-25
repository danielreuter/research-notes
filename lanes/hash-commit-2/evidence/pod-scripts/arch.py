import sys
sys.path.insert(0, "/workspace/src/backends/shared")
import cupy as cp
from hash_gpu import frame_v3 as fv3
d = cp.cuda.Device()
print("cc", d.compute_capability, "nvrtc", cp.cuda.nvrtc.getVersion(), "runtime", cp.cuda.runtime.runtimeGetVersion(),
      "fv3_top max_threads_per_block", fv3._fn("sha", "fv3_top").max_threads_per_block)
