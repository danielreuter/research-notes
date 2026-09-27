"""Safety rails for build+extract experiments.

The operator-graph extractor is superlinear in the number of sequences batched through one attention call
(``tokens / seq`` per forward) and can materialise multi-GB explicit reference tuples; an unguarded probe took
the machine down.  Everything here exists so that cannot happen again:

* :func:`run_guarded` -- run a command in a subprocess with a wall-clock timeout **and** an RSS watchdog
  (``ps -o rss= -p PID`` every 0.5 s, SIGKILL above ``max_rss_mb``, default 3 GB), returning ``status`` in
  ``ok | timeout | oom-guard | error``.  A file lock makes sure only one guarded child runs at a time.
  ``sweep`` (per case), ``characterize_all`` (per row) and ``scaling`` (per probe) all go through it.
* :data:`SAFE_LIMITS` / :func:`check_limits` -- a coarse envelope that stops absurd requests; the pre-fix
  envelope is :data:`LEGACY_LIMITS`.  Drivers record anything outside as ``skipped`` unless ``unsafe=True``.
"""

from __future__ import annotations

import contextlib
import fcntl
import os
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from accumulation.configs import MODELS, Workload
from accumulation.sweeps.util import RESULTS_DIR

#: Envelope for build+extract.  The multi-sequence blow-up is fixed (root-level transposes of batched attention
#: outputs materialised explicit reference tuples; weight gradients are now ``AccMatmulTT`` with token-major
#: operands and the extractor memoises per-member resolutions; extraction is ~linear, ~0.1 s per sequence at
#: 8B), so the envelope is wide: it only stops absurd requests.  Every case still runs in a guarded child
#: (wall clock + RSS watchdog, default 3 GB, one at a time), which is the real protection.
#: The pre-fix envelope is kept as :data:`LEGACY_LIMITS` for reference / regression runs.
SAFE_LIMITS = {"tokens": 1 << 26, "seq": 1 << 17, "population": 1 << 12, "local_steps": 64, "sequences_per_forward": 1 << 14,
               "big_models": ("llama3-70b", "llama3-405b", "deepseek-v3", "qwen3-235b-a22b"), "big_model_sequences": 1 << 14}
DRIVER_LIMITS = SAFE_LIMITS
LEGACY_LIMITS = {"tokens": 8192, "seq": 4096, "population": 8, "local_steps": 2, "sequences_per_forward": 1,
                 "big_models": SAFE_LIMITS["big_models"], "big_model_sequences": 1}
DEFAULT_MAX_RSS_MB = 3072.0


def sequences_per_forward(alg: str, wl: Workload) -> int:
    """Sequences that one ``Block`` call batches through ``AttnSeq`` (ES and local-SGD split the tokens first)."""
    per = wl.tokens
    if alg == "es":
        per //= wl.population
    if alg == "local-sgd":
        per //= wl.local_steps
    return max(1, per // wl.seq)


def check_limits(alg: str, model: str, wl: Workload, limits: dict = SAFE_LIMITS) -> str | None:
    """``None`` if ``(alg, model, wl)`` is inside the safe envelope, else the reason it is not.  Toy configs
    (< 10 M parameters: tiny/tiny2/small/tiny-moe/small-moe) are exempt -- their whole circuit is tiny."""
    if model in MODELS and MODELS[model].total_params() < 10_000_000:
        return None
    why = []
    if wl.tokens > limits["tokens"]:
        why.append(f"tokens {wl.tokens} > {limits['tokens']}")
    if wl.seq > limits["seq"]:
        why.append(f"seq {wl.seq} > {limits['seq']}")
    if wl.population > limits["population"]:
        why.append(f"population {wl.population} > {limits['population']}")
    if wl.local_steps > limits["local_steps"]:
        why.append(f"local_steps {wl.local_steps} > {limits['local_steps']}")
    n = sequences_per_forward(alg, wl)
    if n > limits["sequences_per_forward"]:
        why.append(f"{n} sequences per forward > {limits['sequences_per_forward']}")
    if model in limits["big_models"] and n > limits["big_model_sequences"]:
        why.append(f"{model} with {n} sequences per forward (limit {limits['big_model_sequences']})")
    return "; ".join(why) or None


@dataclass
class GuardResult:
    status: str                 # ok | timeout | oom-guard | error
    returncode: int | None
    elapsed_s: float
    peak_rss_mb: float
    stdout: str = ""
    stderr: str = ""
    samples: int = 0
    detail: str = ""
    rss_trace: list = field(default_factory=list)  # (t, rss_mb) every ~5 s for the report


def _rss_mb(pid: int) -> float | None:
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True, timeout=5).stdout.strip()
        return int(out) / 1024 if out else None
    except (subprocess.SubprocessError, ValueError):
        return None


