#!/usr/bin/env bash
# Loopback sessions (a verifier process serving its own public file), M0 against M1 (--zk), per staged set.
set -u
B=${B:-$HOME/fzk/flock-circuit-prove}; OUT=$HOME/fzk/ev/bench; mkdir -p $OUT
RUNS=${RUNS:-3}; WARM=${WARM:-1}
for set in rope rope16 rope64; do
  D=$HOME/fzk/$set/stage; n=$(ls $D/inst-*.bin | sed 's/.*inst-\([0-9]*\).bin/\1/')
  PIN=$(sha512sum $D/circuit.txt | cut -d' ' -f1)
  for mode in m0 zk; do
    Z=; [ $mode = zk ] && Z=--zk
    port=$((7600 + RANDOM % 300))
    $B serve $Z --listen 127.0.0.1:$port --out $OUT/sessions-$set-$mode --instances $D/pub-$n.bin --circuit $D/circuit.txt --tables /tmp --pin $PIN --operator loopback > $OUT/serve-$set-$mode.log 2>&1 &
    SP=$!
    for i in $(seq 120); do grep -q SERVING $OUT/serve-$set-$mode.log && break; sleep 1; done
    $B prove $Z --verifier 127.0.0.1:$port --instances $D/inst-$n.bin --circuit $D/circuit.txt --tables /tmp --warm $WARM --runs $RUNS > $OUT/prove-$set-$mode.txt 2> $OUT/prove-$set-$mode.err
    kill $SP; wait $SP 2>/dev/null
    grep -h '^LIVE' $OUT/prove-$set-$mode.txt | python3 -c "
import json, sys
for l in sys.stdin:
    v = json.loads(l[5:])
    b = v['buckets']
    print('$set', '$mode', 'n', v['instances'], 'm', v['dense_m'], 'warm' if v['warm'] else 'timed', 'acc', v['accepted'], 'e2e %.3f' % v['e2e_s'], 'wit %.3f' % v['witness_s'],
          'prove', ['%.3f' % x for x in v['prove_s']], 'upstream', ['%.3f' % x.get('t.upstream', x.get('t.prove', 0)) for x in b],
          'zk_inner', ['%.3f' % x.get('t.zk_inner', 0) for x in b], 'bytes', v['proof_bytes'])
"
  done
done
