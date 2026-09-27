#!/usr/bin/env python3
"""red-team-flock-3: independent checks of PR #121 (`TwoStageLaw.profile` over replay units at rate p*k/n_v).

  pr121_checks.py WORKTREE draws          digests of vLLM's LEGACY-module draws and the law's samplers (run at main and PR)
  pr121_checks.py WORKTREE law OLDTREE    the adaptive attack through the real samplers, an exact grid of the certified
                                          bound against the best adaptive attack (new and old profile), edge cases
"""
import hashlib
import json
import math
import sys
from fractions import Fraction

W, MODE = sys.argv[1], sys.argv[2]
sys.path[:0] = [f"{W}/packages/verity/src", f"{W}/protocols/sampled_proofs", f"{W}/integrations/vllm"]

from verity_sampled_proofs import law as L  # noqa: E402


def H(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def rnd(seed: int, n: int = 32) -> bytes:
    return hashlib.sha256(b"rtf3-pr121|" + seed.to_bytes(8, "big")).digest()[:n]


def draws():
    from verity_vllm.commit import challenge as C
    out = {}
    picks, legacy, sampler, probs, pos = [], [], [], [], []
    for s in range(300):
        r = rnd(s)
        pools = [list(range(1 + (r[i] % 40))) for i in range(1 + r[0] % 12)]
        per = 1 + r[1] % 6
        key = C.replay_key(rnd(s + 10_000), rnd(s + 20_000))
        picks.append(C.stratum_picks(pools, per, None, key))
        legacy.append(C.stratum_picks(pools, per, int.from_bytes(r[:8], "big"), None))
        law = L.TwoStageLaw({"a": L.Stage(Fraction(1 + r[2] % 7, 8), 1 + r[3] % 5), "b": L.Stage(Fraction(1), None),
                             "c": L.Stage(Fraction(r[4] % 11, 10), 2)})
        units = [L.ReplayUnit(i, "abc"[r[5 + i % 20] % 3], 1 + r[(6 + i) % 32] % 9) for i in range(40)]
        sel = L.select_replay_units(L.ru_key(rnd(s + 30_000), {"root": r}), law, units)
        vus = L.select_verification_units(L.vu_key(rnd(s + 40_000), {"interiors": r}), law, sel)
        sampler.append([[u.index for u in sel], sorted(vus.items()), law.to_json()])
        probs.append([str(L.check_probability(law, c, n)) for c in "abc" for n in range(0, 10)])
        pos.append([C.challenge_positions(r, [3, 5, 8], 7, legacy=True),
                    C.challenge_positions(r, [3, 5, 8], 7, legacy=False, source=rnd(s + 50_000)),
                    [C.identity_picker(r, "ab" * 16, legacy=True)(i, 97) for i in range(5)]])
    out = {"stratum_picks(key)": H(picks), "stratum_picks(legacy seed)": H(legacy), "select_replay/verification_units": H(sampler),
           "check_probability": H(probs), "challenge_positions/identity_picker": H(pos),
           "domains": [L.RU_DOMAIN, L.VU_DOMAIN]}
    for k, v in out.items():
        print(f"DRAWS\t{k}\t{v}")


def best_attack(q: Fraction, delta: float, n_r: int) -> int:
    """The most wrong RUs an adaptive prover can leave while passing with probability >= delta: max b with
    (1 - q)^b >= delta (exact), each wrong RU escaping with probability 1 - q independently."""
    if q == 1:
        return 0
    if q == 0:
        return n_r
    d = Fraction(delta)
    b = int(math.log(delta) / math.log(1 - float(q)))
    while b + 1 <= n_r and (1 - q) ** (b + 1) >= d:
        b += 1
    while b > 0 and (1 - q) ** b < d:
        b -= 1
    return min(b, n_r)


def law_checks(old_tree: str):
    import importlib
    import random
    # 1. the adaptive attack at TOY, through the real samplers: 16 skipped RUs; each drawn one is replayed honestly but for
    #    one wrong VU at a position the prover picks after the RU draw (it cannot see the VU draw: a later beacon round)
    law = L.TwoStageLaw({"u": L.Stage(Fraction(1, 2), 2)})
    skipped = [L.ReplayUnit(i, "u", 4) for i in range(16)]
    trials, accepted, single = 40_000, 0, [0, 0]
    rng = random.Random(20260927)
    for t in range(trials):
        sel = L.select_replay_units(L.ru_key(rnd(t, 32), {"root": b"toy"}), law, skipped)
        wrong = {u.index: rng.randrange(4) for u in sel}          # the prover's choice, after the RU draw
        chk = L.select_verification_units(L.vu_key(rnd(t + 10**7), {"interiors": H(sorted(wrong.items())).encode()}), law, sel)
        caught = any(wrong[i] in chk[i] for i in wrong)
        accepted += not caught
        single[0] += 1
        single[1] += (0 not in wrong) or (wrong[0] not in chk[0])
    p16 = accepted / trials
    print("ATTACK\t" + json.dumps({"trials": trials, "accept_16_skipped": p16, "expected_0.75^16": 0.75 ** 16,
                                   "sigma": (0.75 ** 16 * (1 - 0.75 ** 16) / trials) ** 0.5,
                                   "single_ru_escape": single[1] / single[0], "expected_single": 0.75}))
    new = law.profile("u", n_r=512, n_v=4, delta=0.01)
    old = None
    if old_tree:
        sys.path.insert(0, f"{old_tree}/protocols/sampled_proofs")
        sys.path.insert(0, f"{old_tree}/packages/verity/src")
        for m in [k for k in sys.modules if k.startswith(("verity_sampled_proofs", "verity.proofs"))]:
            del sys.modules[m]
        OL = importlib.import_module("verity_sampled_proofs.law")
        old = OL.TwoStageLaw({"u": OL.Stage(Fraction(1, 2), 2)}).profile("u", n_r=512, n_v=4, delta=0.01)
    print("TOY\t" + json.dumps({"new_wrong_RUs": new.worst_case(lambda m: 1), "new_work_VUs": new.worst_case(lambda m: 4 * m),
                                "old_incorrect_VUs": old.worst_case(lambda m: m) if old else None,
                                "attack_RUs": best_attack(Fraction(1, 4), 0.01, 512), "attack_work_VUs": 4 * best_attack(Fraction(1, 4), 0.01, 512)}))
    # 2. the exact grid: the certified bound must dominate the best adaptive attack (conservative) and be within 1 RU of it
    #    (tight); the old profile's incorrect-VU reading against the attack's skipped work, for the record
    newL = L
    bad, loose, n_pts, old_under = [], [], 0, 0
    for p in (Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1)):
        for k in (1, 2, 3, 8, None):
            for n_v in (1, 2, 4, 6, 16, 64):
                for delta in (1e-2, 1e-3, 2.0 ** -20, 1e-6, 2.0 ** -10):
                    n_r = 10**6
                    st = newL.Stage(p, k)
                    q = p * Fraction(st.checked(n_v), n_v)
                    b = best_attack(q, delta, n_r)
                    prof = newL.TwoStageLaw({"x": st}).profile("x", n_r=n_r, n_v=n_v, delta=delta)
                    cert = prof.worst_case(lambda m: 1)
                    work = prof.worst_case(lambda m: n_v * m)
                    n_pts += 1
                    if cert + 1e-9 < b or work + 1e-6 < n_v * b:
                        bad.append((str(p), k, n_v, delta, b, cert))
                    if cert >= b + 1:
                        loose.append((str(p), k, n_v, delta, b, cert))
                    if old is not None:
                        o = OL.TwoStageLaw({"x": OL.Stage(p, k)}).profile("x", n_r=n_r, n_v=n_v, delta=delta).worst_case(lambda m: m)
                        old_under += o + 1e-9 < n_v * b
    print("GRID\t" + json.dumps({"points": n_pts, "new_below_attack": bad[:5], "n_new_below_attack": len(bad),
                                 "new_looser_than_1RU": loose[:5], "n_new_loose": len(loose), "old_below_attack_work": old_under}))
    # 3. boundary: (1 - q)^b == delta exactly; the escape of b RUs is delta itself, inside the delta budget
    for q, delta in ((Fraction(1, 2), 2.0 ** -10), (Fraction(1, 4), 0.75 ** 16), (Fraction(1, 2), 2.0 ** -40)):
        prof = newL.TwoStageLaw({"x": newL.Stage(q, None)}).profile("x", n_r=10**6, n_v=1, delta=delta)
        print("BOUNDARY\t" + json.dumps({"q": str(q), "delta": delta, "attack": best_attack(q, delta, 10**6), "certified": prof.worst_case(lambda m: 1)}))
    # 4. mixed RU sizes in one class: the profile takes one n_v; larger RUs are caught less often
    st = newL.Stage(Fraction(1, 2), 2)
    small = newL.TwoStageLaw({"x": st}).profile("x", n_r=10**4, n_v=4, delta=0.01)
    big = newL.TwoStageLaw({"x": st}).profile("x", n_r=10**4, n_v=8, delta=0.01)
    print("MIXED\t" + json.dumps({"profile_n_v4_RUs": small.worst_case(lambda m: 1), "profile_n_v8_RUs": big.worst_case(lambda m: 1),
                                  "attack_on_8VU_RUs": best_attack(Fraction(1, 8), 0.01, 10**4), "attack_on_4VU_RUs": best_attack(Fraction(1, 4), 0.01, 10**4)}))
    # 5. float p: the profile's rate is the sampler's exact probability
    st = newL.Stage(0.1, 3)
    prof = newL.TwoStageLaw({"x": st}).profile("x", n_r=10, n_v=7, delta=0.01)
    print("FLOATP\t" + json.dumps({"rate": str(prof.draws["replay"].p), "sampler_p_times_k_over_n": str(Fraction(0.1) * Fraction(3, 7)),
                                   "equal": prof.draws["replay"].p == Fraction(0.1) * Fraction(3, 7),
                                   "check_probability": str(newL.check_probability(newL.TwoStageLaw({"x": st}), "x", 7))}))
    # 6. edge cases
    E = {}
    for name, st, n_v in (("k=0", newL.Stage(Fraction(1, 2), 0), 4), ("p=0", newL.Stage(Fraction(0), 2), 4),
                          ("p=1,k>=n_v", newL.Stage(Fraction(1), 9), 4), ("p=1,k=None", newL.Stage(Fraction(1), None), 4)):
        prof = newL.TwoStageLaw({"x": st}).profile("x", n_r=100, n_v=n_v, delta=0.01)
        E[name] = [str(prof.draws["replay"].p), prof.worst_case(lambda m: 1)]
    E["n_r=0"] = newL.TwoStageLaw({"x": newL.Stage(Fraction(1, 2), 2)}).profile("x", n_r=0, n_v=4, delta=0.01).worst_case(lambda m: 1)
    print("EDGES\t" + json.dumps(E))


if __name__ == "__main__":
    if MODE == "draws":
        draws()
    else:
        law_checks(sys.argv[3] if len(sys.argv) > 3 else "")
