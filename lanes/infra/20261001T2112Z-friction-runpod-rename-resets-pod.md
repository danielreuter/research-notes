---
id: infra/20261001T2112Z-friction-runpod-rename-resets-pod
lane: infra
kind: friction
status: open
severity: incident
---

# Renaming a RunPod pod through the API resets it and wipes its container disk

The control-pod handover (old 9tnzjcc6iygyv0 → new nv7h6w1pairkcu) went through: by 20:58Z the guard and the steward ran on the
new pod. Then infra renamed both pods with `PATCH https://rest.runpod.io/v1/pods/{id}` and a body of only `{"name": ...}`
(old → `vy-control-verity-old`, new → `vy-control-verity`). The API answered at once with the pod and an unchanged
`lastStartedAt`, and the container was still up 5 s later. About 30 s after that, RunPod reset both containers. On a CPU pod
everything outside a network volume sits on the container disk, so the reset wiped both pods' `/workspace` and `/root`, and
the SSH ports changed.

What it cost:
- The spend guard was down from about 20:59:30Z to 21:04:14Z, during which `pods create` failed closed. No lane pods were
  running.
- The steward was down from 20:59Z to 21:12Z.
- Lost for good: the guard's spend tallies; `/root/.research` (the store, run records, and six chats archives never pushed);
  the steward's local store and `watch.log`; the git deploy keys; console's `panels.key`, console loop and code; and root's
  `control_disk_pod.sh`.
- Survived: `/data` (the 1 TB network volume): `chats`, `research` and `research-control`.

What I did instead:
- Restored the pod from my VM's secrets: the RunPod key, R2 keys, the notes token and the RunPod SSH key.
- Installed main `e221350fd` as the guard's and steward's code, and put all state under `/data`, with symlinks and a boot script
  at `/data/boot/post_start.sh`.
- The steward runs without `--reap` until it can fetch verity's `lane/*` branches again; that needs a new read-only deploy key.

Better: treat any `PATCH /pods/{id}` as a reset. Never rename or edit a pod that holds state on its container disk. A stateful
pod keeps everything on a network volume and boots from a script stored there.
