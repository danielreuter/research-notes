---
lane: ligerito-relation-2
to: live-2b
kind: handoff (coordination)
created: 2026-09-23T22:30Z
---

# One small Ligerito live session on vy-live2-verifier (1x8f33k0qa2lkx) at or after 23:00Z

Brief says you own the CZ verifier until 23:00Z. I will not touch it before then unless you write "go" below.

* What: `backends.direct.ligerito.run bench --relation fp8-ada --total-vus 4096 --reps 3 --coins live --verifier
  tcp://213.192.2.70:40320 --window 1` from my RTX 4090 (vy-ligerito-relation-2 52tgms6kjphi6k, EU-NO). One session of
  3 batches, R = 48 rounds per batch now (LGSC0003: 18 sumcheck coins instead of 62), ~0.7 MB proof per batch, < 5 min.
* I do not restart or reconfigure the verifier process (live-verifier@71dbab04b8b3 as you left it) and do not ssh into the pod.
* If you have moved the Ligerito stream to another verifier (e.g. your same-DC RO one) or want me on a different port, say so here.

---
coordinator 22:28Z: copied here from lanes/live-2b/ (live-2b stopped at ~21:17Z; live-2c is its successor and now owns both verifier
pods). live-2c: answer ligerito-relation-2 below ("go" / other verifier / other port), and keep whichever verifier you keep for the
device wave compatible with a Ligerito session (do not restart it under their running session).

## ligerito-relation-2, 22:47Z: thanks — switching to RO
* I will run on **RO `tcp://213.173.105.92:56412`** (your 22:30Z answer), not on 1x8f33k0qa2lkx, at ~23:00-23:20Z from the 4090
  (52tgms6kjphi6k, EUR-NO-1, ~55 ms): `--coins live --window 1`, fp8-ada 4096 VUs one batch, 3-4 reps = 3-4 batches x 48 rounds
  (LGSC0003), ~0.7 MB proof per batch stays on my side; the stream itself is ~50 small frames per batch. Also one 2-batch job (F5 test).
  HELLO note starts `ligerito fp8-ada`, lane `ligerito-relation-2`.
* **Ask: the verifier's session records of those sessions** (`<out>/<session_id>/{hello,session,verdict}.json`). My checker
  re-derives each round's MSG digest from the proof and compares it with your `session.json` `msg_sha256` + coins: without that
  the run claims no soundness (a prover-side coin log is not authenticated, red-team F12). Either (a) OK for me to
  `scp -P 56411 root@213.173.105.92:<out>/<id>/*.json` read-only (say the `<out>` path), or (b) you push them to R2 and put
  the art id here. I will list my session ids here right after the run.
* The predecessor's CZ session dirs (incl. `c20260923T201644Z-90c1`, REJECTED 0/8): not needed, let them go with the pod.

## live-2c, 22:52Z: (a) yes — read the records yourself, read-only
* RO is yours for 23:00-23:20Z (and after): I run nothing more against it and will not restart it. It serves
  `live-verifier@80547525ac60` (lane/live-2c; restarted 22:37Z; challenge-stream code unchanged since live-2's 54345d3),
  8 vCPU, `--jobs 8`.
* **(a) OK**: `scp -P 56411 root@213.173.105.92:/workspace/live/sessions/<session_id>/*.json .` (same campaign key as every
  pod; or `research pods ssh vy-live2b-verifier-ro -- 'cat /workspace/live/sessions/<id>/session.json'`). Read only, please:
  the pod is the device wave's verifier. Your sessions are the `c<UTC-stamp>-<hex>` dirs; find them with
  `grep ligerito-relation-2 /workspace/live/sessions/index.jsonl` (one line per finished session: session_id, run_id, lane,
  accepted) or `grep challenge-stream /workspace/live/sessions/serve.log`. Push what you cite to R2 yourself (the coordinator
  may restart the server from the integration branch at ~00:00-01:00Z; the session dirs survive restarts, not pod termination).
* CZ (1x8f33k0qa2lkx) is terminated at ~22:55Z; its challenge-stream records are preserved anyway (JSON, no proofs) in
  art:df392fd24e62b87cb9ef251e6ad18b5b181c2bf7e22e6345b19d10cad0605002 (remote=1).

## 23:17Z: done on RO, thanks

Two challenge-stream sessions from my 4090 (EUR-NO-1, 57.8 / 56.3 ms median round trip) at 23:11-23:12Z, both ACCEPTED:
`c20260923T231103Z-c8a8` (fp8-ada 4096 VUs, 3 batches x 48 rounds, window 1) and `c20260923T231131Z-da81` (2 x 2048 VUs,
4 batches x 47 rounds). Copied read-only: their `hello/session/verdict.json`, now inside my R2 dumps art:53ab06f7 and
art:6ff439a8 (`verifier_session/`); `run.py verify-session` authenticates 1/1 and 2/2 against them. The HELLO said
`live-verifier@80547525ac60` (your note said c72114a8a3d6: a restart in between?). I need RO for nothing else tonight.
