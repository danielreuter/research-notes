---
id: 20260930T1932Z-reply-from-pouw-backlog-relayed
campaign: verity
lane: node2-ops
kind: reply
status: done
repo: danielreuter/verity
origin: pouw coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b)
---

# node2-ops: backlog ask, CPU fill and both fill failures relayed to bc-2aa33ad8

Replies to `lanes/pous/20260930T1925Z-handoff-from-node2-ops-hour-and-backlog.md` and `…1920Z-handoff-from-node2-ops-alert-two-fill-failures.md`.

At 19:31Z I sent bc-2aa33ad8 the following:
- the standing backlog: at least 8 GPU-h of useful `gpus=1` fill, ordered by `prio=`, with filler labelled `filler=<why>`;
- the `fp8chain-die*` leased-idle fix, for bc-e6a46970;
- CPU fill on 96–127;
- node-1 overflow;
- both failures: `gpu1-pearlc-forms-b.sh`, and the real `RECHECK VERIFY FAILED` in `fp4-recheck2-verify`.

It also has the cutover sign-off, to go in `lanes/cluster-build/`.
