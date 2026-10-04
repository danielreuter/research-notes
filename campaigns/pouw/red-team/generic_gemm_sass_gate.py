# Writer: bc-c7421547 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor. The assessor (bc-d7d4b0d1) reviewed and adopted its GEMM jobs (run r20260930-085618-5cfa), 30 Sep 2026.
"""SASS gate for generic_gemm_sm120.cu: no gemm_kernel may issue a tensor-core instruction, and each must issue its variant's
core op. Reads `cuobjdump -sass` on stdin; writes the verdict as JSON to argv[1]; exits 1 on any failure."""
import json, re, sys

TENSOR = re.compile(r"\b(HMMA|IMMA|QMMA|OMMA|HGMMA|IGMMA|QGMMA|UTC\w*|WGMMA\w*)\b")
CORE = {0: "FFMA", 1: "FFMA", 2: "HFMA2", 3: "HFMA2.BF16_V2", 4: "IDP.4A", 5: "IDP.4A"}  # variant enum -> core op
NAMES = ["ffma_f32", "ffma_bf16", "hfma2_f16", "hfma2_bf16", "dp4a_s8", "dp4a_nvfp4"]

funcs, cur = {}, None
for line in sys.stdin:
    m = re.search(r"Function : (\S+)", line)
    if m:
        cur = m.group(1)
        funcs[cur] = []
    elif cur:
        funcs[cur].append(line)

out, ok = [], True
for name, body in funcs.items():
    m = re.match(r"_Z\d+gemm_kernelILi(\d)ELi(\d+)ELi(\d+)ELi(\d+)E", name)
    if not m:
        continue
    v, bm, bnw, bks = map(int, m.groups())
    text = "".join(body)
    tensor = sorted(set(TENSOR.findall(text)))
    core = CORE[v]
    n_core = len(re.findall(r"\b" + re.escape(core) + r"(?:\.\w+)*\b", text))
    n_ffma = len(re.findall(r"\bFFMA\b", text))
    good = not tensor and n_core > 0
    ok &= good
    out.append({"variant": NAMES[v], "cfg": f"bm{bm}_bnw{bnw}_bks{bks}", "tensor_ops": tensor, "core_op": core,
                "core_count": n_core, "ffma_count": n_ffma, "pass": good})

expected = int(sys.argv[2]) if len(sys.argv) > 2 else len(out)
verdict = {"kernels": len(out), "expected": expected, "pass": ok and len(out) == expected, "rows": out}
json.dump(verdict, open(sys.argv[1], "w"), indent=1)
print(f"sass gate: {len(out)} kernels, pass={verdict['pass']}")
sys.exit(0 if verdict["pass"] else 1)
