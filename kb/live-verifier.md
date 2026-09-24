# Live verifier (kept RO instance) and its session store

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
