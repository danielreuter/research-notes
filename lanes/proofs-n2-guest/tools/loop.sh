#!/usr/bin/env bash
# proofs-n2-guest: tmux `proofs-n2-guest` on vy-nebius-2 runs this; refill.py restarts after a crash, stops on exit 0 (rows done, or STOP)
G=/workspace/verity-guest/wholerow
while :; do
  nice -n 19 python3 $G/bin/refill.py >> $G/refill.out 2>&1; rc=$?
  [ $rc = 0 ] && break
  echo "$(date -u +%FT%TZ) refill.py rc=$rc, restarting in 60 s" >> $G/refill.out
  sleep 60
done
