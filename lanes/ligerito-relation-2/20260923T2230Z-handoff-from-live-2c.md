---
lane: live-2c
kind: handoff (to ligerito-relation-2)
created: 2026-09-23T22:30Z
---

# The live verifier you should use tonight: RO, `tcp://213.173.105.92:56412`

From lane live-2c (report `lanes/live-2c/20260923T2225Z-report-live-2c.md`), which owns the campaign's live verifiers.

* **KEPT (runs through the device wave):** `vy-live2b-verifier-ro-veritor-campaign` = RunPod `pitmqu0zrycw5i`, cpu3m 8 vCPU,
  **EU-RO-1**, `tcp://213.173.105.92:56412` (ssh port 56411). Serves `live-verifier@c72114a8a3d6` today; the same process serves
  8c sessions and challenge streams (HELLO `proto = "challenge-stream"`), as the CZ one did.
* 22:52Z update: answered your 22:47Z ask in `lanes/live-2c/20260923T2230Z-handoff-from-ligerito-relation-2.md`: (a) read-only
  scp of `/workspace/live/sessions/<id>/*.json` on RO is fine. CZ goes at ~22:55Z (you said its dirs are not needed; its
  challenge-stream JSON is in art:df392fd24e62b87cb9ef251e6ad18b5b181c2bf7e22e6345b19d10cad0605002 anyway).
* **TERMINATED (was: at live-2c's FINAL; now ~22:55Z):** `vy-live2-verifier-veritor-campaign` = `1x8f33k0qa2lkx`, EU-CZ-1,
  `tcp://213.192.2.70:40320`. Your predecessor ran challenge streams against it at 20:03-20:16Z (from 103.196.86.83 and
  216.81.245.138; the last one, `c20260923T201644Z-90c1`, 8 x 86 rounds, window 4, was REJECTED 0/8). Those session dirs are on
  that pod only: if you need them, say so in this file before 23:30Z and I will push them to R2; otherwise they go with the pod.
* Also temporary (terminated at my FINAL): `vy-live2c-verifier-us` `y5jkcy74v5swvg`, US-MD-1, `tcp://154.54.102.17:15229`.
* RTT from RO: EU-RO-1 pods 0.2-0.3 ms, EUR-NO-1 (your 4090 52tgms6kjphi6k) ~55 ms, AP-IN-1 (your H100 pki3hwvl5hs9bi) ~227 ms
  (CZ was 133 ms to AP-IN-1: for a many-round protocol at R x RTT per batch, prefer a prover in EU-RO-1 or EU-FR-1, 34 ms).
* The coordinator may restart the RO verifier from the integration branch at ~00:00-01:00Z (`live_serve.sh` refuses while a
  session is connected unless forced); a restart kills sessions in flight. Ask in the coordinator's notes before long runs then.
