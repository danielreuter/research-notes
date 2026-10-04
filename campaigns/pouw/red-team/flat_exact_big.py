"""`scale-flatness/nvfp4`: modal block-scale share on the exact forming (`pearl_c4.form`), large sample. Rows: every-8th
positions pinned to ±1 (so ρ = 1 exactly), N(0, 1) elsewhere, then `spikes` per 16-block at S (offsets never ≡ 0 mod 8),
plus one entry of `rowmax` in the row's last block (screened and debited), which sets α and so the bucket."""
import argparse, json, struct
import numpy as np
from verity_pouw.schemes import pearl_c4 as C4

OFFS = {4: (1, 5, 9, 13), 14: tuple(o for o in range(16) if o not in (0, 8))}
ap = argparse.ArgumentParser()
ap.add_argument("--rows", type=int, default=16); ap.add_argument("--k", type=int, default=8192)
ap.add_argument("--S", type=float, default=8.9); ap.add_argument("--rowmax", type=float, default=930.0)
ap.add_argument("--spikes", type=int, default=14)
a = ap.parse_args()
rng = np.random.default_rng(7)
x = rng.standard_normal((a.rows, a.k))
x[:, ::8] = rng.choice((-1.0, 1.0), (a.rows, a.k // 8))
for o in OFFS[a.spikes]:
    x[:, o::16] = a.S * rng.choice((-1.0, 1.0), (a.rows, 1))
x[:, a.k - 15] = a.rowmax
W = [[struct.unpack("<I", struct.pack("<f", float(v)))[0] for v in r] for r in x]
seed_a, seed_b = b"flat-exact-big-A" * 2, b"flat-exact-big-B" * 2
e = [C4.line(seed_a, C4.ROLE_EA, i) for i in range(a.rows)]
f = C4.basis(seed_b, C4.ROLE_FA, a.k)
fm = C4.form(C4.NVFP4, W, e, f)
sc = np.array(fm.scales)[:, :-1]                      # drop the screened row-max block
modal = [np.bincount(r).argmax() for r in sc]
share = float(np.mean([np.mean(r == m) for r, m in zip(sc, modal)]))
glob = np.bincount(sc.ravel()).argmax()
print(json.dumps({"rows": a.rows, "k": a.k, "S": a.S, "rowmax": a.rowmax, "spikes": a.spikes,
                  "admitted": sum(C4.row_passes(C4.NVFP4, w) for w in W), "blocks": int(sc.size),
                  "modal_share_per_row": share, "modal_share_global": float((sc == glob).mean()),
                  "f512_flat_tile": share ** 512}))
