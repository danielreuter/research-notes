#!/bin/bash
# main HEAD 64c00bd (lane merged through 07c3039 + enc-hopper's CF_GLOBAL encoder) on the fresh 5090 pod 75dww7vv03yxn2
INT=/Users/danielreuter/projects/verity-main-wt/fp4-fast-int
B=/tmp/fp4fast/bench_fp4.sh
$B main64c00bd-intzk-l16384-pipe3  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 3
$B main64c00bd-intzk-l16384-seq    $INT 16384 --zk --mode interactive --warmup-subs 7
$B main64c00bd-nonzk-l16384-pipe3  $INT 16384 --mode interactive --warmup-subs 7 --pipeline 3
echo INT_SERIES9_DONE
