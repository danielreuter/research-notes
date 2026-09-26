# pod1.sh NAME DC GPU DISK: at most one pod for NAME (red-team-flock-2's pattern: compare the pod list before/after; a new
# NAME-* pod counts whatever the create printed; only a no-stock reply is "no pod"). Last line: POD <id> | NOPOD <why>
cd /workspace; export PYTHONPATH=tools/research/src
NAME=$1 DC=$2 GPU=$3 DISK=${4:-60}
ours() { uv run research pods list 2>/dev/null | awk -v n="$NAME" '$2 ~ "^"n"-" {print $1}' | sort; }
before=$(ours)
[ -n "$before" ] && { echo "POD $(echo "$before" | head -1) (existing)"; exit 0; }
out=$(uv run python /tmp/gql/gql_gpu_pod.py "$NAME" "$DC" "$GPU" "$DISK" 2>&1)
sleep 5
new=$(comm -13 <(echo "$before") <(ours) | head -1)
[ -z "$new" ] && new=$(echo "$out" | grep -oE '"id": "[a-z0-9]+"' | head -1 | cut -d'"' -f4)
if [ -n "$new" ]; then
  uv run research pods register "$NAME" --pod-id "$new" --project verity --guard 45 --replace 2>&1 | tail -1 >&2
  echo "POD $new"; exit 0
fi
echo "NOPOD $(echo "$out" | grep -oE '"message": "[^"]*"' | head -1)"; exit 1
