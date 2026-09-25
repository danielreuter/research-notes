"""Point every importer of check/commit_verdict at its new home (import lines only) and move / drop the lint allowlist entries
of the absorbed module.  Run after absorb.py: uvx --python 3.12 python absorb_imports.py"""
import json
import re
from pathlib import Path

R = Path.home() / "projects/verity-wt/rf-b2v/integrations/vllm"
C2_NAMES = {"_complete_replay_population_gap", "_no_evaluator_gaps", "_form_b_selector_coverage", "_form_b_complete_over_values",
            "_query_population_scope", "_replay_seed_of_record"}
CR_NAMES = {"REQUIRED_CLASSES_DEFAULT", "class_coverage", "required_classes_default", "binding_check"}
V_NAMES = {"commit_verdict"}

LINE = re.compile(r"^(?P<ind>\s*)from verity_vllm\.check\.commit_verdict import (?P<names>[A-Za-z_, ]+?)(?P<tail>\s*(#.*)?)$")


def rewrite(line):
    m = LINE.match(line)
    if not m:
        return line
    names = [n.strip() for n in m.group("names").split(",") if n.strip()]
    unknown = set(names) - C2_NAMES - CR_NAMES - V_NAMES
    assert not unknown, (line, unknown)
    out = []
    for mod, pool in (("c2_rules", C2_NAMES), ("commit_rules", CR_NAMES), ("verdict", V_NAMES)):
        mine = [n for n in names if n in pool]
        if mine:
            out.append(m.group("ind") + "from verity_vllm.check." + mod + " import " + ", ".join(mine))
    tail = m.group("tail").strip()
    if tail:
        noqa = re.match(r"#\s*noqa: E402", tail)
        out = [o + ("  # noqa: E402" if noqa and i < len(out) - 1 else "") for i, o in enumerate(out)]
        out[-1] += "  " + tail
    return "\n".join(out)


files = sorted({*R.glob("tests/**/*.py"), R / "verity_vllm/pipeline/commit.py", R / "verity_vllm/pipeline/tp/commit.py"})
for p in files:
    s = p.read_text()
    if "check.commit_verdict import" not in s:
        continue
    t = "\n".join(rewrite(ln) for ln in s.split("\n"))
    assert "check.commit_verdict" not in t, p
    p.write_text(t)
    print(p.relative_to(R))