def _kill(proc: subprocess.Popen) -> None:
    """SIGKILL the child's whole session (it was started with ``start_new_session=True``), then the pid itself."""
    with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
        os.killpg(proc.pid, signal.SIGKILL)
    with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
        os.kill(proc.pid, signal.SIGKILL)
    with contextlib.suppress(subprocess.SubprocessError):
        proc.wait(timeout=10)


@contextlib.contextmanager
def single_probe_lock(lock_path: Path = RESULTS_DIR / ".probe.lock", courtesy_s: float = 0.3):
    """Block until no other guarded probe is running (cross-process ``flock``).

    ``flock`` is not fair: a driver that releases and immediately re-acquires (one probe after another) starves
    every other waiting driver.  After releasing, the holder therefore sleeps ``courtesy_s`` so a blocked waiter
    is scheduled first."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as fh:
        # A blocked LOCK_EX waiter is not woken preferentially on macOS: a holder that releases and immediately
        # re-acquires (an older driver without the courtesy sleep) starves it indefinitely (observed: 0 wins in 30
        # minutes).  Polling with LOCK_NB at a few-ms period catches the release window instead.
        delay = 0.002
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                time.sleep(delay)
                delay = min(0.02, delay * 1.3)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    if courtesy_s:
        time.sleep(courtesy_s)


def run_guarded(cmd: list[str], *, timeout_s: float = 300.0, max_rss_mb: float = DEFAULT_MAX_RSS_MB, poll_s: float = 0.5,
                cwd: str | Path | None = None, env: dict | None = None, log=None, lock: bool = True) -> GuardResult:
    """Run ``cmd`` under a wall-clock timeout and an RSS ceiling; never raises for child failures.  ``lock=False`` skips the
    machine-wide one-child-at-a-time lock (for drivers whose children are individually RSS-capped well below machine memory)."""
    with (single_probe_lock() if lock else contextlib.nullcontext()), \
            tempfile.TemporaryFile("w+", encoding="utf-8", errors="replace") as out_f, \
            tempfile.TemporaryFile("w+", encoding="utf-8", errors="replace") as err_f:
        t0 = time.monotonic()
        try:
            # files, not pipes: the poll loop below does not drain a pipe, and a child that logs more than the pipe buffer
            # (64 KB) would block in pipe_write forever (observed on the pod: 13 children asleep for an hour)
            proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=out_f, stderr=err_f, text=True, start_new_session=True)
        except OSError as e:
            return GuardResult("error", None, 0.0, 0.0, detail=f"spawn failed: {e}")
        peak = 0.0
        samples = 0
        trace: list = []
        status = "ok"
        detail = ""
        last_trace = -1e9
        while True:
            rc = proc.poll()
            if rc is not None:
                break
            rss = _rss_mb(proc.pid)
            if rss is not None:
                samples += 1
                peak = max(peak, rss)
                now = time.monotonic() - t0
                if now - last_trace >= 5.0:
                    trace.append((round(now, 1), round(rss, 1)))
                    last_trace = now
                if rss > max_rss_mb:
                    status, detail = "oom-guard", f"RSS {rss:.0f} MB > {max_rss_mb:.0f} MB after {now:.1f}s"
                    if log:
                        log(f"[guard] {detail}: killing {proc.pid}")
                    _kill(proc)
                    break
            if time.monotonic() - t0 > timeout_s:
                status, detail = "timeout", f"> {timeout_s:.0f}s wall clock (peak RSS {peak:.0f} MB)"
                if log:
                    log(f"[guard] {detail}: killing {proc.pid}")
                _kill(proc)
                break
            time.sleep(poll_s)
        try:
            proc.wait(timeout=10)
        except subprocess.SubprocessError:
            pass
        out, err = "", ""
        for f, name in ((out_f, "out"), (err_f, "err")):
            try:
                f.flush()
                f.seek(0)
                text_ = f.read()
            except (OSError, ValueError):
                text_ = ""
            if name == "out":
                out = text_
            else:
                err = text_
        elapsed = time.monotonic() - t0
        if status == "ok" and proc.returncode not in (0, None):
            status, detail = "error", f"exit code {proc.returncode}: {(err or '').strip()[-400:]}"
        return GuardResult(status, proc.returncode, elapsed, peak, out or "", err or "", samples, detail, trace)
