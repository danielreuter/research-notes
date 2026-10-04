#!/usr/bin/env bash
# sync.sh SRC DST : copy with retries, verify sha256
src=$1; dst=$2
want=$(sha256sum < "$src" | cut -d' ' -f1)
for i in 1 2 3 4 5 6; do
  mkdir -p "$(dirname "$dst")" 2>/dev/null
  cp "$src" "$dst.tmp.$$" 2>/dev/null && mv -f "$dst.tmp.$$" "$dst" 2>/dev/null
  got=$(sha256sum < "$dst" 2>/dev/null | cut -d' ' -f1)
  [ "$got" = "$want" ] && { echo "ok $dst"; exit 0; }
  rm -f "$dst.tmp.$$" 2>/dev/null; sleep $((2*i))
done
echo "FAILED $dst"; exit 1
