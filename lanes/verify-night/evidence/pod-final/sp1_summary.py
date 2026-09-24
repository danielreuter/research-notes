"""verify-night: one line per SP1 verify in a verify.out (09 / 13 / 16): ok, statement_match, verdict, unsound, vk_hash, seconds.
Accepted = ok and statement_match and verdict and not unsound (the stock host exits 0 when statement_match is false)."""
import json
import sys

cur = None
for line in open(sys.argv[1]):
    if line.startswith("--- "):
        cur = line[4:].strip()
    elif line.startswith("{") and cur:
        d = json.loads(line)
        acc = bool(d.get("ok")) and d.get("statement_match") is not False and bool(d.get("verdict")) and not d.get("unsound")
        secs = d.get("verify_seconds", d.get("seconds", ""))
        print(f"{cur[:56]:56s} ok={d.get('ok')} stmt={d.get('statement_match')} verdict={d.get('verdict')} "
              f"unsound={d.get('unsound')} vk={str(d.get('vk_hash'))[:12]} s={secs} -> {'ACCEPT' if acc else 'REJECT'}")
        cur = None
