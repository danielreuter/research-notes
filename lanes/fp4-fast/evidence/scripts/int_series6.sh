#!/bin/bash
INT=/Users/danielreuter/projects/verity-main-wt/fp4-fast-int
B=/tmp/fp4fast/bench_fp4.sh
$B int6-intzk-l16384-pipe3  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 3
$B int6-intzk-l16384-pipe4  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 4
$B int6-nonzk-l16384-pipe3  $INT 16384 --mode interactive --warmup-subs 7 --pipeline 3
$B int6-intzk-l16384-pipe5  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 5
$B int6-intzk-l8192-pipe4   $INT 8192 --zk --mode interactive --warmup-subs 13 --pipeline 4
echo INT_SERIES6_DONE
