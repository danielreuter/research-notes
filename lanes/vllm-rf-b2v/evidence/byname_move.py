"""Move the by-name allowlist entries of the noninterference family helpers to noninterference_families.py (FINAL_NORM_MODULES
now lives there, public).  Line-based: one entry per line, edited in place, nothing reordered."""
import json
import sys

P = sys.argv[1]
NI, FAM = "verity_vllm/properties/noninterference.py", "verity_vllm/properties/noninterference_families.py"
lines = open(P).read().split("\n")
moves = {  # (kind, symbol, pattern) of a noninterference.py entry -> field updates
    ("model-name", "<module>", r"^\^gpt_neox\\\.layers\\\.\(\\d\+\)\$$"): {"file": FAM},
    ("model-name", "<module>", r"^gpt_neox\.final_layer_norm$"): {"file": FAM},
    ("path-predicate", "_unfused_norm_boundaries", None): {"file": FAM, "symbol": "unfused_norm_boundaries"},
    ("path-predicate", "hooks_boundary_hashes", r'^r\["module"\]\ in\ _FINAL_NORM_MODULES$'):
        {"pattern": r'^r\["module"\]\ in\ FINAL_NORM_MODULES$'},
    ("path-predicate", "run_hooks_variant", r"^name\ in\ _FINAL_NORM_MODULES$"): {"pattern": r"^name\ in\ FINAL_NORM_MODULES$"},
    ("table", "_FINAL_NORM_MODULES", None): {"file": FAM, "symbol": "FINAL_NORM_MODULES", "pattern": "^FINAL_NORM_MODULES$"},
    ("table", "_NEOX_LAYER_RE", None): {"file": FAM},
    ("table", "_POST_FF_RE", None): {"file": FAM},
    ("table", "_PRE_FF_RE", None): {"file": FAM},
}
done = set()
for i, ln in enumerate(lines):
    s = ln.strip()
    if not s.startswith("{") or f'"file": "{NI}"' not in s:
        continue
    e = json.loads(s.rstrip(","))
    for (kind, sym, pat), upd in moves.items():
        if e["kind"] == kind and e["symbol"] == sym and (pat is None or e["pattern"] == pat):
            assert (kind, sym, pat) not in done, (kind, sym, pat)
            e.update(upd)
            indent = ln[: len(ln) - len(ln.lstrip())]
            lines[i] = indent + json.dumps(e, ensure_ascii=False) + ("," if s.endswith(",") else "")
            done.add((kind, sym, pat))
missing = set(moves) - done
assert not missing, missing
open(P, "w").write("\n".join(lines))
print("moved/updated", len(done))
