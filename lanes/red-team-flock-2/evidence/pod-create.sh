#!/usr/bin/env bash
# red-team-flock-2: create at most ONE pod for NAME, trying SPECs in order, then register it.
#
#   pod-create.sh NAME PROJECT GUARD SPEC...     SPEC = cpu:<flavor>:<vcpu> | gpu:<type>:<cloud>   (type may contain spaces)
#
# A create is attempted WITHOUT --register, so its exit status speaks only about the pod. After each attempt the lane's
# pods are listed and compared with the list taken before: any new pod named NAME-* means a pod exists, whatever the
# create printed, and no further SPEC is tried. Only an explicit no-stock reply ("no instances currently available",
# "no longer any instances available") moves on to the next SPEC; any other failure stops. Registration is a separate
# step with --replace (the name may still point at a terminated pod); if it fails the pod id is printed and the script
# exits 3, so the caller registers or terminates that pod instead of creating another.
# Output: last line `POD <id> <spec>` (exit 0), or `NOPOD <why>` (exit 1/2), or `UNREGISTERED <id> <why>` (exit 3).
set -uo pipefail
NAME=$1 PROJECT=$2 GUARD=$3; shift 3
if command -v research >/dev/null 2>&1; then R=(research); else R=(env PYTHONPATH=/workspace/tools/research/src python3 -m research); fi
ours() { "${R[@]}" pods list 2>/dev/null | awk -v n="$NAME" '$2 ~ "^"n"(-|$)" {print $1}' | sort; }
before=$(ours)
log=$(mktemp)
for spec in "$@"; do
  kind=${spec%%:*}; rest=${spec#*:}; a=${rest%%:*}; b=${rest#*:}
  if [ "$kind" = cpu ]; then args=(--cpu "$a" --vcpu "$b"); else args=(--gpu "$a" --min-vcpu 8 --min-ram 30 --cloud "$b"); fi
  "${R[@]}" pods create --name "$NAME" "${args[@]}" --disk 40 > "$log" 2>&1; rc=$?
  new=$(comm -13 <(echo "$before") <(ours) | head -1)
  if [ -z "$new" ]; then
    new=$(grep -oE '^  "id": "[a-z0-9]+"' "$log" | head -1 | cut -d'"' -f4)
  fi
  if [ -n "$new" ]; then
    reg=$("${R[@]}" pods register "$NAME" --pod-id "$new" --replace --project "$PROJECT" --guard "$GUARD" 2>&1 | tail -1)
    if echo "$reg" | grep -qE '^(REGISTERED|UPDATED) '; then echo "POD $new $spec"; exit 0; fi
    echo "UNREGISTERED $new register said: $reg"; exit 3
  fi
  if [ $rc -ne 0 ] && grep -qE 'no instances currently available|no longer any instances available' "$log"; then
    echo "no stock: $spec" >&2; continue
  fi
  echo "NOPOD create failed on $spec (rc=$rc): $(grep -v "^[[:space:]]*$" "$log" | tail -1 | cut -c1-200)"; exit 2
done
echo "NOPOD no stock on any spec"; exit 1
