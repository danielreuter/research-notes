# Live verifier (kept RO instance) and its session store

## GOTCHA: CA-MTL-1 (GPU.ONE) does not hairpin public IPs between pods
Two pods in RunPod CA-MTL-1 (H100 prover 69.30.85.160, A40 verifier 69.30.85.40, both AS20016 GPU.ONE) could not reach
each other on ANY mapped public port (ssh or :7000 mapping), both directions: `Connection refused`; the laptop reached both.
Container IPs (172.x) are separate networks. So a same-DC live verifier on a second pod does not work there; test with
`timeout 4 bash -c '</dev/tcp/IP/PORT'` from the prover BEFORE launching live runs. (wave-h100-2, 2026-09-24 04:08Z; EU-RO-1
pods did reach each other per live-2c.)

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
