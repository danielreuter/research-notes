"""static SASS instruction counts for the v3 encoder and commit_gpu leaves/tree kernels (sm_90)"""
import collections, os, re, subprocess, sys, tempfile
from backends.direct.ligero import encode_simt, commit_gpu
def sass(src, arch="sm_90"):
    with tempfile.TemporaryDirectory() as d:
        cu = os.path.join(d, "k.cu"); cubin = os.path.join(d, "k.cubin"); open(cu, "w").write(src)
        r = subprocess.run(["nvcc", "-cubin", f"-arch={arch}", "-std=c++17", "-O3", "-Xptxas", "-v", "-o", cubin, cu], capture_output=True, text=True)
        for line in r.stderr.splitlines():
            if "registers" in line or "spill" in line: print("   ptxas:", line.strip())
        if r.returncode: print(r.stderr[-1500:]); return
        return subprocess.run(["cuobjdump", "-sass", cubin], capture_output=True, text=True).stdout
def report(text):
    for f in re.split(r"\n\s*Function : ", text)[1:]:
        fname = f.split("\n", 1)[0].strip()
        ops = re.findall(r"/\*[0-9a-f]{4}\*/\s+(?:@!?U?P\d\s+)?([A-Z0-9_.]+)", f)
        h = collections.Counter(o.split(".")[0] for o in ops); full = collections.Counter(ops)
        print(f"   {fname[:40]}: {len(ops)} static;", ", ".join(f"{k}={v}" for k, v in h.most_common(16)))
        print("      full:", ", ".join(f"{k}={v}" for k, v in full.most_common(12)))
        # branch targets / loop structure: count BRA and BAR
        print("      BRA", h.get("BRA", 0), "BAR", h.get("BAR", 0), "LDS", sum(v for k, v in full.items() if k.startswith("LDS")), "STS", sum(v for k, v in full.items() if k.startswith("STS")),
              "LDG", sum(v for k, v in full.items() if k.startswith("LDG")), "STG", sum(v for k, v in full.items() if k.startswith("STG") or k.startswith("ST.")))
l = 16384
params = {"pinv": encode_simt._P_INV_MOD_R, "k": l, "logk": 14, "threads": 1024, "logt": 10, "tp": 256, "kinv_mont": 1}
print("=== encoder v3 l=16384 tp=256"); report(sass(encode_simt._SRC % params))
print("=== commit_gpu"); report(sass(commit_gpu._SRC))
