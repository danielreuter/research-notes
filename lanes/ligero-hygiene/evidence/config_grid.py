from backends.direct.ligero import protocol as pm
from verity_numerical.security import accounting as acc

miss = []
n = 0
for mode in pm.MODES:
    for zk in (False, True):
        for target in (-80.0, -100.0, -128.0):
            for n_proofs in (1, 2, 25, 26, 50):
                for lg in range(6, 16):
                    l = 1 << lg
                    try:
                        c = pm.config_for(l, target, 2, n_proofs, zk=zk, mode=mode)
                    except acc.AccountingError:
                        continue
                    s = pm.soundness(c, 1, 1, 1)
                    want = acc.per_proof_target(target, n_proofs) if n_proofs > 1 else target
                    n += 1
                    if s["per_proof_total_log2"] > want:
                        miss.append((mode, zk, target, n_proofs, l, c.t, round(s["per_proof_total_log2"], 3), round(want, 3)))
print(n, "configs,", len(miss), "miss")
for m in miss:
    print(m)
