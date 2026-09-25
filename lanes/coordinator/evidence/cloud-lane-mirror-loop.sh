#!/bin/bash
# The cloud-lane mirror, every 5 minutes, detached from any agent shell so a worker disconnect doesn't stop it.
# Start: nohup setsid bash ~/.research/notes/lanes/coordinator/evidence/cloud-lane-mirror-loop.sh >/dev/null 2>&1 &
# Stop:  kill $(cat /tmp/cloud-lane-mirror-loop.pid)
cd "$HOME" || exit 1
echo $$ > /tmp/cloud-lane-mirror-loop.pid
while :; do
  bash "$HOME/.research/notes/lanes/coordinator/evidence/cloud-lane-mirror.sh" >> /tmp/mirror-loop.out 2>&1
  sleep 300
done
