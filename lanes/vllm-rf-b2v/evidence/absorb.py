"""Absorb check/commit_verdict.py into check/verdict.py (the decision, as phase functions) + check/commit_rules.py (C1 helpers,
runtime-match / coverage / identity rules) + check/c2_rules.py (C2 helpers, C2 and execution-extent rules).  Text slicing only; line
numbers are those of 6e33c657.  Run from anywhere: uvx --python 3.12 python absorb.py"""
import re
from pathlib import Path

R = Path.home() / "projects/verity-wt/rf-b2v/integrations/vllm"
CK = R / "verity_vllm/check"
V = (CK / "verdict.py").read_text().splitlines(keepends=True)
C = (CK / "commit_verdict.py").read_text().splitlines(keepends=True)
assert len(V) == 1401 and len(C) == 713, (len(V), len(C))


def v(a, b):
    return "".join(V[a - 1:b])


def c(a, b):
    return "".join(C[a - 1:b])


def expect(s, *needles):
    for n in needles:
        assert n in s, n
    return s


# ------------------------------------------------------------------------------------------------ anchors (fail loudly if the base moved)
assert V[166].startswith("#: what a FAIL of each rule"), V[166]
assert V[189].startswith("    return REJECT.get(name)"), V[189]
assert V[252].startswith("# ----") and "helpers" in V[252]
assert V[262].startswith("def _d("), V[262]
assert V[327].startswith("# ----") and "the rules" in V[327]
assert V[772].startswith("def _replay_scope("), V[772]
assert V[961].startswith("def execution_extent_rules("), V[961]
assert V[1040].startswith("def run_checks("), V[1040]
assert V[1061].startswith("# ----") and "aggregation" in V[1061]
assert C[27].startswith("# The interim required-value manifest"), C[27]
assert C[108].startswith("    return True, \"PASS\""), C[108]
assert C[111].startswith("_POPULATION_GAP_CLASSES"), C[111]
assert C[145].startswith("def _is_token_select("), C[145]
assert C[153].startswith("def _no_evaluator_reasons("), C[153]
assert C[462].startswith("def _b2_attribution_note("), C[462]
assert C[488].startswith("def commit_verdict("), C[488]


def cv_to(prefix_map, s):
    """`CV.name` -> the name in its new home (`name` when local, `CR.name` / `C2.name` when imported as a module)."""
    def sub(m):
        name = m.group(1)
        return prefix_map.get(name, "") + name
    return re.sub(r"\bCV\.([A-Za-z_][A-Za-z0-9_]*)", sub, s)


RENAME = {"_b2_attribution_note": "_batch_attribution_note"}


def renamed(s):
    for a, b in RENAME.items():
        s = re.sub(rf"\b{a}\b", b, s)
    return s


# ------------------------------------------------------------------------------------------------ check/commit_rules.py
commit_rules = (
    '"""The rules of one instrumented run\'s Commit record, each a `CheckResult`: runtime match, required-value coverage and program\n'
    "source identity, with the C1 helpers the decision (`verdict.commit_verdict`) shares.\n"
    "\n"
    "`expected_tensors` counts the acquisitions the collector attempted, so a required producer that never fires contributes 0 to both\n"
    "sides.  The required classes close that gap: every required class must be declared by the committer's coverage declaration, and\n"
    "every declared class that binds leaves (`bound-as-leaf` / `registered-input`) must have `tensors > 0`.\"\"\"\n"
    "from __future__ import annotations\n"
    "\n"
    "from typing import Any, Mapping\n"
    "\n"
    "from verity.verification.codes import VerificationCode as VC\n"
    "\n"
    "from verity_vllm.check.result import FAIL, INSUFFICIENT, NOT_RUN, PASS, CheckResult, code_of\n"
    "\n"
    + c(28, 109)
    + "\n\n"
    + v(167, 190)
    + "\n\n"
    + v(253, 253)
    + "\n"
    + v(263, 327)
    + cv_to({}, v(328, 771)).replace(
        "# Every function mirrors ONE predicate of commit_verdict.commit_verdict (cited by its line's comment tag)",
        "# Every function mirrors ONE predicate of verdict.commit_verdict (cited by its line's comment tag)")
)
commit_rules = commit_rules.rstrip("\n") + "\n"
expect(commit_rules, "def binding_check(", "def rule_manifest_verified(", "REJECT: dict[str, VC]", "def _mk(")
assert "CV." not in commit_rules

