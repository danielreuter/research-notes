#!/usr/bin/env bash
# fill-dc (laptop): register every finished, successful run on POD that registered.txt does not list yet (no trees: sweep runs).
#   reg-new.sh POD [TAG-GLOB]      warm-* and probe (hp-*) runs are skipped (untimed --reps 1)
pod=$1 glob=${2:-*}
E=~/.research/notes/lanes/fill-dc/evidence
K=(-i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR -o ConnectTimeout=15)
case $pod in h100) S=(ssh "${K[@]}" -p 10179 root@91.199.227.82) ;; a100) S=(ssh "${K[@]}" -p 16369 root@157.157.221.29) ;; esac
for line in $("${S[@]}" "cd /workspace/fill-dc/runs && for d in $glob; do [ -f \$d/result.json ] && grep -q 'rc=0' \$d/meta.txt && [ ! -d \$d/proofs ] && echo \$d; done"); do
  case $line in warm-*|hp-*) continue ;; esac
  grep -q " $pod $line result=" $E/registered.txt 2>/dev/null && continue
  bash $E/reg.sh $pod $line "$pod sweep $line local coins (no dump)"
done
