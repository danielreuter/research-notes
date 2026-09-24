#!/bin/bash
# vy-live-verifier: the live B-Ligero verifier service (lane live-verifier).  Restart loop; logs + session dumps under /workspace/live.
mkdir -p /workspace/live/sessions
cat > /workspace/live/start.sh <<'INNER'
#!/bin/bash
export PYTHONPATH="/workspace/lv-src/packages/verity/src:/workspace/lv-src/backends/numerical/python:/workspace/lv-src/tools/research/src:/workspace/lv-src"
export RESEARCH_GIT_COMMIT=${RESEARCH_GIT_COMMIT:-11c7075d21ba8cfc9dfa95659cec2efd8a57785d}
cd /workspace/lv-src
while true; do
  /workspace/venv312/bin/python -m backends.direct.ligero.live serve --listen 0.0.0.0:7000 --out /workspace/live/sessions \
      --ligero-verify /workspace/bin/ligero-verify --jobs ${LIVE_JOBS:-8} --threads ${LIVE_THREADS:-1} --target-bits 128 >> /workspace/live/serve.out 2>&1
  echo "[$(date -u +%FT%TZ)] server exited rc=$?; restarting in 2s" >> /workspace/live/serve.out
  sleep 2
done
INNER
chmod +x /workspace/live/start.sh
pkill -f "live serve --listen 0.0.0.0:7000" 2>/dev/null; pkill -f "/workspace/live/start.sh" 2>/dev/null; sleep 1
RESEARCH_GIT_COMMIT=11c7075d21ba8cfc9dfa95659cec2efd8a57785d nohup setsid bash /workspace/live/start.sh > /dev/null 2>&1 &
sleep 3
tail -3 /workspace/live/serve.out
ss -ltnp | grep 7000