# ------------------------------------------------------------------------------------------------ check/c2_rules.py
c2_helpers = c(112, 143) + "\n\n" + c(154, 486)
c2_helpers = c2_helpers.replace("_is_token_select(fam)", "is_token_select(fam)")
assert "_is_token_select" not in c2_helpers
C2_LOCAL = {}
c2_rules = (
    '"""The C2 rules of one instrumented run\'s Commit record (local replay, boundary linkage, weights of record) and its execution\n'
    "extent, each a `CheckResult`, with the helpers the decision (`verdict.commit_verdict`) shares: form (B) coverage of the replay's named\n"
    "gaps, the seed of record, the population scope against Q(P).\n"
    "\n"
    "The rules decide from the structured codes the sampled replay stamps on its record (`replay_codes`: the class / family / domain of\n"
    'every not-evaluable reason, the classes of every unevaluated stratum, the seed form), never from its message texts."""\n'
    "from __future__ import annotations\n"
    "\n"
    "from typing import Any\n"
    "\n"
    "from verity_vllm.check.commit_rules import IMPORTS_CR\n"
    "from verity_vllm.check.replay import replay_codes as RC\n"
    "from verity_vllm.check.result import FAIL, INSUFFICIENT, NOT_RUN, PASS, CheckResult\n"
    "from verity_vllm.query.manifest.format import is_token_select\n"
    "\n"
    + renamed(c2_helpers)
    + "\n\n"
    + renamed(cv_to(C2_LOCAL, v(773, 1039)))
)
c2_rules = c2_rules.rstrip("\n") + "\n"
assert "CV." not in c2_rules
expect(c2_rules, "def _query_population_scope(", "def c2_rules(", "def execution_extent_rules(", "def _batch_attribution_note(")

# ------------------------------------------------------------------------------------------------ check/verdict.py
head = v(1, 39).replace(
    "every rule here is `verity_vllm.check.commit_verdict.commit_verdict`'s own predicate, evaluated",
    "every rule (`check.commit_rules`, `check.c2_rules`) is `commit_verdict`'s own predicate, evaluated")
assert "check.commit_verdict" not in head
imports = expect(v(40, 56), "from verity_vllm.check import commit_verdict as CV\n").replace(
    "from verity_vllm.check import commit_verdict as CV\n",
    "from verity_vllm.check import c2_rules as C2\n"
    "from verity_vllm.check import commit_rules as CR\n"
    "from verity_vllm.check.commit_rules import _d, _int\n")

run_checks = v(1041, 1059).replace(
    "Every rule of `commit_verdict.commit_verdict` (+ commit_delta's", "Every rule of `commit_verdict` (+ commit_delta's")
run_checks = re.sub(r"(?<![.\w])(rule_[a-z0-9_]+)\(", r"CR.\1(", run_checks)
run_checks = run_checks.replace("checks += c2_rules(commit, ctx)", "checks += C2.c2_rules(commit, ctx)").replace(
    "checks += execution_extent_rules(commit, ctx)", "checks += C2.execution_extent_rules(commit, ctx)")
assert run_checks.count("CR.rule_") == 16, run_checks.count("CR.rule_")

# the decision: commit_verdict() in three phases, each returning (False, first failing reason) or None
cv_doc = c(491, 495)
p1 = c(496, 496) + c(498, 553)
p2 = c(554, 672)
p3 = c(673, 710)
assert C[496].strip().startswith("c2_notes: list[str] = []"), C[496]
assert C[553].strip().startswith("vc = commit.get(\"value_correspondence\")"), C[553]
assert C[672].strip().startswith("if oar is not None:"), C[672]
assert C[709].strip().startswith("return False, \"picks deferred to replay"), C[709]
CR_NAMES = ("binding_check", "json_short", "required_classes_check", "REQUIRED_CLASSES_DEFAULT")
C2_NAMES = ("_replay_seed_of_record", "_form_b_complete_over_values", "_complete_replay_population_gap", "_partial_replay_named_gap",
            "_b2_attribution_note", "_query_population_scope")


