"""Move / drop the lint registry and allowlist entries of the absorbed check/commit_verdict.py.
Run after absorb.py: uvx --python 3.12 python absorb_allow.py"""
import json
import re
from pathlib import Path

R = Path.home() / "projects/verity-wt/rf-b2v/integrations/vllm"


def sub_once(path, a, b):
    s = path.read_text()
    assert s.count(a) == 1, (path, a)
    path.write_text(s.replace(a, b))


sub_once(R / "tests/lint/_imports.py",
         'VERDICT_MODULES = ("verity_vllm.check.verdict", "verity_vllm.check.commit_verdict", "verity_vllm.check.gates")',
         'VERDICT_MODULES = ("verity_vllm.check.verdict", "verity_vllm.check.commit_rules", "verity_vllm.check.c2_rules", "verity_vllm.check.gates")')
sub_once(R / "tests/lint/test_p04_one_result.py",
         "absorbs (``_imports.VERDICT_MODULES``: ``check.verdict``, ``check.commit_verdict``, ``check.gates``) is a violation.",
         "absorbs (``_imports.VERDICT_MODULES``: ``check.verdict``, ``check.commit_rules``, ``check.c2_rules``, ``check.gates``) is a violation.")

CV = "verity_vllm/check/commit_verdict.py"
VD = "verity_vllm/check/verdict.py"
CRF = "verity_vllm/check/commit_rules.py"
C2F = "verity_vllm/check/c2_rules.py"
TO_CR = {"binding_check", "required_classes_default", "rule_compiled_check", "rule_identity_layout", "rule_manifest_coverage"}
TO_C2 = {"_b2_attribution_note", "_complete_replay_population_gap", "_form_b_complete_over_values", "_form_b_selector_coverage",
         "_no_evaluator_gaps", "_partial_replay_named_gap", "_replay_seed_of_record", "_query_population_scope", "execution_extent_rules",
         "c2_rules"}


def moved(e):
    f, sym, kind = e["file"], e["symbol"], e["kind"]
    if f == CV and kind in ("broad-except", "function") and sym in ("_is_token_select", "commit_verdict"):
        return []
    if f == CV and sym == "<module>" and kind == "doc-round":
        return []
    if f == CV and kind == "def-name" and e["detail"] == "_b2_attribution_note":
        return []
    if f == CV and kind == "verdict-import":
        return [{**e, "file": C2F, "detail": e["detail"].replace("verity_vllm.check.commit_verdict ->", "verity_vllm.check.c2_rules ->")}]
    if f in (CV, VD) and sym in TO_C2:
        return [{**e, "file": C2F, "symbol": "_batch_attribution_note" if sym == "_b2_attribution_note" else sym}]
    if f in (CV, VD) and sym in TO_CR:
        return [{**e, "file": CRF}]
    assert f != CV, e
    return [e]


def edit_entries(path):
    lines = path.read_text().split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip().startswith('"entries": ['))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() in ("]", "],"))
    entries = [json.loads(ln.strip().rstrip(",")) for ln in lines[start + 1:end]]
    key = lambda e: (e["file"], e["kind"], e["symbol"], e["detail"])
    new, relocate = [], []
    for e in entries:
        for x in moved(e):
            (relocate if x["file"] != e["file"] else new).append(x)
    if new == entries:
        return
    for x in relocate:                     # only the moved entries move: before the first entry that sorts after them
        i = next((i for i, e in enumerate(new) if key(e) > key(x)), len(new))
        new.insert(i, x)
    ind = re.match(r"\s*", lines[start + 1]).group(0)
    body = [ind + json.dumps(e, ensure_ascii=False) + ("," if i < len(new) - 1 else "") for i, e in enumerate(new)]
    path.write_text("\n".join(lines[:start + 1] + body + lines[end:]))
    print(path.name, len(entries), "->", len(new))


for name in ("p04_one_result", "p07_declared_inputs", "p08_facts", "p10_size", "p11_names"):
    edit_entries(R / "tests/lint/allowlists" / (name + ".json"))

bn = R / "tests/by_name_allowlist.json"
out = []
for ln in bn.read_text().split("\n"):
    if CV in ln:
        e = json.loads(ln.strip().rstrip(","))
        if e["symbol"] == "_is_token_select":
            continue
        assert e["symbol"] == "_complete_replay_population_gap", e
        ln = ln.replace(CV, C2F)
    out.append(ln)
bn.write_text("\n".join(out))
print("by_name_allowlist edited")
