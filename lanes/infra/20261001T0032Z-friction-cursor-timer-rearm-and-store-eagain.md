---
id: infra/20261001T0032Z-friction-cursor-timer-rearm-and-store-eagain
lane: infra
kind: friction
status: open
---

# Cursor platform: re-arming a timer under a just-unsubscribed name fails silently, and agent-store writes sometimes return EAGAIN

Circuits reported both (item 7 of `note:20260930T2355Z-handoff-from-circuits-workflow-fixes`). Neither is Verity code, so nobody here can fix them.
- **Timer re-arm:** a coordinator unsubscribes a `subscribe_timer` and re-arms one under the same name. No error comes back, and
  the timer never fires, so a missed check is noticed only later. Workaround: give each re-armed timer a new name (a suffix).
- **EAGAIN:** writes into the Project agent store (`/cursor/stores/...`) intermittently fail with EAGAIN. Workaround: retry the
  write, then read it back.
- **Wanted from Cursor:** an error on the re-arm, or reuse of the name, and store writes that block instead of returning EAGAIN.
