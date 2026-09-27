"""Small shared helpers for the sweeps package: wall-clock guards, JSONL I/O, number formatting."""

from __future__ import annotations

import contextlib
import json
import signal
import sys
import threading
from pathlib import Path
from typing import Iterator

# The op graph / ADW helpers recurse along the dataflow (depth ~ ops per layer x layers); 405B has 126 layers.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 200_000))

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
PLOTS_DIR = RESULTS_DIR / "plots"


class StepTimeout(TimeoutError):
    """Raised inside :func:`time_limit` when the wall-clock budget is exceeded."""


#: H100 SXM roofline: 989 TFLOP/s dense BF16 = 4.945e14 MAC/s over 3.35 TB/s HBM3 -> MACs per byte of HBM traffic.
#: (Kept for the legacy plots only; the P3 translation no longer compares with native traffic, see analysis.py.)
KAPPA_NATIVE_HBM = 4.945e14 / 3.35e12
#: MACs per byte of *cross-device* traffic in FSDP / TP training (order of magnitude range).
KAPPA_NATIVE_INTERCONNECT = (1e3, 1e4)


@contextlib.contextmanager
def time_limit(seconds: float | None) -> Iterator[None]:
    """Abort the enclosed (pure-Python) block with :class:`StepTimeout` after ``seconds`` of wall-clock time.

    Uses ``SIGALRM``/``setitimer`` so it only works in the main thread on Unix; elsewhere it is a no-op
    (the caller still records elapsed time)."""
    if not seconds or threading.current_thread() is not threading.main_thread() or not hasattr(signal, "setitimer"):
        yield
        return

    def _handler(signum, frame):  # noqa: ARG001
        raise StepTimeout(f"exceeded {seconds:.0f}s wall-clock budget")

    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


# --- JSON / JSONL ----------------------------------------------------------------------------------------

def _default(o):
    if isinstance(o, (set, frozenset, tuple)):
        return list(o)
    if hasattr(o, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(o)
    if isinstance(o, Path):
        return str(o)
    return str(o)


def dumps(obj) -> str:
    return json.dumps(obj, default=_default, sort_keys=False)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, default=_default, indent=1))


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(dumps(row) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    rows = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a partial line from an interrupted run
    return rows


def dedupe(rows: list[dict], key_fn) -> list[dict]:
    """Keep the last row per key (later lines of a JSONL supersede earlier ones)."""
    out: dict = {}
    for r in rows:
        out[key_fn(r)] = r
    return list(out.values())


# --- formatting ------------------------------------------------------------------------------------------

def fmt(x, digits: int = 3) -> str:
    """Compact scientific/plain formatting for table cells; ``None`` -> ``-``."""
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, str):
        return x
    if isinstance(x, int) and abs(x) < 10_000:
        return str(x)
    if isinstance(x, (int, float)):
        if x == 0:
            return "0"
        if 1e-3 <= abs(x) < 1e4:
            return f"{x:.{digits}g}"
        return f"{x:.{digits - 1}e}"
    return str(x)


def fmt_bytes(x) -> str:
    if x is None:
        return "-"
    x = float(x)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(x) < 1024 or unit == "PB":
            return f"{x:.3g} {unit}" if unit != "B" else f"{int(x)} B"
        x /= 1024
    return f"{x:.3g} PB"


def md_table(rows: list[dict], cols: list[tuple[str, str]], formatters: dict | None = None) -> str:
    """``rows`` -> a GitHub-markdown table.  ``cols`` = ``[(key, header), ...]``."""
    formatters = formatters or {}
    head = "| " + " | ".join(h for _, h in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = []
    for r in rows:
        cells = []
        for k, _ in cols:
            f = formatters.get(k, fmt)
            cells.append(str(f(r.get(k))).replace("|", "\\|"))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([head, sep, *body])


def replace_between(text: str, tag: str, content: str) -> str:
    """Replace the block between ``<!-- BEGIN:tag -->`` and ``<!-- END:tag -->`` (markers kept); append the
    block at the end if the markers are missing."""
    b, e = f"<!-- BEGIN:{tag} -->", f"<!-- END:{tag} -->"
    if b in text and e in text:
        pre, rest = text.split(b, 1)
        _, post = rest.split(e, 1)
        return f"{pre}{b}\n{content.rstrip()}\n{e}{post}"
    return text.rstrip() + f"\n\n{b}\n{content.rstrip()}\n{e}\n"
