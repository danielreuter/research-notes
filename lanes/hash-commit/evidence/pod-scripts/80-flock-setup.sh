#!/usr/bin/env bash
# commit-gpu: CUDA 13.3.1 redist (nvcc, cudart, cccl, crt) under /workspace/cuda-13.3 and succinctlabs/flock at /workspace/flock
set -euo pipefail
V=13.3.1; C=/workspace/cuda-13.3; R=https://developer.download.nvidia.com/compute/cuda/redist
mkdir -p $C /workspace/dl && cd /workspace/dl
curl -sfo redist.json $R/redistrib_$V.json
python3 - "$V" <<'EOF' > urls.txt
import json, sys
d = json.load(open("redist.json"))
for k in ("cuda_nvcc", "cuda_cudart", "cuda_cccl", "cuda_crt", "libnvvm", "cuda_nvrtc"):
    if k in d and "linux-x86_64" in d[k]:
        print(k, d[k]["version"], d[k]["linux-x86_64"]["relative_path"])
EOF
cat urls.txt
while read k ver path; do
  f=$(basename $path); [ -f $f ] || curl -sfO $R/$path
  tar -xf $f -C $C --strip-components=1
done < urls.txt
$C/bin/nvcc --version | tail -2
[ -d /workspace/flock ] || git clone -q https://github.com/succinctlabs/flock /workspace/flock
cd /workspace/flock && git log -1 --format='%H %cd' | cat && ls cuda-ghash | head -40
