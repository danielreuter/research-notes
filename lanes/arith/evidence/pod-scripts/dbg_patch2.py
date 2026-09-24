"""arith (diagnostic, never committed): per prove_many pass, log wall / host busy / waited / per-stage busy, the CUDA
allocator's device allocs + retries, and every gc pause over 2 ms, to stderr.

    python dbg_patch2.py TREE      # edits TREE/backends/direct/ligero/pipeline.py in place
"""
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "backends/direct/ligero/pipeline.py"
s = p.read_text()
hook = '''
import gc as _gc, time as _t, sys as _s
_GC_T = [0.0]
def _gc_cb(phase, info):
    if phase == "start":
        _GC_T[0] = _t.perf_counter()
    else:
        dt = _t.perf_counter() - _GC_T[0]
        if dt > 0.002:
            print(f"DBG {_t.perf_counter():.3f} gc gen={info.get('generation')} ms={dt * 1e3:.1f} collected={info.get('collected')}", file=_s.stderr)
_gc.callbacks.append(_gc_cb)
'''
n0 = s.count("def prove_many(")
s = s.replace("def prove_many(", hook + "\n\ndef prove_many(", 1)
old = "    return results, wall\n\n\nSWITCH_INTERVAL"
assert old in s, "return anchor"
s = s.replace(old,
    "    try:\n"
    "        _ms = torch.cuda.memory_stats(device)\n"
    "        _al = (_ms.get('num_device_alloc'), _ms.get('num_device_free'), _ms.get('num_alloc_retries'))\n"
    "    except Exception:\n"
    "        _al = None\n"
    "    print(f\"DBG {_t.perf_counter():.3f} pass wall={wall * 1e3:.1f} busy={busy * 1e3:.1f} waited={waited * 1e3:.1f} "
    "stages={LAST_STATS['stage_busy_ms']} alloc={_al}\", file=_s.stderr)\n" + old, 1)
assert n0 == 1
p.write_text(s)
print("patched", p)
