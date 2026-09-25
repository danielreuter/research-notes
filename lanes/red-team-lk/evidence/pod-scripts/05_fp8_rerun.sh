#!/usr/bin/env bash
# red-team-lk: the fp8 forge on the RTX 5090 (Triton 3.4). Our 3be6a35f copy gets the Triton 3.4 constexpr-global syntax fix
# of 679697a4 (packed/kernels_triton.py: `X: tl.constexpr = v` -> `X = tl.constexpr(v)`, 5 lines; the files are otherwise
# identical to b7cec878's), then 02_redteam.sh (static-merge + forge).  The honest control must still be accepted.
set -uo pipefail
cd /workspace
diff tree-3be6a35f/backends/gkr/packed/kernels_triton.py tree-b7cec878/backends/gkr/packed/kernels_triton.py | grep -c '^[<>]'
cp tree-b7cec878/backends/gkr/packed/kernels_triton.py tree-3be6a35f/backends/gkr/packed/kernels_triton.py
rm -rf /workspace/red-team-lk/out/3be6a35f
bash /workspace/red-team-lk/scripts/02_redteam.sh 3be6a35f fp8-ada
