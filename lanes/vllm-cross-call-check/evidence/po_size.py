"""po_size.py: the size of a verity/partition/v1 object (PR #111, amended) per request Program, from the Program's Calls (spec -> Calls)
and, per distinct Definition specialization, its computing gates n (cross_call.analyze), units U and unit classes K (word.unit_rule).
Bytes of canonical JSON: a cut = its key and {"classes": U SHA-512s, "owner": n values < U} (index digits as if uniform over the range);
a Call entry = {"call": k, "cut": key}.  `indexed`: the same with K distinct class digests per cut and a class index per owner value."""
import math

from verity_vllm.query import cross_call as X
from verity_vllm.query import word as W
from verity_vllm.query.program_view import spec_base, spec_statics

_MEMO: dict = {}
_SPEC: dict = {}


def digits_sum(m: int) -> int:
    """Sum of decimal digit counts of 0..m-1."""
    t, d, lo = 0, 1, 0
    while lo < m:
        hi = min(m, 10 ** d)
        t += (hi - lo) * d
        lo, d = hi, d + 1
    return t


def spec_counts(spec: str) -> tuple[int, int, int]:
    got = _SPEC.get(spec)
    if got is None:
        fn = W.specialization(spec_base(spec), spec_statics(spec))
        n = X.analyze(fn, _MEMO).total
        r = W.unit_rule(fn, memo=_MEMO)
        U = r["units_per_call"]
        got = _SPEC[spec] = (n, U, len(r["classes"]))
    return got


def cut_bytes(n: int, U: int, K: int, indexed: bool = False) -> int:
    owner = (digits_sum(U) * n // max(U, 1) + max(n - 1, 0)) if n else 0
    if indexed:
        classes = K * 131 + (digits_sum(K) * U // max(K, 1) + max(U - 1, 0)) + len(',"class_of":[]')
    else:
        classes = U * 131 - (1 if U else 0)
    return 131 + len('{"classes":[],"owner":[]}') + classes + owner + 1          # "<key>": value,


def interpolate_varying(specs: list[str]) -> None:
    """Fill _SPEC for a family whose specs differ only in T (attention's history length): n exactly (cheap), U and K at the key-block
    boundaries (`program_graph._word_values`, as the program graphs do: units exact) and interpolated between."""
    from verity_vllm.pipeline.program_graph import _interp, _word_values
    groups: dict = {}
    for s in specs:
        st = spec_statics(s)
        if "T" in st and s not in _SPEC:
            groups.setdefault((spec_base(s), tuple(sorted((k, str(v)) for k, v in st.items() if k != "T"))), {})[int(st["T"])] = s
    for (_fam, _rest), by_t in groups.items():
        vals = sorted(by_t)
        if len(vals) < 48:
            continue
        bn = spec_statics(by_t[vals[0]]).get("BN")
        pts = _word_values(vals, int(bn) if isinstance(bn, int) else None)
        for t in pts:
            spec_counts(by_t[t])
        us = [float(_SPEC[by_t[t]][1]) for t in pts]
        ks = [float(_SPEC[by_t[t]][2]) for t in pts]
        for t in vals:
            if by_t[t] not in _SPEC:
                fn = W.specialization(spec_base(by_t[t]), spec_statics(by_t[t]))
                _SPEC[by_t[t]] = (X.analyze(fn, _MEMO).total, int(round(_interp(pts, us, t))), int(round(_interp(pts, ks, t))))


def program_bytes(spec_calls: dict[str, int], n_calls: int) -> dict:
    interpolate_varying(list(spec_calls))
    cuts = sum(cut_bytes(*spec_counts(s)) for s in spec_calls)
    cuts_indexed = sum(cut_bytes(*spec_counts(s), indexed=True) for s in spec_calls)
    calls = n_calls * 147 + digits_sum(n_calls) + 2
    head = len('{"calls":[],"cuts":{},"format":"verity/partition/v1","program":""}') + 128
    return {"calls": n_calls, "distinct_cuts": len(spec_calls), "cuts_bytes": cuts, "calls_bytes": calls, "total_bytes": head + cuts + calls,
            "indexed_total_bytes": head + cuts_indexed + calls, "gates": sum(spec_counts(s)[0] for s in spec_calls),
            "units": sum(spec_counts(s)[1] for s in spec_calls)}
