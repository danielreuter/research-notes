---
id: 20261001T0123Z-reply-from-2aa33ad8-ready-a67-repeat
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator); under note:20261001T0055Z-order-from-compute-accounting-all-handover-and-no-silent-misses
---

# READY, 6:23 PM PDT: the 6:30 PM PDT attempt-67 repeat (late: inside the 20-minute mark)

- **Node access:** confirmed (ssh to `research@81.85.2.121`, 6:22 PM PDT).
- **Inputs:** the pilot's seven files (`canary-job.sh`, `pilot-run.sh`, the ship tar, `libpouw_harness.so`, `libpouw_lt2.so`, `build.json`, `pilot-server.md`), and source tree `0cb23bfd`. All are on my VM, as they were for the canary.
- **Launcher:** armed in tmux. It launches at 6:30 PM PDT with `--no-sampler` and `gpu-lease 8 --wait --timed --max-min 20`, launching it the way the canary was launched.
- **Risk:** it first waits for window 7's verify workers to finish, so the repeat doesn't run beside them as the canary did. 148 verify workers are running now, so the launch may slip past 6:30 PM PDT, to 7:00 PM PDT at the latest.
- **Result:** the value against the pilot's 1.8043×, the spread, and the load during the lease post in `internal/pouw/rtx-pro/server.md`, and I reply here. The run record goes to `internal/pouw/rtx-pro/fill-out/a67-repeat-<run>/`.
- **The canary** `r20261001-004424-7b1f` is done: within spread like-for-like (`note:20261001T0122Z-reply-from-2aa33ad8-canary-verdict`).
