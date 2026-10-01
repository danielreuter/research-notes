#!/usr/bin/env bash
# Prints a line (and so wakes watch_inbox.sh) when node 1 admits again, commit-release may release, or gm end events pass ENDS.
SSH=$(/workspace/.venv/bin/research pods ssh vy-nebius-1 --print 2>/dev/null)
out=$($SSH 'export KUBECONFIG=$HOME/.kube/config
for q in deployments-cpu deployments-gpu; do
  p=$(kubectl get clusterqueue $q -o jsonpath="{.spec.stopPolicy}")
  [ "$p" = Hold ] || echo "$q stopPolicy now ${p:-None}"
done
[ -e /home/research/commit-release/no-release ] || echo "no-release removed"
echo "ends $(grep -c "\"ev\": \"end\".*vllm-epoch-run/cov-gm" /workspace/jobs/dispatch/log.jsonl)"' 2>/dev/null) || exit 0
n=$(sed -n 's/^ends //p' <<< "$out")
grep -v "^ends " <<< "$out" | grep -v "${SKIP:-^\$}" | grep .
[ -n "$n" ] && [ "$n" -gt "${ENDS:-999999}" ] && echo "gm end events $n (was $ENDS)"
true
