#!/usr/bin/env bash
# route-a-live: re-register the 4,096-VU route (a) cell (no pod): cell.py rederive from art:4b52879f's envelope with the
# protocol / sweep blocks, commit.seconds (CPU committer) and live.loopback_round_seconds from the same run's loopback
# warm-up session (the run dump's out/cell-4096/s0/times.json), published as a typed output naming the prover run's dump.
set -euo pipefail
I=/tmp/ral/rr; cd /workspace/backends/gkr
/tmp/venv/bin/python tools/cell.py rederive --from $I/result-4096-v2.json --result $RESEARCH_RUN_DIR/cell-result-4096.json \
  --supersedes art:3d7cbea23e9bdd7b14698d1871d7b4f6c24974a70cbd34ba04edfb5bbad58f60 --protocol $I/protocol-4096.json --sweep $I/sweep-4096.json \
  --loopback-times $I/loopback-times-4096-s0.json --loopback-where "run r20260925-201056-1018 session 0 (the warm-up; its times.json in art:d9666f5a out/cell-4096/s0/)" \
  --commit "CPU reference committer (backends/gkr/gpu/commit.py: frame-v3 + blake3-keyed/row/v2 over the 4,096 VUs' operands, one pass before the timed sessions; not a GPU committer)"
cat > $RESEARCH_RUN_DIR/outputs.json <<JSON
{"schema": "research/outputs/v0.1", "outputs": [{"name": "cell_result", "kind": "bench-result/v1", "file": "cell-result-4096.json",
  "meta": {"lane": "route-a-live", "vus": 4096, "prover_run": "r20260925-201056-1018", "verifier_run": "r20260925-195835-65ab",
           "note": "route (a) cell, live prime coins; re-derived from the same runs with protocol, sweep (plateau by memory cap), commit.seconds (CPU committer) and live.loopback_round_seconds (same-run loopback)"},
  "refs": {"run_files": "art:d9666f5a230ca55ea1ed2a181a6357f0c3b79e8fbca7f6291aecb0456e98d998",
           "verifier_files": "art:42841b22664e62484ea6aea459d6faac4a037d20fd273cb42604e49de2b8732a",
           "supersedes": "art:3d7cbea23e9bdd7b14698d1871d7b4f6c24974a70cbd34ba04edfb5bbad58f60",
           "gates": "art:837d95c8efed4cabd8dfb0e06deb6d963b280c8ef3a0515d6d6866da380683c8",
           "sweep_probe": "art:54b53a85e600c43479c30b943160c43b7a59d6ec32b04d6d6d242e745bf882fa",
           "sweep_1024": "art:aa9223c29bae5741e8fc8867f78803e7a4af70692882abbf4c42a3a9586c3f8b"}}]}
JSON
