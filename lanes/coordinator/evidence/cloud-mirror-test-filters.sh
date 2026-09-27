#!/usr/bin/env bash
# Local test of filters.sh with the mirror's rsync options: exit 0 when every case holds.
set -u
here=$(cd "$(dirname "$0")" && pwd)
. "$here/filters.sh"
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
S=$t/store; N=$t/pod
mkdir -p "$S/lanes/lane-a" "$S/lanes/lane-b" "$S/lanes/coordinator" "$N/lanes/lane-a" "$N/lanes/lane-b"
printf -- '---\ncursor: store copy\n---\nsame handoff\n' > "$S/lanes/lane-b/20260926T0335Z-handoff-from-lane-a.md"
printf -- '---\nlane: lane-b\n---\nsame handoff\n' > "$N/lanes/lane-b/20260926T0335Z-handoff-from-lane-a.md"
touch -d '2026-09-26 04:00' "$N/lanes/lane-b/20260926T0335Z-handoff-from-lane-a.md"      # older than the store's copy
echo new > "$S/lanes/lane-b/20260926T0400Z-handoff-from-lane-a.md"
echo brief > "$S/lanes/lane-a/20260926T0401Z-handoff-from-coordinator.md"
echo report > "$S/lanes/lane-a/20260926T0100Z-report-lane-a.md"
echo pushed > "$N/lanes/lane-a/20260926T0402Z-handoff-from-lane-b.md"
echo storecopy > "$S/lanes/lane-a/20260926T0402Z-handoff-from-lane-b.md"

mirror_filters lane-a
opts=(-rcuW --max-size=1m --omit-dir-times --no-perms)
rsync "${opts[@]}" "${fwd[@]}" "$S/" "$N/" && rsync "${opts[@]}" --ignore-existing "${fwdh[@]}" "$S/" "$N/" || exit 1

fail=0
check() { if eval "$2"; then echo "ok   $1"; else echo "FAIL $1"; fail=1; fi; }
check "a handoff the pod already has (pushed by the lane) keeps the pod's copy" \
      "grep -q 'lane: lane-b' '$N/lanes/lane-b/20260926T0335Z-handoff-from-lane-a.md'"
check "a handoff in a cloud lane's own folder the pod already has keeps the pod's copy" \
      "grep -qx pushed '$N/lanes/lane-a/20260926T0402Z-handoff-from-lane-b.md'"
check "a new handoff from a cloud lane is forwarded" "[ -f '$N/lanes/lane-b/20260926T0400Z-handoff-from-lane-a.md' ]"
check "a new handoff from the coordinator is forwarded" "[ -f '$N/lanes/lane-a/20260926T0401Z-handoff-from-coordinator.md' ]"
check "a cloud lane's report is forwarded" "[ -f '$N/lanes/lane-a/20260926T0100Z-report-lane-a.md' ]"

# machines.d: the later registration wins by registered_at, whatever the mtimes (vy-verify-night-3, 2026-09-26)
mkdir -p "$t/md-store" "$t/md-pod"
printf 'pod_id = "heudtct27whkty"\nregistered_at = "2026-09-26T05:33Z"\n' > "$t/md-store/vy-a.toml"
printf 'pod_id = "o2gvkt3wwmn1le"\nregistered_at = "2026-09-25T23:20Z"\n' > "$t/md-pod/vy-a.toml"
touch -d '2026-09-26 06:00' "$t/md-pod/vy-a.toml"                                           # the stale copy is newer on disk
printf 'pod_id = "pushedbylane"\nregistered_at = "2026-09-26T05:40Z"\n' > "$t/md-pod/vy-b.toml"
printf 'pod_id = "storecopy"\nregistered_at = "2026-09-26T04:00Z"\n' > "$t/md-store/vy-b.toml"
printf 'pod_id = "onlyinstore"\nregistered_at = "2026-09-26T05:00Z"\n' > "$t/md-store/vy-c.toml"
python3 "$here/machines_merge.py" "$t/md-store" "$t/md-pod" >/dev/null || exit 1
check "a fresh registration in the store beats an older one with a newer mtime on the pod (both sides)" \
      "grep -q heudtct27whkty '$t/md-pod/vy-a.toml' && grep -q heudtct27whkty '$t/md-store/vy-a.toml'"
check "a newer registration on the pod wins over an older store copy" "grep -q pushedbylane '$t/md-store/vy-b.toml'"
check "a registration only one side has reaches the other" "[ -f '$t/md-pod/vy-c.toml' ]"
exit $fail
