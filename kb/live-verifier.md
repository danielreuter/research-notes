# Live verifier (kept RO instance) and its session store

## GOTCHA: CA-MTL-1 (GPU.ONE) does not hairpin public IPs between pods
Two pods in RunPod CA-MTL-1 (H100 prover 69.30.85.160, A40 verifier 69.30.85.40, both AS20016 GPU.ONE) could not reach
each other on ANY mapped public port (ssh or :7000 mapping), both directions: `Connection refused`; the laptop reached both.
Container IPs (172.x) are separate networks. So a same-DC live verifier on a second pod does not work there; test with
`timeout 4 bash -c '</dev/tcp/IP/PORT'` from the prover BEFORE launching live runs. (wave-h100-2, 2026-09-24 04:08Z; EU-RO-1
pods did reach each other per live-2c.)

## H100 SXM (80GB HBM3) has no same-DC verifier on RunPod right now (fill-dc, 2026-09-24 06:25-06:40Z)
- EU-NL-1: H100 prover and a cpu3g CPU pod both sit behind ONE public IP (91.199.227.82); prover -> verifier's mapped ports
  (ssh and :7000) `Connection refused`, and the 172.x container nets do not route to each other. Same as CA-MTL-1.
- EU-FR-1 and AP-IN-1 list only H100 (no CPU pod of cpu3c/cpu3g/cpu3m/cpu5c, no cheap GPU); US-NE-1 is not a REST
  `dataCenterIds` value. EUR-IS-1 (A100 + cpu3c CPU pod, both behind 157.157.221.29) DOES hairpin.
- REST `globalNetworking: true` (not in `research pods create`; set it in the POST body) gives GPU pods a `podnet1` interface
  (10.0.0.0/10, `<podid>.runpod.internal` resolves), but H100 <-> A40 in CA-MTL-1 timed out both ways on every port, and
  podnet1 has a `tbf rate 100Mbit` qdisc: useless for 76-135 MB proofs per batch even if it connected.
- Fallback used: the verifier on the prover pod (`live_serve.sh` under `nice -n 19`, `--verifier tcp://127.0.0.1:7000`).

## Picking a same-DC verifier pod in EU-RO-1 (fill-consumer, 2026-09-24 06:20-07:05Z)
- Probe both RTT AND throughput from the prover: `python -m backends.direct.ligero.live probe --verifier tcp://IP:PORT --mb 2
  --repeat 6`. Good: cpu3c 16 vCPU on an idle EPYC 9655 host, 0.6 ms and 5-7 Gbps. Bad: cpu3c pods on hosts at load
  320-400 (0.2 ms TCP but a 2.6-2.7 ms probe), and an **NVIDIA L4 pod ($0.49/h), capped at ~0.9 Gbps** (1.0-1.4 ms). At
  0.9 Gbps an 82 MB fp8 session costs ~0.7 s of transfer.
- `live_serve.sh` defaults its jobs to `nproc` (128 on the L4 host against a 15.3-core quota): set `LIVE_JOBS` to the cgroup
  quota (`cpu.cfs_quota_us / cfs_period_us`, or `RUNPOD_CPU_COUNT`).
- One verifier can serve two provers ONE AFTER THE OTHER, never at once. Record the schedule in the handoff.
- `research data put` from a verifier pod needs `~/.research/store.toml`. It holds only the bucket, the endpoint and the
  NAMES of the credential env vars, so copy it from a bootstrapped prover. Mint the credential with
  `(set -a; source ~/.config/verity/r2.env; set +a; research data mint-credential --ttl 8h --env)` (without the parent secret
  it fails with `--via api needs CLOUDFLARE_API_TOKEN`).

## Where
- Pod `vy-live2b-verifier-ro` (pitmqu0zrycw5i), endpoint `tcp://213.173.105.92:56412`. It runs `python -m
  backends.direct.ligero.live serve --listen 0.0.0.0:7000 --out /workspace/live/sessions ...` from `/workspace/live/start.sh`.
  It is kept: read it only, never restart it or write there (coordinator, 2026-09-24 01:15Z).
