"""Per rule P1-P12: scan() vs the allowlist -> keys found more often than allowed, and entries allowing more than found."""
import importlib
import sys
from collections import Counter

sys.path.insert(0, ".")  # integrations/vllm
from tests.lint import _ratchet as R  # noqa: E402

RULES = ["p01_core_abstractions", "p02_value_checks", "p03_one_evaluator", "p04_one_result", "p05_properties", "p06_one_cli",
         "p07_declared_inputs", "p08_facts", "p09_layering", "p10_size", "p11_names", "p12_shared_keys"]
total_bad = 0
for name in RULES:
    mod = importlib.import_module(f"tests.lint.test_{name}")
    allow = R.load_allowlist(name)
    if name == "p10_size":
        have = Counter({k: v for k, v in mod.sizes().items()})
        over = {k: v for k, v in have.items() if k not in allow or v > allow[k]}
        under = {k: c for k, c in allow.items() if k not in have or have[k] < c}
    else:
        have = Counter(v.key for v in mod.scan())
        over = {k: v for k, v in have.items() if v > allow.get(k, 0)}
        under = {k: c for k, c in allow.items() if have.get(k, 0) < c}
    print(f"{name}: entries {len(allow)}, allowed total {sum(allow.values())}, found keys {len(have)}, found total {sum(have.values())}")
    for k, v in sorted(over.items()):
        print(f"   ADD/RAISE {R.entry_line(k, v)}   (allowed {allow.get(k, 0)})"); total_bad += 1
    for k, c in sorted(under.items()):
        print(f"   DEL/LOWER {R.entry_line(k, c)}   (found {have.get(k, 0)})"); total_bad += 1
print("problems:", total_bad)