def qualify(s):
    for n in CR_NAMES:
        s = re.sub(rf"(?<![.\w]){n}\b", f"CR.{n}", s)
    for n in C2_NAMES:
        s = re.sub(rf"(?<![.\w]){n}\b", f"C2.{n}", s)
    return renamed(s)


decision = (
    "def commit_verdict(commit: dict, tokens_equal: bool | None, *, min_openings: int = 64, declaration: dict | None = None,\n"
    "                   required_classes: tuple[str, ...] | list[str] | None = None) -> tuple[bool, str]:\n"
    + cv_doc
    + "    c2_notes: list[str] = []                               # named gaps carried on a PASS (form (B) covered a partial replay)\n"
    "    fail = (_c1_verdict(commit, tokens_equal, min_openings, declaration, required_classes) or _c2_verdict(commit, c2_notes)\n"
    "            or _after_release_verdict(commit, min_openings))\n"
    "    if fail is not None:\n"
    "        return fail\n"
    "    if c2_notes:\n"
    "        return True, \"PASS (\" + \"; \".join(c2_notes) + \")\"\n"
    "    return True, \"PASS\"\n"
    "\n\n"
    "def _c1_verdict(commit: dict, tokens_equal: bool | None, min_openings: int, declaration: dict | None,\n"
    "                required_classes: tuple[str, ...] | list[str] | None) -> tuple[bool, str] | None:\n"
    "    \"\"\"Reference integrity, identity coverage, collector errors, required classes, bounded staging, openings, tokens.\"\"\"\n"
    + qualify(p1)
    + "    return None\n"
    "\n\n"
    "def _c2_verdict(commit: dict, c2_notes: list[str]) -> tuple[bool, str] | None:\n"
    "    \"\"\"Value correspondence, the C2 of record (sampled replay, boundary linkage, weights of record) and its population scope.\"\"\"\n"
    "    bnd = commit.get(\"binding\")\n"
    + qualify(p2)
    + "    return None\n"
    "\n\n"
    "def _after_release_verdict(commit: dict, min_openings: int) -> tuple[bool, str] | None:\n"
    "    \"\"\"Openings after the raw device staging was released, and every pick deferred to replay.\"\"\"\n"
    "    ops = commit.get(\"openings\") or {}\n"
    "    oar = commit.get(\"openings_after_release\")\n"
    "    bnd = commit.get(\"binding\")\n"
    + qualify(p3)
    + "    return None\n"
)
assert "c2_notes: list[str] = []" not in qualify(p1)

verdict = (
    head
    + imports
    + v(57, 166)
    + v(193, 262)
    + run_checks
    + "\n\n"
    + decision
    + "\n\n"
    + v(1062, 1401)
)
verdict = verdict.replace("return cls(checks=[CheckResult.from_dict(c, reject_of(c))", "return cls(checks=[CheckResult.from_dict(c, CR.reject_of(c))")
assert "CV." not in verdict and "reject_of(c))" in verdict

# the names c2_rules takes from commit_rules
used = sorted({n for n in re.findall(r"(?<![.\w])(_[a-z_]+|[a-z_]+)\(", c2_rules)} & {
    "_d", "_int", "_first", "_components", "_replay_of", "_linkage_of", "_oracle_of", "_is_row_procedure", "_base_inputs", "_leak", "_mk"})
c2_rules = c2_rules.replace("IMPORTS_CR", ", ".join(used))

(CK / "commit_rules.py").write_text(commit_rules)
(CK / "c2_rules.py").write_text(c2_rules)
(CK / "verdict.py").write_text(verdict)
(CK / "commit_verdict.py").unlink()
for name, s in (("commit_rules.py", commit_rules), ("c2_rules.py", c2_rules), ("verdict.py", verdict)):
    print(name, s.count("\n"))
print("c2_rules imports from commit_rules:", used)
