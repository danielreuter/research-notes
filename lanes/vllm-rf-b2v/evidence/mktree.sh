#!/usr/bin/env bash
# mktree.sh SRC_TREE SRC_LIST DST_TREE DST_LIST [PATCH]
# Copies the files of SRC_LIST out of SRC_TREE into a fresh DST_TREE, applies PATCH (git diff --binary between the
# two commits), then checks every file of DST_TREE against DST_LIST (git blob id per path) and reports extras.
set -euo pipefail
src=$1 srclist=$2 dst=$3 dstlist=$4 patch=${5:-}
verify() {  # TREE LIST [extras-allowed]
  local bad
  bad=$(cd "$1" && cut -f2 "$2" | git hash-object --stdin-paths | paste - <(cut -f1 "$2") <(cut -f2 "$2") \
        | awk -F'\t' '$1!=$2' | wc -l)
  local extra
  extra=$(cd "$1" && comm -23 <(find . -type f ! -path '*/__pycache__/*' ! -path './.pytest_cache/*' \
          ! -name .research-source.json ! -name .b2v-tree | sed 's|^\./||' | sort) <(cut -f2 "$2" | sort) | wc -l)
  echo "verify $1: files $(wc -l < "$2") mismatched $bad extra $extra"
  [ "$bad" = 0 ] && { [ "$extra" = 0 ] || [ -n "${3:-}" ]; }
}
if [ "$src" = "$dst" ]; then verify "$dst" "$dstlist"; exit; fi
verify "$src" "$srclist" extras-allowed
rm -rf "$dst.tmp" && mkdir -p "$dst.tmp"
(cd "$src" && cut -f2 "$srclist" | tar -cf - -T -) | tar -xf - -C "$dst.tmp"
if [ -n "$patch" ]; then (cd "$dst.tmp" && git apply --whitespace=nowarn "$patch"); fi
verify "$dst.tmp" "$dstlist"
rm -rf "$dst" && mv "$dst.tmp" "$dst"
echo "$(basename "$dstlist" .lst) built from $src by mktree.sh; blob ids verified" > "$dst/.b2v-tree"
echo "OK $dst"
