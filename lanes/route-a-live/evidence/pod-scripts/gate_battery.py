"""route-a-live: the cell gate (tools/cell_gate.py, with --rust and --flock) over every session of a run, plus the
negatives that need whole records: a stale prime state (a coin before its commitment), prime coins replayed across
sessions (one session's proof against another's record), a Fiat-Shamir prime prover against the live verifier, and
tampered records (prime words, prime order, a prime state, a Flock coin, the public words and y re-sealed).

Run from backends/gkr (cwd).  Writes OUT/battery.json and OUT/battery.tsv; exit 0 iff every case has its expected outcome.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

P = 2013265921


def rf_of_link_txt(p: Path) -> str | None:
    for ln in p.read_text().splitlines():
        if ln.startswith("root_f_sha256 "):
            return ln.split()[1]
    return None


def reseal(rec: dict) -> None:
    ln = rec["link"]
    le = lambda h: bytes.fromhex(h[16:])[::-1] + bytes.fromhex(h[:16])[::-1]   # noqa: E731  {hi}{lo} hex -> lo LE, hi LE
    b = bytes.fromhex(ln["root_f"]) + b"".join(bytes.fromhex(ln["root_b"][t]) for t in sorted(ln["root_b"]))
    b += b"".join(le(c) for p in ln["points"] for c in p) + b"".join(le(y) for y in ln["y"])
    rec["link_sha256"] = hashlib.sha256(b).hexdigest()


def flip_hex(h: str) -> str:
    return h[:-1] + ("1" if h[-1] == "0" else "0")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--neg-stale", default=None)
    ap.add_argument("--statement", required=True)
    ap.add_argument("--digests", required=True)
    ap.add_argument("--prime-commitment", required=True)
    ap.add_argument("--vus", type=int, required=True)
    ap.add_argument("--rust", required=True)
    ap.add_argument("--flock", required=True)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--producer", action="append", default=[])
    ap.add_argument("--gate", default="tools/cell_gate.py")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    recs = {}
    for d in sorted(Path(a.sessions).glob("l*")):
        r = json.loads((d / "session.json").read_text())
        rf = (r.get("link") or {}).get("root_f_sha256")
        recs[d.name] = (d, r, rf)
    provers = {}
    for base in [Path(a.cells)] + ([Path(a.neg_stale)] if a.neg_stale else []):
        for s in sorted(base.glob("s*")):
            if (s / "link.txt").is_file() and (s / "proof.bin").is_file():
                t = json.loads((s / "times.json").read_text()) if (s / "times.json").is_file() else {}
                provers[f"{base.name}/{s.name}"] = (s / "proof.bin", rf_of_link_txt(s / "link.txt"), t.get("warmup"))
    pair = {name: next((k for k, (_, _, rf) in recs.items() if rf and rf == prf), None) for name, (_, prf, _) in provers.items()}

    def gate(session: Path, proof: Path, tag: str) -> dict:
        g = out / tag
        cmd = [sys.executable, a.gate, "--session", str(session), "--sigma", str(Path(a.statement) / "sigma.txt"), "--out", str(g),
               "--rust", a.rust, "--statement", a.statement, "--proof", str(proof), "--vus", str(a.vus), "--threads", str(a.threads),
               "--flock", a.flock, "--digests", a.digests, "--prime-commitment", a.prime_commitment]
        for p in a.producer:
            cmd += ["--producer", p]
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return json.loads((g / "gate.json").read_text())
        except FileNotFoundError:
            return {"admitted": False, "checks": {}, "error": r.stderr[-400:]}

    rows = []

    def case(name: str, doc: dict, want_fail: list[str], want_ok: list[str] | None = None, why: str = "") -> None:
        ch = doc.get("checks") or {}
        ok_fail = all(not (ch.get(k) or {}).get("ok", False) for k in want_fail)
        ok_ok = all((ch.get(k) or {}).get("ok") for k in (want_ok or []))
        hit = all(why in (ch.get(k) or {}).get("detail", "") for k in want_fail[:1]) if why else True
        rows.append({"case": name, "expect_fail": want_fail, "expect_ok": want_ok or [], "pass": ok_fail and ok_ok and hit,
                     "details": {k: (ch.get(k) or {}).get("detail", "")[:300] for k in set(want_fail) | set(want_ok or [])},
                     "failed_checks": sorted(k for k, v in ch.items() if not v.get("ok"))})

    # warm-ups ran against a loopback verifier whose records are not in --sessions
    honest = [n for n in provers if n.startswith(Path(a.cells).name + "/") and not (provers[n][2] and pair[n] is None)]
    everything_but_producer = ["exchange", "gated", "sigma", "accepted", "context", "preserved", "prime_live", "replayable", "prime", "flock_replay"]
    admitted = []
    for n in honest:
        k = pair[n]
        if k is None:
            rows.append({"case": f"honest {n}", "pass": False, "details": {"pairing": "no record with this root_F"}})
            continue
        doc = gate(recs[k][0], provers[n][0], f"honest-{n.replace('/', '-')}")
        case(f"honest {n} <- record {k}", doc, ["non_producer"], everything_but_producer)
        admitted.append((n, k))
    if a.neg_stale:
        for n in [x for x in provers if x.startswith(Path(a.neg_stale).name + "/")]:
            k = pair[n]
            if k:
                case(f"neg stale prime state (coin before its commitment) {n} <- {k}", gate(recs[k][0], provers[n][0], f"neg-stale-{n.replace('/', '-')}"),
                     ["prime"], ["accepted", "prime_live", "flock_replay"], why="R2-prime")
    fs = [k for k, (_, r, _) in recs.items() if "R7" in str(r.get("aborted") or "")]
    if a.neg_stale:  # the probe mode's sessions include the Fiat-Shamir prover's; a sweep's do not
      rows.append({"case": "neg fiat-shamir prime prover against the live verifier (hello pins prime: live-coins/v1)", "pass": bool(fs),
                 "details": {"records": fs, "aborted": [recs[k][1].get("aborted", "")[:200] for k in fs]}})
    if len(admitted) >= 2:
        (na, ka), (nb, kb) = admitted[0], admitted[1]
        case(f"neg prime coins across sessions: proof {na} against record {kb}", gate(recs[kb][0], provers[na][0], "neg-cross"),
             ["prime"], ["flock_replay"], why="R2-prime")
    if admitted:
        n0, k0 = admitted[0]
        src, base = recs[k0][0], recs[k0][1]

        def tampered(tag: str, f) -> dict:
            d = out / "tamper" / tag
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(src, d)
            r = copy.deepcopy(base)
            f(r)
            (d / "session.json").write_text(json.dumps(r, indent=1))
            return gate(d, provers[n0][0], f"tamper-{tag}")

        def word(r):
            w = r["prime"]["rounds"][3]["words"]
            w[0] = (w[0] + 1) % P
        # a coin feeds the verifier's next check before the next round's state comparison: rejected by that check
        case("tampered record: a prime coin word", tampered("prime-word", word), ["prime"], ["flock_replay"])
        case("tampered record: prime before_commit - 1", tampered("prime-before", lambda r: r["prime"].update(before_commit=r["prime"]["before_commit"] - 1)),
             ["prime"], ["flock_replay"], why="root_F follows")
        case("tampered record: a prime state", tampered("prime-state", lambda r: r["prime"]["rounds"][2].update(state=flip_hex(r["prime"]["rounds"][2]["state"]))),
             ["prime"], ["flock_replay"], why="R2-prime")

        def coin(r):
            st = next(s for s in r["streams"] if s["stream"] == "chain/rep0")
            st["rounds"][3]["coins"][0] = flip_hex(st["rounds"][3]["coins"][0])
        case("tampered record: a Flock coin", tampered("flock-coin", coin), ["flock_replay"], ["prime"])

        def publics(r):
            p = r["link"]["publics"]["chain"]
            p = p[:64] + flip_hex(p[64:66]) + p[66:]
            r["link"]["publics"]["chain"] = p
            r["link"]["publics_sha256"]["chain"] = hashlib.sha256(bytes.fromhex(p)).hexdigest()
        case("tampered record: a committed public word (hash re-sealed)", tampered("publics", publics), ["flock_replay"], ["replayable"])

        def ytamper(r):
            r["link"]["y"][1] = flip_hex(r["link"]["y"][1])
            reseal(r)
        case("tampered record: y (link_sha256 re-sealed)", tampered("y", ytamper), ["flock_replay", "prime"])
        case("tampered record: prime rounds dropped (a Fiat-Shamir record)", tampered("prime-dropped", lambda r: r.update(prime=None)),
             ["prime_live", "prime"])
    ok = all(r["pass"] for r in rows)
    (out / "battery.json").write_text(json.dumps({"kind": "route-a-live-gate-battery/v1", "all_pass": ok, "cases": rows}, indent=1))
    with open(out / "battery.tsv", "w") as fh:
        for r in rows:
            fh.write(f"{'PASS' if r['pass'] else 'FAIL'}\t{r['case']}\t{json.dumps(r.get('failed_checks'))}\t{json.dumps(r['details'])[:400]}\n")
    print((out / "battery.tsv").read_text())
    print("BATTERY", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
