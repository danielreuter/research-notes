#!/usr/bin/env python3
"""proofs-n2-hill on vy-nebius-2: run the hill-climb lanes' items on infra's reserved 16-core slots (stdlib only).

    python3 n2h.py loop              tmux proofs-n2-hill; log feed.log; stop: touch /workspace/verity-guest/hill/STOP
    python3 n2h.py job ITEM          one attempt of a taken item on its slot, started through vy-provers (infra's scope on the
                                     prover cores): by the fill runner for a GPU item, by the loop for a 0-GPU one and for a GPU
                                     item's CPU pre-stage
    python3 n2h.py affinity CPUS     the other processes that may run on CPUS and how busy CPUS are (JSON)
    python3 n2h.py allow SECONDS     exit 0 if a job of that expected wall may be placed now, else print why and exit 1

Lanes write items to vy-nebius-1 /workspace/jobs/ready-n2/<lane>/*.json, in the format of node 1's ready items ({"tree", "env":
{"CMD", "QUESTION", ...}, "resources": {...: {"cpus", "memory", "gpus"}}}, optional "expected_s"). The loop takes one only when
a slot is free and the window rules allow it, moves it to /workspace/jobs/proofs-n2-hill/taken/<lane>/ on node 1, copies its
tree (by commit) and the lane's prover binary and stage-cache entries for its dtype and K to node 2, then runs it on one slot of
RANGE (128-191, infra's prover cores, four 16-core slices): a GPU item first as a 0-GPU pre-stage (the same CMD with
STAGE_ONLY=1: a cache hit in seconds, else it stages on the CPU, never on the GPU), then through the fill runner (owner proofs,
project verity, gpus=1, on= the slot's NUMA node's GPUs). Every attempt runs in `vy-provers` with VY_PROVERS_CPUS= its slot, so
its scope cannot leave the slot, and 74-gemm-hill.sh holds the slot's lock under /workspace/jobs/slices. Each attempt's run dir
(what a node-1 run writes, plus n2.json: host, cpuset, scope, affinity checks, question, commit, GPU) goes back to node 1
/workspace/jobs/proofs-n2-hill/runs/<run id>/, and a line to points.jsonl there; custody.sh, on an agent VM, puts each one into
the evidence store.

Rules (proofs, 2026-10-01): at most one job per slot; nothing placed from 20 min before a booked window (fill/windows) until it
ends, or while the runner reports a timed window running or waiting; nothing whose expected wall reaches a window or 14:50Z; no
node-1 traffic while node 1's /workspace is offline (12:40-12:55Z); nothing new once node 2's /workspace is 55% full. A
preempted attempt is moved aside and re-run, never reported. Node 2 has no unprivileged network namespaces (AppArmor), so every
job's IPv4 loopback traffic goes to its slot's own address (n2h_loopback.so, N2H_LOOPBACK=127.77.<slot+1>.1, ports unchanged):
74-gemm-hill.sh's fixed ports 7720/7721, which node 1's pods each have to themselves, never meet another slot's.
"""
from __future__ import annotations

import fcntl
import json
import math
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

H = Path(os.environ.get("N2H_DIR", "/workspace/verity-guest/hill"))
FILL = Path(os.environ.get("FILL_DIR", "/workspace/pouw/fill"))
N1 = "vy-n1"
N1_READY = "/workspace/jobs/ready-n2"
N1_OUT = "/workspace/jobs/proofs-n2-hill"
LANE = "proofs-n2-hill"
OWNER = "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4"           # proofs (@proofs), whose worker this is
HOST = "vy-nebius-2"
END = datetime(2026, 10, 1, 14, 50, tzinfo=timezone.utc).timestamp()
LEAD_S, MARGIN_S = 20 * 60, 120
N1_OFFLINE = (datetime(2026, 10, 1, 12, 38, tzinfo=timezone.utc).timestamp(), datetime(2026, 10, 1, 12, 57, tzinfo=timezone.utc).timestamp())
DISK_STOP = 55.0
SLOT = 16
PY = "/workspace/jobs/cache/python/cpython-3.12.14-linux-x86_64-gnu/bin/python3.12"
VY_PROVERS = "/usr/local/bin/vy-provers"
SLICE_LOCKS = "/workspace/jobs/slices"
CUDA_TK = str(H / "cuda-root/usr/local/cuda-13.3")
EVERY_S, LOG_EVERY_S = 15, 300
DEFS = {"bf16": "GemmCoordinate_v2", "e4m3": "GemmCoordinateE4m3_v1", "nvf4": "GemmCoordinateNvf4_v1", "mxf4": "GemmCoordinateMxf4_v1"}
#: expected walls on node 1 (dispatch log, 98669b9 / 5fac5f0 trees, statements cached): a GPU point, a 0-GPU stage job
GPU_S = {2048: 300, 4096: 360, 8192: 480, 16384: 900}
STAGE_S = {2048: 600, 4096: 900, 8192: 1300, 16384: 2400}
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15"]


def now() -> float:
    return time.time()


