#!/usr/bin/env bash
# red-team-flock PB3: non-producer replay of 8 Chunk(n)/wgmma cells' verifier sessions (flock-pure-gpu replay, CPU build at
# e4f631bd), on the verifier pods' own instance files (replay recomputes a/b/y roots natively; admission applies NV1/CN2).
set -uxo pipefail
I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
MODE=build GPU=0 bash backends/flock/pod/20-gpu-link.sh > $O/build.log 2>&1 || { tail -30 $O/build.log; exit 1; }
source $HOME/.cargo/env
B=/workspace/flock-gpu-link/flock/target/release/flock-pure-gpu; sha256sum $B | tee $O/binary.sha256
for t in $I/*.tgz; do
  a=$(basename $t .tgz); S=/workspace/rep-$a; rm -rf $S; mkdir -p $S; tar xzf $t -C $S
  NET=$(ls $S/net-*.txt); PIN=$(sha256sum $NET | cut -c1-64); n=0; bad=0
  for sd in $S/p*/sessions-s*; do
    inst=$(dirname $sd)/instances-s${sd##*sessions-s}.bin
    for ses in $sd/l*; do
      [ -f $ses/pure.rep0.bin ] || continue
      line=$($B replay --instances $inst --netlist $NET --pin $PIN --session $ses/session.json --proofs $ses/pure.rep0.bin,$ses/pure.rep1.bin 2>&1 | grep '^REPLAY\|REFUSED' | head -1)
      n=$((n+1)); echo "$a $(basename $ses) $line" | cut -c1-260 >> $O/replay.txt
      echo "$line" | grep -q '"accepted":true' || bad=$((bad+1))
    done
    s1=$(ls -d $sd/l* | while read d; do [ -f $d/pure.rep0.bin ] && echo $d; done | sed -n 1p); s2=$(ls -d $sd/l* | while read d; do [ -f $d/pure.rep0.bin ] && echo $d; done | sed -n 2p)
    for neg in other swap; do
      if [ $neg = other ]; then p="$s2/pure.rep0.bin,$s2/pure.rep1.bin"; else p="$s1/pure.rep1.bin,$s1/pure.rep0.bin"; fi
      line=$($B replay --instances $inst --netlist $NET --pin $PIN --session $s1/session.json --proofs $p 2>&1 | grep '^REPLAY' | head -1)
      r=$(echo "$line" | grep -q '"accepted":true' && echo ACCEPTED || echo rejected); echo "$a NEG-$neg $r" >> $O/replay.txt
      [ $r = rejected ] || bad=$((bad+1))
    done
  done
  echo "CELL $a replayed $n sessions; bad (unaccepted honest or accepted negative) $bad" | tee -a $O/summary.txt
done
true
