"""agkr-nvf4: per-kernel device time of one generic LogUp round at the big levels (T4 (4, 2^m, 6) int32).
python 11_lkern.py   (PYTHONPATH = <tree>/backends/gkr:<tree>)"""
import torch

from packed import kernels_graph as kg
from packed import sumcheck_packed as sp
from packed import reference as ref

dev = torch.device("cuda")
k = sp.Kernel("cuda", k1_log2=sp.K1_LOG2_DEFAULT, mode="triton")
tk = k._tk
P = ref.P


def bench(fn, it=20):
    fn()
    torch.cuda.synchronize()
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    a.record()
    for _ in range(it):
        fn()
    b.record()
    torch.cuda.synchronize()
    return a.elapsed_time(b) / it


for lg in (23, 22, 20, 17):
    m = 1 << lg
    T4 = torch.randint(0, P, (4, 2 * m, 6), dtype=torch.int32, device=dev)
    K1, K2 = k.split(m)
    split = sp.Kernel.split_b1(K1, K2)
    rho = torch.randint(0, P, (40, 6), dtype=torch.int32, device=dev)
    kappa = K1.bit_length() - 1
    e_lo = kg.eq_table_vars(rho, 1, kappa)
    e_lo32 = tk.eq_limbs32(e_lo)
    e_hi = kg.eq_table_vars(rho, 1 + kappa, lg - kappa).contiguous()
    r_R = torch.randint(0, P, (6,), dtype=torch.int32, device=dev)
    out = torch.empty((4, m, 6), dtype=torch.int32, device=dev)
    Zs = tk.logup_ext_inner_product(T4, e_lo32, K1, K2, split)
    Z = Zs.to(torch.int64).sum(0) if split > 1 else Zs[0]
    t_ip = bench(lambda: tk.logup_ext_inner_product(T4, e_lo32, K1, K2, split))
    t_sum = bench(lambda: Zs.to(torch.int64).sum(0)) if split > 1 else 0.0
    t_rc = bench(lambda: tk.reduce_contract(Z, e_hi, k.pw16, K2, 6, 6))
    t_fold = bench(lambda: tk.fold_ext4(T4, m, r_R, out))
    t_eq = bench(lambda: (kg.eq_table_vars(rho, 1, kappa), kg.eq_table_vars(rho, 1 + kappa, lg - kappa)))
    gb = T4.numel() * 4 / 1e9
    print(f"m=2^{lg} K1={K1} K2={K2} split={split} T4 {gb:.2f} GB: ip {t_ip:.3f} ms ({gb / t_ip:.2f} TB/s)  zsum {t_sum:.3f}  "
          f"rc {t_rc:.3f}  fold {t_fold:.3f} ms ({1.5 * gb / t_fold:.2f} TB/s)  eq {t_eq:.3f}", flush=True)