def iso(t: float | None = None) -> str:
    return datetime.fromtimestamp(now() if t is None else t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp(t: float | None = None) -> str:
    return datetime.fromtimestamp(now() if t is None else t, timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def log(**kw) -> None:
    with open(H / "feed.log", "a") as f:
        f.write(json.dumps({"utc": iso(), **kw}, default=str) + "\n")


def cpulist(s: str) -> list[int]:
    out: list[int] = []
    for part in s.strip().split(","):
        if part:
            lo, _, hi = part.partition("-")
            out.extend(range(int(lo), int(hi or lo) + 1))
    return out


def span(c: list[int]) -> str:
    return f"{c[0]}-{c[-1]}" if c == list(range(c[0], c[-1] + 1)) else ",".join(map(str, c))


# ---------------------------------------------------------------- items (one JSON file each, read-modify-write under a lock)

class Items:
    def __init__(self) -> None:
        (H / "items").mkdir(parents=True, exist_ok=True)
        self.lock = H / "items" / ".lock"

    def path(self, i: str) -> Path:
        return H / "items" / f"{i}.json"

    def get(self, i: str) -> dict:
        return json.loads(self.path(i).read_text())

    def all(self) -> list[dict]:
        out = []
        for p in sorted((H / "items").glob("*.json")):
            try:
                out.append(json.loads(p.read_text()))
            except (OSError, ValueError):
                pass
        return out

    def update(self, i: str, fn) -> dict:
        with open(self.lock, "a") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            p = self.path(i)
            d = json.loads(p.read_text()) if p.exists() else {}
            fn(d)
            tmp = p.with_name(f".{p.name}.{os.getpid()}.tmp")
            tmp.write_text(json.dumps(d, indent=1, default=str))
            os.replace(tmp, p)
            return d


ITEMS = Items()


def set_state(i: str, state: str, why: str | None = None, **kw) -> dict:
    def f(d):
        d["state"], d["why"] = state, why
        d.update(kw)
        d.setdefault("history", []).append({"utc": iso(), "state": state, "why": why})
    return ITEMS.update(i, f)


# ---------------------------------------------------------------- windows, placement, disk

def status() -> dict:
    try:
        head = (FILL / "status.txt").read_text().splitlines()[0]
    except (OSError, IndexError):
        return {"timed": True, "waiting": True, "line": "no status.txt"}
    return {"timed": "timed True" in head, "waiting": "window waiting True" in head, "line": head[:200]}


def booked() -> list[tuple[float, float, str]]:
    out = []
    try:
        lines = (FILL / "windows").read_text().splitlines()
    except OSError:
        return out
    for ln in lines:
        body, _, who = ln.partition("#")
        f = body.split()
        try:
            t = datetime.fromisoformat(f[0].replace("Z", "+00:00")).timestamp()
            out.append((t, t + 60 * float(f[1] if len(f) > 1 else 30), who.strip()))
        except (IndexError, ValueError):
            continue
    return out


def allow(expected_s: float, t: float | None = None) -> str | None:
    """None if a job of this expected wall may be placed at t, else why not."""
    t = now() if t is None else t
    if t + expected_s > END:
        return f"would run past 14:50Z (expected {expected_s:.0f} s)"
    st = status()
    if st["timed"] or st["waiting"]:
        return f"the fill runner reports a window: {st['line'][:120]}"
    for s, e, who in booked():
        if t >= e:
            continue
        if t >= s - LEAD_S:
            return f"20 min before or inside the window at {iso(s)} ({who}), until {iso(e)}"
        if t + expected_s + MARGIN_S > s:
            return f"expected {expected_s:.0f} s would reach the window at {iso(s)} ({who})"
    return None


def disk_pct() -> float:
    s = os.statvfs("/workspace")
    return 100.0 * (1 - s.f_bavail / s.f_blocks)


def n1_offline(t: float | None = None) -> bool:
    t = now() if t is None else t
    return N1_OFFLINE[0] <= t < N1_OFFLINE[1]


# ---------------------------------------------------------------- slots

def slots() -> list[dict]:
    """The reserved range (RANGE, one line such as 64-127) split into 16-core slots, each with its NUMA node, local GPUs and loopback."""
    try:
        line = (H / "RANGE").read_text().split("#")[0].strip()
    except OSError:
        return []
    if not line:
        return []
    c = sorted(set(cpulist(line)))
    out = []
    for k in range(0, len(c) - SLOT + 1, SLOT):
        cs = c[k:k + SLOT]
        numa = 0 if cs[-1] <= 95 else 1 if cs[0] >= 96 else None
        # any free GPU, as node 1's scheduler places them without regard to socket (r20261001-052527-2ac1: slice 160-175 on
        # NUMA 1, GPU 0 on NUMA 0); an item's "on" pins it, and each record has the GPU's NUMA node
        out.append({"index": len(out), "cpus": span(cs), "numa": numa, "gpus": None, "loopback": f"127.77.{len(out) + 1}.1"})
    return out


# ---------------------------------------------------------------- affinity: who else may run on a set of cores

def _proc(pid: str) -> dict | None:
    try:
        with open(f"/proc/{pid}/status") as f:
            st = f.read()
        with open(f"/proc/{pid}/cgroup") as f:
            cg = f.read().strip().split("::", 1)[-1]
        return {"pid": int(pid), "name": re.search(r"Name:\s*(.*)", st).group(1), "uid": int(re.search(r"Uid:\s*(\d+)", st).group(1)),
                "ppid": int(re.search(r"PPid:\s*(\d+)", st).group(1)), "cpus_allowed": re.search(r"Cpus_allowed_list:\s*(\S+)", st).group(1),
                "cgroup": cg}
    except (OSError, AttributeError):
        return None


def _n2h_item(pid: int) -> str | None:
    try:
        with open(f"/proc/{pid}/environ", "rb") as f:
            for kv in f.read().split(b"\0"):
                if kv.startswith(b"N2H_ITEM="):
                    return kv[9:].decode(errors="replace")
    except OSError:
        pass
    return None


def _tree(root: int) -> set[int]:
    kids: dict[int, list[int]] = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open(f"/proc/{d}/stat") as f:
                    ppid = int(f.read().rsplit(")", 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(d))
            except (OSError, ValueError, IndexError):
                pass
    out, todo = set(), [root]
    while todo:
        p = todo.pop()
        if p not in out:
            out.add(p)
            todo.extend(kids.get(p, []))
    return out


def _busy(cpus: set[int]) -> float:
    t = 0
    with open("/proc/stat") as f:
        for ln in f:
            if ln[:3] == "cpu" and ln[3].isdigit():
                name, *v = ln.split()
                if int(name[3:]) in cpus:
                    t += sum(map(int, v)) - int(v[3]) - int(v[4])
    return t / os.sysconf("SC_CLK_TCK")


def affinity(cpus_s: str, mine_root: int | None = None, sample_s: float = 3.0, item: str | None = None) -> dict:
    """Every user-space process outside `mine_root`'s tree whose affinity reaches CPUS, and CPUS's busy cores over sample_s
    seconds. Kernel threads (children of kthreadd, per-CPU by design) are only counted; pid 1 (init.scope, affinity of every
    CPU) is listed as broad; this loop's own jobs on other slots (N2H_ITEM in their environment) are listed apart. Clean: no
    other process at all."""
    cpus = set(cpulist(cpus_s))
    every = set(range(os.cpu_count() or 1))
    mine = _tree(mine_root) if mine_root else {os.getpid()}
    others, broad, n2h, kthreads = [], [], [], 0
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) in mine:
            continue
        p = _proc(d)
        if p is None or not set(cpulist(p["cpus_allowed"])) & cpus:
            continue
        if p["pid"] == 2 or p["ppid"] == 2:
            kthreads += 1
            continue
        it = _n2h_item(p["pid"])
        if it is not None and it != item:
            n2h.append({**p, "n2h_item": it})
        elif p["pid"] == 1 and p["cgroup"] == "/init.scope" and set(cpulist(p["cpus_allowed"])) == every:
            broad.append(p)
        else:
            others.append(p)
    b0, t0 = _busy(cpus), time.monotonic()
    time.sleep(sample_s)
    busy = (_busy(cpus) - b0) / (time.monotonic() - t0)
    return {"utc": iso(), "cpus": cpus_s,
            "checked": "every /proc/<pid>/status Cpus_allowed_list against these cores, this job's own process tree excluded, kernel "
                       f"threads counted apart; /proc/stat busy cores over {sample_s:.0f} s",
            "others": others[:50], "others_n": len(others), "n2h_other_slots": n2h[:50], "broad": broad, "kernel_threads": kthreads,
            "busy_cores": round(busy, 3), "clean": not others}


# ---------------------------------------------------------------- node-1 I/O

def n1(cmd: str, timeout: int = 120, input_: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(SSH + [N1, cmd], capture_output=True, text=True, timeout=timeout, input=input_)


def rsync(src: str, dst: str, *extra: str, timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(["rsync", "-a", "-e", " ".join(SSH), *extra, src, dst], capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- preparing an item

def parse_cmd(cmd: str) -> dict:
    kv = dict(re.findall(r"(?<![\w$])([A-Z_][A-Z0-9_]*)=(\S+)", cmd))
    return kv


def expected(item: dict, cmd: str, gpus: int) -> float:
    if item.get("expected_s"):
        return float(item["expected_s"])
    kv = parse_cmd(cmd)
    k = int(kv.get("K", "16384")) if kv.get("K", "").isdigit() else 16384
    if kv.get("STAGE_ONLY") == "1" or not gpus:
        return STAGE_S.get(k, 2400)
    return GPU_S.get(k, 900)


def tree_dir(item_tree: str) -> tuple[Path, dict]:
    """The node-1 tree, copied to node 2 once per commit: trees/<name>@<commit12>[+<dirty digest>]."""
    r = n1(f"cat {shlex.quote(item_tree)}/.research-source.json")
    if r.returncode:
        raise RuntimeError(f"tree {item_tree}: no .research-source.json on node 1 ({r.stderr.strip()[:200]})")
    src = json.loads(r.stdout)
    tag = (src.get("commit") or "nocommit")[:12] + (f"+{(src.get('dirty_digest') or 'dirty')[:8]}" if src.get("dirty") else "")
    dst = H / "trees" / f"{Path(item_tree).name}@{tag}"
    if (dst / ".n2h-complete").exists():
        return dst, src
    inc = H / "trees" / f".incoming-{dst.name}-{os.getpid()}"
    for _ in range(3):
        p = rsync(f"{N1}:{item_tree}/", f"{inc}/", "--delete")
        if p.returncode:
            raise RuntimeError(f"rsync {item_tree}: {p.stderr.strip()[:300]}")
        if json.loads((inc / ".research-source.json").read_text()) == src == json.loads(n1(f"cat {shlex.quote(item_tree)}/.research-source.json").stdout):
            (inc / ".n2h-complete").write_text(iso() + "\n")
            if dst.exists():
                subprocess.run(["rm", "-rf", str(inc)])
            else:
                os.rename(inc, dst)
            return dst, src
        src = json.loads(n1(f"cat {shlex.quote(item_tree)}/.research-source.json").stdout)
        tag = (src.get("commit") or "nocommit")[:12] + (f"+{(src.get('dirty_digest') or 'dirty')[:8]}" if src.get("dirty") else "")
        dst = H / "trees" / f"{Path(item_tree).name}@{tag}"
    raise RuntimeError(f"tree {item_tree} kept changing while it was copied")


def bin_key(tree: Path) -> str:
    """70-class-sweep.sh's prover build key, computed the same way."""
    sh = ("cat backends/flock/pod/20-gpu-link.sh backends/flock/pod/60-circuit.sh backends/flock/*.patch backends/flock/cuda_*_patch.py "
          "$(find backends/flock/cuda backends/flock/live -type f | LC_ALL=C sort) | sha256sum | cut -c1-16")
    return subprocess.run(["bash", "-c", sh], cwd=tree, capture_output=True, text=True, check=True).stdout.strip()


def venv(fw: Path, fw1: str) -> None:
    py = fw / "flock-circuit" / "py"
    if (py / "bin" / "python3").exists():
        return
    r = n1(f"ls {fw1}/flock-circuit/py/lib/python3.12/site-packages/")
    pins = [f"{m.group(1)}=={m.group(2)}" for m in re.finditer(r"^(numpy|blake3)-([\w.]+)\.dist-info$", r.stdout, re.M)] or ["numpy==2.5.3", "blake3==1.0.10"]
    env = {**os.environ, "UV_CACHE_DIR": str(H / "uv-cache"), "UV_NO_CONFIG": "1", "UV_PYTHON_DOWNLOADS": "never"}
    subprocess.run(["uv", "venv", "-q", "--python", PY, str(py)], env=env, check=True, capture_output=True, text=True)
    subprocess.run(["uv", "pip", "install", "-q", "--python", str(py / "bin" / "python3"), *pins], env=env, check=True, capture_output=True, text=True)
    subprocess.run(["rm", "-rf", str(H / "uv-cache")])


def sync_cache(fw: Path, fw1: str, dtype: str | None, K: str | None) -> dict:
    """Node 1's stage-cache entries for this Definition and K (all of them if the item names neither), each copied whole into
    stage-cache.incoming and then renamed into place, so a half-copied entry is never a cache hit."""
    sc, inc = fw / "stage-cache", fw / "stage-cache.incoming"
    sc.mkdir(parents=True, exist_ok=True)
    inc.mkdir(parents=True, exist_ok=True)
    if dtype and K:
        pat = f'"definition": "{DEFS.get(dtype, dtype)}{{K={K},'
        r = n1(f"cd {fw1}/stage-cache 2>/dev/null && grep -lF {shlex.quote(pat)} */rec.json | cut -d/ -f1", timeout=300)
    else:
        r = n1(f"cd {fw1}/stage-cache 2>/dev/null && ls -d */rec.json | cut -d/ -f1", timeout=300)
    keys = [k for k in r.stdout.split() if re.fullmatch(r"[0-9a-f]{32}", k)]
    want = [k for k in keys if not (sc / k / "rec.json").exists()]
    copied = []
    for k in want:
        p = rsync(f"{N1}:{fw1}/stage-cache/{k}", f"{inc}/")
        if p.returncode == 0 and (inc / k / "rec.json").exists():
            if not (sc / k).exists():
                os.rename(inc / k, sc / k)
            else:
                subprocess.run(["rm", "-rf", str(inc / k)])
            copied.append(k)
    return {"matching_on_node1": len(keys), "copied": copied, "already": len(keys) - len(want)}


def rewrite(s: str, fw1: str, fw2: Path) -> str:
    return s.replace(fw1, str(fw2))


PREP_LOCK = threading.Lock()


def prepare(i: str) -> None:
    """Copies trees, binaries, venvs and cache entries that items share, so one item at a time (the loop's prep threads)."""
    with PREP_LOCK:
        _prepare(i)


def _prepare(i: str) -> None:
    d = ITEMS.get(i)
    item = d["item"]
    env = dict(item.get("env") or {})
    cmd = env.pop("CMD", "")
    tree, src = tree_dir(item["tree"])
    kv = parse_cmd(cmd)
    fw1 = kv.get("FLOCK_WORK") or env.get("FLOCK_WORK")
    if not fw1:
        m = re.search(r"FLOCK_WORK:-([^}]+)\}", (tree / "backends/flock/pod/74-gemm-hill.sh").read_text(errors="replace")) \
            if (tree / "backends/flock/pod/74-gemm-hill.sh").exists() else None
        fw1 = m.group(1) if m else "/workspace/jobs/proofs-bf16-hill"
    if not fw1.startswith("/workspace/jobs/") or "/" in fw1[len("/workspace/jobs/"):].strip("/"):
        raise RuntimeError(f"FLOCK_WORK {fw1}: only /workspace/jobs/<dir> is mirrored")
    fw = H / "work" / Path(fw1).name
    (fw / "flock-circuit").mkdir(parents=True, exist_ok=True)
    (fw / "home").mkdir(parents=True, exist_ok=True)
    cmd2 = rewrite(cmd, fw1, fw)
    env2 = {k: rewrite(str(v), fw1, fw) for k, v in env.items()}
    for v in [cmd2, *env2.values()]:
        for p in re.findall(r"/workspace/jobs/[\w./-]+", v):
            raise RuntimeError(f"{p}: a node-1 path outside FLOCK_WORK, not on node 2")
    # the lane's files under FLOCK_WORK that the item names (zoneinfo and the like), copied as they are
    for v in [cmd2, *env2.values()]:
        for p in re.findall(re.escape(str(fw)) + r"/[\w.-]+", v):
            rel = Path(p).relative_to(fw)
            if rel.parts[0] not in ("stage-cache", "scratch", "home", "flock-circuit"):
                rsync(f"{N1}:{fw1}/{rel.parts[0]}", f"{fw}/")
    key = bin_key(tree)
    b = fw / "flock-circuit" / f"bin-{key}-g1-sm120"
    if not (b / "flock-circuit-selftest").exists():
        r = n1(f"test -x {fw1}/flock-circuit/bin-{key}-g1-sm120/flock-circuit-selftest && echo yes")
        if "yes" not in r.stdout:
            raise RuntimeError(f"no prover binary bin-{key}-g1-sm120 for this tree in node 1's {fw1}: build it there first")
        p = rsync(f"{N1}:{fw1}/flock-circuit/bin-{key}-g1-sm120", f"{fw}/flock-circuit/")
        if p.returncode:
            raise RuntimeError(f"rsync bin-{key}: {p.stderr.strip()[:200]}")
    venv(fw, fw1)
    cache = sync_cache(fw, fw1, kv.get("DTYPE", "bf16") if kv.get("K") else None, kv.get("K"))
    k = int(kv["K"]) if kv.get("K", "").isdigit() else 16384
    # entries of this Definition and K from another tree miss the cache (the key has the source digest): expect a full stage then
    stage_exp = 300.0 if cache["matching_on_node1"] else float(STAGE_S.get(k, 2400))
    ITEMS.update(i, lambda x: x.update(tree={"node1": item["tree"], "node2": str(tree), "source": src}, flock_work={"node1": fw1, "node2": str(fw)},
                                       cmd=cmd2, env=env2, bin={"key": key, "dir": str(b)}, stage_cache_sync=cache,
                                       **({"stage_expected_s": stage_exp} if x.get("gpus") else {})))


# ---------------------------------------------------------------- one attempt (n2h.py job ITEM [stage])

def job(i: str, phase: str) -> int:
    d = ITEMS.get(i)
    if (H / "STOP").exists():
        print("STOP is set: nothing to do")
        return 0
    q = (d.get("env") or {}).get("QUESTION")
    if not q:
        set_state(i, "refused", "no QUESTION")
        return 0
    fj = os.environ.get("FILL_JOB", "")
    if fj and phase == "gpu":
        try:
            ev = (FILL / "events.jsonl").read_text()
            if any(f'"job": "{fj}"' in ln and '"why": "max_min"' in ln for ln in ev.splitlines()):
                set_state(i, "failed", f"{fj} was stopped at max_min before: not re-run")
                return 0
        except OSError:
            pass
    back = "deferred" if phase == "gpu" else "ready"
    exp = d["expected_s"] if phase == "gpu" else d.get("stage_expected_s", d["expected_s"])
    why = allow(exp)
    if why:
        set_state(i, back, why)
        print("deferred:", why)
        return 0
    slot = d["slot"]
    own = sorted(os.sched_getaffinity(0))
    if not set(own) <= set(cpulist(slot["cpus"])):
        set_state(i, back, f"this attempt's CPUs are {span(own)}, not inside slot {slot['cpus']}: not started through vy-provers")
        print("refused: not on the slot's prover cores")
        return 0
    lock = Path(SLICE_LOCKS) / f"{slot['cpus']}.lock"
    if lock.exists():
        with open(lock) as lk:
            try:
                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(lk, fcntl.LOCK_UN)
            except BlockingIOError:
                set_state(i, back, f"slot {slot['cpus']}'s lock {lock} is held by another job")
                return 0
    pre = affinity(H.joinpath("RANGE").read_text().split("#")[0].strip(), mine_root=os.getpid(), item=i)
    mine = affinity(slot["cpus"], mine_root=os.getpid(), sample_s=1.0, item=i)
    if not mine["clean"]:
        set_state(i, back, f"another process may run on slot {slot['cpus']}: {[(x['pid'], x['name'], x['cgroup']) for x in mine['others'][:3]]}")
        return 0
    run = f"n2h-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{os.urandom(2).hex()}"
    R = H / "runs" / run
    (R / "out").mkdir(parents=True)
    (R / "n2-affinity-pre.json").write_text(json.dumps({"range": pre, "slot": mine}, indent=1))
    t0 = now()
    att = {"run": run, "phase": phase, "t0": iso(t0), "fill_job": fj, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
           "gpu_lease_uuid": os.environ.get("GPU_LEASE_UUID"), "pid": os.getpid(), "state": "running"}
    ITEMS.update(i, lambda x: (x.setdefault("attempts", []).append(att), x.update(state="running" if phase == "gpu" else "staging", why=None)))
    fw = Path(d["flock_work"]["node2"])
    env = {**os.environ, **d["env"], "RESEARCH_RUN_DIR": str(R), "RESEARCH_RUN_ID": run, "HILL_NODE": HOST, "CPUSET": slot["cpus"],
           "SLICE_LOCKS": SLICE_LOCKS, "FLOCK_WORK": str(fw), "PYBIN": str(fw / "flock-circuit/py/bin/python3"), "CUDA_TK": CUDA_TK,
           "OMP_NUM_THREADS": str(SLOT), "N2H_LOOPBACK": slot["loopback"], "N2H_ITEM": i,
           "LD_PRELOAD": ":".join(x for x in (str(H / "bin/n2h_loopback.so"), os.environ.get("LD_PRELOAD", "")) if x)}
    cmd = d["cmd"]
    if phase == "stage":
        env["PATH"] = f"{H / 'stub'}:{env['PATH']}"
        env.pop("CUDA_VISIBLE_DEVICES", None)
        if "STAGE_ONLY=1" not in cmd:
            cmd += " STAGE_ONLY=1"
    (R / "n2-command.json").write_text(json.dumps({"cwd": d["tree"]["node2"], "cmd": ["taskset", "-c", slot["cpus"], "bash", "-c", cmd],
                                                   "env": {k: env[k] for k in sorted(env) if k in d["env"] or k.startswith(("N2H", "RESEARCH_", "HILL_", "FLOCK_", "CUDA_", "GPU_LEASE", "FILL"))
                                                           or k in ("CPUSET", "SLICE_LOCKS", "PYBIN", "OMP_NUM_THREADS", "LD_PRELOAD", "PATH")}}, indent=1))
    child: list[subprocess.Popen] = []

    def term(*_):
        # the runner SIGKILLs gpu-lease's group 20 s after its SIGTERM, and this job's group is outside it (vy-provers' scope)
        for p_ in child:
            for sig, wait_s in ((signal.SIGTERM, 8.0), (signal.SIGKILL, 2.0)):
                try:
                    os.killpg(p_.pid, sig)
                except ProcessLookupError:
                    break
                t = time.monotonic()
                while p_.poll() is None and time.monotonic() - t < wait_s:
                    time.sleep(0.2)
                if p_.poll() is not None:
                    break
        mark(i, run, "preempted", None, t0)
        os._exit(143)

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(sig, term)
    with open(R / "stdout.log", "w") as so, open(R / "stderr.log", "w") as se:
        p = subprocess.Popen(["taskset", "-c", slot["cpus"], "bash", "-c", cmd], cwd=d["tree"]["node2"], env=env, stdout=so, stderr=se,
                             start_new_session=True)
        child.append(p)
        ITEMS.update(i, lambda x: [a.update(pgid=p.pid) for a in x["attempts"] if a["run"] == run])
        rc = p.wait()
    t1 = now()
    post = affinity(slot["cpus"], mine_root=os.getpid(), sample_s=1.0)
    rec = record(d, R, run, phase, rc, t0, t1, pre, mine, post)
    ok = rc == 0 and (phase == "stage" or (R / "hillclimb.json").exists())
    mark(i, run, "done" if ok else "failed", rc, t0, t1)
    if phase == "stage":
        set_state(i, "staged" if ok else "failed", None if ok else f"pre-stage rc {rc}", stage_run=run, stage_cached=rec.get("stage_cached"))
    else:
        set_state(i, "done" if ok else "failed", None if ok else f"rc {rc}", run=run)
    return 0


def mark(i: str, run: str, state: str, rc, t0: float, t1: float | None = None) -> None:
    def f(x):
        for a in x.get("attempts", []):
            if a["run"] == run:
                a.update(state=state, rc=rc, t1=iso(t1 or now()), wall_s=round((t1 or now()) - t0, 1))
    ITEMS.update(i, f)


def _staged(R: Path) -> dict:
    out = {}
    for name in ("gate-staged.jsonl", "staged.jsonl"):
        p = R / "out" / name
        recs = [json.loads(ln) for ln in p.read_text().splitlines() if ln.startswith("{")] if p.exists() else []
        out[name] = [{"definition": r.get("definition"), "stage_cached": r.get("stage_cached"), "stage_s": r.get("stage_s"),
                      "staged": "stage" in r} for r in recs]
    return out


def record(d: dict, R: Path, run: str, phase: str, rc: int, t0: float, t1: float, pre: dict, mine: dict, post: dict) -> dict:
    gpu = {"cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), "gpu_lease_uuid": os.environ.get("GPU_LEASE_UUID")}
    try:
        head = (R / "out" / "gpu.csv").read_text().splitlines()
        gpu.update(dict(zip(head[0].split(","), (v.strip() for v in head[1].split(",")))))
    except (OSError, IndexError):
        pass
    idx = gpu.get("cuda_visible_devices")
    gpu["numa"] = (0 if int(idx) <= 3 else 1) if idx and idx.isdigit() else None
    hc = {}
    if (R / "hillclimb.json").exists():
        h = json.loads((R / "hillclimb.json").read_text())
        hc = {k: h.get(k) for k in ("subcircuit", "step", "overhead", "overhead_prove_only", "throughput_vu_per_s", "gpu_util", "gpu_held_s_per_vu",
                                    "verify_s_per_statement", "byte_identical", "flags", "cpu_slice_others", "setup_s", "vus", "why")}
    rec = {"schema": "proofs-n2-hill/record/v0", "run_id": run, "phase": phase, "host": HOST, "lane": d["lane"], "item": d["file"],
           "item_id": d["id"], "taken": d.get("taken"), "question": d["env"].get("QUESTION"), "label": d["env"].get("LABEL"),
           "step": d["env"].get("STEP"), "tree": {"node1": d["tree"]["node1"], "node2": d["tree"]["node2"], "commit": d["tree"]["source"].get("commit"),
                                                   "dirty": d["tree"]["source"].get("dirty"), "branch": d["tree"]["source"].get("branch")},
           "cpuset": d["slot"]["cpus"], "slot": d["slot"], "range": H.joinpath("RANGE").read_text().split("#")[0].strip(),
           "range_source": H.joinpath("RANGE").read_text().partition("#")[2].strip() or None,
           "scope": {"cgroup": Path("/proc/self/cgroup").read_text().strip().split("::", 1)[-1], "cpus": span(sorted(os.sched_getaffinity(0))),
                     "via": f"{VY_PROVERS} with VY_PROVERS_CPUS={os.environ.get('VY_PROVERS_CPUS')}", "slice_locks": SLICE_LOCKS},
           "affinity_check": {"before_range": pre, "before_slot": mine, "after_slot": post},
           "nice": os.getpriority(os.PRIO_PROCESS, 0), "gpu": gpu if phase == "gpu" else None, "fill_job": os.environ.get("FILL_JOB"),
           "loopback": f"{d['slot']['loopback']} (n2h_loopback.so; node 1 runs each job in a pod network namespace of its own)",
           "rc": rc, "t_start": iso(t0), "t_end": iso(t1), "wall_s": round(t1 - t0, 1), "cmd": d["cmd"] + (" STAGE_ONLY=1" if phase == "stage" and "STAGE_ONLY=1" not in d["cmd"] else ""),
           "flock_work": d["flock_work"], "bin": d.get("bin"), "stage_cache_sync": d.get("stage_cache_sync"), "staged": _staged(R),
           "hillclimb": hc, "parity": d.get("parity")}
    if phase == "stage":
        s = rec["staged"].get("staged.jsonl") or []
        rec["stage_cached"] = all(x.get("stage_cached") for x in s + (rec["staged"].get("gate-staged.jsonl") or [])) if s else None
    (R / "n2.json").write_text(json.dumps(rec, indent=1, default=str))
    return rec


# ---------------------------------------------------------------- the loop

class Loop:
    def __init__(self) -> None:
        self.cpu: dict[str, subprocess.Popen] = {}
        self.prep: dict[str, threading.Thread] = {}
        self.last_log = 0.0
        self.last_n1 = 0.0
        self.frozen: set[str] = set()

    # -- fill scripts
    def where(self, name: str) -> str | None:
        for dd in ("running", "queue", "done", "failed", "held-overnight", "withdrawn"):
            if (FILL / dd / name).exists():
                return dd
        return None

    def submit(self, d: dict) -> None:
        n = len([h for h in d.get("history", []) if h["state"] == "queued"])
        name = f"pn2h-{d['id'][:60]}-q{n}.sh"
        q = d["env"]["QUESTION"].replace('"', "'")
        mm = min(30, math.ceil(d["expected_s"] * 1.5 / 60) + 2)
        mem = int(((d["item"].get("resources") or {}).get("prover-bench") or {}).get("memory") or 128)
        gp = d["item"].get("on") or d["slot"].get("gpus")
        on = f" on={gp}" if gp else ""
        body = (f"#!/usr/bin/env bash\n# fill: owner={OWNER} gpus=1 project=verity cpus={SLOT} max_min={mm} mem_gb={mem}{on}\n"
                f"# question: \"{q}\"\n# proofs-n2-hill: lane {d['lane']}'s item {d['file']} on prover slot {d['slot']['cpus']} through vy-provers "
                f"(infra, 128-191 until 14:50Z); LD_PRELOAD n2h_loopback.so moves its loopback to {d['slot']['loopback']}\n"
                f"export N2H_ITEM={shlex.quote(d['id'])} VY_PROVERS_CPUS={d['slot']['cpus']}\n"
                f"exec {VY_PROVERS} python3 {H}/bin/n2h.py job {shlex.quote(d['id'])} gpu\n")
        p = H / "scripts" / name
        p.write_text(body)
        p.chmod(0o755)
        os.replace(p, FILL / "queue" / name)
        set_state(d["id"], "queued", None, fill_script=name, max_min=mm)

    # -- 0-GPU attempts, started by the loop through vy-provers on their slot
    def launch_cpu(self, d: dict) -> None:
        tag = f"pn2h-{d['id'][:50]}-{int(now())}"
        logf = open(H / "logs" / f"{tag}.log", "w")
        env = {**os.environ, "N2H_ITEM": d["id"], "VY_PROVERS_CPUS": d["slot"]["cpus"]}
        p = subprocess.Popen([VY_PROVERS, "python3", str(H / "bin/n2h.py"), "job", d["id"], "stage"], env=env,
                             stdout=logf, stderr=subprocess.STDOUT, start_new_session=True)
        logf.close()
        self.cpu[d["id"]] = p
        set_state(d["id"], "staging", None, cpu_log=tag, cpu_pid=p.pid)

    def freeze(self, on: bool) -> None:
        """While the runner reports a timed window running or waiting, stop the running 0-GPU attempts (SIGSTOP to the workload's
        process group, which the attempt records), as the runner freezes its own CPU jobs; continue them after."""
        for d in ITEMS.all():
            att = (d.get("attempts") or [{}])[-1]
            g = att.get("pgid")
            if d.get("state") != "staging" or att.get("phase") != "stage" or att.get("state") != "running" or not g:
                continue
            key = f"{d['id']}:{g}"
            try:
                if on and key not in self.frozen:
                    os.killpg(g, signal.SIGSTOP)
                    self.frozen.add(key)
                    log(event="freeze", item=d["id"], pgid=g)
                elif not on and key in self.frozen:
                    os.killpg(g, signal.SIGCONT)
                    self.frozen.discard(key)
                    log(event="thaw", item=d["id"], pgid=g)
            except (ProcessLookupError, PermissionError):
                self.frozen.discard(key)

    # -- taking items from node 1
    def take(self, free: list[dict]) -> None:
        r = n1(f"cd {N1_READY} 2>/dev/null && for f in */*.json; do [ -f \"$f\" ] && printf '%s\\t%s\\n' \"$(stat -c %Y \"$f\")\" \"$f\"; done")
        cands = sorted((int(t), f) for t, f in (ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln))
        lanes_busy = {}
        for d in ITEMS.all():
            if d.get("state") not in ("done", "failed", "refused", "shipped", "withdrawn"):
                lanes_busy[d["lane"]] = lanes_busy.get(d["lane"], 0) + 1
        # round-robin: the lane holding fewest slots first, then the oldest item
        cands.sort(key=lambda x: (lanes_busy.get(x[1].split("/")[0], 0), x[0]))
        for _t, f in cands:
            if not free:
                return
            lane, name = f.split("/", 1)
            body = n1(f"cat {N1_READY}/{shlex.quote(f)}").stdout
            try:
                item = json.loads(body)
                env = item.get("env") or {}
                gpus = int(((item.get("resources") or {}).get("prover-bench") or {}).get("gpus", 1))
                cmd = env.get("CMD", "")
            except (ValueError, AttributeError, TypeError) as e:
                self.refuse(f, f"not an item: {e}")
                continue
            if not env.get("QUESTION") or not cmd or not item.get("tree"):
                self.refuse(f, "an item needs tree, env.CMD and env.QUESTION")
                continue
            exp = expected(item, cmd, gpus)
            stage_exp = 120.0 if gpus else exp
            why = allow(exp + stage_exp + 300)
            if why:
                return
            stem = name[:-5]
            iid = f"{lane}__{stem}"
            if ITEMS.path(iid).exists():
                iid = f"{iid}__{stamp()}"
            taken = f"{N1_OUT}/taken/{lane}/{stem}.{stamp()}.json"
            mv = n1(f"mkdir -p {N1_OUT}/taken/{lane} && mv {N1_READY}/{shlex.quote(f)} {shlex.quote(taken)} && echo moved")
            if "moved" not in mv.stdout:
                continue
            slot = free.pop(0)
            ITEMS.update(iid, lambda x: x.update(id=iid, lane=lane, file=name, taken=taken, taken_utc=iso(), item=item, gpus=gpus,
                                                 expected_s=exp, stage_expected_s=stage_exp, slot=slot, state="taken",
                                                 parity=item.get("parity")))
            log(event="taken", item=iid, slot=slot["cpus"], gpus=gpus, expected_s=exp)
            self.start_prep(iid)

    def refuse(self, f: str, why: str) -> None:
        lane, name = f.split("/", 1)
        n1(f"mkdir -p {N1_OUT}/refused/{lane} && mv {N1_READY}/{shlex.quote(f)} {N1_OUT}/refused/{lane}/{shlex.quote(name)} && "
           f"printf '%s\\n' {shlex.quote(why)} > {N1_OUT}/refused/{lane}/{shlex.quote(name)}.why")
        log(event="refused", file=f, why=why)

    def start_prep(self, iid: str) -> None:
        set_state(iid, "preparing")

        def run():
            try:
                prepare(iid)
                set_state(iid, "ready")
            except Exception as e:  # noqa: BLE001
                set_state(iid, "failed", f"prepare: {type(e).__name__}: {str(e)[:400]}")
        t = threading.Thread(target=run, daemon=True)
        self.prep[iid] = t
        t.start()

    # -- shipping finished attempts to node 1
    def ship(self) -> None:
        if n1_offline():
            return
        for d in ITEMS.all():
            for a in d.get("attempts", []):
                if a.get("state") not in ("done", "failed") or a.get("shipped"):
                    continue
                R = H / "runs" / a["run"]
                if not (R / "n2.json").exists():
                    continue
                n1(f"mkdir -p {N1_OUT}/runs")
                p = rsync(f"{R}", f"{N1}:{N1_OUT}/runs/")
                if p.returncode:
                    log(event="ship-failed", run=a["run"], why=p.stderr.strip()[:200])
                    return
                rec = json.loads((R / "n2.json").read_text())
                line = {k: rec.get(k) for k in ("run_id", "phase", "lane", "item", "question", "cpuset", "rc", "t_start", "t_end", "wall_s", "hillclimb",
                                                "stage_cached", "parity")}
                line.update(commit=rec["tree"]["commit"], node1_dir=f"{N1_OUT}/runs/{a['run']}", attempt=a["state"], host=HOST,
                            gpu=(rec.get("gpu") or {}).get("cuda_visible_devices"), gpu_numa=(rec.get("gpu") or {}).get("numa"))
                n1(f"cat >> {N1_OUT}/points.jsonl", input_=json.dumps(line, default=str) + "\n")
                ITEMS.update(d["id"], lambda x: [b.update(shipped=iso()) for b in x.get("attempts", []) if b["run"] == a["run"]])
                log(event="shipped", run=a["run"], item=d["id"], state=a["state"])

    def preempted_aside(self, d: dict) -> None:
        for a in d.get("attempts", []):
            if a.get("state") in ("running", "preempted") and a.get("phase") == "gpu" and not a.get("aside"):
                pid = a.get("pid")
                alive = bool(pid) and Path(f"/proc/{pid}").exists()
                if alive and a["state"] == "running":
                    continue
                src = H / "runs" / a["run"]
                (H / "runs" / "preempted").mkdir(exist_ok=True)
                if src.exists():
                    os.rename(src, H / "runs" / "preempted" / a["run"])
                ITEMS.update(d["id"], lambda x: [b.update(state="preempted", aside=iso()) for b in x["attempts"] if b["run"] == a["run"]])
                log(event="preempted", item=d["id"], run=a["run"])

    def tick(self) -> dict:
        st = status()
        sl = slots()
        self.freeze(st["timed"] or st["waiting"])
        busy, counts = set(), {}
        for d in ITEMS.all():
            s = d.get("state")
            counts[s] = counts.get(s, 0) + 1
            iid = d["id"]
            if s in ("done", "failed", "refused", "withdrawn"):
                continue
            if d.get("slot"):
                busy.add(d["slot"]["cpus"])
            if s == "ready":
                if not d.get("gpus"):
                    if not allow(d["expected_s"]):
                        self.launch_cpu(d)
                elif d.get("skip_prestage"):
                    set_state(iid, "staged")
                elif not allow(d["stage_expected_s"] + d["expected_s"]):
                    self.launch_cpu(d)
            elif s == "staging":
                p = self.cpu.get(iid)
                if p is not None and p.poll() is not None:
                    self.cpu.pop(iid)
                    d2 = ITEMS.get(iid)
                    if d2["state"] == "staging":
                        set_state(iid, "failed", f"0-GPU attempt exited {p.returncode} without a record")
                elif p is None:
                    att = (d.get("attempts") or [{}])[-1]
                    pids = [x for x in (att.get("pid") if att.get("phase") == "stage" else None, d.get("cpu_pid")) if x]
                    if not any(Path(f"/proc/{x}").exists() for x in pids):
                        d2 = ITEMS.get(iid)
                        if d2["state"] == "staging":
                            set_state(iid, "ready", "its 0-GPU attempt ended without a record (loop restart?): again")
            elif s == "staged":
                if not d.get("gpus"):
                    set_state(iid, "done", None)
                elif d.get("stage_cached") is False and not d.get("skip_prestage"):
                    # the pre-stage staged something itself: the GPU job will now hit the cache
                    if not allow(d["expected_s"]):
                        self.submit(d)
                elif not allow(d["expected_s"]):
                    self.submit(d)
            elif s in ("queued", "running", "held"):
                w = self.where(d["fill_script"])
                if w == "held-overnight":
                    if s == "queued":
                        set_state(iid, "held", "node2-ops' overnight gate holds its script in fill/held-overnight/")
                        log(event="held", item=iid, script=d["fill_script"])
                elif w in ("queue", "running") and s == "held":
                    set_state(iid, "queued", f"released from held-overnight/ to {w}/")
                elif w == "queue" and s == "running":
                    self.preempted_aside(d)
                    set_state(iid, "queued", "preempted: requeued by the fill runner")
                elif w is None and s == "held":
                    set_state(iid, "deferred", "its held script left held-overnight/ for neither queue/ nor running/: queue it again")
                elif w in ("done", "failed", "withdrawn") and s in ("queued", "running", "held"):
                    d2 = ITEMS.get(iid)
                    if d2["state"] in ("queued", "running"):
                        self.preempted_aside(d2)
                        set_state(iid, "deferred", f"fill script in {w}/ without a finished attempt")
            elif s == "deferred":
                self.preempted_aside(d)
                last = max((datetime.fromisoformat(h["utc"].replace("Z", "+00:00")).timestamp() for h in d.get("history", [])
                            if h["state"] == "deferred"), default=0.0)
                if now() - last >= 120 and not allow(d["expected_s"]) and self.where(d.get("fill_script", "")) not in ("queue", "running"):
                    self.submit(d)
        if (H / "STOP").exists():
            return {"stop": True}
        free = [x for x in sl if x["cpus"] not in busy]
        if sl and free and disk_pct() < DISK_STOP and not n1_offline() and now() - self.last_n1 >= 30:
            self.last_n1 = now()
            try:
                self.take(free)
            except (subprocess.SubprocessError, OSError) as e:
                log(event="take-error", why=str(e)[:200])
        try:
            self.ship()
        except (subprocess.SubprocessError, OSError) as e:
            log(event="ship-error", why=str(e)[:200])
        return {"status": st["line"][:110], "range": [x["cpus"] for x in sl], "free_slots": len(free), "states": counts,
                "disk_pct": round(disk_pct(), 1), "next_allow_gpu_300s": allow(300)}

    def run(self) -> int:
        log(event="loop-start", pid=os.getpid())
        while True:
            if (H / "STOP").exists():
                log(event="stopped", why="STOP file")
                return 0
            try:
                t = self.tick()
            except Exception as e:  # noqa: BLE001
                t = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
                log(event="tick-error", **t)
            if now() - self.last_log >= LOG_EVERY_S:
                log(event="tick", **t)
                self.last_log = now()
            time.sleep(EVERY_S)


def main() -> int:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    if a[0] == "loop":
        return Loop().run()
    if a[0] == "job":
        return job(a[1], a[2] if len(a) > 2 else "gpu")
    if a[0] == "affinity":
        print(json.dumps(affinity(a[1]), indent=1))
        return 0
    if a[0] == "allow":
        why = allow(float(a[1]))
        print(why or "ok")
        return 1 if why else 0
    if a[0] == "slots":
        print(json.dumps(slots(), indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
