"""Run a script with torch's current CUDA stream at the device's greatest priority: the pre-fix profile's stand-in for the
review's ``main_priority = "greatest"`` on #564 at 9acf562b, whose tree has no such switch.  Every kernel vLLM and the
Pearl-C main lane launch from this thread goes to that stream, and #564's side stream stays at priority 0, the least.

  python prio.py SCRIPT ARGS...

Writes $RESEARCH_RUN_DIR/stream.json: the priority range, the stream's priority and handle, and the raw handles the first
calls of torch's current-stream accessor returned (which is where the device run reads its stream).
"""
import atexit
import json
import os
import runpy
import sys
from pathlib import Path

import torch

least, greatest = torch.cuda.Stream.priority_range()
stream = torch.cuda.Stream(priority=greatest)
seen: set[int] = set()
original = torch._C._cuda_getCurrentRawStream
calls = [0]


def watched(device):
    raw = original(device)
    seen.add(raw)
    calls[0] += 1
    if calls[0] >= 5000:
        torch._C._cuda_getCurrentRawStream = original
    return raw


def record():
    out = os.environ.get("RESEARCH_RUN_DIR")
    doc = {"priority_range": {"least": least, "greatest": greatest}, "stream_priority": stream.priority,
           "stream": stream.cuda_stream, "raw_streams_seen": sorted(seen), "calls_watched": calls[0],
           "only_the_greatest_stream": seen == {stream.cuda_stream}}
    print("prio.py: " + json.dumps(doc), flush=True)
    if out:
        Path(out, "stream.json").write_text(json.dumps(doc, indent=1))


torch._C._cuda_getCurrentRawStream = watched
atexit.register(record)
sys.argv = sys.argv[1:]
with torch.cuda.stream(stream):
    runpy.run_path(sys.argv[0], run_name="__main__")
