# verifier pod vy-ligerito-2pass-verifier (RTX 2000 Ada, EU-RO-1, same DC as the prover); tree /workspace/lv-src-e0c7acd2
# (backends/direct/ligero identical to main 24f252b1)
setsid nohup bash /workspace/lv-src-e0c7acd2/backends/direct/ligero/live_serve.sh > /workspace/live_serve_setup.log 2>&1 < /dev/null & disown
