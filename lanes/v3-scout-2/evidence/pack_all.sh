#!/bin/bash
# pack_all.sh POD TAG... (runs on the pod): put_pack.sh for every TAG not yet in packed.txt; one line "TAG art:..." per pack.
# put_pack.sh = the predecessor's run-files/v1 pack (result, Rust verdict, logs, rep-1 dump), PRESERVED on R2 from the pod.
POD=$1; shift
O=/workspace/v3s; touch $O/packed.txt
for TAG in "$@"; do
  grep -q "^$TAG " $O/packed.txt && continue
  [ -f $O/results/$TAG.json ] || { echo "$TAG MISSING" >> $O/packed.txt; continue; }
  ID=$(bash /workspace/put_pack2.sh $TAG $POD 2>>$O/logs/pack_err.log | /workspace/venv312/bin/python -c \
       'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])' 2>>$O/logs/pack_err.log)
  echo "$TAG ${ID:-FAILED} $(date -u +%H:%M:%S)" >> $O/packed.txt
done
echo "PACK_DONE $(date -u +%H:%M:%S)" >> $O/packed.txt
