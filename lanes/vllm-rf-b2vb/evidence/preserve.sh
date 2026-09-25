#!/usr/bin/env bash
# Workload of a `research run --on vyv-rf-b2v-tp2 --custody-r2` run: copies into this run dir (so the runner publishes and verifies every
# byte on the store's remote) what the TP2 pod holds that R2 does not: the logs of the 7 runs launched before --custody-r2 (their
# attempts are preserved, their run files are not), row #70's evidence (top level, commit/ without the two 219 MB binding maps,
# properties/, match/ files under 1 MB to depth 2; not the 37 GB capture, the 171 MB manifest or build/'s Programs), the gate outputs
# and /workspace/b2vb.  PRESERVED.sha256 lists every copied file.
set -eu
P=$PWD/preserved
ROW=olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager
D=/workspace/cp/sweep/$ROW
mkdir -p "$P/runs" "$P/row70/$ROW" "$P/gates" "$P/b2vb"
for r in r20260925-093353-557e r20260925-095754-ee6c r20260925-105008-bca1 r20260925-110440-71eb r20260925-111138-272a \
         r20260925-111454-b341 r20260925-111729-3301; do
  cp -a "/workspace/research/runs/$r" "$P/runs/"
done
( cd "$D" && { find . -maxdepth 1 -type f ! -name manifest.json; find commit properties -type f ! -name 'binding_map_rank*';
               find match -maxdepth 2 -type f -size -1M; } | sort > "$P/row70/files.txt" )
( cd "$D" && tar cf - -T "$P/row70/files.txt" ) | ( cd "$P/row70/$ROW" && tar xf - )
find /workspace/out/gates -maxdepth 1 -type f -exec cp -a {} "$P/gates/" \;
cp -a /workspace/out/gates/verdict_bytes "$P/gates/"
cp -a /workspace/b2vb/. "$P/b2vb/"
( cd "$P" && find . -type f ! -name PRESERVED.sha256 -print0 | sort -z | xargs -0 sha256sum > PRESERVED.sha256 )
echo "preserved: $(wc -l < "$P/PRESERVED.sha256") files, $(du -sb "$P" | cut -f1) bytes"
for s in runs row70 gates b2vb; do echo "  $s: $(find "$P/$s" -type f | wc -l) files, $(du -sb "$P/$s" | cut -f1) bytes"; done
