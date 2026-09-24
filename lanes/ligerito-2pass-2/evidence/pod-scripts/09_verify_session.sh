# item 4: session claim over MY verifier's whole store (vy-ligerito-2pass-verifier /workspace/live/sessions, copied by the laptop:
#   verifier 'cd /workspace/live && tar cf - sessions' | prover 'tar xf - -C /workspace/ligerito-2pass-2/verifier-store')
source /workspace/env.sh; cd /workspace/src; B=/workspace/ligerito-2pass-2/bench/final; S=/workspace/ligerito-2pass-2/verifier-store/sessions
RV=/workspace/cargo-target/release/ligerito-verify; SID=c20260924T040322Z-ff4e
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ls $S > $B/verifier-store.ls
$PY -m backends.direct.ligerito.run verify-session $B/live-zk $S/$SID --sessions-root $S > $B/verify-session-py.log 2>&1; echo "python verify-session exit $?" >> $B/summary.txt
$RV batch --dir $B/live-zk --session $S --json $B/verify-session-rust.json > $B/verify-session-rust.log 2>&1; echo "rust batch --session exit $?" >> $B/summary.txt
echo VS_DONE >> $B/summary.txt
