#!/usr/bin/env bash
# arith H100 (diagnostic): does flushing rep 1's proof dump to disk (os.sync, untimed) before rep 2 remove the slow rep 2?
# tip vs tip + relchain os.sync (/workspace/src-sync, relchain.py shipped as relchain-sync.py), BF16 local, 4 rounds.
source /workspace/arith/scripts/lib.sh
export LIGERO_REFERENCE_HINTS=0
while pgrep -f "[h]100-ab2.sh" >/dev/null; do sleep 5; done
rm -rf /workspace/src-sync && cp -a /workspace/src /workspace/src-sync && cp /workspace/arith/scripts/relchain-sync.py /workspace/src-sync/backends/direct/ligero/relchain.py
echo "src-sync: $(grep -c 'os.sync()' /workspace/src-sync/backends/direct/ligero/relchain.py) os.sync" | tee -a $LOG
for rr in 1 2 3 4; do
  if [ $((rr % 2)) = 1 ]; then order="tip sync"; else order="sync tip"; fi
  for a in $order; do
    case $a in
      tip) run hsy-tip-r$rr bf16-hopper-v3x4 4096 8 5 ;;
      sync) SRC=/workspace/src-sync COMMIT=$TIP-sync run hsy-sync-r$rr bf16-hopper-v3x4 4096 8 5 ;;
    esac
  done
done
echo DONE-hsync
