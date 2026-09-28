"""gate_write.py EVIDENCE_DIR ROWKEY: may `rebaseline write --force` take this row's recorded results?  (VM side, from integrations/vllm)

EVIDENCE_DIR is the row run's evidence/ (record/<row>/<check>.json from `rebaseline run`, row/verdict.json, row/commit/manifest_verify.json,
strict_word.json).  WRITE needs all of:
  * the verdict of record states the row's class: GREEN -> PASS, FAIL -> FAIL (a GREEN row that comes out FAIL is deferred, never written);
  * the strict word check passed and manifest-verify is ok;
  * every failing check is one whose values the epoch moves (digests, counts, populations), and in it no boolean fact of the contract
    changed (`ok`, `pass`, `tokens_equal`, ... stay as the record states them);
  * the verdict-like checks (verdict, global_match_checks, executed_prefix, stoch_value) pass as recorded, except that
    global_match_checks may move its fold-record pins (`$.fold_record_pins.*`, sha256 of the Programs the fold read) when no boolean
    fact changed (coordinator 20:14Z);
  * coverage passes, or is PENDING (coordinator 20:14Z): the harness's recompute misses only `norm_scales` while the Commit's own
    `required_value_coverage/manifest_coverage` PASSed with exactly that many `norm_scales` checked.  A pending coverage result is left
    out of the write (its previous contract stays, `write` lists it) until checks/coverage.py reads the family and it is backfilled.
Prints `WRITE forced=<checks>[ pending=coverage]` or `HOLD <reasons>` and exits 0 / 1.  Nothing is written here."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tests.regression import resolver

MOVES = {"manifest_digest", "program_digest", "step_segmentation", "decomp_hashes", "replay_partition", "attempt_provenance", "coverage",
         "commit_summary"}
VERDICT_LIKE = {"verdict", "global_match_checks", "executed_prefix", "stoch_value"}


def _doc(p: Path) -> dict:
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def _bools(x: object, at: str = "") -> dict[str, bool]:
    if isinstance(x, bool):
        return {at: x}
    if isinstance(x, dict):
        out: dict[str, bool] = {}
        for k, v in x.items():
            out.update(_bools(v, f"{at}.{k}" if at else str(k)))
        return out
    return {}


def gate(ev: Path, key: str) -> tuple[bool, list[str], list[str]]:
    row = next(r for r in resolver.rows() if r.key == key)
    hold: list[str] = []
    outcome = _doc(ev / "row" / "verdict.json").get("outcome")
    want = "PASS" if row.cls == "GREEN" else "FAIL"
    if outcome != want:
        hold.append(f"verdict {outcome} on a {row.cls} row (the class states {want})")
    if not _doc(ev / "strict_word.json").get("ok"):
        hold.append("strict word check not PASS")
    if _doc(ev / "row" / "commit" / "manifest_verify.json").get("ok") is not True:
        hold.append("manifest-verify not ok")
    rec = ev / "record" / key
    results = {p.stem: _doc(p) for p in sorted(rec.glob("*.json"))} if rec.is_dir() else {}
    results = {k: v for k, v in results.items() if v.get("schema") == "verity-vllm/regression-result/v1"}
    if not results:
        hold.append(f"no recorded results under {rec}")
    forced: list[str] = []
    pending: list[str] = []
    for name, r in sorted(results.items()):
        if not r.get("problems"):
            continue
        eb, ab = _bools(r.get("expected")), _bools(r.get("actual"))
        flipped = [k for k in eb if k in ab and eb[k] != ab[k]]
        if name == "coverage" and _coverage_pending(ev, r):
            pending.append(name)
        elif name == "global_match_checks" and not flipped and all(str(p).startswith("$.fold_record_pins.") for p in r["problems"]):
            forced.append(name)
        elif name in VERDICT_LIKE:
            hold.append(f"{name} FAILED: {'; '.join(r['problems'][:3])}")
        elif name in MOVES:
            if flipped:
                hold.append(f"{name}: boolean facts changed {flipped[:6]}")
            else:
                forced.append(name)
        else:
            hold.append(f"{name} FAILED (not a check the epoch moves): {'; '.join(r['problems'][:3])}")
    return not hold, forced, hold, pending


def _coverage_pending(ev: Path, r: dict) -> bool:
    act = r.get("actual") or {}
    missing = act.get("missing_by_family") or {}
    if set(missing) != {"norm_scales"} or act.get("committed_unmatched_n") or act.get("duplicate_names_n"):
        return False
    for c in _doc(ev / "row" / "verdict.json").get("checks") or []:
        if c.get("name") == "required_value_coverage/manifest_coverage":
            return c.get("outcome") == "PASS" and ((c.get("scope") or {}).get("checked_by_family") or {}).get("norm_scales") == missing["norm_scales"]
    return False


def main() -> int:
    ok, forced, hold, pending = gate(Path(sys.argv[1]), sys.argv[2])
    print(f"WRITE forced={','.join(forced) or 'none'}{' pending=' + ','.join(pending) if pending else ''}" if ok else "HOLD " + " | ".join(hold))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
