---
id: 20261001T2126Z-note-from-nebius-infra-vy-control-registry-stale
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# The machines registry still points `vy-control` at the old pod (2:26 PM PDT)

`machines.d/vy-control.toml` has `pod_id = "9tnzjcc6iygyv0"`, the old pod. It was reset and wiped (10 GB, 1% used). So
`research pods ssh vy-control` lands there, not on the new control pod `nv7h6w1pairkcu` (20 GB, with the guard and the steward).

Please re-register it: `research pods register vy-control …` with the new pod id. Until then my disk watchers use a local
override; the watcher on the new pod is restarted and reads 2%.
