# Filter rules of the store <-> notes mirror (sourced by pass.sh and test-filters.sh).  mirror_filters LANES... sets:
#   fwd   store -> pod, every file but handoffs (rsync -u: a newer pod copy is never replaced)
#   fwdh  store -> pod, handoffs only, sent with --ignore-existing: a handoff is write-once, so one the pod already has (a cloud
#         lane pushed it to the notes remote itself) is never replaced by the store's copy -- the two differ only in the store's
#         front matter, and replacing it made every steward sync a rebase conflict (83 commits behind, 2026-09-26)
#   rev   pod -> store
# machines.d/ is in neither: machines_merge.py merges it by each registration's registered_at, never by mtime (a rewrite of the
# pod clone gave last night's vy-verify-night-3.toml a newer mtime and it replaced the fresh registration, 2026-09-26)
mirror_filters() {
  fwd=(--exclude='/lanes/*/*-handoff-*.md'
       --include=/lanes/ --include=/lanes/*/
       --include=/lanes/coordinator/*-report-coordinator.md
       --include=/lanes/coordinator/evidence/ --include=/lanes/coordinator/evidence/cloud-mirror-control-pod.sh)
  fwdh=(--include=/lanes/ --include=/lanes/*/ --include='/lanes/*/*-handoff-from-coordinator*.md')
  rev=(--exclude=/lanes/coordinator/*-report-coordinator.md --exclude=*-handoff-from-coordinator*.md)
  local l
  for l in "$@"; do
    fwd+=(--include="/lanes/$l/***")
    fwdh+=(--include="/lanes/$l/*-handoff-*.md" --include="/lanes/*/*-handoff-from-$l*.md")
    rev+=(--exclude="/lanes/$l/*-report-$l.md" --exclude="/lanes/$l/evidence/" --exclude="*-handoff-from-$l*.md")
    # a cloud lane owns its folder in the store: only handoffs to it come back, never an older STATE.md / READY.md
    rev+=(--include="/lanes/$l/*-handoff-*.md" --exclude="/lanes/$l/*")
  done
  fwd+=(--exclude='*')
  fwdh+=(--exclude='*')
  rev+=(--include=/kb/*** --include=/lanes/ --include=/lanes/*/ --include=/lanes/*/*.md --exclude='*')
}
