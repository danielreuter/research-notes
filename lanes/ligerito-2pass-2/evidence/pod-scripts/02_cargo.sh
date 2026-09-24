# item 2: cargo test --release ligerito-verify; cargo check every Cargo.toml under backends/direct
source /workspace/env.sh; O=/workspace/ligerito-2pass-2/cargo; mkdir -p $O; cd /workspace/src
( cd backends/ligerito-verify && cargo test --release 2>&1 ) > $O/ligerito-verify-test.log; echo "ligerito-verify test exit $?" >> $O/summary.txt
for t in $(find backends/direct -name Cargo.toml -not -path '*/target/*'); do d=$(dirname $t)
  ( cd $d && cargo check --release 2>&1 ) > $O/check-$(echo $d | tr / _).log; echo "check $d exit $?" >> $O/summary.txt; done
( cd backends/ligerito-verify && cargo build --release 2>&1 | tail -2 ) >> $O/summary.txt; ls -la $CARGO_TARGET_DIR/release/ligerito-verify >> $O/summary.txt
echo CARGO_DONE >> $O/summary.txt
