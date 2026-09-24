---
lane: coordinator
kind: handoff
created: now
---
# coordinator: read LANE-CONTRACT §3a (chatter budget, v1.2) — poll pods with foreground commands, not background sleeps

Every background local shell you start pings the coordinator and the human when it ends. Run long jobs detached on the pod
and check them with short FOREGROUND ssh commands (no background `sleep N; tail` polls). One-line checkpoints. No reply needed.
