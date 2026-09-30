---
id: 20260930T2215Z-handoff-from-infra-586-in-tqs-with-603
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: #586 failed in train TCL on a host leak. It's re-cut as TQS with #603 and should land about 3:52 PM PDT; infra accepted #603 for you

- **Why TCL failed:** two gpu-lease tests in `test_nebius2.py` read the host's `/etc/vy/direct-gpus`, which says "none" on node 1.
- **The fix:** #603, where the tests set `GPU_LEASE_ALLOWED_FILE` under `tmp_path`. Infra accepted it on your behalf.
- **TQS** carries #586, `--queue` (27676a80c), #603 and #326: run `r20260930-221143-c9f1`, expected merge `ce30e9b6`, about 40 min, so
  about 3:52 PM PDT. TQR is obsolete.
- **Your branch:** if you push again, rebase onto the merged main after TQS lands. #603's change is then already in.
- **The switch** stays on hold pending Daniel's OK (`note:20260930T2213Z-...`).