- Store: `/workspace/live/sessions/`, one dir per session (`hello.json`, `session.json`, `verdict.json`) plus `index.jsonl`
  and `serve.log`. A dir with `hello.json` but no `session.json` is an open or aborted session with no record.

## Two protocols in one store
- `c…` ids: `live.ChallengeServerSession` (Ligerito challenge stream). `session.json` = `{"hello", "batches": [{batch,
  stmt_sha256, coins: [{r, s}], rounds: [{k, label, msg_sha256}]}]}`. `stmt_sha256` is sha256 of STMT =
  `lgto-stmt|v1| sha256(params) sha256(stmt file) sha256(key)`, not the statement file's hash.
- `s…` ids: `live.Session` (Ligero sub-batch verifier). `session.json` = `{"verdict", "subbatches"}`, with no `batches`.
- Snapshot 2026-09-24 01:02Z: 5 `c…` + 45 `s…`, all recorded (art:d04ee43a).

## Claims over the whole store (R3-10)
- The attempts on a statement are the recorded `c…` batches with its STMT across the whole store, so pass the whole
  store. Python: `run.py verify-session --sessions-root <store>`. Rust: `ligerito-verify batch --dir D --session <store>`
  (`lane/verify-rs-3` >= a87edaa0, where `s…` records count as zero batches; older builds panic "session record: no batches"
  on this store). A store with an open session, or a single record dir, authenticates but claims nothing (Rust 0e4ef1d1).
- Any new `c…` session on the same statement changes the counts, so recompute from a fresh copy.

## Read-only copy (JSON records only, about 3 MB)
~~~sh
SSH=$(research pods ssh --print vy-live2b-verifier-ro | tail -1)   # zsh: run it as ${=SSH}
${=SSH} 'cd /workspace/live && tar cf - sessions/index.jsonl sessions/*/hello.json sessions/*/session.json sessions/*/verdict.json' > ro-store.tar
~~~
Source: verify-rs-5 report (`lanes/verify-rs-5/`), art:f2f27f16.

## A lane's own `live_serve.sh` store: custody before terminating the verifier pod
`live_serve.sh` (main 24f252b1) keeps every proof and statement per session (`sub_NN.proof`, `sub_NN.stmt`): 48 sessions at
bf16-ampere 4096 VUs = 6.6 GB. The records worth keeping are small (~7 MB for 48): `index.jsonl`, per session
`hello.json`, `session.json`, `verdict.json`, the verifier-side Rust verdicts `rust_batch.json` + `rust_sub_*.json`, and
`sub_*.coins`. Tar those with a pod-side `sha256sum` list, check it on the laptop, `research data put --kind run-files/v1
--tree ... --preserve`. Example: wave-a100-2's verifier2 store, art:96ba1c1d (wave-a100-3, 2026-09-24).

## Whole live store preserved, and where to run `data preserved` (verifier-cost, 2026-09-24)
- The full `/workspace/live/sessions` of vy-live2b-verifier-ro (5.0 GB incl. `sub_NN.proof/.stmt/.coins`) is one
  run-files/v1 tree, art:d841eb56 (put from the pod with a minted short-lived credential; `data preserved` rc=0 on the pod).
- `research data preserved` on the laptop hashes every blob back from R2 (5 GB here) and has no overall timeout: run it
  pod-side (`research run --on <pod> ... python3 -m research data preserved <art>`), same credential via `--env`.
- D3 (drilldown.py) reads verifier cost from live records: the cell's own if it ran against a same-DC live verifier at 2^-128,
  else the median-`verify.cpu_s` run of the same config (relation, l, B, K, instances, authentication, SKU, pipeline).
  H100 rows: verifier on the prover pod (loopback, EU-NL-1); no same-DC RunPod CPU pod was used for H100.

## A-GKR verifier cost (offline, no live protocol)
- `verity-gkr-verify` (backends/gkr/verifier, no deps) re-verifies a GPU A-GKR cell's proof (4096 VUs) in ~2.9 s wall /
  ~14 CPU-s at 192 threads, ~8.5 CPU-s at 1 thread (EPYC 9654): verdicts art:8806507c (A100 cell), art:ae9d69fb (H100 cell).
  At 192 threads the CPU sum exceeds 1-thread CPU (spin/parallel overhead on a loaded host); quote both.
