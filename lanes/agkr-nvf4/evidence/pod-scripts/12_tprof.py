"""agkr-nvf4: torch.profiler over one prove (the last rep) inside bench_result; prints the top CUDA kernels and the
top host ops.  python 12_tprof.py STMT_DIR [bench_result args...]"""
import sys

import torch
from torch.profiler import ProfilerActivity, profile

import bench_result
from gpu import prover

orig = prover.prove
calls = [0]
REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 1


def prove(*a, **k):
    calls[0] += 1
    if calls[0] < 1 + REPS:
        return orig(*a, **k)
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True, with_stack=True) as p:
        r = orig(*a, **k)
        torch.cuda.synchronize()
    ka = p.key_averages()
    print(ka.table(sort_by="cuda_time_total", row_limit=45, max_name_column_width=70), flush=True)
    print(ka.table(sort_by="self_cpu_time_total", row_limit=30, max_name_column_width=70), flush=True)
    kb = p.key_averages(group_by_input_shape=True)
    print(kb.table(sort_by="cuda_time_total", row_limit=40, max_name_column_width=40, max_shapes_column_width=90), flush=True)
    ks = p.key_averages(group_by_stack_n=6)
    rows = [e for e in ks if e.key in ("aten::copy_", "aten::index", "aten::fill_", "aten::index_put_", "aten::sum", "aten::mm")]
    rows.sort(key=lambda e: -e.device_time_total)
    for e in rows[:25]:
        print(f"{e.key} {e.device_time_total / 1e3:.2f} ms x{e.count}", " | ".join(e.stack[:6]), flush=True)
    return r


prover.prove = prove
if __name__ == "__main__":
    sys.exit(bench_result.main(sys.argv[1:]))
