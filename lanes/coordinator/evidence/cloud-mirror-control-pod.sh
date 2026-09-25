#!/usr/bin/env bash
# One pass of the store <-> notes mirror for cloud lanes, through the steward's notes clone on vy-control-verity.
#   forward: store lanes/<L>/ for L in CLOUD-LANES.txt, every *-handoff-from-<L>*.md, lanes/coordinator/*-report-coordinator.md,
#            *-handoff-from-coordinator*.md written in the store, machines.d/  ->  pod notes clone; then `research notes sync` there
#   reverse: pod kb/, lanes/*/*.md, machines.d/  ->  store, never the files cloud writers own (their reports, evidence, handoffs)
# Forward compares by checksum, reverse by size + mtime; neither replaces a newer receiver file (-u); nothing is deleted; files over 1 MB stay out.
# Loop: tmux session cloud-mirror on the cloud research coordinator's VM runs a local copy (~/cloud-mirror/pass.sh) every 5 min.
set -u
S=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal
N=/workspace/steward/research-notes
REPO=${REPO:-/workspace}
stamp() { date -u +%H:%MZ; }

cd "$REPO" || exit 1
line=$(RESEARCH_MACHINES_D=/tmp/machines.d PYTHONPATH=tools/research/src python3 -m research pods ssh vy-control-verity --print 2>&1) || { echo "$(stamp) FAIL ssh line: $line"; exit 1; }
host=${line##* }
sshcmd=${line% *}
for i in 1 2 3 4 5 6; do l=$(cat "$S/lanes/CLOUD-LANES.txt" 2>/dev/null) && break; sleep 5; done
[ -n "${l:-}" ] || { echo "$(stamp) FAIL CLOUD-LANES.txt unreadable (store busy)"; exit 1; }
lanes=$(grep -Ev '^\s*(#|$)' <<<"$l" | tr -d ' \r')
# the store answers EAGAIN under load: rsync rc 23/24 (some files unread) is a partial pass, the next one catches up
ok() { [ "$1" = 0 ] || [ "$1" = 23 ] || [ "$1" = 24 ]; }

fwd=(--include=/lanes/ --include=/lanes/*/ --include=/machines.d/ --include=/machines.d/*.toml
     --include=/lanes/coordinator/*-report-coordinator.md --include=/lanes/*/*-handoff-from-coordinator*.md
     --include=/lanes/coordinator/evidence/ --include=/lanes/coordinator/evidence/cloud-mirror-control-pod.sh)
rev=(--exclude=/lanes/coordinator/*-report-coordinator.md --exclude=*-handoff-from-coordinator*.md)
for l in $lanes; do
  fwd+=(--include="/lanes/$l/***" --include="/lanes/*/*-handoff-from-$l*.md")
  rev+=(--exclude="/lanes/$l/*-report-$l.md" --exclude="/lanes/$l/evidence/" --exclude="*-handoff-from-$l*.md")
done
fwd+=(--exclude='*')
rev+=(--include=/kb/*** --include=/lanes/ --include=/lanes/*/ --include=/lanes/*/*.md --include=/machines.d/ --include=/machines.d/*.toml --exclude='*')

opts=(-rcuW --max-size=1m --omit-dir-times --no-perms --itemize-changes -e "$sshcmd")
# reverse by size + mtime: checksumming every notes file over the store mount took minutes
ropts=(-rtuW --max-size=1m --omit-dir-times --no-perms --itemize-changes -e "$sshcmd")
out=$(rsync "${opts[@]}" "${fwd[@]}" "$S/" "$host:$N/" 2>&1); frc=$?
ok $frc || { echo "$(stamp) FAIL forward rsync rc=$frc: ${out: -300}"; exit 1; }
nf=$(grep -c '^<f' <<<"$out")

sync=$(timeout 240 $sshcmd "$host" "cd /workspace/steward/verity && PY=\$(/root/.local/bin/uv python find 3.12) && \
  PYTHONPATH=tools/research/src \$PY -m research notes sync --root $N -m 'cloud mirror $(date -u +%Y-%m-%dT%H:%MZ): $nf files' 2>&1 | tail -3")
src=$?

echo "$(stamp) forward $nf (rc $frc); sync rc=$src: $(tr '\n' ' ' <<<"$sync")"
out2=$(timeout 240 rsync "${ropts[@]}" "${rev[@]}" "$host:$N/" "$S/" 2>&1); rrc=$?
[ $rrc = 124 ] && { echo "$(stamp) reverse cut at 240 s (continues next pass)"; exit 0; }
ok $rrc || { echo "$(stamp) FAIL reverse rsync rc=$rrc: ${out2: -300}"; exit 1; }
nr=$(grep -c '^>f' <<<"$out2")

echo "$(stamp) pass: forward $nf (rc $frc), reverse-rc $rrc, reverse $nr, lanes [$(echo $lanes | tr ' ' ,)]; sync rc=$src: $(tr '\n' ' ' <<<"$sync")"
[ "$nf" -gt 0 ] && grep '^<f' <<<"$out" | awk '{print "  > " $2}' | head -20
[ "$nr" -gt 0 ] && grep '^>f' <<<"$out2" | awk '{print "  < " $2}' | head -20
exit 0
