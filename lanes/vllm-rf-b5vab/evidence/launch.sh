# usage: launch.sh LOG POD SOURCE TIMEOUT SCRIPT ENV...   (retries on the store FS's EAGAIN)
LOG=$1 POD=$2 SRC=$3 TMO=$4 SCRIPT=$5; shift 5
ENVS=(); for e in "$@"; do ENVS+=(--env "$e"); done
cd /workspace
for i in $(seq 1 15); do
  PYTHONPATH=tools/research/src python3 -m research run --on $POD --project verity --custody-r2 --source $SRC --cwd source --timeout $TMO "${ENVS[@]}" --send $SCRIPT -- bash -c "bash \"\$RESEARCH_RUN_DIR/inputs/$(basename $SCRIPT)\"" > $LOG 2>&1 && break
  grep -q "BlockingIOError" $LOG || break
  sleep 10
done
echo "LAUNCHER DONE" >> $LOG
