#!/bin/bash
INT=/Users/danielreuter/projects/verity-main-wt/fp4-fast-int
B=/tmp/fp4fast/bench_fp4.sh
$B int5-intzk-l16384-seq    $INT 16384 --zk --mode interactive --warmup-subs 7
$B int5-intzk-l16384-pipe3  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 3
$B int5-intzk-l16384-pipe4  $INT 16384 --zk --mode interactive --warmup-subs 7 --pipeline 4
$B int5-nonzk-l16384-pipe3  $INT 16384 --mode interactive --warmup-subs 7 --pipeline 3
echo INT_SERIES5_DONE
