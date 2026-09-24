#!/usr/bin/env bash
# merge-postwave (CPU pod): cargo check --release of the SP1 crates the merges touched, from inputs/sp1-<sha>.tar.gz
# (`git archive <sha> backends/sp1` of lane/post-wave, shipped with --send because `research pods sync` runs at ~100 KB/s):
#   check-sp1        backends/sp1: veritor-zk-host + veritor-zk-common + veritor-check-model (host build.rs builds the guest ELF)
#   check-sp1-bare   veritor-zk-host --features relation-bare
#   tcdot-fork       build_fork.sh OPERANDS=witness SKIP_SERVER=1 (upstream v6.4.0 + patches 0001-0011, tree == FORK_TREE_WIT)
#   check-tcdot      verity-tcdot-host --features stream-operands at VERITY_TCDOT_FORK_HEAD = FORK_HEAD_WIT
#   test-sp1-common  (not gating) cargo test --release -p veritor-zk-common --features relation-bare
# Waits for setup.sh's toolchains. STAGE_RC[<name>]=<rc> per stage; exit 1 if a gating stage failed.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="$HOME/.sp1/bin:$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/go/bin:$PATH"
IN="$(pwd)/inputs"
W=/workspace/merge-postwave
S=$W/sp1src
mkdir -p "$W"
declare -A RC
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
run() {
  local name=$1; shift
  stage "$name: $*"
  "$@" > "$W/$name.log" 2>&1
  local rc=$?
  grep -E "^error|FAILED|panicked|test result|MISMATCH|fork HEAD" "$W/$name.log" | cut -c1-240 | tail -20
  tail -3 "$W/$name.log" | cut -c1-240
  RC[$name]=$rc; echo "STAGE_RC[$name]=$rc"
}

stage "source"
ls -la "$IN"; sha256sum "$IN"/sp1-*.tar.gz
rm -rf "$S"; mkdir -p "$S"; tar xzf "$IN"/sp1-*.tar.gz -C "$S"; ls "$S/backends/sp1"

stage "wait for setup.sh toolchains"
for i in $(seq 1 90); do cargo prove --version >/dev/null 2>&1 && break; sleep 10; done
cargo prove --version; rustc --version
stage "apt"
for i in 1 2 3; do
  apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    build-essential pkg-config libssl-dev clang libclang-dev cmake protobuf-compiler libprotobuf-dev git jq golang-go time >/dev/null \
    && break
  sleep 20
done; echo "apt rc=$?"; clang --version | head -1; protoc --version

cd "$S/backends/sp1"
export CARGO_TARGET_DIR=$W/target-sp1
run check-sp1       cargo check --release --locked -p veritor-zk-host -p veritor-zk-common -p veritor-check-model
run check-sp1-bare  cargo check --release --locked -p veritor-zk-host --features relation-bare
run tcdot-fork      env OPERANDS=witness SKIP_SERVER=1 SP1_TCDOT_ROOT=$W/sp1-tcdot bash tcdot/build_fork.sh
cd tcdot
run check-tcdot     env VERITY_TCDOT_FORK_HEAD="$(cat FORK_HEAD_WIT)" CARGO_TARGET_DIR=$W/target-tcdot \
                    cargo check --release --locked -p verity-tcdot-host --features stream-operands
cd ..
run test-sp1-common cargo test --release --locked -p veritor-zk-common --features relation-bare

stage "SUMMARY"
fail=0
for k in check-sp1 check-sp1-bare tcdot-fork check-tcdot test-sp1-common; do
  echo "$k ${RC[$k]:-missing}"
  case $k in test-*) ;; *) [ "${RC[$k]:-1}" = 0 ] || fail=1 ;; esac
done
echo "GATING_FAIL=$fail"; exit $fail
