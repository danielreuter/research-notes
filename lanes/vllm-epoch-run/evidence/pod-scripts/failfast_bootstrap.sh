#!/bin/bash
# failfast_bootstrap.sh CASES OUT: pod_bootstrap.sh --cases CASES --out OUT --gpu, under the fail-fast (coordinator 09:13Z): nvidia-smi,
# torch's CUDA init and `import vllm` must all pass within 15 min of the pod's start (POD_START, epoch seconds, from the launcher), else
# the bootstrap's process group is stopped and this exits 40 ("STOP failfast FAIL" in progress.txt; watch_pods.sh then terminates the pod).
# Exit: the bootstrap's rc once the imports passed; 40 on the fail-fast.  Run from integrations/vllm with $EV set.
set -u
CASES=${1:?cases}; OUT=${2:?out}
P=$EV/progress.txt; PY=/workspace/venv312/bin/python
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$P"; }
START=${POD_START:-$(date +%s)}; END=$(( START + 900 )); ff=0
set -m   # the bootstrap as its own process group (pgid = its pid), so the fail-fast stops all of it
bash verity_vllm/ops/pod_bootstrap.sh --cases "$CASES" --out "$OUT" --gpu > "$EV/bootstrap.log" 2>&1 &
B=$!; set +m
while kill -0 "$B" 2>/dev/null || [ "$ff" = 0 ]; do
  if [ "$ff" = 0 ] && nvidia-smi > /dev/null 2>&1 && [ -x "$PY" ] \
     && timeout 180 "$PY" -c "import torch; torch.cuda.init(); assert torch.cuda.is_available(); import vllm" > /dev/null 2>&1; then
    ff=1; say "failfast OK: nvidia-smi, torch CUDA init, vllm import $(( $(date +%s) - START )) s after the pod start"
  fi
  if [ "$ff" = 0 ] && [ "$(date +%s)" -ge "$END" ]; then
    kill -TERM -- "-$B" 2>/dev/null; sleep 5; kill -KILL -- "-$B" 2>/dev/null
    tail -n 30 "$EV/bootstrap.log" > "$EV/bootstrap.tail"
    say "STOP failfast FAIL: nvidia-smi / torch CUDA init / vllm import not passing 15 min after the pod start; terminate this pod"
    exit 40
  fi
  kill -0 "$B" 2>/dev/null || [ "$ff" = 1 ] || { sleep 1; kill -0 "$B" 2>/dev/null || break; }
  sleep 20
done
wait "$B"; rc=$?
if [ "$ff" != 1 ]; then
  tail -n 30 "$EV/bootstrap.log" > "$EV/bootstrap.tail"
  say "STOP failfast FAIL: the bootstrap ended rc=$rc before torch CUDA init and the vllm import passed; terminate this pod"
  exit 40
fi
exit "$rc"
