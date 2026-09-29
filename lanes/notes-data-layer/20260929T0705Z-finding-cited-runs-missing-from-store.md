---
lane: notes-data-layer
kind: finding
status: final
created: 2026-09-29T07:05Z
repo: danielreuter/verity
origin: cursor cloud agent bc-93a93908-683e-52bd-ba14-f8aefce01cae
---

# 16% of the run ids the notes cite have no attempt in the evidence store; 0.2% of the art: ids name no artifact

Inputs: the notes at `eb677ddb` (2026-09-29T05:05Z), and the store's catalog as mirrored at 05:16Z. The script is at the end
(sha256 `62deb34ff09ea42e…`): `python3 citediag.py NOTES_CLONE CATALOG_SQLITE > out.json` reproduces every number here.

## Run ids

- The notes (every `.md` under `lanes/` and `kb/`) cite 2,374 distinct run ids. 1,985 have an attempt in the catalog, and
  **389 (16.4%) don't**.
- 83 of the 389 carry a label (82 `custody=waived`, 1 `outcome`). The store has an account of them, and the citation check at
  `research notes sync` (verity #377) counts them as resolved.
- 7 are a sibling or a typo of a stored run (the same launch second, or one character off).
- **299 (12.6%) have neither an attempt nor a label.** Here is what the lines citing them say, classified by the first class
  that matches. The classification is a heuristic over free text, so read the examples in the script's output:

| What the citing text says | Runs |
|---|---|
| It finished and a result is quoted (passed, rc 0, a time or a ratio) | 177 |
| Nothing (a bare citation) | 97 |
| It ended without a record (killed, died, timed out, cancelled) | 17 |
| It was cited while in flight and never published | 8 |

- Miss rate by launch day (the date in the id):
  - 09-22: 5.1% (20 of 392)
  - 09-23: 13.0% (51 of 393)
  - 09-24: 49.4% (81 of 164)
  - 09-25: 22.8% (136 of 596)
  - 09-26: 4.4% (19 of 429)
  - 09-27: 15.2% (31 of 204)
  - 09-28: 27.3% (44 of 161)
  - 09-29: 22.6% (7 of 31, to 05:05Z)
- The coordinator's notes cite 109 of the 306 misses without a label, more than any other lane (verify-night 29, verify-po 23).

## Why they're missing

An attempt reaches the store only when the runner publishes it after the workload exits, or when `research data custody
--publish` publishes the run directory later. A run whose supervisor or pod was killed leaves nothing, and so does a local run
nobody fetched, even when someone read its result and quoted it (177 of the 299). One example: `r20260928-042319-9aac` "passed
but unrecorded -- my 04:25Z kill loop matched the new runner" (the coordinator's report, 06:07Z checkpoint).

## art: ids

The notes cite 3,960 distinct `art:` ids. **7 (0.2%) name no artifact**:

- a placeholder, `art:1a2b3c4d` (workflow-review);
- two 62-digit ids with a digit lost (b-merge-h100, vllm-coordinator);
- `art:37993420` (enc-hopper);
- `art:84fd7745`, `art:8d03bb26` and `art:9ef7438d` (the coordinator's reports of 09-25 and 09-29).

## What would close it (the coordinator's call)

- **For each of the 299 runs:** publish it with `research data custody --publish` if its directory still exists; otherwise label it
  `custody=waived`, with a ref naming the note that says what happened. Then the store holds an account of every run a note cites.
- **Going forward:** verity #377 warns at `research notes sync` when a pushed note cites a run or an `art:` id the store lacks,
  so a new case shows up when it's written rather than weeks later.

## The script

~~~python
"""Which cited run ids and art: ids in the notes repo resolve in the evidence store, and why the rest do not.

    python3 citediag.py NOTES_CLONE CATALOG_SQLITE > out.json

The same patterns as `research notes sync`'s citation check, over every .md under lanes/ and kb/.  A run id resolves when the
store has its attempt; a label on it (custody waived | never-ran, outcome) is an account of it, counted apart.  The rest are
classified by the line that cites them, first match wins: another attempt shares its launch second or is one character away
(a sibling or a typo); some line quotes its result (passed, failed, green, rc N, a number with a unit...); some line says it
ended without one (killed, died, stopped, timed out, cancelled, OOM...); some line cites it in flight (running, launched,
queued...); else a bare citation.  A heuristic over free text: read the examples.
"""
import collections
import json
import re
import sqlite3
import sys
from pathlib import Path

RUN_RE = re.compile(r"\br\d{8}-\d{6}-[0-9a-f]{4}\b")
ART_RE = re.compile(r"\bart:([0-9a-f]{8,64})\b")
STAMP_RE = re.compile(r"^(\d{8}T\d{4}Z)-")
ENDED = re.compile(r"(?i)\b(kill(ed|s)?|died|dead|timed? ?out|timeout|cancel+ed|preempt\w*|oom\w*|crash\w*|abort\w*|reaped|"
                   r"terminated|stopped|lost|wedged|hung|never (finished|completed|ran)|evicted|interrupted)\b")
RESULT = re.compile(r"(?i)\b(pass(ed|es)?|fail(ed|s)?|green|rc[ =:]?-?\d+|exit(ed)? \d+|done|finished|completed|succeeded|"
                    r"measured|median|verdict|agree[sd]?|match(ed|es)|\d+(\.\d+)? ?(ms|s|min|gb|gib|mb|mib|x)\b|"
                    r"\d+(\.\d+)?%|proved|verified|BOOTSTRAP_OK)\b")
FLIGHT = re.compile(r"(?i)\b(running|in[- ]flight|launch(ed|ing)?|start(ed|ing)|queued|pending|waiting|poll\w*|eta|"
                    r"under way|in progress|kicked off|submitted|dispatched)\b")


def main(notes: Path, catalog: Path) -> dict:
    db = sqlite3.connect(f"file:{catalog}?mode=ro", uri=True)
    attempts = {r[0] for r in db.execute("SELECT id FROM attempts")}
    labelled = collections.defaultdict(set)
    for t, k, v in db.execute("SELECT target, key, value FROM labels"):
        labelled[t].add(f"{k}={v}")
    arts = sorted(r[0] for r in db.execute("SELECT id FROM artifacts"))
    by_second = collections.defaultdict(set)
    for a in attempts:
        by_second[a[:16]].add(a)

    runs = collections.defaultdict(list)        # run id -> [(path, context)]
    art_cites = collections.defaultdict(list)
    for p in sorted([*notes.glob("lanes/**/*.md"), *notes.glob("kb/**/*.md")]):
        rel = str(p.relative_to(notes))
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for m in RUN_RE.finditer(text):
            a, b = text.rfind("\n", 0, m.start()) + 1, text.find("\n", m.end())
            b = len(text) if b < 0 else b
            runs[m[0]].append((rel, text[max(a, m.start() - 200):min(b, m.end() + 200)]))
        for m in ART_RE.finditer(text):
            art_cites["art:" + m[1]].append(rel)

    def sibling(r: str) -> bool:
        if by_second.get(r[:16], set()) - {r}:
            return True
        return any(sum(a != b for a, b in zip(r, x)) == 1 for x in by_second.get(r[:16], ()))

    missing = sorted(r for r in runs if r not in attempts)
    klass: dict[str, str] = {}
    for r in missing:
        ctx = " ".join(c for _, c in runs[r])
        klass[r] = ("labelled (custody waived / never-ran, outcome)" if r in labelled else
                    "sibling or typo of a stored run" if sibling(r) else
                    "finished, result quoted, never published" if RESULT.search(ctx) else
                    "ended without a record (killed, died, timed out, cancelled)" if ENDED.search(ctx) else
                    "cited in flight, never published" if FLIGHT.search(ctx) else
                    "bare citation")
    by_class = collections.Counter(klass.values())

    def day_of(r: str) -> str:
        return f"{r[1:5]}-{r[5:7]}-{r[7:9]}"

    days = collections.defaultdict(lambda: [0, 0])
    for r in runs:
        days[day_of(r)][0] += 1
        days[day_of(r)][1] += r in klass
    lanes = collections.Counter()
    for r in missing:
        if klass[r].startswith("labelled"):
            continue
        for lane in {p.split("/")[1] for p, _ in runs[r] if p.startswith("lanes/")}:
            lanes[lane] += 1

    def art_ok(a: str) -> bool:
        import bisect
        i = bisect.bisect_left(arts, a)
        return i < len(arts) and arts[i].startswith(a)

    art_missing = sorted(a for a in art_cites if not art_ok(a))
    return {
        "notes_head": None,
        "run_ids_cited": len(runs),
        "run_ids_missing": len(missing),
        "run_ids_missing_unlabelled": sum(1 for r in missing if not klass[r].startswith("labelled")),
        "by_class": dict(by_class.most_common()),
        "by_launch_day": {d: {"cited": n, "missing": m, "pct": round(100 * m / n, 1)} for d, (n, m) in sorted(days.items())},
        "unlabelled_missing_by_citing_lane": dict(lanes.most_common(12)),
        "art_ids_cited": len(art_cites),
        "art_ids_missing": len(art_missing),
        "art_missing_examples": {a: sorted(set(art_cites[a]))[:2] for a in art_missing[:12]},
        "examples": {c: [(r, runs[r][-1][0], runs[r][-1][1][:240]) for r in missing if klass[r] == c][:3] for c in by_class},
        "classes": {c: [r for r in missing if klass[r] == c] for c in by_class},
    }


if __name__ == "__main__":
    out = main(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps(out, indent=1))
~~~
