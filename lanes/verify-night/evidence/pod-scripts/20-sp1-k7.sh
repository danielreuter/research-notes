#!/usr/bin/env bash
# verify-night: sp1-table k7 + indexed (handoff 20260924T0835Z): build 2da1e77e (18-sp1-build-rev.sh), then 09-sp1-verify.sh.
REV=2da1e77e bash /workspace/verify-night/18-sp1-build-rev.sh
RES=art:fffbf728d9c50eb1862166e680caef9f1d334c83109bde3532a5fafb8cb61a3a TREE=art:299b7e0e124995cda8e2fa440861280afd4fa66a35abb726d705756f7c8165cf TAG=k7 HOST_BIN=/workspace/sp1-target-2da1e77e/release/veritor-zk-host bash /workspace/verify-night/09-sp1-verify.sh
