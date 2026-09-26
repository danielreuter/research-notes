"""Compare two pytest JUnit XML files (xunit1, plain or .gz): outcome per test id, tests only on one side, skip reasons.

usage: python3 jdiff.py BASE.xml[.gz] HEAD.xml[.gz] [--ignore-prefix PREFIX ...]

Exit 0 when HEAD has no new failure and no new skip against BASE:
  new failure  a test failed or errored on HEAD that did not fail or error on BASE (a test new on HEAD included);
  new skip     a test skipped on HEAD that was not skipped on BASE (a test new on HEAD included), or a skip reason
               (paths normalised) that BASE does not have.
Improvements (failed -> passed, skipped -> passed) and tests only in BASE (deleted) are listed but do not fail.
Tests in UNSTABLE are listed but never fail the comparison.
"""
import collections
import gzip
import re
import sys
import xml.etree.ElementTree as ET

BAD = ("failed", "error")

# Their outcome at 72884c8a depends on test order or heap state; baseline.md, "Order-dependent outcomes".
UNSTABLE = frozenset({
    "tests.harness.test_admit_r19_host_working_set::test_fork_gc_freeze_opt_out_is_named_on_the_record",
    "tests.harness.test_admit_r19_host_working_set::"
    "test_forked_children_inherit_a_frozen_heap_and_the_parent_unfreezes_after_the_pool_joins",
    "tests.observe.test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation",
    "tests.program.test_lifted_tiny::test_specified_list_is_closed",
})


def outcomes(path):
    with (gzip.open(path) if path.endswith(".gz") else open(path, "rb")) as f:
        root = ET.parse(f).getroot()
    out, reasons = {}, {}
    for tc in root.iter("testcase"):
        tid = f"{tc.get('classname')}::{tc.get('name')}"
        kind, msg = "passed", ""
        for child in tc:
            if child.tag in ("failure", "error"):
                kind, msg = ("failed" if child.tag == "failure" else "error"), (child.get("message") or "")
                break
            if child.tag == "skipped":
                kind = "xfailed" if "xfail" in (child.get("type") or "") else "skipped"
                msg = child.get("message") or ""
        if tid in out and out[tid] != kind:
            kind = "error" if "error" in (kind, out[tid]) else kind
        out[tid] = kind
        reasons[tid] = msg
    return out, reasons


def norm(reason):
    return re.sub(r"\s+", " ", re.sub(r"/[\w./-]+", "<path>", reason))[:160]


def main():
    args = sys.argv[1:]
    ignore = []
    while "--ignore-prefix" in args:
        i = args.index("--ignore-prefix")
        ignore.append(args[i + 1])
        del args[i:i + 2]
    base_p, head_p = args
    a, ra = outcomes(base_p)
    b, rb = outcomes(head_p)
    for name, o in (("base", a), ("head", b)):
        print(name, len(o), dict(sorted(collections.Counter(o.values()).items())))
    only_a = sorted(set(a) - set(b))
    new_b = sorted(set(b) - set(a))
    shown_b = [t for t in new_b if not any(t.startswith(p) for p in ignore)]
    print(f"only in base (deleted or renamed): {len(only_a)}")
    for t in only_a:
        print("  -", t, a[t])
    print(f"only in head: {len(new_b)} {dict(collections.Counter(b[t] for t in new_b))}"
          + (f", listed below except those under {ignore}" if ignore else ""))
    for t in shown_b:
        print("  +", t, b[t])
    changed = sorted(t for t in set(a) & set(b) if a[t] != b[t])
    print(f"outcome changed: {len(changed)}")
    for t in changed:
        mark = "  (order-dependent at base; not counted)" if t in UNSTABLE else ""
        print(f"  ~ {t}: {a[t]} -> {b[t]}  [{norm(rb[t] or ra[t])}]{mark}")
    new_fail = sorted(t for t in b if b[t] in BAD and a.get(t) not in BAD and t not in UNSTABLE)
    new_skip = sorted(t for t in b if b[t] == "skipped" and a.get(t) != "skipped" and t not in UNSTABLE)
    sa = collections.Counter(norm(ra[t]) for t in a if a[t] == "skipped")
    sb = collections.Counter(norm(rb[t]) for t in b if b[t] == "skipped" and t not in UNSTABLE)
    new_reasons = sorted(set(sb) - set(sa))
    print(f"new failures on head: {len(new_fail)}")
    for t in new_fail:
        print(f"  ! {t}: {a.get(t, 'absent')} -> {b[t]}  [{norm(rb[t])}]")
    print(f"new skips on head: {len(new_skip)}; skip reasons new on head: {len(new_reasons)}")
    for t in new_skip:
        print(f"  s {t}: {a.get(t, 'absent')} -> skipped  [{norm(rb[t])}]")
    for r in new_reasons:
        print(f"  {sb[r]} x {r}")
    fixed = sorted(t for t in a if a[t] in BAD and b.get(t) not in BAD and t in b)
    print(f"failures+errors: base {sum(v in BAD for v in a.values())}, head {sum(v in BAD for v in b.values())}, "
          f"fixed on head {len(fixed)}")
    sys.exit(1 if new_fail or new_skip or new_reasons else 0)


if __name__ == "__main__":
    main()
