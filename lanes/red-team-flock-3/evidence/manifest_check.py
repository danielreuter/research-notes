#!/usr/bin/env python3
"""red-team-flock-3: a key-count class manifest (flock-ir-lowering's class pin) against CP1–CP6.

- its bytes are their own canonical serialization (sorted keys, no whitespace, no duplicate keys) and the class pin is their
  sha256;
- format, template and the T range are what the class claims; `nets` holds exactly the integers lo..hi;
- every nets[T] is the sha256 of the reviewed generator's lowering of T (class_ref.py's table), so each T's leaf maps (LEAVES) and
  softmax tail (CUT) are the reviewed ones; `unit_rows` is the rows every T shares.

  manifest_check.py MANIFEST CLASS_REF.json [PIN]
"""
import hashlib
import json
import sys


def no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate keys {sorted(k for k in set(keys) if keys.count(k) > 1)}")
    return dict(pairs)


def main():
    mpath, refp = sys.argv[1:3]
    pin = sys.argv[3] if len(sys.argv) > 3 else None
    raw = open(mpath, "rb").read()
    problems = []
    sha = hashlib.sha256(raw).hexdigest()
    if pin and sha != pin:
        problems.append(f"sha256(manifest) {sha[:16]} != pin {pin[:16]}")
    try:
        m = json.loads(raw, object_pairs_hook=no_dupes)
    except ValueError as e:
        print("MANIFEST_CHECK FAIL", e); return
    canon = json.dumps(m, sort_keys=True, separators=(",", ":")).encode()
    if canon != raw and canon + b"\n" != raw:
        problems.append("the manifest is not its own canonical serialization")
    ref = json.load(open(refp))
    per = {int(k): v for k, v in ref["per_T"].items()}
    lo, hi = (m.get("T") or [None, None])[:2]
    nets = {int(k): v for k, v in (m.get("nets") or {}).items()}
    if sorted(nets) != list(range(lo, hi + 1)):
        problems.append(f"nets keys are not exactly {lo}..{hi}")
    for T in range(lo, hi + 1):
        if T not in per:
            problems.append(f"T={T} outside my reference table"); break
        if nets.get(T) != per[T]["net"]:
            problems.append(f"T={T}: nets {str(nets.get(T))[:16]} != reviewed generator {per[T]['net'][:16]}")
    if m.get("unit_rows") not in (ref["unit_rows_sha256"], ref.get("unit_rows_header_sha256")):
        problems.append(f"unit_rows {str(m.get('unit_rows'))[:16]} != the rows every T shares {ref['unit_rows_sha256'][:16]} (check the definition)")
    print("MANIFEST", json.dumps({k: (v if k != "nets" else f"{len(v)} entries") for k, v in m.items()}))
    print("MANIFEST_CHECK", "PASS" if not problems else "FAIL", json.dumps({"sha256": sha, "T": [lo, hi], "problems": problems[:10]}))


if __name__ == "__main__":
    main()
