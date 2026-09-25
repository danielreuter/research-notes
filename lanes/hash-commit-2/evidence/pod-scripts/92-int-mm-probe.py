# hash-commit-2: which row counts M does torch._int_mm (cuBLASLt int8) accept on this GPU, at the Poseidon2-16 int8 MDS
# shape (K = N = 8 * 16 = 128)?  test_poseidon2_tree_matches_reference[...torch...] fails on sm_90 at M = 17.
import torch

print(torch.__version__, torch.cuda.get_device_name(), torch.cuda.get_device_capability())
b = torch.randint(-128, 127, (128, 128), dtype=torch.int8, device="cuda")
ok, bad = [], []
for m in list(range(17, 41)) + [48, 63, 64, 65, 100, 128, 200, 1000, 1024, 4096 + 3]:
    a = torch.randint(-128, 127, (m, 128), dtype=torch.int8, device="cuda")
    try:
        y = torch._int_mm(a, b)
        torch.cuda.synchronize()
        assert torch.equal(y.cpu(), a.cpu().int() @ b.cpu().int())
        ok.append(m)
    except Exception as e:  # noqa: BLE001
        bad.append((m, type(e).__name__))
print("ok", ok)
print("bad", bad)
